import math
import random

import pygame

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
        "x": x,
        "y": y,
        "spawn_x": x,
        "spawn_y": y,
        # MOVIMENTO
        "velocita_x": 0,
        "velocita_y": 0,
        # ASPETTO
        "colore_corpo": colore_corpo,
        "nome": nome,
        "è_bot": è_bot,
        "vivo": True,
        # ATTACCO
        "attaccando": False,
        "cooldown_attacco": 0,
        "durata_attacco": 0,
        # AI (BOT)
        "difficolta": difficolta,
        "piattaforma_target": None,
        "target_x": None,  # punto x casuale dentro la piattaforma target
        "target_y": None,  # punto y casuale dentro la piattaforma target
        "timer_ai": 0,
        "tempo_reazione_ai": ottieni_tempo_reazione_ai(difficolta),
        "qualita_decisioni_ai": ottieni_qualita_decisioni_ai(difficolta),
        "probabilita_attacco_ai": ottieni_probabilita_attacco_ai(difficolta),
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
    else:  # DIFFICILE
        return random.randint(5, 15)


def ottieni_qualita_decisioni_ai(difficolta):
    """
    Calcola quanto bene un bot sceglie le piattaforme.
    Restituisce un numero da 0 (pessimo) a 1 (perfetto).
    """
    if difficolta == "FACILE":
        return 0.7
    elif difficolta == "MEDIO":
        return 0.85
    else:  # DIFFICILE
        return 0.92


def ottieni_probabilita_attacco_ai(difficolta):
    """
    Calcola quanto spesso un bot attacca (probabilità per frame).
    Più alto = bot più aggressivo.
    """
    if difficolta == "FACILE":
        return 0.015
    elif difficolta == "MEDIO":
        return 0.04
    else:  # DIFFICILE
        return 0.10


def lottatore_aggiorna(
    lottatore,
    tasti,
    pulsanti_mouse,
    lista_piattaforme,
    nome_colore_target,
    tutti_lottatori,
):
    """
    Aggiorna lo stato di un lottatore ogni frame.
    Gestisce movimento, attacco, fisica, ecc.
    """
    # se il lottatore è morto, cade verso il basso
    if not lottatore["vivo"]:
        lottatore["y"] += 5
        return

    # aggiorna i timer di attacco
    if lottatore["cooldown_attacco"] > 0:
        lottatore["cooldown_attacco"] -= 1

    if lottatore["durata_attacco"] > 0:
        lottatore["durata_attacco"] -= 1
        if lottatore["durata_attacco"] == 0:
            lottatore["attaccando"] = False

    # controlli: bot usa AI, umano usa tastiera e mouse
    if lottatore["è_bot"]:
        lottatore_aggiorna_ai(
            lottatore, lista_piattaforme, nome_colore_target, tutti_lottatori
        )
    else:
        if tasti and pulsanti_mouse:
            accelerazione = 0.6
            if tasti[pygame.K_a]:
                lottatore["velocita_x"] -= accelerazione
            if tasti[pygame.K_d]:
                lottatore["velocita_x"] += accelerazione
            if tasti[pygame.K_w]:
                lottatore["velocita_y"] -= accelerazione
            if tasti[pygame.K_s]:
                lottatore["velocita_y"] += accelerazione
            if pulsanti_mouse[0] and lottatore["cooldown_attacco"] == 0:
                lottatore_esegui_attacco(lottatore, tutti_lottatori)

    # limita la velocità massima
    velocita = math.sqrt(lottatore["velocita_x"] ** 2 + lottatore["velocita_y"] ** 2)
    velocita_massima = 6.5
    if velocita > velocita_massima:
        rapporto = velocita_massima / velocita
        lottatore["velocita_x"] *= rapporto
        lottatore["velocita_y"] *= rapporto

    # applica attrito per rallentare gradualmente
    lottatore["velocita_x"] *= 0.85
    lottatore["velocita_y"] *= 0.85

    # sposta il lottatore in base alla velocità
    lottatore["x"] += lottatore["velocita_x"]
    lottatore["y"] += lottatore["velocita_y"]

    # impedisce l'uscita dai bordi dello schermo
    lottatore["x"] = max(22, min(LARGHEZZA - 22, lottatore["x"]))
    lottatore["y"] = max(22, min(ALTEZZA - 22, lottatore["y"]))


