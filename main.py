import simpy
import pandas as pd

# ==========================================
# 1. CONSTANTES E CONFIGURAÇÕES
# ==========================================
# Tempos (em minutos) baseados na descrição do problema
TEMPOS_ATIVIDADES = {
    'P': {'pouso': 40, 'desembarque': 20, 'hangar': 35, 'embarque': 30, 'decolagem': 40},
    'G': {'pouso': 60, 'desembarque': 40, 'hangar': 70, 'embarque': 60, 'decolagem': 60}
}

# Lista para armazenar métricas e ajudar na identificação de gargalos
log_esperas = []

# ==========================================
# 2. ABSTRAÇÃO DO AMBIENTE (RECURSOS)
# ==========================================
class Aeroporto:
    """Encapsula todos os recursos físicos do aeroporto."""
    def __init__(self, env):
        self.env = env
        # Capacidades definidas no problema
        self.pistas_pequenas = simpy.Resource(env, capacity=2)
        self.pista_grande = simpy.Resource(env, capacity=1)
        self.plataformas = simpy.Resource(env, capacity=5)
        self.hangares = simpy.Resource(env, capacity=4)

# ==========================================
# 3. PROCESSO DA ENTIDADE (CICLO DA AERONAVE)
# ==========================================
def ciclo_aeronave(env, id_aeronave, tipo, aeroporto):
    """ Modela o fluxo de vida (ACD) de uma aeronave no sistema. """
    tempos = TEMPOS_ATIVIDADES[tipo]
    
    # Define qual pista será usada com base no porte da aeronave
    pista_adequada = aeroporto.pistas_pequenas if tipo == 'P' else aeroporto.pista_grande
    
    # ----------------------------------
    # FASE 1: POUSO
    # ----------------------------------
    chegada_fila_pouso = env.now
    with pista_adequada.request() as req:
        yield req  # Aguarda na fila até a pista liberar
        espera_pouso = env.now - chegada_fila_pouso
        print(f"[{env.now:06.1f}] Voo {id_aeronave} ({tipo}) inicia POUSO. (Espera: {espera_pouso} min)")
        yield env.timeout(tempos['pouso']) # Executa a atividade
    
    # ----------------------------------
    # FASE 2: DESEMBARQUE
    # ----------------------------------
    chegada_fila_desemb = env.now
    with aeroporto.plataformas.request() as req:
        yield req
        espera_desemb = env.now - chegada_fila_desemb
        print(f"[{env.now:06.1f}] Voo {id_aeronave} ({tipo}) inicia DESEMBARQUE.")
        yield env.timeout(tempos['desembarque'])
        
    # ----------------------------------
    # FASE 3: HANGAR
    # ----------------------------------
    chegada_fila_hangar = env.now
    with aeroporto.hangares.request() as req:
        yield req
        espera_hangar = env.now - chegada_fila_hangar
        print(f"[{env.now:06.1f}] Voo {id_aeronave} ({tipo}) entra no HANGAR.")
        yield env.timeout(tempos['hangar'])

    # ----------------------------------
    # FASE 4: EMBARQUE
    # ----------------------------------
    chegada_fila_embarque = env.now
    with aeroporto.plataformas.request() as req:
        yield req
        espera_embarque = env.now - chegada_fila_embarque
        print(f"[{env.now:06.1f}] Voo {id_aeronave} ({tipo}) inicia EMBARQUE.")
        yield env.timeout(tempos['embarque'])

    # ----------------------------------
    # FASE 5: DECOLAGEM
    # ----------------------------------
    chegada_fila_decolagem = env.now
    with pista_adequada.request() as req:
        yield req
        espera_decolagem = env.now - chegada_fila_decolagem
        print(f"[{env.now:06.1f}] Voo {id_aeronave} ({tipo}) inicia DECOLAGEM.")
        yield env.timeout(tempos['decolagem'])

    print(f"[{env.now:06.1f}] ---> Voo {id_aeronave} ({tipo}) FINALIZOU e deixou o sistema.")
    
    # Registra as métricas dessa aeronave para análise de gargalos
    log_esperas.append({
        'ID': id_aeronave,
        'Tipo': tipo,
        'Espera_Pouso': espera_pouso,
        'Espera_Desemb': espera_desemb,
        'Espera_Hangar': espera_hangar,
        'Espera_Embarque': espera_embarque,
        'Espera_Decolagem': espera_decolagem
    })

# ==========================================
# 4. GERADOR DE CHEGADAS (INPUT DE DADOS)
# ==========================================
def gerador_chegadas(env, aeroporto, arquivo_csv):
    """ Lê o CSV e gera as aeronaves nos momentos corretos da simulação. """
    try:
        # Espera-se que o CSV tenha cabeçalhos como: ID, Tipo, Chegada
        df = pd.read_csv(arquivo_csv, delimiter=',') # Ajuste o delimiter (',', ';') se necessário
        
        
        for _, row in df.iterrows():
            id_aeronave = row['id']
            tipo = str(row['tipo']).strip().upper()
            tempo_chegada = float(row['horario_chegada'])
            
            # Trava o processo gerador até o tempo exato de chegada dessa aeronave
            if tempo_chegada > env.now:
                yield env.timeout(tempo_chegada - env.now)
            
            # Inicia o processo de fluxo da aeronave independentemente do gerador
            env.process(ciclo_aeronave(env, id_aeronave, tipo, aeroporto))
            
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{arquivo_csv}' não encontrado no diretório.")
        print("Crie um CSV com colunas: ID, Tipo, Chegada")

# ==========================================
# 5. EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == '__main__':
    print("Iniciando Simulação Discreta do Aeroporto...\n" + "="*50)
    
    # Cria o ambiente e o aeroporto
    env = simpy.Environment()
    aeroporto = Aeroporto(env)
    
    # Inicia o processo do gerador lendo o arquivo especificado na prova
    env.process(gerador_chegadas(env, aeroporto, 'chegadas.csv'))
    
    # Executa até a exaustão de todos os eventos
    env.run()
    
    print("="*50 + f"\nTempo final da simulação: {env.now:.1f} minutos\n")
    
    # Transforma o log num DataFrame
    df_metricas = pd.DataFrame(log_esperas)
    if not df_metricas.empty:
        print("MÉDIA DE TEMPO DE ESPERA POR FILA (em minutos):")
        
        # Agrupa pelo 'Tipo' e calcula a média das colunas selecionadas
        medias_por_tipo = df_metricas.groupby('Tipo')[
            ['Espera_Pouso', 'Espera_Desemb', 'Espera_Hangar', 'Espera_Embarque', 'Espera_Decolagem']
        ].mean()
        
        print(medias_por_tipo)