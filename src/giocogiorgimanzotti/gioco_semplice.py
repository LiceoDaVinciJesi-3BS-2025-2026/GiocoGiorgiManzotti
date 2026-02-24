"""
==============================================================================
SUMO COLOR SURVIVAL - Versione Didattica per Studenti
==============================================================================

Questo è un gioco in cui 8 lottatori di sumo (1 giocatore + 7 bot) devono
sopravvivere saltando sulle piattaforme del colore giusto!

Autore: [Il tuo nome]
Classe: 3^ Liceo Scientifico
Data: [Data]

ISTRUZIONI:
- WASD per muoversi
- Click sinistro del mouse per attaccare
- Salta sul colore giusto prima che le altre piattaforme scompaiano!
- L'ultimo che rimane vince!

==============================================================================
"""

# Importiamo le librerie necessarie
import pygame  # Per creare il gioco
import math    # Per calcoli matematici (distanze, angoli)
import random  # Per generare cose casuali (posizioni colori, AI)


# ==============================================================================
# SEZIONE 1: COSTANTI DEL GIOCO
# ==============================================================================
# Le costanti sono valori che NON cambiano mai durante l'esecuzione del programma.
# In Python si scrivono SEMPRE IN MAIUSCOLO per distinguerle dalle variabili.

# ✏️ MODIFICABILE: Dimensioni della finestra di gioco
LARGHEZZA = 1400  # Larghezza finestra in pixel (puoi cambiarla!)
ALTEZZA = 800     # Altezza finestra in pixel (puoi cambiarla!)

# ✏️ MODIFICABILE: Velocità del gioco
FPS = 60  # Frame Per Secondo - quante volte al secondo si aggiorna il gioco
          # Più alto = più fluido ma più pesante
          # Valori tipici: 30, 60, 120

# Dizionario dei colori delle piattaforme
# Un dizionario è come un "vocabolario": ad ogni parola (chiave) corrisponde un significato (valore)
# Formato: 'NOME': (R, G, B) dove R=Rosso, G=Verde, B=Blu (valori da 0 a 255)
# ✏️ MODIFICABILE: Puoi cambiare i colori o aggiungerne di nuovi!
COLORI = {
    'ROSSO': (255, 0, 0),      # Rosso puro
    'BIANCO': (255, 255, 255), # Bianco
    'GIALLO': (255, 255, 0),   # Giallo
    'BLU': (0, 0, 255),        # Blu puro
    'ARANCIONE': (255, 165, 0),# Arancione
    'VERDE': (0, 255, 0)       # Verde puro
}

# Lista con i nomi dei colori (utile per sceglierne uno a caso)
NOMI_COLORI = ['ROSSO', 'BIANCO', 'GIALLO', 'BLU', 'ARANCIONE', 'VERDE']


# ==============================================================================
# SEZIONE 2: VARIABILI GLOBALI
# ==============================================================================
# Queste variabili possono essere lette e modificate da qualsiasi funzione.
# Rappresentano lo "stato" del gioco in un dato momento.

# Lo stato del gioco può essere: "MENU", "GIOCANDO", "ATTESA", "VINCITORE"
stato_gioco = "MENU"

# La difficoltà scelta: "FACILE", "MEDIO", "DIFFICILE"
difficolta = "FACILE"

# Liste vuote che verranno riempite durante il gioco
piattaforme = []  # Conterrà tutte le piattaforme colorate
lottatori = []    # Conterrà tutti i giocatori (umano + bot)

# Altre variabili di gioco
colore_target = None           # Il colore su cui bisogna saltare
conto_alla_rovescia = 3.0     # Secondi prima che le piattaforme scompaiano
numero_round = 1               # Round corrente
vincitore = None               # Chi ha vinto (None = nessuno ancora)
piattaforme_scomparse = False  # Flag: le piattaforme sono già scomparse?


# ==============================================================================
# SEZIONE 3: FUNZIONI PER LE PIATTAFORME
# ==============================================================================
# Le piattaforme sono i quadrati colorati su cui i giocatori devono saltare.
# Ogni piattaforma è un DIZIONARIO (come un contenitore di informazioni).

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
    # Creiamo un dizionario (tipo un "contenitore di informazioni")
    # Ogni informazione ha un nome (chiave) e un valore
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
    
    return piattaforma  # Restituiamo il dizionario creato


def piattaforma_inizia_scomparsa(piattaforma):
    """
    Fa iniziare l'animazione di scomparsa di una piattaforma.
    La piattaforma diventerà gradualmente più piccola fino a sparire.
    
    Parametri:
        piattaforma: il dizionario della piattaforma da far scomparire
    """
    piattaforma['attiva'] = False  # Disattiva la piattaforma


def piattaforma_aggiorna(piattaforma):
    """
    Aggiorna lo stato della piattaforma (animazione di scomparsa).
    Questa funzione viene chiamata 60 volte al secondo (per ogni frame).
    
    Parametri:
        piattaforma: il dizionario della piattaforma da aggiornare
    """
    # Se la piattaforma NON è attiva E non è ancora completamente scomparsa
    if not piattaforma['attiva'] and piattaforma['progresso_scomparsa'] < 1:
        # ✏️ MODIFICABILE: Velocità di scomparsa (0.05 = lenta, 0.1 = veloce)
        piattaforma['progresso_scomparsa'] += 0.07


