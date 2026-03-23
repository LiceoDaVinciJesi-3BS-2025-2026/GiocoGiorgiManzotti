import pygame  
import math    
import random


LARGHEZZA = 1400  
ALTEZZA = 800     

FPS = 60 
COLORI = {
    'ROSSO': (255, 0, 0),      # Rosso puro
    'BIANCO': (255, 255, 255), # Bianco
    'GIALLO': (255, 255, 0),   # Giallo
    'BLU': (0, 0, 255),        # Blu puro
    'ARANCIONE': (255, 165, 0),# Arancione
    'VERDE': (0, 255, 0)       # Verde puro
}


NOMI_COLORI = ['ROSSO', 'BIANCO', 'GIALLO', 'BLU', 'ARANCIONE', 'VERDE']

stato_gioco = "MENU"
difficolta = "FACILE"

piattaforme = []  
lottatori = []    


colore_target = None           
conto_alla_rovescia = 3.0   
numero_round = 1              
vincitore = None               
piattaforme_scomparse = False 
