import networkx as nx

G = nx.DiGraph()

# Layout: Extremidades bifurcadas (Y=4 e Y=2) e centro unificado (Y=3)
posicoes = {
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

G.add_edges_from([
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
])

estado_nos = {no: 0 for no in G.nodes()}
total_aeronaves = 102