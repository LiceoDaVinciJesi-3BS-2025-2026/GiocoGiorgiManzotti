import pygame  
import math    
import random

from Costanti_e_variabili import *
from Lottatori import *

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


def disegna_menu(schermo, fonts, pos_mouse, difficolta):
    """
    Disegna il menu principale con 3 pannelli:
    1. Difficoltà
    2. Controlli
    3. Pulsante Inizia
    
    Restituisce: (bottoni_difficolta, bottone_inizio)
    """
    LARGHEZZA = 1400
    titolo = fonts['titolo'].render("SUMO COLOR SURVIVAL", True, (255, 255, 255))
    rett_titolo = titolo.get_rect(center=(LARGHEZZA // 2, 120))
    schermo.blit(titolo, rett_titolo)
    
    ALTEZZA=800

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
            colore_testo = (0,0,0)#100, 255, 100
        elif è_hover:
            pygame.draw.rect(schermo, (200, 200,200), bottone, border_radius=10)
            pygame.draw.rect(schermo, colore_diff, bottone, 3, border_radius=10)
            colore_testo = (0,0, 0)#255, 200, 100
        else:
            pygame.draw.rect(schermo, (180, 180, 180), bottone, border_radius=10)
            colore_testo = (0,0,0)#255, 100, 100
        

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
        "SOPRAVVIVERE"
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
  
    pygame.draw.rect(schermo, (0, 0, 0, 100), (0, 0, LARGHEZZA, 80))
    
  
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
        
        titolo = fonts['piccolo'].render("PANZATA", True, (255, 215, 0))
        rett_titolo = titolo.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 25))
        schermo.blit(titolo, rett_titolo)
        
        desc1 = fonts['piccolo'].render("Click Sinistro per colpire", True, (200, 200, 200))
        rett_desc1 = desc1.get_rect(center=(x_pannello + largh_pannello // 2, y_pannello + 55))
        schermo.blit(desc1, rett_desc1)
        
        
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
    bottone_riavvio = pygame.Rect(40, ALTEZZA // 2 - 50, 200, 80)
    è_hover = bottone_riavvio.collidepoint(pos_mouse)
    
    if è_hover:
        colore_bottone = (180, 40, 40)
        colore_bordo = (255, 120, 120)
    else:
        colore_bottone = (120, 30, 30)
        colore_bordo = (200, 80, 80)
    
    pygame.draw.rect(schermo, colore_bottone, bottone_riavvio, border_radius=15)
    pygame.draw.rect(schermo, colore_bordo, bottone_riavvio, 4, border_radius=15)
    
    testo_icona = fonts['grande'].render(" ", True, (255, 255, 255))
    rett_icona = testo_icona.get_rect(center=(bottone_riavvio.centerx, bottone_riavvio.centery - 15))
    schermo.blit(testo_icona, rett_icona)
    
    testo_bottone = fonts['piccolo'].render("Nuova Partita", True, (255, 255, 200))
    rett_testo_bottone = testo_bottone.get_rect(center=(bottone_riavvio.centerx, bottone_riavvio.centery))
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
    
        testo_vincitore = fonts['titolo'].render(f" {lottatore_vincitore['nome']} HA VINTO! ", 
                                                 True, (255, 215, 0))
        
        lottatore_vincitore['x'] = LARGHEZZA // 2
        lottatore_vincitore['y'] = ALTEZZA // 2 + 150
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

