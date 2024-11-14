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
from turn_order import show_turn_message

# Establish game clock
clock = pygame.time.Clock()

# Initialize game objects
dice = Dice()
card_popup = Event()
menu = Menu(screen)
player_menu = Player_Menu(screen)
number_menu = PlayerNumberMenu(screen)
players = []
current_turn = 0 #tracks the current player's turn
turn_displayed = False # track if turn message has been displayed
running = True


# Test rects to try to fit a rect to a tile on the board
# Note the dimensions here give us the closest result (553px) to 550px (the size of the game board image) 
# when we calculate the length of one side of the board, from big tile to big tile (ex. from GO to JAIL)
tile_size_test_rect1 = pygame.Rect(125, 125, 74, 74) # Size of rect is 74 x 74 at the top left of the board
tile_size_test_rect2 = pygame.Rect(tile_size_test_rect1.right, tile_size_test_rect1.top, 45, 74) # Size is 45 x 74 to the right of the above rect

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
                    random.shuffle(players) # randomize the player turn order
                    current_turn = 0 #start with the first person


                    # TEST OUTPUT
                    for player in players:
                        print("Name: " + player.playerName)
                        print("Token " + player.token.tokenName)
                        

            # Handle in-game events only after the initial set up is complete
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    rollRes = dice.roll()
                    if rollRes[0] == rollRes[1]:
                        print("Doubles!")

                elif event.key == pygame.K_SPACE:
                    card_popup.show_event_message(random.randint(1, 32))

                #press Left Shift to change players for now till we get functionality 
                elif event.key == pygame.K_LSHIFT:  # Press LSHIFT to advance turn
                    current_turn = (current_turn + 1) % len(players)  # Move to the next player
                    turn_displayed = False #resets to show new player message

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if tile_size_test_rect1.collidepoint(mouse_pos):
                    print("Free parking clicked")
                elif tile_size_test_rect2.collidepoint(mouse_pos):
                    print("Circuit City Clicked")
            
            

    screen.fill(backgroundColor)

    # Draw appropriate screen based on game state
    if menu.isActive():  # if player in main menu
        menu.draw()
    elif player_number_menu and player_number_menu.isActive(): #if player is in the number menu
        player_number_menu.draw()
    elif player_menu and player_menu.isActive(): #if player is in the player menu
        player_menu.draw()
    else: #if in game
               
        # Trying to fit the game board to the screen here
        board_surf = pygame.transform.scale(pygame.image.load("images/GameBoard.png").convert(), (550, 550))
        board_rect = pygame.Rect(125, 125, 550, 550)
        screen.blit(board_surf, board_rect)
        # player.drawScore(screen)
        
        #draw other game elements
        dice.draw(screen)
        card_popup.draw(screen)

       # Show the current player's turn message if not already displayed, must be after all initial elements has been drawn.
        if not turn_displayed:
            show_turn_message(screen, players[current_turn].playerName) #displays the message
            turn_displayed = True  # Set to avoid re-displaying on every frame
        

    pygame.display.update()  # update the display
    clock.tick(60)  # one while loop 60 times per second
