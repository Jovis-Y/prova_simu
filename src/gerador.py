import pandas as pd
import logging
from typing import Callable, Any, Generator

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def gerador_chegadas(
    env: Any, 
    aeroporto: Any, 
    arquivo_csv: str, 
    funcao_ciclo_aeronave: Callable, 
    **kwargs
) -> Generator:
    
    try:
        df = pd.read_csv(arquivo_csv, delimiter=',') 
        
        colunas_obrigatorias = {'id', 'tipo', 'horario_chegada'}
        if not colunas_obrigatorias.issubset(df.columns):
            raise ValueError(f"O CSV deve conter obrigatoriamente as colunas: {colunas_obrigatorias}")

        df['horario_chegada'] = pd.to_numeric(df['horario_chegada'], errors='coerce')
        
        linhas_iniciais = len(df)
        df.dropna(subset=['horario_chegada'], inplace=True)
        if len(df) < linhas_iniciais:
            logger.warning(f"{linhas_iniciais - len(df)} linhas ignoradas por 'horario_chegada' inválido.")

        df.sort_values(by='horario_chegada', ascending=True, inplace=True)
        
        logger.info(f"Dados carregados com sucesso. Total de {len(df)} aeronaves programadas.")

        for index, row in df.iterrows():
            id_aeronave = str(row['id']).strip()
            tipo = str(row['tipo']).strip().upper()
            tempo_chegada = float(row['horario_chegada'])
            
            espera = tempo_chegada - env.now
            
            if espera > 0:
                yield env.timeout(espera)
            elif espera < 0:
                logger.debug(f"Aviso: Aeronave {id_aeronave} inserida com atraso simulado de {abs(espera)}.")
            
            env.process(funcao_ciclo_aeronave(env, id_aeronave, tipo, aeroporto, **kwargs))
            
    except FileNotFoundError:
        logger.error(f"Arquivo '{arquivo_csv}' não encontrado no diretório especificado.")
        logger.error("Certifique-se de criar o arquivo com as colunas: id, tipo, horario_chegada")
    
    except pd.errors.EmptyDataError:
        logger.error(f"O arquivo '{arquivo_csv}' está vazio.")
        
    except ValueError as ve:
        logger.error(f"Erro de Validação de Dados: {ve}")
        
    except Exception as e:
        logger.exception(f"Erro inesperado durante a leitura do gerador de chegadas: {e}")