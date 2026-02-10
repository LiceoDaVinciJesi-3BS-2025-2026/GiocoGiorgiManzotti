def crea_lottatore(x, y, colore_corpo, nome, è_bot, difficolta):
    """
    Crea un giocatore lottatore di sumo.
    Restituisce un dizionario con tutte le informazioni del giocatore.
    """
    return {
        # Posizione
        'x': x,
        'y': y,
        'spawn_x': x,  # Posizione iniziale dove riappare
        'spawn_y': y,
        
        # Movimento
        'velocita_x': 0,
        'velocita_y': 0,
        
        # Aspetto
        'colore_corpo': colore_corpo,
        'nome': nome,
        'è_bot': è_bot,
        'vivo': True,
        
        # Attacco
        'attaccando': False,
        'cooldown_attacco': 0,  # Tempo prima di poter attaccare di nuovo
        'durata_attacco': 0,    # Durata dell'animazione di attacco
        
        # AI (per i bot)
        'difficolta': difficolta,
        'piattaforma_target': None,  # Piattaforma verso cui il bot si sta muovendo
        'timer_ai': 0,
        'tempo_reazione_ai': ottieni_tempo_reazione_ai(difficolta),
        'qualita_decisioni_ai': ottieni_qualita_decisioni_ai(difficolta),
        'probabilita_attacco_ai': ottieni_probabilita_attacco_ai(difficolta)
    }


def ottieni_tempo_reazione_ai(difficolta):
    """Quanto velocemente il bot reagisce (in frame) - BOT PIÙ FORTI"""
    if difficolta == "FACILE":
        return random.randint(50, 80)   # Da 80-120 a 50-80 (più veloci)
    elif difficolta == "MEDIO":
        return random.randint(20, 40)   # Da 40-70 a 20-40 (più veloci)
    else:  # DIFFICILE
        return random.randint(5, 15)    # Da 10-30 a 5-15 (molto più veloci)


def ottieni_qualita_decisioni_ai(difficolta):
    """Quanto bene il bot sceglie le piattaforme (0-1) - BOT PIÙ INTELLIGENTI"""
    if difficolta == "FACILE":
        return 0.6   # Da 0.3 a 0.6 (60% scelte ottime)
    elif difficolta == "MEDIO":
        return 0.85  # Da 0.7 a 0.85 (85% scelte ottime)
    else:  # DIFFICILE
        return 0.98  # Da 0.95 a 0.98 (98% scelte ottime)


def ottieni_probabilita_attacco_ai(difficolta):
    """Quanto spesso il bot attacca quando vicino a un nemico"""
    if difficolta == "FACILE":
        return 0.015  # Da 0.01 a 0.015 (più aggressivi)
    elif difficolta == "MEDIO":
        return 0.04   # Da 0.03 a 0.04 (più aggressivi)
    else:  # DIFFICILE
        return 0.10   # Da 0.08 a 0.10 (molto aggressivi)


