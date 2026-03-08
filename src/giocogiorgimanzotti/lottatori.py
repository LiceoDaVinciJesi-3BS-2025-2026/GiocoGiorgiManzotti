import pygame  
import math    
import random

from costanti_e_variabili import *
from piattaforme import *

def crea_lottatore(x, y, colore_corpo, nome, è_bot, difficolta):
    """
    Crea un lottatore di sumo.
    
    Restituisce:
        Un dizionario con tutte le informazioni del lottatore
    """
    lottatore = {
        # POSIZIONE
        'x': x,
        'y': y,
        'spawn_x': x, 
        'spawn_y': y,
        # MOVIMENTO
        'velocita_x': 0,
        'velocita_y': 0,
        
        # ASPETTO
        'colore_corpo': colore_corpo,
        'nome': nome,
        'è_bot': è_bot,
        'vivo': True,
        
        # ATTACCO
        'attaccando': False,        
        'cooldown_attacco': 0,      
        'durata_attacco': 0,   
        
        # AI (BOT)
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
    
    """
    if difficolta == "FACILE":
        return random.randint(50, 80)
    
    elif difficolta == "MEDIO":
        return random.randint(20, 40)
    
    else: # DIFFICILE
        return random.randint(5, 15)


def ottieni_qualita_decisioni_ai(difficolta):
    """
    Calcola quanto bene un bot sceglie le piattaforme.
    Restituisce un numero da 0 (pessimo) a 1 (perfetto).
   
    """
    if difficolta == "FACILE":
        return 0.7   # 60% delle volte sceglie la piattaforma migliore
    elif difficolta == "MEDIO":
        return 0.85  # 85% delle volte sceglie la piattaforma migliore
    else:  # DIFFICILE
        return 0.98  # 98% delle volte sceglie la piattaforma migliore


def ottieni_probabilita_attacco_ai(difficolta):
    """
    Calcola quanto spesso un bot attacca (probabilità per frame).
    Più alto = bot più aggressivo.
    
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
    
    """
    # Se il lottatore è morto, cade verso il basso
    if not lottatore['vivo']:
        lottatore['y'] += 5  # Velocità di caduta
        return  # Esce dalla funzione 
    
    # AGGIORNA TIMER
    if lottatore['cooldown_attacco'] > 0:
        lottatore['cooldown_attacco'] -= 1
    
    if lottatore['durata_attacco'] > 0:
        lottatore['durata_attacco'] -= 1
        if lottatore['durata_attacco'] == 0:
            lottatore['attaccando'] = False
    
    # CONTROLLI
    if lottatore['è_bot']:
        # Bot che usa l'intelligenza artificiale
        lottatore_aggiorna_ai(lottatore, lista_piattaforme, nome_colore_target, tutti_lottatori)
    else:
        # Giocatore umano
        if tasti and pulsanti_mouse:
            accelerazione = 0.6
            
            # Tasti per muoversi
            if tasti[pygame.K_a]:  # Tasto A = sinistra
                lottatore['velocita_x'] -= accelerazione
            if tasti[pygame.K_d]:  # Tasto D = destra
                lottatore['velocita_x'] += accelerazione
            if tasti[pygame.K_w]:  # Tasto W = su
                lottatore['velocita_y'] -= accelerazione
            if tasti[pygame.K_s]:  # Tasto S = giù
                lottatore['velocita_y'] += accelerazione
            
            # Tasto sinistro per attaccare
            if pulsanti_mouse[0] and lottatore['cooldown_attacco'] == 0:
                lottatore_esegui_attacco(lottatore, tutti_lottatori)
    
    #VELOCITA MASSIMA
    velocita = math.sqrt(lottatore['velocita_x']**2 + lottatore['velocita_y']**2)
    velocita_massima = 6.5
    
    if velocita > velocita_massima:
      
        rapporto = velocita_massima / velocita
        lottatore['velocita_x'] *= rapporto
        lottatore['velocita_y'] *= rapporto
    
    # ATTRITO
    lottatore['velocita_x'] *= 0.85
    lottatore['velocita_y'] *= 0.85
    
    # SPOSTA IL GIOCATORE
    lottatore['x'] += lottatore['velocita_x']
    lottatore['y'] += lottatore['velocita_y']
    
    # IMPEDISCE L'USCITA DALLO SCHERMO
    lottatore['x'] = max(22, min(LARGHEZZA - 22, lottatore['x']))
    lottatore['y'] = max(22, min(ALTEZZA - 22, lottatore['y']))


def lottatore_esegui_attacco(lottatore, tutti_lottatori):
    """
    Esegue una panciata.
    
    """
    lottatore['attaccando'] = True
    lottatore['durata_attacco'] = 15  # Frame di animazione
    lottatore['cooldown_attacco'] = 60  # Frame prima di poter riattaccare
    

    raggio_attacco = 80   # Quanto lontano arriva l'attacco 
    spinta_attacco = 300  # Quanto forte spinge 
    
    # Cerca tutti i lottatori nel raggio d'attacco
    for altro in tutti_lottatori:
  
        if altro['vivo'] and altro != lottatore:
              
            # Calcola la distanza usando il teorema di Pitagora
            dx = altro['x'] - lottatore['x']
            dy = altro['y'] - lottatore['y']
            distanza = math.sqrt(dx**2 + dy**2)
            
            # Se è abbastanza vicino viene colpito
            if distanza < raggio_attacco and distanza > 0:
                
                # Calcola la direzione della spinta e la applica
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
    # Se non ci sono piattaforme o il colore non è uscito, non fa nulla
    if not lista_piattaforme or not nome_colore_target:
        return
    
    #  calcola quanto è lontana una piattaforma dal lottatore
    def calcola_distanza_da_lottatore(piattaforma):
        """
        Calcola la distanza tra il lottatore e una piattaforma.
        Usa il TEOREMA DI PITAGORA
        
        Parametri:
            piattaforma: la piattaforma da cui calcolare la distanza
        
        Restituisce:
            La distanza in pixel (numero decimale)
        """
        # Ottieni le coordinate del centro della piattaforma
        centro_x, centro_y = piattaforma_ottieni_centro(piattaforma)
        
        # Calcola le differenze sugli assi X e Y
        differenza_x = centro_x - lottatore['x']
        differenza_y = centro_y - lottatore['y']
        
        # Applica il teorema di Pitagora
        distanza = math.sqrt(differenza_x**2 + differenza_y**2)
        
        return distanza
    
    
    lottatore['timer_ai'] += 1
    
    # Ogni tot frame sceglie una nuova piattaforma
    if lottatore['timer_ai'] > lottatore['tempo_reazione_ai'] or lottatore['piattaforma_target'] is None:
        
        # Trova tutte le piattaforme del colore giusto
        piattaforme_valide = []
        for p in lista_piattaforme:
            if p['nome_colore'] == nome_colore_target and p['attiva']:
                piattaforme_valide.append(p)
        
        if piattaforme_valide:
            if random.random() < lottatore['qualita_decisioni_ai']:
                # min() + key trovano la piattaforma più vicina
                lottatore['piattaforma_target'] = min(piattaforme_valide, 
                                                      key=calcola_distanza_da_lottatore)
                
                
            else:
                # SCELTA CASUALE
                lottatore['piattaforma_target'] = random.choice(piattaforme_valide)
            
            # Reset del timer
            lottatore['timer_ai'] = 0
            lottatore['tempo_reazione_ai'] = ottieni_tempo_reazione_ai(lottatore['difficolta'])
    
    # si muove verso la piattaforma scelta
    if lottatore['piattaforma_target'] and lottatore['piattaforma_target']['attiva']:
        # Ottieni il centro della piattaforma target
        tx, ty = piattaforma_ottieni_centro(lottatore['piattaforma_target'])
        
        # Calcola la direzione
        dx = tx - lottatore['x']
        dy = ty - lottatore['y']
        distanza = math.sqrt(dx**2 + dy**2)
        
        if distanza > 5:
            #  Velocità di movimento del bot
            fattore_movimento = 0.75 if lottatore['difficolta'] == "FACILE" else 0.9
            
            # Normalizza il vettore direzione e applicalo alla velocità
            lottatore['velocita_x'] += (dx / distanza) * 0.6 * fattore_movimento
            lottatore['velocita_y'] += (dy / distanza) * 0.6 * fattore_movimento
    
    # ATTACCA SE QUALCUNO È VICINO
    if lottatore['cooldown_attacco'] == 0 and tutti_lottatori:
        for altro in tutti_lottatori:
            if altro['vivo'] and altro != lottatore:
                # Calcola distanza dall'altro giocatore
                dx = altro['x'] - lottatore['x']
                dy = altro['y'] - lottatore['y']
                distanza = math.sqrt(dx**2 + dy**2)
                
                # Se è vicino, attacca (con una certa probabilità)
                if distanza < 60 and random.random() < lottatore['probabilita_attacco_ai']:
                    lottatore_esegui_attacco(lottatore, tutti_lottatori)
                    break  # Attacca solo una volta per frame


def lottatore_controlla_su_piattaforma(lottatore, lista_piattaforme, nome_colore_target=None):
    """
    Controlla se il lottatore è su una piattaforma attiva.
    Se nome_colore_target è specificato, controlla solo piattaforme di quel colore.
    
    Restituisce:
        True se è su una piattaforma del colore giusto, altrimenti False
    """
    for piattaforma in lista_piattaforme:
        
        # Controlla se è sulla piattaforma giusta
        if piattaforma['attiva'] and piattaforma_contiene_punto(piattaforma, lottatore['x'], lottatore['y']):

            if nome_colore_target is None or piattaforma['nome_colore'] == nome_colore_target:
                return True
    
    return False


def lottatore_resetta_posizione(lottatore):
    """
    Riporta il lottatore allo spawn
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
    
    """
    
    pos = (int(lottatore['x']), int(lottatore['y']))
    raggio = 28 # raggio del corpo
    
    # CORONA PER IL GIOCATORE UMANO
    if not lottatore['è_bot'] and lottatore['vivo']:
        corona_y = pos[1] - raggio - 28
 
        pygame.draw.circle(schermo, (255, 215, 0), (pos[0], corona_y), 12)
        pygame.draw.circle(schermo, (200, 150, 0), (pos[0], corona_y), 12, 2)
        
        # stella dorata
        punti = []
        for i in range(5):
            angolo = (2 * math.pi / 5) * i - math.pi / 2
            px = pos[0] + math.cos(angolo) * 9
            py = corona_y + math.sin(angolo) * 9
            punti.append((px, py))
        pygame.draw.polygon(schermo, (255, 255, 150), punti)
        
        pygame.draw.circle(schermo, (255, 215, 0), pos, raggio + 4, 4)
    
    # effetto attacco
    if lottatore['attaccando'] and lottatore['durata_attacco'] > 5:
        # cerchi gialli del raggio d'azione
        raggio_attacco = raggio + (15 - lottatore['durata_attacco']) * 3
        pygame.draw.circle(schermo, (255, 255, 0), pos, raggio_attacco, 4)
        pygame.draw.circle(schermo, (255, 200, 0), pos, raggio_attacco - 5, 2)
    # ombra
    if lottatore['vivo']:
        ombra = pygame.Surface((raggio * 3, raggio))
        ombra.set_alpha(80)  
        ombra.fill((0, 0, 0))
        schermo.blit(ombra, (pos[0] - raggio * 1.5, pos[1] + 8))
    # corpo
    raggio_corpo = raggio + (4 if lottatore['attaccando'] else 0)
    
    pygame.draw.circle(schermo, tuple(max(0, c - 40) for c in lottatore['colore_corpo']), 
                      pos, raggio_corpo)
    pygame.draw.circle(schermo, lottatore['colore_corpo'], 
                      (pos[0] - 3, pos[1] - 3), raggio_corpo - 2)
    pygame.draw.circle(schermo, tuple(min(255, c + 30) for c in lottatore['colore_corpo']), 
                      (pos[0] - 5, pos[1] - 5), raggio_corpo - 8)
    
    pygame.draw.circle(schermo, (0, 0, 0), pos, raggio_corpo, 3)
    # muscoli
    offset_muscoli = 8
    pygame.draw.circle(schermo, tuple(max(0, c - 20) for c in lottatore['colore_corpo']),
                      (pos[0] - offset_muscoli, pos[1] - 5), 10)
    pygame.draw.circle(schermo, tuple(max(0, c - 20) for c in lottatore['colore_corpo']),
                      (pos[0] + offset_muscoli, pos[1] - 5), 10)
    
    pygame.draw.line(schermo, tuple(max(0, c - 50) for c in lottatore['colore_corpo']),
                    (pos[0] - 6, pos[1] + 5), (pos[0] - 3, pos[1] + 12), 2)
    pygame.draw.line(schermo, tuple(max(0, c - 50) for c in lottatore['colore_corpo']),
                    (pos[0] + 3, pos[1] + 5), (pos[0] + 6, pos[1] + 12), 2)
    
    # cintura
    pygame.draw.rect(schermo, (40, 40, 40), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 8))
    pygame.draw.rect(schermo, (70, 70, 70), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 3))
 
    pygame.draw.circle(schermo, (200, 180, 100), (pos[0], pos[1]), 5)
    pygame.draw.circle(schermo, (150, 130, 50), (pos[0], pos[1]), 5, 2)
    
    # testa
    raggio_testa = 16
    testa_y = int(lottatore['y'] - raggio_corpo + 12)
    
    pygame.draw.circle(schermo, (230, 200, 160), (pos[0], testa_y), raggio_testa)
    pygame.draw.circle(schermo, (255, 220, 177), (pos[0] - 2, testa_y - 2), raggio_testa - 2)
    pygame.draw.circle(schermo, (0, 0, 0), (pos[0], testa_y), raggio_testa, 2)
    
    capelli_y = testa_y - raggio_testa + 4
    pygame.draw.circle(schermo, (20, 20, 20), (pos[0], capelli_y), 7)
    pygame.draw.circle(schermo, (10, 10, 10), (pos[0], capelli_y - 3), 4)
    
    # viso
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
    # nome visualizzato
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
    
    """
    lista_lottatori = []
    
    # centro piattaforme
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
        # i=0 è l'umano 
        if i == 0:
            nome = "PLAYER"
            è_bot = False
        else:
            nome = f"BOT {i}"
            è_bot = True
        
        lottatore = crea_lottatore(spawn_x, spawn_y, colori_giocatori[i], nome, è_bot, livello_difficolta)
        lista_lottatori.append(lottatore)
    
    return lista_lottatori