def piattaforma_disegna(schermo, piattaforma):
    """
    Disegna una piattaforma sullo schermo.
    
    Parametri:
        schermo: la superficie pygame su cui disegnare
        piattaforma: il dizionario della piattaforma da disegnare
    """
    # Se la piattaforma è completamente scomparsa, non disegnarla
    if piattaforma['progresso_scomparsa'] >= 1:
        return
    
    # Se la piattaforma sta scomparendo, falla diventare più piccola
    if not piattaforma['attiva']:
        # Calcola quanto deve essere piccola (scala da 1 a 0)
        scala = 1 - piattaforma['progresso_scomparsa']
        # Calcola uno spostamento per l'effetto "implosione"
        offset = piattaforma['progresso_scomparsa'] * 20
        
        # Crea un rettangolo ridotto
        rett = pygame.Rect(
            piattaforma['x'] + offset,
            piattaforma['y'] + offset,
            piattaforma['larghezza'] * scala,
            piattaforma['altezza'] * scala
        )
    else:
        # Piattaforma normale (non sta scomparendo)
        rett = pygame.Rect(
            piattaforma['x'], 
            piattaforma['y'], 
            piattaforma['larghezza'], 
            piattaforma['altezza']
        )
    
    # Disegna il rettangolo colorato
    pygame.draw.rect(schermo, piattaforma['colore'], rett)
    # Disegna il bordo nero (spessore 4 pixel)
    # ✏️ MODIFICABILE: Cambia il 4 per bordi più sottili o più spessi
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
    # Se la piattaforma è scomparsa, non può contenere nulla
    if not piattaforma['attiva'] or piattaforma['progresso_scomparsa'] >= 1:
        return False
    
    # Controlla se x e y sono dentro l'area della piattaforma (con margine)
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
    lista_piattaforme = []  # Lista vuota che riempiremo
    
    # ✏️ MODIFICABILE: Configurazione della griglia
    righe = 6               # Numero di righe di piattaforme
    colonne = 5             # Numero di colonne di piattaforme
    larghezza_piattaforma = 140   # Larghezza di ogni piattaforma
    altezza_piattaforma = 110     # Altezza di ogni piattaforma
    spaziatura = 10         # Spazio tra le piattaforme (camminabile!)
    
    # Calcola dove posizionare la griglia per centrarla sullo schermo
    larghezza_griglia = colonne * larghezza_piattaforma + (colonne - 1) * spaziatura
    altezza_griglia = righe * altezza_piattaforma + (righe - 1) * spaziatura
    offset_x = (LARGHEZZA - larghezza_griglia) // 2  # Centra orizzontalmente
    offset_y = (ALTEZZA - altezza_griglia) // 2 + 30  # Centra verticalmente (+ 30 per HUD)
    
    # Crea una lista con esattamente 5 copie di ogni colore
    # Esempio: ['ROSSO', 'ROSSO', 'ROSSO', 'ROSSO', 'ROSSO', 'BIANCO', ...]
    lista_colori = []
    for nome_colore in NOMI_COLORI:
        # extend() aggiunge tutti gli elementi di una lista a un'altra lista
        # [nome_colore] * 5 crea una lista con nome_colore ripetuto 5 volte
        lista_colori.extend([nome_colore] * 5)
    
    # Mescola i colori in ordine casuale
    random.shuffle(lista_colori)
    
    # Crea le piattaforme con un doppio ciclo (righe e colonne)
    idx = 0  # Indice per scorrere la lista_colori
    for riga in range(righe):
        for col in range(colonne):
            # Calcola la posizione x, y di questa piattaforma
            x = offset_x + col * (larghezza_piattaforma + spaziatura)
            y = offset_y + riga * (altezza_piattaforma + spaziatura)
            
            # Prendi il colore corrispondente
            nome_colore = lista_colori[idx]
            
            # Crea la piattaforma e aggiungila alla lista
            piattaforma = crea_piattaforma(x, y, larghezza_piattaforma, altezza_piattaforma, nome_colore)
            lista_piattaforme.append(piattaforma)
            
            idx += 1  # Passa al prossimo colore
    
    return lista_piattaforme


