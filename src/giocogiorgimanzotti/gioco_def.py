
import pygame  
import math    
import random  


LARGHEZZA = 1400  
ALTEZZA = 800     

FPS = 60 
COLORI = {
    'ROSSO': (255, 0, 0),      # Rosso puro
    'BIANCO': (255, 255, 255), # Bianco
    'GIALLO': (255, 255, 0),   # Giallo
    'BLU': (0, 0, 255),        # Blu puro
    'ARANCIONE': (255, 165, 0),# Arancione
    'VERDE': (0, 255, 0)       # Verde puro
}


NOMI_COLORI = ['ROSSO', 'BIANCO', 'GIALLO', 'BLU', 'ARANCIONE', 'VERDE']



stato_gioco = "MENU"
difficolta = "FACILE"

piattaforme = []  
lottatori = []    


colore_target = None           
conto_alla_rovescia = 3.0   
numero_round = 1              
vincitore = None               
piattaforme_scomparse = False 


def crea_piattaforma(x, y, larghezza, altezza, nome_colore):
    """
    Crea una singola piattaforma.
    
    Parametri:
        x, y: posizione della piattaforma sullo schermo
        larghezza, altezza: dimensioni della piattaforma
        nome_colore: uno dei colori in NOMI_COLORI
    
    Restituisce:
        Un dizionario con tutte le informazioni della piattaforma
    """
   
    piattaforma = {
        'x': x,                              # Posizione orizzontale
        'y': y,                              # Posizione verticale  
        'larghezza': larghezza,              # Larghezza in pixel
        'altezza': altezza,                  # Altezza in pixel
        'nome_colore': nome_colore,          # Nome del colore (es: "ROSSO")
        'colore': COLORI[nome_colore],       # Colore RGB (es: (255, 0, 0))
        'attiva': True,                      # Se True, la piattaforma è visibile
        'progresso_scomparsa': 0             # Da 0 (visibile) a 1 (scomparsa)
    }
    
    return piattaforma  


def piattaforma_inizia_scomparsa(piattaforma):
    """
    Fa iniziare l'animazione di scomparsa di una piattaforma.
    La piattaforma diventerà gradualmente più piccola fino a sparire.
    
    Parametri:
        piattaforma: il dizionario della piattaforma da far scomparire
    """
    piattaforma['attiva'] = False  


def piattaforma_aggiorna(piattaforma):
    """
    Aggiorna lo stato della piattaforma (animazione di scomparsa).
    Questa funzione viene chiamata 60 volte al secondo (per ogni frame).
    
    Parametri:
        piattaforma: il dizionario della piattaforma da aggiornare
    """
   
    if not piattaforma['attiva'] and piattaforma['progresso_scomparsa'] < 1:
        
        piattaforma['progresso_scomparsa'] += 0.07


def piattaforma_disegna(schermo, piattaforma):
    """
    Disegna una piattaforma sullo schermo.
    
    Parametri:
        schermo: la superficie pygame su cui disegnare
        piattaforma: il dizionario della piattaforma da disegnare
    """
   
    if piattaforma['progresso_scomparsa'] >= 1:
        return
    
   
    if not piattaforma['attiva']:
        
        scala = 1 - piattaforma['progresso_scomparsa']
        
        offset = piattaforma['progresso_scomparsa'] * 20
        
       
        rett = pygame.Rect(
            piattaforma['x'] + offset,
            piattaforma['y'] + offset,
            piattaforma['larghezza'] * scala,
            piattaforma['altezza'] * scala
        )
    else:
      
        rett = pygame.Rect(
            piattaforma['x'], 
            piattaforma['y'], 
            piattaforma['larghezza'], 
            piattaforma['altezza']
        )
    
   
    pygame.draw.rect(schermo, piattaforma['colore'], rett)
   
    pygame.draw.rect(schermo, (0, 0, 0), rett, 4)


def piattaforma_contiene_punto(piattaforma, x, y, margine=15):
    """
    Controlla se un punto (x, y) è dentro o vicino alla piattaforma.
    Il margine permette di camminare tra piattaforme adiacenti senza cadere!
    
    Parametri:
        piattaforma: la piattaforma da controllare
        x, y: coordinate del punto da controllare
        margine: spazio extra intorno alla piattaforma (default 15 pixel)
    
    Restituisce:
        True se il punto è dentro/vicino, False altrimenti
    
    ✏️ MODIFICABILE: Cambia 'margine=15' per rendere più facile/difficile
    """
    
    if not piattaforma['attiva'] or piattaforma['progresso_scomparsa'] >= 1:
        return False
    
    
    dentro_x = piattaforma['x'] - margine <= x <= piattaforma['x'] + piattaforma['larghezza'] + margine
    dentro_y = piattaforma['y'] - margine <= y <= piattaforma['y'] + piattaforma['altezza'] + margine
    
    return dentro_x and dentro_y


def piattaforma_ottieni_centro(piattaforma):
    """
    Calcola e restituisce il centro della piattaforma.
    Utile per far muovere i bot verso il centro delle piattaforme.
    
    Parametri:
        piattaforma: la piattaforma di cui vogliamo il centro
    
    Restituisce:
        Una tupla (centro_x, centro_y) con le coordinate del centro
    """
    centro_x = piattaforma['x'] + piattaforma['larghezza'] // 2  # // = divisione intera
    centro_y = piattaforma['y'] + piattaforma['altezza'] // 2
    return (centro_x, centro_y)


def crea_tutte_piattaforme():
    """
    Crea TUTTE le piattaforme del gioco disposte a griglia.
    Assegna 5 piattaforme per ogni colore (totale 30 piattaforme).
    
    Restituisce:
        Una lista con tutti i dizionari delle piattaforme
    """
    lista_piattaforme = []  
    
   
    righe = 6               
    colonne = 5             
    larghezza_piattaforma = 140   
    altezza_piattaforma = 110    
    spaziatura = 10         
    

    larghezza_griglia = colonne * larghezza_piattaforma + (colonne - 1) * spaziatura
    altezza_griglia = righe * altezza_piattaforma + (righe - 1) * spaziatura
    offset_x = (LARGHEZZA - larghezza_griglia) // 2  
    offset_y = (ALTEZZA - altezza_griglia) // 2 + 30  
    
    lista_colori = []
    for nome_colore in NOMI_COLORI:

        lista_colori.extend([nome_colore] * 5)
    
    random.shuffle(lista_colori)

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


