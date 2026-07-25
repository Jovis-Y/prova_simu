import networkx as nx
import matplotlib.pyplot as plt

class SimuladorAeroporto:
    """
    Classe para modelar e visualizar o fluxo de aeronaves em um aeroporto,
    utilizando grafos direcionados para representar filas e pátios.
    """
    def __init__(self, total_aeronaves: int):
        self.grafo = nx.DiGraph()
        self.total_aeronaves = total_aeronaves
        
        # Inicializa a estrutura do grafo
        self._configurar_nos_e_posicoes()
        self._configurar_arestas()
        self._inicializar_estados()

    def _configurar_nos_e_posicoes(self) -> None:
        """
        Define os nós e suas coordenadas espaciais.
        Layout: Extremidades bifurcadas e centro unificado.
        """
        self.posicoes = {
            'Chegada': (0, 3),
            
            # --- Bifurcação de Pouso ---
            'Fila Pouso (P)': (2, 4), 'Pouso (P)': (4, 4),
            'Fila Pouso (G)': (2, 2), 'Pouso (G)': (4, 2),
            
            # --- Centro Compartilhado ---
            'Fila Desemb': (6, 3), 'Desembarque': (8, 3), 
            'Fila Hangar': (10, 3), 'Hangar': (12, 3),
            'Fila Embarque': (12, 1), 'Embarque': (10, 1),

            # --- Bifurcação de Decolagem ---
            'Fila Decolagem (P)': (8, 2), 'Decolagem (P)': (6, 2),
            'Fila Decolagem (G)': (8, 0), 'Decolagem (G)': (6, 0),
            
            'Saída': (4, 1)
        }
        # Adiciona os nós ao grafo utilizando as chaves do dicionário
        self.grafo.add_nodes_from(self.posicoes.keys())

    def _configurar_arestas(self) -> None:
        """Define as conexões direcionadas (arestas) determinando o fluxo do aeroporto."""
        arestas = [
            # Separa na chegada
            ('Chegada', 'Fila Pouso (P)'), ('Chegada', 'Fila Pouso (G)'),
            ('Fila Pouso (P)', 'Pouso (P)'), ('Fila Pouso (G)', 'Pouso (G)'),
            
            # Unifica no desembarque e segue pelo centro
            ('Pouso (P)', 'Fila Desemb'), ('Pouso (G)', 'Fila Desemb'),
            ('Fila Desemb', 'Desembarque'), ('Desembarque', 'Fila Hangar'),
            ('Fila Hangar', 'Hangar'), ('Hangar', 'Fila Embarque'),
            ('Fila Embarque', 'Embarque'),
            
            # Separa novamente para a decolagem
            ('Embarque', 'Fila Decolagem (P)'), ('Embarque', 'Fila Decolagem (G)'),
            ('Fila Decolagem (P)', 'Decolagem (P)'), ('Fila Decolagem (G)', 'Decolagem (G)'),
            
            # Unifica na saída
            ('Decolagem (P)', 'Saída'), ('Decolagem (G)', 'Saída')
        ]
        self.grafo.add_edges_from(arestas)

    def _inicializar_estados(self) -> None:
        """Cria um dicionário para rastrear a quantidade de aeronaves em cada nó."""
        self.estado_nos = {no: 0 for no in self.grafo.nodes()}
        
    def atualizar_estado_no(self, no: str, quantidade: int) -> None:
        """
        Atualiza dinamicamente o número de aeronaves presentes em um nó específico.
        Ideal para integrar com loops de simulação de tempo.
        """
        if no in self.estado_nos:
            self.estado_nos[no] = quantidade
        else:
            raise ValueError(f"O nó '{no}' não existe na topologia atual do aeroporto.")

    def visualizar_grafo(self) -> None:
        """Gera uma representação visual do fluxo utilizando matplotlib."""
        plt.figure(figsize=(15, 8))
        
        # Desenha os componentes do grafo
        nx.draw(
            self.grafo, 
            pos=self.posicoes, 
            with_labels=True, 
            node_color='#87CEFA', 
            node_size=3500, 
            font_size=9, 
            font_weight='bold', 
            arrows=True,
            arrowsize=20,
            edge_color='#555555'
        )
        
        plt.title(f"Diagrama de Fluxo Aeroportuário\n(Capacidade Simulada: {self.total_aeronaves} Aeronaves)", fontsize=16)
        plt.axis('off') # Remove os eixos numéricos para melhorar o design
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Instancia o modelo com a constante de aeronaves predefinida
    modelo = SimuladorAeroporto(total_aeronaves=102)
    
    # Exibe metadados no console
    print("--- Inicialização do Sistema ---")
    print(f"Total de Aeronaves a processar: {modelo.total_aeronaves}")
    print(f"Total de Etapas (Nós): {modelo.grafo.number_of_nodes()}")
    print(f"Total de Caminhos (Arestas): {modelo.grafo.number_of_edges()}")
    
    # Renderiza o diagrama visual
    modelo.visualizar_grafo()