# ==============================================================================
# SEZIONE 4: FUNZIONI PER I LOTTATORI (GIOCATORI)
# ==============================================================================
# Ogni lottatore è un dizionario con posizione, velocità, colore, ecc.

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
        
        # --- MOVIMENTO ---
        # La velocità è quanto si sposta ogni frame
        # velocità positiva = va a destra/giù, negativa = va a sinistra/su
        'velocita_x': 0,
        'velocita_y': 0,
        
        # --- ASPETTO ---
        'colore_corpo': colore_corpo,
        'nome': nome,
        'è_bot': è_bot,
        'vivo': True,
        
        # --- ATTACCO ---
        'attaccando': False,        # True durante l'animazione di attacco
        'cooldown_attacco': 0,      # Frame rimanenti prima di poter riattaccare
        'durata_attacco': 0,        # Frame rimanenti dell'animazione
        
        # --- AI (per i bot) ---
        'difficolta': difficolta,
        'piattaforma_target': None,  # Piattaforma verso cui il bot sta andando
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
        # Bot lenti: reagiscono dopo 50-80 frame (circa 0.8-1.3 secondi)
        return random.randint(50, 80)
    elif difficolta == "MEDIO":
        # Bot medi: reagiscono dopo 20-40 frame (circa 0.3-0.7 secondi)
        return random.randint(20, 40)
    else:  # DIFFICILE
        # Bot veloci: reagiscono dopo 5-15 frame (circa 0.1-0.25 secondi)
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
    
    # --- LIMITA VELOCITÀ MASSIMA ---
    # Calcola la velocità totale usando il teorema di Pitagora
    # velocità_totale = √(velocita_x² + velocita_y²)
    velocita = math.sqrt(lottatore['velocita_x']**2 + lottatore['velocita_y']**2)
    
    # ✏️ MODIFICABILE: Velocità massima
    velocita_massima = 4.0
    
    if velocita > velocita_massima:
        # Se va troppo veloce, riduci proporzionalmente
        rapporto = velocita_massima / velocita
        lottatore['velocita_x'] *= rapporto
        lottatore['velocita_y'] *= rapporto
    
    # --- APPLICA ATTRITO ---
    # L'attrito rallenta gradualmente il lottatore
    # ✏️ MODIFICABILE: Attrito (0.85 = rallenta gradualmente, 0.5 = frena molto)
    lottatore['velocita_x'] *= 0.85
    lottatore['velocita_y'] *= 0.85
    
    # --- AGGIORNA POSIZIONE ---
    # Sposta il lottatore in base alla velocità
    lottatore['x'] += lottatore['velocita_x']
    lottatore['y'] += lottatore['velocita_y']
    
    # --- LIMITI DELLO SCHERMO ---
    # Impedisce al lottatore di uscire dallo schermo
    # ✏️ MODIFICABILE: 22 è il raggio del lottatore
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
    
    # ✏️ MODIFICABILE: Parametri dell'attacco
    raggio_attacco = 50   # Quanto lontano arriva l'attacco (in pixel)
    spinta_attacco = 250  # Quanto forte spinge (più alto = più forte!)
    
    # Cerca tutti i lottatori nel raggio d'attacco
    for altro in tutti_lottatori:
        # Salta se stesso o se l'altro è morto
        if altro['vivo'] and altro != lottatore:
            # Calcola la distanza usando il teorema di Pitagora
            # distanza = √((x₂-x₁)² + (y₂-y₁)²)
            dx = altro['x'] - lottatore['x']
            dy = altro['y'] - lottatore['y']
            distanza = math.sqrt(dx**2 + dy**2)
            
            # Se è abbastanza vicino, colpiscilo!
            if distanza < raggio_attacco and distanza > 0:
                # Calcola la direzione della spinta (verso l'altro giocatore)
                # Normalizza il vettore (dx, dy) dividendo per la distanza
                # poi moltiplicalo per la forza della spinta
                spinta_x = (dx / distanza) * spinta_attacco
                spinta_y = (dy / distanza) * spinta_attacco
                
                # Applica la spinta all'avversario
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
    
    # --- DECISIONE: SCEGLI PIATTAFORMA TARGET ---
    lottatore['timer_ai'] += 1
    
    # Ogni tot frame (o se non ha un target), sceglie una nuova piattaforma
    if lottatore['timer_ai'] > lottatore['tempo_reazione_ai'] or lottatore['piattaforma_target'] is None:
        # Trova tutte le piattaforme del colore giusto e ancora attive
        piattaforme_valide = [p for p in lista_piattaforme 
                             if p['nome_colore'] == nome_colore_target and p['attiva']]
        
        if piattaforme_valide:
            # Sceglie in base alla qualità delle decisioni
            # random.random() genera un numero casuale tra 0 e 1
            if random.random() < lottatore['qualita_decisioni_ai']:
                # Scelta OTTIMALE: piattaforma più vicina
                # Usa min() con key= per trovare la piattaforma con distanza minima
                lottatore['piattaforma_target'] = min(piattaforme_valide, 
                    key=lambda p: math.sqrt((piattaforma_ottieni_centro(p)[0] - lottatore['x'])**2 + 
                                           (piattaforma_ottieni_centro(p)[1] - lottatore['y'])**2))
            else:
                # Scelta CASUALE
                lottatore['piattaforma_target'] = random.choice(piattaforme_valide)
            
            # Reset del timer
            lottatore['timer_ai'] = 0
            lottatore['tempo_reazione_ai'] = ottieni_tempo_reazione_ai(lottatore['difficolta'])
    
    # --- AZIONE: MUOVITI VERSO IL TARGET ---
    if lottatore['piattaforma_target'] and lottatore['piattaforma_target']['attiva']:
        # Ottieni il centro della piattaforma target
        tx, ty = piattaforma_ottieni_centro(lottatore['piattaforma_target'])
        
        # Calcola il vettore direzione (verso la piattaforma)
        dx = tx - lottatore['x']
        dy = ty - lottatore['y']
        distanza = math.sqrt(dx**2 + dy**2)
        
        # Se non è già arrivato, muoviti
        if distanza > 5:
            # ✏️ MODIFICABILE: Velocità di movimento del bot
            # 0.75 per facile, 0.9 per medio/difficile
            fattore_movimento = 0.75 if lottatore['difficolta'] == "FACILE" else 0.9
            
            # Normalizza il vettore direzione e applicalo alla velocità
            lottatore['velocita_x'] += (dx / distanza) * 0.6 * fattore_movimento
            lottatore['velocita_y'] += (dy / distanza) * 0.6 * fattore_movimento
    
    # --- AZIONE: ATTACCA SE QUALCUNO È VICINO ---
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
        True se è su una piattaforma (del colore giusto), False altrimenti
    """
    for piattaforma in lista_piattaforme:
        # Controlla se è su questa piattaforma
        if piattaforma['attiva'] and piattaforma_contiene_punto(piattaforma, lottatore['x'], lottatore['y']):
            # Se non ci interessa il colore, o se il colore è giusto
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
    raggio = 28  # ✏️ Raggio del corpo (più grande = lottatore più grosso)
    
    # --- CORONA PER IL GIOCATORE UMANO ---
    if not lottatore['è_bot'] and lottatore['vivo']:
        corona_y = pos[1] - raggio - 28
        
        # Cerchio dorato
        pygame.draw.circle(schermo, (255, 215, 0), (pos[0], corona_y), 12)
        pygame.draw.circle(schermo, (200, 150, 0), (pos[0], corona_y), 12, 2)
        
        # Stella a 5 punte dentro la corona
        punti = []
        for i in range(5):
            angolo = (2 * math.pi / 5) * i - math.pi / 2
            px = pos[0] + math.cos(angolo) * 9
            py = corona_y + math.sin(angolo) * 9
            punti.append((px, py))
        pygame.draw.polygon(schermo, (255, 255, 150), punti)
        
        # Bordo dorato intorno al personaggio
        pygame.draw.circle(schermo, (255, 215, 0), pos, raggio + 4, 4)
    
    # --- EFFETTO ATTACCO ---
    if lottatore['attaccando'] and lottatore['durata_attacco'] > 5:
        # Cerchi gialli che si espandono
        raggio_attacco = raggio + (15 - lottatore['durata_attacco']) * 3
        pygame.draw.circle(schermo, (255, 255, 0), pos, raggio_attacco, 4)
        pygame.draw.circle(schermo, (255, 200, 0), pos, raggio_attacco - 5, 2)
    
    # --- OMBRA ---
    if lottatore['vivo']:
        ombra = pygame.Surface((raggio * 3, raggio))
        ombra.set_alpha(80)  # Trasparenza
        ombra.fill((0, 0, 0))
        schermo.blit(ombra, (pos[0] - raggio * 1.5, pos[1] + 8))
    
    # --- CORPO MUSCOLOSO ---
    raggio_corpo = raggio + (4 if lottatore['attaccando'] else 0)
    
    # Effetto 3D con 3 cerchi sfumati
    # ✏️ MODIFICABILE: Cambia i numeri (-40, -20, +30) per sfumature diverse
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
    
    # --- CINTURA ---
    pygame.draw.rect(schermo, (40, 40, 40), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 8))
    pygame.draw.rect(schermo, (70, 70, 70), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 3))
    # Fibbia dorata
    pygame.draw.circle(schermo, (200, 180, 100), (pos[0], pos[1]), 5)
    pygame.draw.circle(schermo, (150, 130, 50), (pos[0], pos[1]), 5, 2)
    
    # --- TESTA ---
    raggio_testa = 16
    testa_y = int(lottatore['y'] - raggio_corpo + 12)
    
    # Sfumatura testa (effetto 3D)
    pygame.draw.circle(schermo, (230, 200, 160), (pos[0], testa_y), raggio_testa)
    pygame.draw.circle(schermo, (255, 220, 177), (pos[0] - 2, testa_y - 2), raggio_testa - 2)
    pygame.draw.circle(schermo, (0, 0, 0), (pos[0], testa_y), raggio_testa, 2)
    
    # Chonmage (nodo capelli tradizionale sumo)
    capelli_y = testa_y - raggio_testa + 4
    pygame.draw.circle(schermo, (20, 20, 20), (pos[0], capelli_y), 7)
    pygame.draw.circle(schermo, (10, 10, 10), (pos[0], capelli_y - 3), 4)
    
    # --- VISO ESPRESSIVO ---
    offset_occhi = 6
    occhi_y = testa_y + 2
    
    if lottatore['attaccando']:
        # Occhi chiusi (aggressivo)
        pygame.draw.line(schermo, (0, 0, 0), 
                       (pos[0] - offset_occhi - 3, occhi_y),
                       (pos[0] - offset_occhi + 3, occhi_y - 2), 3)
        pygame.draw.line(schermo, (0, 0, 0),
                       (pos[0] + offset_occhi - 3, occhi_y - 2),
                       (pos[0] + offset_occhi + 3, occhi_y), 3)
    else:
        # Occhi aperti
        # Bianco dell'occhio
        pygame.draw.ellipse(schermo, (255, 255, 255), 
                          (pos[0] - offset_occhi - 4, occhi_y - 3, 8, 6))
        pygame.draw.ellipse(schermo, (255, 255, 255), 
                          (pos[0] + offset_occhi - 4, occhi_y - 3, 8, 6))
        # Iride marrone
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] - offset_occhi, occhi_y), 3)
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] + offset_occhi, occhi_y), 3)
        # Pupilla nera
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
    
    # Bocca (cambia se sta attaccando)
    if lottatore['attaccando']:
        # Bocca seria
        pygame.draw.arc(schermo, (100, 50, 50), 
                       (pos[0] - 6, testa_y + 10, 12, 8), 0, math.pi, 2)
    else:
        # Bocca sorridente
        pygame.draw.arc(schermo, (150, 80, 80), 
                       (pos[0] - 7, testa_y + 8, 14, 10), math.pi, 2 * math.pi, 2)
    
    # --- NOME ---
    if lottatore['vivo']:
        font = pygame.font.Font(None, 22 if not lottatore['è_bot'] else 20)
        colore_nome = (255, 215, 0) if not lottatore['è_bot'] else (255, 255, 255)
        superficie_nome = font.render(lottatore['nome'], True, colore_nome)
        rett_nome = superficie_nome.get_rect(center=(pos[0], pos[1] - raggio_corpo - 15))
        
        # Sfondo nome
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
    
    # Centro della griglia
    centro_griglia_x = LARGHEZZA // 2
    centro_griglia_y = ALTEZZA // 2 + 30
    
    # ✏️ MODIFICABILE: Numero di giocatori
    num_giocatori = 8
    
    # ✏️ MODIFICABILE: Distanza dal centro dove spawnano
    raggio_spawn = 100
    
    # ✏️ MODIFICABILE: Colori dei giocatori (uno per ognuno)
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
    
    # Crea i giocatori disposti in cerchio
    for i in range(num_giocatori):
        # Calcola l'angolo per questo giocatore (divisione equa del cerchio)
        angolo = (2 * math.pi / num_giocatori) * i
        
        # Calcola posizione x, y usando seno e coseno
        spawn_x = centro_griglia_x + math.cos(angolo) * raggio_spawn
        spawn_y = centro_griglia_y + math.sin(angolo) * raggio_spawn
        
        # Il primo giocatore (i=0) è quello umano
        if i == 0:
            nome = "TU"
            è_bot = False
        else:
            nome = f"BOT {i}"
            è_bot = True
        
        # Crea il lottatore e aggiungilo alla lista
        lottatore = crea_lottatore(spawn_x, spawn_y, colori_giocatori[i], nome, è_bot, livello_difficolta)
        lista_lottatori.append(lottatore)
    
    return lista_lottatori


# ==============================================================================
# SEZIONE 5: FUNZIONI PER IL MENU E L'INTERFACCIA
# ==============================================================================
# Queste funzioni disegnano menu, HUD, bottoni, ecc.

def disegna_pannello(schermo, rett, titolo, font):
    """
    Disegna un pannello bianco moderno con ombra e titolo.
    Usato nel menu principale.
    """
    # Ombra (rettangolo nero spostato)
    rett_ombra = rett.copy()
    rett_ombra.x += 5
    rett_ombra.y += 5
    pygame.draw.rect(schermo, (10, 10, 15), rett_ombra, border_radius=15)
    
    # Pannello bianco
    pygame.draw.rect(schermo, (240, 240, 245), rett, border_radius=15)
    pygame.draw.rect(schermo, (200, 200, 210), rett, 3, border_radius=15)
    
    # Header (parte superiore colorata)
    rett_header = pygame.Rect(rett.x, rett.y, rett.width, 50)
    pygame.draw.rect(schermo, (220, 220, 230), rett_header, 
                    border_top_left_radius=15, border_top_right_radius=15)
    
    # Titolo centrato
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
    # Titolo grande in alto
    titolo = fonts['titolo'].render("SUMO COLOR SURVIVAL", True, (255, 255, 255))
    rett_titolo = titolo.get_rect(center=(LARGHEZZA // 2, 120))
    schermo.blit(titolo, rett_titolo)
    
    # ✏️ MODIFICABILE: Dimensioni e posizioni dei pannelli
    larghezza_pannello = 380
    altezza_pannello = 280
    spaziatura_pannello = 50
    
    # Calcola posizioni per centrare i 3 pannelli
    larghezza_totale = larghezza_pannello * 3 + spaziatura_pannello * 2
    inizio_x = (LARGHEZZA - larghezza_totale) // 2
    centro_y = ALTEZZA // 2
    
    # Crea i 3 rettangoli per i pannelli
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
    
    # --- PANNELLO 1: DIFFICOLTÀ ---
    pannello = rett_pannelli['difficolta']
    disegna_pannello(schermo, pannello, "DIFFICOLTÀ", fonts['medio'])
    
    # Dati per i 3 bottoni difficoltà
    dati_diff = [
        ("FACILE", "FACILE", (100, 255, 100)),
        ("MEDIO", "MEDIO", (255, 200, 100)),
        ("DIFFICILE", "DIFFICILE", (255, 100, 100))
    ]
    
    bottoni_difficolta = {}
    y_bottone = pannello.y + 80
    
    # Disegna i 3 bottoni
    for i, (valore_diff, testo_diff, colore_diff) in enumerate(dati_diff):
        bottone = pygame.Rect(pannello.centerx - 150, y_bottone + i * 60, 300, 50)
        bottoni_difficolta[valore_diff] = bottone
        
        # Controlla se selezionato o hover
        è_selezionato = (difficolta == valore_diff)
        è_hover = bottone.collidepoint(pos_mouse)
        
        # Disegna il bottone con colore appropriato
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
        
        # Scrivi il testo del bottone
        testo_btn = fonts['medio'].render(testo_diff, True, colore_testo)
        rett_testo_btn = testo_btn.get_rect(center=bottone.center)
        schermo.blit(testo_btn, rett_testo_btn)
    
    # --- PANNELLO 2: CONTROLLI ---
    pannello = rett_pannelli['controlli']
    disegna_pannello(schermo, pannello, "CONTROLLI", fonts['medio'])
    
    # Testi da mostrare (uno per riga)
    controlli = [
        "WASD - Movimento",
        "",
        "Click Sinistro",
        "Attacco Pancia",
        "",
        "Obiettivo:",
        "Colore giusto!"
    ]
    
    # Scrivi i testi
    offset_y = pannello.y + 70
    for testo in controlli:
        if testo:  # Salta righe vuote
            surf = fonts['piccolo'].render(testo, True, (50, 50, 50))
            rett = surf.get_rect(center=(pannello.centerx, offset_y))
            schermo.blit(surf, rett)
        offset_y += 28
    
    # --- PANNELLO 3: INIZIA ---
    pannello = rett_pannelli['inizio']
    disegna_pannello(schermo, pannello, "GIOCA", fonts['medio'])
    
    # Bottone INIZIA grande
    bottone_inizio = pygame.Rect(pannello.centerx - 150, pannello.centery - 40, 300, 80)
    è_hover_inizio = bottone_inizio.collidepoint(pos_mouse)
    
    # Cambia colore se hover
    if è_hover_inizio:
        pygame.draw.rect(schermo, (100, 220, 100), bottone_inizio, border_radius=15)
    else:
        pygame.draw.rect(schermo, (80, 180, 80), bottone_inizio, border_radius=15)
    
    pygame.draw.rect(schermo, (150, 255, 150), bottone_inizio, 4, border_radius=15)
    
    # Testo "INIZIA"
    testo_inizio = fonts['grande'].render("INIZIA", True, (255, 255, 255))
    rett_testo_inizio = testo_inizio.get_rect(center=bottone_inizio.center)
    schermo.blit(testo_inizio, rett_testo_inizio)
    
    # Info sotto i pannelli
    info = fonts['piccolo'].render("8 Giocatori - Sopravvivi!", True, (150, 150, 150))
    rett_info = info.get_rect(center=(LARGHEZZA // 2, ALTEZZA - 50))
    schermo.blit(info, rett_info)
    
    return bottoni_difficolta, bottone_inizio


def disegna_hud_gioco(schermo, fonts, num_round, diff, col_target, stato, conta, lista_lottatori):
    """
    Disegna l'HUD (interfaccia utente) durante il gioco.
    Include: round, difficoltà, colore target, countdown, giocatori vivi, pannello attacco.
    """
    # Barra superiore scura
    pygame.draw.rect(schermo, (0, 0, 0, 200), (0, 0, LARGHEZZA, 90))
    
    # --- SINISTRA: Round e Difficoltà ---
    testo_round = fonts['medio'].render(f"ROUND {num_round}", True, (255, 255, 255))
    schermo.blit(testo_round, (20, 15))
    
    nomi_diff = {"FACILE": "FACILE", "MEDIO": "MEDIO", "DIFFICILE": "DIFFICILE"}
    colori_diff = {"FACILE": (100, 255, 100), "MEDIO": (255, 200, 100), "DIFFICILE": (255, 100, 100)}
    testo_diff = fonts['piccolo'].render(nomi_diff[diff], True, colori_diff[diff])
    schermo.blit(testo_diff, (20, 55))
    
    # --- CENTRO: Colore Target e Countdown ---
    if stato == "GIOCANDO":
        # Nome del colore grande
        testo_target = fonts['grande'].render(f"{col_target}", True, COLORI[col_target])
        rett_target = testo_target.get_rect(center=(LARGHEZZA // 2, 35))
        
        # Box colorato intorno
        rett_box = rett_target.inflate(40, 20)
        pygame.draw.rect(schermo, COLORI[col_target], rett_box, 5, border_radius=10)
        
        schermo.blit(testo_target, rett_target)
        
        # Countdown numerico
        if conta > 0:
            testo_conta = fonts['grande'].render(f"{int(conta) + 1}", True, (255, 200, 0))
            rett_conta = testo_conta.get_rect(center=(LARGHEZZA // 2, 75))
            schermo.blit(testo_conta, rett_conta)
    
    # --- DESTRA: Giocatori Vivi ---
    conteggio_vivi = sum(1 for l in lista_lottatori if l['vivo'])
    testo_vivi = fonts['medio'].render(f"Vivi: {conteggio_vivi}/8", True, (0, 255, 0))
    schermo.blit(testo_vivi, (LARGHEZZA - 150, 15))
    
    # --- PANNELLO ATTACCO (DESTRA) ---
    # Trova il giocatore umano
    giocatore = None
    for l in lista_lottatori:
        if not l['è_bot']:
            giocatore = l
            break
    
    # Se il giocatore è vivo, mostra il pannello
    if giocatore and giocatore['vivo']:
        x_pannello = LARGHEZZA - 300
        y_pannello = 120
        largh_pannello = 280
        alt_pannello = 140
        
        # Disegna pannello
        rett_pannello = pygame.Rect(x_pannello, y_pannello, largh_pannello, alt_pannello)
        pygame.draw.rect(schermo, (40, 40, 50), rett_pannello, border_radius=10)
        pygame.draw.rect(schermo, (100, 100, 120), rett_pannello, 3, border_radius=10)
        
        # Titolo pannello
        titolo = fonts['piccolo'].render("ATTACCO PANCIA", True, (255, 215, 0))
        rett_titolo = titolo.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 25))
        schermo.blit(titolo, rett_titolo)
        
        # Descrizioni
        desc1 = fonts['piccolo'].render("Click Sinistro per colpire", True, (200, 200, 200))
        rett_desc1 = desc1.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 55))
        schermo.blit(desc1, rett_desc1)
        
        desc2 = fonts['piccolo'].render("Spinta: SUPER FORTE!", True, (255, 150, 150))
        rett_desc2 = desc2.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 75))
        schermo.blit(desc2, rett_desc2)
        
        # --- BARRA RICARICA ---
        largh_barra = 240
        alt_barra = 25
        x_barra = x_pannello + (largh_pannello - largh_barra) // 2
        y_barra = y_pannello + 100
        
        # Sfondo barra
        pygame.draw.rect(schermo, (60, 60, 70), (x_barra, y_barra, largh_barra, alt_barra), border_radius=5)
        
        if giocatore['cooldown_attacco'] > 0:
            # Sta ricaricando
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
    """
    Disegna il bottone "Nuova Partita" durante il gioco.
    Posizionato in basso a sinistra.
    
    Restituisce: il rett del bottone
    """
    bottone_riavvio = pygame.Rect(40, ALTEZZA // 2 - 50, 300, 100)
    è_hover = bottone_riavvio.collidepoint(pos_mouse)
    
    # Cambia colore se hover
    if è_hover:
        colore_bottone = (180, 40, 40)
        colore_bordo = (255, 120, 120)
    else:
        colore_bottone = (120, 30, 30)
        colore_bordo = (200, 80, 80)
    
    # Disegna bottone
    pygame.draw.rect(schermo, colore_bottone, bottone_riavvio, border_radius=15)
    pygame.draw.rect(schermo, colore_bordo, bottone_riavvio, 4, border_radius=15)
    
    # Icona freccia circolare
    testo_icona = fonts['grande'].render("↻", True, (255, 255, 255))
    rett_icona = testo_icona.get_rect(center=(bottone_riavvio.centerx, bottone_riavvio.centery - 15))
    schermo.blit(testo_icona, rett_icona)
    
    # Testo
    testo_bottone = fonts['piccolo'].render("Nuova Partita", True, (255, 255, 200))
    rett_testo_bottone = testo_bottone.get_rect(center=(bottone_riavvio.centerx, bottone_riavvio.centery + 25))
    schermo.blit(testo_bottone, rett_testo_bottone)
    
    return bottone_riavvio


def disegna_schermata_vincitore(schermo, fonts, lottatore_vincitore, num_round, diff):
    """
    Disegna la schermata finale quando qualcuno vince.
    """
    # Overlay scuro semi-trasparente
    overlay = pygame.Surface((LARGHEZZA, ALTEZZA))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    schermo.blit(overlay, (0, 0))
    
    # Testo vincitore
    if lottatore_vincitore:
        # C'è un vincitore!
        testo_vincitore = fonts['titolo'].render(f"🏆 {lottatore_vincitore['nome']} VINCE! 🏆", 
                                                 True, (255, 215, 0))
        
        # Disegna il vincitore al centro
        lottatore_vincitore['x'] = LARGHEZZA // 2
        lottatore_vincitore['y'] = ALTEZZA // 2 + 80
        lottatore_disegna(schermo, lottatore_vincitore)
    else:
        # Pareggio (tutti morti)
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
    
    # Istruzioni per riavviare
    testo_riavvio = fonts['piccolo'].render("Premi SPAZIO per giocare ancora", True, (200, 200, 200))
    rett_riavvio = testo_riavvio.get_rect(center=(LARGHEZZA // 2, ALTEZZA - 100))
    schermo.blit(testo_riavvio, rett_riavvio)


# ==============================================================================
# SEZIONE 6: FUNZIONE PRINCIPALE (MAIN)
# ==============================================================================
# Questa è la funzione che fa partire tutto!

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
    # Usa le variabili globali (definite fuori dalle funzioni)
    global stato_gioco, difficolta, piattaforme, lottatori, colore_target
    global conto_alla_rovescia, numero_round, vincitore, piattaforme_scomparse
    
    # --- INIZIALIZZAZIONE ---
    pygame.init()  # Inizializza Pygame
    schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    pygame.display.set_caption("Sumo Color Survival")
    orologio = pygame.time.Clock()  # Per controllare gli FPS
    
    # Crea i font (dimensioni diverse per testi diversi)
    fonts = {
        'titolo': pygame.font.Font(None, 70),
        'grande': pygame.font.Font(None, 50),
        'medio': pygame.font.Font(None, 36),
        'piccolo': pygame.font.Font(None, 28),
        'minuscolo': pygame.font.Font(None, 22)
    }
    
    # Variabili per tenere traccia dei bottoni
    bottoni_difficolta = {}
    bottone_inizio = None
    bottone_riavvio = None
    
    # --- LOOP PRINCIPALE ---
    # Questo loop si ripete 60 volte al secondo (FPS)
    in_esecuzione = True
    while in_esecuzione:
        
        # Ottieni posizione del mouse
        pos_mouse = pygame.mouse.get_pos()
        
        # --- GESTIONE EVENTI ---
        # Un "evento" è qualcosa che succede: click, tasto premuto, finestra chiusa, ecc.
        for evento in pygame.event.get():
            
            # Chiusura finestra (X rosso)
            if evento.type == pygame.QUIT:
                in_esecuzione = False
            
            # Tasto premuto
            elif evento.type == pygame.KEYDOWN:
                # SPAZIO nella schermata vincitore = torna al menu
                if evento.key == pygame.K_SPACE and stato_gioco == "VINCITORE":
                    stato_gioco = "MENU"
            
            # Click del mouse
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:  # 1 = click sinistro
                
                # --- CLICK NEL MENU ---
                if stato_gioco == "MENU":
                    # Controlla click sui bottoni difficoltà
                    for valore_diff, rett_bottone in bottoni_difficolta.items():
                        if rett_bottone.collidepoint(pos_mouse):
                            difficolta = valore_diff
                    
                    # Controlla click sul bottone INIZIA
                    if bottone_inizio and bottone_inizio.collidepoint(pos_mouse):
                        # --- INIZIA IL GIOCO! ---
                        
                        # Crea piattaforme e lottatori
                        piattaforme = crea_tutte_piattaforme()
                        lottatori = crea_tutti_lottatori(difficolta)
                        
                        # Reset variabili
                        numero_round = 1
                        vincitore = None
                        piattaforme_scomparse = False
                        
                        # Inizia il primo round
                        stato_gioco = "GIOCANDO"
                        conto_alla_rovescia = 3.0
                        colore_target = random.choice(NOMI_COLORI)
                        
                        # Attiva tutte le piattaforme
                        for piattaforma in piattaforme:
                            piattaforma['attiva'] = True
                            piattaforma['progresso_scomparsa'] = 0
                        
                        # Reset AI dei bot
                        for lottatore in lottatori:
                            if lottatore['è_bot']:
                                lottatore['timer_ai'] = 0
                                lottatore['piattaforma_target'] = None
                
                # --- CLICK DURANTE IL GIOCO ---
                elif stato_gioco in ["GIOCANDO", "ATTESA"]:
                    # Controlla click sul bottone RIAVVIO
                    if bottone_riavvio and bottone_riavvio.collidepoint(pos_mouse):
                        stato_gioco = "MENU"
        
        # ==============================================================
        # AGGIORNA LO STATO DEL GIOCO
        # ==============================================================
        
        if stato_gioco == "GIOCANDO":
            # --- FASE DI GIOCO: COUNTDOWN ---
            # Diminuisci il countdown (1/60 = un frame)
            conto_alla_rovescia -= 1/60
            
            # Ottieni input da tastiera e mouse
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            # Aggiorna tutti i lottatori vivi
            for lottatore in lottatori:
                if lottatore['vivo']:
                    lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            # Quando il countdown arriva a zero...
            if conto_alla_rovescia <= 0:
                # Fa scomparire tutte le piattaforme del colore SBAGLIATO
                for piattaforma in piattaforme:
                    if piattaforma['nome_colore'] != colore_target:
                        piattaforma_inizia_scomparsa(piattaforma)
                
                piattaforme_scomparse = True
                
                # Controlla chi è su piattaforme sbagliate e falli morire
                for lottatore in lottatori:
                    if lottatore['vivo']:
                        su_corretta = False
                        
                        # Cerca se è su almeno una piattaforma del colore giusto
                        for piattaforma in piattaforme:
                            if (piattaforma['nome_colore'] == colore_target and 
                                piattaforma['attiva'] and 
                                piattaforma_contiene_punto(piattaforma, lottatore['x'], lottatore['y'])):
                                su_corretta = True
                                break
                        
                        # Se non è su una piattaforma corretta, muore!
                        if not su_corretta:
                            lottatore['vivo'] = False
                
                # Passa alla fase di attesa
                stato_gioco = "ATTESA"
                conto_alla_rovescia = 2.0  # Attendi 2 secondi prima del prossimo round
            
            # Aggiorna animazione piattaforme
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
        
        elif stato_gioco == "ATTESA":
            # --- FASE DI ATTESA: TRA UN ROUND E L'ALTRO ---
            conto_alla_rovescia -= 1/60
            
            # Continua ad aggiornare i lottatori (anche quelli che cadono)
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            for lottatore in lottatori:
                lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            # CONTROLLO IMPORTANTE: chi esce dalle piattaforme giuste, muore!
            if piattaforme_scomparse:
                for lottatore in lottatori:
                    if lottatore['vivo']:
                        if not lottatore_controlla_su_piattaforma(lottatore, piattaforme, colore_target):
                            lottatore['vivo'] = False
            
            # Aggiorna piattaforme
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
            
            # Quando il countdown finisce...
            if conto_alla_rovescia <= 0:
                # Conta i sopravvissuti
                lottatori_vivi = [l for l in lottatori if l['vivo']]
                
                if len(lottatori_vivi) == 1:
                    # UN SOLO SOPRAVVISSUTO = VINCITORE!
                    vincitore = lottatori_vivi[0]
                    stato_gioco = "VINCITORE"
                
                elif len(lottatori_vivi) == 0:
                    # NESSUN SOPRAVVISSUTO = PAREGGIO
                    vincitore = None
                    stato_gioco = "VINCITORE"
                
                else:
                    # PIÙ SOPRAVVISSUTI = NUOVO ROUND!
                    numero_round += 1
                    
                    # Crea nuove piattaforme (colori mescolati diversamente)
                    piattaforme = crea_tutte_piattaforme()
                    
                    # Respawn dei sopravvissuti al centro
                    num_vivi = len(lottatori_vivi)
                    centro_griglia_x = LARGHEZZA // 2
                    centro_griglia_y = ALTEZZA // 2 + 30
                    raggio_spawn = 100
                    
                    for i, lottatore in enumerate(lottatori_vivi):
                        angolo = (2 * math.pi / num_vivi) * i
                        lottatore['spawn_x'] = centro_griglia_x + math.cos(angolo) * raggio_spawn
                        lottatore['spawn_y'] = centro_griglia_y + math.sin(angolo) * raggio_spawn
                        lottatore_resetta_posizione(lottatore)
                    
                    # Inizia il nuovo round
                    stato_gioco = "GIOCANDO"
                    conto_alla_rovescia = 3.0
                    piattaforme_scomparse = False
                    colore_target = random.choice(NOMI_COLORI)
                    
                    # Reset AI
                    for lottatore in lottatori:
                        if lottatore['è_bot']:
                            lottatore['timer_ai'] = 0
                            lottatore['piattaforma_target'] = None
        
        # ==============================================================
        # DISEGNA TUTTO SULLO SCHERMO
        # ==============================================================
        
        # Cancella schermo con colore di sfondo
        schermo.fill((25, 25, 30))  # Grigio scuro
        
        # Disegna in base allo stato
        if stato_gioco == "MENU":
            # Disegna il menu
            bottoni_difficolta, bottone_inizio = disegna_menu(schermo, fonts, pos_mouse)
        
        elif stato_gioco in ["GIOCANDO", "ATTESA"]:
            # Disegna il gioco
            
            # Prima le piattaforme (sotto)
            for piattaforma in piattaforme:
                piattaforma_disegna(schermo, piattaforma)
            
            # Poi i lottatori (sopra)
            for lottatore in lottatori:
                lottatore_disegna(schermo, lottatore)
            
            # Poi l'HUD (interfaccia)
            disegna_hud_gioco(schermo, fonts, numero_round, difficolta, colore_target, 
                           stato_gioco, conto_alla_rovescia, lottatori)
            
            # Infine il bottone riavvio
            bottone_riavvio = disegna_bottone_riavvio(schermo, fonts, pos_mouse)
        
        elif stato_gioco == "VINCITORE":
            # Disegna schermata vincitore
            disegna_schermata_vincitore(schermo, fonts, vincitore, numero_round, difficolta)
        
        # Aggiorna lo schermo (rende visibili tutti i disegni)
        pygame.display.flip()
        
        # Limita il gioco a 60 FPS
        orologio.tick(FPS)
    
    # Fine del gioco: chiudi Pygame
    pygame.quit()


# ==============================================================================
# PUNTO DI PARTENZA DEL PROGRAMMA
# ==============================================================================
# Quando esegui questo file, Python parte da qui!

if __name__ == "__main__":
    # Esegui la funzione main
    main()


"""
==============================================================================
GUIDA ALLE MODIFICHE - COSA PUOI CAMBIARE
==============================================================================

