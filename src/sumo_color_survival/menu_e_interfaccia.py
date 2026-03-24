import math
import random

import pygame

from classifica import ottieni_classifica_ordinata
from costanti_e_variabili import *
from lottatori import *


def disegna_pannello(schermo, rett, titolo, font):
    """
    Disegna un pannello bianco moderno con ombra e titolo.
    Usato nel menu principale.
    """
    # Rettangolo nero
    rett_ombra = rett.copy()
    rett_ombra.x += 5
    rett_ombra.y += 5
    pygame.draw.rect(schermo, (10, 10, 15), rett_ombra, border_radius=15)

    # Pannello bianco
    pygame.draw.rect(schermo, (240, 240, 245), rett, border_radius=15)
    pygame.draw.rect(schermo, (200, 200, 210), rett, 3, border_radius=15)

    # Parte superiore colorata
    rett_header = pygame.Rect(rett.x, rett.y, rett.width, 50)
    pygame.draw.rect(
        schermo,
        (220, 220, 230),
        rett_header,
        border_top_left_radius=15,
        border_top_right_radius=15,
    )

    # Titolo centrato
    testo_titolo = font.render(titolo, True, (50, 50, 50))
    rett_titolo = testo_titolo.get_rect(center=(rett.centerx, rett.y + 25))
    schermo.blit(testo_titolo, rett_titolo)


