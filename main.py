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

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            # Handle main menu events
            if menu.checkMenu():
                menu.handle_event(event)
                # When start game is clicked in main menu
                if (
                    not menu.checkMenu() and menu.buttons[0]["action"] == "start_game"
                ):  # Check if Start Game was clicked
                      player_number_menu = PlayerNumberMenu(screen)  # Show player number selection first
            
            # Handle player number selection
            elif player_number_menu and player_number_menu.checkMenu():
                player_number_menu.handle_event(event)
                # When player count is selected
                if not player_number_menu.checkMenu():
                    num_players = player_number_menu.getPlayerCount()
                    player_menu = Player_Menu(screen)
                    player_menu.total_players = num_players  # Set the number of players

            # Handle player menu events if it exists and is active
            elif player_menu and player_menu.checkMenu():
                player_menu.handle_event(event)

                # When player setup is complete
                if not player_menu.checkMenu():

                    # Create player objects from setup data
                    player_data = player_menu.getPlayers()
                    for i, data in enumerate(player_data):
                           # data["token"] is already a PlayerTokenImage instance
                            player = Player(i + 1, data["name"], data["token"])
                            players.append(player)
                        

            # Handle game events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    rollRes = dice.roll()
                    if rollRes[0] == rollRes[1]:
                        print("Doubles!")
                if event.key == pygame.K_SPACE:
                    card_popup.show_event_message(random.randint(1, 32))

    screen.fill(backgroundColor)

    # Draw appropriate screen based on game state
    if menu.checkMenu():  # if player in main menu
        menu.draw()
    elif player_number_menu and player_number_menu.checkMenu(): #if player is in the number menu
        player_number_menu.draw()
    elif player_menu and player_menu.checkMenu(): #if player is in the player menu
        player_menu.draw()
    else: #if in game
        dice.draw(screen)
        card_popup.draw(screen)
        # player.drawScore(screen)

    pygame.display.update()  # update the display
    clock.tick(60)  # one while loop 60 times per second