✏️ MODIFICHE FACILI (cerca "✏️ MODIFICABILE" nel codice):

1. DIMENSIONI FINESTRA (righe 30-31)
   - Cambia LARGHEZZA e ALTEZZA per finestra più grande/piccola

2. VELOCITÀ GIOCO (riga 35)
   - Cambia FPS (30=lento, 60=normale, 120=velocissimo)

3. COLORI PIATTAFORME (righe 41-48)
   - Cambia i valori (R, G, B) o aggiungi nuovi colori

4. DIMENSIONI PIATTAFORME (righe 204-207)
   - Cambia larghezza_piattaforma, altezza_piattaforma, spaziatura

5. NUMERO GIOCATORI (riga 729)
   - Cambia num_giocatori per più/meno giocatori

6. DIFFICOLTÀ BOT (righe 334-363)
   - Cambia i numeri in ottieni_tempo_reazione_ai
   - Cambia i numeri in ottieni_qualita_decisioni_ai
   - Cambia i numeri in ottieni_probabilita_attacco_ai

7. FORZA ATTACCO (righe 432-434)
   - Cambia raggio_attacco (quanto lontano colpisce)
   - Cambia spinta_attacco (quanto forte spinge)

8. VELOCITÀ MOVIMENTO (righe 388-390)
   - Cambia accelerazione per giocatori più veloci/lenti
   - Cambia velocita_massima per limite di velocità

