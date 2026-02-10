def main():
    """Funzione principale che esegue il gioco"""
    
    # Variabili globali
    global stato_gioco, difficolta, piattaforme, lottatori, colore_target
    global conto_alla_rovescia, numero_round, vincitore, piattaforme_scomparse
    
    # Inizializza Pygame
    pygame.init()
    schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
    pygame.display.set_caption("Sumo Color Survival")
    orologio = pygame.time.Clock()
    
    # Crea i font
    fonts = {
        'titolo': pygame.font.Font(None, 70),
        'grande': pygame.font.Font(None, 50),
        'medio': pygame.font.Font(None, 36),
        'piccolo': pygame.font.Font(None, 28),
        'minuscolo': pygame.font.Font(None, 22)
    }
    
    # Variabili per i bottoni del menu
    bottoni_difficolta = {}
    bottone_inizio = None
    bottone_riavvio = None
    
    # Loop principale del gioco
    in_esecuzione = True
    while in_esecuzione:
        
        # Ottieni la posizione del mouse
        pos_mouse = pygame.mouse.get_pos()
        
        # Gestisci eventi (chiusura, click, tasti)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                in_esecuzione = False
            
            elif evento.type == pygame.KEYDOWN:
                # Tasto SPAZIO nella schermata vincitore
                if evento.key == pygame.K_SPACE and stato_gioco == "VINCITORE":
                    stato_gioco = "MENU"
            
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # Click sinistro
                
                if stato_gioco == "MENU":
                    # Click sui bottoni difficoltà
                    for valore_diff, rett_bottone in bottoni_difficolta.items():
                        if rett_bottone.collidepoint(pos_mouse):
                            difficolta = valore_diff
                    
                    # Click sul bottone INIZIO
                    if bottone_inizio and bottone_inizio.collidepoint(pos_mouse):
                        # Inizia il gioco!
                        piattaforme = crea_tutte_piattaforme()
                        lottatori = crea_tutti_lottatori(difficolta)
                        numero_round = 1
                        vincitore = None
                        piattaforme_scomparse = False
                        
                        # Inizia il primo round
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
                    # Click sul bottone RIAVVIO
                    if bottone_riavvio and bottone_riavvio.collidepoint(pos_mouse):
                        stato_gioco = "MENU"
        
        # ==============================================================
        # AGGIORNA LO STATO DEL GIOCO
        # ==============================================================
        
        if stato_gioco == "GIOCANDO":
            # Aggiorna countdown
            conto_alla_rovescia -= 1/60
            
            # Ottieni input da tastiera e mouse
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            # Aggiorna tutti i giocatori
            for lottatore in lottatori:
                if lottatore['vivo']:
                    lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            # Quando il countdown finisce
            if conto_alla_rovescia <= 0:
                # Fa scomparire le piattaforme sbagliate
                for piattaforma in piattaforme:
                    if piattaforma['nome_colore'] != colore_target:
                        piattaforma_inizia_scomparsa(piattaforma)
                
                piattaforme_scomparse = True
                
                # Controlla chi è su piattaforme sbagliate
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
            
            # Aggiorna animazione piattaforme
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
        
        elif stato_gioco == "ATTESA":
            # Aggiorna countdown
            conto_alla_rovescia -= 1/60
            
            # Ottieni input
            tasti = pygame.key.get_pressed()
            pulsanti_mouse = pygame.mouse.get_pressed()
            
            # Aggiorna giocatori
            for lottatore in lottatori:
                lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, piattaforme, colore_target, lottatori)
            
            # Controlla se qualcuno cade dalle piattaforme
            if piattaforme_scomparse:
                for lottatore in lottatori:
                    if lottatore['vivo']:
                        if not lottatore_controlla_su_piattaforma(lottatore, piattaforme, colore_target):
                            lottatore['vivo'] = False
            
            # Aggiorna piattaforme
            for piattaforma in piattaforme:
                piattaforma_aggiorna(piattaforma)
            
            # Quando il countdown finisce
            if conto_alla_rovescia <= 0:
                # Conta i sopravvissuti
                lottatori_vivi = [l for l in lottatori if l['vivo']]
                
                if len(lottatori_vivi) == 1:
                    # Abbiamo un vincitore!
                    vincitore = lottatori_vivi[0]
                    stato_gioco = "VINCITORE"
                
                elif len(lottatori_vivi) == 0:
                    # Pareggio
                    vincitore = None
                    stato_gioco = "VINCITORE"
                
                else:
                    # Continua con un nuovo round
                    numero_round += 1
                    piattaforme = crea_tutte_piattaforme()
                    
                    # Respawn dei giocatori vivi al centro
                    num_vivi = len(lottatori_vivi)
                    centro_griglia_x = LARGHEZZA // 2
                    centro_griglia_y = ALTEZZA // 2 + 30
                    raggio_spawn = 100
                    
                    for i, lottatore in enumerate(lottatori_vivi):
                        angolo = (2 * math.pi / num_vivi) * i
                        lottatore['spawn_x'] = centro_griglia_x + math.cos(angolo) * raggio_spawn
                        lottatore['spawn_y'] = centro_griglia_y + math.sin(angolo) * raggio_spawn
                        lottatore_resetta_posizione(lottatore)
                    
                    # Inizia nuovo round
                    stato_gioco = "GIOCANDO"
                    conto_alla_rovescia = 3.0
                    piattaforme_scomparse = False
                    colore_target = random.choice(NOMI_COLORI)
                    
                    for lottatore in lottatori:
                        if lottatore['è_bot']:
                            lottatore['timer_ai'] = 0
                            lottatore['piattaforma_target'] = None