def disegna_menu(schermo, fonts, pos_mouse, difficolta):
    """
    Disegna il menu principale con 4 pannelli:
    1. Difficoltà
    2. Controlli
    3. Pulsante Inizia
    4. Classifica Vittorie (modalità difficile)

    Restituisce: (bottoni_difficolta, bottone_inizio)
    """

    # Titolo grande in alto
    LARGHEZZA = 1400
    titolo = fonts["titolo"].render("SUMO COLOR SURVIVAL", True, (255, 255, 255))
    rett_titolo = titolo.get_rect(center=(LARGHEZZA // 2, 120))
    schermo.blit(titolo, rett_titolo)

    ALTEZZA = 800

    # Dimensioni e posizioni dei 4 pannelli
    # 4 * 310 + 3 * 26 = 1240 + 78 = 1318px → centrati in 1400px
    larghezza_pannello = 310
    altezza_pannello = 300
    spaziatura_pannello = 26

    # Calcola le posizioni per centrare i 4 pannelli
    larghezza_totale = larghezza_pannello * 4 + spaziatura_pannello * 3
    inizio_x = (LARGHEZZA - larghezza_totale) // 2
    centro_y = ALTEZZA // 2 + 20  # leggermente abbassato per il titolo più grande

    # Crea i 4 rettangoli per i pannelli
    passo = larghezza_pannello + spaziatura_pannello
    rett_pannelli = {
        "difficolta": pygame.Rect(
            inizio_x,
            centro_y - altezza_pannello // 2,
            larghezza_pannello,
            altezza_pannello,
        ),
        "controlli": pygame.Rect(
            inizio_x + passo,
            centro_y - altezza_pannello // 2,
            larghezza_pannello,
            altezza_pannello,
        ),
        "inizio": pygame.Rect(
            inizio_x + passo * 2,
            centro_y - altezza_pannello // 2,
            larghezza_pannello,
            altezza_pannello,
        ),
        "classifica": pygame.Rect(
            inizio_x + passo * 3,
            centro_y - altezza_pannello // 2,
            larghezza_pannello,
            altezza_pannello,
        ),
    }

    # PANNELLO 1: DIFFICOLTÀ
    pannello = rett_pannelli["difficolta"]
    disegna_pannello(schermo, pannello, "DIFFICOLTÀ", fonts["medio"])

    dati_diff = [
        ("FACILE", "FACILE", (100, 255, 100)),
        ("MEDIO", "MEDIO", (255, 200, 100)),
        ("DIFFICILE", "DIFFICILE", (255, 100, 100)),
    ]

    bottoni_difficolta = {}
    largh_btn_diff = pannello.width - 40  # bottoni adattati alla larghezza del pannello
    y_bottone = pannello.y + 80

    # Disegna i 3 bottoni
    for i, (valore_diff, testo_diff, colore_diff) in enumerate(dati_diff):
        bottone = pygame.Rect(
            pannello.centerx - largh_btn_diff // 2,
            y_bottone + i * 65,
            largh_btn_diff,
            52,
        )
        bottoni_difficolta[valore_diff] = bottone

        # Controlla se selezionato o sei sopra
        è_selezionato = difficolta == valore_diff
        è_hover = bottone.collidepoint(pos_mouse)

        # Disegna il bottone con il colore appropriato
        if è_selezionato:
            pygame.draw.rect(schermo, colore_diff, bottone, border_radius=10)
            colore_testo = (0, 0, 0)
        elif è_hover:
            pygame.draw.rect(schermo, (200, 200, 200), bottone, border_radius=10)
            pygame.draw.rect(schermo, colore_diff, bottone, 3, border_radius=10)
            colore_testo = (0, 0, 0)
        else:
            pygame.draw.rect(schermo, (180, 180, 180), bottone, border_radius=10)
            colore_testo = (0, 0, 0)

        # Testo del bottone
        testo_btn = fonts["medio"].render(testo_diff, True, colore_testo)
        rett_testo_btn = testo_btn.get_rect(center=bottone.center)
        schermo.blit(testo_btn, rett_testo_btn)

    # PANNELLO 2: CONTROLLI
    pannello = rett_pannelli["controlli"]
    disegna_pannello(schermo, pannello, "CONTROLLI", fonts["medio"])

    # Tasti
    controlli = [
        "WASD - Movimento",
        "",
        "Click Sinistro",
        "Attacco Pancia",
        "",
        "Obiettivo:",
        "SOPRAVVIVERE",
    ]

    # Scrivi i testi
    offset_y = pannello.y + 70
    for testo in controlli:
        if testo:
            surf = fonts["piccolo"].render(testo, True, (50, 50, 50))
            rett = surf.get_rect(center=(pannello.centerx, offset_y))
            schermo.blit(surf, rett)
        offset_y += 30

    # PANNELLO 3: INIZIA
    pannello = rett_pannelli["inizio"]
    disegna_pannello(schermo, pannello, "GIOCA", fonts["medio"])

    largh_btn_inizio = pannello.width - 40
    # Bottone INIZIA
    bottone_inizio = pygame.Rect(
        pannello.centerx - largh_btn_inizio // 2,
        pannello.centery - 35,
        largh_btn_inizio,
        70,
    )
    è_hover_inizio = bottone_inizio.collidepoint(pos_mouse)

    # Cambia colore
    if è_hover_inizio:
        pygame.draw.rect(schermo, (100, 220, 100), bottone_inizio, border_radius=15)
    else:
        pygame.draw.rect(schermo, (80, 180, 80), bottone_inizio, border_radius=15)

    pygame.draw.rect(schermo, (150, 255, 150), bottone_inizio, 4, border_radius=15)

    # Testo
    testo_inizio = fonts["grande"].render("INIZIA", True, (255, 255, 255))
    rett_testo_inizio = testo_inizio.get_rect(center=bottone_inizio.center)
    schermo.blit(testo_inizio, rett_testo_inizio)

    # PANNELLO 4: CLASSIFICA VITTORIE
    pannello = rett_pannelli["classifica"]
    disegna_pannello(schermo, pannello, "CLASSIFICA VITTORIE", fonts["piccolo"])

    # Sottotitolo "modalità difficile"
    surf_sub = fonts["minuscolo"].render("modalità difficile", True, (100, 100, 120))
    schermo.blit(
        surf_sub, surf_sub.get_rect(center=(pannello.centerx, pannello.y + 62))
    )

    # Linea separatrice sotto il sottotitolo
    pygame.draw.line(
        schermo,
        (200, 200, 210),
        (pannello.x + 15, pannello.y + 76),
        (pannello.x + pannello.width - 15, pannello.y + 76),
        1,
    )

    # Carica e mostra i primi 5 giocatori
    classifica = ottieni_classifica_ordinata()
    colori_podio = [
        (255, 215, 0),
        (192, 192, 192),
        (205, 127, 50),
    ]  # oro, argento, bronzo

    if not classifica:
        surf_vuota = fonts["piccolo"].render(
            "Nessuna vittoria ancora!", True, (160, 160, 160)
        )
        schermo.blit(
            surf_vuota,
            surf_vuota.get_rect(center=(pannello.centerx, pannello.centery + 20)),
        )
    else:
        y_riga = pannello.y + 92
        for i, (nome, vittorie) in enumerate(classifica[:5]):
            # colore della riga: oro/argento/bronzo per il podio, grigio scuro per il resto
            if i < 3:
                colore_riga = colori_podio[i]
            else:
                colore_riga = (80, 80, 90)

            # sfondo alternato per leggibilità
            if i % 2 == 0:
                pygame.draw.rect(
                    schermo,
                    (210, 210, 220),
                    pygame.Rect(pannello.x + 12, y_riga - 3, pannello.width - 24, 32),
                    border_radius=6,
                )

            # numero posizione
            surf_pos = fonts["piccolo"].render(f"{i + 1}.", True, colore_riga)
            schermo.blit(surf_pos, (pannello.x + 20, y_riga))

            # nome utente (troncato se troppo lungo)
            nome_display = nome if len(nome) <= 12 else nome[:11] + "…"
            surf_nome = fonts["piccolo"].render(nome_display, True, colore_riga)
            schermo.blit(surf_nome, (pannello.x + 46, y_riga))

            # numero vittorie tra parentesi, allineato a destra
            testo_vit = f"({vittorie})"
            surf_vit = fonts["piccolo"].render(testo_vit, True, colore_riga)
            schermo.blit(
                surf_vit,
                (pannello.x + pannello.width - surf_vit.get_width() - 18, y_riga),
            )

            y_riga += 36

    # Testo in fondo al pannello
    info = fonts["piccolo"].render("8 Giocatori - Sopravvivi!", True, (150, 150, 150))
    rett_info = info.get_rect(center=(LARGHEZZA // 2, ALTEZZA - 40))
    schermo.blit(info, rett_info)

    return bottoni_difficolta, bottone_inizio


def disegna_hud_gioco(
    schermo, fonts, num_round, diff, col_target, stato, conta, lista_lottatori
):
    """
    Disegna l'HUD (interfaccia utente) durante il gioco.
    Include: round, difficoltà, colore target, countdown, giocatori vivi, pannello attacco.
    """

    pygame.draw.rect(schermo, (0, 0, 0, 100), (0, 0, LARGHEZZA, 80))

    # Round e Difficoltà
    testo_round = fonts["medio"].render(f"ROUND {num_round}", True, (255, 255, 255))
    schermo.blit(testo_round, (20, 15))

    nomi_diff = {"FACILE": "FACILE", "MEDIO": "MEDIO", "DIFFICILE": "DIFFICILE"}
    colori_diff = {
        "FACILE": (100, 255, 100),
        "MEDIO": (255, 200, 100),
        "DIFFICILE": (255, 100, 100),
    }
    testo_diff = fonts["piccolo"].render(nomi_diff[diff], True, colori_diff[diff])
    schermo.blit(testo_diff, (20, 55))

    # Colore e Countdown
    if stato == "GIOCANDO":
        testo_target = fonts["grande"].render(f"{col_target}", True, COLORI[col_target])
        rett_target = testo_target.get_rect(center=(LARGHEZZA // 2, 35))

        rett_box = rett_target.inflate(40, 20)
        pygame.draw.rect(schermo, COLORI[col_target], rett_box, 5, border_radius=10)

        schermo.blit(testo_target, rett_target)

        if conta > 0:
            testo_conta = fonts["grande"].render(
                f"{int(conta) + 1}", True, (255, 200, 0)
            )
            rett_conta = testo_conta.get_rect(center=(LARGHEZZA // 2, 75))
            schermo.blit(testo_conta, rett_conta)

    # Giocatori Vivi
    conteggio_vivi = sum(1 for l in lista_lottatori if l["vivo"])
    testo_vivi = fonts["medio"].render(f"Vivi: {conteggio_vivi}/8", True, (0, 255, 0))
    schermo.blit(testo_vivi, (LARGHEZZA - 150, 15))

    # PANNELLO ATTACCO
    # Trova il giocatore umano

    giocatore = None
    for l in lista_lottatori:
        if not l["è_bot"]:
            giocatore = l
            break

    # Se il giocatore è vivo, mostra il pannello
    if giocatore and giocatore["vivo"]:
        x_pannello = LARGHEZZA - 300
        y_pannello = 120
        largh_pannello = 280
        alt_pannello = 140

        # Disegno e testo del pannello
        rett_pannello = pygame.Rect(
            x_pannello, y_pannello, largh_pannello, alt_pannello
        )
        pygame.draw.rect(schermo, (40, 40, 50), rett_pannello, border_radius=10)
        pygame.draw.rect(schermo, (100, 100, 120), rett_pannello, 3, border_radius=10)

        titolo = fonts["piccolo"].render("PANZATA", True, (255, 215, 0))
        rett_titolo = titolo.get_rect(
            center=(x_pannello + largh_pannello // 2, y_pannello + 25)
        )
        schermo.blit(titolo, rett_titolo)

        desc1 = fonts["piccolo"].render(
            "Click Sinistro per colpire", True, (200, 200, 200)
        )
        rett_desc1 = desc1.get_rect(
            center=(x_pannello + largh_pannello // 2, y_pannello + 55)
        )
        schermo.blit(desc1, rett_desc1)

        # BARRA RICARICA
        largh_barra = 240
        alt_barra = 25
        x_barra = x_pannello + (largh_pannello - largh_barra) // 2
        y_barra = y_pannello + 100

        pygame.draw.rect(
            schermo,
            (60, 60, 70),
            (x_barra, y_barra, largh_barra, alt_barra),
            border_radius=5,
        )

        if giocatore["cooldown_attacco"] > 0:
            # La barra sta ricaricando
            progresso = 1 - (giocatore["cooldown_attacco"] / 60)
            largh_riempimento = int(largh_barra * progresso)
            pygame.draw.rect(
                schermo,
                (255, 200, 0),
                (x_barra, y_barra, largh_riempimento, alt_barra),
                border_radius=5,
            )

            # Percentuale della ricarica
            testo_percentuale = fonts["piccolo"].render(
                f"{int(progresso * 100)}%", True, (255, 255, 255)
            )
            rett_percentuale = testo_percentuale.get_rect(
                center=(x_barra + largh_barra // 2, y_barra + alt_barra // 2)
            )
            schermo.blit(testo_percentuale, rett_percentuale)

        else:
            # Attacco pronto
            pygame.draw.rect(
                schermo,
                (100, 255, 100),
                (x_barra, y_barra, largh_barra, alt_barra),
                border_radius=5,
            )
            testo_pronto = fonts["piccolo"].render("PRONTO!", True, (0, 100, 0))
            rett_pronto = testo_pronto.get_rect(
                center=(x_barra + largh_barra // 2, y_barra + alt_barra // 2)
            )
            schermo.blit(testo_pronto, rett_pronto)

        pygame.draw.rect(
            schermo,
            (150, 150, 160),
            (x_barra, y_barra, largh_barra, alt_barra),
            2,
            border_radius=5,
        )


def disegna_bottone_riavvio(schermo, fonts, pos_mouse):
    """
    Disegna il bottone "Nuova Partita" durante il gioco.
    Posizionato in basso a sinistra.

    Restituisce: il rett del bottone
    """
    bottone_riavvio = pygame.Rect(40, ALTEZZA // 2 - 50, 200, 80)
    è_hover = bottone_riavvio.collidepoint(pos_mouse)

    if è_hover:
        colore_bottone = (180, 40, 40)
        colore_bordo = (255, 120, 120)
    else:
        colore_bottone = (120, 30, 30)
        colore_bordo = (200, 80, 80)

    # Disegna bottone
    pygame.draw.rect(schermo, colore_bottone, bottone_riavvio, border_radius=15)
    pygame.draw.rect(schermo, colore_bordo, bottone_riavvio, 4, border_radius=15)

    testo_icona = fonts["grande"].render(" ", True, (255, 255, 255))
    rett_icona = testo_icona.get_rect(
        center=(bottone_riavvio.centerx, bottone_riavvio.centery - 15)
    )
    schermo.blit(testo_icona, rett_icona)

    testo_bottone = fonts["piccolo"].render("Nuova Partita", True, (255, 255, 200))
    rett_testo_bottone = testo_bottone.get_rect(
        center=(bottone_riavvio.centerx, bottone_riavvio.centery)
    )
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

    # Testo vincitore
    if lottatore_vincitore:
        testo_vincitore = fonts["titolo"].render(
            f" {lottatore_vincitore['nome']} HA VINTO! ", True, (255, 215, 0)
        )

        lottatore_vincitore["x"] = LARGHEZZA // 2
        lottatore_vincitore["y"] = ALTEZZA // 2 + 150
        lottatore_disegna(schermo, lottatore_vincitore)
    else:
        # Pareggio
        testo_vincitore = fonts["titolo"].render("PAREGGIO!", True, (255, 255, 255))

    rett_vincitore = testo_vincitore.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 3))
    schermo.blit(testo_vincitore, rett_vincitore)

    # Statistiche
    testo_rounds = fonts["medio"].render(
        f"Round giocati: {num_round}", True, (255, 255, 255)
    )
    rett_rounds = testo_rounds.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 - 20))
    schermo.blit(testo_rounds, rett_rounds)

    nome_diff = {"FACILE": "Facile", "MEDIO": "Medio", "DIFFICILE": "Difficile"}
    testo_diff = fonts["medio"].render(
        f"Difficoltà: {nome_diff[diff]}", True, (200, 200, 200)
    )
    rett_diff = testo_diff.get_rect(center=(LARGHEZZA // 2, ALTEZZA // 2 + 20))
    schermo.blit(testo_diff, rett_diff)

    # Istruzioni per riavviare
    testo_riavvio = fonts["piccolo"].render(
        "Premi SPAZIO per giocare ancora", True, (200, 200, 200)
    )
    rett_riavvio = testo_riavvio.get_rect(center=(LARGHEZZA // 2, ALTEZZA - 100))
    schermo.blit(testo_riavvio, rett_riavvio)
