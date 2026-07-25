import simpy
from typing import Dict, Any

# Estrutura simulada para armazenar o estado global dos nós.
# Recomenda-se importar de um módulo de configuração (ex: from config import estado_nos)
estado_nos: Dict[str, int] = {}

class ConfiguracaoAeroporto:
    """
    Centraliza os parâmetros de capacidades e os tempos operacionais (em minutos).
    """
    # Capacidades de recursos
    CAPACIDADE_PISTA_PEQ = 4
    CAPACIDADE_PISTA_GRA = 2
    CAPACIDADE_PLATAFORMA = 5
    CAPACIDADE_HANGAR = 3
    CAPACIDADE_ABASTECIMENTO = 2  # Novo recurso

    # Tempos mapeados por tipo de aeronave ('P': Pequena, 'G': Grande)
    TEMPOS = {
        'P': {
            'pouso': 40, 
            'desembarque': 20, 
            'abastecimento': 15, 
            'hangar': 35, 
            'embarque': 30, 
            'decolagem': 40
        },
        'G': {
            'pouso': 60, 
            'desembarque': 40, 
            'abastecimento': 25, 
            'hangar': 70, 
            'embarque': 60, 
            'decolagem': 60
        }
    }

class AeroportoVisual:
    """
    Gerencia a alocação de recursos do aeroporto que serão consumidos pelas aeronaves
    e monitora o estado de ocupação de cada nó.
    """
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.pistas_pequenas = simpy.Resource(env, capacity=ConfiguracaoAeroporto.CAPACIDADE_PISTA_PEQ)
        self.pista_grande = simpy.Resource(env, capacity=ConfiguracaoAeroporto.CAPACIDADE_PISTA_GRA)
        self.plataformas = simpy.Resource(env, capacity=ConfiguracaoAeroporto.CAPACIDADE_PLATAFORMA)
        self.hangares = simpy.Resource(env, capacity=ConfiguracaoAeroporto.CAPACIDADE_HANGAR)
        # Novo recurso expandido
        self.caminhoes_abastecimento = simpy.Resource(env, capacity=ConfiguracaoAeroporto.CAPACIDADE_ABASTECIMENTO)

    @staticmethod
    def atualizar_estado(chave: str, delta: int) -> None:
        """
        Garante a atualização segura dos nós do aeroporto no dicionário de estados globais.
        """
        estado_nos[chave] = estado_nos.get(chave, 0) + delta


def ciclo_aeronave_visual(env: simpy.Environment, id_aeronave: str, tipo: str, aeroporto: AeroportoVisual):
    """
    Lógica de transição e enfileiramento da aeronave pelos setores do aeroporto.
    """
    tempos = ConfiguracaoAeroporto.TEMPOS.get(tipo)
    if not tempos:
        raise ValueError(f"Tipo de aeronave '{tipo}' não reconhecido.")

    # --- CHEGADA ---
    aeroporto.atualizar_estado('Chegada', 1)
    yield env.timeout(1)
    aeroporto.atualizar_estado('Chegada', -1)
    
    # --- POUSO (Segregado) ---
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

    # --- DESEMBARQUE (Compartilhado) ---
    aeroporto.atualizar_estado('Fila Desemb', 1)
    with aeroporto.plataformas.request() as req:
        yield req
        aeroporto.atualizar_estado('Fila Desemb', -1)
        aeroporto.atualizar_estado('Desembarque', 1)
        yield env.timeout(tempos['desembarque'])
        aeroporto.atualizar_estado('Desembarque', -1)

    # --- ABASTECIMENTO (Nova Etapa Expandida) ---
    aeroporto.atualizar_estado('Fila Abastecimento', 1)
    with aeroporto.caminhoes_abastecimento.request() as req:
        yield req
        aeroporto.atualizar_estado('Fila Abastecimento', -1)
        aeroporto.atualizar_estado('Abastecimento', 1)
        yield env.timeout(tempos['abastecimento'])
        aeroporto.atualizar_estado('Abastecimento', -1)

    # --- HANGAR (Compartilhado) ---
    aeroporto.atualizar_estado('Fila Hangar', 1)
    with aeroporto.hangares.request() as req:
        yield req
        aeroporto.atualizar_estado('Fila Hangar', -1)
        aeroporto.atualizar_estado('Hangar', 1)
        yield env.timeout(tempos['hangar'])
        aeroporto.atualizar_estado('Hangar', -1)

    # --- EMBARQUE (Compartilhado) ---
    aeroporto.atualizar_estado('Fila Embarque', 1)
    with aeroporto.plataformas.request() as req:
        yield req
        aeroporto.atualizar_estado('Fila Embarque', -1)
        aeroporto.atualizar_estado('Embarque', 1)
        yield env.timeout(tempos['embarque'])
        aeroporto.atualizar_estado('Embarque', -1)

    # --- DECOLAGEM (Segregado) ---
    fila_decolagem = f'Fila Decolagem ({tipo})'
    acao_decolagem = f'Decolagem ({tipo})'
    
    aeroporto.atualizar_estado(fila_decolagem, 1)
    with pista.request() as req:
        yield req
        aeroporto.atualizar_estado(fila_decolagem, -1)
        aeroporto.atualizar_estado(acao_decolagem, 1)
        yield env.timeout(tempos['decolagem'])
        aeroporto.atualizar_estado(acao_decolagem, -1)

    # --- SAÍDA ---
    aeroporto.atualizar_estado('Saída', 1)