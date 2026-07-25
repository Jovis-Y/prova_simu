import simpy
from typing import Dict, Tuple, List

TOTAL_AERONAVES: int = 102

TEMPOS_ATIVIDADES: Dict[str, Dict[str, int]] = {
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

CAPACIDADES: Dict[str, int] = {
    'pistas_pequenas': 2,
    'pista_grande': 1,
    'plataformas': 5,
    'hangares': 3
}

POSICOES: Dict[str, Tuple[int, int]] = {
    'Chegada': (0, 3),
    
    'Fila Pouso (P)': (2, 4), 'Pouso (P)': (4, 4),
    'Fila Pouso (G)': (2, 2), 'Pouso (G)': (4, 2),
    
    'Fila Desemb': (6, 3),    'Desembarque': (8, 3), 
    'Fila Hangar': (10, 3),   'Hangar': (12, 3),
    'Fila Embarque': (12, 1), 'Embarque': (10, 1),

    'Fila Decolagem (P)': (8, 2), 'Decolagem (P)': (6, 2),
    'Fila Decolagem (G)': (8, 0), 'Decolagem (G)': (6, 0),
    
    'Saída': (4, 1)
}

ARESTAS: List[Tuple[str, str]] = [
    ('Chegada', 'Fila Pouso (P)'), 
    ('Chegada', 'Fila Pouso (G)'),
    ('Fila Pouso (P)', 'Pouso (P)'), 
    ('Fila Pouso (G)', 'Pouso (G)'),
    
    ('Pouso (P)', 'Fila Desemb'), 
    ('Pouso (G)', 'Fila Desemb'),
    ('Fila Desemb', 'Desembarque'), 
    ('Desembarque', 'Fila Hangar'),
    ('Fila Hangar', 'Hangar'), 
    ('Hangar', 'Fila Embarque'),
    ('Fila Embarque', 'Embarque'),
    
    ('Embarque', 'Fila Decolagem (P)'), 
    ('Embarque', 'Fila Decolagem (G)'),
    ('Fila Decolagem (P)', 'Decolagem (P)'), 
    ('Fila Decolagem (G)', 'Decolagem (G)'),
    
    ('Decolagem (P)', 'Saída'), 
    ('Decolagem (G)', 'Saída')
]

estado_nos: Dict[str, int] = {no: 0 for no in POSICOES.keys()}

class AeroportoVisual:
    
    def __init__(self, env: simpy.Environment, capacidades: Dict[str, int] = None):
        self.env = env
        
        _caps = capacidades if capacidades is not None else CAPACIDADES
        
        self.pistas_pequenas = simpy.Resource(env, capacity=_caps['pistas_pequenas'])
        self.pista_grande = simpy.Resource(env, capacity=_caps['pista_grande'])
        self.plataformas = simpy.Resource(env, capacity=_caps['plataformas'])
        self.hangares = simpy.Resource(env, capacity=_caps['hangares'])

    @staticmethod
    def obter_tempo_atividade(porte: str, atividade: str) -> int:
        return TEMPOS_ATIVIDADES.get(porte, {}).get(atividade, 0)

    @staticmethod
    def atualizar_estado_no(no_origem: str, no_destino: str) -> None:
        if no_origem in estado_nos and estado_nos[no_origem] > 0:
            estado_nos[no_origem] -= 1
            
        if no_destino in estado_nos:
            estado_nos[no_destino] += 1