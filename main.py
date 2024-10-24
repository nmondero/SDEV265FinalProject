import pygame
from classes import Dice

#Set display window
width = 800
height = 800
screen = pygame.display.set_mode((width, height))
background_color = (200, 200, 200)
pygame.display.set_caption("Speedopoly")

#Establish game clock
clock = pygame.time.Clock()

#Initialize game objects
dice = Dice()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                rollRes = dice.roll()
                if rollRes[0] == rollRes[1]:
                    print("Doubles!")

    screen.fill(background_color)     
    dice.draw(screen) #draw dice onto the screen
    
    pygame.display.update() #update the display
    clock.tick(60) #one while loop 60 times per second
