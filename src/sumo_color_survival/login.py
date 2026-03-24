# login.py - the login and registration file.

# Descrizione più lunga opzionale su più righe,
# che spiega cosa fa il modulo.

# Authors: 
# Paolo Giorgi: paologiorgi04@gmail.com
# Leonardo Manzotti: leomanzotti04@gmail.com


import pygame
import json
import os
import math    
import random

# File dove vengono salvati i dati degli utenti
from platformdirs import PlatformDirs

_dirs = PlatformDirs("sumo_color_survival", ensure_exists=True)
FILE_UTENTI = _dirs.user_data_path / "utenti.json"

# Colori schermata login
COLORI_LOGIN = {
    'SFONDO':        (25, 25, 30),    # Sfondo scuro quasi nero
    'PANNELLO':      (40, 40, 50),    # Colore del pannello centrale
    'BORDO':         (100, 100, 120), # Bordo inattivo dei campi
    'BORDO_ATTIVO':  (100, 200, 255), # Bordo azzurro quando un campo è selezionato
    'TESTO':         (255, 255, 255), # Testo bianco principale
    'TESTO_GRIGIO':  (150, 150, 150), # Testo secondario (etichette campi)
    'TESTO_ERRORE':  (255, 80, 80),   # Messaggi di errore in rosso
    'TESTO_OK':      (80, 255, 80),   # Messaggi di successo in verde
    'BOTTONE':       (80, 180, 80),   # Bottone Login (verde)
    'BOTTONE_HOVER': (100, 220, 100), # Bottone Login quando il mouse ci passa sopra
    'BOTTONE2':      (60, 100, 180),  # Bottone Registrazione (blu)
    'BOTTONE2_HOVER':(80, 130, 220),  # Bottone Registrazione con hover
    'INPUT_SFONDO':  (30, 30, 40),    # Sfondo scuro dei campi di testo
}


# ==============================================================================
# GESTIONE FILE UTENTI
# ==============================================================================

def carica_utenti():
    """
    Legge il file JSON degli utenti e restituisce un dizionario {username: password}.
    Se il file non esiste o è corrotto, restituisce un dizionario vuoto.
    """
    if not os.path.exists(FILE_UTENTI):
        return {}
    try:
        f = open(FILE_UTENTI, 'r', encoding='utf-8') # utf-8 è un sistema di "traduzione" da lettere a numeri per il computer
        dati = json.load(f)
        f.close()
        return dati
    except Exception:
        return {}  # In caso di errore di lettura, si riparte da zero


def salva_utenti(utenti):
    """
    Sovrascrive il file JSON con il dizionario aggiornato degli utenti.
    """
    f = open(FILE_UTENTI, 'w', encoding='utf-8')
    json.dump(utenti, f, indent=2)
    f.close()


def registra_utente(username, password):
    """
    Tenta di registrare un nuovo utente dopo alcune validazioni:
    - Username deve avere almeno 3 caratteri
    - Password deve avere almeno 4 caratteri
    - Username non deve essere già in uso 
    Restituisce (True, messaggio) se ha successo, (False, errore) altrimenti.
    """
    if len(username.strip()) < 3:
        return False, "Username troppo corto (min. 3 caratteri)"
    if len(password) < 4:
        return False, "Password troppo corta (min. 4 caratteri)"
    
    utenti = carica_utenti()
    
    # Controlla duplicati ignorando maiuscole/minuscole
    if username.lower() in [u.lower() for u in utenti]:
        return False, "Username già in uso!"
    
    utenti[username] = password  # Aggiunge il nuovo utente al dizionario
    salva_utenti(utenti)         # Salva tutto su file
    return True, "Registrazione completata!"


def verifica_login(username, password):
    """
    Controlla se username e password corrispondono a un utente registrato.
    La ricerca dell'username è case-insensitive (Mario == mario).
    Restituisce (True, messaggio benvenuto) oppure (False, motivo errore).
    """
    if not username or not password:
        return False, "Inserisci username e password"
    
    utenti = carica_utenti()
    
    # Cerca l'username nel dizionario 
    trovato = next((u for u in utenti if u.lower() == username.lower()), None)
    if not trovato:
        return False, "Username non trovato"
    if utenti[trovato] != password:
        return False, "Password errata"
    
    return True, f"Benvenuto, {trovato}!"


# ==============================================================================
# CAMPO DI TESTO
# ==============================================================================

