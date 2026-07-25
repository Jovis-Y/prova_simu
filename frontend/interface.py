import logging
from typing import Any, Generator
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

try:
    from config import estado_nos
except ImportError:
    logger.warning("Não foi possível importar 'estado_nos' do config. Utilizando dicionário padrão vazio.")
    estado_nos = {}


def gerador_chegadas(env: Any, aeroporto: Any, arquivo_csv: str) -> Generator:
    try:
        df = pd.read_csv(arquivo_csv, delimiter=',')
        
        colunas_necessarias = {'id', 'tipo', 'horario_chegada'}
        if not colunas_necessarias.issubset(df.columns):
            raise KeyError(f"O CSV '{arquivo_csv}' não possui todas as colunas necessárias: {colunas_necessarias}")

        # Limpeza e transformação dos dados
        df['id'] = df['id'].astype(str).str.strip()
        df['tipo'] = df['tipo'].astype(str).str.strip().str.upper()
        df['horario_chegada'] = pd.to_numeric(df['horario_chegada'], errors='coerce')
        
        if df['horario_chegada'].isna().any():
            logger.warning("Detectados horários de chegada inválidos. As respectivas linhas serão ignoradas.")
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
            
            # Importação tardia opcional caso ocorra dependência circular, ou chamada direta se estruturado
            from src.ciclo import ciclo_aeronave_visual
            env.process(ciclo_aeronave_visual(env, id_aeronave, tipo, aeroporto))
            
    except FileNotFoundError:
        logger.error(f"ERRO CRÍTICO: Arquivo '{arquivo_csv}' não encontrado no diretório especificado.")
    except KeyError as e:
        logger.error(f"ERRO DE ESTRUTURA: {e}")
    except pd.errors.EmptyDataError:
        logger.error(f"ERRO: O arquivo '{arquivo_csv}' está vazio.")
    except Exception as e:
        logger.critical(f"ERRO INESPERADO no gerador de chegadas: {e}")


def inicializar_grafo() -> nx.DiGraph:
    grafo = nx.DiGraph()
    
    posicoes = {
        'Chegada': (0, 2),
        'Espera_Pouso': (1, 2),
        'Pista_Pouso': (2, 2),
        'Desemb/Hangar': (3, 1),
        'Espera_Embarque': (4, 1),
        'Espera_Decolagem': (5, 0),
        'Pista_Decolagem': (6, 0),
        'Saída': (7, 0)
    }
    
    for no, pos in posicoes.items():
        grafo.add_node(no, pos=pos)
        
    arestas = [
        ('Chegada', 'Espera_Pouso'),
        ('Espera_Pouso', 'Pista_Pouso'),
        ('Pista_Pouso', 'Desemb/Hangar'),
        ('Desemb/Hangar', 'Espera_Embarque'),
        ('Espera_Embarque', 'Espera_Decolagem'),
        ('Espera_Decolagem', 'Pista_Decolagem'),
        ('Pista_Decolagem', 'Saída')
    ]
    grafo.add_edges_from(arestas)
    
    return grafo


def renderizar_frame(ax: plt.Axes, G: nx.DiGraph) -> None:
    pos = nx.get_node_attributes(G, 'pos')
    
    labels = {}
    node_colors = []
    
    for no in G.nodes():
        qtd = estado_nos.get(no, 0)
        labels[no] = f"{no}\n({qtd})"
        
        if qtd > 0:
            node_colors.append('#90EE90')
        else:
            node_colors.append('#ADD8E6')
            
    nx.draw(
        G, 
        pos, 
        ax=ax, 
        with_labels=True, 
        labels=labels, 
        node_size=4000, 
        node_color=node_colors, 
        node_shape="s", 
        font_size=9, 
        font_weight='bold', 
        edge_color='gray', 
        arrows=True, 
        arrowsize=20,
        margins=0.1
    )