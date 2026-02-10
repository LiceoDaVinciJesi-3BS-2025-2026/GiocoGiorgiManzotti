import pygame   
import random

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
pygame.display.set_caption("Rettangolo che si muove con nemici a caso") 

# crea un nuovo (tipo di) evento (da gestire nel for degli eventi sotto)
# che verrà scatenato ogni TOT ms
ADD_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_ENEMY, 1000)

# l'elenco dei nemici
enemies = []

# info utili per il rettangolo giocatore:
# (x,y) la posizione, (w,h) la dimensione, speed... indovina!!!!!
x = SCREEN_WIDTH // 2
y = SCREEN_HEIGHT // 2
w = 40
h = 20
speed = 4

running = True

while running: 
    pygame.time.delay(10) 

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == ADD_ENEMY:
            posx = random.randint(0,SCREEN_WIDTH - 20)
            posy = random.randint(0,SCREEN_HEIGHT - 20)
            enemies.append( (posx,posy) )

    keys = pygame.key.get_pressed() 
    if keys[pygame.K_LEFT] and x > 0: 
        w,h = 40,20
        x -= speed 
    if keys[pygame.K_RIGHT] and x < SCREEN_WIDTH - w: 
        w,h = 40,20
        x += speed 
    if keys[pygame.K_UP] and y > 0: 
        w,h = 20,40
        y -= speed 
    if keys[pygame.K_DOWN] and y < SCREEN_HEIGHT - h: 
        w,h = 20,40
        y += speed 

    screen.fill("black") 
    player = pygame.draw.rect(screen, "red", (x, y, w, h)) 

    # in questo caso i nemici sono fermi: sono ostacoli
    for posx,posy in enemies:
        # en è il rettangolo disegnato 
        en = pygame.draw.rect(screen, "white", (posx, posy, 20, 20)) 

        # se questo rettangolo "collide" con il punto (x,y) ove si trova il giocatore...
        if player.colliderect(en):
            print("HAI PERSO!")
            running = False

    pygame.display.flip()  

pygame.quit()