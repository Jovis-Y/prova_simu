from src.topologia import estado_nos

def ciclo_aeronave_visual(env, id_aeronave, tipo, aeroporto):
    # --- CHEGADA ---
    estado_nos['Chegada'] += 1
    yield env.timeout(1)
    estado_nos['Chegada'] -= 1
    
    # --- POUSO (Segregado) ---
    estado_nos[f'Fila Pouso ({tipo})'] += 1
    pista = aeroporto.pistas_pequenas if tipo == 'P' else aeroporto.pista_grande
    with pista.request() as req:
        yield req
        estado_nos[f'Fila Pouso ({tipo})'] -= 1
        estado_nos[f'Pouso ({tipo})'] += 1
        yield env.timeout(40 if tipo == 'P' else 60)
        estado_nos[f'Pouso ({tipo})'] -= 1

    # --- DESEMBARQUE (Compartilhado) ---
    estado_nos['Fila Desemb'] += 1
    with aeroporto.plataformas.request() as req:
        yield req
        estado_nos['Fila Desemb'] -= 1
        estado_nos['Desembarque'] += 1
        yield env.timeout(20 if tipo == 'P' else 40)
        estado_nos['Desembarque'] -= 1

    # --- HANGAR (Compartilhado) ---
    estado_nos['Fila Hangar'] += 1
    with aeroporto.hangares.request() as req:
        yield req
        estado_nos['Fila Hangar'] -= 1
        estado_nos['Hangar'] += 1
        yield env.timeout(35 if tipo == 'P' else 70)
        estado_nos['Hangar'] -= 1

    # --- EMBARQUE (Compartilhado) ---
    estado_nos['Fila Embarque'] += 1
    with aeroporto.plataformas.request() as req:
        yield req
        estado_nos['Fila Embarque'] -= 1
        estado_nos['Embarque'] += 1
        yield env.timeout(30 if tipo == 'P' else 60)
        estado_nos['Embarque'] -= 1

    # --- DECOLAGEM (Segregado) ---
    estado_nos[f'Fila Decolagem ({tipo})'] += 1
    with pista.request() as req:
        yield req
        estado_nos[f'Fila Decolagem ({tipo})'] -= 1
        estado_nos[f'Decolagem ({tipo})'] += 1
        yield env.timeout(40 if tipo == 'P' else 60)
        estado_nos[f'Decolagem ({tipo})'] -= 1

    # --- SAÍDA ---
    estado_nos['Saída'] += 1