def lottatore_aggiorna(lottatore, tasti, pulsanti_mouse, lista_piattaforme, nome_colore_target, tutti_lottatori):
    """Aggiorna un giocatore (movimento, attacco, ecc.)"""
    
    if not lottatore['vivo']:
        # Se morto, cade verso il basso (sempre, senza sparire improvvisamente)
        lottatore['y'] += 5
        return
    
    # Aggiorna cooldown attacco
    if lottatore['cooldown_attacco'] > 0:
        lottatore['cooldown_attacco'] -= 1
    
    # Aggiorna durata attacco
    if lottatore['durata_attacco'] > 0:
        lottatore['durata_attacco'] -= 1
        if lottatore['durata_attacco'] == 0:
            lottatore['attaccando'] = False
    
    # Controlli
    if lottatore['è_bot']:
        # Bot: usa intelligenza artificiale
        lottatore_aggiorna_ai(lottatore, lista_piattaforme, nome_colore_target, tutti_lottatori)
    else:
        # Giocatore umano: usa tastiera e mouse
        if tasti and pulsanti_mouse:
            # Movimento WASD
            if tasti[pygame.K_a]:
                lottatore['velocita_x'] -= 0.6
            if tasti[pygame.K_d]:
                lottatore['velocita_x'] += 0.6
            if tasti[pygame.K_w]:
                lottatore['velocita_y'] -= 0.6
            if tasti[pygame.K_s]:
                lottatore['velocita_y'] += 0.6
            
            # Attacco con click sinistro
            if pulsanti_mouse[0] and lottatore['cooldown_attacco'] == 0:
                lottatore_esegui_attacco(lottatore, tutti_lottatori)
    
    # Limita la velocità massima
    velocita = math.sqrt(lottatore['velocita_x']**2 + lottatore['velocita_y']**2)
    velocita_massima = 4.0
    if velocita > velocita_massima:
        rapporto = velocita_massima / velocita
        lottatore['velocita_x'] *= rapporto
        lottatore['velocita_y'] *= rapporto
    
    # Applica attrito (rallenta gradualmente)
    lottatore['velocita_x'] *= 0.85
    lottatore['velocita_y'] *= 0.85
    
    # Aggiorna posizione
    lottatore['x'] += lottatore['velocita_x']
    lottatore['y'] += lottatore['velocita_y']
    
    # Limiti dello schermo
    lottatore['x'] = max(22, min(LARGHEZZA - 22, lottatore['x']))
    lottatore['y'] = max(22, min(ALTEZZA - 22, lottatore['y']))


def lottatore_esegui_attacco(lottatore, tutti_lottatori):
    """Esegue un attacco pancia (stile Kung Fu Panda) - SPINTA DOPPIA!"""
    
    lottatore['attaccando'] = True
    lottatore['durata_attacco'] = 15
    lottatore['cooldown_attacco'] = 60  # 1 secondo
    
    raggio_attacco = 50
    spinta_attacco = 250  # RADDOPPIATA! Da 120 a 250!
    
    # Cerca altri giocatori da colpire
    for altro in tutti_lottatori:
        if altro['vivo'] and altro != lottatore:
            dx = altro['x'] - lottatore['x']
            dy = altro['y'] - lottatore['y']
            distanza = math.sqrt(dx**2 + dy**2)
            
            if distanza < raggio_attacco and distanza > 0:
                # Calcola direzione della spinta
                spinta_x = (dx / distanza) * spinta_attacco
                spinta_y = (dy / distanza) * spinta_attacco
                
                # Applica la spinta all'avversario
                altro['velocita_x'] += spinta_x
                altro['velocita_y'] += spinta_y


def lottatore_aggiorna_ai(lottatore, lista_piattaforme, nome_colore_target, tutti_lottatori):
    """Intelligenza artificiale per i bot - MIGLIORATA"""
    
    if not lista_piattaforme or not nome_colore_target:
        return
    
    # Timer per prendere decisioni
    lottatore['timer_ai'] += 1
    
    # Ogni tot frame, sceglie una nuova piattaforma target
    if lottatore['timer_ai'] > lottatore['tempo_reazione_ai'] or lottatore['piattaforma_target'] is None:
        # Trova piattaforme con il colore giusto
        piattaforme_valide = [p for p in lista_piattaforme 
                             if p['nome_colore'] == nome_colore_target and p['attiva']]
        
        if piattaforme_valide:
            # Sceglie la piattaforma in base alla qualità delle decisioni
            if random.random() < lottatore['qualita_decisioni_ai']:
                # Scelta ottimale: piattaforma più vicina
                lottatore['piattaforma_target'] = min(piattaforme_valide, 
                    key=lambda p: math.sqrt((piattaforma_ottieni_centro(p)[0] - lottatore['x'])**2 + 
                                           (piattaforma_ottieni_centro(p)[1] - lottatore['y'])**2))
            else:
                # Scelta casuale
                lottatore['piattaforma_target'] = random.choice(piattaforme_valide)
            
            lottatore['timer_ai'] = 0
            lottatore['tempo_reazione_ai'] = ottieni_tempo_reazione_ai(lottatore['difficolta'])
    
    # Muovi verso la piattaforma target
    if lottatore['piattaforma_target'] and lottatore['piattaforma_target']['attiva']:
        tx, ty = piattaforma_ottieni_centro(lottatore['piattaforma_target'])
        
        dx = tx - lottatore['x']
        dy = ty - lottatore['y']
        distanza = math.sqrt(dx**2 + dy**2)
        
        if distanza > 5:
            # BOT PIÙ FORTI: movimento più veloce anche in modalità facile
            fattore_movimento = 0.75 if lottatore['difficolta'] == "FACILE" else 0.9
            lottatore['velocita_x'] += (dx / distanza) * 0.6 * fattore_movimento
            lottatore['velocita_y'] += (dy / distanza) * 0.6 * fattore_movimento
    
    # AI per l'attacco
    if lottatore['cooldown_attacco'] == 0 and tutti_lottatori:
        for altro in tutti_lottatori:
            if altro['vivo'] and altro != lottatore:
                dx = altro['x'] - lottatore['x']
                dy = altro['y'] - lottatore['y']
                distanza = math.sqrt(dx**2 + dy**2)
                
                if distanza < 60 and random.random() < lottatore['probabilita_attacco_ai']:
                    lottatore_esegui_attacco(lottatore, tutti_lottatori)
                    break


