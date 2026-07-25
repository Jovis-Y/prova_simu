import pandas as pd
import logging
from typing import Callable, Any, Generator

# Configuração básica de logging para substituir os 'prints' simples e ter melhor controle de debug
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def gerador_chegadas(
    env: Any, 
    aeroporto: Any, 
    arquivo_csv: str, 
    funcao_ciclo_aeronave: Callable, 
    **kwargs
) -> Generator:
    """
    Lê uma base de dados CSV, valida, ordena e faz o agendamento das chegadas 
    das aeronaves no ambiente de simulação.

    Args:
        env: O ambiente de simulação (ex: simpy.Environment).
        aeroporto: O objeto ou recurso que representa o aeroporto.
        arquivo_csv (str): O caminho para o arquivo CSV de chegadas.
        funcao_ciclo_aeronave (Callable): A função que define o ciclo da aeronave 
            (ex: ciclo_aeronave ou ciclo_aeronave_visual).
        **kwargs: Parâmetros extras que sua função de ciclo possa exigir (ex: log_esperas).
    """
    
    try:
        df = pd.read_csv(arquivo_csv, delimiter=',') 
        
        # 1. Validação estrutural: verificar se as colunas mínimas existem
        colunas_obrigatorias = {'id', 'tipo', 'horario_chegada'}
        if not colunas_obrigatorias.issubset(df.columns):
            raise ValueError(f"O CSV deve conter obrigatoriamente as colunas: {colunas_obrigatorias}")

        # 2. Limpeza: Garantir que os horários são números, transformando erros em NaN
        df['horario_chegada'] = pd.to_numeric(df['horario_chegada'], errors='coerce')
        
        # 3. Remover linhas onde o horário de chegada é inválido (NaN)
        linhas_iniciais = len(df)
        df.dropna(subset=['horario_chegada'], inplace=True)
        if len(df) < linhas_iniciais:
            logger.warning(f"{linhas_iniciais - len(df)} linhas ignoradas por 'horario_chegada' inválido.")

        # 4. Ordenação (CRÍTICO): A simulação precisa que os eventos aconteçam em ordem cronológica.
        # Se o CSV estiver desordenado, a simulação no simpy quebraria com tempos negativos.
        df.sort_values(by='horario_chegada', ascending=True, inplace=True)
        
        logger.info(f"Dados carregados com sucesso. Total de {len(df)} aeronaves programadas.")

        # 5. Iteração sobre as aeronaves programadas
        for index, row in df.iterrows():
            id_aeronave = str(row['id']).strip()
            tipo = str(row['tipo']).strip().upper()
            tempo_chegada = float(row['horario_chegada'])
            
            # Calcula quanto tempo falta no ambiente de simulação para a chegada desta aeronave
            espera = tempo_chegada - env.now
            
            # Aguarda o momento exato da chegada no mundo simulado
            if espera > 0:
                yield env.timeout(espera)
            elif espera < 0:
                # Alerta caso uma aeronave esteja atrasada em relação ao relógio da simulação
                logger.debug(f"Aviso: Aeronave {id_aeronave} inserida com atraso simulado de {abs(espera)}.")
            
            # Dispara o processo para esta aeronave no aeroporto.
            # O uso do `**kwargs` repassa qualquer variável extra (como `log_esperas` ou `interface_grafica`).
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