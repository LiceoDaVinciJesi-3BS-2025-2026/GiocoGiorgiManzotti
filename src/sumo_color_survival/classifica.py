import pygame
import json
import os
import math    
import random

# File dove viene salvata la classifica tra una sessione e l'altra
from platformdirs import PlatformDirs

_dirs = PlatformDirs("sumo_color_survival", ensure_exists=True)
FILE_CLASSIFICA = _dirs.user_data_path / "classifica.json"


# ==============================================================================
# GESTIONE FILE CLASSIFICA
# ==============================================================================

def carica_classifica():
    """
    Legge il file classifica.json e restituisce il dizionario degli utenti.
    Se il file non esiste ancora (prima volta), restituisce un dizionario vuoto.
    """
    if not os.path.exists(FILE_CLASSIFICA):
        return {}
    try:
        f = open(FILE_CLASSIFICA, 'r', encoding='utf-8')
        dati = json.load(f)
        f.close()
        return dati
    except Exception:
        # se il file è corrotto o illeggibile, riparte da zero
        return {}


def salva_classifica(classifica):
    """
    Salva il dizionario della classifica nel file JSON locale.
    Viene chiamata ogni volta che un utente vince in modalità DIFFICILE.

    Parametri:
        classifica: dizionario { 'username': numero_vittorie, ... }
    """
    f = open(FILE_CLASSIFICA, 'w', encoding='utf-8')
    json.dump(classifica, f, indent=2)
    f.close()


def aggiungi_vittoria(username):
    """
    Aggiunge una vittoria all'utente nella classifica e salva il file.
    Se l'utente non è ancora in classifica, lo aggiunge con 1 vittoria.
    Se è già presente, incrementa il suo contatore di 1.

    Parametri:
        username: nome dell'utente che ha vinto
    """
    classifica = carica_classifica()

    if username in classifica:
        classifica[username] += 1   # utente già presente: aggiunge 1
    else:
        classifica[username] = 1    # primo accesso in classifica

    salva_classifica(classifica)


def ottieni_classifica_ordinata():
    """
    Carica la classifica e la ordina dal più vittorie al meno.

    Restituisce:
        Lista di tuple ordinate: [ ('username', vittorie), ... ]
        Esempio: [ ('Mario', 5), ('Luigi', 3), ('Peach', 1) ]
    """
    classifica = carica_classifica()
    # sorted() con reverse=True mette prima chi ha più vittorie
    return sorted(classifica.items(), key=lambda x: x[1], reverse=True)


# ==============================================================================
# SCHERMATA CLASSIFICA
# ==============================================================================