def lottatore_controlla_su_piattaforma(lottatore, lista_piattaforme, nome_colore_target=None):
    """Controlla se il giocatore è su una piattaforma (opzionalmente del colore giusto)"""
    for piattaforma in lista_piattaforme:
        if piattaforma['attiva'] and piattaforma_contiene_punto(piattaforma, lottatore['x'], lottatore['y']):
            if nome_colore_target is None or piattaforma['nome_colore'] == nome_colore_target:
                return True
    return False


def lottatore_resetta_posizione(lottatore):
    """Riporta il giocatore alla posizione iniziale"""
    lottatore['x'] = lottatore['spawn_x']
    lottatore['y'] = lottatore['spawn_y']
    lottatore['velocita_x'] = 0
    lottatore['velocita_y'] = 0
    lottatore['vivo'] = True
    lottatore['attaccando'] = False
    lottatore['cooldown_attacco'] = 0
    lottatore['durata_attacco'] = 0


def lottatore_disegna(schermo, lottatore):
    """Disegna un lottatore con grafica REALISTICA"""
    
    # I bot morti cadono sempre visibili (rimosso il controllo che li nascondeva)
    
    pos = (int(lottatore['x']), int(lottatore['y']))
    raggio = 28  # Più grande per più dettagli
    
    # CORONA PER IL GIOCATORE UMANO
    if not lottatore['è_bot'] and lottatore['vivo']:
        corona_y = pos[1] - raggio - 28
        # Corona più elaborata
        pygame.draw.circle(schermo, (255, 215, 0), (pos[0], corona_y), 12)
        pygame.draw.circle(schermo, (200, 150, 0), (pos[0], corona_y), 12, 2)
        
        # Stella nella corona
        punti = []
        for i in range(5):
            angolo = (2 * math.pi / 5) * i - math.pi / 2
            px = pos[0] + math.cos(angolo) * 9
            py = corona_y + math.sin(angolo) * 9
            punti.append((px, py))
        pygame.draw.polygon(schermo, (255, 255, 150), punti)
        
        # Bordo dorato brillante
        pygame.draw.circle(schermo, (255, 215, 0), pos, raggio + 4, 4)
    
    # Effetto attacco più evidente
    if lottatore['attaccando'] and lottatore['durata_attacco'] > 5:
        raggio_attacco = raggio + (15 - lottatore['durata_attacco']) * 3
        pygame.draw.circle(schermo, (255, 255, 0), pos, raggio_attacco, 4)
        pygame.draw.circle(schermo, (255, 200, 0), pos, raggio_attacco - 5, 2)
    
    # Ombra più realistica
    if lottatore['vivo']:
        ombra = pygame.Surface((raggio * 3, raggio))
        ombra.set_alpha(80)
        ombra.fill((0, 0, 0))
        schermo.blit(ombra, (pos[0] - raggio * 1.5, pos[1] + 8))
    
    # CORPO REALISTICO - Più muscoloso
    raggio_corpo = raggio + (4 if lottatore['attaccando'] else 0)
    
    # Sfumatura del corpo (3 cerchi per effetto 3D)
    pygame.draw.circle(schermo, tuple(max(0, c - 40) for c in lottatore['colore_corpo']), 
                      pos, raggio_corpo)
    pygame.draw.circle(schermo, lottatore['colore_corpo'], 
                      (pos[0] - 3, pos[1] - 3), raggio_corpo - 2)
    pygame.draw.circle(schermo, tuple(min(255, c + 30) for c in lottatore['colore_corpo']), 
                      (pos[0] - 5, pos[1] - 5), raggio_corpo - 8)
    
    # Bordo corpo
    pygame.draw.circle(schermo, (0, 0, 0), pos, raggio_corpo, 3)
    
    # Muscoli pettorali (due cerchi)
    offset_muscoli = 8
    pygame.draw.circle(schermo, tuple(max(0, c - 20) for c in lottatore['colore_corpo']),
                      (pos[0] - offset_muscoli, pos[1] - 5), 10)
    pygame.draw.circle(schermo, tuple(max(0, c - 20) for c in lottatore['colore_corpo']),
                      (pos[0] + offset_muscoli, pos[1] - 5), 10)
    
    # Addominali (linee)
    pygame.draw.line(schermo, tuple(max(0, c - 50) for c in lottatore['colore_corpo']),
                    (pos[0] - 6, pos[1] + 5), (pos[0] - 3, pos[1] + 12), 2)
    pygame.draw.line(schermo, tuple(max(0, c - 50) for c in lottatore['colore_corpo']),
                    (pos[0] + 3, pos[1] + 5), (pos[0] + 6, pos[1] + 12), 2)
    
    # Cintura più dettagliata
    pygame.draw.rect(schermo, (40, 40, 40), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 8))
    pygame.draw.rect(schermo, (70, 70, 70), 
                    (pos[0] - raggio_corpo, pos[1] - 2, raggio_corpo * 2, 3))
    # Fibbia cintura
    pygame.draw.circle(schermo, (200, 180, 100), (pos[0], pos[1]), 5)
    pygame.draw.circle(schermo, (150, 130, 50), (pos[0], pos[1]), 5, 2)
    
    # TESTA più realistica
    raggio_testa = 16
    testa_y = int(lottatore['y'] - raggio_corpo + 12)
    
    # Sfumatura testa
    pygame.draw.circle(schermo, (230, 200, 160), (pos[0], testa_y), raggio_testa)
    pygame.draw.circle(schermo, (255, 220, 177), (pos[0] - 2, testa_y - 2), raggio_testa - 2)
    pygame.draw.circle(schermo, (0, 0, 0), (pos[0], testa_y), raggio_testa, 2)
    
    # Capelli più realistici (chonmage - nodo tradizionale sumo)
    capelli_y = testa_y - raggio_testa + 4
    pygame.draw.circle(schermo, (20, 20, 20), (pos[0], capelli_y), 7)
    pygame.draw.circle(schermo, (10, 10, 10), (pos[0], capelli_y - 3), 4)
    
    # Viso più espressivo
    offset_occhi = 6
    occhi_y = testa_y + 2
    
    if lottatore['attaccando']:
        # Occhi chiusi aggressivi
        pygame.draw.line(schermo, (0, 0, 0), 
                       (pos[0] - offset_occhi - 3, occhi_y),
                       (pos[0] - offset_occhi + 3, occhi_y - 2), 3)
        pygame.draw.line(schermo, (0, 0, 0),
                       (pos[0] + offset_occhi - 3, occhi_y - 2),
                       (pos[0] + offset_occhi + 3, occhi_y), 3)
    else:
        # Occhi aperti più realistici
        # Bianco occhio
        pygame.draw.ellipse(schermo, (255, 255, 255), 
                          (pos[0] - offset_occhi - 4, occhi_y - 3, 8, 6))
        pygame.draw.ellipse(schermo, (255, 255, 255), 
                          (pos[0] + offset_occhi - 4, occhi_y - 3, 8, 6))
        # Iride
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] - offset_occhi, occhi_y), 3)
        pygame.draw.circle(schermo, (80, 60, 40), (pos[0] + offset_occhi, occhi_y), 3)
        # Pupilla
        pygame.draw.circle(schermo, (0, 0, 0), (pos[0] - offset_occhi, occhi_y), 2)
        pygame.draw.circle(schermo, (0, 0, 0), (pos[0] + offset_occhi, occhi_y), 2)
    
    # Sopracciglia
    pygame.draw.line(schermo, (40, 30, 20),
                    (pos[0] - offset_occhi - 5, occhi_y - 6),
                    (pos[0] - offset_occhi + 3, occhi_y - 7), 2)
    pygame.draw.line(schermo, (40, 30, 20),
                    (pos[0] + offset_occhi - 3, occhi_y - 7),
                    (pos[0] + offset_occhi + 5, occhi_y - 6), 2)
    
    # Naso
    pygame.draw.circle(schermo, (220, 190, 150), (pos[0], testa_y + 8), 3)
    
    # Bocca (sorride se sta vincendo, seria se attacca)
    if lottatore['attaccando']:
        pygame.draw.arc(schermo, (100, 50, 50), 
                       (pos[0] - 6, testa_y + 10, 12, 8), 0, math.pi, 2)
    else:
        pygame.draw.arc(schermo, (150, 80, 80), 
                       (pos[0] - 7, testa_y + 8, 14, 10), math.pi, 2 * math.pi, 2)
    
    # Nome con sfondo migliore
    if lottatore['vivo']:
        font = pygame.font.Font(None, 22 if not lottatore['è_bot'] else 20)
        colore_nome = (255, 215, 0) if not lottatore['è_bot'] else (255, 255, 255)
        superficie_nome = font.render(lottatore['nome'], True, colore_nome)
        rett_nome = superficie_nome.get_rect(center=(pos[0], pos[1] - raggio_corpo - 15))
        
        colore_sfondo = (50, 40, 0) if not lottatore['è_bot'] else (0, 0, 0)
        rett_sfondo = rett_nome.inflate(12, 6)
        pygame.draw.rect(schermo, colore_sfondo, rett_sfondo, border_radius=5)
        pygame.draw.rect(schermo, colore_nome, rett_sfondo, 2, border_radius=5)
        schermo.blit(superficie_nome, rett_nome)


