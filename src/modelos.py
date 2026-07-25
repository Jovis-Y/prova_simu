import simpy
from config import CAPACIDADES, TEMPOS_ATIVIDADES, estado_nos

class AeroportoVisual:
    def __init__(self, env: simpy.Environment, capacidades=None):
        self.env = env
        _caps = capacidades if capacidades is not None else CAPACIDADES
        
        self.pistas_pequenas = simpy.Resource(env, capacity=_caps['pistas_pequenas'])
        self.pista_grande = simpy.Resource(env, capacity=_caps['pista_grande'])
        self.plataformas = simpy.Resource(env, capacity=_caps['plataformas'])
        self.hangares = simpy.Resource(env, capacity=_caps['hangares'])

    @staticmethod
    def atualizar_estado(chave: str, delta: int) -> None:
        estado_nos[chave] = estado_nos.get(chave, 0) + delta

def ciclo_aeronave_visual(env: simpy.Environment, id_aeronave: str, tipo: str, aeroporto: AeroportoVisual):
    tempos = TEMPOS_ATIVIDADES.get(tipo)
    if not tempos:
        raise ValueError(f"Tipo de aeronave '{tipo}' não reconhecido.")

    aeroporto.atualizar_estado('Chegada', 1)
    yield env.timeout(1)
    aeroporto.atualizar_estado('Chegada', -1)
    
    fila_pouso = f'Fila Pouso ({tipo})'
    acao_pouso = f'Pouso ({tipo})'
    pista = aeroporto.pistas_pequenas if tipo == 'P' else aeroporto.pista_grande
    
    aeroporto.atualizar_estado(fila_pouso, 1)
    with pista.request() as req:
        yield req
        aeroporto.atualizar_estado(fila_pouso, -1)
        aeroporto.atualizar_estado(acao_pouso, 1)
        yield env.timeout(tempos['pouso'])
        aeroporto.atualizar_estado(acao_pouso, -1)

    aeroporto.atualizar_estado('Fila Desemb', 1)
    with aeroporto.plataformas.request() as req:
        yield req
        aeroporto.atualizar_estado('Fila Desemb', -1)
        aeroporto.atualizar_estado('Desembarque', 1)
        yield env.timeout(tempos['desembarque'])
        aeroporto.atualizar_estado('Desembarque', -1)

    aeroporto.atualizar_estado('Fila Hangar', 1)
    with aeroporto.hangares.request() as req:
        yield req
        aeroporto.atualizar_estado('Fila Hangar', -1)
        aeroporto.atualizar_estado('Hangar', 1)
        yield env.timeout(tempos['hangar'])
        aeroporto.atualizar_estado('Hangar', -1)

    aeroporto.atualizar_estado('Fila Embarque', 1)
    with aeroporto.plataformas.request() as req:
        yield req
        aeroporto.atualizar_estado('Fila Embarque', -1)
        aeroporto.atualizar_estado('Embarque', 1)
        yield env.timeout(tempos['embarque'])
        aeroporto.atualizar_estado('Embarque', -1)

    fila_decolagem = f'Fila Decolagem ({tipo})'
    acao_decolagem = f'Decolagem ({tipo})'
    
    aeroporto.atualizar_estado(fila_decolagem, 1)
    with pista.request() as req:
        yield req
        aeroporto.atualizar_estado(fila_decolagem, -1)
        aeroporto.atualizar_estado(acao_decolagem, 1)
        yield env.timeout(tempos['decolagem'])
        aeroporto.atualizar_estado(acao_decolagem, -1)

    aeroporto.atualizar_estado('Saída', 1)