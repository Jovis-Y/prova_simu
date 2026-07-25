from typing import Any, Dict, List
import simpy

from config import TEMPOS_ATIVIDADES

def processar_fase(env: simpy.Environment, 
                   nome_fase: str, 
                   recurso: simpy.Resource, 
                   tempo_atividade: float, 
                   id_aeronave: str, 
                   tipo: str, 
                   chave_log: str, 
                   metricas: Dict[str, Any]):
    chegada_fila = env.now
    
    with recurso.request() as req:
        yield req
        
        tempo_espera = env.now - chegada_fila
        metricas[chave_log] = tempo_espera
        
        print(f"[{env.now:06.1f}] Voo {id_aeronave} ({tipo}) inicia {nome_fase}. (Espera: {tempo_espera:.1f} min)")
        
        yield env.timeout(tempo_atividade)


def ciclo_aeronave(env: simpy.Environment, 
                   id_aeronave: str, 
                   tipo: str, 
                   aeroporto: Any, 
                   log_esperas: List[Dict[str, Any]]):
    
    tempos = TEMPOS_ATIVIDADES.get(tipo)
    if not tempos:
        print(f"[{env.now:06.1f}] ERRO: Tempos para o tipo '{tipo}' não encontrados na configuração.")
        return
    
    pista_adequada = aeroporto.pistas_pequenas if tipo == 'P' else aeroporto.pista_grande
    
    metricas_voo = {
        'ID': id_aeronave,
        'Tipo': tipo
    }
    
    fases_do_voo = [
        ("POUSO", pista_adequada, tempos['pouso'], 'Espera_Pouso'),
        ("DESEMBARQUE", aeroporto.plataformas, tempos['desembarque'], 'Espera_Desemb'),
        ("HANGAR", aeroporto.hangares, tempos['hangar'], 'Espera_Hangar'),
        ("EMBARQUE", aeroporto.plataformas, tempos['embarque'], 'Espera_Embarque'),
        ("DECOLAGEM", pista_adequada, tempos['decolagem'], 'Espera_Decolagem')
    ]
    
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
    
    log_esperas.append(metricas_voo)