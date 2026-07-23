import simpy
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO DA TOPOLOGIA EM "AMPULHETA"
# ==========================================
G = nx.DiGraph()

# Layout: Extremidades bifurcadas (Y=4 e Y=2) e centro unificado (Y=3)
posicoes = {
    'Chegada': (0, 3),
    
    # --- Bifurcação de Pouso ---
    'Fila Pouso (P)': (2, 4), 'Pouso (P)': (4, 4),
    'Fila Pouso (G)': (2, 2), 'Pouso (G)': (4, 2),
    
    # --- Centro Compartilhado ---
    'Fila Desemb': (6, 3), 'Desembarque': (8, 3), 
    'Fila Hangar': (10, 3), 'Hangar': (12, 3),
    'Fila Embarque': (12, 1), 'Embarque': (10, 1),

    # --- Bifurcação de Decolagem ---
    'Fila Decolagem (P)': (8, 2), 'Decolagem (P)': (6, 2),
    'Fila Decolagem (G)': (8, 0), 'Decolagem (G)': (6, 0),
    
    'Saída': (4, 1)
}

# Conectando a malha
G.add_edges_from([
    # Separa na chegada
    ('Chegada', 'Fila Pouso (P)'), ('Chegada', 'Fila Pouso (G)'),
    ('Fila Pouso (P)', 'Pouso (P)'), ('Fila Pouso (G)', 'Pouso (G)'),
    
    # Unifica no desembarque e segue pelo centro
    ('Pouso (P)', 'Fila Desemb'), ('Pouso (G)', 'Fila Desemb'),
    ('Fila Desemb', 'Desembarque'), ('Desembarque', 'Fila Hangar'),
    ('Fila Hangar', 'Hangar'), ('Hangar', 'Fila Embarque'),
    ('Fila Embarque', 'Embarque'),
    
    # Separa novamente para a decolagem
    ('Embarque', 'Fila Decolagem (P)'), ('Embarque', 'Fila Decolagem (G)'),
    ('Fila Decolagem (P)', 'Decolagem (P)'), ('Fila Decolagem (G)', 'Decolagem (G)'),
    
    # Unifica na saída
    ('Decolagem (P)', 'Saída'), ('Decolagem (G)', 'Saída')
])

estado_nos = {no: 0 for no in G.nodes()}

# ==========================================
# 2. ABSTRAÇÃO E LÓGICA DE TRANSIÇÃO VISUAL
# ==========================================
class AeroportoVisual:
    def __init__(self, env):
        self.pistas_pequenas = simpy.Resource(env, capacity=4)
        self.pista_grande = simpy.Resource(env, capacity=2)
        self.plataformas = simpy.Resource(env, capacity=5)
        self.hangares = simpy.Resource(env, capacity=3)

def ciclo_aeronave_visual(env, id_aeronave, tipo, aeroporto):
    # --- CHEGADA ---
    estado_nos['Chegada'] += 1
    yield env.timeout(1)
    estado_nos['Chegada'] -= 1
    
    # --- POUSO (Segregado) ---
    estado_nos[f'Fila Pouso ({tipo})'] += 1
    pista = aeroporto.pistas_pequenas if tipo == 'P' else aeroporto.pista_grande
    with pista.request() as req:
        yield req
        estado_nos[f'Fila Pouso ({tipo})'] -= 1
        estado_nos[f'Pouso ({tipo})'] += 1
        yield env.timeout(40 if tipo == 'P' else 60)
        estado_nos[f'Pouso ({tipo})'] -= 1

    # --- DESEMBARQUE (Compartilhado) ---
    estado_nos['Fila Desemb'] += 1
    with aeroporto.plataformas.request() as req:
        yield req
        estado_nos['Fila Desemb'] -= 1
        estado_nos['Desembarque'] += 1
        yield env.timeout(20 if tipo == 'P' else 40)
        estado_nos['Desembarque'] -= 1

    # --- HANGAR (Compartilhado) ---
    estado_nos['Fila Hangar'] += 1
    with aeroporto.hangares.request() as req:
        yield req
        estado_nos['Fila Hangar'] -= 1
        estado_nos['Hangar'] += 1
        yield env.timeout(35 if tipo == 'P' else 70)
        estado_nos['Hangar'] -= 1

    # --- EMBARQUE (Compartilhado) ---
    estado_nos['Fila Embarque'] += 1
    with aeroporto.plataformas.request() as req:
        yield req
        estado_nos['Fila Embarque'] -= 1
        estado_nos['Embarque'] += 1
        yield env.timeout(30 if tipo == 'P' else 60)
        estado_nos['Embarque'] -= 1

    # --- DECOLAGEM (Segregado) ---
    estado_nos[f'Fila Decolagem ({tipo})'] += 1
    with pista.request() as req:
        yield req
        estado_nos[f'Fila Decolagem ({tipo})'] -= 1
        estado_nos[f'Decolagem ({tipo})'] += 1
        yield env.timeout(40 if tipo == 'P' else 60)
        estado_nos[f'Decolagem ({tipo})'] -= 1

    # --- SAÍDA ---
    estado_nos['Saída'] += 1

# ==========================================
# 3. GERADOR DE CHEGADAS
# ==========================================
total_aeronaves = 102

def gerador_chegadas(env, aeroporto, arquivo_csv):
    try:
        df = pd.read_csv(arquivo_csv, delimiter=',') 
        for _, row in df.iterrows():
            id_aeronave = row['id']
            tipo = str(row['tipo']).strip().upper()
            tempo_chegada = float(row['horario_chegada'])
            
            if tempo_chegada > env.now:
                yield env.timeout(tempo_chegada - env.now)
            
            env.process(ciclo_aeronave_visual(env, id_aeronave, tipo, aeroporto))
            
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{arquivo_csv}' não encontrado no diretório.")

# ==========================================
# 4. EXECUÇÃO E ANIMAÇÃO
# ==========================================
fig, ax = plt.subplots(figsize=(15, 7))
env = simpy.Environment()
aeroporto = AeroportoVisual(env)

env.process(gerador_chegadas(env, aeroporto, 'chegadas.csv'))

def atualizar_frame(frame):
    ax.clear()
    
    if estado_nos['Saída'] == total_aeronaves:
        ax.text(0.5, 0.95, "SIMULAÇÃO CONCLUÍDA!", 
                transform=ax.transAxes, ha='center', 
                fontsize=14, color='red', weight='bold')
        
        if hasattr(ani, 'event_source') and ani.event_source:
            ani.event_source.stop()
            
    else:
        env.run(until=env.now + 10)
    
    cores_nos = []
    labels = {}
    
    for no in G.nodes():
        qtd = estado_nos[no]
        labels[no] = f"{no}\n({qtd})"
        if qtd >= 3 and "Fila" in no:
            cores_nos.append('lightcoral')
        elif qtd > 0:
            cores_nos.append('lightgreen')
        else:
            cores_nos.append('lightblue')

    nx.draw(G, posicoes, ax=ax, with_labels=True, labels=labels, 
            node_color=cores_nos, node_size=3000, font_size=8, 
            font_weight='bold', edge_color='gray', arrows=True)
    
    ax.set_title(f"ACD Aeroporto (Foco Pistas) - Tempo Simulado: {env.now} min")

ani = animation.FuncAnimation(fig, atualizar_frame, interval=100, cache_frame_data=False)

plt.tight_layout()
plt.show()