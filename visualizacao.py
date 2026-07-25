import pandas as pd
from modelos import ciclo_aeronave_visual

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