def classifica_disegna(schermo, fonts, pos_mouse, utente_loggato):
    """
    Disegna il pannello della classifica sopra la schermata vincitore.
    Viene chiamata solo quando si vince in modalità DIFFICILE.

    La classifica mostra i primi 10 giocatori con:
    - posizione numerica (1., 2., 3. ...)
    - nome utente (in azzurro se sei tu, oro/argento/bronzo per il podio)
    - numero di vittorie totali

    Parametri:
        schermo: superficie pygame su cui disegnare
        fonts: dizionario dei font del gioco
        pos_mouse: posizione attuale del mouse (per effetto hover sul bottone)
        utente_loggato: username del giocatore attuale (per evidenziarlo)

    Restituisce:
        Il rettangolo del bottone CONTINUA (usato in funzione_principale per
        rilevare il click e tornare al menu)
    """
    LARGHEZZA = 1400
    ALTEZZA = 800

    # overlay scuro semi-trasparente sopra la schermata vincitore
    overlay = pygame.Surface((LARGHEZZA, ALTEZZA))
    overlay.set_alpha(230)
    overlay.fill((15, 15, 20))
    schermo.blit(overlay, (0, 0))

    # dimensioni e posizione del pannello centrale
    larg, alt = 600, 500
    px = (LARGHEZZA - larg) // 2   # centrato orizzontalmente
    py = (ALTEZZA - alt) // 2      # centrato verticalmente

    # ombra del pannello (rettangolo scuro spostato di 6px)
    pygame.draw.rect(schermo, (10, 10, 15), pygame.Rect(px+6, py+6, larg, alt), border_radius=18)
    # pannello principale
    pygame.draw.rect(schermo, (40, 40, 55), pygame.Rect(px, py, larg, alt), border_radius=18)
    # bordo del pannello
    pygame.draw.rect(schermo, (100, 100, 130), pygame.Rect(px, py, larg, alt), 2, border_radius=18)

    # titolo del pannello
    surf_titolo = fonts['grande'].render("🏆  CLASSIFICA  🏆", True, (255, 215, 0))
    schermo.blit(surf_titolo, surf_titolo.get_rect(center=(px + larg//2, py + 40)))

    # linea separatrice sotto il titolo
    pygame.draw.line(schermo, (100, 100, 130), (px+20, py+70), (px+larg-20, py+70), 1)

    # sottotitolo che spiega di cosa è la classifica
    surf_sub = fonts['piccolo'].render("Modalità DIFFICILE — vittorie totali", True, (150, 150, 180))
    schermo.blit(surf_sub, surf_sub.get_rect(center=(px + larg//2, py + 90)))

    # carica e disegna le righe della classifica
    classifica = ottieni_classifica_ordinata()
    y_riga = py + 125   # punto di partenza verticale per la prima riga

    # colori speciali per i primi 3 posti (oro, argento, bronzo)
    colori_podio = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]

    if not classifica:
        # nessuno ha ancora vinto in difficile
        surf = fonts['medio'].render("Nessuna vittoria ancora!", True, (150, 150, 150))
        schermo.blit(surf, surf.get_rect(center=(px + larg//2, py + alt//2)))
    else:
        # mostra al massimo i primi 10 giocatori
        for i, (nome, vittorie) in enumerate(classifica[:10]):

            # sceglie il colore del testo per questa riga:
            # - azzurro se è l'utente attualmente loggato
            # - oro/argento/bronzo per i primi 3 posti
            # - bianco per tutti gli altri
            if nome == utente_loggato:
                colore_nome = (100, 220, 255)
            elif i < 3:
                colore_nome = colori_podio[i]
            else:
                colore_nome = (220, 220, 220)

            # sfondo alternato sulle righe pari per leggibilità
            if i % 2 == 0:
                pygame.draw.rect(schermo, (50, 50, 65),
                                 pygame.Rect(px+20, y_riga - 5, larg-40, 32), border_radius=6)

            # numero di posizione (es. "1.")
            surf_pos = fonts['medio'].render(f"{i+1}.", True, colore_nome)
            schermo.blit(surf_pos, (px + 40, y_riga))

            # nome utente
            surf_nome = fonts['medio'].render(nome, True, colore_nome)
            schermo.blit(surf_nome, (px + 90, y_riga))

            # numero vittorie allineato a destra
            # usa "vittoria" al singolare se è 1, "vittorie" al plurale altrimenti
            testo_vit = f"{vittorie} {'vittoria' if vittorie == 1 else 'vittorie'}"
            surf_vit = fonts['medio'].render(testo_vit, True, colore_nome)
            schermo.blit(surf_vit, (px + larg - surf_vit.get_width() - 40, y_riga))

            y_riga += 36   # sposta verso il basso per la riga successiva

    # bottone CONTINUA in fondo al pannello
    rett_btn = pygame.Rect(px + larg//2 - 150, py + alt - 65, 300, 48)
    is_hover = rett_btn.collidepoint(pos_mouse)
    colore_btn = (100, 220, 100) if is_hover else (80, 180, 80)
    pygame.draw.rect(schermo, colore_btn, rett_btn, border_radius=10)
    pygame.draw.rect(schermo, (150, 255, 150), rett_btn, 2, border_radius=10)
    surf_btn = fonts['medio'].render("CONTINUA", True, (255, 255, 255))
    schermo.blit(surf_btn, surf_btn.get_rect(center=rett_btn.center))

    # restituisce il rettangolo del bottone per rilevare il click in funzione_principale
    return rett_btn