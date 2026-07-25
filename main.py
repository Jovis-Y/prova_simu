import os
import sys
import simpy
import logging
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from pathlib import Path
from typing import List, Dict, Any

# Adiciona o diretório atual ao path para garantir que os módulos locais sejam encontrados
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Define o caminho padrão apontando para a pasta 'data/'
caminho_csv = str(Path("data") / "chegadas.csv")

# Configuração global de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

try:
    from config import TOTAL_AERONAVES, estado_nos
    from src.aeroporto import Aeroporto
    from src.aeronave import ciclo_aeronave
    from src.modelos import AeroportoVisual
    from src.gerador import gerador_chegadas
    from frontend.interface import inicializar_grafo, renderizar_frame
except ImportError as e:
    logging.error(f"Falha ao importar módulos internos do projeto: {e}")
    logging.error("Certifique-se de que os pacotes 'config', 'src' e 'frontend' existem.")
    sys.exit(1)

def executar_modo_texto(arquivo_chegadas: str = caminho_csv) -> None:
    """Executa a simulação discreta focada na coleta e exibição de métricas (modo texto)."""
    logging.info(f"{'='*50}\nIniciando Simulação Discreta do Aeroporto (Modo Métricas)...\n{'='*50}")
    
    log_esperas: List[Dict[str, Any]] = []
    
    # Inicialização do ambiente SimPy
    env = simpy.Environment()
    aeroporto = Aeroporto(env)
    
    # Adicionando o processo gerador de chegadas ao ambiente passando ciclo_aeronave
    env.process(
        gerador_chegadas(
            env, 
            aeroporto, 
            arquivo_chegadas, 
            ciclo_aeronave, 
            log_esperas=log_esperas
        )
    )
    
    # Executa a simulação até que todos os eventos terminem
    env.run()
    
    logging.info(f"{'='*50}\nTempo final da simulação: {env.now:.1f} minutos\n{'='*50}")

    # Transformando os logs em um DataFrame do Pandas para análise
    df_metricas = pd.DataFrame(log_esperas)
    if df_metricas.empty:
        logging.warning("Nenhum dado foi registrado durante a simulação.")
        return

    logging.info("Calculando gargalos e médias de tempo de espera...")
    
    # Colunas de interesse para avaliação de gargalos
    colunas_espera = [
        'Espera_Pouso', 'Espera_Desemb', 'Espera_Hangar', 
        'Espera_Embarque', 'Espera_Decolagem'
    ]
    
    # Filtra apenas as colunas que realmente foram registradas no log de forma segura
    colunas_presentes = [col for col in colunas_espera if col in df_metricas.columns]
    
    if colunas_presentes:
        medias_por_tipo = df_metricas.groupby('Tipo')[colunas_presentes].mean()
        print("\n--- MÉDIA DE TEMPO DE ESPERA POR FILA (em minutos) ---")
        print(medias_por_tipo.to_string())
    else:
        logging.warning("As colunas de espera esperadas não foram encontradas no log.")

def executar_modo_visual(arquivo_chegadas: str = caminho_csv, arquivo_saida: str = 'simulacao_aeroporto.mp4') -> None:
    """Executa a simulação com renderização visual (Matplotlib/NetworkX) e salva em vídeo."""
    logging.info("Inicializando ambiente visual da simulação...")
    
    fig, ax = plt.subplots(figsize=(15, 7))
    env = simpy.Environment()
    aeroporto = AeroportoVisual(env)
    
    # No modo visual, o gerador também recebe o ciclo da aeronave agora
    env.process(gerador_chegadas(env, aeroporto, arquivo_chegadas, ciclo_aeronave))
    
    try:
        G = inicializar_grafo()
    except Exception as e:
        logging.error(f"Erro ao inicializar topologia visual do grafo: {e}")
        return

    def atualizar_frame(frame: int):
        """Atualiza os elementos gráficos a cada tick da animação."""
        ax.clear()
        
        # Condição de parada baseada no processamento total das aeronaves
        if estado_nos.get('Saída', 0) >= TOTAL_AERONAVES:
            ax.text(0.5, 0.95, "SIMULAÇÃO CONCLUÍDA!", 
                    transform=ax.transAxes, ha='center', 
                    fontsize=14, color='red', weight='bold')
        else:
            env.run(until=env.now + 10)
        
        # Renderiza os nós e arestas no frame atual
        renderizar_frame(ax, G)
        ax.set_title(f"ACD Aeroporto (Foco Pistas) - Tempo Simulado: {env.now} min")

    def gerador_frames():
        """Gera os frames até que todas as aeronaves tenham saído do sistema."""
        frame = 0
        while estado_nos.get('Saída', 0) < TOTAL_AERONAVES:
            yield frame
            frame += 1
        yield frame

    logging.info("Processando a simulação e gerando o vídeo... Este processo pode levar alguns minutos.")
    
    ani = animation.FuncAnimation(
        fig, atualizar_frame, frames=gerador_frames, 
        interval=100, cache_frame_data=False, save_count=2000
    )
    
    plt.tight_layout()
    
    # Tenta salvar o arquivo; se falhar (ex: falta de FFmpeg), mostra a interface estática
    try:
        ani.save(arquivo_saida, writer='ffmpeg', fps=10)
        logging.info(f"Vídeo salvo com sucesso: {arquivo_saida}")
    except Exception as e:
        logging.error(f"Erro crítico ao salvar o vídeo (Verifique se o FFmpeg está instalado): {e}")
        logging.info("Exibindo interface gráfica como alternativa fallback.")
        plt.show()

def main() -> None:
    """Função principal que analisa argumentos de CLI e aciona o modo escolhido."""
    parser = argparse.ArgumentParser(
        description="Simulador de Tráfego Aeroportuário (Eventos Discretos)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--modo', 
        type=str, 
        choices=['texto', 'visual'], 
        default='texto',
        help="Define o modo de execução da simulação: 'texto' para gerar métricas e 'visual' para gerar vídeo."
    )
    
    parser.add_argument(
        '--arquivo', 
        type=str, 
        default=caminho_csv,  # <- Atualizado para usar o caminho correto com a pasta 'data/'
        help="Caminho para o arquivo CSV com a agenda de chegadas."
    )
    
    parser.add_argument(
        '--saida', 
        type=str, 
        default='simulacao_aeroporto.mp4',
        help="Nome do arquivo de vídeo de saída (aplicável apenas no modo visual)."
    )

    args = parser.parse_args()

    if args.modo == 'texto':
        executar_modo_texto(arquivo_chegadas=args.arquivo)
    elif args.modo == 'visual':
        executar_modo_visual(arquivo_chegadas=args.arquivo, arquivo_saida=args.saida)


if __name__ == '__main__':
    main()