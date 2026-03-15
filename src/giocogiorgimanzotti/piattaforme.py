import math
import random

import pygame

from giocogiorgimanzotti.costanti_e_variabili import *


def crea_piattaforma(x, y, larghezza, altezza, nome_colore):
    """
    Crea una singola piattaforma.
    Restituisce:
        Un dizionario con tutte le informazioni della piattaforma
    """

    piattaforma = {
        "x": x,  # Posizione orizzontale
        "y": y,  # Posizione verticale
        "larghezza": larghezza,  # Larghezza in pixel
        "altezza": altezza,  # Altezza in pixel
        "nome_colore": nome_colore,  # Nome del colore
        "colore": COLORI[nome_colore],  # Colore RGB
        "attiva": True,  # Se True, la piattaforma è visibile
        "progresso_scomparsa": 0,  # Da 0 (visibile) a 1 (scomparsa)
    }

    return piattaforma


def piattaforma_inizia_scomparsa(piattaforma):
    """
    Fa iniziare l'animazione di scomparsa di una piattaforma.
    La piattaforma diventerà gradualmente più piccola fino a sparire.

    Parametri:
        piattaforma: il dizionario della piattaforma da far scomparire
    """
    piattaforma["attiva"] = False  # fa scomparire la piattaforma


def piattaforma_aggiorna(piattaforma):
    """
    Aggiorna lo stato della piattaforma (animazione di scomparsa).
    Questa funzione viene chiamata 60 volte al secondo (per ogni frame).

    Parametri:
        piattaforma: il dizionario della piattaforma da aggiornare
    """

    if not piattaforma["attiva"] and piattaforma["progresso_scomparsa"] < 1:
        # velocita di scomparsa
        piattaforma["progresso_scomparsa"] += 0.07


def piattaforma_disegna(schermo, piattaforma):
    """
    Disegna una piattaforma sullo schermo.

    Parametri:
        schermo: la superficie pygame su cui disegnare
        piattaforma: il dizionario della piattaforma da disegnare
    """

    if piattaforma["progresso_scomparsa"] >= 1:
        return

    # fa ridurre sempre di piu la piattaforma mentre scompare
    if not piattaforma["attiva"]:
        # rimpicciolisce e fa implodere
        scala = 1 - piattaforma["progresso_scomparsa"]
        offset = piattaforma["progresso_scomparsa"] * 20

        rett = pygame.Rect(
            piattaforma["x"] + offset,
            piattaforma["y"] + offset,
            piattaforma["larghezza"] * scala,
            piattaforma["altezza"] * scala,
        )
    else:
        # piattaforma in stato base
        rett = pygame.Rect(
            piattaforma["x"],
            piattaforma["y"],
            piattaforma["larghezza"],
            piattaforma["altezza"],
        )

    # disegna la piattaforma
    pygame.draw.rect(schermo, piattaforma["colore"], rett)

    pygame.draw.rect(schermo, (0, 0, 0), rett, 4)


def piattaforma_contiene_punto(piattaforma, x, y, margine=15):
    """
    Controlla se un punto (x, y) è dentro o vicino alla piattaforma.
    Il margine permette di camminare tra piattaforme adiacenti senza cadere!
    Restituisce:
        True se il punto è dentro/vicino, False altrimenti
    """

    if not piattaforma["attiva"] or piattaforma["progresso_scomparsa"] >= 1:
        return False
    # controlla se cè qualchuno dentro la piattaforma
    dentro_x = (
        piattaforma["x"] - margine
        <= x
        <= piattaforma["x"] + piattaforma["larghezza"] + margine
    )
    dentro_y = (
        piattaforma["y"] - margine
        <= y
        <= piattaforma["y"] + piattaforma["altezza"] + margine
    )

    return dentro_x and dentro_y


def piattaforma_ottieni_centro(piattaforma):
    """
    Calcola e restituisce il centro della piattaforma.
    Utile per far muovere i bot verso il centro delle piattaforme.
    Restituisce:
        Una tupla (centro_x, centro_y) con le coordinate del centro
    """
    centro_x = piattaforma["x"] + piattaforma["larghezza"] // 2
    centro_y = piattaforma["y"] + piattaforma["altezza"] // 2
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

    # centra nello schermo la griglia
    larghezza_griglia = colonne * larghezza_piattaforma + (colonne - 1) * spaziatura
    altezza_griglia = righe * altezza_piattaforma + (righe - 1) * spaziatura
    offset_x = (LARGHEZZA - larghezza_griglia) // 2
    offset_y = (ALTEZZA - altezza_griglia) // 2 + 30

    # crea le 5 piattaforme per colore
    lista_colori = []
    for nome_colore in NOMI_COLORI:
        lista_colori.extend([nome_colore] * 5)
    # mescola i colori
    random.shuffle(lista_colori)

    idx = 0  # scorre lista_colori
    for riga in range(righe):
        for col in range(colonne):
            # la posizione della piattaforma
            x = offset_x + col * (larghezza_piattaforma + spaziatura)
            y = offset_y + riga * (altezza_piattaforma + spaziatura)

            nome_colore = lista_colori[idx]
            # crea la piattaforma assegnandole le caratteristiche (colore, posizione ecc)
            piattaforma = crea_piattaforma(
                x, y, larghezza_piattaforma, altezza_piattaforma, nome_colore
            )
            lista_piattaforme.append(piattaforma)

            idx += 1

    return lista_piattaforme
