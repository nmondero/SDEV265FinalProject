import os
import random
os.environ['SDL_AUDIODRIVER'] = 'dsp'
from menu import Menu

import pygame
pygame.init()


# Set display window
WIDTH = 800
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
backgroundColor = (200, 200, 200)
pygame.display.set_caption("Speedopoly")

from menu import Menu
from p_menu import Player_Menu
from number_players import PlayerNumberMenu  
from classes import Dice, Event, Player, PlayerTokenImage, Tile


# Establish game clock
clock = pygame.time.Clock()

# Initialize game objects
dice = Dice()
card_popup = Event()
menu = Menu(screen)
player_menu = Player_Menu(screen)
number_menu = PlayerNumberMenu(screen)
players = []
running = True

# Test rects to try to fit a rect to a tile on the board
# Note the dimensions here give us the closest result (553px) to 550px (the size of the game board image) 


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            # Handle main menu events
            if menu.isActive():
                menu.handle_event(event)
                # When start game is clicked in main menu
                if (not menu.isActive()):  # Check if Start Game was clicked
                      player_number_menu = PlayerNumberMenu(screen)  # Show player number selection first
            
            # Handle player number selection
            elif player_number_menu and player_number_menu.isActive():
                player_number_menu.handle_event(event)
                # When player count is selected
                if not player_number_menu.isActive():
                    num_players = player_number_menu.getPlayerCount()
                    player_menu = Player_Menu(screen)
                    player_menu.total_players = num_players  # Set the number of players

            # Handle player menu events if it exists and is active
            elif player_menu and player_menu.isActive():
                player_menu.handle_event(event)

                # When player setup is complete
                if not player_menu.isActive():

                    # Extract Player objects from player_menu
                    players = player_menu.getPlayers()
                    random.shuffle(players)

                    # TEST OUTPUT
                    for player in players:
                        print("Name: " + player.playerName)
                        print("Token " + player.token.tokenName)


                    tiles = []
                    for i in range(40):
                        tiles.append(Tile(i))
                    
                        
                        
                        

            # Handle game events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    rollRes = dice.roll()
                    if rollRes[0] == rollRes[1]:
                        print("Doubles!")
                if event.key == pygame.K_SPACE:
                    card_popup.show_event_message(random.randint(1, 32))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for i in range(40):
                    if tiles[i].tileRect.collidepoint(mouse_pos):
                        print("Clicked Tile: " + tiles[i].tileName)

    screen.fill(backgroundColor)

    # Draw appropriate screen based on game state
    if menu.isActive():  # if player in main menu
        menu.draw()
    elif player_number_menu and player_number_menu.isActive(): #if player is in the number menu
        player_number_menu.draw()
    elif player_menu and player_menu.isActive(): #if player is in the player menu
        player_menu.draw()
    else: #if in game
        dice.draw(screen)
        card_popup.draw(screen)
        
        # Trying to fit the game board to the screen here
        board_surf = pygame.transform.scale(pygame.image.load("images/GameBoard.png").convert(), (550, 550))
        board_rect = pygame.Rect(125, 125, 550, 550)
        screen.blit(board_surf, board_rect)
        # player.drawScore(screen)

    pygame.display.update()  # update the display
    clock.tick(60)  # one while loop 60 times per second
