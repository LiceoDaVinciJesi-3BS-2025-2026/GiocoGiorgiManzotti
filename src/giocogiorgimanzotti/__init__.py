import pygame
import math
import random
from enum import Enum

# Costanti
WIDTH, HEIGHT = 1400, 800
FPS = 60

# Colori
COLORS = {
    'RED': (255, 0, 0),
    'WHITE': (255, 255, 255),
    'YELLOW': (255, 255, 0),
    'BLUE': (0, 0, 255),
    'ORANGE': (255, 165, 0),
    'GREEN': (0, 255, 0)
}

COLOR_NAMES = list(COLORS.keys())


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    WAITING = 3
    WINNER = 4


class Platform:
    """Classe per una piattaforma colorata"""
    
    def __init__(self, x, y, width, height, color_name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color_name = color_name
        self.color = COLORS[color_name]
        self.active = True
        self.disappear_progress = 0
        
    def start_disappear(self):
        """Inizia l'animazione di scomparsa"""
        self.active = False
    
    def update(self):
        """Aggiorna l'animazione"""
        if not self.active and self.disappear_progress < 1:
            self.disappear_progress += 0.05
    
    def draw(self, screen):
        """Disegna la piattaforma"""
        if self.disappear_progress >= 1:
            return
        
        if not self.active:
            scale = 1 - self.disappear_progress
            offset = self.disappear_progress * 20
            
            rect = pygame.Rect(
                self.x + offset,
                self.y + offset,
                self.width * scale,
                self.height * scale
            )
        else:
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 3)
    
    def contains_point(self, x, y):
        """Controlla se un punto è dentro la piattaforma"""
        if not self.active or self.disappear_progress >= 1:
            return False
        
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def get_center(self):
        """Restituisce il centro della piattaforma"""
        return (self.x + self.width // 2, self.y + self.height // 2)


class SumoWrestler:
    """Classe per un personaggio lottatore di sumo"""
    
    def __init__(self, x, y, body_color, name, is_bot=False, difficulty=Difficulty.EASY):
        # Posizione
        self.x = x
        self.y = y
        self.spawn_x = x
        self.spawn_y = y
        
        # Fisica
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.6
        self.max_speed = 4.0
        self.friction = 0.85
        
        # Dimensioni
        self.radius = 22
        self.head_radius = 13
        
        # Aspetto
        self.body_color = body_color
        self.skin_color = (255, 220, 177)
        self.belt_color = (50, 50, 50)
        
        # Info
        self.name = name
        self.is_bot = is_bot
        self.alive = True
        self.difficulty = difficulty
        
        # Attacco - SPINTA PIÙ FORTE (80 pixel = circa 70% di una piattaforma)
        self.attacking = False
        self.attack_cooldown = 0
        self.attack_range = 50
        self.attack_duration = 0
        self.attack_knockback = 80  # Aumentato da 55 a 80 per spinta più forte
        
        # AI per i bot
        self.target_platform = None
        self.ai_timer = 0
        self.ai_reaction_time = self.get_ai_reaction_time()
        self.ai_decision_quality = self.get_ai_decision_quality()
        self.ai_attack_chance = self.get_ai_attack_chance()
        
    def get_ai_reaction_time(self):
        """Ottiene il tempo di reazione dell'AI basato sulla difficoltà"""
        if self.difficulty == Difficulty.EASY:
            return random.randint(80, 120)
        elif self.difficulty == Difficulty.MEDIUM:
            return random.randint(40, 70)
        else:  # HARD
            return random.randint(10, 30)
    
    def get_ai_decision_quality(self):
        """Percentuale di decisioni ottimali (0-1)"""
        if self.difficulty == Difficulty.EASY:
            return 0.3
        elif self.difficulty == Difficulty.MEDIUM:
            return 0.7
        else:  # HARD
            return 0.95
    
    def get_ai_attack_chance(self):
        """Probabilità di attacco per frame quando vicino a un nemico"""
        if self.difficulty == Difficulty.EASY:
            return 0.01
        elif self.difficulty == Difficulty.MEDIUM:
            return 0.03
        else:  # HARD
            return 0.08
    
    def update(self, keys=None, mouse_buttons=None, platforms=None, target_color=None, other_wrestlers=None):
        """Aggiorna lo stato del lottatore"""
        if not self.alive:
            self.y += 5
            return
        
        # Aggiorna cooldown attacco
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Aggiorna durata attacco
        if self.attack_duration > 0:
            self.attack_duration -= 1
            if self.attack_duration == 0:
                self.attacking = False
        
        # Controlli
        if self.is_bot:
            self.update_ai(platforms, target_color, other_wrestlers)
        elif keys and mouse_buttons:
            # Controlli umani (WASD)
            if keys[pygame.K_a]:
                self.velocity_x -= self.acceleration
            if keys[pygame.K_d]:
                self.velocity_x += self.acceleration
            if keys[pygame.K_w]:
                self.velocity_y -= self.acceleration
            if keys[pygame.K_s]:
                self.velocity_y += self.acceleration
            
            # Attacco con click sinistro
            if mouse_buttons[0] and self.attack_cooldown == 0:
                self.perform_attack(other_wrestlers)
        
        # Limita la velocità
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > self.max_speed:
            ratio = self.max_speed / speed
            self.velocity_x *= ratio
            self.velocity_y *= ratio
        
        # Applica attrito
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Aggiorna posizione
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Limiti dello schermo
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
    
    def perform_attack(self, other_wrestlers):
        """Esegue un attacco pancia in stile Kung Fu Panda"""
        if not other_wrestlers:
            return
        
        self.attacking = True
        self.attack_duration = 15
        self.attack_cooldown = 60
        
        # Controlla collisioni con altri lottatori
        for other in other_wrestlers:
            if other.alive and other != self:
                dx = other.x - self.x
                dy = other.y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < self.attack_range and distance > 0:
                    # Calcola direzione del knockback (80 pixel = spinta più forte)
                    knock_x = (dx / distance) * self.attack_knockback
                    knock_y = (dy / distance) * self.attack_knockback
                    
                    # Applica knockback
                    other.velocity_x += knock_x
                    other.velocity_y += knock_y
    
    def update_ai(self, platforms, target_color, other_wrestlers):
        """AI per i bot con difficoltà variabile"""
        if not platforms or not target_color:
            return
        
        # Timer per le decisioni
        self.ai_timer += 1
        
        if self.ai_timer > self.ai_reaction_time or not self.target_platform:
            # Trova piattaforme con il colore target
            valid_platforms = [p for p in platforms 
                             if p.color_name == target_color and p.active]
            
            if valid_platforms:
                # Scelta della piattaforma basata sulla qualità delle decisioni
                if random.random() < self.ai_decision_quality:
                    # Scelta ottimale: piattaforma più vicina
                    self.target_platform = min(valid_platforms, 
                        key=lambda p: math.sqrt((p.get_center()[0] - self.x)**2 + 
                                               (p.get_center()[1] - self.y)**2))
                else:
                    # Scelta casuale
                    self.target_platform = random.choice(valid_platforms)
                
                self.ai_timer = 0
                self.ai_reaction_time = self.get_ai_reaction_time()
        
        # Muovi verso la piattaforma target
        if self.target_platform and self.target_platform.active:
            tx, ty = self.target_platform.get_center()
            
            dx = tx - self.x
            dy = ty - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 5:
                movement_factor = 0.5 if self.difficulty == Difficulty.EASY else 0.8
                self.velocity_x += (dx / distance) * self.acceleration * movement_factor
                self.velocity_y += (dy / distance) * self.acceleration * movement_factor
        
        # AI per l'attacco
        if self.attack_cooldown == 0 and other_wrestlers:
            for other in other_wrestlers:
                if other.alive and other != self:
                    dx = other.x - self.x
                    dy = other.y - self.y
                    distance = math.sqrt(dx**2 + dy**2)
                    
                    if distance < self.attack_range * 1.2 and random.random() < self.ai_attack_chance:
                        self.perform_attack(other_wrestlers)
                        break
    
    def check_on_platform(self, platforms, target_color=None):
        """Controlla se il lottatore è su una piattaforma"""
        for platform in platforms:
            if platform.active and platform.contains_point(self.x, self.y):
                if target_color is None or platform.color_name == target_color:
                    return True
        return False
    
    def reset_position(self):
        """Resetta alla posizione di spawn"""
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.alive = True
        self.attacking = False
        self.attack_cooldown = 0
        self.attack_duration = 0
    
    def draw(self, screen):
        """Disegna il lottatore"""
        if not self.alive and self.y > HEIGHT + 50:
            return
        
        pos = (int(self.x), int(self.y))
        
        # INDICATORE GIOCATORE UMANO - Corona dorata sopra la testa
        if not self.is_bot and self.alive:
            crown_y = pos[1] - self.radius - 25
            # Sfondo corona
            pygame.draw.circle(screen, (255, 215, 0), (pos[0], crown_y), 10)
            # Stella interna
            points = []
            for i in range(5):
                angle = (2 * math.pi / 5) * i - math.pi / 2
                px = pos[0] + math.cos(angle) * 8
                py = crown_y + math.sin(angle) * 8
                points.append((px, py))
            pygame.draw.polygon(screen, (255, 255, 100), points)
            
            # Bordo dorato sul personaggio
            pygame.draw.circle(screen, (255, 215, 0), pos, self.radius + 3, 3)
        
        # Effetto attacco
        if self.attacking and self.attack_duration > 5:
            attack_radius = self.radius + (15 - self.attack_duration) * 2
            pygame.draw.circle(screen, (255, 255, 0, 100), pos, attack_radius, 3)
        
        # Ombra
        if self.alive:
            pygame.draw.ellipse(screen, (0, 0, 0, 100), 
                              (pos[0] - self.radius, pos[1] + 5, 
                               self.radius * 2, self.radius))
        
        # Corpo
        body_radius = self.radius + (3 if self.attacking else 0)
        pygame.draw.circle(screen, self.body_color, pos, body_radius)
        pygame.draw.circle(screen, (0, 0, 0), pos, body_radius, 2)
        
        # Cintura
        pygame.draw.rect(screen, self.belt_color, 
                        (pos[0] - body_radius, pos[1] - 3, 
                         body_radius * 2, 6))
        
        # Testa
        head_y = int(self.y - body_radius + 10)
        pygame.draw.circle(screen, self.skin_color, 
                         (pos[0], head_y), self.head_radius)
        pygame.draw.circle(screen, (0, 0, 0), 
                         (pos[0], head_y), self.head_radius, 2)
        
        # Capelli
        hair_y = head_y - self.head_radius + 3
        pygame.draw.circle(screen, (20, 20, 20), 
                         (pos[0], hair_y), 5)
        
        # Occhi
        eye_offset = 5
        eye_y = head_y
        if self.attacking:
            pygame.draw.line(screen, (0, 0, 0), 
                           (pos[0] - eye_offset - 2, eye_y),
                           (pos[0] - eye_offset + 2, eye_y), 2)
            pygame.draw.line(screen, (0, 0, 0),
                           (pos[0] + eye_offset - 2, eye_y),
                           (pos[0] + eye_offset + 2, eye_y), 2)
        else:
            pygame.draw.circle(screen, (255, 255, 255), 
                             (pos[0] - eye_offset, eye_y), 3)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (pos[0] - eye_offset, eye_y), 1)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (pos[0] + eye_offset, eye_y), 3)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (pos[0] + eye_offset, eye_y), 1)
        
        # Nome (colore oro per il giocatore)
        if self.alive:
            font = pygame.font.Font(None, 20 if not self.is_bot else 18)
            name_color = (255, 215, 0) if not self.is_bot else (255, 255, 255)
            name_surface = font.render(self.name, True, name_color)
            name_rect = name_surface.get_rect(center=(pos[0], pos[1] - body_radius - 12))
            
            bg_color = (50, 40, 0) if not self.is_bot else (0, 0, 0)
            bg_rect = name_rect.inflate(10, 5)
            pygame.draw.rect(screen, bg_color, bg_rect, border_radius=3)
            screen.blit(name_surface, name_rect)
        
        # Barra cooldown attacco
        if self.attack_cooldown > 0 and self.alive:
            cooldown_ratio = self.attack_cooldown / 60
            bar_width = body_radius * 2
            bar_height = 3
            bar_x = pos[0] - body_radius
            bar_y = pos[1] + body_radius + 8
            
            pygame.draw.rect(screen, (100, 100, 100), 
                           (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 200, 0), 
                           (bar_x, bar_y, bar_width * cooldown_ratio, bar_height))


