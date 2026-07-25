import logging
import pandas as pd
from typing import Any, Generator

from src import ciclo_aeronave_visual 

logger = logging.getLogger(__name__)

def gerador_chegadas(env: Any, aeroporto: Any, arquivo_csv: str) -> Generator:
    try:
        df = pd.read_csv(arquivo_csv, delimiter=',')
        
        colunas_necessarias = {'id', 'tipo', 'horario_chegada'}
        if not colunas_necessarias.issubset(df.columns):
            raise KeyError(f"O CSV '{arquivo_csv}' não possui todas as colunas necessárias: {colunas_necessarias}")

        df['id'] = df['id'].astype(str).str.strip()
        df['tipo'] = df['tipo'].astype(str).str.strip().str.upper()
        df['horario_chegada'] = pd.to_numeric(df['horario_chegada'], errors='coerce')
        
        if df['horario_chegada'].isna().any():
            logger.warning("Detectados horários de chegada inválidos. Estas linhas serão ignoradas.")
            df = df.dropna(subset=['horario_chegada'])

        df = df.sort_values(by='horario_chegada', ascending=True)

        logger.info(f"Arquivo '{arquivo_csv}' carregado com sucesso. Iniciando agendamento para {len(df)} aeronaves.")

        for row in df.itertuples(index=False):
            id_aeronave = row.id
            tipo = row.tipo
            tempo_chegada = float(row.horario_chegada)
            
            tempo_espera = tempo_chegada - env.now
            
            if tempo_espera > 0:
                yield env.timeout(tempo_espera)
            elif tempo_espera < 0:
                logger.debug(f"Aeronave {id_aeronave} programada para o passado. Inserindo no tempo atual ({env.now}).")
            
            logger.debug(f"[{env.now:.2f}] Iniciando ciclo da aeronave {id_aeronave} (Tipo: {tipo})")
            env.process(ciclo_aeronave_visual(env, id_aeronave, tipo, aeroporto))
            
    except FileNotFoundError:
        logger.error(f"ERRO CRÍTICO: Arquivo '{arquivo_csv}' não encontrado no diretório especificado.")
    except KeyError as e:
        logger.error(f"ERRO DE ESTRUTURA: {e}")
    except pd.errors.EmptyDataError:
        logger.error(f"ERRO: O arquivo '{arquivo_csv}' está vazio.")
    except Exception as e:
        logger.critical(f"ERRO INESPERADO no gerador de chegadas: {e}")