def lottatore_esegui_attacco(lottatore, tutti_lottatori):
    """
    Esegue una panciata che spinge via i lottatori vicini.
    """
    lottatore["attaccando"] = True
    lottatore["durata_attacco"] = 20
    lottatore["cooldown_attacco"] = 60

    raggio_attacco = 80
    spinta_attacco = 800

    for altro in tutti_lottatori:
        if altro["vivo"] and altro != lottatore:
            dx = altro["x"] - lottatore["x"]
            dy = altro["y"] - lottatore["y"]
            distanza = math.sqrt(dx**2 + dy**2)
            if distanza < raggio_attacco and distanza > 0:
                spinta_x = (dx / distanza) * spinta_attacco
                spinta_y = (dy / distanza) * spinta_attacco
                altro["velocita_x"] += spinta_x
                altro["velocita_y"] += spinta_y


def _scegli_punto_random_in_piattaforma(piattaforma):
    """
    Sceglie un punto casuale all'interno della piattaforma, con un margine
    dai bordi per evitare che il bot vada troppo sul ciglio.

    Parametri:
        piattaforma: dizionario della piattaforma target

    Restituisce:
        Tupla (x, y) con le coordinate del punto casuale
    """
    margine = 20  # distanza minima dai bordi della piattaforma
    x = random.randint(
        int(piattaforma["x"] + margine),
        int(piattaforma["x"] + piattaforma["larghezza"] - margine),
    )
    y = random.randint(
        int(piattaforma["y"] + margine),
        int(piattaforma["y"] + piattaforma["altezza"] - margine),
    )
    return x, y


def lottatore_aggiorna_ai(
    lottatore, lista_piattaforme, nome_colore_target, tutti_lottatori
):
    """
    Intelligenza artificiale per i bot.
    Decide dove muoversi e quando attaccare.

    ALGORITMO:
    1. Ogni tot frame sceglie una piattaforma del colore giusto
    2. Sceglie un punto CASUALE dentro quella piattaforma (non sempre il centro)
       così il bot si muove in modo più naturale e non sta mai fermo
    3. Si muove verso quel punto
    4. Quando arriva vicino al punto, ne sceglie un altro nella stessa piattaforma
       per continuare a muoversi anche quando è già al sicuro
    5. Se qualcuno è vicino, lo attacca con una certa probabilità
    """
    if not lista_piattaforme or not nome_colore_target:
        return

    def calcola_distanza_da_lottatore(piattaforma):
        """
        Calcola la distanza tra il lottatore e il centro di una piattaforma.
        Usa il teorema di Pitagora: distanza = √(dx² + dy²)
        """
        centro_x, centro_y = piattaforma_ottieni_centro(piattaforma)
        return math.sqrt(
            (centro_x - lottatore["x"]) ** 2 + (centro_y - lottatore["y"]) ** 2
        )

    lottatore["timer_ai"] += 1

    # ogni tot frame (o se non ha un target) sceglie una nuova piattaforma
    if (
        lottatore["timer_ai"] > lottatore["tempo_reazione_ai"]
        or lottatore["piattaforma_target"] is None
    ):
        # trova tutte le piattaforme del colore giusto ancora attive
        piattaforme_valide = [
            p
            for p in lista_piattaforme
            if p["nome_colore"] == nome_colore_target and p["attiva"]
        ]

        if piattaforme_valide:
            # sceglie la piattaforma: ottimale (più vicina) o casuale in base alla qualità AI
            if random.random() < lottatore["qualita_decisioni_ai"]:
                lottatore["piattaforma_target"] = min(
                    piattaforme_valide, key=calcola_distanza_da_lottatore
                )
            else:
                lottatore["piattaforma_target"] = random.choice(piattaforme_valide)

            # sceglie un punto casuale dentro la piattaforma come destinazione
            # questo evita che il bot stia sempre immobile al centro
            lottatore["target_x"], lottatore["target_y"] = (
                _scegli_punto_random_in_piattaforma(lottatore["piattaforma_target"])
            )

            # reset del timer
            lottatore["timer_ai"] = 0
            lottatore["tempo_reazione_ai"] = ottieni_tempo_reazione_ai(
                lottatore["difficolta"]
            )

    # si muove verso il punto target dentro la piattaforma
    if lottatore["piattaforma_target"] and lottatore["piattaforma_target"]["attiva"]:
        # usa il punto casuale se disponibile, altrimenti usa il centro
        tx = (
            lottatore["target_x"]
            if lottatore["target_x"]
            else piattaforma_ottieni_centro(lottatore["piattaforma_target"])[0]
        )
        ty = (
            lottatore["target_y"]
            if lottatore["target_y"]
            else piattaforma_ottieni_centro(lottatore["piattaforma_target"])[1]
        )

        dx = tx - lottatore["x"]
        dy = ty - lottatore["y"]
        distanza = math.sqrt(dx**2 + dy**2)

        if distanza > 5:
            fattore_movimento = 0.75 if lottatore["difficolta"] == "FACILE" else 0.9
            lottatore["velocita_x"] += (dx / distanza) * 0.6 * fattore_movimento
            lottatore["velocita_y"] += (dy / distanza) * 0.6 * fattore_movimento
        else:
            # il bot ha raggiunto il punto target: ne sceglie uno nuovo
            # nella stessa piattaforma per continuare a muoversi
            if lottatore["piattaforma_target"]["attiva"]:
                lottatore["target_x"], lottatore["target_y"] = (
                    _scegli_punto_random_in_piattaforma(lottatore["piattaforma_target"])
                )

    # attacca se qualcuno è abbastanza vicino
    if lottatore["cooldown_attacco"] == 0 and tutti_lottatori:
        for altro in tutti_lottatori:
            if altro["vivo"] and altro != lottatore:
                dx = altro["x"] - lottatore["x"]
                dy = altro["y"] - lottatore["y"]
                distanza = math.sqrt(dx**2 + dy**2)
                if (
                    distanza < 60
                    and random.random() < lottatore["probabilita_attacco_ai"]
                ):
                    lottatore_esegui_attacco(lottatore, tutti_lottatori)
                    break


