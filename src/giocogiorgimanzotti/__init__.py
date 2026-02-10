import pygame
import math
import random

# ==============================================================================
# COSTANTI DEL GIOCO - Valori che non cambiano mai
# ==============================================================================

LARGHEZZA = 1920  # Larghezza finestra
ALTEZZA = 1080     # Altezza finestra
FPS = 60          # Frame per secondo

# Colori delle piattaforme (Rosso, Bianco, Giallo, Blu, Arancione, Verde)
COLORI = {
    'ROSSO': (255, 0, 0),
    'BIANCO': (255, 255, 255),
    'GIALLO': (255, 255, 0),
    'BLU': (0, 0, 255),
    'ARANCIONE': (255, 165, 0),
    'VERDE': (0, 255, 0)
}

NOMI_COLORI = ['ROSSO', 'BIANCO', 'GIALLO', 'BLU', 'ARANCIONE', 'VERDE']


# ==============================================================================
# VARIABILI GLOBALI - Lo stato del gioco
# ==============================================================================

# Stato del gioco: "MENU", "GIOCANDO", "ATTESA", "VINCITORE"
stato_gioco = "MENU"

# Difficoltà: "FACILE", "MEDIO", "DIFFICILE"
difficolta = "FACILE"

# Liste che contengono piattaforme e giocatori
piattaforme = []     # Lista di dizionari, ogni piattaforma è un dizionario
lottatori = []       # Lista di dizionari, ogni giocatore è un dizionario

# Colore target del round corrente
colore_target = None

# Tempo prima che le piattaforme scompaiano
conto_alla_rovescia = 3.5

# Numero del round corrente
numero_round = 1

# Vincitore (dizionario del giocatore che ha vinto)
vincitore = None

# Flag per sapere se le piattaforme sono già scomparse
piattaforme_scomparse = False


# ==============================================================================
# FUNZIONI PER LE PIATTAFORME
# ==============================================================================

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


# ==============================================================================
# FUNZIONI PER I GIOCATORI (LOTTATORI SUMO)
# ==============================================================================

def crea_lottatore(x, y, colore_corpo, nome, è_bot, difficolta):
    """
    Crea un giocatore lottatore di sumo.
    Restituisce un dizionario con tutte le informazioni del giocatore.
    """
    return {
        # Posizione
        'x': x,
        'y': y,
        'spawn_x': x,  # Posizione iniziale dove riappare
        'spawn_y': y,
        
        # Movimento
        'velocita_x': 0,
        'velocita_y': 0,
        
        # Aspetto
        'colore_corpo': colore_corpo,
        'nome': nome,
        'è_bot': è_bot,
        'vivo': True,
        
        # Attacco
        'attaccando': False,
        'cooldown_attacco': 0,  # Tempo prima di poter attaccare di nuovo
        'durata_attacco': 0,    # Durata dell'animazione di attacco
        
        # AI (per i bot)
        'difficolta': difficolta,
        'piattaforma_target': None,  # Piattaforma verso cui il bot si sta muovendo
        'timer_ai': 0,
        'tempo_reazione_ai': ottieni_tempo_reazione_ai(difficolta),
        'qualita_decisioni_ai': ottieni_qualita_decisioni_ai(difficolta),
        'probabilita_attacco_ai': ottieni_probabilita_attacco_ai(difficolta)
    }


def ottieni_tempo_reazione_ai(difficolta):
    """Quanto velocemente il bot reagisce (in frame) - BOT PIÙ FORTI"""
    if difficolta == "FACILE":
        return random.randint(50, 80)   # Da 80-120 a 50-80 (più veloci)
    elif difficolta == "MEDIO":
        return random.randint(20, 40)   # Da 40-70 a 20-40 (più veloci)
    else:  # DIFFICILE
        return random.randint(5, 15)    # Da 10-30 a 5-15 (molto più veloci)


def ottieni_qualita_decisioni_ai(difficolta):
    """Quanto bene il bot sceglie le piattaforme (0-1) - BOT PIÙ INTELLIGENTI"""
    if difficolta == "FACILE":
        return 0.6   # Da 0.3 a 0.6 (60% scelte ottime)
    elif difficolta == "MEDIO":
        return 0.85  # Da 0.7 a 0.85 (85% scelte ottime)
    else:  # DIFFICILE
        return 0.98  # Da 0.95 a 0.98 (98% scelte ottime)


