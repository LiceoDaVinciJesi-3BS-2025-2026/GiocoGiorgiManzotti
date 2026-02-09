import pygame
import math
import random
from enum import Enum

# Costanti
WIDTH, HEIGHT = 1280, 720
FPS = 60

# Colori (5 quadrati per ogni colore)
MAIN_COLORS = {
    'ROSSO': (255, 50, 50),
    'BLU': (50, 150, 255),
    'GIALLO': (255, 255, 50),
    'VERDE': (50, 255, 100),
    'ARANCIONE': (255, 150, 50),
    'VIOLA': (200, 100, 255),
    'ROSA': (255, 150, 200),
    'CIANO': (100, 255, 255),
    'BIANCO': (255, 255, 255),
    'MARRONE': (180, 120, 80)
}

COLORS = MAIN_COLORS
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
    DIFFICULTY_SELECT = 5


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
        self.warning = False
        
    def start_disappear(self, speed=0.05):
        """Inizia l'animazione di scomparsa"""
        self.active = False
        self.disappear_speed = speed
    
    def update(self):
        """Aggiorna l'animazione"""
        if not self.active and self.disappear_progress < 1:
            self.disappear_progress += self.disappear_speed
    
    def draw(self, screen):
        """Disegna la piattaforma"""
        if self.disappear_progress >= 1:
            return
        
        # Effetto lampeggiante
        if not self.active and self.disappear_progress < 0.5:
            blink = int(pygame.time.get_ticks() / 200) % 2
            if blink == 0:
                color = self.color
            else:
                color = (min(self.color[0] + 100, 255), 
                        min(self.color[1] + 100, 255), 
                        min(self.color[2] + 100, 255))
        else:
            color = self.color
        
        if not self.active:
            scale = 1 - self.disappear_progress
            offset = self.disappear_progress * 25
            rect = pygame.Rect(
                self.x + offset,
                self.y + offset,
                self.width * scale,
                self.height * scale
            )
        else:
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 3)
        
        # Effetto di selezione
        if self.active and hasattr(self, 'is_target_color') and self.is_target_color:
            pygame.draw.rect(screen, (255, 255, 200), rect, 4)
    
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
    
    def __init__(self, x, y, body_color, name, is_bot=False):
        # Posizione
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        
        # Fisica
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.8
        self.max_speed = 5.0
        self.friction = 0.88
        
        # Combattimento
        self.attack_cooldown = 0
        self.attack_power = 12
        self.attack_range = 50
        self.is_attacking = False
        self.attack_timer = 0
        
        # Dimensioni
        self.radius = 24
        self.head_radius = 16
        
        # Aspetto
        self.body_color = body_color
        self.skin_color = (255, 220, 177)
        self.belt_color = (50, 50, 50)
        
        # Info
        self.name = name
        self.is_bot = is_bot
        self.alive = True
        self.is_stunned = False
        self.stun_timer = 0
        
        # AI per i bot
        self.target_platform = None
        self.target_wrestler = None
        self.ai_timer = 0
        self.aggression = 0.4
        self.attack_chance = 0.15
        
        # Timer per controlli di sopravvivenza
        self.off_platform_timer = 0
        
    def update(self, keys=None, platforms=None, target_color=None, wrestlers=None, mouse_pos=None, mouse_click=False, difficulty=Difficulty.EASY):
        """Aggiorna lo stato del lottatore"""
        if not self.alive:
            self.y += 10
            if self.y > HEIGHT + 100:
                return
            return
        
        # Aggiorna cooldown attacco
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Aggiorna stun
        if self.is_stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.is_stunned = False
            else:
                self.velocity_x *= 0.85
                self.velocity_y *= 0.85
                self.x += self.velocity_x
                self.y += self.velocity_y
                return
        
        # Controlli umani con FRECCE
        if not self.is_bot and keys:
            if keys[pygame.K_LEFT]:
                self.velocity_x -= self.acceleration
            if keys[pygame.K_RIGHT]:
                self.velocity_x += self.acceleration
            if keys[pygame.K_UP]:
                self.velocity_y -= self.acceleration
            if keys[pygame.K_DOWN]:
                self.velocity_y += self.acceleration
            
            # Attacco con click sinistro
            if mouse_click and self.attack_cooldown <= 0:
                self.attack(mouse_pos, wrestlers)
        
        # AI per i bot
        elif self.is_bot and platforms and target_color and wrestlers:
            self.update_ai(platforms, target_color, wrestlers, difficulty)
        
        # Limita velocità
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
        
        # Limiti schermo - se esce, muore!
        if (self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT):
            self.alive = False
            return
        
        # Controlla se è su una piattaforma corretta
        if target_color:
            on_correct_platform = False
            for platform in platforms:
                if platform.active and platform.color_name == target_color:
                    if platform.contains_point(self.x, self.y):
                        on_correct_platform = True
                        self.off_platform_timer = 0
                        break
            
            # Se non è su una piattaforma corretta, inizia il timer
            if not on_correct_platform:
                self.off_platform_timer += 1
                # Dopo 30 frame (0.5 secondi) muore
                if self.off_platform_timer > 30:
                    self.alive = False
                    return
            else:
                self.off_platform_timer = 0
        
        # Aggiorna animazione attacco
        if self.is_attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.is_attacking = False
    
    def update_ai(self, platforms, target_color, wrestlers, difficulty):
        """AI avanzata per i bot"""
        self.ai_timer += 1
        
        # Aggressione in base alla difficoltà
        if difficulty == Difficulty.MEDIUM:
            self.aggression = 0.7
            self.attack_chance = 0.3
            self.attack_power = 14
        elif difficulty == Difficulty.HARD:
            self.aggression = 1.0
            self.attack_chance = 0.6
            self.attack_power = 16
            self.max_speed = 6.0
        
        # Ogni secondo, decide cosa fare
        if self.ai_timer > 45 or not self.target_platform:
            # Trova nemici vicini
            nearby_enemies = []
            for wrestler in wrestlers:
                if wrestler != self and wrestler.alive:
                    distance = math.sqrt((wrestler.x - self.x)**2 + (wrestler.y - self.y)**2)
                    if distance < 300:
                        nearby_enemies.append((wrestler, distance))
            
            # Decidi se attaccare o andare sulla piattaforma
            if nearby_enemies and random.random() < self.aggression:
                nearby_enemies.sort(key=lambda x: x[1])
                self.target_wrestler = nearby_enemies[0][0]
                self.target_platform = None
            else:
                # Vai sulla piattaforma target
                valid_platforms = [p for p in platforms 
                                 if p.color_name == target_color and p.active]
                
                if valid_platforms:
                    if random.random() < 0.8:
                        self.target_platform = min(valid_platforms, 
                            key=lambda p: math.sqrt((p.get_center()[0] - self.x)**2 + 
                                                   (p.get_center()[1] - self.y)**2))
                    else:
                        self.target_platform = random.choice(valid_platforms)
                    self.target_wrestler = None
            
            self.ai_timer = 0
        
        # Esegue l'azione decisa
        if self.target_wrestler and self.target_wrestler.alive:
            dx = self.target_wrestler.x - self.x
            dy = self.target_wrestler.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.attack_range and self.attack_cooldown <= 0 and random.random() < self.attack_chance:
                attack_pos = (self.target_wrestler.x, self.target_wrestler.y)
                self.attack(attack_pos, wrestlers)
            elif distance > 50:
                self.velocity_x += (dx / distance) * self.acceleration * 1.0
                self.velocity_y += (dy / distance) * self.acceleration * 1.0
        
        elif self.target_platform and self.target_platform.active:
            tx, ty = self.target_platform.get_center()
            dx = tx - self.x
            dy = ty - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 15:
                self.velocity_x += (dx / distance) * self.acceleration * 1.0
                self.velocity_y += (dy / distance) * self.acceleration * 1.0
    
    def attack(self, target_pos, wrestlers):
        """Esegue un attacco con knockback migliorato"""
        if self.attack_cooldown > 0:
            return
        
        self.is_attacking = True
        self.attack_timer = 20
        self.attack_cooldown = 20
        
        # Calcola direzione dell'attacco
        attack_angle = math.atan2(target_pos[1] - self.y, target_pos[0] - self.x)
        
        # Cerca bersagli nell'area di attacco
        for wrestler in wrestlers:
            if wrestler != self and wrestler.alive:
                distance = math.sqrt((wrestler.x - self.x)**2 + (wrestler.y - self.y)**2)
                
                if distance < self.attack_range:
                    dx = wrestler.x - self.x
                    dy = wrestler.y - self.y
                    dist = max(1, math.sqrt(dx**2 + dy**2))
                    
                    knockback_power = self.attack_power * (2.0 - distance/self.attack_range)
                    
                    wrestler.velocity_x += (dx / dist) * knockback_power * 1.5
                    wrestler.velocity_y += (dy / dist) * knockback_power * 1.5
                    
                    wrestler.is_stunned = True
                    wrestler.stun_timer = 25
    
    def check_on_platform(self, platforms):
        """Controlla se il lottatore è su una piattaforma"""
        for platform in platforms:
            if platform.contains_point(self.x, self.y):
                return True
        return False
    
    def reset_position(self):
        """Resetta la posizione iniziale"""
        self.x = self.start_x
        self.y = self.start_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.alive = True
        self.is_stunned = False
        self.stun_timer = 0
        self.off_platform_timer = 0
    
    def draw(self, screen):
        """Disegna il lottatore"""
        if not self.alive and self.y > HEIGHT + 50:
            return
        
        pos = (int(self.x), int(self.y))
        
        # Ombra
        if self.alive:
            shadow_rect = pygame.Rect(pos[0] - self.radius, pos[1] + 10, 
                                     self.radius * 2, self.radius)
            pygame.draw.ellipse(screen, (0, 0, 0, 120), shadow_rect)
        
        # Corpo
        pygame.draw.circle(screen, self.body_color, pos, self.radius)
        pygame.draw.circle(screen, (0, 0, 0), pos, self.radius, 4)
        
        # Effetto attacco
        if self.is_attacking and self.attack_timer > 0:
            attack_radius = self.radius + 25 + (20 - self.attack_timer)
            for i in range(3):
                pygame.draw.circle(screen, (255, 255, 100, 200 - i*50), 
                                 pos, attack_radius - i*5, 3 - i)
        
        # Effetto stun
        if self.is_stunned:
            for i in range(3):
                radius_offset = 5 + i * 3
                alpha = 180 - i * 40
                stun_surface = pygame.Surface((self.radius*2 + radius_offset*2, 
                                             self.radius*2 + radius_offset*2), 
                                            pygame.SRCALPHA)
                pygame.draw.circle(stun_surface, (255, 100, 100, alpha), 
                                 (self.radius + radius_offset, self.radius + radius_offset), 
                                 self.radius + radius_offset, 3)
                screen.blit(stun_surface, (pos[0] - self.radius - radius_offset, 
                                         pos[1] - self.radius - radius_offset))
        
        # Cintura
        pygame.draw.rect(screen, self.belt_color, 
                        (pos[0] - self.radius, pos[1] - 5, 
                         self.radius * 2, 10))
        pygame.draw.rect(screen, (200, 200, 200), 
                        (pos[0] - self.radius, pos[1] - 5, 
                         self.radius * 2, 10), 2)
        
        # Testa
        head_y = int(self.y - self.radius + 12)
        pygame.draw.circle(screen, self.skin_color, 
                         (pos[0], head_y), self.head_radius)
        pygame.draw.circle(screen, (0, 0, 0), 
                         (pos[0], head_y), self.head_radius, 3)
        
        # Capelli
        hair_y = head_y - self.head_radius + 5
        pygame.draw.ellipse(screen, (30, 30, 30), 
                          (pos[0] - 8, hair_y - 3, 16, 10))
        
        # Occhi
        eye_offset = 6
        eye_y = head_y
        
        if self.is_stunned:
            # Occhi a spirale
            for i in range(2):
                side = -1 if i == 0 else 1
                center_x = pos[0] + side * eye_offset
                for j in range(3):
                    angle = pygame.time.get_ticks() * 0.01 + j * 1.0
                    spiral_x = center_x + math.cos(angle) * (3 - j)
                    spiral_y = eye_y + math.sin(angle) * (3 - j)
                    pygame.draw.circle(screen, (0, 0, 0), (int(spiral_x), int(spiral_y)), 1)
        else:
            # Occhi normali
            for i in range(2):
                side = -1 if i == 0 else 1
                center_x = pos[0] + side * eye_offset
                
                pygame.draw.circle(screen, (255, 255, 255), (center_x, eye_y), 4)
                pygame.draw.circle(screen, (0, 0, 0), (center_x, eye_y), 4, 1)
                
                look_x = self.velocity_x * 0.5
                look_y = self.velocity_y * 0.5
                pupil_offset = max(-1.5, min(1.5, look_x if i == 0 else -look_x))
                pygame.draw.circle(screen, (0, 0, 0), 
                                 (int(center_x + pupil_offset), int(eye_y + look_y * 0.3)), 2)
        
        # Bocca
        mouth_y = head_y + 8
        if self.is_attacking:
            pygame.draw.ellipse(screen, (180, 80, 80), 
                              (pos[0] - 8, mouth_y - 5, 16, 10))
            pygame.draw.ellipse(screen, (0, 0, 0), 
                              (pos[0] - 8, mouth_y - 5, 16, 10), 2)
        else:
            mouth_happy = 0.5 + math.sin(pygame.time.get_ticks() * 0.005) * 0.3
            start_angle = math.pi * (0.5 - mouth_happy * 0.5)
            end_angle = math.pi * (0.5 + mouth_happy * 0.5)
            pygame.draw.arc(screen, (0, 0, 0), 
                          (pos[0] - 6, mouth_y - 3, 12, 8), 
                          start_angle, end_angle, 3)
        
        # Indicatore timer piattaforma
        if hasattr(self, 'off_platform_timer') and self.off_platform_timer > 0:
            timer_width = 40
            timer_height = 6
            timer_x = pos[0] - timer_width // 2
            timer_y = pos[1] - self.radius - 25
            
            pygame.draw.rect(screen, (100, 100, 100), 
                           (timer_x, timer_y, timer_width, timer_height), 
                           border_radius=2)
            
            fill_width = max(0, timer_width * (1 - self.off_platform_timer / 30))
            if fill_width > 0:
                red_value = 255 - int(255 * (self.off_platform_timer / 30))
                pygame.draw.rect(screen, (255, red_value, red_value), 
                               (timer_x, timer_y, fill_width, timer_height), 
                               border_radius=2)
        
        # Nome
        if self.alive:
            font = pygame.font.Font(None, 24)
            name_surface = font.render(self.name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(center=(pos[0], pos[1] - self.radius - 40))
            
            bg_rect = name_rect.inflate(15, 8)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=5)
            pygame.draw.rect(screen, self.body_color, bg_rect, 3, border_radius=5)
            screen.blit(name_surface, name_rect)


