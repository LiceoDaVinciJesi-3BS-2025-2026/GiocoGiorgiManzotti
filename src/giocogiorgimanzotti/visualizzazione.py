 
        # Sfondo nero/grigio scuro
        schermo.fill((25, 25, 30))
        
        if stato_gioco == "MENU":
            # Disegna il menu
            bottoni_difficolta, bottone_inizio = disegna_menu(schermo, fonts, pos_mouse)
        
        elif stato_gioco in ["GIOCANDO", "ATTESA"]:
            # Disegna il gioco
            
            # Disegna piattaforme
            for piattaforma in piattaforme:
                piattaforma_disegna(schermo, piattaforma)
            
            # Disegna giocatori
            for lottatore in lottatori:
                lottatore_disegna(schermo, lottatore)
            
            # Disegna HUD
            disegna_hud_gioco(schermo, fonts, numero_round, difficolta, colore_target, 
                           stato_gioco, conto_alla_rovescia, lottatori)
            
            # Disegna bottone riavvio
            bottone_riavvio = disegna_bottone_riavvio(schermo, fonts, pos_mouse)
        
        elif stato_gioco == "VINCITORE":
            # Disegna schermata vincitore
            disegna_schermata_vincitore(schermo, fonts, vincitore, numero_round, difficolta)
        
        # Aggiorna lo schermo
        pygame.display.flip()
        
        # Limita a 60 FPS
        orologio.tick(FPS)
    
    # Chiudi Pygame
    pygame.quit()


# Esegui il gioco!
if __name__ == "__main__":
    main()