def ottieni_probabilita_attacco_ai(difficolta):
    """Quanto spesso il bot attacca quando vicino a un nemico"""
    if difficolta == "FACILE":
        return 0.015  # Da 0.01 a 0.015 (più aggressivi)
    elif difficolta == "MEDIO":
        return 0.04   # Da 0.03 a 0.04 (più aggressivi)
    else:  # DIFFICILE
        return 0.10   # Da 0.08 a 0.10 (molto aggressivi)


def lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, lista_piattaforme, nome_colore_target, tutti_lottatori):
    """Aggiorna un giocatore (movimento, attacco, ecc.)"""
    
    if not lottatore['vivo']:
        # Se morto, cade verso il basso (sempre, senza sparire improvvisamente)
        lottatore['y'] += 5
        return
    
    # Aggiorna cooldown attacco
    if lottatore['cooldown_attacco'] > 0:
        lottatore['cooldown_attacco'] -= 1
    
    # Aggiorna durata attacco
    if lottatore['durata_attacco'] > 0:
        lottatore['durata_attacco'] -= 1
        if lottatore['durata_attacco'] == 0:
            lottatore['attaccando'] = False
    
    # Controlli
    if lottatore['è_bot']:
        # Bot: usa intelligenza artificiale
        lottatore_aggiorna_ai(lottatore, lista_piattaforme, nome_colore_target, tutti_lottatori)
    else:
        # Giocatore umano: usa tastiera e mouse
        if tasti and pulsanti_mouse:
            # Movimento WASD
            if tasti[pygame.K_a]:
                lottatore['velocita_x'] -= 0.6
            if tasti[pygame.K_d]:
                lottatore['velocita_x'] += 0.6
            if tasti[pygame.K_w]:
                lottatore['velocita_y'] -= 0.6
            if tasti[pygame.K_s]:
                lottatore['velocita_y'] += 0.6
            
            # Attacco con click sinistro
            if pulsanti_mouse[0] and lottatore['cooldown_attacco'] == 0:
                lottatore_esegui_attacco(lottatore, tutti_lottatori)
    
    # Limita la velocità massima
    velocita = math.sqrt(lottatore['velocita_x']**2 + lottatore['velocita_y']**2)
    velocita_massima = 4.0
    if velocita > velocita_massima:
        rapporto = velocita_massima / velocita
        lottatore['velocita_x'] *= rapporto
        lottatore['velocita_y'] *= rapporto
    
    # Applica attrito (rallenta gradualmente)
    lottatore['velocita_x'] *= 0.85
    lottatore['velocita_y'] *= 0.85
    
    # Aggiorna posizione
    lottatore['x'] += lottatore['velocita_x']
    lottatore['y'] += lottatore['velocita_y']
    
    # Limiti dello schermo
    lottatore['x'] = max(22, min(LARGHEZZA - 22, lottatore['x']))
    lottatore['y'] = max(22, min(ALTEZZA - 22, lottatore['y']))


def lottatore_esegui_attacco(lottatore, tutti_lottatori):
    """Esegue un attacco pancia (stile Kung Fu Panda) - SPINTA DOPPIA!"""
    
    lottatore['attaccando'] = True
    lottatore['durata_attacco'] = 15
    lottatore['cooldown_attacco'] = 60  # 1 secondo
    
    raggio_attacco = 50
    spinta_attacco = 250  # RADDOPPIATA! Da 120 a 250!
    
    # Cerca altri giocatori da colpire
    for altro in tutti_lottatori:
        if altro['vivo'] and altro != lottatore:
            dx = altro['x'] - lottatore['x']
            dy = altro['y'] - lottatore['y']
            distanza = math.sqrt(dx**2 + dy**2)
            
            if distanza < raggio_attacco and distanza > 0:
                # Calcola direzione della spinta
                spinta_x = (dx / distanza) * spinta_attacco
                spinta_y = (dy / distanza) * spinta_attacco
                
                # Applica la spinta all'avversario
                altro['velocita_x'] += spinta_x
                altro['velocita_y'] += spinta_y