def crea_campo(x, y, larghezza, altezza, etichetta, nascosta=False):
    """
    Crea e restituisce un dizionario che rappresenta una casella di testo.
    Parametri principali:
      - x, y: posizione sullo schermo
      - larghezza, altezza: dimensioni del rettangolo
      - etichetta: testo descrittivo mostrato sopra alla casella
      - nascosta: se True, il testo viene mostrato come asterischi
    """
    return {
        'x': x, 'y': y,
        'larghezza': larghezza, 'altezza': altezza,
        'etichetta': etichetta,
        'testo': '',            # Testo digitato dall'utente
        'attivo': False,        # True se la casella viene usata 
        'nascosta': nascosta,   # True per le caselle password
        'cursore_visibile': True,  # Stato attuale del cursore (visibile/nascosto)
        'timer_cursore': 0,     # Contatore per controllare la frequenza del lampeggio
    }


def campo_aggiorna(campo):
    """
    Va chiamata ogni frame. Gestisce il lampeggio del cursore:
    ogni 30 frame (circa 0.5 secondi a 60fps) inverte la visibilità del cursore.
    """
    campo['timer_cursore'] += 1
    if campo['timer_cursore'] >= 30:
        campo['cursore_visibile'] = not campo['cursore_visibile']
        campo['timer_cursore'] = 0


def campo_gestisci_evento(campo, evento):
    """
    Processa gli eventi pygame relativi alla casella:
    Restituisce True solo se viene premuto INVIO.
    """
    
    # attiva il campo se il click è dentro il rettangolo
    if evento.type == pygame.MOUSEBUTTONDOWN:
        rett = pygame.Rect(campo['x'], campo['y'], campo['larghezza'], campo['altezza'])
        campo['attivo'] = rett.collidepoint(evento.pos)
    
    if evento.type == pygame.KEYDOWN and campo['attivo']:
        # cancella l'ultimo carattere
        if evento.key == pygame.K_BACKSPACE:
            campo['testo'] = campo['testo'][:-1]
            
        # segnala che l'utente ha premuto invio (restituisce True)
        elif evento.key == pygame.K_RETURN:
            return True  # Segnale di conferma (INVIO premuto)
        
        # aggiunge il carattere se stampabile e se non si supera il limite di 30 caratteri
        elif len(campo['testo']) < 30 and evento.unicode and evento.unicode.isprintable():
            campo['testo'] += evento.unicode
    return False


