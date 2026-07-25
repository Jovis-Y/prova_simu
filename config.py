import simpy

class AeroportoVisual:
    def __init__(self, env):
        self.pistas_pequenas = simpy.Resource(env, capacity=4)
        self.pista_grande = simpy.Resource(env, capacity=2)
        self.plataformas = simpy.Resource(env, capacity=5)
        self.hangares = simpy.Resource(env, capacity=3)

"""
Módulo responsável por armazenar todas as constantes, parâmetros e 
configurações físicas da simulação do aeroporto.
"""

# Tempos (em minutos) baseados estritamente na descrição do problema da Prova II
TEMPOS_ATIVIDADES = {
    'P': {
        'pouso': 40, 
        'desembarque': 20, 
        'hangar': 35, 
        'embarque': 30, 
        'decolagem': 40
    },
    'G': {
        'pouso': 60, 
        'desembarque': 40, 
        'hangar': 70, 
        'embarque': 60, 
        'decolagem': 60
    }
}

# Capacidades de recursos conforme a descrição do documento prova-2.pdf
CAPACIDADES = {
    'pistas_pequenas': 2,
    'pista_grande': 1,
    'plataformas': 5,
    'hangares': 3  # Valor corrigido conforme exigência do PDF (eram 4 no original)
}

"""
Arquivo responsável por armazenar configurações, topologia e estados globais
para que possam ser acessados por outros módulos sem causar dependência circular.
"""

TOTAL_AERONAVES = 102

# Layout: Extremidades bifurcadas (Y=4 e Y=2) e centro unificado (Y=3)
POSICOES = {
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

# Conexões da malha de grafos
ARESTAS = [
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
]

# Dicionário de estado compartilhado entre os arquivos
# Como dicionários são mutáveis, as atualizações em outros arquivos refletirão aqui.
estado_nos = {no: 0 for no in POSICOES.keys()}