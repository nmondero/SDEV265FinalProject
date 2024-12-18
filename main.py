import os
import random
os.environ['SDL_AUDIODRIVER'] = 'dsp'
from menu import Menu
from namesave import NameSaveFile
import sys
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
from loadgame import LoadGame
from classes import Board, Dice, Event, Player, PlayerTokenImage, Tile, Property, ColorProperty, Jail, Utility, Railroad
from auction import Auction
from button import Buttons

# Establish game clock
clock = pygame.time.Clock()

# Initialize game objects
dice = Dice()
card_popup = Event()
menu = Menu(screen)
name_save_file = NameSaveFile(screen)
player_menu = Player_Menu(screen)
number_menu = PlayerNumberMenu(screen)
load_game_menu = LoadGame(screen)
players = []
current_turn = 0 #tracks the current player's turn
turn_displayed = False # track if turn message has been displayed
running = True
running_auction = False
buttons = Buttons(screen)  # Create the buttons


def cleanScreen():
    screen.fill(backgroundColor)
    screen.blit(board_surf, board_rect)
    dice.draw(screen)
    gameboard.drawPlayers(players)
    buttons.draw_buttons(is_doubles)
    gameboard.show_turn_message(players[current_turn].playerName)


def endGame():
    # Sort players by net worth in descending order
    player_net_worths = [(player, player.isPossibletoLive()) for player in players]
    player_net_worths.sort(key=lambda x: x[1], reverse=True)

    # Clear the screen
    screen.fill(backgroundColor)

    # Display the end game results
    font = pygame.font.SysFont("Arial", 24)
    title = font.render("Game Over - Final Standings", True, (0, 0, 0))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 50))

    # Display each player's net worth
    y_offset = 100
    for player, net_worth in player_net_worths:
        player_text = font.render(f"{player.playerName}: ${net_worth}", True, (0, 0, 0))
        screen.blit(player_text, (screen.get_width() // 2 - player_text.get_width() // 2, y_offset))
        y_offset += 40

    pygame.display.update()

    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

# Loads a game given the savefile_name and the screen (screen is only used to construct the gameboard)
def load_the_game(savefile_name: str, screen: pygame.Surface) -> Board:
    file = open(savefile_name, "r")
    
    global current_turn # Declare we are using the current_turn in the rest of main.py
    current_turn = int(file.readline())

    # Process the players
    player_property_ids = {}
    players = []
    num_players = int(file.readline())
    for i in range(num_players):
        playerNumber = int(file.readline()) # Read in player number
        player_property_ids[playerNumber] = [] # Create an empty array for the player's property ids
        
        # Read in the rest of the player specific information
        name = file.readline()
        name = name[:-1] # Shave off the \n character from readLine
        balance = int(file.readline())
        position = int(file.readline())
        playerTokenId = int(file.readline())
        token = PlayerTokenImage(playerTokenId)
        isInJail = (file.readline() == "True")
        isBankrupt = (file.readline() == "True")
        lastDiceResult = int(file.readline())
        consecutiveDoubles = int(file.readline())
        cards = int(file.readline())
        turnsLeftInJail = int(file.readline())

        # For each property in player's property list, read in the tile ID
        num_properties = int(file.readline())
        for j in range(num_properties):
            player_property_ids[playerNumber].append(int(file.readline()))

        # Append a new player to our player list (Without properties)
        players.append(Player(playerNumber = playerNumber, name = name, token = token, balance = balance, position = position, isInJail = isInJail, isBankrupt = isBankrupt, lastDiceResult = lastDiceResult, consecutiveDoubles = consecutiveDoubles, cards = cards, turnsLeftInJail = turnsLeftInJail))

    # Process the tiles
    tiles = []
    for i in range(40): # Iterate through each tile ID number
        players_on_tile = []
        tileNumber = int(file.readline())
        players_in_jail = []
    
        # Get players by their player numbers and add them to the players on the tile
        num_on_tile = int(file.readline())
        for j in range(num_on_tile): # Iterate for each player on the current tile
            current_player_number = int(file.readline()) # Declare the current player number
            
            # Compare player numbers from our currently constructed players with the current player number from the save file
            for p in players:
                if current_player_number == p.playerNumber:
                    players_on_tile.append(p)

        # If the current index is a color property, get the upgrade level
        if tileNumber in Board.COLOR_PROPERTY_INDEXES:
            upgradeLevel = int(file.readline())
            tiles.append(ColorProperty(tileNumber = tileNumber, playersOnTile = players_on_tile, upgradeLevel = upgradeLevel))

        # If the current index is jail, get a list of the players in jail
        elif tileNumber == Board.JAIL_INDEX:
            
            num_in_jail = int(file.readline())
            for j in range(num_in_jail):
                current_player_number = int(file.readline())

                for p in players:
                    if current_player_number == p.playerNumber:
                        players_in_jail.append(p)

            tiles.append(Jail(playersOnTile = players_on_tile, playersInJail = players_in_jail))

        elif tileNumber in Board.UTILITIES_INDEXES:
            tiles.append(Utility(tileNumber = tileNumber, playersOnTile = players_on_tile))

        elif tileNumber in Board.SPEEDWAY_INDEXES:
            tiles.append(Railroad(tileNumber = tileNumber, playersOnTile = players_on_tile))
        
        else:
            tiles.append(Tile(tileNumber = tileNumber, playersOnTile = players_on_tile))

    # Assign tiles to player lists based on previously recorded ownership
    for p in players:
        for prop_id in player_property_ids[p.playerNumber]:
            p.propertyList.append(tiles[prop_id])

    # Create and return the new gameboard object
    return Board(screen = screen, playerTurnQueue = players, savefile = savefile_name, currentTurn = current_turn, tileArray = tiles)


#           MAIN EVENT HANDLER STARTS HERE


# Trying to fit the game board to the screen here (this orientation seems good)
board_surf = pygame.transform.scale(pygame.image.load("images/GameBoard.png").convert(), (550, 550))
board_rect = pygame.Rect(125, 125, 550, 550)

is_doubles = False
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
                    if menu.new_game_clicked:
                        name_save_file = NameSaveFile(screen)
                        name_save_file.name_savegame_active = True
                        menu.new_game_clicked = False
                    elif menu.load_game_clicked:
                        load_game_menu = LoadGame(screen)
                        load_game_menu.load_game_active = True
                        menu.new_game_clicked = False

            elif load_game_menu and load_game_menu.isActive():
                load_game_menu.handle_event(event)
                if not load_game_menu.isActive() and not load_game_menu.x_clicked:
                    savefile_name = load_game_menu.get_file_name()
                    gameboard = load_the_game(savefile_name, screen)
                    players = []
                    for player in gameboard.playerTurnQueue:
                        players.append(player)

                elif not load_game_menu.isActive() and load_game_menu.x_clicked:
                    menu.menu_active = True

            elif name_save_file and name_save_file.isActive():
                name_save_file.handle_event(event)
                if not name_save_file.isActive():
                    savefile = name_save_file.get_save_name()
                    number_menu = PlayerNumberMenu(screen)  # Show player number selection first
                    number_menu.menu_active = True
            
            # Handle player number selection
            elif number_menu and number_menu.isActive():
                number_menu.handle_event(event)
                # When player count is selected
                if not number_menu.isActive():
                    num_players = number_menu.getPlayerCount()
                    player_menu = Player_Menu(screen)
                    player_menu.total_players = num_players  # Set the number of players
                    player_menu.player_setup_active = True

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
                    gameboard = Board(screen, players, savefile)
                    print("Save file is: " + gameboard.savefile)
                    gameboard.assignPlayerPosition(players)    

            
    # Fill background to empty before updating with new draws
    screen.fill(backgroundColor)

    # Draw appropriate screen based on game state
    if menu.isActive():  # if player in main menu
        menu.draw()
    elif load_game_menu and load_game_menu.isActive():
        load_game_menu.draw()
    elif name_save_file and name_save_file.isActive():
        name_save_file.draw()
    elif number_menu and number_menu.isActive(): #if player is in the number menu
        number_menu.draw()
    elif player_menu and player_menu.isActive(): #if player is in the player menu
        player_menu.draw()
    else: #if in game
        screen.blit(board_surf, board_rect)
        
            
        #BEGIN MAIN PLAYING LOOP
        #Put anything the needs to be refreshed after a player turn here
        current_player = players[current_turn]
        
        while current_player.playerBalance < 0:
            #debug_player(current_player)
            if current_player.bankruptcyCheck() == True:
                #Player is bankrupt with no way of getting out
                print(f"Player: {current_player.playerName} is bankrupt with no way of getting out")
                font = pygame.font.SysFont("Arial", 18)
                event_start_time = pygame.time.get_ticks()
                popup_rect2 = pygame.Rect(screen.get_width() // 2 - 405, screen.get_height() // 2 - 55, 810, 110)
                pygame.draw.rect(screen, (0,0,0), popup_rect2, border_radius=20)
                popup_rect = pygame.Rect(screen.get_width() // 2 - 400, screen.get_height() // 2 - 50, 800, 100)
                pygame.draw.rect(screen, (200,200,200), popup_rect, border_radius=20)
                popup_message = font.render("You have run out of money and cannot make it back! The game is over.", True, (0,0,0))
                screen.blit(popup_message, (screen.get_width() // 2 - popup_message.get_width() // 2, screen.get_height() // 2 - popup_message.get_height() // 2))
                waiting_for_event = True
                    
                    # Keep updating the screen while waiting
                while waiting_for_event:
                    # Check if 6 seconds have passed
                    if pygame.time.get_ticks() - event_start_time >= 6000:
                        waiting_for_event = False
                    
                    # Keep processing events to prevent the game from appearing frozen
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            waiting_for_event = False
                        elif event.type == pygame.MOUSEBUTTONDOWN:  # Optional: allow clicking to dismiss
                            waiting_for_event = False
                    
                    pygame.display.update()
                    clock.tick(60)  # Maintain frame rate
                endGame() #end the game and show result screen
            else:
                font = pygame.font.SysFont("Arial", 18)
                event_start_time = pygame.time.get_ticks()
                popup_rect2 = pygame.Rect(screen.get_width() // 2 - 405, screen.get_height() // 2 - 55, 810, 110)
                pygame.draw.rect(screen, (0,0,0), popup_rect2, border_radius=20)
                popup_rect = pygame.Rect(screen.get_width() // 2 - 400, screen.get_height() // 2 - 50, 800, 100)
                pygame.draw.rect(screen, (200,200,200), popup_rect, border_radius=20)
                popup_message = font.render("You have run out of money! Sell properties to get out of debt. Click Back when you are done.", True, (0,0,0))
                screen.blit(popup_message, (screen.get_width() // 2 - popup_message.get_width() // 2, screen.get_height() // 2 - popup_message.get_height() // 2))
                waiting_for_event = True
                    
                    # Keep updating the screen while waiting
                while waiting_for_event:
                    # Check if 6 seconds have passed
                    if pygame.time.get_ticks() - event_start_time >= 6000:
                        waiting_for_event = False
                    
                    # Keep processing events to prevent the game from appearing frozen
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            waiting_for_event = False
                        elif event.type == pygame.MOUSEBUTTONDOWN:  # Optional: allow clicking to dismiss
                            waiting_for_event = False
                    
                    pygame.display.update()
                    clock.tick(60)  # Maintain frame rate
                gameboard.sellScreen(current_player)
                cleanScreen()
        
        print(f"\nPlayer: {current_player.playerName}")
        buttons.draw_buttons(is_doubles)
        if (input == 2 or input == 3) and is_doubles:
                #If the other buttons are pressed instead of roll dice, you still have doubles you need to roll for
                is_doubles = True
        else:
            is_doubles = False
        input = 0
        result = 0
        while(input!=4): #input 4 is the end turn button
            #Put everything that needs to be refreshed during a player turn here
            screen.blit(board_surf, board_rect)
            gameboard.drawPlayers(players)
            gameboard.show_turn_message(current_player.playerName)
            
            buttons.draw_buttons(is_doubles)
            # Check if the current player is in jail and display red text if so
            if current_player.isInJail:
                jail_text = pygame.font.Font(None, 24).render("You are in jail! Roll doubles to get out.", True, (255, 0, 0))
                screen.blit(jail_text, ((screen.get_width() // 2) - (jail_text.get_width() // 2),700))
                
            pygame.display.update()
            input = buttons.getInput()
            if input == 1:
                is_doubles = gameboard.rollDice(dice, players, current_turn)
                cleanScreen()
                dice.draw(screen)
                result = gameboard.moveResults(players, current_turn)
                if result == 0: #Landed on a free space (visitng jail, go, own property, free parking)
                    cleanScreen()
                elif result == 1: #Landed on an unowned property
                    current_property = gameboard.tileArray[current_player.playerPosition]
                    if(gameboard.propertyDecision(current_player) == 1): #Asks if player wants to buy or auction
                        # Create and run auction
                        auction_instance = Auction(players, current_property, current_turn)
                        winner, winning_bid = auction_instance.run_auction(screen)
                        if winner:
                            winner.removeBalance(winning_bid)
                            winner.addProperty(current_property)
                            print(f"Auction winner: {winner.playerName} - Paid: ${winning_bid}")
                        ##Clean up the screen after an auction
                        cleanScreen()
                        # The auction instance will be automatically cleaned up by Python's garbage collector
                    else: #Player wants to buy
                        current_player.addProperty(current_property)
                        current_player.removeBalance(current_property.buyPrice)
                        cleanScreen()
                        print(f"Bought property for: {current_property.buyPrice} - New balance: {current_player.playerBalance}")
                
                elif result == 2: #Landed on an event tile
                    event_code = random.randint(1,31)
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
                    Event.event_outcome(event_code, current_player, gameboard)
                    cleanScreen()
                    if(event_code == 20 or event_code == 29 or event_code == 19 or event_code == 26 or event_code == 27 or event_code == 28):
                        result = gameboard.moveResults(players, current_turn)
                        if result != 5 and result != 0: #Means the property is not owned
                            current_property = gameboard.tileArray[current_player.playerPosition]
                            if(gameboard.propertyDecision(current_player) == 1): #Asks if player wants to buy or auction
                            # Create and run auction
                                auction_instance = Auction(players, current_property, current_turn)
                                winner, winning_bid = auction_instance.run_auction(screen)
                                if winner:
                                    winner.removeBalance(winning_bid)
                                    winner.addProperty(current_property)
                                    print(f"Auction winner: {winner.playerName} - Paid: ${winning_bid}")
                                    # The auction instance will be automatically cleaned up by Python's garbage collector
                            else: #Player wants to buy
                                current_player.addProperty(current_property)
                                current_player.removeBalance(current_property.buyPrice)
                                print(f"Bought property for: {current_property.buyPrice} - New balance: {current_player.playerBalance}")
                    cleanScreen()
                    
                elif result == 3: #Landed on a tax tile
                    if current_player.playerPosition == 4: # BLACK FLAG tile
                        current_player.removeBalance(int(current_player.playerBalance * 0.1))
                    elif current_player.playerPosition == 38: # LUXURY SUITE tile
                        current_player.removeBalance(75)
                    cleanScreen()
                elif result == 4: #Landed on go to jail
                    current_player.putInJail()
                    gameboard.movePlayer(players, current_turn, moveAmount = None, jumpToTile = 10, passGoViable = False)
                elif result == 5: #Landed on own property
                    #Functionality for paying rent is within the gameboard class moveResults
                    cleanScreen()
            elif input == 2: #sell property
                gameboard.sellScreen(current_player)
                cleanScreen()
            elif input == 3: #Upgrade property
                gameboard.upgradeScreen(current_player)
                cleanScreen()
            elif input == 4: #End turn
                current_turn = (current_turn + 1) % len(players)  # Move to the next player
                gameboard.turnNumber = current_turn
                turn_displayed = True #resets to show new player message

            elif input == 5:
                gameboard.save_the_game()
        
        if running_auction:
            if auction_instance.is_running():
                auction_instance.auction_screen(screen)
                del auction_instance
                running_auction = False
        

    pygame.display.update()  # update the display
    clock.tick(60)  # one while loop 60 times per second