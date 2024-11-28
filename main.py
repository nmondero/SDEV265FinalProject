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
from classes import Board, Dice, Event, Player, PlayerTokenImage, Tile, Property, ColorProperty
from auction import Auction
from button import Buttons

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
running_auction = False
buttons = Buttons(screen)  # Create the buttons




# Trying to fit the game board to the screen here (this orientation seems good)
board_surf = pygame.transform.scale(pygame.image.load("images/GameBoard.png").convert(), (550, 550))
board_rect = pygame.Rect(125, 125, 550, 550)

didImove = False
diceResult = 0
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
                    current_turn = 0

                    # TEST OUTPUT
                    for player in players:
                        print("Name: " + player.playerName)
                        print("Token " + player.token.tokenName)

                    tiles = []
                    for i in range(40):
                        tiles.append(Tile(i))
                    
                    # Initialize buttons on the board after player setup
                    buttons = Buttons(screen)
                    gameboard = Board(screen, players)
                    gameboard.assignPlayerPosition(players)    
                                            

           # Handle key pressing events
            elif event.type == pygame.KEYDOWN:
                print("Input detected")
                if event.key == pygame.K_RETURN:
                    dice.roll()
                    diceResult = dice.result()
                    print(f"Dice Result: {diceResult}")
                    
                    
                    if dice.isDoubles():
                        print("Doubles!")
                    didImove = True

                elif event.key == pygame.K_SPACE:
                    card_popup.show_event_message(random.randint(1, 32))

                #press Left Shift to change players for now till we get functionality 
                elif event.key == pygame.K_LSHIFT:  # Press LSHIFT to advance turn
                    current_turn = (current_turn + 1) % len(players)  # Move to the next player
                    turn_displayed = False #resets to show new player message
                    didImove = True
                
                elif event.key == pygame.K_a:
                    auction_instance = Auction(players, Property(1), current_turn)
                    running_auction=True

            # Handle clicking events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for i in range(40):
                    if tiles[i].tileRect.collidepoint(mouse_pos):
                        print("Clicked Tile: " + tiles[i].tileName)
            
            
    # Fill background to empty before updating with new draws
    screen.fill(backgroundColor)

    # Draw appropriate screen based on game state
    if menu.isActive():  # if player in main menu
        menu.draw()
    elif player_number_menu and player_number_menu.isActive(): #if player is in the number menu
        player_number_menu.draw()
    elif player_menu and player_menu.isActive(): #if player is in the player menu
        player_menu.draw()
    else: #if in game
        screen.blit(board_surf, board_rect)


        
            
        #BEGIN MAIN PLAYING LOOP
        #Put anything the needs to be refreshed after a player turn here
        print(f"\nPlayer: {players[current_turn].playerName}")
        input = 0
        result = 0
        while(input!=4): #input 4 is the end turn button
            #Put everything that needs to be refreshed during a player turn here
            screen.blit(board_surf, board_rect)
            gameboard.drawPlayers(players)
            buttons.draw_buttons()
            gameboard.show_turn_message(players[current_turn].playerName)
                
            pygame.display.update()
            input = buttons.getInput()
            if input == 1:
                dice.roll()
                dice.draw(screen)
                diceResult = dice.result()
                print(f"Dice Result: {diceResult}")
                gameboard.movePlayer(players, current_turn, moveAmount=diceResult)
                result = gameboard.moveResults(players, current_turn)
                if result == 0: #Landed on a free space (visitng jail, go, own property, free parking)
                    pass
                elif result == 1: #Landed on an unowned property
                    if(gameboard.propertyDecision(players[current_turn]) == 1): #Asks if player wants to buy or auction
                        # Create and run auction
                        auction_instance = Auction(players, gameboard.tileArray[players[current_turn].playerPosition], current_turn)
                        winner, winning_bid = auction_instance.run_auction(screen)
                        if winner:
                            winner.removeBalance(winning_bid)
                            winner.addProperty(gameboard.tileArray[players[current_turn].playerPosition])
                            print(f"Auction winner: {winner.playerName} - Paid: ${winning_bid}")
                        ##Clean up the screen after an auction
                        screen.fill(backgroundColor)
                        screen.blit(board_surf, board_rect)
                        dice.draw(screen)
                        gameboard.drawPlayers(players)
                        buttons.draw_buttons()
                        gameboard.show_turn_message(players[current_turn].playerName)
                        # The auction instance will be automatically cleaned up by Python's garbage collector
                    else: #Player wants to buy
                        players[current_turn].addProperty(gameboard.tileArray[players[current_turn].playerPosition])
                        players[current_turn].removeBalance(gameboard.tileArray[players[current_turn].playerPosition].buyPrice)
                        print(f"Bought property for: {gameboard.tileArray[players[current_turn].playerPosition].buyPrice} - New balance: {players[current_turn].playerBalance}")
                
                elif result == 2: #Landed on an event tile
                    event_code = random.randint(1,32)  
                    event_start_time = pygame.time.get_ticks()
                    card_popup.show_event_message(event_code)
                    waiting_for_event = True
                    
                    # Keep updating the screen while waiting
                    while waiting_for_event:
                        
                        # Check if 6 seconds have passed
                        if pygame.time.get_ticks() - event_start_time >= 6000:
                            waiting_for_event = False
                            card_popup.hide_event_message()
                        
                        # Keep processing events to prevent the game from appearing frozen
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                waiting_for_event = False
                            elif event.type == pygame.MOUSEBUTTONDOWN:  # Optional: allow clicking to dismiss
                                waiting_for_event = False
                                card_popup.hide_event_message()
                        
                        pygame.display.update()
                        clock.tick(60)  # Maintain frame rate
                    
                    # Process the event outcome after showing the card
                    ##Clean up the screen after an auction
                    screen.fill(backgroundColor)
                    screen.blit(board_surf, board_rect)
                    dice.draw(screen)
                    gameboard.drawPlayers(players)
                    buttons.draw_buttons()
                    gameboard.show_turn_message(players[current_turn].playerName)
                    #Event.event_outcome(event_code, players[current_turn], gameboard)
                
                elif result == 3: #Landed on a tax tile
                    pass
                elif result == 4: #Landed on go to jail
                    pass
            elif input == 2: #sell property
                pass
            elif input == 3: #Upgrade property
                pass
            elif input == 4: #End turn
                current_turn = (current_turn + 1) % len(players)  # Move to the next player
                turn_displayed = True #resets to show new player message
        card_popup.draw(screen)
        
        if running_auction:
            if auction_instance.is_running():
                auction_instance.auction_screen(screen)
                del auction_instance
                running_auction = False
        

    pygame.display.update()  # update the display
    clock.tick(60)  # one while loop 60 times per second
