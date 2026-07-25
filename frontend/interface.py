import logging
import pandas as pd
from typing import Any
from src.ciclo import ciclo_aeronave_visual

# Configuração básica de log (pode ser ajustada no arquivo principal do seu projeto)
logger = logging.getLogger(__name__)

def gerador_chegadas(env: Any, aeroporto: Any, arquivo_csv: str):
    """
    Lê um arquivo CSV contendo os dados de chegada das aeronaves e agenda
    a entrada de cada uma no ambiente de simulação no tempo correto.

    Args:
        env: O ambiente de simulação do SimPy (simpy.Environment).
        aeroporto: O objeto, recurso ou infraestrutura representando o aeroporto.
        arquivo_csv (str): Caminho para o arquivo CSV com os dados das aeronaves.
    """
    try:
        # 1. Carregamento dos dados
        df = pd.read_csv(arquivo_csv, delimiter=',') 
        
        # 2. Validação das colunas obrigatórias
        colunas_necessarias = {'id', 'tipo', 'horario_chegada'}
        if not colunas_necessarias.issubset(df.columns):
            raise KeyError(f"O CSV '{arquivo_csv}' não possui todas as colunas necessárias: {colunas_necessarias}")

        # 3. Ordenação (CRÍTICO)
        # Garante que os horários de chegada estejam em ordem crescente. 
        # O SimPy falhará se tentarmos fazer um yield com tempo negativo no futuro.
        df = df.sort_values(by='horario_chegada')
        
        logger.info(f"Arquivo '{arquivo_csv}' carregado com sucesso. {len(df)} aeronaves programadas.")

        # 4. Iteração performática
        # O 'itertuples' é significativamente mais rápido e eficiente que o 'iterrows' no Pandas
        for row in df.itertuples(index=False):
            # Limpeza e extração dos dados
            id_aeronave = str(row.id).strip()
            tipo = str(row.tipo).strip().upper()
            
            try:
                tempo_chegada = float(row.horario_chegada)
            except ValueError:
                logger.error(f"Horário de chegada inválido para a aeronave {id_aeronave}: {row.horario_chegada}. Ignorando...")
                continue
            
            # 5. Tratamento de tempos no passado
            if tempo_chegada < env.now:
                logger.warning(f"Aeronave {id_aeronave} programada para o passado ({tempo_chegada}). Ajustando para o tempo atual ({env.now}).")
                tempo_chegada = env.now

            # 6. Aguarda o momento certo para injetar a aeronave no ambiente
            if tempo_chegada > env.now:
                yield env.timeout(tempo_chegada - env.now)
            
            # 7. Injeção no ambiente
            logger.debug(f"[{env.now:.2f}] Iniciando ciclo da aeronave {id_aeronave} (Tipo: {tipo})")
            env.process(ciclo_aeronave_visual(env, id_aeronave, tipo, aeroporto))
            
    # 8. Tratamento de Erros Expandido
    except FileNotFoundError:
        logger.error(f"ERRO CRÍTICO: Arquivo '{arquivo_csv}' não encontrado no diretório especificado.")
    except KeyError as e:
        logger.error(f"ERRO DE ESTRUTURA: {e}")
    except pd.errors.EmptyDataError:
        logger.error(f"ERRO: O arquivo '{arquivo_csv}' está vazio.")
    except Exception as e:
        logger.error(f"ERRO INESPERADO no gerador de chegadas: {e}")