def lottatore_aggiorna_ai(lottatore, lista_piattaforme, nome_colore_target, tutti_lottatori):
    """Intelligenza artificiale per i bot - MIGLIORATA"""
    
    if not lista_piattaforme or not nome_colore_target:
        return
    
    # Timer per prendere decisioni
    lottatore['timer_ai'] += 1
    
    # Ogni tot frame, sceglie una nuova piattaforma target
    if lottatore['timer_ai'] > lottatore['tempo_reazione_ai'] or lottatore['piattaforma_target'] is None:
        # Trova piattaforme con il colore giusto
        piattaforme_valide = [p for p in lista_piattaforme 
                             if p['nome_colore'] == nome_colore_target and p['attiva']]
        
        if piattaforme_valide:
            # Sceglie la piattaforma in base alla qualità delle decisioni
            if random.random() < lottatore['qualita_decisioni_ai']:
                # Scelta ottimale: piattaforma più vicina
                lottatore['piattaforma_target'] = min(piattaforme_valide, 
                    key=lambda p: math.sqrt((piattaforma_ottieni_centro(p)[0] - lottatore['x'])**2 + 
                                           (piattaforma_ottieni_centro(p)[1] - lottatore['y'])**2))
            else:
                # Scelta casuale
                lottatore['piattaforma_target'] = random.choice(piattaforme_valide)
            
            lottatore['timer_ai'] = 0
            lottatore['tempo_reazione_ai'] = ottieni_tempo_reazione_ai(lottatore['difficolta'])
    
    # Muovi verso la piattaforma target
    if lottatore['piattaforma_target'] and lottatore['piattaforma_target']['attiva']:
        tx, ty = piattaforma_ottieni_centro(lottatore['piattaforma_target'])
        
        dx = tx - lottatore['x']
        dy = ty - lottatore['y']
        distanza = math.sqrt(dx**2 + dy**2)
        
        if distanza > 5:
            # BOT PIÙ FORTI: movimento più veloce anche in modalità facile
            fattore_movimento = 0.75 if lottatore['difficolta'] == "FACILE" else 0.9
            lottatore['velocita_x'] += (dx / distanza) * 0.6 * fattore_movimento
            lottatore['velocita_y'] += (dy / distanza) * 0.6 * fattore_movimento
    
    # AI per l'attacco
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
    """Controlla se il giocatore è su una piattaforma (opzionalmente del colore giusto)"""
    for piattaforma in lista_piattaforme:
        if piattaforma['attiva'] and piattaforma_contiene_punto(piattaforma, lottatore['x'], lottatore['y']):
            if nome_colore_target is None or piattaforma['nome_colore'] == nome_colore_target:
                return True
    return False


def lottatore_resetta_posizione(lottatore):
    """Riporta il giocatore alla posizione iniziale"""
    lottatore['x'] = lottatore['spawn_x']
    lottatore['y'] = lottatore['spawn_y']
    lottatore['velocita_x'] = 0
    lottatore['velocita_y'] = 0
    lottatore['vivo'] = True
    lottatore['attaccando'] = False
    lottatore['cooldown_attacco'] = 0
    lottatore['durata_attacco'] = 0


