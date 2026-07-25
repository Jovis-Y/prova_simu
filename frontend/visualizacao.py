import logging
import pandas as pd
from typing import Any, Generator
from src.modelos import ciclo_aeronave_visual

# Configuração básica do sistema de logs para rastrear a simulação
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def gerador_chegadas(env: Any, aeroporto: Any, arquivo_csv: str) -> Generator:
    """
    Lê a base de dados CSV, valida e limpa os dados, e realiza o agendamento
    cronológico das chegadas das aeronaves no ambiente de simulação.

    Parâmetros:
    -----------
    env : simpy.Environment
        O ambiente de simulação de eventos discretos.
    aeroporto : Any
        O objeto ou recurso que representa a infraestrutura aeroportuária.
    arquivo_csv : str
        O caminho para o arquivo CSV. Espera-se as colunas 'id', 'tipo' e 'horario_chegada'.
    """
    try:
        # Leitura da base de dados
        df = pd.read_csv(arquivo_csv, delimiter=',')
        
        # Validação estrutural: garante que o CSV tem as colunas requeridas
        colunas_necessarias = {'id', 'tipo', 'horario_chegada'}
        if not colunas_necessarias.issubset(df.columns):
            raise KeyError(f"O CSV deve conter obrigatoriamente as colunas: {colunas_necessarias}")

        # Limpeza e padronização dos dados
        df['tipo'] = df['tipo'].astype(str).str.strip().str.upper()
        
        # Converte para numérico; transforma dados inválidos (como strings não numéricas) em NaN
        df['horario_chegada'] = pd.to_numeric(df['horario_chegada'], errors='coerce')
        
        # Remove eventuais linhas com falha de conversão nos horários
        if df['horario_chegada'].isna().any():
            logging.warning("Detectados horários de chegada inválidos. Estas linhas serão ignoradas.")
            df = df.dropna(subset=['horario_chegada'])

        # ORDENAÇÃO CRONOLÓGICA: Fundamental para o relógio da simulação avançar corretamente
        df = df.sort_values(by='horario_chegada', ascending=True)

        logging.info(f"Iniciando agendamento para {len(df)} aeronaves validadas.")

        # Iteração otimizada utilizando itertuples (muito mais rápido que iterrows)
        for row in df.itertuples(index=False):
            id_aeronave = row.id
            tipo = row.tipo
            tempo_chegada = float(row.horario_chegada)
            
            # O tempo a aguardar é a diferença entre o tempo agendado e o relógio atual
            tempo_espera = tempo_chegada - env.now
            
            if tempo_espera > 0:
                yield env.timeout(tempo_espera)
            elif tempo_espera < 0:
                # Alerta se o gerador estiver atrasado em relação ao cronograma
                logging.debug(f"Aeronave {id_aeronave} inserida com atraso relativo ao relógio ({tempo_espera}).")
            
            # Dispara o processo para esta aeronave no mundo simulado
            env.process(ciclo_aeronave_visual(env, id_aeronave, tipo, aeroporto))
            logging.debug(f"Processo instanciado: Aeronave {id_aeronave} [{tipo}] no tempo {env.now}.")
            
    except FileNotFoundError:
        logging.error(f"Falha de execução: Arquivo '{arquivo_csv}' não foi encontrado no sistema.")
    except KeyError as ke:
        logging.error(f"Erro de integridade nos dados: {ke}")
    except Exception as e:
        logging.critical(f"Erro inesperado no gerador de chegadas: {e}")