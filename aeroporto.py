import simpy
from config import CAPACIDADES

class Aeroporto:
    """
    Encapsula todos os recursos físicos do aeroporto modelados 
    como Resources do SimPy para controle de filas e concorrência.
    """
    def __init__(self, env):
        self.env = env
        
        # Alocação das capacidades definidas nas configurações (config.py)
        self.pistas_pequenas = simpy.Resource(env, capacity=CAPACIDADES['pistas_pequenas'])
        self.pista_grande = simpy.Resource(env, capacity=CAPACIDADES['pista_grande'])
        self.plataformas = simpy.Resource(env, capacity=CAPACIDADES['plataformas'])
        self.hangares = simpy.Resource(env, capacity=CAPACIDADES['hangares'])