def crea_tutti_lottatori(livello_difficolta):
    """Crea tutti gli 8 giocatori (1 umano + 7 bot)"""
    lista_lottatori = []
    
    # Centro della griglia
    centro_griglia_x = LARGHEZZA // 2
    centro_griglia_y = ALTEZZA // 2 + 30
    
    num_giocatori = 8
    raggio_spawn = 100
    
    # Colori diversi per ogni giocatore
    colori_giocatori = [
        (255, 100, 100),  # Rosso chiaro (GIOCATORE UMANO)
        (100, 255, 100),  # Verde chiaro
        (100, 100, 255),  # Blu chiaro
        (255, 255, 100),  # Giallo chiaro
        (255, 100, 255),  # Magenta
        (100, 255, 255),  # Ciano
        (255, 150, 100),  # Arancione chiaro
        (200, 100, 255)   # Viola
    ]
    
    # Crea i giocatori in cerchio
    for i in range(num_giocatori):
        angolo = (2 * math.pi / num_giocatori) * i
        spawn_x = centro_griglia_x + math.cos(angolo) * raggio_spawn
        spawn_y = centro_griglia_y + math.sin(angolo) * raggio_spawn
        
        if i == 0:
            # Primo giocatore = umano
            nome = "TU"
            è_bot = False
        else:
            # Altri giocatori = bot
            nome = f"BOT {i}"
            è_bot = True
        
        lottatore = crea_lottatore(spawn_x, spawn_y, colori_giocatori[i], nome, è_bot, livello_difficolta)
        lista_lottatori.append(lottatore)
    
    return lista_lottatori

