import pygame  
import math    
import random

from Costanti_e_variabili import *
from Menu_e_interfaccia import *
from Piattaforme import *
from Lottatori import *


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
    orologio = pygame.time.Clock() 
    
    fonts = {
        'titolo': pygame.font.Font(None, 70),
        'grande': pygame.font.Font(None, 50),
        'medio': pygame.font.Font(None, 36),
        'piccolo': pygame.font.Font(None, 28),
        'minuscolo': pygame.font.Font(None, 22)
    }
    
    bottoni_difficolta = {}
    bottone_inizio = None
    bottone_riavvio = None
    
    in_esecuzione = True
    while in_esecuzione:
        
        pos_mouse = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            
            if evento.type == pygame.QUIT:
                in_esecuzione = False
            
            elif evento.type == pygame.KEYDOWN:
                
                if evento.key == pygame.K_SPACE and stato_gioco == "VINCITORE":
                    stato_gioco = "MENU"
            
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1: 
                
                if stato_gioco == "MENU":
                 
                    for valore_diff, rett_bottone in bottoni_difficolta.items():
                        if rett_bottone.collidepoint(pos_mouse):
                            difficolta = valore_diff
                    
                    if bottone_inizio and bottone_inizio.collidepoint(pos_mouse):
                      
                        piattaforme = crea_tutte_piattaforme()
                        lottatori = crea_tutti_lottatori(difficolta)
                        
                        numero_round = 1
                        vincitore = None
                        piattaforme_scomparse = False
                        
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
               
                    if bottone_riavvio and bottone_riavvio.collidepoint(pos_mouse):
                        stato_gioco = "MENU"
        
        # ==============================================================
        # AGGIORNA LO STATO DEL GIOCO
        # ==============================================================
        
        if stato_gioco == "GIOCANDO":
        
            conto_alla_rovescia -= 1/60
            
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            for lottatore in lottatori:
                if lottatore['vivo']:
                    lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            if conto_alla_rovescia <= 0:

                for piattaforma in piattaforme:
                    if piattaforma['nome_colore'] != colore_target:
                        piattaforma_inizia_scomparsa(piattaforma)
                
                piattaforme_scomparse = True
                
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
            
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
        
        elif stato_gioco == "ATTESA":
          
            conto_alla_rovescia -= 1/60
            
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            for lottatore in lottatori:
                lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            if piattaforme_scomparse:
                for lottatore in lottatori:
                    if lottatore['vivo']:
                        if not lottatore_controlla_su_piattaforma(lottatore, piattaforme, colore_target):
                            lottatore['vivo'] = False
            
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
            
            if conto_alla_rovescia <= 0:
            
                lottatori_vivi = [l for l in lottatori if l['vivo']]
                
                if len(lottatori_vivi) == 1:
                 
                    vincitore = lottatori_vivi[0]
                    stato_gioco = "VINCITORE"
                
                elif len(lottatori_vivi) == 0:
                    
                    vincitore = None
                    stato_gioco = "VINCITORE"
                
                else:
                 
                    numero_round += 1
                    
                    piattaforme = crea_tutte_piattaforme()
                    
                    num_vivi = len(lottatori_vivi)
                    centro_griglia_x = LARGHEZZA // 2
                    centro_griglia_y = ALTEZZA // 2 + 30
                    raggio_spawn = 100
                    
                    for i, lottatore in enumerate(lottatori_vivi):
                        angolo = (2 * math.pi / num_vivi) * i
                        lottatore['spawn_x'] = centro_griglia_x + math.cos(angolo) * raggio_spawn
                        lottatore['spawn_y'] = centro_griglia_y + math.sin(angolo) * raggio_spawn
                        lottatore_resetta_posizione(lottatore)
                    
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
        
     
        schermo.fill((25, 25, 30))  
        
     
        if stato_gioco == "MENU":
           
            bottoni_difficolta, bottone_inizio = disegna_menu(schermo, fonts, pos_mouse, difficolta)
        
        elif stato_gioco in ["GIOCANDO", "ATTESA"]:
      
            for piattaforma in piattaforme:
                piattaforma_disegna(schermo, piattaforma)
            
            
            for lottatore in lottatori:
                lottatore_disegna(schermo, lottatore)
           
            disegna_hud_gioco(schermo, fonts, numero_round, difficolta, colore_target, 
                           stato_gioco, conto_alla_rovescia, lottatori)
            
            bottone_riavvio = disegna_bottone_riavvio(schermo, fonts, pos_mouse)
        
        elif stato_gioco == "VINCITORE":
      
            disegna_schermata_vincitore(schermo, fonts, vincitore, numero_round, difficolta)
        
        pygame.display.flip()
    
        orologio.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    
    main()