# ==============================================================================
# SEZIONE 4: FUNZIONI PER I LOTTATORI (GIOCATORI)
# ==============================================================================


def crea_lottatore(x, y, colore_corpo, nome, è_bot, difficolta):
    """
    Crea un lottatore di sumo.
    
    Parametri:
        x, y: posizione iniziale
        colore_corpo: colore RGB del corpo (es: (255, 100, 100))
        nome: nome del giocatore (es: "TU", "BOT 1")
        è_bot: True se controllato dal computer, False se controllato dal giocatore
        difficolta: "FACILE", "MEDIO" o "DIFFICILE"
    
    Restituisce:
        Un dizionario con tutte le informazioni del lottatore
    """
    lottatore = {
        # --- POSIZIONE ---
        'x': x,
        'y': y,
        'spawn_x': x,  # Posizione dove riappare dopo un round
        'spawn_y': y,
      
        'velocita_x': 0,
        'velocita_y': 0,
        
      
        'colore_corpo': colore_corpo,
        'nome': nome,
        'è_bot': è_bot,
        'vivo': True,
        
     
        'attaccando': False,        
        'cooldown_attacco': 0,      
        'durata_attacco': 0,   
        
      
        'difficolta': difficolta,
        'piattaforma_target': None, 
        'timer_ai': 0,
        'tempo_reazione_ai': ottieni_tempo_reazione_ai(difficolta),
        'qualita_decisioni_ai': ottieni_qualita_decisioni_ai(difficolta),
        'probabilita_attacco_ai': ottieni_probabilita_attacco_ai(difficolta)
    }
    
    return lottatore


def ottieni_tempo_reazione_ai(difficolta):
    """
    Calcola quanto velocemente un bot reagisce (in frame).
    Più basso = bot più veloce.
    
    ✏️ MODIFICABILE: Cambia i numeri per rendere i bot più veloci o lenti!
    """
    if difficolta == "FACILE":
       
        return random.randint(50, 80)
    elif difficolta == "MEDIO":
       
        return random.randint(20, 40)
    else:  
       
        return random.randint(5, 15)


def ottieni_qualita_decisioni_ai(difficolta):
    """
    Calcola quanto bene un bot sceglie le piattaforme.
    Restituisce un numero da 0 (pessimo) a 1 (perfetto).
    
    ✏️ MODIFICABILE: Cambia questi numeri per bot più intelligenti o stupidi!
    """
    if difficolta == "FACILE":
        return 0.6   # 60% delle volte sceglie la piattaforma migliore
    elif difficolta == "MEDIO":
        return 0.85  # 85% delle volte sceglie la piattaforma migliore
    else:  # DIFFICILE
        return 0.98  # 98% delle volte sceglie la piattaforma migliore


def ottieni_probabilita_attacco_ai(difficolta):
    """
    Calcola quanto spesso un bot attacca (probabilità per frame).
    Più alto = bot più aggressivo.
    
    ✏️ MODIFICABILE: Cambia per bot più o meno aggressivi!
    """
    if difficolta == "FACILE":
        return 0.015  # 1.5% per frame = attacca raramente
    elif difficolta == "MEDIO":
        return 0.04   # 4% per frame = attacca abbastanza spesso
    else:  # DIFFICILE
        return 0.10   # 10% per frame = molto aggressivo!


def lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, lista_piattaforme, nome_colore_target, tutti_lottatori):
    """
    Aggiorna lo stato di un lottatore ogni frame.
    Gestisce movimento, attacco, fisica, ecc.
    
    Questa è una delle funzioni più importanti del gioco!
    """
    # Se il lottatore è morto, cade verso il basso
    if not lottatore['vivo']:
        lottatore['y'] += 5  # ✏️ MODIFICABILE: Velocità di caduta
        return  # Esce dalla funzione (niente altro da fare)
    
    # --- AGGIORNA TIMER ---
    if lottatore['cooldown_attacco'] > 0:
        lottatore['cooldown_attacco'] -= 1
    
    if lottatore['durata_attacco'] > 0:
        lottatore['durata_attacco'] -= 1
        if lottatore['durata_attacco'] == 0:
            lottatore['attaccando'] = False
    
    # --- CONTROLLI ---
    if lottatore['è_bot']:
        # Bot: usa l'intelligenza artificiale
        lottatore_aggiorna_ai(lottatore, lista_piattaforme, nome_colore_target, tutti_lottatori)
    else:
        # Giocatore umano: usa tastiera e mouse
        if tasti and pulsanti_mouse:
            # ✏️ MODIFICABILE: Accelerazione (quanto velocemente accelera)
            accelerazione = 0.6
            
            # Tasti WASD per muoversi
            if tasti[pygame.K_a]:  # Tasto A = sinistra
                lottatore['velocita_x'] -= accelerazione
            if tasti[pygame.K_d]:  # Tasto D = destra
                lottatore['velocita_x'] += accelerazione
            if tasti[pygame.K_w]:  # Tasto W = su
                lottatore['velocita_y'] -= accelerazione
            if tasti[pygame.K_s]:  # Tasto S = giù
                lottatore['velocita_y'] += accelerazione
            
            # Click sinistro per attaccare
            if pulsanti_mouse[0] and lottatore['cooldown_attacco'] == 0:
                lottatore_esegui_attacco(lottatore, tutti_lottatori)
    
   
    velocita = math.sqrt(lottatore['velocita_x']**2 + lottatore['velocita_y']**2)
    
    # ✏️ MODIFICABILE: Velocità massima
    velocita_massima = 4.0
    
    if velocita > velocita_massima:
        # Se va troppo veloce, riduci proporzionalmente
        rapporto = velocita_massima / velocita
        lottatore['velocita_x'] *= rapporto
        lottatore['velocita_y'] *= rapporto
    

    lottatore['velocita_x'] *= 0.85
    lottatore['velocita_y'] *= 0.85
    
   
    lottatore['x'] += lottatore['velocita_x']
    lottatore['y'] += lottatore['velocita_y']
    
 
    lottatore['x'] = max(22, min(LARGHEZZA - 22, lottatore['x']))
    lottatore['y'] = max(22, min(ALTEZZA - 22, lottatore['y']))


