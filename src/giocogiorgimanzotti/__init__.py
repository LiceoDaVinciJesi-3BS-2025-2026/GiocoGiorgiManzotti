def main() -> None:
    print("Hello from giocogiorgimanzotti!")
    
import pygame
import math
import random
from enum import Enum

# Costanti
WIDTH, HEIGHT = 1280, 720
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
        self.disappear_progress = 0  # 0 = visibile, 1 = scomparsa
        
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
        
        # Calcola l'alpha per l'effetto di scomparsa
        if not self.active:
            # Piattaforma che sta scomparendo
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
        
        # Disegna la piattaforma
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
    
    def __init__(self, x, y, body_color, name, is_bot=False):
        # Posizione
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        
        # Fisica
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.6
        self.max_speed = 4.0
        self.friction = 0.85
        
        # Dimensioni
        self.radius = 20
        self.head_radius = 12
        
        # Aspetto
        self.body_color = body_color
        self.skin_color = (255, 220, 177)
        self.belt_color = (50, 50, 50)
        
        # Info
        self.name = name
        self.is_bot = is_bot
        self.alive = True
        
        # AI per i bot
        self.target_platform = None
        self.ai_timer = 0
        
    def update(self, keys=None, platforms=None, target_color=None):
        """Aggiorna lo stato del lottatore"""
        if not self.alive:
            # Cade verso il basso
            self.y += 5
            return
        
        # Controlli
        if self.is_bot:
            self.update_ai(platforms, target_color)
        elif keys:
            # Controlli umani (WASD)
            if keys[pygame.K_a]:
                self.velocity_x -= self.acceleration
            if keys[pygame.K_d]:
                self.velocity_x += self.acceleration
            if keys[pygame.K_w]:
                self.velocity_y -= self.acceleration
            if keys[pygame.K_s]:
                self.velocity_y += self.acceleration
        
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
    
    def update_ai(self, platforms, target_color):
        """AI per i bot"""
        if not platforms or not target_color:
            return
        
        # Ogni secondo, sceglie una nuova piattaforma target
        self.ai_timer += 1
        if self.ai_timer > 60 or not self.target_platform:
            # Trova piattaforme con il colore target
            valid_platforms = [p for p in platforms 
                             if p.color_name == target_color and p.active]
            
            if valid_platforms:
                # Sceglie la piattaforma più vicina o una casuale
                if random.random() < 0.7:  # 70% va alla più vicina
                    self.target_platform = min(valid_platforms, 
                        key=lambda p: math.sqrt((p.get_center()[0] - self.x)**2 + 
                                               (p.get_center()[1] - self.y)**2))
                else:
                    self.target_platform = random.choice(valid_platforms)
                
                self.ai_timer = 0
        
        # Muovi verso la piattaforma target
        if self.target_platform and self.target_platform.active:
            tx, ty = self.target_platform.get_center()
            
            dx = tx - self.x
            dy = ty - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 5:
                # Muovi verso il target
                self.velocity_x += (dx / distance) * self.acceleration * 0.8
                self.velocity_y += (dy / distance) * self.acceleration * 0.8
    
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
    
    def draw(self, screen):
        """Disegna il lottatore"""
        if not self.alive and self.y > HEIGHT + 50:
            return
        
        pos = (int(self.x), int(self.y))
        
        # Ombra
        if self.alive:
            pygame.draw.ellipse(screen, (0, 0, 0, 100), 
                              (pos[0] - self.radius, pos[1] + 5, 
                               self.radius * 2, self.radius))
        
        # Corpo
        pygame.draw.circle(screen, self.body_color, pos, self.radius)
        pygame.draw.circle(screen, (0, 0, 0), pos, self.radius, 2)
        
        # Cintura
        pygame.draw.rect(screen, self.belt_color, 
                        (pos[0] - self.radius, pos[1] - 3, 
                         self.radius * 2, 6))
        
        # Testa
        head_y = int(self.y - self.radius + 8)
        pygame.draw.circle(screen, self.skin_color, 
                         (pos[0], head_y), self.head_radius)
        pygame.draw.circle(screen, (0, 0, 0), 
                         (pos[0], head_y), self.head_radius, 2)
        
        # Capelli
        hair_y = head_y - self.head_radius + 3
        pygame.draw.circle(screen, (20, 20, 20), 
                         (pos[0], hair_y), 4)
        
        # Occhi
        eye_offset = 4
        eye_y = head_y
        pygame.draw.circle(screen, (255, 255, 255), 
                         (pos[0] - eye_offset, eye_y), 2)
        pygame.draw.circle(screen, (0, 0, 0), 
                         (pos[0] - eye_offset, eye_y), 1)
        pygame.draw.circle(screen, (255, 255, 255), 
                         (pos[0] + eye_offset, eye_y), 2)
        pygame.draw.circle(screen, (0, 0, 0), 
                         (pos[0] + eye_offset, eye_y), 1)
        
        # Nome
        if self.alive:
            font = pygame.font.Font(None, 20)
            name_surface = font.render(self.name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(center=(pos[0], pos[1] - self.radius - 10))
            
            # Sfondo per il nome
            bg_rect = name_rect.inflate(10, 4)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=3)
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
        
        # Font
        self.title_font = pygame.font.Font(None, 80)
        self.big_font = pygame.font.Font(None, 60)
        self.medium_font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 30)
        
        self.setup_game()
    
    def setup_game(self):
        """Inizializza il gioco"""
        self.platforms = []
        self.wrestlers = []
        self.round_number = 1
        self.winner = None
        
        # Crea le piattaforme (griglia 6x5)
        self.create_platforms()
        
        # Crea i giocatori
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
        names = ["TU", "BOT 1", "BOT 2", "BOT 3"]
        
        positions = [
            (200, 200),
            (WIDTH - 200, 200),
            (200, HEIGHT - 200),
            (WIDTH - 200, HEIGHT - 200)
        ]
        
        for i in range(4):
            wrestler = SumoWrestler(
                positions[i][0], 
                positions[i][1], 
                colors[i], 
                names[i],
                is_bot=(i > 0)
            )
            self.wrestlers.append(wrestler)
    
    def create_platforms(self):
        """Crea la griglia di piattaforme con colori casuali"""
        self.platforms = []
        
        # Configurazione griglia
        rows = 5
        cols = 6
        platform_width = 100
        platform_height = 80
        spacing = 10
        
        # Calcola offset per centrare
        grid_width = cols * platform_width + (cols - 1) * spacing
        grid_height = rows * platform_height + (rows - 1) * spacing
        offset_x = (WIDTH - grid_width) // 2
        offset_y = (HEIGHT - grid_height) // 2 + 50
        
        # Crea piattaforme
        for row in range(rows):
            for col in range(cols):
                x = offset_x + col * (platform_width + spacing)
                y = offset_y + row * (platform_height + spacing)
                
                color_name = random.choice(COLOR_NAMES)
                platform = Platform(x, y, platform_width, platform_height, color_name)
                self.platforms.append(platform)
    
    def start_round(self):
        """Inizia un nuovo round"""
        self.state = GameState.PLAYING
        self.countdown = 3.0
        
        # Sceglie un colore target casuale
        self.target_color = random.choice(COLOR_NAMES)
        
        # Reset piattaforme
        for platform in self.platforms:
            platform.active = True
            platform.disappear_progress = 0
    
    def update(self):
        """Aggiorna la logica del gioco"""
        if self.state == GameState.PLAYING:
            # Countdown
            self.countdown -= 1/60
            
            # Aggiorna lottatori
            keys = pygame.key.get_pressed()
            for wrestler in self.wrestlers:
                if wrestler.alive:
                    wrestler.update(
                        keys if not wrestler.is_bot else None,
                        self.platforms,
                        self.target_color
                    )
            
            # Quando il countdown finisce
            if self.countdown <= 0:
                # Fa scomparire le piattaforme sbagliate
                for platform in self.platforms:
                    if platform.color_name != self.target_color:
                        platform.start_disappear()
                
                # Controlla quali lottatori sono su piattaforme sbagliate
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
                self.countdown = 2.0  # Tempo di attesa prima del prossimo round
            
            # Aggiorna piattaforme
            for platform in self.platforms:
                platform.update()
        
        elif self.state == GameState.WAITING:
            # Countdown per il prossimo round
            self.countdown -= 1/60
            
            # Aggiorna lottatori morti (cadono)
            for wrestler in self.wrestlers:
                wrestler.update()
            
            # Aggiorna piattaforme
            for platform in self.platforms:
                platform.update()
            
            if self.countdown <= 0:
                # Conta i sopravvissuti
                alive_wrestlers = [w for w in self.wrestlers if w.alive]
                
                if len(alive_wrestlers) == 1:
                    # Abbiamo un vincitore!
                    self.winner = alive_wrestlers[0]
                    self.state = GameState.WINNER
                elif len(alive_wrestlers) == 0:
                    # Pareggio (raro)
                    self.state = GameState.WINNER
                else:
                    # Continua con un nuovo round
                    self.round_number += 1
                    self.create_platforms()  # Nuove piattaforme casuali
                    self.start_round()
    
    def draw(self):
        """Disegna tutto sullo schermo"""
        # Sfondo
        self.screen.fill((30, 30, 40))
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state in [GameState.PLAYING, GameState.WAITING]:
            self.draw_game()
        elif self.state == GameState.WINNER:
            self.draw_winner()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Disegna il menu iniziale"""
        # Titolo
        title = self.title_font.render("SUMO COLOR SURVIVAL", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        # Istruzioni
        instructions = [
            "Salta sulla piattaforma del colore giusto!",
            "Usa WASD per muoverti",
            "Batti i 3 bot per vincere!",
            "",
            "Premi SPAZIO per iniziare"
        ]
        
        for i, text in enumerate(instructions):
            surf = self.small_font.render(text, True, (200, 200, 200))
            rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
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
        # Sfondo HUD
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (0, 0, WIDTH, 100))
        
        # Round number
        round_text = self.medium_font.render(f"ROUND {self.round_number}", True, (255, 255, 255))
        self.screen.blit(round_text, (20, 20))
        
        # Colore target
        if self.state == GameState.PLAYING:
            target_text = self.big_font.render(f"COLORE: {self.target_color}", True, COLORS[self.target_color])
            target_rect = target_text.get_rect(center=(WIDTH // 2, 40))
            
            # Box intorno al colore
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
        alive_text = self.medium_font.render(f"Vivi: {alive_count}/4", True, (0, 255, 0))
        self.screen.blit(alive_text, (WIDTH - 180, 20))
    
    def draw_winner(self):
        """Disegna la schermata del vincitore"""
        # Sfondo scuro
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Testo vincitore
        if self.winner:
            winner_text = self.title_font.render(f"{self.winner.name} VINCE!", True, (255, 215, 0))
        else:
            winner_text = self.title_font.render("PAREGGIO!", True, (255, 255, 255))
        
        winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(winner_text, winner_rect)
        
        # Statistiche
        rounds_text = self.medium_font.render(f"Round giocati: {self.round_number}", True, (255, 255, 255))
        rounds_rect = rounds_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(rounds_text, rounds_rect)
        
        # Istruzioni
        restart_text = self.small_font.render("Premi SPAZIO per giocare ancora", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        self.screen.blit(restart_text, restart_rect)
    
    def handle_event(self, event):
        """Gestisce gli eventi"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == GameState.MENU:
                    self.start_round()
                elif self.state == GameState.WINNER:
                    self.setup_game()
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
    