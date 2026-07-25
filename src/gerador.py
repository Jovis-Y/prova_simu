import pandas as pd
from src.aeronave import ciclo_aeronave

def gerador_chegadas(env, aeroporto, arquivo_csv, log_esperas):
    """ 
    Lê o arquivo CSV de entrada e insere as aeronaves no sistema de simulação
    nos momentos (tempos) correspondentes aos seus horários de chegada.
    """
    try:
        # Espera-se que o CSV possua as colunas: id, tipo, horario_chegada
        df = pd.read_csv(arquivo_csv, delimiter=',')
        
        for _, row in df.iterrows():
            id_aeronave = row['id']
            tipo = str(row['tipo']).strip().upper()
            tempo_chegada = float(row['horario_chegada'])
            
            # Trava o processo gerador até o tempo exato de chegada dessa aeronave
            if tempo_chegada > env.now:
                yield env.timeout(tempo_chegada - env.now)
            
            # Inicia o processo de fluxo da aeronave independentemente do gerador
            env.process(ciclo_aeronave(env, id_aeronave, tipo, aeroporto, log_esperas))
            
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{arquivo_csv}' não encontrado no diretório.")
        print("Crie um CSV com colunas: id, tipo, horario_chegada")

import pandas as pd
from src.modelos import ciclo_aeronave_visual

def gerador_chegadas(env, aeroporto, arquivo_csv):
    """
    Lê a base de dados CSV e faz o agendamento das chegadas das aeronaves.
    """
    try:
        df = pd.read_csv(arquivo_csv, delimiter=',') 
        for _, row in df.iterrows():
            id_aeronave = row['id']
            tipo = str(row['tipo']).strip().upper()
            tempo_chegada = float(row['horario_chegada'])
            
            # Aguarda até o momento da chegada no mundo simulado
            if tempo_chegada > env.now:
                yield env.timeout(tempo_chegada - env.now)
            
            # Dispara o processo para esta aeronave
            env.process(ciclo_aeronave_visual(env, id_aeronave, tipo, aeroporto))
            
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{arquivo_csv}' não encontrado no diretório.")

import pandas as pd
from src.ciclo import ciclo_aeronave_visual

def gerador_chegadas(env, aeroporto, arquivo_csv):
    try:
        df = pd.read_csv(arquivo_csv, delimiter=',') 
        for _, row in df.iterrows():
            id_aeronave = row['id']
            tipo = str(row['tipo']).strip().upper()
            tempo_chegada = float(row['horario_chegada'])
            
            # Aguarda o momento certo para injetar a aeronave no ambiente
            if tempo_chegada > env.now:
                yield env.timeout(tempo_chegada - env.now)
            
            env.process(ciclo_aeronave_visual(env, id_aeronave, tipo, aeroporto))
            
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{arquivo_csv}' não encontrado no diretório.")