def lottatore_esegui_attacco(lottatore, tutti_lottatori):
    """
    Esegue un attacco pancia (stile Kung Fu Panda)!
    Spinge via tutti i lottatori vicini.
    
    ✏️ SUPER MODIFICABILE! Cambia raggio e spinta per attacchi diversi!
    """
    lottatore['attaccando'] = True
    lottatore['durata_attacco'] = 15  # ✏️ Frame di animazione
    lottatore['cooldown_attacco'] = 60  # ✏️ Frame prima di poter riattaccare
    

    raggio_attacco = 50   # Quanto lontano arriva l'attacco (in pixel)
    spinta_attacco = 250  # Quanto forte spinge (più alto = più forte!)
    

    for altro in tutti_lottatori:
  
        if altro['vivo'] and altro != lottatore:
  
            dx = altro['x'] - lottatore['x']
            dy = altro['y'] - lottatore['y']
            distanza = math.sqrt(dx**2 + dy**2)
            
       
            if distanza < raggio_attacco and distanza > 0:
    
                spinta_x = (dx / distanza) * spinta_attacco
                spinta_y = (dy / distanza) * spinta_attacco
                
        
                altro['velocita_x'] += spinta_x
                altro['velocita_y'] += spinta_y


def lottatore_aggiorna_ai(lottatore, lista_piattaforme, nome_colore_target, tutti_lottatori):
    """
    Intelligenza artificiale per i bot.
    Decide dove muoversi e quando attaccare.
    
    ALGORITMO:
    1. Ogni tot frame, sceglie una piattaforma del colore giusto
    2. Si muove verso quella piattaforma
    3. Se qualcuno è vicino, lo attacca (con una certa probabilità)
    """
    # Se non ci sono piattaforme o colore target, non fare nulla
    if not lista_piattaforme or not nome_colore_target:
        return
    

    lottatore['timer_ai'] += 1
    

    if lottatore['timer_ai'] > lottatore['tempo_reazione_ai'] or lottatore['piattaforma_target'] is None:
    
        piattaforme_valide = [p for p in lista_piattaforme 
                             if p['nome_colore'] == nome_colore_target and p['attiva']]
        
        if piattaforme_valide:
    
            if random.random() < lottatore['qualita_decisioni_ai']:
          
                lottatore['piattaforma_target'] = min(piattaforme_valide, 
                    key=lambda p: math.sqrt((piattaforma_ottieni_centro(p)[0] - lottatore['x'])**2 + 
                                           (piattaforma_ottieni_centro(p)[1] - lottatore['y'])**2))
            else:
        
                lottatore['piattaforma_target'] = random.choice(piattaforme_valide)
            

            lottatore['timer_ai'] = 0
            lottatore['tempo_reazione_ai'] = ottieni_tempo_reazione_ai(lottatore['difficolta'])
    

    if lottatore['piattaforma_target'] and lottatore['piattaforma_target']['attiva']:
   
        tx, ty = piattaforma_ottieni_centro(lottatore['piattaforma_target'])
        
        dx = tx - lottatore['x']
        dy = ty - lottatore['y']
        distanza = math.sqrt(dx**2 + dy**2)
        
        if distanza > 5:

            fattore_movimento = 0.75 if lottatore['difficolta'] == "FACILE" else 0.9
            
      
            lottatore['velocita_x'] += (dx / distanza) * 0.6 * fattore_movimento
            lottatore['velocita_y'] += (dy / distanza) * 0.6 * fattore_movimento

    if lottatore['cooldown_attacco'] == 0 and tutti_lottatori:
        for altro in tutti_lottatori:
            if altro['vivo'] and altro != lottatore:
          
                dx = altro['x'] - lottatore['x']
                dy = altro['y'] - lottatore['y']
                distanza = math.sqrt(dx**2 + dy**2)
                
                if distanza < 60 and random.random() < lottatore['probabilita_attacco_ai']:
                    lottatore_esegui_attacco(lottatore, tutti_lottatori)
                    break


def lottatore_controlla_su_piattaforma(lottatore, lista_piattaforme, nome_colore_target=None):
    """
    Controlla se il lottatore è su una piattaforma attiva.
    Se nome_colore_target è specificato, controlla solo piattaforme di quel colore.
    
    Restituisce:
        True se è su una piattaforma (del colore giusto), False altrimenti
    """
    for piattaforma in lista_piattaforme:

        if piattaforma['attiva'] and piattaforma_contiene_punto(piattaforma, lottatore['x'], lottatore['y']):

            if nome_colore_target is None or piattaforma['nome_colore'] == nome_colore_target:
                return True
    
    return False


def lottatore_resetta_posizione(lottatore):
    """
    Riporta il lottatore alla sua posizione iniziale (spawn).
    Usato all'inizio di ogni nuovo round.
    """
    lottatore['x'] = lottatore['spawn_x']
    lottatore['y'] = lottatore['spawn_y']
    lottatore['velocita_x'] = 0
    lottatore['velocita_y'] = 0
    lottatore['vivo'] = True
    lottatore['attaccando'] = False
    lottatore['cooldown_attacco'] = 0
    lottatore['durata_attacco'] = 0


