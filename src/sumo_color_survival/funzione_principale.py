# funzione_principale.py - the function that starts the game.

# Descrizione più lunga opzionale su più righe,
# che spiega cosa fa il modulo.

# Authors: 
# Paolo Giorgi: paologiorgi04@gmail.com
# Leonardo Manzotti: leomanzotti04@gmail.com


import math
import random

import pygame

from classifica import *
from costanti_e_variabili import *
from login import *
from lottatori import *
from menu_e_interfaccia import *
from piattaforme import *


def main():
    pygame.init()
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
    orologio = pygame.time.Clock()  # Per controllare gli FPS

    # Crea i font delle scritte
    fonts = {
        "titolo": pygame.font.Font(None, 70),
        "grande": pygame.font.Font(None, 50),
        "medio": pygame.font.Font(None, 36),
        "piccolo": pygame.font.Font(None, 28),
        "minuscolo": pygame.font.Font(None, 22),
    }

    bottoni_difficolta = {}
    bottone_inizio = None
    bottone_riavvio = None

    # Dizionario con tutto lo stato della schermata di login (campi, modalità, messaggi)
    stato_login = crea_stato_login()
    # Username salvato dopo il login riuscito, usato per la classifica
    utente_loggato = None

    # Flag: True quando bisogna mostrare la classifica sopra la schermata vincitore
    mostra_classifica = False
    # Rettangolo del bottone CONTINUA della classifica (serve per rilevare il click)
    bottone_classifica_continua = None

    # Il gioco parte dalla schermata di LOGIN (non dal menu)
    stato_gioco = "LOGIN"

    # LOOP PRINCIPALE
    # Questo loop si ripete 60 volte al secondo
    in_esecuzione = True
    while in_esecuzione:
        # La posizione del mouse
        pos_mouse = pygame.mouse.get_pos()

        # EVENTI
        for evento in pygame.event.get():
            # Chiusura finestra
            if evento.type == pygame.QUIT:
                in_esecuzione = False

            # Tasto premuto
            elif evento.type == pygame.KEYDOWN:
                # "SPAZIO" nella schermata vincitore = torna al menu
                # (solo se la classifica non è aperta, altrimenti si usa il bottone CONTINUA)
                if (
                    evento.key == pygame.K_SPACE
                    and stato_gioco == "VINCITORE"
                    and not mostra_classifica
                ):
                    stato_gioco = "MENU"

            # Gestione eventi della schermata login (campi di testo, bottoni, link)
            # Va fuori dall'elif perché login_gestisci_eventi gestisce internamente
            # sia MOUSEBUTTONDOWN che KEYDOWN
            if stato_gioco == "LOGIN":
                risultato = login_gestisci_eventi(stato_login, evento)
                if risultato:
                    # Login riuscito: salva l'username e vai al menu
                    utente_loggato = risultato
                    stato_gioco = "MENU"

            # Click del mouse
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # CLICK NEL MENU
                if stato_gioco == "MENU":
                    # Controlla click sui bottoni delle difficoltà
                    for valore_diff, rett_bottone in bottoni_difficolta.items():
                        if rett_bottone.collidepoint(pos_mouse):
                            difficolta = valore_diff
                    # Controlla click sul bottone "INIZIA"
                    if bottone_inizio and bottone_inizio.collidepoint(pos_mouse):
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
                            piattaforma["attiva"] = True
                            piattaforma["progresso_scomparsa"] = 0

                        # Reset AI dei bot
                        for lottatore in lottatori:
                            if lottatore["è_bot"]:
                                lottatore["timer_ai"] = 0
                                lottatore["piattaforma_target"] = None

                # CLICK DURANTE IL GIOCO
                elif stato_gioco in ["GIOCANDO", "ATTESA"]:
                    if bottone_riavvio and bottone_riavvio.collidepoint(pos_mouse):
                        stato_gioco = "MENU"

                # CLICK SULLA CLASSIFICA (bottone CONTINUA)
                elif stato_gioco == "VINCITORE" and mostra_classifica:
                    if (
                        bottone_classifica_continua
                        and bottone_classifica_continua.collidepoint(pos_mouse)
                    ):
                        mostra_classifica = False
                        stato_gioco = "MENU"

        # ==============================================================
        # AGGIORNA LO STATO DEL GIOCO
        # ==============================================================

        # Aggiorna il cursore lampeggiante nei campi di testo del login
        if stato_gioco == "LOGIN":
            login_aggiorna(stato_login)

        if stato_gioco == "GIOCANDO":
            # Diminuisce il countdown (1/60 = un frame)
            conto_alla_rovescia -= 1 / 60

            # Ottieni input da tastiera e mouse
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()

            # Aggiorna tutti i lottatori vivi
            for lottatore in lottatori:
                if lottatore["vivo"]:
                    lottatore_aggiorna(
                        lottatore,
                        tasti,
                        pulsanti_mouse,
                        piattaforme,
                        colore_target,
                        lottatori,
                    )

            if conto_alla_rovescia <= 0:
                # Fa scomparire tutte le piattaforme del colore SBAGLIATO
                for piattaforma in piattaforme:
                    if piattaforma["nome_colore"] != colore_target:
                        piattaforma_inizia_scomparsa(piattaforma)

                piattaforme_scomparse = True

                # Controlla chi è su piattaforme sbagliate e falli morire
                for lottatore in lottatori:
                    if lottatore["vivo"]:
                        su_corretta = False

                        # Cerca se è su almeno una piattaforma del colore giusto
                        for piattaforma in piattaforme:
                            if (
                                piattaforma["nome_colore"] == colore_target
                                and piattaforma["attiva"]
                                and piattaforma_contiene_punto(
                                    piattaforma, lottatore["x"], lottatore["y"]
                                )
                            ):
                                su_corretta = True
                                break
                        # Se non è su una piattaforma corretta muore
                        if not su_corretta:
                            lottatore["vivo"] = False

                # Passa alla fase di attesa
                stato_gioco = "ATTESA"
                conto_alla_rovescia = 2.0  # Attendi 2 secondi prima del prossimo round

            # Aggiorna animazione piattaforme
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)

        elif stato_gioco == "ATTESA":
            conto_alla_rovescia -= 1 / 60

            # Continua ad aggiornare i lottatori (anche quelli che cadono)
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()

            for lottatore in lottatori:
                lottatore_aggiorna(
                    lottatore,
                    tasti,
                    pulsanti_mouse,
                    piattaforme,
                    colore_target,
                    lottatori,
                )

            # Chi esce dalle piattaforme giuste, muore!
            if piattaforme_scomparse:
                for lottatore in lottatori:
                    if lottatore["vivo"]:
                        if not lottatore_controlla_su_piattaforma(
                            lottatore, piattaforme, colore_target
                        ):
                            lottatore["vivo"] = False

            # Aggiorna piattaforme
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)

            if conto_alla_rovescia <= 0:
                # Conta i sopravvissuti
                lottatori_vivi = [l for l in lottatori if l["vivo"]]

                if len(lottatori_vivi) == 1:
                    # se rimane un solo sopravvissuto vince
                    vincitore = lottatori_vivi[0]
                    stato_gioco = "VINCITORE"

                    # Se il giocatore umano vince in DIFFICILE: salva la vittoria
                    # nella classifica e mostra il pannello classifica
                    if (
                        difficolta == "DIFFICILE"
                        and not vincitore["è_bot"]
                        and utente_loggato
                    ):
                        aggiungi_vittoria(utente_loggato)
                        mostra_classifica = True
                    else:
                        mostra_classifica = False

                elif len(lottatori_vivi) == 0:
                    vincitore = None
                    stato_gioco = "VINCITORE"
                    mostra_classifica = False

                else:
                    # PIÙ SOPRAVVISSUTI = NUOVO ROUND
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
                        lottatore["spawn_x"] = (
                            centro_griglia_x + math.cos(angolo) * raggio_spawn
                        )
                        lottatore["spawn_y"] = (
                            centro_griglia_y + math.sin(angolo) * raggio_spawn
                        )
                        lottatore_resetta_posizione(lottatore)

                    # Inizia il nuovo round
                    stato_gioco = "GIOCANDO"
                    conto_alla_rovescia = 3.0
                    piattaforme_scomparse = False
                    colore_target = random.choice(NOMI_COLORI)

                    # Reset dei bot
                    for lottatore in lottatori:
                        if lottatore["è_bot"]:
                            lottatore["timer_ai"] = 0
                            lottatore["piattaforma_target"] = None

        # ==============================================================
        # DISEGNA TUTTO SULLO SCHERMO
        # ==============================================================

        schermo.fill((25, 25, 30))

        # Disegna la schermata di login
        if stato_gioco == "LOGIN":
            login_disegna(schermo, stato_login, fonts, pos_mouse)

        elif stato_gioco == "MENU":
            # Disegna il menu
            bottoni_difficolta, bottone_inizio = disegna_menu(
                schermo, fonts, pos_mouse, difficolta
            )

        elif stato_gioco in ["GIOCANDO", "ATTESA"]:
            # Disegna le piattaforme
            for piattaforma in piattaforme:
                piattaforma_disegna(schermo, piattaforma)

            # Disegna i lottatori
            for lottatore in lottatori:
                lottatore_disegna(schermo, lottatore)

            # Disegna l'interfaccia (hud)
            disegna_hud_gioco(
                schermo,
                fonts,
                numero_round,
                difficolta,
                colore_target,
                stato_gioco,
                conto_alla_rovescia,
                lottatori,
            )

            # Disegna il bottone del riavvio
            bottone_riavvio = disegna_bottone_riavvio(schermo, fonts, pos_mouse)

        elif stato_gioco == "VINCITORE":
            # Disegna la schermata del vincitore
            disegna_schermata_vincitore(
                schermo, fonts, vincitore, numero_round, difficolta
            )

            # Se il giocatore ha vinto in DIFFICILE, sovrapponi il pannello classifica
            # classifica_disegna restituisce il rettangolo del bottone CONTINUA
            if mostra_classifica:
                bottone_classifica_continua = classifica_disegna(
                    schermo, fonts, pos_mouse, utente_loggato
                )

        # Aggiorna lo schermo (rende visibili tutti i disegni)
        pygame.display.flip()

        # Limita il gioco a 60 FPS
        orologio.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