def lottatore_disegna(schermo, lottatore):
    """Disegna un lottatore con grafica REALISTICA"""
    
    # I bot morti cadono sempre visibili (rimosso il controllo che li nascondeva)
    
    pos = (int(lottatore['x']), int(lottatore['y']))
    raggio = 28  # Più grande per più dettagli
    
    # CORONA PER IL GIOCATORE UMANO
    if not lottatore['è_bot'] and lottatore['vivo']:
        corona_y = pos[1] - raggio - 28
        # Corona più elaborata
        pygame.draw.circle(schermo, (255, 215, 0), (pos[0], corona_y), 12)
        pygame.draw.circle(schermo, (200, 150, 0), (pos[0], corona_y), 12, 2)
        
        # Stella nella corona
        punti = []
        for i in range(5):
            angolo = (2 * math.pi / 5) * i - math.pi / 2
            px = pos[0] + math.cos(angolo) * 9
            py = corona_y + math.sin(angolo) * 9
            punti.append((px, py))
        pygame.draw.polygon(schermo, (255, 255, 150), punti)
        
        # Bordo dorato brillante
        pygame.draw.circle(schermo, (255, 215, 0), pos, raggio + 4, 4)
    
    # Effetto attacco più evidente
    if lottatore['attaccando'] and lottatore['durata_attacco'] > 5:
        raggio_attacco = raggio + (15 - lottatore['durata_attacco']) * 3
        pygame.draw.circle(schermo, (255, 255, 0), pos, raggio_attacco, 4)
        pygame.draw.circle(schermo, (255, 200, 0), pos, raggio_attacco - 5, 2)
    
    # Ombra più realistica
    if lottatore['vivo']:
        ombra = pygame.Surface((raggio * 3, raggio))
        ombra.set_alpha(80)
        ombra.fill((0, 0, 0))
        schermo.blit(ombra, (pos[0] - raggio * 1.5, pos[1] + 8))
    
    # CORPO REALISTICO - Più muscoloso
    raggio_corpo = raggio + (4 if lottatore['attaccando'] else 0)
    
    # Sfumatura del corpo (3 cerchi per effetto 3D)
    pygame.draw.circle(schermo, tuple(max(0, c - 40) for c in lottatore['colore_corpo']), 
                      pos, raggio_corpo)
    pygame.draw.circle(schermo, lottatore['colore_corpo'], 
                      (pos[0] - 3, pos[1] - 3), raggio_corpo - 2)
    pygame.draw.circle(schermo, tuple(min(255, c + 30) for c in lottatore['colore_corpo']), 
                      (pos[0] - 5, pos[1] - 5), raggio_corpo - 8)
    
    # Bordo corpo
    pygame.draw.circle(schermo, (0, 0, 0), pos, raggio_corpo, 3)
    
    # Muscoli pettorali (due cerchi)
    offset_muscoli = 8
    pygame.draw.circle(schermo, tuple(max(0, c - 20) for c in lottatore['colore_corpo']),
                      (pos[0] - offset_muscoli, pos[1] - 5), 10)
    pygame.draw.circle(schermo, tuple(max(0, c - 20) for c in lottatore['colore_corpo']),
                      (pos[0] + offset_muscoli, pos[1] - 5), 10)
    
    # Addominali (linee)
    pygame.draw.line(schermo, tuple(max(0, c - 50) for c in lottatore['colore_corpo']),
                    (pos[0] - 6, pos[1] + 5), (pos[0] - 3, pos[1] + 12), 2)
    pygame.draw.line(schermo, tuple(max(0, c - 50) for c in lottatore['colore_corpo']),
                    (pos[0] + 3, pos[1] + 5), (pos[0] + 6, pos[1] + 12), 2)
    
    # Cintura più dettagliata
    pygame.draw.rect(schermo, (40, 40, 40), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 8))
    pygame.draw.rect(schermo, (70, 70, 70), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 3))
    # Fibbia cintura
    pygame.draw.circle(schermo, (200, 180, 100), (pos[0], pos[1]), 5)
    pygame.draw.circle(schermo, (150, 130, 50), (pos[0], pos[1]), 5, 2)
    
    # TESTA più realistica
    raggio_testa = 16
    testa_y = int(lottatore['y'] - raggio_corpo + 12)
    
    # Sfumatura testa
    pygame.draw.circle(schermo, (230, 200, 160), (pos[0], testa_y), raggio_testa)
    pygame.draw.circle(schermo, (255, 220, 177), (pos[0] - 2, testa_y - 2), raggio_testa - 2)
    pygame.draw.circle(schermo, (0, 0, 0), (pos[0], testa_y), raggio_testa, 2)
    
    # Capelli più realistici (chonmage - nodo tradizionale sumo)
    capelli_y = testa_y - raggio_testa + 4
    pygame.draw.circle(schermo, (20, 20, 20), (pos[0], capelli_y), 7)
    pygame.draw.circle(schermo, (10, 10, 10), (pos[0], capelli_y - 3), 4)
    
    # Viso più espressivo
    offset_occhi = 6
    occhi_y = testa_y + 2
    
    if lottatore['attaccando']:
        # Occhi chiusi aggressivi
        pygame.draw.line(schermo, (0, 0, 0), 
                       (pos[0] - offset_occhi - 3, occhi_y),
                       (pos[0] - offset_occhi + 3, occhi_y - 2), 3)
        pygame.draw.line(schermo, (0, 0, 0),
                       (pos[0] + offset_occhi - 3, occhi_y - 2),
                       (pos[0] + offset_occhi + 3, occhi_y), 3)
    else:
        # Occhi aperti più realistici
        # Bianco occhio
        pygame.draw.ellipse(schermo, (255, 255, 255), 
                          (pos[0] - offset_occhi - 4, occhi_y - 3, 8, 6))
        pygame.draw.ellipse(schermo, (255, 255, 255), 
                          (pos[0] + offset_occhi - 4, occhi_y - 3, 8, 6))
        # Iride
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] - offset_occhi, occhi_y), 3)
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] + offset_occhi, occhi_y), 3)
        # Pupilla
        pygame.draw.circle(schermo, (0, 0, 0), (pos[0] - offset_occhi, occhi_y), 2)
        pygame.draw.circle(schermo, (0, 0, 0), (pos[0] + offset_occhi, occhi_y), 2)
    
    # Sopracciglia
    pygame.draw.line(schermo, (40, 30, 20),
                    (pos[0] - offset_occhi - 5, occhi_y - 6),
                    (pos[0] - offset_occhi + 3, occhi_y - 7), 2)
    pygame.draw.line(schermo, (40, 30, 20),
                    (pos[0] + offset_occhi - 3, occhi_y - 7),
                    (pos[0] + offset_occhi + 5, occhi_y - 6), 2)
    
    # Naso
    pygame.draw.circle(schermo, (220, 190, 150), (pos[0], testa_y + 8), 3)
    
    # Bocca (sorride se sta vincendo, seria se attacca)
    if lottatore['attaccando']:
        pygame.draw.arc(schermo, (100, 50, 50), 
                       (pos[0] - 6, testa_y + 10, 12, 8), 0, math.pi, 2)
    else:
        pygame.draw.arc(schermo, (150, 80, 80), 
                       (pos[0] - 7, testa_y + 8, 14, 10), math.pi, 2 * math.pi, 2)
    
    # Nome con sfondo migliore
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
    """Crea tutti gli 8 giocatori (1 umano + 7 bot)"""
    lista_lottatori = []
    
    # Centro della griglia
    centro_griglia_x = LARGHEZZA // 2
    centro_griglia_y = ALTEZZA // 2 + 30
    
    num_giocatori = 8
    raggio_spawn = 100
    
    # Colori diversi per ogni giocatore
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
    
    # Crea i giocatori in cerchio
    for i in range(num_giocatori):
        angolo = (2 * math.pi / num_giocatori) * i
        spawn_x = centro_griglia_x + math.cos(angolo) * raggio_spawn
        spawn_y = centro_griglia_y + math.sin(angolo) * raggio_spawn
        
        if i == 0:
            # Primo giocatore = umano
            nome = "TU"
            è_bot = False
        else:
            # Altri giocatori = bot
            nome = f"BOT {i}"
            è_bot = True
        
        lottatore = crea_lottatore(spawn_x, spawn_y, colori_giocatori[i], nome, è_bot, livello_difficolta)
        lista_lottatori.append(lottatore)
    
    return lista_lottatori