def lottatore_disegna(schermo, lottatore):
    """
    Disegna un lottatore sullo schermo con grafica REALISTICA.
    Include muscoli, viso espressivo, ombra, ecc.
    
    ✏️ MODIFICABILE: Puoi cambiare colori, dimensioni, dettagli grafici!
    """
    pos = (int(lottatore['x']), int(lottatore['y']))
    raggio = 28 
    
    if not lottatore['è_bot'] and lottatore['vivo']:
        corona_y = pos[1] - raggio - 28
 
        pygame.draw.circle(schermo, (255, 215, 0), (pos[0], corona_y), 12)
        pygame.draw.circle(schermo, (200, 150, 0), (pos[0], corona_y), 12, 2)
        
        punti = []
        for i in range(5):
            angolo = (2 * math.pi / 5) * i - math.pi / 2
            px = pos[0] + math.cos(angolo) * 9
            py = corona_y + math.sin(angolo) * 9
            punti.append((px, py))
        pygame.draw.polygon(schermo, (255, 255, 150), punti)
        
        pygame.draw.circle(schermo, (255, 215, 0), pos, raggio + 4, 4)
    
    if lottatore['attaccando'] and lottatore['durata_attacco'] > 5:
    
        raggio_attacco = raggio + (15 - lottatore['durata_attacco']) * 3
        pygame.draw.circle(schermo, (255, 255, 0), pos, raggio_attacco, 4)
        pygame.draw.circle(schermo, (255, 200, 0), pos, raggio_attacco - 5, 2)
    
    if lottatore['vivo']:
        ombra = pygame.Surface((raggio * 3, raggio))
        ombra.set_alpha(80)  
        ombra.fill((0, 0, 0))
        schermo.blit(ombra, (pos[0] - raggio * 1.5, pos[1] + 8))
    
    raggio_corpo = raggio + (4 if lottatore['attaccando'] else 0)
    
    pygame.draw.circle(schermo, tuple(max(0, c - 40) for c in lottatore['colore_corpo']), 
                      pos, raggio_corpo)
    pygame.draw.circle(schermo, lottatore['colore_corpo'], 
                      (pos[0] - 3, pos[1] - 3), raggio_corpo - 2)
    pygame.draw.circle(schermo, tuple(min(255, c + 30) for c in lottatore['colore_corpo']), 
                      (pos[0] - 5, pos[1] - 5), raggio_corpo - 8)
    
    pygame.draw.circle(schermo, (0, 0, 0), pos, raggio_corpo, 3)
    
    offset_muscoli = 8
    pygame.draw.circle(schermo, tuple(max(0, c - 20) for c in lottatore['colore_corpo']),
                      (pos[0] - offset_muscoli, pos[1] - 5), 10)
    pygame.draw.circle(schermo, tuple(max(0, c - 20) for c in lottatore['colore_corpo']),
                      (pos[0] + offset_muscoli, pos[1] - 5), 10)
    
    pygame.draw.line(schermo, tuple(max(0, c - 50) for c in lottatore['colore_corpo']),
                    (pos[0] - 6, pos[1] + 5), (pos[0] - 3, pos[1] + 12), 2)
    pygame.draw.line(schermo, tuple(max(0, c - 50) for c in lottatore['colore_corpo']),
                    (pos[0] + 3, pos[1] + 5), (pos[0] + 6, pos[1] + 12), 2)
    
    pygame.draw.rect(schermo, (40, 40, 40), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 8))
    pygame.draw.rect(schermo, (70, 70, 70), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 3))
 
    pygame.draw.circle(schermo, (200, 180, 100), (pos[0], pos[1]), 5)
    pygame.draw.circle(schermo, (150, 130, 50), (pos[0], pos[1]), 5, 2)
    
 
    raggio_testa = 16
    testa_y = int(lottatore['y'] - raggio_corpo + 12)
    
    pygame.draw.circle(schermo, (230, 200, 160), (pos[0], testa_y), raggio_testa)
    pygame.draw.circle(schermo, (255, 220, 177), (pos[0] - 2, testa_y - 2), raggio_testa - 2)
    pygame.draw.circle(schermo, (0, 0, 0), (pos[0], testa_y), raggio_testa, 2)
    
    capelli_y = testa_y - raggio_testa + 4
    pygame.draw.circle(schermo, (20, 20, 20), (pos[0], capelli_y), 7)
    pygame.draw.circle(schermo, (10, 10, 10), (pos[0], capelli_y - 3), 4)
    
    offset_occhi = 6
    occhi_y = testa_y + 2
    
    if lottatore['attaccando']:
     
        pygame.draw.line(schermo, (0, 0, 0), 
                       (pos[0] - offset_occhi - 3, occhi_y),
                       (pos[0] - offset_occhi + 3, occhi_y - 2), 3)
        pygame.draw.line(schermo, (0, 0, 0),
                       (pos[0] + offset_occhi - 3, occhi_y - 2),
                       (pos[0] + offset_occhi + 3, occhi_y), 3)
    else:
     
        pygame.draw.ellipse(schermo, (255, 255, 255), 
                          (pos[0] - offset_occhi - 4, occhi_y - 3, 8, 6))
        pygame.draw.ellipse(schermo, (255, 255, 255), 
                          (pos[0] + offset_occhi - 4, occhi_y - 3, 8, 6))
     
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] - offset_occhi, occhi_y), 3)
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] + offset_occhi, occhi_y), 3)
        # Pupilla nera
        pygame.draw.circle(schermo, (0, 0, 0), (pos[0] - offset_occhi, occhi_y), 2)
        pygame.draw.circle(schermo, (0, 0, 0), (pos[0] + offset_occhi, occhi_y), 2)
    
 
    pygame.draw.line(schermo, (40, 30, 20),
                    (pos[0] - offset_occhi - 5, occhi_y - 6),
                    (pos[0] - offset_occhi + 3, occhi_y - 7), 2)
    pygame.draw.line(schermo, (40, 30, 20),
                    (pos[0] + offset_occhi - 3, occhi_y - 7),
                    (pos[0] + offset_occhi + 5, occhi_y - 6), 2)
    
    pygame.draw.circle(schermo, (220, 190, 150), (pos[0], testa_y + 8), 3)
    
    if lottatore['attaccando']:

        pygame.draw.arc(schermo, (100, 50, 50), 
                       (pos[0] - 6, testa_y + 10, 12, 8), 0, math.pi, 2)
    else:
      
        pygame.draw.arc(schermo, (150, 80, 80), 
                       (pos[0] - 7, testa_y + 8, 14, 10), math.pi, 2 * math.pi, 2)
    
    if lottatore['vivo']:
        font = pygame.font.Font(None, 22 if not lottatore['è_bot'] else 20)
        colore_nome = (255, 215, 0) if not lottatore['è_bot'] else (255, 255, 255)
        superficie_nome = font.render(lottatore['nome'], True, colore_nome)
        rett_nome = superficie_nome.get_rect(center=(pos[0], pos[1] - raggio_corpo - 15))
        
        colore_sfondo = (50, 40, 0) if not lottatore['è_bot'] else (0, 0, 0)
        rett_sfondo = rett_nome.inflate(12, 6)
        pygame.draw.rect(schermo, colore_sfondo, rett_sfondo, border_radius=5)
        pygame.draw.rect(schermo, colore_nome, rett_sfondo, 2, border_radius=5)
        schermo.blit(superficie_nome, rett_nome)


