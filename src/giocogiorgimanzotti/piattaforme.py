def crea_piattaforma(x, y, larghezza, altezza, nome_colore):
    """
    Crea una piattaforma colorata.
    Restituisce un dizionario con tutte le informazioni della piattaforma.
    """
    return {
        'x': x,
        'y': y,
        'larghezza': larghezza,
        'altezza': altezza,
        'nome_colore': nome_colore,
        'colore': COLORI[nome_colore],
        'attiva': True,  # Se la piattaforma è visibile/utilizzabile
        'progresso_scomparsa': 0  # 0 = visibile, 1 = completamente scomparsa
    }


def piattaforma_inizia_scomparsa(piattaforma):
    """Fa iniziare l'animazione di scomparsa di una piattaforma"""
    piattaforma['attiva'] = False


def piattaforma_aggiorna(piattaforma):
    """Aggiorna l'animazione di scomparsa di una piattaforma"""
    if not piattaforma['attiva'] and piattaforma['progresso_scomparsa'] < 1:
        piattaforma['progresso_scomparsa'] += 0.05


def piattaforma_disegna(schermo, piattaforma):
    """Disegna una piattaforma sullo schermo"""
    if piattaforma['progresso_scomparsa'] >= 1:
        return  # Non disegnare se completamente scomparsa
    
    if not piattaforma['attiva']:
        # Animazione di scomparsa: la piattaforma diventa più piccola
        scala = 1 - piattaforma['progresso_scomparsa']
        offset = piattaforma['progresso_scomparsa'] * 20
        
        rett = pygame.Rect(
            piattaforma['x'] + offset,
            piattaforma['y'] + offset,
            piattaforma['larghezza'] * scala,
            piattaforma['altezza'] * scala
        )
    else:
        # Piattaforma normale
        rett = pygame.Rect(piattaforma['x'], piattaforma['y'], 
                          piattaforma['larghezza'], piattaforma['altezza'])
    
    # Disegna il rettangolo colorato
    pygame.draw.rect(schermo, piattaforma['colore'], rett)
    # Disegna il bordo nero
    pygame.draw.rect(schermo, (0, 0, 0), rett, 4)


def piattaforma_contiene_punto(piattaforma, x, y, margine=15):
    """
    Controlla se un punto (x, y) è dentro o vicino alla piattaforma.
    Il margine permette di camminare tra piattaforme adiacenti senza cadere.
    """
    if not piattaforma['attiva'] or piattaforma['progresso_scomparsa'] >= 1:
        return False
    
    # Espandi l'area di controllo con il margine
    return (piattaforma['x'] - margine <= x <= piattaforma['x'] + piattaforma['larghezza'] + margine and 
            piattaforma['y'] - margine <= y <= piattaforma['y'] + piattaforma['altezza'] + margine)


def piattaforma_ottieni_centro(piattaforma):
    """Restituisce il centro della piattaforma come tupla (x, y)"""
    centro_x = piattaforma['x'] + piattaforma['larghezza'] // 2
    centro_y = piattaforma['y'] + piattaforma['altezza'] // 2
    return (centro_x, centro_y)


def crea_tutte_piattaforme():
    """
    Crea tutte le piattaforme del gioco.
    Restituisce una lista di piattaforme (dizionari).
    """
    lista_piattaforme = []
    
    # Configurazione griglia
    righe = 6
    colonne = 5
    larghezza_piattaforma = 140
    altezza_piattaforma = 110
    spaziatura = 10  # Spazio tra piattaforme (camminabile con il margine)
    
    # Calcola dove posizionare la griglia per centrarla
    larghezza_griglia = colonne * larghezza_piattaforma + (colonne - 1) * spaziatura
    altezza_griglia = righe * altezza_piattaforma + (righe - 1) * spaziatura
    offset_x = (LARGHEZZA - larghezza_griglia) // 2
    offset_y = (ALTEZZA - altezza_griglia) // 2 + 30
    
    # Crea lista di colori: esattamente 5 di ogni colore
    lista_colori = []
    for nome_colore in NOMI_COLORI:
        lista_colori.extend([nome_colore] * 5)  # Aggiunge 5 volte ogni colore
    
    # Mescola i colori casualmente
    random.shuffle(lista_colori)
    
    # Crea le piattaforme
    idx = 0
    for riga in range(righe):
        for col in range(colonne):
            x = offset_x + col * (larghezza_piattaforma + spaziatura)
            y = offset_y + riga * (altezza_piattaforma + spaziatura)
            
            nome_colore = lista_colori[idx]
            piattaforma = crea_piattaforma(x, y, larghezza_piattaforma, altezza_piattaforma, nome_colore)
            lista_piattaforme.append(piattaforma)
            idx += 1
    
    return lista_piattaforme
