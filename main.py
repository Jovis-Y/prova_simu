import simpy
import pandas as pd
from aeroporto import Aeroporto
from gerador import gerador_chegadas

if __name__ == '__main__':
    print("Iniciando Simulação Discreta do Aeroporto...\n" + "="*50)
    
    # Lista para armazenar métricas; agora local, enviada por referência para não ser global
    log_esperas = []
    
    # Cria o ambiente de simulação e a instância do aeroporto
    env = simpy.Environment()
    aeroporto = Aeroporto(env)
    
    # Inicia o processo do gerador lendo o arquivo especificado
    env.process(gerador_chegadas(env, aeroporto, 'chegadas.csv', log_esperas))
    
    # Executa até a exaustão de todos os eventos programados no ambiente
    env.run()
    
    print("="*50 + f"\nTempo final da simulação: {env.now:.1f} minutos\n")
    
    # Transforma o log num DataFrame Pandas para facilitar a análise de gargalos
    df_metricas = pd.DataFrame(log_esperas)
    if not df_metricas.empty:
        print("MÉDIA DE TEMPO DE ESPERA POR FILA (em minutos):")
        
        # Agrupa pelo 'Tipo' da aeronave e calcula a média das colunas de espera
        medias_por_tipo = df_metricas.groupby('Tipo')[
            ['Espera_Pouso', 'Espera_Desemb', 'Espera_Hangar', 'Espera_Embarque', 'Espera_Decolagem']
        ].mean()
        
        print(medias_por_tipo)

import simpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Importações dos módulos locais separados
from config import TOTAL_AERONAVES, estado_nos
from modelos import AeroportoVisual
from gerador import gerador_chegadas
from visualizacao import inicializar_grafo, renderizar_frame

def main():
    # Inicializando gráficos
    fig, ax = plt.subplots(figsize=(15, 7))
    
    # Inicializando ambiente SimPy
    env = simpy.Environment()
    aeroporto = AeroportoVisual(env)
    
    # Iniciando o processo gerador
    env.process(gerador_chegadas(env, aeroporto, 'chegadas.csv'))
    
    # Obtendo a topologia visual do Grafo
    G = inicializar_grafo()
    
    def atualizar_frame(frame):
        ax.clear()
        
        if estado_nos['Saída'] >= TOTAL_AERONAVES:
            ax.text(0.5, 0.95, "SIMULAÇÃO CONCLUÍDA!", 
                    transform=ax.transAxes, ha='center', 
                    fontsize=14, color='red', weight='bold')
        else:
            # Avança a simulação em passos de 10 min por frame
            env.run(until=env.now + 10)
        
        # Chama módulo de renderização visual
        renderizar_frame(ax, G)
        ax.set_title(f"ACD Aeroporto (Foco Pistas) - Tempo Simulado: {env.now} min")

    def gerador_frames():
        """ Gera frames apenas enquanto a simulação não acabar """
        frame = 0
        while estado_nos['Saída'] < TOTAL_AERONAVES:
            yield frame
            frame += 1
        yield frame # Frame extra de conclusão
        
    ani = animation.FuncAnimation(
        fig, atualizar_frame, frames=gerador_frames, 
        interval=100, cache_frame_data=False, save_count=2000
    )
    
    plt.tight_layout()
    print("Processando a simulação e gerando o vídeo... Aguarde.")
    
    # Salvando a simulação (Certifique-se de ter o FFmpeg instalado)
    try:
        ani.save('simulacao_2_pista_P_e_1_pista_G_a_mais.mp4', writer='ffmpeg', fps=10)
        print("Vídeo salvo com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar vídeo: {e}")
        # plt.show() # Descomente se preferir ver a janela ao invés de salvar

if __name__ == "__main__":
    main()