def crea_tutti_lottatori(livello_difficolta):
    """
    Crea tutti gli 8 giocatori del gioco.
    1 giocatore umano + 7 bot, disposti in cerchio al centro.
    
    ✏️ MODIFICABILE: Cambia num_giocatori per avere più o meno giocatori!
    """
    lista_lottatori = []
    
    centro_griglia_x = LARGHEZZA // 2
    centro_griglia_y = ALTEZZA // 2 + 30
    
 
    num_giocatori = 8
    
    raggio_spawn = 100
    
    colori_giocatori = [
        (255, 100, 100),  # Rosso chiaro (GIOCATORE UMANO)
        (100, 255, 100),  # Verde chiaro
        (100, 100, 255),  # Blu chiaro
        (255, 255, 100),  # Giallo chiaro
        (255, 100, 255),  # Magenta
        (100, 255, 255),  # Ciano
        (255, 150, 100),  # Arancione chiaro
        (200, 100, 255)   # Viola
    ]
    
    for i in range(num_giocatori):

        angolo = (2 * math.pi / num_giocatori) * i
       
        spawn_x = centro_griglia_x + math.cos(angolo) * raggio_spawn
        spawn_y = centro_griglia_y + math.sin(angolo) * raggio_spawn
        
        if i == 0:
            nome = "TU"
            è_bot = False
        else:
            nome = f"BOT {i}"
            è_bot = True
        
        lottatore = crea_lottatore(spawn_x, spawn_y, colori_giocatori[i], nome, è_bot, livello_difficolta)
        lista_lottatori.append(lottatore)
    
    return lista_lottatori


# ==============================================================================
# SEZIONE 5: FUNZIONI PER IL MENU E L'INTERFACCIA
# ==============================================================================


def disegna_pannello(schermo, rett, titolo, font):
    """
    Disegna un pannello bianco moderno con ombra e titolo.
    Usato nel menu principale.
    """
    rett_ombra = rett.copy()
    rett_ombra.x += 5
    rett_ombra.y += 5
    pygame.draw.rect(schermo, (10, 10, 15), rett_ombra, border_radius=15)
    
    pygame.draw.rect(schermo, (240, 240, 245), rett, border_radius=15)
    pygame.draw.rect(schermo, (200, 200, 210), rett, 3, border_radius=15)
    
    rett_header = pygame.Rect(rett.x, rett.y, rett.width, 50)
    pygame.draw.rect(schermo, (220, 220, 230), rett_header, 
                    border_top_left_radius=15, border_top_right_radius=15)

    testo_titolo = font.render(titolo, True, (50, 50, 50))
    rett_titolo = testo_titolo.get_rect(center=(rett.centerx, rett.y + 25))
    schermo.blit(testo_titolo, rett_titolo)


