from typing import Any, Dict, List
import simpy

# Supõe-se que TEMPOS_ATIVIDADES está neste arquivo
from config import TEMPOS_ATIVIDADES

def processar_fase(env: simpy.Environment, 
                   nome_fase: str, 
                   recurso: simpy.Resource, 
                   tempo_atividade: float, 
                   id_aeronave: str, 
                   tipo: str, 
                   chave_log: str, 
                   metricas: Dict[str, Any]):
    """
    Função auxiliar geradora que encapsula a lógica repetitiva de entrar em uma fila,
    aguardar um recurso, registrar a espera e realizar a atividade.
    """
    chegada_fila = env.now
    
    with recurso.request() as req:
        yield req  # Aguarda na fila até o recurso liberar
        
        # Calcula e registra o tempo de espera
        tempo_espera = env.now - chegada_fila
        metricas[chave_log] = tempo_espera
        
        print(f"[{env.now:06.1f}] Voo {id_aeronave} ({tipo}) inicia {nome_fase}. (Espera: {tempo_espera:.1f} min)")
        
        # Executa a atividade consumindo tempo no simulador
        yield env.timeout(tempo_atividade)


def ciclo_aeronave(env: simpy.Environment, 
                   id_aeronave: str, 
                   tipo: str, 
                   aeroporto: Any, 
                   log_esperas: List[Dict[str, Any]]):
    """ 
    Modela o fluxo de vida (ACD) de uma aeronave no sistema, desde o pouso 
    até a sua decolagem, coletando métricas de tempo de espera.
    """
    # Resgate seguro dos tempos; previne erro caso o tipo não exista na config
    tempos = TEMPOS_ATIVIDADES.get(tipo)
    if not tempos:
        print(f"[{env.now:06.1f}] ERRO: Tempos para o tipo '{tipo}' não encontrados na configuração.")
        return
    
    # Define qual pista será usada com base no porte da aeronave
    pista_adequada = aeroporto.pistas_pequenas if tipo == 'P' else aeroporto.pista_grande
    
    # Dicionário inicial para armazenar os logs estruturados desta aeronave
    metricas_voo = {
        'ID': id_aeronave,
        'Tipo': tipo
    }
    
    # Roteiro do ciclo: (Nome da Fase, Recurso Utilizado, Tempo da Atividade, Chave do Log)
    fases_do_voo = [
        ("POUSO", pista_adequada, tempos['pouso'], 'Espera_Pouso'),
        ("DESEMBARQUE", aeroporto.plataformas, tempos['desembarque'], 'Espera_Desemb'),
        ("HANGAR", aeroporto.hangares, tempos['hangar'], 'Espera_Hangar'),
        ("EMBARQUE", aeroporto.plataformas, tempos['embarque'], 'Espera_Embarque'),
        ("DECOLAGEM", pista_adequada, tempos['decolagem'], 'Espera_Decolagem')
    ]
    
    # Itera sobre cada fase sequencialmente delegando (yield from) para a função auxiliar
    for nome_fase, recurso, tempo, chave_log in fases_do_voo:
        yield from processar_fase(
            env=env,
            nome_fase=nome_fase,
            recurso=recurso,
            tempo_atividade=tempo,
            id_aeronave=id_aeronave,
            tipo=tipo,
            chave_log=chave_log,
            metricas=metricas_voo
        )

    print(f"[{env.now:06.1f}] ---> Voo {id_aeronave} ({tipo}) FINALIZOU e deixou o sistema.")
    
    # Salva o log final preenchido no sistema central de métricas
    log_esperas.append(metricas_voo)