class Game:
    """Classe principale del gioco"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sumo Color Survival - 8 Players")
        self.clock = pygame.time.Clock()
        
        # Stato del gioco
        self.state = GameState.MENU
        self.difficulty = Difficulty.EASY
        self.platforms = []
        self.wrestlers = []
        self.target_color = None
        self.countdown = 3.0
        self.round_number = 1
        self.winner = None
        self.platforms_disappeared = False
        
        # Font
        self.title_font = pygame.font.Font(None, 90)
        self.big_font = pygame.font.Font(None, 60)
        self.medium_font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 26)
        self.tiny_font = pygame.font.Font(None, 22)
        
        # Bottoni menu - LAYOUT MIGLIORATO
        self.difficulty_buttons = {
            Difficulty.EASY: pygame.Rect(WIDTH // 2 - 180, 340, 360, 70),
            Difficulty.MEDIUM: pygame.Rect(WIDTH // 2 - 180, 430, 360, 70),
            Difficulty.HARD: pygame.Rect(WIDTH // 2 - 180, 520, 360, 70)
        }
        self.start_button = pygame.Rect(WIDTH // 2 - 200, 650, 400, 80)
        
        # Bottone restart - SEMPRE VISIBILE DURANTE IL GIOCO
        self.restart_button = pygame.Rect(40, HEIGHT // 2 - 50, 300, 100)
    
    def setup_game(self):
        """Inizializza il gioco"""
        self.platforms = []
        self.wrestlers = []
        self.round_number = 1
        self.winner = None
        self.platforms_disappeared = False
        
        self.create_platforms()
        
        grid_center_x = WIDTH // 2
        grid_center_y = HEIGHT // 2 + 30
        
        num_players = 8
        spawn_radius = 80
        
        player_colors = [
            (255, 100, 100),  # Rosso chiaro (Player)
            (100, 255, 100),
            (100, 100, 255),
            (255, 255, 100),
            (255, 100, 255),
            (100, 255, 255),
            (255, 150, 100),
            (200, 100, 255)
        ]
        
        for i in range(num_players):
            angle = (2 * math.pi / num_players) * i
            spawn_x = grid_center_x + math.cos(angle) * spawn_radius
            spawn_y = grid_center_y + math.sin(angle) * spawn_radius
            
            if i == 0:
                name = "TU"
                is_bot = False
            else:
                name = f"BOT {i}"
                is_bot = True
            
            wrestler = SumoWrestler(
                spawn_x,
                spawn_y,
                player_colors[i],
                name,
                is_bot=is_bot,
                difficulty=self.difficulty
            )
            self.wrestlers.append(wrestler)
    
    def create_platforms(self):
        """Crea la griglia di piattaforme con ESATTAMENTE 5 piattaforme per ogni colore"""
        self.platforms = []
        
        rows = 6
        cols = 5
        platform_width = 110
        platform_height = 85
        spacing = 8
        
        grid_width = cols * platform_width + (cols - 1) * spacing
        grid_height = rows * platform_height + (rows - 1) * spacing
        offset_x = (WIDTH - grid_width) // 2
        offset_y = (HEIGHT - grid_height) // 2 + 30
        
        color_list = []
        for color_name in COLOR_NAMES:
            color_list.extend([color_name] * 5)
        
        random.shuffle(color_list)
        
        idx = 0
        for row in range(rows):
            for col in range(cols):
                x = offset_x + col * (platform_width + spacing)
                y = offset_y + row * (platform_height + spacing)
                
                color_name = color_list[idx]
                platform = Platform(x, y, platform_width, platform_height, color_name)
                self.platforms.append(platform)
                idx += 1
    
    def start_round(self):
        """Inizia un nuovo round"""
        self.state = GameState.PLAYING
        self.countdown = 3.0
        self.platforms_disappeared = False
        
        self.target_color = random.choice(COLOR_NAMES)
        
        for platform in self.platforms:
            platform.active = True
            platform.disappear_progress = 0
        
        for wrestler in self.wrestlers:
            if wrestler.is_bot:
                wrestler.ai_timer = 0
                wrestler.target_platform = None
    
    def update(self):
        """Aggiorna la logica del gioco"""
        if self.state == GameState.PLAYING:
            self.countdown -= 1/60
            
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            
            for wrestler in self.wrestlers:
                if wrestler.alive:
                    wrestler.update(
                        keys if not wrestler.is_bot else None,
                        mouse_buttons if not wrestler.is_bot else None,
                        self.platforms,
                        self.target_color,
                        self.wrestlers
                    )
            
            if self.countdown <= 0:
                for platform in self.platforms:
                    if platform.color_name != self.target_color:
                        platform.start_disappear()
                
                self.platforms_disappeared = True
                
                for wrestler in self.wrestlers:
                    if wrestler.alive:
                        on_correct_platform = False
                        for platform in self.platforms:
                            if (platform.color_name == self.target_color and 
                                platform.active and 
                                platform.contains_point(wrestler.x, wrestler.y)):
                                on_correct_platform = True
                                break
                        
                        if not on_correct_platform:
                            wrestler.alive = False
                
                self.state = GameState.WAITING
                self.countdown = 2.0
            
            for platform in self.platforms:
                platform.update()
        
        elif self.state == GameState.WAITING:
            self.countdown -= 1/60
            
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            
            for wrestler in self.wrestlers:
                wrestler.update(
                    keys if not wrestler.is_bot else None,
                    mouse_buttons if not wrestler.is_bot else None,
                    self.platforms,
                    self.target_color,
                    self.wrestlers
                )
            
            if self.platforms_disappeared:
                for wrestler in self.wrestlers:
                    if wrestler.alive:
                        if not wrestler.check_on_platform(self.platforms, self.target_color):
                            wrestler.alive = False
            
            for platform in self.platforms:
                platform.update()
            
            if self.countdown <= 0:
                alive_wrestlers = [w for w in self.wrestlers if w.alive]
                
                if len(alive_wrestlers) == 1:
                    self.winner = alive_wrestlers[0]
                    self.state = GameState.WINNER
                elif len(alive_wrestlers) == 0:
                    self.state = GameState.WINNER
                else:
                    self.round_number += 1
                    self.create_platforms()
                    self.respawn_alive_wrestlers()
                    self.start_round()
    
    def respawn_alive_wrestlers(self):
        """Respawn dei giocatori vivi al centro della scacchiera"""
        alive = [w for w in self.wrestlers if w.alive]
        num_alive = len(alive)
        
        if num_alive == 0:
            return
        
        grid_center_x = WIDTH // 2
        grid_center_y = HEIGHT // 2 + 30
        spawn_radius = 80
        
        for i, wrestler in enumerate(alive):
            angle = (2 * math.pi / num_alive) * i
            wrestler.spawn_x = grid_center_x + math.cos(angle) * spawn_radius
            wrestler.spawn_y = grid_center_y + math.sin(angle) * spawn_radius
            wrestler.reset_position()
    
    def is_player_alive(self):
        """Controlla se il giocatore umano è vivo"""
        for wrestler in self.wrestlers:
            if not wrestler.is_bot:
                return wrestler.alive
        return False
    
    def draw(self):
        """Disegna tutto sullo schermo"""
        self.screen.fill((30, 30, 40))
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state in [GameState.PLAYING, GameState.WAITING]:
            self.draw_game()
            # BOTTONE RESTART SEMPRE VISIBILE DURANTE IL GIOCO
            self.draw_restart_button()
        elif self.state == GameState.WINNER:
            self.draw_winner()
        
        pygame.display.flip()
    
    def draw_restart_button(self):
        """Disegna il bottone restart sempre visibile durante il gioco"""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.restart_button.collidepoint(mouse_pos)
        
        # Colore basato su hover
        if is_hovered:
            button_color = (180, 40, 40)
            border_color = (255, 120, 120)
        else:
            button_color = (120, 30, 30)
            border_color = (200, 80, 80)
        
        # Disegna bottone
        pygame.draw.rect(self.screen, button_color, self.restart_button, border_radius=15)
        pygame.draw.rect(self.screen, border_color, self.restart_button, 4, border_radius=15)
        
        # Icona e testo
        icon_text = self.big_font.render("↻", True, (255, 255, 255))
        icon_rect = icon_text.get_rect(center=(self.restart_button.centerx, self.restart_button.centery - 15))
        self.screen.blit(icon_text, icon_rect)
        
        button_text = self.small_font.render("Nuova Partita", True, (255, 255, 200))
        button_text_rect = button_text.get_rect(center=(self.restart_button.centerx, self.restart_button.centery + 25))
        self.screen.blit(button_text, button_text_rect)
    
    def draw_menu(self):
        """Disegna il menu iniziale con layout migliorato"""
        # Sfondo gradiente
        for i in range(HEIGHT):
            color_val = 30 + int(i / HEIGHT * 20)
            pygame.draw.line(self.screen, (color_val, color_val, color_val + 10), (0, i), (WIDTH, i))
        
        # Titolo principale con ombra
        shadow_offset = 4
        title_shadow = self.title_font.render("SUMO COLOR SURVIVAL", True, (0, 0, 0))
        title_shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, 120 + shadow_offset))
        self.screen.blit(title_shadow, title_shadow_rect)
        
        title = self.title_font.render("SUMO COLOR SURVIVAL", True, (255, 215, 0))
        title_rect = title.get_rect(center=(WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Sottotitolo
        subtitle = self.medium_font.render("⚔️ 8 Giocatori - Battaglia Finale ⚔️", True, (255, 255, 150))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Separatore decorativo
        pygame.draw.line(self.screen, (100, 100, 120), (WIDTH // 2 - 300, 240), (WIDTH // 2 + 300, 240), 2)
        
        # Etichetta difficoltà con box
        diff_box = pygame.Rect(WIDTH // 2 - 250, 265, 500, 50)
        pygame.draw.rect(self.screen, (50, 50, 60), diff_box, border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 120), diff_box, 2, border_radius=10)
        
        diff_label = self.medium_font.render("⚙️ SELEZIONA DIFFICOLTÀ", True, (255, 255, 100))
        diff_label_rect = diff_label.get_rect(center=(WIDTH // 2, 290))
        self.screen.blit(diff_label, diff_label_rect)
        
        # Bottoni difficoltà con hover migliorato
        mouse_pos = pygame.mouse.get_pos()
        
        difficulties = [
            (Difficulty.EASY, "FACILE", (100, 255, 100), "Bot lenti e poco aggressivi"),
            (Difficulty.MEDIUM, "MEDIO", (255, 200, 100), "Bot abili e tattici"),
            (Difficulty.HARD, "DIFFICILE", (255, 100, 100), "Bot esperti e spietati")
        ]
        
        for diff, text, color, description in difficulties:
            button_rect = self.difficulty_buttons[diff]
            is_selected = (self.difficulty == diff)
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # Effetto glow per selezione
            if is_selected:
                glow_rect = button_rect.inflate(10, 10)
                pygame.draw.rect(self.screen, color, glow_rect, border_radius=12)
                button_color = color
                text_color = (0, 0, 0)
                border_width = 5
            elif is_hovered:
                button_color = (70, 70, 80)
                text_color = color
                border_width = 4
            else:
                button_color = (50, 50, 60)
                text_color = (200, 200, 200)
                border_width = 2
            
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=12)
            pygame.draw.rect(self.screen, color, button_rect, border_width, border_radius=12)
            
            # Testo principale
            button_text = self.medium_font.render(text, True, text_color)
            button_text_rect = button_text.get_rect(center=(button_rect.centerx, button_rect.centery - 8))
            self.screen.blit(button_text, button_text_rect)
            
            # Descrizione
            desc_text = self.tiny_font.render(description, True, (180, 180, 180) if not is_selected else (50, 50, 50))
            desc_rect = desc_text.get_rect(center=(button_rect.centerx, button_rect.centery + 18))
            self.screen.blit(desc_text, desc_rect)
        
        # Bottone START con effetto
        is_start_hovered = self.start_button.collidepoint(mouse_pos)
        
        if is_start_hovered:
            # Glow effect
            glow_rect = self.start_button.inflate(15, 15)
            pygame.draw.rect(self.screen, (80, 220, 80), glow_rect, border_radius=15)
        
        start_color = (100, 220, 100) if is_start_hovered else (60, 160, 60)
        pygame.draw.rect(self.screen, start_color, self.start_button, border_radius=15)
        pygame.draw.rect(self.screen, (150, 255, 150), self.start_button, 5, border_radius=15)
        
        start_text = self.big_font.render("▶ INIZIA PARTITA", True, (255, 255, 255))
        start_text_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_text_rect)
        
        # Istruzioni in fondo con box
        instructions_y = HEIGHT - 150
        inst_box = pygame.Rect(WIDTH // 2 - 400, instructions_y - 10, 800, 140)
        pygame.draw.rect(self.screen, (40, 40, 50), inst_box, border_radius=10)
        pygame.draw.rect(self.screen, (80, 80, 100), inst_box, 2, border_radius=10)
        
        instructions = [
            "🎮 Controlli:",
            "WASD - Movimento  |  Click Sinistro - Attacco Pancia",
            "",
            "🎯 Obiettivo: Salta sul colore giusto e butta giù gli avversari!",
            "⚠️ Non cadere dalle piattaforme quando scompaiono!"
        ]
        
        for i, text in enumerate(instructions):
            if i == 0:
                surf = self.small_font.render(text, True, (255, 215, 0))
            else:
                surf = self.small_font.render(text, True, (200, 200, 200))
            rect = surf.get_rect(center=(WIDTH // 2, instructions_y + 20 + i * 28))
            self.screen.blit(surf, rect)
    
    def draw_game(self):
        """Disegna il gioco in corso"""
        # Disegna piattaforme
        for platform in self.platforms:
            platform.draw(self.screen)
        
        # Disegna lottatori
        for wrestler in self.wrestlers:
            wrestler.draw(self.screen)
        
        # HUD superiore
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (0, 0, WIDTH, 100))
        
        # Round number
        round_text = self.medium_font.render(f"ROUND {self.round_number}", True, (255, 255, 255))
        self.screen.blit(round_text, (20, 20))
        
        # Difficoltà
        diff_names = {Difficulty.EASY: "FACILE", Difficulty.MEDIUM: "MEDIO", Difficulty.HARD: "DIFFICILE"}
        diff_colors = {Difficulty.EASY: (100, 255, 100), Difficulty.MEDIUM: (255, 200, 100), Difficulty.HARD: (255, 100, 100)}
        diff_text = self.small_font.render(diff_names[self.difficulty], True, diff_colors[self.difficulty])
        self.screen.blit(diff_text, (20, 60))
        
        # Colore target
        if self.state == GameState.PLAYING:
            target_text = self.big_font.render(f"COLORE: {self.target_color}", True, COLORS[self.target_color])
            target_rect = target_text.get_rect(center=(WIDTH // 2, 40))
            
            box_rect = target_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, COLORS[self.target_color], box_rect, 5, border_radius=10)
            
            self.screen.blit(target_text, target_rect)
            
            # Countdown
            if self.countdown > 0:
                countdown_text = self.big_font.render(f"{int(self.countdown) + 1}", True, (255, 200, 0))
                countdown_rect = countdown_text.get_rect(center=(WIDTH // 2, 90))
                self.screen.blit(countdown_text, countdown_rect)
        
        # Giocatori vivi
        alive_count = sum(1 for w in self.wrestlers if w.alive)
        alive_text = self.medium_font.render(f"Vivi: {alive_count}/8", True, (0, 255, 0))
        self.screen.blit(alive_text, (WIDTH - 180, 20))
        
        # Lista giocatori vivi
        y_offset = 60
        for wrestler in self.wrestlers:
            if wrestler.alive:
                prefix = "👑 " if not wrestler.is_bot else "🤖 "
                status_text = self.small_font.render(f"{prefix}{wrestler.name}", True, wrestler.body_color)
                self.screen.blit(status_text, (WIDTH - 180, y_offset))
                y_offset += 25
    
    def draw_winner(self):
        """Disegna la schermata del vincitore"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Testo vincitore
        if self.winner:
            winner_text = self.title_font.render(f"🏆 {self.winner.name} VINCE! 🏆", True, (255, 215, 0))
            
            # Disegna il vincitore al centro
            self.winner.x = WIDTH // 2
            self.winner.y = HEIGHT // 2 + 80
            self.winner.draw(self.screen)
        else:
            winner_text = self.title_font.render("PAREGGIO!", True, (255, 255, 255))
        
        winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(winner_text, winner_rect)
        
        # Statistiche
        rounds_text = self.medium_font.render(f"Round giocati: {self.round_number}", True, (255, 255, 255))
        rounds_rect = rounds_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.screen.blit(rounds_text, rounds_rect)
        
        diff_name = {Difficulty.EASY: "Facile", Difficulty.MEDIUM: "Medio", Difficulty.HARD: "Difficile"}
        diff_text = self.medium_font.render(f"Difficoltà: {diff_name[self.difficulty]}", True, (200, 200, 200))
        diff_rect = diff_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(diff_text, diff_rect)
        
        # Istruzioni
        restart_text = self.small_font.render("Premi SPAZIO per giocare ancora", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        self.screen.blit(restart_text, restart_rect)
    
    def handle_event(self, event):
        """Gestisce gli eventi"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == GameState.WINNER:
                    self.state = GameState.MENU
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.state == GameState.MENU:
                    # Click su difficoltà
                    for diff, button_rect in self.difficulty_buttons.items():
                        if button_rect.collidepoint(mouse_pos):
                            self.difficulty = diff
                    
                    # Click su START
                    if self.start_button.collidepoint(mouse_pos):
                        self.setup_game()
                        self.start_round()
                
                # Click su RESTART durante il gioco
                elif self.state in [GameState.PLAYING, GameState.WAITING]:
                    if self.restart_button.collidepoint(mouse_pos):
                        self.state = GameState.MENU
    
    def run(self):
        """Loop principale del gioco"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_event(event)
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()