def disegna_menu(schermo, fonts, pos_mouse):
    """
    Disegna il menu principale con 3 pannelli:
    1. Difficoltà
    2. Controlli
    3. Pulsante Inizia
    
    Restituisce: (bottoni_difficolta, bottone_inizio)
    """
 
    titolo = fonts['titolo'].render("SUMO COLOR SURVIVAL", True, (255, 255, 255))
    rett_titolo = titolo.get_rect(center=(LARGHEZZA // 2, 120))
    schermo.blit(titolo, rett_titolo)
    

    larghezza_pannello = 380
    altezza_pannello = 280
    spaziatura_pannello = 50

    larghezza_totale = larghezza_pannello * 3 + spaziatura_pannello * 2
    inizio_x = (LARGHEZZA - larghezza_totale) // 2
    centro_y = ALTEZZA // 2
    
    rett_pannelli = {
        'difficolta': pygame.Rect(inizio_x, centro_y - altezza_pannello // 2, 
                                 larghezza_pannello, altezza_pannello),
        'controlli': pygame.Rect(inizio_x + larghezza_pannello + spaziatura_pannello, 
                                centro_y - altezza_pannello // 2, 
                                larghezza_pannello, altezza_pannello),
        'inizio': pygame.Rect(inizio_x + (larghezza_pannello + spaziatura_pannello) * 2, 
                            centro_y - altezza_pannello // 2, 
                            larghezza_pannello, altezza_pannello)
    }
    

    pannello = rett_pannelli['difficolta']
    disegna_pannello(schermo, pannello, "DIFFICOLTÀ", fonts['medio'])
 
    dati_diff = [
        ("FACILE", "FACILE", (100, 255, 100)),
        ("MEDIO", "MEDIO", (255, 200, 100)),
        ("DIFFICILE", "DIFFICILE", (255, 100, 100))
    ]
    
    bottoni_difficolta = {}
    y_bottone = pannello.y + 80
    
    for i, (valore_diff, testo_diff, colore_diff) in enumerate(dati_diff):
        bottone = pygame.Rect(pannello.centerx - 150, y_bottone + i * 60, 300, 50)
        bottoni_difficolta[valore_diff] = bottone
        
     
        è_selezionato = (difficolta == valore_diff)
        è_hover = bottone.collidepoint(pos_mouse)
        

        if è_selezionato:
            pygame.draw.rect(schermo, colore_diff, bottone, border_radius=10)
            colore_testo = (0, 0, 0)
        elif è_hover:
            pygame.draw.rect(schermo, (200, 200, 200), bottone, border_radius=10)
            pygame.draw.rect(schermo, colore_diff, bottone, 3, border_radius=10)
            colore_testo = (0, 0, 0)
        else:
            pygame.draw.rect(schermo, (180, 180, 180), bottone, border_radius=10)
            colore_testo = (50, 50, 50)
        

        testo_btn = fonts['medio'].render(testo_diff, True, colore_testo)
        rett_testo_btn = testo_btn.get_rect(center=bottone.center)
        schermo.blit(testo_btn, rett_testo_btn)
    

    pannello = rett_pannelli['controlli']
    disegna_pannello(schermo, pannello, "CONTROLLI", fonts['medio'])
    

    controlli = [
        "WASD - Movimento",
        "",
        "Click Sinistro",
        "Attacco Pancia",
        "",
        "Obiettivo:",
        "Colore giusto!"
    ]
    

    offset_y = pannello.y + 70
    for testo in controlli:
        if testo: 
            surf = fonts['piccolo'].render(testo, True, (50, 50, 50))
            rett = surf.get_rect(center=(pannello.centerx, offset_y))
            schermo.blit(surf, rett)
        offset_y += 28
    
   
    pannello = rett_pannelli['inizio']
    disegna_pannello(schermo, pannello, "GIOCA", fonts['medio'])
   
    bottone_inizio = pygame.Rect(pannello.centerx - 150, pannello.centery - 40, 300, 80)
    è_hover_inizio = bottone_inizio.collidepoint(pos_mouse)
 
    if è_hover_inizio:
        pygame.draw.rect(schermo, (100, 220, 100), bottone_inizio, border_radius=15)
    else:
        pygame.draw.rect(schermo, (80, 180, 80), bottone_inizio, border_radius=15)
    
    pygame.draw.rect(schermo, (150, 255, 150), bottone_inizio, 4, border_radius=15)
    
   
    testo_inizio = fonts['grande'].render("INIZIA", True, (255, 255, 255))
    rett_testo_inizio = testo_inizio.get_rect(center=bottone_inizio.center)
    schermo.blit(testo_inizio, rett_testo_inizio)
    

    info = fonts['piccolo'].render("8 Giocatori - Sopravvivi!", True, (150, 150, 150))
    rett_info = info.get_rect(center=(LARGHEZZA // 2, ALTEZZA - 50))
    schermo.blit(info, rett_info)
    
    return bottoni_difficolta, bottone_inizio


def disegna_hud_gioco(schermo, fonts, num_round, diff, col_target, stato, conta, lista_lottatori):
    """
    Disegna l'HUD (interfaccia utente) durante il gioco.
    Include: round, difficoltà, colore target, countdown, giocatori vivi, pannello attacco.
    """
  
    pygame.draw.rect(schermo, (0, 0, 0, 200), (0, 0, LARGHEZZA, 90))
    
  
    testo_round = fonts['medio'].render(f"ROUND {num_round}", True, (255, 255, 255))
    schermo.blit(testo_round, (20, 15))
    
    nomi_diff = {"FACILE": "FACILE", "MEDIO": "MEDIO", "DIFFICILE": "DIFFICILE"}
    colori_diff = {"FACILE": (100, 255, 100), "MEDIO": (255, 200, 100), "DIFFICILE": (255, 100, 100)}
    testo_diff = fonts['piccolo'].render(nomi_diff[diff], True, colori_diff[diff])
    schermo.blit(testo_diff, (20, 55))
    

    if stato == "GIOCANDO":
    
        testo_target = fonts['grande'].render(f"{col_target}", True, COLORI[col_target])
        rett_target = testo_target.get_rect(center=(LARGHEZZA // 2, 35))
        
    
        rett_box = rett_target.inflate(40, 20)
        pygame.draw.rect(schermo, COLORI[col_target], rett_box, 5, border_radius=10)
        
        schermo.blit(testo_target, rett_target)
        
   
        if conta > 0:
            testo_conta = fonts['grande'].render(f"{int(conta) + 1}", True, (255, 200, 0))
            rett_conta = testo_conta.get_rect(center=(LARGHEZZA // 2, 75))
            schermo.blit(testo_conta, rett_conta)
    
  
    conteggio_vivi = sum(1 for l in lista_lottatori if l['vivo'])
    testo_vivi = fonts['medio'].render(f"Vivi: {conteggio_vivi}/8", True, (0, 255, 0))
    schermo.blit(testo_vivi, (LARGHEZZA - 150, 15))
    
    giocatore = None
    for l in lista_lottatori:
        if not l['è_bot']:
            giocatore = l
            break
    

    if giocatore and giocatore['vivo']:
        x_pannello = LARGHEZZA - 300
        y_pannello = 120
        largh_pannello = 280
        alt_pannello = 140
        
        rett_pannello = pygame.Rect(x_pannello, y_pannello, largh_pannello, alt_pannello)
        pygame.draw.rect(schermo, (40, 40, 50), rett_pannello, border_radius=10)
        pygame.draw.rect(schermo, (100, 100, 120), rett_pannello, 3, border_radius=10)
        
        titolo = fonts['piccolo'].render("ATTACCO PANCIA", True, (255, 215, 0))
        rett_titolo = titolo.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 25))
        schermo.blit(titolo, rett_titolo)
        
        desc1 = fonts['piccolo'].render("Click Sinistro per colpire", True, (200, 200, 200))
        rett_desc1 = desc1.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 55))
        schermo.blit(desc1, rett_desc1)
        
        desc2 = fonts['piccolo'].render("Spinta: SUPER FORTE!", True, (255, 150, 150))
        rett_desc2 = desc2.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 75))
        schermo.blit(desc2, rett_desc2)
        
        largh_barra = 240
        alt_barra = 25
        x_barra = x_pannello + (largh_pannello - largh_barra) // 2
        y_barra = y_pannello + 100
        
        pygame.draw.rect(schermo, (60, 60, 70), (x_barra, y_barra, largh_barra, alt_barra), border_radius=5)
        
        if giocatore['cooldown_attacco'] > 0:
         
            progresso = 1 - (giocatore['cooldown_attacco'] / 60)
            largh_riempimento = int(largh_barra * progresso)
            pygame.draw.rect(schermo, (255, 200, 0), (x_barra, y_barra, largh_riempimento, alt_barra), border_radius=5)
            
           
            testo_percentuale = fonts['piccolo'].render(f"{int(progresso * 100)}%", True, (255, 255, 255))
            rett_percentuale = testo_percentuale.get_rect(center=(x_barra + largh_barra // 2, y_barra + alt_barra // 2))
            schermo.blit(testo_percentuale, rett_percentuale)
        else:
          
            pygame.draw.rect(schermo, (100, 255, 100), (x_barra, y_barra, largh_barra, alt_barra), border_radius=5)
            testo_pronto = fonts['piccolo'].render("PRONTO!", True, (0, 100, 0))
            rett_pronto = testo_pronto.get_rect(center=(x_barra + largh_barra // 2, y_barra + alt_barra // 2))
            schermo.blit(testo_pronto, rett_pronto)
        
        pygame.draw.rect(schermo, (150, 150, 160), (x_barra, y_barra, largh_barra, alt_barra), 2, border_radius=5)


def disegna_bottone_riavvio(schermo, fonts, pos_mouse):
    """
    Disegna il bottone "Nuova Partita" durante il gioco.
    Posizionato in basso a sinistra.
    
    Restituisce: il rett del bottone
    """
    bottone_riavvio = pygame.Rect(40, ALTEZZA // 2 - 50, 300, 100)
    è_hover = bottone_riavvio.collidepoint(pos_mouse)
    
    if è_hover:
        colore_bottone = (180, 40, 40)
        colore_bordo = (255, 120, 120)
    else:
        colore_bottone = (120, 30, 30)
        colore_bordo = (200, 80, 80)
    
    pygame.draw.rect(schermo, colore_bottone, bottone_riavvio, border_radius=15)
    pygame.draw.rect(schermo, colore_bordo, bottone_riavvio, 4, border_radius=15)
    
    testo_icona = fonts['grande'].render("↻", True, (255, 255, 255))
    rett_icona = testo_icona.get_rect(center=(bottone_riavvio.centerx, bottone_riavvio.centery - 15))
    schermo.blit(testo_icona, rett_icona)
    
    testo_bottone = fonts['piccolo'].render("Nuova Partita", True, (255, 255, 200))
    rett_testo_bottone = testo_bottone.get_rect(center=(bottone_riavvio.centerx, bottone_riavvio.centery + 25))
    schermo.blit(testo_bottone, rett_testo_bottone)
    
    return bottone_riavvio


def disegna_schermata_vincitore(schermo, fonts, lottatore_vincitore, num_round, diff):
    """
    Disegna la schermata finale quando qualcuno vince.
    """
    overlay = pygame.Surface((LARGHEZZA, ALTEZZA))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    schermo.blit(overlay, (0, 0))
    
    if lottatore_vincitore:
    
        testo_vincitore = fonts['titolo'].render(f"🏆 {lottatore_vincitore['nome']} VINCE! 🏆", 
                                                 True, (255, 215, 0))
        
        lottatore_vincitore['x'] = LARGHEZZA // 2
        lottatore_vincitore['y'] = ALTEZZA // 2 + 80
        lottatore_disegna(schermo, lottatore_vincitore)
    else:
       
        testo_vincitore = fonts['titolo'].render("PAREGGIO!", True, (255, 255, 255))
    
    rett_vincitore = testo_vincitore.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 3))
    schermo.blit(testo_vincitore, rett_vincitore)
    
    testo_rounds = fonts['medio'].render(f"Round giocati: {num_round}", True, (255, 255, 255))
    rett_rounds = testo_rounds.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 - 20))
    schermo.blit(testo_rounds, rett_rounds)
    
    nome_diff = {"FACILE": "Facile", "MEDIO": "Medio", "DIFFICILE": "Difficile"}
    testo_diff = fonts['medio'].render(f"Difficoltà: {nome_diff[diff]}", True, (200, 200, 200))
    rett_diff = testo_diff.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 + 20))
    schermo.blit(testo_diff, rett_diff)
    
    testo_riavvio = fonts['piccolo'].render("Premi SPAZIO per giocare ancora", True, (200, 200, 200))
    rett_riavvio = testo_riavvio.get_rect(center=(LARGHEZZA // 2, ALTEZZA - 100))
    schermo.blit(testo_riavvio, rett_riavvio)


# ==============================================================================
# SEZIONE 6: FUNZIONE PRINCIPALE (MAIN)
# ==============================================================================


def main():
    """
    Funzione principale che esegue il gioco.
    
    STRUTTURA:
    1. Inizializza Pygame
    2. Crea font
    3. Loop infinito:
       - Gestisce eventi (click, tasti)
       - Aggiorna lo stato del gioco
       - Disegna tutto sullo schermo
    """
    global stato_gioco, difficolta, piattaforme, lottatori, colore_target
    global conto_alla_rovescia, numero_round, vincitore, piattaforme_scomparse
    
    pygame.init()  
    schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    pygame.display.set_caption("Sumo Color Survival")
    orologio = pygame.time.Clock() 
    
    fonts = {
        'titolo': pygame.font.Font(None, 70),
        'grande': pygame.font.Font(None, 50),
        'medio': pygame.font.Font(None, 36),
        'piccolo': pygame.font.Font(None, 28),
        'minuscolo': pygame.font.Font(None, 22)
    }
    
    bottoni_difficolta = {}
    bottone_inizio = None
    bottone_riavvio = None
    
    in_esecuzione = True
    while in_esecuzione:
        
        pos_mouse = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            
            if evento.type == pygame.QUIT:
                in_esecuzione = False
            
            elif evento.type == pygame.KEYDOWN:
                
                if evento.key == pygame.K_SPACE and stato_gioco == "VINCITORE":
                    stato_gioco = "MENU"
            
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1: 
                
                if stato_gioco == "MENU":
                 
                    for valore_diff, rett_bottone in bottoni_difficolta.items():
                        if rett_bottone.collidepoint(pos_mouse):
                            difficolta = valore_diff
                    
                    if bottone_inizio and bottone_inizio.collidepoint(pos_mouse):
                      
                        piattaforme = crea_tutte_piattaforme()
                        lottatori = crea_tutti_lottatori(difficolta)
                        
                        numero_round = 1
                        vincitore = None
                        piattaforme_scomparse = False
                        
                        stato_gioco = "GIOCANDO"
                        conto_alla_rovescia = 3.0
                        colore_target = random.choice(NOMI_COLORI)
                        
                        for piattaforma in piattaforme:
                            piattaforma['attiva'] = True
                            piattaforma['progresso_scomparsa'] = 0
                        
                        for lottatore in lottatori:
                            if lottatore['è_bot']:
                                lottatore['timer_ai'] = 0
                                lottatore['piattaforma_target'] = None
                
                elif stato_gioco in ["GIOCANDO", "ATTESA"]:
               
                    if bottone_riavvio and bottone_riavvio.collidepoint(pos_mouse):
                        stato_gioco = "MENU"
        
        # ==============================================================
        # AGGIORNA LO STATO DEL GIOCO
        # ==============================================================
        
        if stato_gioco == "GIOCANDO":
        
            conto_alla_rovescia -= 1/60
            
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            for lottatore in lottatori:
                if lottatore['vivo']:
                    lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            if conto_alla_rovescia <= 0:

                for piattaforma in piattaforme:
                    if piattaforma['nome_colore'] != colore_target:
                        piattaforma_inizia_scomparsa(piattaforma)
                
                piattaforme_scomparse = True
                
                for lottatore in lottatori:
                    if lottatore['vivo']:
                        su_corretta = False
                        
                        for piattaforma in piattaforme:
                            if (piattaforma['nome_colore'] == colore_target and 
                                piattaforma['attiva'] and 
                                piattaforma_contiene_punto(piattaforma, lottatore['x'], lottatore['y'])):
                                su_corretta = True
                                break
                        
                        if not su_corretta:
                            lottatore['vivo'] = False
                
                stato_gioco = "ATTESA"
                conto_alla_rovescia = 2.0 
            
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
        
        elif stato_gioco == "ATTESA":
          
            conto_alla_rovescia -= 1/60
            
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            for lottatore in lottatori:
                lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            if piattaforme_scomparse:
                for lottatore in lottatori:
                    if lottatore['vivo']:
                        if not lottatore_controlla_su_piattaforma(lottatore, piattaforme, colore_target):
                            lottatore['vivo'] = False
            
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
            
            if conto_alla_rovescia <= 0:
            
                lottatori_vivi = [l for l in lottatori if l['vivo']]
                
                if len(lottatori_vivi) == 1:
                 
                    vincitore = lottatori_vivi[0]
                    stato_gioco = "VINCITORE"
                
                elif len(lottatori_vivi) == 0:
                    
                    vincitore = None
                    stato_gioco = "VINCITORE"
                
                else:
                 
                    numero_round += 1
                    
                    piattaforme = crea_tutte_piattaforme()
                    
                    num_vivi = len(lottatori_vivi)
                    centro_griglia_x = LARGHEZZA // 2
                    centro_griglia_y = ALTEZZA // 2 + 30
                    raggio_spawn = 100
                    
                    for i, lottatore in enumerate(lottatori_vivi):
                        angolo = (2 * math.pi / num_vivi) * i
                        lottatore['spawn_x'] = centro_griglia_x + math.cos(angolo) * raggio_spawn
                        lottatore['spawn_y'] = centro_griglia_y + math.sin(angolo) * raggio_spawn
                        lottatore_resetta_posizione(lottatore)
                    
                    stato_gioco = "GIOCANDO"
                    conto_alla_rovescia = 3.0
                    piattaforme_scomparse = False
                    colore_target = random.choice(NOMI_COLORI)
                    
                    for lottatore in lottatori:
                        if lottatore['è_bot']:
                            lottatore['timer_ai'] = 0
                            lottatore['piattaforma_target'] = None
        
        # ==============================================================
        # DISEGNA TUTTO SULLO SCHERMO
        # ==============================================================
        
     
        schermo.fill((25, 25, 30))  
        
     
        if stato_gioco == "MENU":
           
            bottoni_difficolta, bottone_inizio = disegna_menu(schermo, fonts, pos_mouse)
        
        elif stato_gioco in ["GIOCANDO", "ATTESA"]:
      
            for piattaforma in piattaforme:
                piattaforma_disegna(schermo, piattaforma)
            
            
            for lottatore in lottatori:
                lottatore_disegna(schermo, lottatore)
           
            disegna_hud_gioco(schermo, fonts, numero_round, difficolta, colore_target, 
                           stato_gioco, conto_alla_rovescia, lottatori)
            
            bottone_riavvio = disegna_bottone_riavvio(schermo, fonts, pos_mouse)
        
        elif stato_gioco == "VINCITORE":
      
            disegna_schermata_vincitore(schermo, fonts, vincitore, numero_round, difficolta)
        
        pygame.display.flip()
    
        orologio.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    
    main()