class Game:
    """Classe principale del gioco"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sumo Color Survival")
        self.clock = pygame.time.Clock()
        
        # Stato del gioco
        self.state = GameState.MENU
        self.platforms = []
        self.wrestlers = []
        self.target_color = None
        self.countdown = 3.0
        self.round_number = 1
        self.winner = None
        self.difficulty = Difficulty.EASY
        
        # Font
        self.title_font = pygame.font.Font(None, 80)
        self.big_font = pygame.font.Font(None, 60)
        self.medium_font = pygame.font.Font(None, 45)
        self.small_font = pygame.font.Font(None, 30)
        
        self.setup_game()
    
    def setup_game(self):
        """Inizializza il gioco"""
        self.platforms = []
        self.wrestlers = []
        self.round_number = 1
        self.winner = None
        
        # Crea la scacchiera
        self.create_platforms()
        
        # Crea 8 giocatori
        colors = [
            (255, 50, 50),    # Rosso
            (50, 150, 255),   # Blu
            (255, 255, 50),   # Giallo
            (50, 255, 100),   # Verde
            (255, 150, 50),   # Arancione
            (200, 100, 255),  # Viola
            (255, 150, 200),  # Rosa
            (100, 255, 255)   # Ciano
        ]
        
        names = ["TU", "BOT 1", "BOT 2", "BOT 3", "BOT 4", "BOT 5", "BOT 6", "BOT 7"]
        
        # Posizioni in cerchio
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        radius = 280
        
        for i in range(8):
            angle = (2 * math.pi * i) / 8
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            wrestler = SumoWrestler(x, y, colors[i], names[i], is_bot=(i > 0))
            self.wrestlers.append(wrestler)
    
    def create_platforms(self):
        """Crea la scacchiera con 5 piattaforme sparse per ogni colore"""
        self.platforms = []
        
        # 10 colori × 5 piattaforme = 50 piattaforme totali
        colors_to_use = COLOR_NAMES[:10]
        platform_width = 80
        platform_height = 65
        spacing = 6
        
        # Griglia 10×5
        cols = 10
        rows = 5
        grid_width = cols * platform_width + (cols - 1) * spacing
        grid_height = rows * platform_height + (rows - 1) * spacing
        offset_x = (WIDTH - grid_width) // 2
        offset_y = (HEIGHT - grid_height) // 2 + 20
        
        # Crea tutte le posizioni
        grid_positions = []
        for row in range(rows):
            for col in range(cols):
                x = offset_x + col * (platform_width + spacing)
                y = offset_y + row * (platform_height + spacing)
                grid_positions.append((x, y, col, row))
        
        # Mescola le posizioni
        random.shuffle(grid_positions)
        
        # Distribuisci i colori
        color_distribution = {}
        for color in colors_to_use:
            color_distribution[color] = 5
        
        position_index = 0
        for color, count in color_distribution.items():
            for _ in range(count):
                if position_index < len(grid_positions):
                    x, y, col, row = grid_positions[position_index]
                    platform = Platform(x, y, platform_width, platform_height, color)
                    self.platforms.append(platform)
                    position_index += 1
    
    def start_round(self):
        """Inizia un nuovo round"""
        self.state = GameState.PLAYING
        self.countdown = 3.0
        
        self.target_color = random.choice(COLOR_NAMES[:8])
        
        # Reset piattaforme
        for platform in self.platforms:
            platform.active = True
            platform.disappear_progress = 0
            platform.is_target_color = (platform.color_name == self.target_color)
        
        # Reset posizioni
        for wrestler in self.wrestlers:
            if wrestler.alive:
                wrestler.reset_position()
    
    def update(self):
        """Aggiorna la logica del gioco"""
        if self.state == GameState.PLAYING:
            self.countdown -= 1/60
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()[0]
            
            keys = pygame.key.get_pressed()
            for wrestler in self.wrestlers:
                if wrestler.alive:
                    wrestler.update(
                        keys if not wrestler.is_bot else None,
                        self.platforms,
                        self.target_color,
                        [w for w in self.wrestlers if w != wrestler and w.alive],
                        mouse_pos,
                        mouse_click,
                        self.difficulty
                    )
            
            if self.countdown <= 0:
                disappear_speed = 0.04
                if self.difficulty == Difficulty.MEDIUM:
                    disappear_speed = 0.07
                elif self.difficulty == Difficulty.HARD:
                    disappear_speed = 0.10
                
                for platform in self.platforms:
                    if platform.color_name != self.target_color:
                        platform.start_disappear(disappear_speed)
                
                self.state = GameState.WAITING
                self.countdown = 1.5
            
            for platform in self.platforms:
                platform.update()
        
        elif self.state == GameState.WAITING:
            self.countdown -= 1/60
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()[0]
            keys = pygame.key.get_pressed()
            
            for wrestler in self.wrestlers:
                if wrestler.alive:
                    wrestler.update(
                        keys if not wrestler.is_bot else None,
                        self.platforms,
                        self.target_color,
                        [w for w in self.wrestlers if w != wrestler and w.alive],
                        mouse_pos,
                        mouse_click,
                        self.difficulty
                    )
            
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
                    self.start_round()
    
    def draw(self):
        """Disegna tutto sullo schermo"""
        self.screen.fill((20, 20, 30))
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.draw_difficulty_select()
        elif self.state in [GameState.PLAYING, GameState.WAITING]:
            self.draw_game()
        elif self.state == GameState.WINNER:
            self.draw_winner()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Disegna il menu iniziale"""
        # Sfondo
        self.screen.fill((30, 30, 45))
        
        # Titolo
        title = self.title_font.render("SUMO COLOR SURVIVAL", True, (255, 255, 180))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title, title_rect)
        
        # Istruzioni
        instructions = [
            "• 8 GIOCATORI (Tu + 7 Bot)",
            "• 5 PIATTAFORME SPARSE per OGNI COLORE",
            "• STAI sul COLORE GIUSTO prima che scompaia",
            "• Se cadi o sei fuori dal colore → MUORI SUBITO!",
            "• SPINGI gli avversari con ATTACCHI",
            "",
            "CONTROLLI:",
            "  → FRECCE per muoverti",
            "  → CLICK SINISTRO per attaccare",
            "",
            "Premi SPAZIO per iniziare"
        ]
        
        for i, text in enumerate(instructions):
            y = HEIGHT // 2 + i * 30
            if "•" in text or "→" in text:
                color = (220, 240, 255)
                font = self.small_font
            elif "CONTROLLI:" in text:
                color = (255, 255, 150)
                font = pygame.font.Font(None, 32)
            elif "  " in text:
                color = (180, 200, 220)
                font = pygame.font.Font(None, 26)
            else:
                color = (200, 200, 200)
                font = self.small_font
            
            surf = font.render(text, True, color)
            rect = surf.get_rect(center=(WIDTH // 2, y))
            self.screen.blit(surf, rect)
    
    def draw_difficulty_select(self):
        """Disegna la selezione difficoltà"""
        self.screen.fill((20, 25, 40))
        
        title = self.big_font.render("SELEZIONA DIFFICOLTÀ", True, (255, 255, 180))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 6))
        self.screen.blit(title, title_rect)
        
        difficulties = [
            ("FACILE", (100, 255, 100)),
            ("MEDIO", (255, 255, 100)),
            ("DIFFICILE", (255, 100, 100))
        ]
        
        for i, (name, color) in enumerate(difficulties):
            y = HEIGHT // 3 + i * 120
            
            button_rect = pygame.Rect(WIDTH//2 - 150, y - 25, 300, 60)
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 3, border_radius=10)
            
            name_surf = self.medium_font.render(name, True, (0, 0, 0))
            name_rect = name_surf.get_rect(center=(WIDTH // 2, y))
            self.screen.blit(name_surf, name_rect)
        
        instr = self.small_font.render("Premi 1, 2 o 3 per selezionare", True, (200, 200, 255))
        instr_rect = instr.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(instr, instr_rect)
    
    def draw_game(self):
        """Disegna il gioco in corso"""
        # Disegna piattaforme
        for platform in self.platforms:
            platform.draw(self.screen)
        
        # Disegna lottatori
        for wrestler in self.wrestlers:
            wrestler.draw(self.screen)
        
        # HUD superiore
        hud_height = 100
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (0, 0, WIDTH, hud_height))
        
        # Round number
        round_text = self.medium_font.render(f"ROUND {self.round_number}", True, (255, 255, 200))
        self.screen.blit(round_text, (20, 20))
        
        # Colore target
        if self.state == GameState.PLAYING:
            target_text = self.big_font.render(f"COLORE: {self.target_color}", True, COLORS[self.target_color])
            target_rect = target_text.get_rect(center=(WIDTH // 2, 40))
            
            box_rect = target_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, COLORS[self.target_color], box_rect, 4, border_radius=10)
            
            self.screen.blit(target_text, target_rect)
            
            # Countdown
            if self.countdown > 0:
                countdown_text = self.big_font.render(f"{int(self.countdown) + 1}", True, (255, 200, 0))
                countdown_rect = countdown_text.get_rect(center=(WIDTH // 2, 80))
                self.screen.blit(countdown_text, countdown_rect)
        
        # Giocatori vivi
        alive_count = sum(1 for w in self.wrestlers if w.alive)
        alive_text = self.medium_font.render(f"VIVI: {alive_count}/8", True, 
                                           (100, 255, 100) if alive_count > 4 else 
                                           (255, 255, 100) if alive_count > 1 else 
                                           (255, 100, 100))
        self.screen.blit(alive_text, (WIDTH - 180, 20))
    
    def draw_winner(self):
        """Disegna la schermata del vincitore"""
        # Sfondo scuro
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.winner:
            winner_text = self.title_font.render(f"{self.winner.name} VINCE!", True, (255, 215, 0))
        else:
            winner_text = self.title_font.render("PAREGGIO!", True, (255, 255, 255))
        
        winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(winner_text, winner_rect)
        
        rounds_text = self.medium_font.render(f"Round giocati: {self.round_number}", True, (255, 255, 255))
        rounds_rect = rounds_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(rounds_text, rounds_rect)
        
        restart_text = self.small_font.render("Premi SPAZIO per giocare ancora", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        self.screen.blit(restart_text, restart_rect)
    
    def handle_event(self, event):
        """Gestisce gli eventi"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == GameState.MENU:
                    self.state = GameState.DIFFICULTY_SELECT
                elif self.state == GameState.WINNER:
                    self.setup_game()
                    self.state = GameState.MENU
            
            elif event.key in [pygame.K_1, pygame.K_KP1] and self.state == GameState.DIFFICULTY_SELECT:
                self.difficulty = Difficulty.EASY
                self.setup_game()
                self.start_round()
            
            elif event.key in [pygame.K_2, pygame.K_KP2] and self.state == GameState.DIFFICULTY_SELECT:
                self.difficulty = Difficulty.MEDIUM
                self.setup_game()
                self.start_round()
            
            elif event.key in [pygame.K_3, pygame.K_KP3] and self.state == GameState.DIFFICULTY_SELECT:
                self.difficulty = Difficulty.HARD
                self.setup_game()
                self.start_round()
    
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