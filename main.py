import pygame
import os
import random
os.environ['SDL_AUDIODRIVER'] = 'dsp'
from menu import Menu



#Set display window
WIDTH = 800
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
backgroundColor = (200, 200, 200)
pygame.display.set_caption("Speedopoly")

from classes import Dice, Event, Player, Tile, PlayerTokenImage



#Establish game clock
clock = pygame.time.Clock()

#Initialize game objects
dice = Dice()
card_popup = Event()
menu = Menu(screen)




#token = PlayerTokenImage()
#player = Player(1, "Nate", token)
running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            menu.handle_event(event) 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                rollRes = dice.roll()            
                if rollRes[0] == rollRes[1]:
                    print("Doubles!")
            if event.key == pygame.K_SPACE:
                card_popup.show_event_message(random.randint(1, 32))
      
        
        

    screen.fill(background_color)   
    
    menu.draw() 
    if(not menu.checkMenu()):
        dice.draw(screen) #draw dice onto the screen
        card_popup.draw(screen) #draw the popup box on the screen
        #player.drawScore(screen)

    pygame.display.update() #update the display
    clock.tick(60) #one while loop 60 times per second