def lottatore_controlla_su_piattaforma(
    lottatore, lista_piattaforme, nome_colore_target=None
):
    """
    Controlla se il lottatore è su una piattaforma attiva.
    Se nome_colore_target è specificato, controlla solo piattaforme di quel colore.

    Restituisce:
        True se è sulla piattaforma giusta, False altrimenti
    """
    for piattaforma in lista_piattaforme:
        if piattaforma["attiva"] and piattaforma_contiene_punto(
            piattaforma, lottatore["x"], lottatore["y"]
        ):
            if (
                nome_colore_target is None
                or piattaforma["nome_colore"] == nome_colore_target
            ):
                return True
    return False


def lottatore_resetta_posizione(lottatore):
    """
    Riporta il lottatore allo spawn all'inizio di ogni nuovo round.
    Azzera velocità, stato attacco e lo rimette in vita.
    """
    lottatore["x"] = lottatore["spawn_x"]
    lottatore["y"] = lottatore["spawn_y"]
    lottatore["velocita_x"] = 0
    lottatore["velocita_y"] = 0
    lottatore["vivo"] = True
    lottatore["attaccando"] = False
    lottatore["cooldown_attacco"] = 0
    lottatore["durata_attacco"] = 0


def lottatore_disegna(schermo, lottatore):
    """
    Disegna un lottatore sullo schermo con grafica realistica.
    Include corpo muscoloso, testa, viso espressivo, corona per il giocatore umano.
    """
    pos = (int(lottatore["x"]), int(lottatore["y"]))
    raggio = 28

    # corona dorata sopra il giocatore umano
    if not lottatore["è_bot"] and lottatore["vivo"]:
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

    # cerchi gialli durante l'attacco
    if lottatore["attaccando"] and lottatore["durata_attacco"] > 5:
        raggio_attacco = raggio + (15 - lottatore["durata_attacco"]) * 3
        pygame.draw.circle(schermo, (255, 255, 0), pos, raggio_attacco, 4)
        pygame.draw.circle(schermo, (255, 200, 0), pos, raggio_attacco - 5, 2)

    # ombra sotto il lottatore
    if lottatore["vivo"]:
        ombra = pygame.Surface((raggio * 3, raggio))
        ombra.set_alpha(80)
        ombra.fill((0, 0, 0))
        schermo.blit(ombra, (pos[0] - raggio * 1.5, pos[1] + 8))

    # corpo con effetto 3D (tre cerchi sfumati)
    raggio_corpo = raggio + (4 if lottatore["attaccando"] else 0)
    pygame.draw.circle(
        schermo,
        tuple(max(0, c - 40) for c in lottatore["colore_corpo"]),
        pos,
        raggio_corpo,
    )
    pygame.draw.circle(
        schermo, lottatore["colore_corpo"], (pos[0] - 3, pos[1] - 3), raggio_corpo - 2
    )
    pygame.draw.circle(
        schermo,
        tuple(min(255, c + 30) for c in lottatore["colore_corpo"]),
        (pos[0] - 5, pos[1] - 5),
        raggio_corpo - 8,
    )
    pygame.draw.circle(schermo, (0, 0, 0), pos, raggio_corpo, 3)

    # muscoli pettorali
    offset_muscoli = 8
    pygame.draw.circle(
        schermo,
        tuple(max(0, c - 20) for c in lottatore["colore_corpo"]),
        (pos[0] - offset_muscoli, pos[1] - 5),
        10,
    )
    pygame.draw.circle(
        schermo,
        tuple(max(0, c - 20) for c in lottatore["colore_corpo"]),
        (pos[0] + offset_muscoli, pos[1] - 5),
        10,
    )

    # addominali
    pygame.draw.line(
        schermo,
        tuple(max(0, c - 50) for c in lottatore["colore_corpo"]),
        (pos[0] - 6, pos[1] + 5),
        (pos[0] - 3, pos[1] + 12),
        2,
    )
    pygame.draw.line(
        schermo,
        tuple(max(0, c - 50) for c in lottatore["colore_corpo"]),
        (pos[0] + 3, pos[1] + 5),
        (pos[0] + 6, pos[1] + 12),
        2,
    )

    # cintura con fibbia dorata
    pygame.draw.rect(
        schermo, (40, 40, 40), (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 8)
    )
    pygame.draw.rect(
        schermo, (70, 70, 70), (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 3)
    )
    pygame.draw.circle(schermo, (200, 180, 100), (pos[0], pos[1]), 5)
    pygame.draw.circle(schermo, (150, 130, 50), (pos[0], pos[1]), 5, 2)

    # testa con effetto 3D
    raggio_testa = 16
    testa_y = int(lottatore["y"] - raggio_corpo + 12)
    pygame.draw.circle(schermo, (230, 200, 160), (pos[0], testa_y), raggio_testa)
    pygame.draw.circle(
        schermo, (255, 220, 177), (pos[0] - 2, testa_y - 2), raggio_testa - 2
    )
    pygame.draw.circle(schermo, (0, 0, 0), (pos[0], testa_y), raggio_testa, 2)

    # chonmage (nodo capelli sumo)
    capelli_y = testa_y - raggio_testa + 4
    pygame.draw.circle(schermo, (20, 20, 20), (pos[0], capelli_y), 7)
    pygame.draw.circle(schermo, (10, 10, 10), (pos[0], capelli_y - 3), 4)

    # viso: occhi diversi se sta attaccando
    offset_occhi = 6
    occhi_y = testa_y + 2
    if lottatore["attaccando"]:
        # occhi chiusi e aggressivi
        pygame.draw.line(
            schermo,
            (0, 0, 0),
            (pos[0] - offset_occhi - 3, occhi_y),
            (pos[0] - offset_occhi + 3, occhi_y - 2),
            3,
        )
        pygame.draw.line(
            schermo,
            (0, 0, 0),
            (pos[0] + offset_occhi - 3, occhi_y - 2),
            (pos[0] + offset_occhi + 3, occhi_y),
            3,
        )
    else:
        # occhi aperti con iride e pupilla
        pygame.draw.ellipse(
            schermo, (255, 255, 255), (pos[0] - offset_occhi - 4, occhi_y - 3, 8, 6)
        )
        pygame.draw.ellipse(
            schermo, (255, 255, 255), (pos[0] + offset_occhi - 4, occhi_y - 3, 8, 6)
        )
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] - offset_occhi, occhi_y), 3)
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] + offset_occhi, occhi_y), 3)
        pygame.draw.circle(schermo, (0, 0, 0), (pos[0] - offset_occhi, occhi_y), 2)
        pygame.draw.circle(schermo, (0, 0, 0), (pos[0] + offset_occhi, occhi_y), 2)

    # sopracciglia
    pygame.draw.line(
        schermo,
        (40, 30, 20),
        (pos[0] - offset_occhi - 5, occhi_y - 6),
        (pos[0] - offset_occhi + 3, occhi_y - 7),
        2,
    )
    pygame.draw.line(
        schermo,
        (40, 30, 20),
        (pos[0] + offset_occhi - 3, occhi_y - 7),
        (pos[0] + offset_occhi + 5, occhi_y - 6),
        2,
    )

    # naso
    pygame.draw.circle(schermo, (220, 190, 150), (pos[0], testa_y + 8), 3)

    # bocca: seria se attacca, sorridente altrimenti
    if lottatore["attaccando"]:
        pygame.draw.arc(
            schermo, (100, 50, 50), (pos[0] - 6, testa_y + 10, 12, 8), 0, math.pi, 2
        )
    else:
        pygame.draw.arc(
            schermo,
            (150, 80, 80),
            (pos[0] - 7, testa_y + 8, 14, 10),
            math.pi,
            2 * math.pi,
            2,
        )

    # nome sopra il lottatore (giallo per l'umano, bianco per i bot)
    if lottatore["vivo"]:
        font = pygame.font.Font(None, 22 if not lottatore["è_bot"] else 20)
        colore_nome = (255, 215, 0) if not lottatore["è_bot"] else (255, 255, 255)
        superficie_nome = font.render(lottatore["nome"], True, colore_nome)
        rett_nome = superficie_nome.get_rect(
            center=(pos[0], pos[1] - raggio_corpo - 15)
        )
        colore_sfondo = (50, 40, 0) if not lottatore["è_bot"] else (0, 0, 0)
        rett_sfondo = rett_nome.inflate(12, 6)
        pygame.draw.rect(schermo, colore_sfondo, rett_sfondo, border_radius=5)
        pygame.draw.rect(schermo, colore_nome, rett_sfondo, 2, border_radius=5)
        schermo.blit(superficie_nome, rett_nome)


