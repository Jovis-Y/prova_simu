import networkx as nx
import matplotlib.pyplot as plt

class SimuladorAeroporto:
    def __init__(self, total_aeronaves: int):
        self.grafo = nx.DiGraph()
        self.total_aeronaves = total_aeronaves
        
        self._configurar_nos_e_posicoes()
        self._configurar_arestas()
        self._inicializar_estados()

    def _configurar_nos_e_posicoes(self) -> None:
        self.posicoes = {
            'Chegada': (0, 3),
            
            'Fila Pouso (P)': (2, 4), 'Pouso (P)': (4, 4),
            'Fila Pouso (G)': (2, 2), 'Pouso (G)': (4, 2),
            
            'Fila Desemb': (6, 3), 'Desembarque': (8, 3), 
            'Fila Hangar': (10, 3), 'Hangar': (12, 3),
            'Fila Embarque': (12, 1), 'Embarque': (10, 1),

            'Fila Decolagem (P)': (8, 2), 'Decolagem (P)': (6, 2),
            'Fila Decolagem (G)': (8, 0), 'Decolagem (G)': (6, 0),
            
            'Saída': (4, 1)
        }
        self.grafo.add_nodes_from(self.posicoes.keys())

    def _configurar_arestas(self) -> None:
        arestas = [
            ('Chegada', 'Fila Pouso (P)'), ('Chegada', 'Fila Pouso (G)'),
            ('Fila Pouso (P)', 'Pouso (P)'), ('Fila Pouso (G)', 'Pouso (G)'),
            
            ('Pouso (P)', 'Fila Desemb'), ('Pouso (G)', 'Fila Desemb'),
            ('Fila Desemb', 'Desembarque'), ('Desembarque', 'Fila Hangar'),
            ('Fila Hangar', 'Hangar'), ('Hangar', 'Fila Embarque'),
            ('Fila Embarque', 'Embarque'),
            
            ('Embarque', 'Fila Decolagem (P)'), ('Embarque', 'Fila Decolagem (G)'),
            ('Fila Decolagem (P)', 'Decolagem (P)'), ('Fila Decolagem (G)', 'Decolagem (G)'),
            
            ('Decolagem (P)', 'Saída'), ('Decolagem (G)', 'Saída')
        ]
        self.grafo.add_edges_from(arestas)

    def _inicializar_estados(self) -> None:
        self.estado_nos = {no: 0 for no in self.grafo.nodes()}
        
    def atualizar_estado_no(self, no: str, quantidade: int) -> None:
        if no in self.estado_nos:
            self.estado_nos[no] = quantidade
        else:
            raise ValueError(f"O nó '{no}' não existe na topologia atual do aeroporto.")

    def visualizar_grafo(self) -> None:
        plt.figure(figsize=(15, 8))
        
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
        plt.axis('off')
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    modelo = SimuladorAeroporto(total_aeronaves=102)
    
    print("--- Inicialização do Sistema ---")
    print(f"Total de Aeronaves a processar: {modelo.total_aeronaves}")
    print(f"Total de Etapas (Nós): {modelo.grafo.number_of_nodes()}")
    print(f"Total de Caminhos (Arestas): {modelo.grafo.number_of_edges()}")
    
    modelo.visualizar_grafo()