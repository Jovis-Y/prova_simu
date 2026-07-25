from typing import Any
from contextlib import contextmanager

# Importação do dicionário global de topologia original
from topologia import estado_nos

# --- CONFIGURAÇÕES DO SISTEMA ---
# A centralização dos tempos facilita testes e a inclusão de novas categorias (ex: M, Carga).
TEMPOS_PROCESSO = {
    'P': {'pouso': 40, 'desembarque': 20, 'hangar': 35, 'embarque': 30, 'decolagem': 40},
    'G': {'pouso': 60, 'desembarque': 40, 'hangar': 70, 'embarque': 60, 'decolagem': 60}
}

@contextmanager
def atualizar_estado(chave: str):
    """
    Gerenciador de contexto para atualizar o dicionário global de estados de forma segura.
    Substitui a adição e subtração manual repetitiva.
    """
    estado_nos[chave] = estado_nos.get(chave, 0) + 1
    try:
        yield
    finally:
        estado_nos[chave] -= 1

def ciclo_aeronave_visual(env: Any, id_aeronave: str, tipo: str, aeroporto: Any):
    """
    Simula o fluxo completo de uma aeronave no ambiente aeroportuário, englobando
    desde a chegada até a decolagem e saída.
    """
    # Define os tempos de acordo com o tipo, com fallback seguro para 'G'
    tempos = TEMPOS_PROCESSO.get(tipo, TEMPOS_PROCESSO['G'])
    
    # Seleção de pistas segregadas com base no tipo da aeronave
    pista = aeroporto.pistas_pequenas if tipo == 'P' else aeroporto.pista_grande

    # --- 1. CHEGADA ---
    with atualizar_estado('Chegada'):
        yield env.timeout(1)

    # --- 2. POUSO (Segregado) ---
    with atualizar_estado(f'Fila Pouso ({tipo})'):
        req_pouso = pista.request()
        yield req_pouso
        
    with atualizar_estado(f'Pouso ({tipo})'):
        yield env.timeout(tempos['pouso'])
    pista.release(req_pouso)

    # --- 3. DESEMBARQUE (Compartilhado) ---
    with atualizar_estado('Fila Desemb'):
        req_desemb = aeroporto.plataformas.request()
        yield req_desemb
        
    with atualizar_estado('Desembarque'):
        yield env.timeout(tempos['desembarque'])
    aeroporto.plataformas.release(req_desemb)

    # --- 4. HANGAR (Compartilhado) ---
    with atualizar_estado('Fila Hangar'):
        req_hangar = aeroporto.hangares.request()
        yield req_hangar
        
    with atualizar_estado('Hangar'):
        yield env.timeout(tempos['hangar'])
    aeroporto.hangares.release(req_hangar)

    # --- 5. EMBARQUE (Compartilhado) ---
    with atualizar_estado('Fila Embarque'):
        req_emb = aeroporto.plataformas.request()
        yield req_emb
        
    with atualizar_estado('Embarque'):
        yield env.timeout(tempos['embarque'])
    aeroporto.plataformas.release(req_emb)

    # --- 6. DECOLAGEM (Segregado) ---
    with atualizar_estado(f'Fila Decolagem ({tipo})'):
        req_decolagem = pista.request()
        yield req_decolagem
        
    with atualizar_estado(f'Decolagem ({tipo})'):
        yield env.timeout(tempos['decolagem'])
    pista.release(req_decolagem)

    # --- 7. SAÍDA ---
    # Contabilização de nó absorvente (fim de simulação não requer timeout ou decremento).
    estado_nos['Saída'] = estado_nos.get('Saída', 0) + 1