def crea_tutti_lottatori(livello_difficolta):
    """
    Crea tutti gli 8 giocatori del gioco.
    1 giocatore umano (PLAYER) + 7 bot, disposti in cerchio al centro.
    """
    lista_lottatori = []

    centro_griglia_x = LARGHEZZA // 2
    centro_griglia_y = ALTEZZA // 2 + 30
    num_giocatori = 8
    raggio_spawn = 100

    colori_giocatori = [
        (255, 100, 100),  # Rosso chiaro  — giocatore umano
        (100, 255, 100),  # Verde chiaro  — bot 1
        (100, 100, 255),  # Blu chiaro    — bot 2
        (255, 255, 100),  # Giallo chiaro — bot 3
        (255, 100, 255),  # Magenta       — bot 4
        (100, 255, 255),  # Ciano         — bot 5
        (255, 150, 100),  # Arancione     — bot 6
        (200, 100, 255),  # Viola         — bot 7
    ]

    for i in range(num_giocatori):
        angolo = (2 * math.pi / num_giocatori) * i
        spawn_x = centro_griglia_x + math.cos(angolo) * raggio_spawn
        spawn_y = centro_griglia_y + math.sin(angolo) * raggio_spawn

        if i == 0:
            nome = "PLAYER"
            è_bot = False
        else:
            nome = f"BOT {i}"
            è_bot = True

        lottatore = crea_lottatore(
            spawn_x, spawn_y, colori_giocatori[i], nome, è_bot, livello_difficolta
        )
        lista_lottatori.append(lottatore)

    return lista_lottatori