# ==============================================================================
# FUNZIONI PER IL MENU E L'INTERFACCIA
# ==============================================================================

def disegna_pannello(schermo, rett, titolo, font):
    """Disegna un pannello bianco moderno con titolo"""
    
    # Ombra
    rett_ombra = rett.copy()
    rett_ombra.x += 5
    rett_ombra.y += 5
    pygame.draw.rect(schermo, (10, 10, 15), rett_ombra, border_radius=15)
    
    # Pannello principale bianco
    pygame.draw.rect(schermo, (240, 240, 245), rett, border_radius=15)
    pygame.draw.rect(schermo, (200, 200, 210), rett, 3, border_radius=15)
    
    # Header (parte superiore del pannello)
    rett_header = pygame.Rect(rett.x, rett.y, rett.width, 50)
    pygame.draw.rect(schermo, (220, 220, 230), rett_header, 
                    border_top_left_radius=15, border_top_right_radius=15)
    
    # Titolo
    testo_titolo = font.render(titolo, True, (50, 50, 50))
    rett_titolo = testo_titolo.get_rect(center=(rett.centerx, rett.y + 25))
    schermo.blit(testo_titolo, rett_titolo)


def disegna_menu(schermo, fonts, pos_mouse):
    """Disegna il menu principale"""
    
    # Titolo
    titolo = fonts['titolo'].render("SUMO COLOR SURVIVAL", True, (255, 255, 255))
    rett_titolo = titolo.get_rect(center=(LARGHEZZA // 2, 120))
    schermo.blit(titolo, rett_titolo)
    
    # Posizioni dei 3 pannelli
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
    
    # PANNELLO 1: DIFFICOLTÀ
    pannello = rett_pannelli['difficolta']
    disegna_pannello(schermo, pannello, "DIFFICOLTÀ", fonts['medio'])
    
    # Bottoni difficoltà
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
    
    # PANNELLO 2: CONTROLLI
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
    
    # PANNELLO 3: INIZIO
    pannello = rett_pannelli['inizio']
    disegna_pannello(schermo, pannello, "GIOCA", fonts['medio'])
    
    # Bottone INIZIO grande
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
    
    # Info sotto
    info = fonts['piccolo'].render("8 Giocatori - Sopravvivi!", True, (150, 150, 150))
    rett_info = info.get_rect(center=(LARGHEZZA // 2, ALTEZZA - 50))
    schermo.blit(info, rett_info)
    
    return bottoni_difficolta, bottone_inizio


def disegna_hud_gioco(schermo, fonts, num_round, diff, col_target, stato, conta, lista_lottatori):
    """Disegna l'HUD (interfaccia) durante il gioco"""
    
    # Barra superiore scura
    pygame.draw.rect(schermo, (0, 0, 0, 200), (0, 0, LARGHEZZA, 90))
    
    # Round e difficoltà (sinistra)
    testo_round = fonts['medio'].render(f"ROUND {num_round}", True, (255, 255, 255))
    schermo.blit(testo_round, (20, 15))
    
    nomi_diff = {"FACILE": "FACILE", "MEDIO": "MEDIO", "DIFFICILE": "DIFFICILE"}
    colori_diff = {"FACILE": (100, 255, 100), "MEDIO": (255, 200, 100), "DIFFICILE": (255, 100, 100)}
    testo_diff = fonts['piccolo'].render(nomi_diff[diff], True, colori_diff[diff])
    schermo.blit(testo_diff, (20, 55))
    
    # Colore target (centro)
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
    
    # Giocatori vivi (destra)
    conteggio_vivi = sum(1 for l in lista_lottatori if l['vivo'])
    testo_vivi = fonts['medio'].render(f"Vivi: {conteggio_vivi}/8", True, (0, 255, 0))
    schermo.blit(testo_vivi, (LARGHEZZA - 150, 15))
    
    # Pannello ricarica attacco (destra)
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
        
        # Pannello
        rett_pannello = pygame.Rect(x_pannello, y_pannello, largh_pannello, alt_pannello)
        pygame.draw.rect(schermo, (40, 40, 50), rett_pannello, border_radius=10)
        pygame.draw.rect(schermo, (100, 100, 120), rett_pannello, 3, border_radius=10)
        
        # Titolo
        titolo = fonts['piccolo'].render("ATTACCO PANCIA", True, (255, 215, 0))
        rett_titolo = titolo.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 25))
        schermo.blit(titolo, rett_titolo)
        
        # Descrizione
        desc1 = fonts['piccolo'].render("Click Sinistro per colpire", True, (200, 200, 200))
        rett_desc1 = desc1.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 55))
        schermo.blit(desc1, rett_desc1)
        
        desc2 = fonts['piccolo'].render("Spinta: SUPER FORTE!", True, (255, 150, 150))
        rett_desc2 = desc2.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 75))
        schermo.blit(desc2, rett_desc2)
        
        # Barra ricarica
        largh_barra = 240
        alt_barra = 25
        x_barra = x_pannello + (largh_pannello - largh_barra) // 2
        y_barra = y_pannello + 100
        
        # Sfondo barra
        pygame.draw.rect(schermo, (60, 60, 70), (x_barra, y_barra, largh_barra, alt_barra), border_radius=5)
        
        if giocatore['cooldown_attacco'] > 0:
            # Ricarica in corso
            progresso = 1 - (giocatore['cooldown_attacco'] / 60)
            largh_riempimento = int(largh_barra * progresso)
            pygame.draw.rect(schermo, (255, 200, 0), (x_barra, y_barra, largh_riempimento, alt_barra), border_radius=5)
            
            # Percentuale
            testo_percentuale = fonts['piccolo'].render(f"{int(progresso * 100)}%", True, (255, 255, 255))
            rett_percentuale = testo_percentuale.get_rect(center=(x_barra + largh_barra // 2, y_barra + alt_barra // 2))
            schermo.blit(testo_percentuale, rett_percentuale)
        else:
            # Pronto!
            pygame.draw.rect(schermo, (100, 255, 100), (x_barra, y_barra, largh_barra, alt_barra), border_radius=5)
            testo_pronto = fonts['piccolo'].render("PRONTO!", True, (0, 100, 0))
            rett_pronto = testo_pronto.get_rect(center=(x_barra + largh_barra // 2, y_barra + alt_barra // 2))
            schermo.blit(testo_pronto, rett_pronto)
        
        # Bordo barra
        pygame.draw.rect(schermo, (150, 150, 160), (x_barra, y_barra, largh_barra, alt_barra), 2, border_radius=5)


def disegna_bottone_riavvio(schermo, fonts, pos_mouse):
    """Disegna il bottone per riavviare il gioco"""
    
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
    """Disegna la schermata del vincitore"""
    
    # Overlay scuro
    overlay = pygame.Surface((LARGHEZZA, ALTEZZA))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    schermo.blit(overlay, (0, 0))
    
    # Testo vincitore
    if lottatore_vincitore:
        testo_vincitore = fonts['titolo'].render(f"🏆 {lottatore_vincitore['nome']} VINCE! 🏆", 
                                                 True, (255, 215, 0))
        
        # Disegna il vincitore al centro
        lottatore_vincitore['x'] = LARGHEZZA // 2
        lottatore_vincitore['y'] = ALTEZZA // 2 + 80
        lottatore_disegna(schermo, lottatore_vincitore)
    else:
        testo_vincitore = fonts['titolo'].render("PAREGGIO!", True, (255, 255, 255))
    
    rett_vincitore = testo_vincitore.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 3))
    schermo.blit(testo_vincitore, rett_vincitore)
    
    # Statistiche
    testo_rounds = fonts['medio'].render(f"Round giocati: {num_round}", True, (255, 255, 255))
    rett_rounds = testo_rounds.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 - 20))
    schermo.blit(testo_rounds, rett_rounds)
    
    nome_diff = {"FACILE": "Facile", "MEDIO": "Medio", "DIFFICILE": "Difficile"}
    testo_diff = fonts['medio'].render(f"Difficoltà: {nome_diff[diff]}", True, (200, 200, 200))
    rett_diff = testo_diff.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 + 20))
    schermo.blit(testo_diff, rett_diff)
    
    # Istruzioni
    testo_riavvio = fonts['piccolo'].render("Premi SPAZIO per giocare ancora", True, (200, 200, 200))
    rett_riavvio = testo_riavvio.get_rect(center=(LARGHEZZA // 2, ALTEZZA - 100))
    schermo.blit(testo_riavvio, rett_riavvio)


# ==============================================================================
# FUNZIONE PRINCIPALE - LOOP DEL GIOCO
# ==============================================================================

def main():
    """Funzione principale che esegue il gioco"""
    
    # Variabili globali
    global stato_gioco, difficolta, piattaforme, lottatori, colore_target
    global conto_alla_rovescia, numero_round, vincitore, piattaforme_scomparse
    
    # Inizializza Pygame
    pygame.init()
    schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    pygame.display.set_caption("Sumo Color Survival")
    orologio = pygame.time.Clock()
    
    # Crea i font
    fonts = {
        'titolo': pygame.font.Font(None, 70),
        'grande': pygame.font.Font(None, 50),
        'medio': pygame.font.Font(None, 36),
        'piccolo': pygame.font.Font(None, 28),
        'minuscolo': pygame.font.Font(None, 22)
    }
    
    # Variabili per i bottoni del menu
    bottoni_difficolta = {}
    bottone_inizio = None
    bottone_riavvio = None
    
    # Loop principale del gioco
    in_esecuzione = True
    while in_esecuzione:
        
        # Ottieni la posizione del mouse
        pos_mouse = pygame.mouse.get_pos()
        
        # Gestisci eventi (chiusura, click, tasti)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                in_esecuzione = False
            
            elif evento.type == pygame.KEYDOWN:
                # Tasto SPAZIO nella schermata vincitore
                if evento.key == pygame.K_SPACE and stato_gioco == "VINCITORE":
                    stato_gioco = "MENU"
            
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Click sinistro
                
                if stato_gioco == "MENU":
                    # Click sui bottoni difficoltà
                    for valore_diff, rett_bottone in bottoni_difficolta.items():
                        if rett_bottone.collidepoint(pos_mouse):
                            difficolta = valore_diff
                    
                    # Click sul bottone INIZIO
                    if bottone_inizio and bottone_inizio.collidepoint(pos_mouse):
                        # Inizia il gioco!
                        piattaforme = crea_tutte_piattaforme()
                        lottatori = crea_tutti_lottatori(difficolta)
                        numero_round = 1
                        vincitore = None
                        piattaforme_scomparse = False
                        
                        # Inizia il primo round
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
                    # Click sul bottone RIAVVIO
                    if bottone_riavvio and bottone_riavvio.collidepoint(pos_mouse):
                        stato_gioco = "MENU"
        
        # ==============================================================
        # AGGIORNA LO STATO DEL GIOCO
        # ==============================================================
        
        if stato_gioco == "GIOCANDO":
            # Aggiorna countdown
            conto_alla_rovescia -= 1/60
            
            # Ottieni input da tastiera e mouse
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            # Aggiorna tutti i giocatori
            for lottatore in lottatori:
                if lottatore['vivo']:
                    lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            # Quando il countdown finisce
            if conto_alla_rovescia <= 0:
                # Fa scomparire le piattaforme sbagliate
                for piattaforma in piattaforme:
                    if piattaforma['nome_colore'] != colore_target:
                        piattaforma_inizia_scomparsa(piattaforma)
                
                piattaforme_scomparse = True
                
                # Controlla chi è su piattaforme sbagliate
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
            
            # Aggiorna animazione piattaforme
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
        
        elif stato_gioco == "ATTESA":
            # Aggiorna countdown
            conto_alla_rovescia -= 1/60
            
            # Ottieni input
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            # Aggiorna giocatori
            for lottatore in lottatori:
                lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            # Controlla se qualcuno cade dalle piattaforme
            if piattaforme_scomparse:
                for lottatore in lottatori:
                    if lottatore['vivo']:
                        if not lottatore_controlla_su_piattaforma(lottatore, piattaforme, colore_target):
                            lottatore['vivo'] = False
            
            # Aggiorna piattaforme
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
            
            # Quando il countdown finisce
            if conto_alla_rovescia <= 0:
                # Conta i sopravvissuti
                lottatori_vivi = [l for l in lottatori if l['vivo']]
                
                if len(lottatori_vivi) == 1:
                    # Abbiamo un vincitore!
                    vincitore = lottatori_vivi[0]
                    stato_gioco = "VINCITORE"
                
                elif len(lottatori_vivi) == 0:
                    # Pareggio
                    vincitore = None
                    stato_gioco = "VINCITORE"
                
                else:
                    # Continua con un nuovo round
                    numero_round += 1
                    piattaforme = crea_tutte_piattaforme()
                    
                    # Respawn dei giocatori vivi al centro
                    num_vivi = len(lottatori_vivi)
                    centro_griglia_x = LARGHEZZA // 2
                    centro_griglia_y = ALTEZZA // 2 + 30
                    raggio_spawn = 100
                    
                    for i, lottatore in enumerate(lottatori_vivi):
                        angolo = (2 * math.pi / num_vivi) * i
                        lottatore['spawn_x'] = centro_griglia_x + math.cos(angolo) * raggio_spawn
                        lottatore['spawn_y'] = centro_griglia_y + math.sin(angolo) * raggio_spawn
                        lottatore_resetta_posizione(lottatore)
                    
                    # Inizia nuovo round
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
        
        # Sfondo nero/grigio scuro
        schermo.fill((25, 25, 30))
        
        if stato_gioco == "MENU":
            # Disegna il menu
            bottoni_difficolta, bottone_inizio = disegna_menu(schermo, fonts, pos_mouse)
        
        elif stato_gioco in ["GIOCANDO", "ATTESA"]:
            # Disegna il gioco
            
            # Disegna piattaforme
            for piattaforma in piattaforme:
                piattaforma_disegna(schermo, piattaforma)
            
            # Disegna giocatori
            for lottatore in lottatori:
                lottatore_disegna(schermo, lottatore)
            
            # Disegna HUD
            disegna_hud_gioco(schermo, fonts, numero_round, difficolta, colore_target, 
                           stato_gioco, conto_alla_rovescia, lottatori)
            
            # Disegna bottone riavvio
            bottone_riavvio = disegna_bottone_riavvio(schermo, fonts, pos_mouse)
        
        elif stato_gioco == "VINCITORE":
            # Disegna schermata vincitore
            disegna_schermata_vincitore(schermo, fonts, vincitore, numero_round, difficolta)
        
        # Aggiorna lo schermo
        pygame.display.flip()
        
        # Limita a 60 FPS
        orologio.tick(FPS)
    
    # Chiudi Pygame
    pygame.quit()


# Esegui il gioco!
if __name__ == "__main__":
    main()
