import pandas as pd
from ciclo import ciclo_aeronave_visual

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