9. COLORI GIOCATORI (righe 732-741)
   - Cambia i valori RGB in colori_giocatori

10. ASPETTO LOTTATORI (righe 595-690)
    - Cambia raggio per dimensioni
    - Cambia colori di pelle, muscoli, ecc.

==============================================================================
STRUTTURA DEL CODICE (per capire come funziona): 

1. COSTANTI (righe 20-50)
   - Valori fissi usati in tutto il programma

2. VARIABILI GLOBALI (righe 55-75)
   - Lo stato del gioco che cambia durante l'esecuzione

3. PIATTAFORME (righe 80-230)
   - Funzioni per creare, disegnare, gestire le piattaforme

4. LOTTATORI (righe 235-750)
   - Funzioni per creare, muovere, disegnare i giocatori

5. INTERFACCIA (righe 755-1050)
   - Funzioni per menu, HUD, bottoni

6. MAIN (righe 1055-fine)
   - Loop principale del gioco

==============================================================================
CONSIGLI PER STUDENTI:

1. Inizia modificando cose semplici (colori, dimensioni)
2. Sperimenta con UN parametro alla volta
3. Se qualcosa si rompe, usa CTRL+Z per tornare indietro
4. Leggi i commenti per capire cosa fa ogni parte
5. Prova ad aggiungere print() per vedere cosa succede

Buon divertimento! 🎮
==============================================================================
"""