def campo_disegna(schermo, campo, fonts):
    """
    Disegna la casella di testo sullo schermo con:
    """
    # Etichetta sopra la casella
    surf = fonts['piccolo'].render(campo['etichetta'], True, COLORI_LOGIN['TESTO_GRIGIO'])
    schermo.blit(surf, (campo['x'], campo['y'] - 22))
    
    # Rettangolo della casella con bordo colorato se attivo
    rett = pygame.Rect(campo['x'], campo['y'], campo['larghezza'], campo['altezza'])
    pygame.draw.rect(schermo, COLORI_LOGIN['INPUT_SFONDO'], rett, border_radius=8)
    colore_bordo = COLORI_LOGIN['BORDO_ATTIVO'] if campo['attivo'] else COLORI_LOGIN['BORDO']
    pygame.draw.rect(schermo, colore_bordo, rett, 2, border_radius=8)
    
    # Mostra asterischi per le password, testo normale altrimenti
    testo = ('*' * len(campo['testo'])) if campo['nascosta'] else campo['testo']
    
    # Aggiunge il cursore lampeggiante solo se il campo è attivo
    if campo['attivo'] and campo['cursore_visibile']:
        testo += '|'
    
    surf_t = fonts['medio'].render(testo, True, COLORI_LOGIN['TESTO'])
    # Centra il testo verticalmente nel campo
    schermo.blit(surf_t, (campo['x'] + 12, campo['y'] + (campo['altezza'] - surf_t.get_height()) // 2))


# ==============================================================================
# STATO LOGIN E FUNZIONI PRINCIPALI
# ==============================================================================

def crea_stato_login():
    """
    Crea e restituisce il dizionario che contiene tutto lo stato della schermata di login.
    Calcola la posizione centrata del pannello rispetto alla finestra 1400x800.
    Inizializza i tre campi (username, password, conferma password) e la modalità iniziale (LOGIN).
    """
    larg, alt = 460, 420       
    px = (1400 - larg) // 2    
    py = (800 - alt) // 2      
    cx = px + (larg - 360) // 2  

    return {
        'modalita': 'LOGIN',        # Modalità corrente: 'LOGIN' o 'REGISTRAZIONE'
        'messaggio': '',            # Testo del messaggio di feedback all'utente
        'messaggio_ok': False,      # True = verde (successo), False = rosso (errore)
        'pannello_x': px, 'pannello_y': py,
        'pannello_larg': larg, 'pannello_alt': alt,
        'campo_username':  crea_campo(cx, py + 110, 360, 45, 'Username'),
        'campo_password':  crea_campo(cx, py + 200, 360, 45, 'Password', nascosta=True),
        # La casella conferma password è visibile solo in modalità REGISTRAZIONE
        'campo_password2': crea_campo(cx, py + 290, 360, 45, 'Conferma Password', nascosta=True),
        'link_rett': None,          # Rettangolo del link "Registrati/Accedi" (per il click)
    }


def _switch_modalita(sl):
    """
    Alterna tra la modalità LOGIN e REGISTRAZIONE.
    Resetta il contenuto di tutte le caselle e il messaggio corrente
    per avere una schermata pulita dopo il cambio.
    """
    sl['modalita'] = 'REGISTRAZIONE' if sl['modalita'] == 'LOGIN' else 'LOGIN'
    for c in ['campo_username', 'campo_password', 'campo_password2']:
        sl[c]['testo'] = ''
        sl[c]['attivo'] = False
    sl['messaggio'] = ''


def login_aggiorna(sl):
    """
    Va chiamata ogni frame nel loop principale.
    Aggiorna il timer del cursore lampeggiante per tutti le caselle visibili.
    In modalità REGISTRAZIONE aggiorna anche la casella di conferma password.
    """
    campo_aggiorna(sl['campo_username'])
    campo_aggiorna(sl['campo_password'])
    if sl['modalita'] == 'REGISTRAZIONE':
        campo_aggiorna(sl['campo_password2'])


def login_gestisci_eventi(sl, evento):
    """
    Gestisce tutti gli eventi della schermata di login:
    - TAB: sposta il focus al campo successivo (ciclicamente)
    - Click sul link: cambia modalità (login ↔ registrazione)
    - Se viene premuto INVIO o cliccato il bottone principale:
        * In LOGIN: verifica le credenziali → restituisce l'username se il login ha successo
        * In REGISTRAZIONE: valida e salva il nuovo utente, poi torna al login
    Restituisce None finché il login non ha successo, poi restituisce l'username.
    """
    campi = [sl['campo_username'], sl['campo_password']]
    if sl['modalita'] == 'REGISTRAZIONE':
        campi.append(sl['campo_password2'])

    # TAB sposta il focus alla casella successiva in modo circolare
    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_TAB:
        for i, c in enumerate(campi):
            if c['attivo']:
                c['attivo'] = False
                campi[(i + 1) % len(campi)]['attivo'] = True
                break

    # Controlla il click sul link di cambio modalità
    if evento.type == pygame.MOUSEBUTTONDOWN and sl['link_rett']:
        if sl['link_rett'].collidepoint(evento.pos):
            _switch_modalita(sl)

    # Propaga l'evento a tutti i campi; True se qualcuno ha ricevuto INVIO
    invio = any(campo_gestisci_evento(c, evento) for c in campi)

    # Controlla se il bottone principale è stato cliccato
    rett_btn = pygame.Rect(sl['pannello_x'] + 50, sl['pannello_y'] + 355, 360, 48)
    click = evento.type == pygame.MOUSEBUTTONDOWN and rett_btn.collidepoint(evento.pos)

    if click or invio:
        username = sl['campo_username']['testo'].strip()
        password = sl['campo_password']['testo']

        if sl['modalita'] == 'LOGIN':
            ok, msg = verifica_login(username, password)
            sl['messaggio'] = msg
            sl['messaggio_ok'] = ok
            if ok:
                return username 

        else:  # REGISTRAZIONE
            if password != sl['campo_password2']['testo']:
                sl['messaggio'] = "Le password non coincidono"
                sl['messaggio_ok'] = False
            else:
                ok, msg = registra_utente(username, password)
                sl['messaggio'] = msg
                sl['messaggio_ok'] = ok
                if ok:
                    _switch_modalita(sl)  # Torna automaticamente al login dopo la registrazione
                    sl['messaggio'] = "Registrato! Ora accedi."
                    sl['messaggio_ok'] = True

    return None  # Login non ancora completato


def login_disegna(schermo, sl, fonts, pos_mouse):
    """
    Disegna l'intera schermata di login ogni frame:
    1. Sfondo nero
    2. Titolo del gioco in alto
    3. Pannello con ombra, bordi arrotondati e titolo interno
    4. Separatore orizzontale sotto il titolo pannello
    5. Campi di input (username, password, e conferma se in REGISTRAZIONE)
    6. Bottone principale con effetto hover (cambia colore quando il mouse ci passa sopra)
    7. Messaggio di feedback (errore in rosso, successo in verde)
    8. Link cliccabile per passare da login a registrazione e viceversa
    """
    schermo.fill(COLORI_LOGIN['SFONDO'])

    # Titolo del gioco centrato in alto
    surf = fonts['titolo'].render("SUMO COLOR SURVIVAL", True, (255, 255, 255))
    schermo.blit(surf, surf.get_rect(center=(700, 100)))

    px, py = sl['pannello_x'], sl['pannello_y']
    larg, alt = sl['pannello_larg'], sl['pannello_alt']

    # Ombra del pannello (rettangolo leggermente spostato e più scuro)
    pygame.draw.rect(schermo, (10, 10, 15), pygame.Rect(px+6, py+6, larg, alt), border_radius=18)
    # Pannello principale
    pygame.draw.rect(schermo, COLORI_LOGIN['PANNELLO'], pygame.Rect(px, py, larg, alt), border_radius=18)
    # Bordo del pannello
    pygame.draw.rect(schermo, COLORI_LOGIN['BORDO'], pygame.Rect(px, py, larg, alt), 2, border_radius=18)

    # Titolo interno al pannello ("ACCEDI" o "CREA ACCOUNT")
    titolo = "ACCEDI" if sl['modalita'] == 'LOGIN' else "CREA ACCOUNT"
    surf_t = fonts['grande'].render(titolo, True, (255, 255, 255))
    schermo.blit(surf_t, surf_t.get_rect(center=(px + larg//2, py + 45)))
    
    # Linea separatrice sotto il titolo del pannello
    pygame.draw.line(schermo, COLORI_LOGIN['BORDO'], (px+20, py+70), (px+larg-20, py+70), 1)

    # Disegna i campi di input
    campo_disegna(schermo, sl['campo_username'], fonts)
    campo_disegna(schermo, sl['campo_password'], fonts)
    if sl['modalita'] == 'REGISTRAZIONE':
        campo_disegna(schermo, sl['campo_password2'], fonts)

    # Bottone principale con cambio colore al passaggio del mouse
    rett_btn = pygame.Rect(px + 50, py + 355, 360, 48)
    is_hover = rett_btn.collidepoint(pos_mouse)
    if sl['modalita'] == 'LOGIN':
        colore = COLORI_LOGIN['BOTTONE_HOVER'] if is_hover else COLORI_LOGIN['BOTTONE']
    else:
        colore = COLORI_LOGIN['BOTTONE2_HOVER'] if is_hover else COLORI_LOGIN['BOTTONE2']
    pygame.draw.rect(schermo, colore, rett_btn, border_radius=10)
    pygame.draw.rect(schermo, (200, 200, 200), rett_btn, 2, border_radius=10)  # Bordo grigio chiaro
    testo_btn = "ACCEDI" if sl['modalita'] == 'LOGIN' else "REGISTRATI"
    surf_btn = fonts['medio'].render(testo_btn, True, (255, 255, 255))
    schermo.blit(surf_btn, surf_btn.get_rect(center=rett_btn.center))

    # Messaggio di feedback colorato in base all'esito
    if sl['messaggio']:
        colore_msg = COLORI_LOGIN['TESTO_OK'] if sl['messaggio_ok'] else COLORI_LOGIN['TESTO_ERRORE']
        surf_msg = fonts['piccolo'].render(sl['messaggio'], True, colore_msg)
        schermo.blit(surf_msg, surf_msg.get_rect(center=(px + larg//2, py + alt - 30)))

    # Link cliccabile in fondo per cambiare modalità
    testo_link = "Non hai un account? Registrati" if sl['modalita'] == 'LOGIN' else "Hai già un account? Accedi"
    surf_link = fonts['minuscolo'].render(testo_link, True, (100, 180, 255))
    rett_link = surf_link.get_rect(center=(px + larg//2, py + alt + 30))
    schermo.blit(surf_link, rett_link)
    sl['link_rett'] = rett_link  # Salva il rettangolo per rilevare i click futuri
