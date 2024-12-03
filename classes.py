from __future__ import annotations
import random
import pygame
from typing import Optional, List, Tuple
import os

pygame.init()

class Dice:
    DICE_WIDTH = 50
    DICE_HEIGHT = 50
    #All dice face images preloaded in and scaled to 50x50 pixels as a static member
    #Note: It makes sense for all of the dice to be loaded in at once because each face will be retrieved frequently
    diceFaces = (
        pygame.transform.scale(pygame.image.load("images/1face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/2face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/3face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/4face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/5face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/6face.png").convert(), (DICE_WIDTH, DICE_HEIGHT))
    )
    
    DICE_HEIGHT
    #Constructor
    def __init__(self):
        #Default dice values (doesn't matter what they are as default)
        self.dice1Val = 1
        self.dice2Val = 2

        #Default images for each dice (doesn't matter what they are as default)
        self.dice1Img = self.diceFaces[self.dice1Val - 1]
        self.dice2Img = self.diceFaces[self.dice2Val - 1]

        #Rectangles for positioning images
        self.dice1Rect = self.dice1Img.get_rect(top = 10, bottom = 60, left = 690, right = 740)
        self.dice2Rect = self.dice2Img.get_rect(top = 10, bottom = 60, left = 740, right = 790)
    
    #Roll random dice values, change dice images, then return the dice roll as a tuple of ints
    def roll(self) -> Dice:
        self.dice1Val = random.randint(1, 6)
        self.dice2Val = random.randint(1, 6)
        self.dice1Img = self.diceFaces[self.dice1Val - 1]
        self.dice2Img = self.diceFaces[self.dice2Val - 1]
        return self
    
    def result(self) -> int:
        return self.dice1Val + self.dice2Val
    
    # Tells you if the current dice values are the same
    def isDoubles(self) -> bool:
        if self.dice1Val == self.dice2Val:
            return True
        else: 
            return False
    
    #Draw the dice values onto the top right of the screen at the specified rectangles (We can change the positions if we need to depending on screen size)
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.dice1Img, self.dice1Rect)
        screen.blit(self.dice2Img, self.dice2Rect)

class Player:
    #Static map to help determine the location (rectangle coordinates) for a Player's score card
    #Note: We will properly place these later
    PLAYER_SCORE_RECT_COORDINATES = {
        1: (400, 100),
        2: (750, 50),
        3: (50, 750),
        4: (750, 50)
    }

    #Constructor (Only playerName and token are required. All other values have default values for creating players at the start of the game)
    def __init__(self, playerNumber: int, name: str, token: PlayerTokenImage, balance: int = 1500, position: int = 0, properties: Optional[List[Property]] = None, cards: int = 0, isInJail: bool = False, consecutiveDoubles: int = 0, turnsLeftInJail: int = 0, isBankrupt: bool = False, lastDiceResult: int = 0):
        self.playerNumber = playerNumber
        self.playerName = name
        self.playerBalance = balance
        self.propertyList = properties if properties is not None else []
        
        #Used to set and determine the content of the player's score card where the player's score rectangle is
        self.scoreTextFont = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.scoreTextSurface = self.scoreTextFont.render(f"{self.playerName}\nBalance: ${self.playerBalance}", True, "Blue") #NOTE: We need to make sure playerBalance is changed whenever Player.player balance changes.
        self.scoreTextRect = self.scoreTextSurface.get_rect(center = self.PLAYER_SCORE_RECT_COORDINATES[self.playerNumber])

        self.token = token
        self.playerPosition = position
    

        self.numGetOutOfJailCards = cards        
        self.isInJail = isInJail
        self.consecutiveDoubles = consecutiveDoubles
        self.turnsLeftInJail = turnsLeftInJail
        
        self.isBankrupt = isBankrupt # Might not need this, we just end the game on bankruptcy anyways... although might be useful if we 
        self.playerNumber = playerNumber # Dont think we need this
        self.lastDiceResult = lastDiceResult # The only reason I am keeping track of the last total roll result is for the Utilities getRent() function

    def drawScore(self, screen: pygame.Surface):
        screen.blit(self.scoreTextSurface, self.scoreTextRect)
    
    def draw(self, screen: pygame.Surface, x: int, y: int, outline_color: tuple = (0,0,0)):
        circle_diameter = 24  # Diameter of the circle
        outline_thickness = 1  # Outline thickness

        # Create the circle surface and scale the image to fit
        circle_surface = pygame.Surface((circle_diameter, circle_diameter), pygame.SRCALPHA)
        image = pygame.transform.scale(self.token.tokenImg, (circle_diameter, circle_diameter))
        
        # Draw the inner white circle for the background
        pygame.draw.circle(circle_surface, (255, 255, 255, 255), (circle_diameter // 2, circle_diameter // 2), circle_diameter // 2)
        
        # Blit the scaled image onto the circular surface
        circle_surface.blit(image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Draw the outline on the main screen
        pygame.draw.circle(screen, outline_color, (x, y), (circle_diameter // 2) + outline_thickness)
        pygame.draw.circle(screen, (255,255,255), (x, y), (circle_diameter // 2))
        
        # Draw the image with the circular background on the main screen
        screen.blit(circle_surface, (x - circle_diameter // 2, y - circle_diameter // 2))

    def putInJail(self): 
        self.isInJail = True
        self.turnsLeftInJail = 3

    def releaseFromJail(self):
        self.isInJail = False

    #Add a property to player's property list
    def addProperty(self, propertyToAdd: Property) -> None:
        self.propertyList.append(propertyToAdd)

    #Remove a property from player's property list
    def removeProperty(self, propertyToRemove: Property) -> None:
        if propertyToRemove not in self.properties: #Raise exception if the property is not in the player's property list
            raise ValueError("Exception: Property to remove is not in player's property list.")
        self.propertyList.remove(propertyToRemove) #Remove the property from the player's property list

    #Add an amount to player balance
    def addBalance(self, balanceToAdd: int) -> None:
        if (balanceToAdd <= 0): #Raise an exception if invalid parameter
            raise ValueError("Exception: Balance to add (${balanceToAdd}) is not greater than 0.")
        self.playerBalance += balanceToAdd #Add specified amount to player balance

    #Remove an amount from player balance
    def removeBalance(self, balanceToRemove: int) -> None:
        if (balanceToRemove < 0): #Raise exception if invalid parameter
            raise ValueError("Exception: Balance to remove (${balanceToRemove}) is not greater than 0.")

        self.playerBalance -= balanceToRemove #Remove specified amount from player 
        
        ''' 
        Note: I am thinking of moving this to the main so that we dont have to awkwardly pass the screen display to the removeBalance function to get the sellProperty function to work
        if self.playerBalance < 0: #If player balance is less than 0, check if they can sell properties to avoid bankruptcy
            totalPropertyValue = 0
            for property in self.propertyList:
                totalPropertyValue += property.sellValue
            
            if totalPropertyValue < balanceToRemove: #Player is bankrupt if they cannot sell enough value to get out of negative balance
                self.isBankrupt = True

            else: #Make the player sell property until they have enough money to stay out of negative
                while self.playerBalance < balanceToRemove:
                    self.sellProperty(screen)
        '''

    # Pays another player a certain amount
    def payPlayer(self, payAmount: int, payee: Player):
        self.removeBalance(payAmount)
        payee.addBalance(payAmount)
    
    def sellProperty(self, screen: pygame.Surface) -> None:
        if self.propertyList.count() == 0:
            raise ValueError("Exception: No properties to sell.")

        '''
        Create "Sell Property" Surface to display as a title for sell property screen
        Create button objects (Surfaces) that will display properties and their sell values
        Map each button to the properties in the player's property list
        Create an array of Property that represents properties selected to sell
        Create button objects to Confirm the sell or cancel the sell
        Draw over the entire Display Surface with the background color then draw on the new button objects
        Event loop looking for player clicks:
            if player clicks a property button:
                if the property for that button IS NOT in the properties to sell array (the button is UNCLICKED):
                    add the property at that button to properties to sell array
                    Update the button to look like it has been selected (probably change the Surface color)
                if the property for that button IS in the properties to sell array:
                    Remove the property at that button from properties to sell array
                    Update the button to look like it has not been selected (probably change the Surface color back to default)
            if player clicks Sell Properties:
                For each property in the properties to sell array:
                    Add property sell value to player balance
                    Remove the property from player property array
        '''
            

    # Determines if the player owns the full property set of the specified color
    def ownsPropertySet(self, color: str) -> bool:
        # Get a list of the property I
        propIds = []
        for p in self.propertyList: 
            propIds.append(p.tileNumber)
        # Check if the player has each property in the color set
        for colorMemberID in ColorProperty.COLOR_GROUPS[color]:
            if colorMemberID not in propIds:
                return False # Return false if no match found
        
        return True # If player had the whole set

    # Return the value of the nearest speedway
    def nearestSpeedway(self) -> int:
        # Determine index of closest speedway
        pos = self.playerPosition
        railroadIndices = (5, 15, 25, 35)
        minIndex = railroadIndices[0]
        minDistance = abs(minIndex - pos)
        for index in railroadIndices[1:]:
            current_distance = abs(index - pos)
            if current_distance < minDistance:
                minDistance = current_distance
                minIndex = index
        return minIndex

class Board:
    COLOR_PROPERTY_INDEXES = (1, 3, 6, 8, 9, 11, 13, 14, 16, 18, 19, 21, 23, 24, 26, 27, 29, 31, 32, 34, 37, 39)
    UTILITIES_INDEXES = (12, 28)
    SPEEDWAY_INDEXES = (5, 15, 25, 35)
    EVENT_INDEXES = (2, 7, 17, 22, 33, 36)
    TAX_INDEXES = (4, 38)
    JAIL_INDEX = 10
    GO_INDEX = 0
    FREE_PARKING_INDEX = 20
    GO_TO_JAIL_INDEX = 30
    PLAYER_COLOR = [(255, 0, 0),(0,255,0),(0,0,255),(255,255,0)]
    
    def __init__(self, screen: pygame.Surface, playerTurnQueue: List[Player], turnNumber: int = 1, eventCardDeck: List[int] = None):
        self.tileArray = []
        for i in range(40):
            if i in self.COLOR_PROPERTY_INDEXES:
                self.tileArray.append(ColorProperty(i)) 
            elif i in self.UTILITIES_INDEXES:
                self.tileArray.append(Utility(i))
            elif i in self.SPEEDWAY_INDEXES:
                self.tileArray.append(Railroad(i))
            elif i == self.JAIL_INDEX:
                self.tileArray.append(Jail())
            elif i == self.GO_INDEX:
                self.tileArray.append(Tile(i))
            elif i == self.FREE_PARKING_INDEX:
                self.tileArray.append(Tile(i))
            elif i == self.GO_TO_JAIL_INDEX:
                self.tileArray.append(Tile(i))
            elif i in self.EVENT_INDEXES:  # Event card spaces
                self.tileArray.append(Tile(i))
            elif i in self.TAX_INDEXES:
                self.tileArray.append(Tile(i))
            else:
                self.tileArray.append(Tile(i))
        self.playerTurnQueue = playerTurnQueue # We are looking at this like a queue. Current player is the player in position 0. At end of turn, remove at position 0 and append it to the end
        self.turnNumber = turnNumber
        self.GameActive = True
        self.screen = screen

    def drawEvent(self) -> None:
        pass

    def checkEndGame(self) -> bool:
        for player in self.playerTurnQueue:
            if player.playerBalance < 0:
                return True
    
    def endGame(self, playerToRemove: Player) -> None:
        '''
        1. Order players by playerBalance
        2. Make game board screen inactive
        3. Make results screen active -> Display end-of-game rankings and final net worths.
        '''
        pass
    
    def assignPlayerPosition(self, players: Player[Player]):
        for player in players:
            player.playerPosition = 0  # Explicitly set starting position
            tile = self.tileArray[0]
            tile.playersOnTile.append(player)
    
    def rollDice(self, dice: Dice, players: Player[Player], turn: int = 0) -> bool:
        dice.roll()
        players[turn].lastDiceResult = dice.result() # The only reason I am keeping track of the last dice roll result is for the Utilities getRent function
        print(f"Dice Result: {players[turn].lastDiceResult}")
        print(f"Doubles: {dice.isDoubles()}")
        print(f"Consecutive Doubles: {players[turn].consecutiveDoubles}")
        print(f"Is In Jail: {players[turn].isInJail}")
        print(f"Turns Left in Jail: {players[turn].turnsLeftInJail}")
        
        # Decide whether to increment consecutive doubles
        doubles = dice.isDoubles()
        
        if players[turn].isInJail:
            if doubles:
                players[turn].isInJail = False
                self.movePlayer(players, turn, moveAmount = players[turn].lastDiceResult)
                players[turn].consecutiveDoubles += 1
                players[turn].turnsLeftInJail = 0
                return False #You don't roll again if you go to jail after rolling 3 doubles
                

            else:
                players[turn].turnsLeftInJail -= 1
        
        else: #Else not in jail    
            if doubles: #If doubles are rolled, check if 3 consecutive
                players[turn].consecutiveDoubles += 1
                if players[turn].consecutiveDoubles == 3: # If 3 consecutive doubles, go directly to jail
                    players[turn].putInJail()
                    self.movePlayer(players, turn, moveAmount = None, jumpToTile = self.JAIL_INDEX, passGoViable = False)
                    return False

                else: # Else, regular dice roll-based movement
                    self.movePlayer(players, turn, moveAmount = players[turn].lastDiceResult)
                    return True
                
            else: #If not doubles, just move
                players[turn].consecutiveDoubles = 0
                self.movePlayer(players, turn, moveAmount = players[turn].lastDiceResult)
                return False

    
    def drawPlayers(self, players: Player[Player]):
        offset = 0
        font = pygame.font.Font(None, 20)  # Use pygame's default font, size 36
    
        # Draw player scores in each corner
        score_positions = [
            (250,100),     # 2nd position
            (450,100),     # 3rd position
            (50, 100),      # 1st position
            (650,100)     # 4th position
        ]

        # Draw player scores
        for i, player in enumerate(players):
            if i < len(score_positions):  # Make sure we don't exceed available positions
                score_text = font.render(f"Balance: {player.playerName} - ${player.playerBalance}", True, (0, 0, 0))
                self.screen.blit(score_text, score_positions[i])
        
        #Drawing Player Properties
        for player in players:
            for property in player.propertyList:
                tile = self.tileArray[property.tileNumber]
                tileRect = tile.tileRect
                index = tile.tileNumber # Get the tile's index (so we know what side of the board its on)
                if 0 <= index <= 9:  # Bottom row only
                    property.draw(self.screen, tileRect.centerx, tileRect.centery - 50, self.PLAYER_COLOR[players.index(player)])
                elif 10 <= index <= 19:  # Left row
                    property.draw(self.screen, tileRect.centerx + 50, tileRect.centery, self.PLAYER_COLOR[players.index(player)])
                elif 20 <= index <= 29:  # Top row
                    property.draw(self.screen, tileRect.centerx, tileRect.centery + 50, self.PLAYER_COLOR[players.index(player)])
                elif 30 <= index <= 39:  # Right row
                    property.draw(self.screen, tileRect.centerx - 50, tileRect.centery, self.PLAYER_COLOR[players.index(player)])
        
        #Drawing the players on the board
        for player in players:
            tile = self.tileArray[player.playerPosition] # Get the tile that the player landed on
            offset = 10 * tile.playersOnTile.index(player)
            # Determine the magnitude of token offset from center of tile (before adding it to the tile itself) 
            tileRect = tile.tileRect                   
            index = tile.tileNumber # Get the tile's index (so we know what side of the board its on)
            if 0 <= index <= 9:  # Bottom row only
                player.draw(self.screen, tileRect.centerx, tileRect.centery + offset, self.PLAYER_COLOR[players.index(player)])
            elif 10 <= index <= 19:  # Left row
                player.draw(self.screen, tileRect.centerx - offset, tileRect.centery, self.PLAYER_COLOR[players.index(player)])
            elif 20 <= index <= 29:  # Top row
                player.draw(self.screen, tileRect.centerx, tileRect.centery - offset, self.PLAYER_COLOR[players.index(player)])
            elif 30 <= index <= 39:  # Right row
                player.draw(self.screen, tileRect.centerx + offset, tileRect.centery, self.PLAYER_COLOR[players.index(player)])
    
    def movePlayer(self, players: Player[Player], turn: int = 0, moveAmount: Optional[int] = None, jumpToTile: Optional[int] = None, passGoViable: Optional[bool] = None) -> None:
        #Raise exception if parameters are not provided (this function requires either moveAmount alone, or jumpToTile and passGoViable)
        if moveAmount == None and jumpToTile == None:
            raise ValueError("Exception: Function must have at least one parameter of the following sets of parameters:\n\t-int moveAmount = combined dice roll\n\t-int jumpToTile = index of tile to jump to\tbool passGoViable determines if player can pass go from movement")
        
        if moveAmount != None and jumpToTile != None:
            raise ValueError("Exception: Cannot include both a moveAmount and jumpToTile parameter")

        if jumpToTile != None and passGoViable == None:
            raise ValueError("Exception: A jumpToTile parameter must be accompanied by a passGoViable boolean parameter indicating whether the teleport allows the player to collect Passing Go money.")

        initialPosition = players[turn].playerPosition # Set initial position
        initialTile = self.tileArray[initialPosition] # Set initial tile
        
        #If the parameter indicated an amount of spaces to move...
        if moveAmount != None: 
            players[turn].playerPosition += moveAmount
            #Passing Go condition - Apply modulo BEFORE any other operations
            if players[turn].playerPosition >= 40: #Changed from > 39 to >= 40 for clarity
                players[turn].playerPosition %= 40
                players[turn].playerBalance += 200

            #If the parameter indicated a tile to "teleport" to...
        else: 
            players[turn].playerPosition = jumpToTile
            #Passing Go check when jumping to a lower tile index
            if initialPosition > players[turn].playerPosition and passGoViable:
                players[turn].playerBalance += 200
                
        # Handle moving the player token rectangle
        tile = self.tileArray[players[turn].playerPosition] # Get the tile that the player landed on
        tileRect = tile.tileRect
        index = tile.tileNumber # Get the tile's index (so we know what side of the board its on)
        
        # First update the player lists
        tile.playersOnTile.append(players[turn]) # Add the player to the tile landed on
        if(len(initialTile.playersOnTile) > 0):
            initialTile.playersOnTile.remove(players[turn])
        
        # Now calculate offset based on player's position in the list
        offset = 10 * tile.playersOnTile.index(players[turn]) # Use index instead of len to get this player's specific offset
           
            

        if 0 <= index <= 9:  # Bottom row only
            players[turn].draw(self.screen, tileRect.centerx, tileRect.centery + offset)
        elif 10 <= index <= 19:  # Left row
            players[turn].draw(self.screen, tileRect.centerx - offset, tileRect.centery)
        elif 20 <= index <= 29:  # Top row
            players[turn].draw(self.screen, tileRect.centerx, tileRect.centery - offset)
        elif 30 <= index <= 39:  # Right row
            players[turn].draw(self.screen, tileRect.centerx + offset, tileRect.centery)
        '''
        elif isinstance(tile, Jail): # Player is on the jail tile
            if self.isInJail:
                offset = 10 * len(tile.playersInJail)
            
            if self.isInJail: # If player is currently jailed --> offset y down starting from the top right based on how many players on the jail tile are currently jailed
                for player in gameBoard.playerTurnQueue:
                    if player.isInJail:
                        offset += 10
                self.token.moveToken(tileRect.right - 30, tileRect.top + 30 + offset) #NOTE: need to make sure to change offset based on number of player on jail tile that are actually jailed
            
        '''
    def show_turn_message(self, player_name):    
        font = pygame.font.Font(None, 36)
        text_color = (0, 0, 0)  # Black text
        background_color = (200, 200, 200)  # Light gray background

        # Render the message and get a centered rect
        text_surface = font.render(f"{player_name}'s Turn", True, text_color)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, 50))  # position above game board
        
        # Draw a background rect, then the text
        pygame.draw.rect(self.screen, background_color, text_rect.inflate(20, 20))  # Slight padding around text
        self.screen.blit(text_surface, text_rect)

        #update the display to show th message after being called in main loop
        pygame.display.update()
        
    def moveResults(self, players: Player[Player], turn: int)->int:
        currentPlayer = players[turn]
        print(f"Current player: {currentPlayer.playerPosition}")
        if (currentPlayer.playerPosition == self.GO_INDEX) or (currentPlayer.playerPosition == self.JAIL_INDEX) or (currentPlayer.playerPosition == self.FREE_PARKING_INDEX):
            print("0 - Free space")
            return 0
        for property in currentPlayer.propertyList: #Look at all the properties of current player
            if currentPlayer.playerPosition == property.tileNumber: #If the currentplayer is on their own property
                    print("0 - My Property")
                    return 0 #return 0 (do nothing)
        for pos in self.EVENT_INDEXES: #If player landed on an event tile
            if currentPlayer.playerPosition == pos:
                print("2 - Event tile") 
                return 2
        for pos in self.TAX_INDEXES: #If player landed on a tax tile
            if currentPlayer.playerPosition == pos:
                print("3 - Tax tile")
                return 3
        if currentPlayer.playerPosition == self.GO_TO_JAIL_INDEX: #if player landed on go to jail tile
            print("4 - Go to Jail tile")
            return 4
        for player in players: #For all players in the game
            if player != currentPlayer: #Exclude the current player
                for property in player.propertyList: #Look at all the properties they own
                    if currentPlayer.playerPosition == property.tileNumber: #If the currentplayer is on an owned property
                        print(f"{currentPlayer.playerName} pays ${property.getRent(player, currentPlayer)} to {player.playerName}")
                        currentPlayer.payPlayer(property.getRent(player, currentPlayer), player) #Pay the player the rent
                        print("0 - Already Owned Property")
                        return 5 #And end the checks
        print("1 - Unowned Property")
        return 1
    
    def propertyDecision(self, player: Player) -> int:
        currentPlayer = player
        property_image = pygame.image.load(self.tileArray[currentPlayer.playerPosition].image)
        font = pygame.font.SysFont("Arial", 22)
        
        self.screen.fill((200, 200, 200))

        self.screen.blit(property_image, (self.screen.get_width() // 2 - property_image.get_width() // 2, 150))
        
        balance_text = font.render(f"Current Balance: ${currentPlayer.playerBalance}", True, (0, 0, 0))
        self.screen.blit(balance_text, (self.screen.get_width() // 2 - balance_text.get_width() // 2, 50))
        
        cost_text = font.render(f"Cost: ${self.tileArray[currentPlayer.playerPosition].buyPrice}", True, (0, 0, 0))
        self.screen.blit(cost_text, (self.screen.get_width() // 2 - cost_text.get_width() // 2, 100))

        button_width = 100
        button_height = 50
        button_gap = 50  # Gap between buttons
        total_width = button_width * 2 + button_gap
        start_x = (self.screen.get_width() - total_width) // 2

        # Buy Button
        if(player.playerBalance >= self.tileArray[currentPlayer.playerPosition].buyPrice):
            buy_button = pygame.Rect(start_x, self.screen.get_height() - 150 + 20, button_width, button_height)
            pygame.draw.rect(self.screen, (100, 100, 100), buy_button)
            buy_button_text = font.render(f"Buy", True, (0, 0, 0))
            self.screen.blit(buy_button_text, (buy_button.centerx - buy_button_text.get_width() // 2, buy_button.centery - buy_button_text.get_height() // 2))

        # Auction Button
        auction_button = pygame.Rect(start_x + button_width + button_gap, self.screen.get_height() - 150 + 20, button_width, button_height)
        pygame.draw.rect(self.screen, (100, 100, 100), auction_button)
        auction_button_text = font.render(f"Auction", True, (0, 0, 0))
        self.screen.blit(auction_button_text, (auction_button.centerx - auction_button_text.get_width() // 2, auction_button.centery - auction_button_text.get_height() // 2))
        
        pygame.display.update()
        
        waitforinput = True
        while(waitforinput):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pass
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if auction_button.collidepoint(mouse_pos):
                        waitforinput = False
                        self.screen.fill((200, 200, 200))
                        return 1
                    elif buy_button.collidepoint(mouse_pos):
                        waitforinput = False
                        self.screen.fill((200, 200, 200))
                        return 0
                    
        return 0
        pass
    
class PlayerTokenImage: 
    TOKEN_WIDTH = 20
    TOKEN_HEIGHT = 20
    #Static map for token ID numbers to specific token image paths
    ID_TO_IMAGE_PATH = {
        0: "images/pieces/piece1.png",
        1: "images/pieces/piece2.png",
        2: "images/pieces/piece3.png",
        3: "images/pieces/piece4.png",
        4: "images/pieces/piece5.png",
        5: "images/pieces/piece6.png",
        6: "images/pieces/piece7.png",
        7: "images/pieces/piece8.png"
    }
   
    #Static member for token ID to token name
    ID_TO_TOKEN_NAME = {
        0: "Modern Racecar",
        1: "Helmet",
        2: "NASCAR Logo",
        3: "Trophy",
        4: "Classic Racecar",
        5: "Checkered Flags",
        6: "Wheel",
        7: "Steering Wheel"
    }

    #Constructor
    def __init__(self, tokenID: int, x_pos: int = 0, y_pos: int = 0):
        self.tokenID = tokenID
        self.tokenName = self.ID_TO_TOKEN_NAME[tokenID]
        self.tokenImg = pygame.transform.scale(pygame.image.load(self.ID_TO_IMAGE_PATH[tokenID]).convert_alpha(), (self.TOKEN_WIDTH, self.TOKEN_HEIGHT))
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.tokenRect = self.tokenImg.get_rect(center = (self.x_pos, self.y_pos))

    #Draw token image to screen using token rectangle position
    def draw(self, screen: pygame.Surface):
        screen.blit(self.tokenImg, self.tokenRect)

    #Change token rectangle position
    def moveToken(self, x_pos: int, y_pos: int):
        #Raise exception if new token rectangle center would put any part of the rectangle outside of the screen dimensions
        if ((x_pos - self.TOKEN_WIDTH / 2 < 0) or x_pos + self.TOKEN_WIDTH / 2 > 800) or (y_pos - self.TOKEN_HEIGHT / 2 < 0) or (y_pos + self.TOKEN_HEIGHT / 2 > 800):
            raise ValueError("Exception: New token center is outside of the bounds of the window.")
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.tokenRect.center = (self.x_pos, self.y_pos) 

class Tile:
    '''
    Tile Dimensions:
    Resolution: 300px / in
    Tile: 55px x 90px
    Corner Tile: 74px x 74px
    Color bar: 45px x 74px
    '''
    TILE_NUM_TO_INFO = {
        0: {"Name": "GO"},
        1: {"Name": "First Union"},
        2: {"Name": "Event"},
        3: {"Name": "Caterpillar"},
        4: {"Name": "BLACK FLAG"},
        5: {"Name": "California Speedway"},
        6: {"Name": "Lowe's Home Improvement Warehouse"},
        7: {"Name": "Event"},
        8: {"Name": "Skittles"},
        9: {"Name": "Cartoon Network"},
        10: {"Name": "JAIL"},
        11: {"Name": "Bellsouth"},
        12: {"Name": "The Phone Company"},
        13: {"Name": "QVC"},
        14: {"Name": "Kodak Gold Film"},
        15: {"Name": "Talladega Speedway"},
        16: {"Name": "Interstate Batteries"},
        17: {"Name": "Event"},
        18: {"Name": "Exide Batteries"},
        19: {"Name": "The Family Channel Primestar"},
        20: {"Name": "Free Parking"},
        21: {"Name": "Circuit City"},
        22: {"Name": "Event"},
        23: {"Name": "Parts America"},
        24: {"Name": "Pennzoil"},
        25: {"Name": "Charlotte Speedway"},
        26: {"Name": "Texaco"},
        27: {"Name": "Tide"},
        28: {"Name": "The Gas Company"},
        29: {"Name": "Ford Quality Care"},
        30: {"Name": "Go To Jail"},
        31: {"Name": "Valvoline"},
        32: {"Name": "Kellog's"},
        33: {"Name": "Event"},
        34: {"Name": "McDonalds"},
        35: {"Name": "Dayton Speedway"},
        36: {"Name": "Event"},
        37: {"Name": "Du Pont Automotive Finishes"},
        38: {"Name": "Luxury Tax"},
        39: {"Name": "Goodwrench Service Plus"}
    }

    for i in range(len(TILE_NUM_TO_INFO)):
        if (i > 0 and i < 10): # Bottom Row
            width = 45
            height = 74
            TILE_NUM_TO_INFO[i]["Rect"] = pygame.Rect(125 + 74 + (45 * 9) - (45 * (i % 10)) , 604, width, height)

        elif (i > 10 and i < 20): # Left Row
            width = 74
            height = 45
            TILE_NUM_TO_INFO[i]["Rect"] = pygame.Rect(125, 604 - (45 * (i % 10)), width, height)


        elif (i > 20 and i < 30): # Top Row
            width = 45
            height = 74
            TILE_NUM_TO_INFO[i]["Rect"] = pygame.Rect(125 + 74 + (45 * ((i - 1) % 10)), 126, width, height)

        elif (i > 30 and i < 40): # Right Row
            width = 74
            height = 45
            TILE_NUM_TO_INFO[i]["Rect"] = pygame.Rect(604, 125 + 74 + (45 * ((i - 1) % 10)), width, height)

        elif (i == 0): # Bottom Right
            TILE_NUM_TO_INFO[i]["Rect"] = pygame.Rect(604, 604, 74, 74)

        elif (i == 10): # Bottom Left
            TILE_NUM_TO_INFO[i]["Rect"] = pygame.Rect(125, 604, 74, 74)

        elif (i == 20): # Top Left
            TILE_NUM_TO_INFO[i]["Rect"] = pygame.Rect(125, 125, 74, 74)

        elif (i == 30): # Top Right
            TILE_NUM_TO_INFO[i]["Rect"] = pygame.Rect(604, 125, 74, 74)

    def __init__(self, tileNumber: int, playersOnTile: Optional[List[Player]] = None):
        self.tileNumber = tileNumber
        self.playersOnTile = playersOnTile if playersOnTile is not None else []
        self.tileName = self.TILE_NUM_TO_INFO[tileNumber]["Name"]
        self.tileRect = self.TILE_NUM_TO_INFO[tileNumber]["Rect"]

class Property(Tile):
    # Property Number to map containing buy price, rent prices (Decide which one by upgrade value), sell value, and upgrade cost
    # Color property: rent will be determined by upgrade level as a "Rent" index
    # Railroad: rent will be determined with number of railroads in possession of the owning player - 1 as a "Rent" index
    # Utility: rent will be determined with number of utilities in possession of the owning player -1 as a "Rent" index. The "Rent" values are multipliers, NOT rent itself
    PROPERTY_NUM_TO_INFO = {
        1: {"BuyPrice" : 60, "Rent": (2, 10, 30, 90, 160, 250), "SellValue": 30, "Image":"images/properties/P22.png"}, # First Union
        3: {"BuyPrice" : 60, "Rent": (4, 20, 60, 180, 320, 450), "SellValue": 30, "Image":"images/properties/P13.png"}, # Caterpillar
        5: {"BuyPrice" : 200, "Rent": (25, 50, 100, 200), "SellValue": 100, "Image":"images/properties/P14.png"}, # California Speedway
        6: {"BuyPrice" : 100, "Rent": (6, 30, 90, 270, 400, 550), "SellValue": 50, "Image":"images/properties/P18.png"}, # Lowe's Home Improvement Warehouse
        8: {"BuyPrice" : 100, "Rent": (6, 30, 90, 270, 400, 550), "SellValue": 50, "Image":"images/properties/P24.png"}, # Skittles
        9: {"BuyPrice" : 120, "Rent": (8, 40, 100, 300, 450, 600), "SellValue": 60, "Image":"images/properties/P16.png"}, # Cartoon Network
        11: {"BuyPrice" : 140, "Rent": (10, 50, 150, 450, 625, 750), "SellValue": 70, "Image":"images/properties/P17.png"}, # Bellsouth
        12: {"BuyPrice" : 150, "Rent": (4, 10), "SellValue": 75, "Image":"images/properties/P28.png"}, # The Phone Company
        13: {"BuyPrice" : 140, "Rent": (10, 50, 150, 450, 625, 750), "SellValue": 70, "Image":"images/properties/P1.png"}, # QVC
        14: {"BuyPrice" : 160, "Rent": (12, 60, 180, 500, 700, 900), "SellValue": 80, "Image":"images/properties/P7.png"}, # Kodak Gold Film
        15: {"BuyPrice" : 200, "Rent": (25, 50, 100, 200), "SellValue": 100, "Image":"images/properties/P23.png"}, # Talladega Speedway
        16: {"BuyPrice" : 180, "Rent": (14, 70, 200, 550, 750, 950), "SellValue": 90, "Image":"images/properties/P9.png"}, # Interstate Batteries
        18: {"BuyPrice" : 180, "Rent": (14, 70, 200, 550, 750, 950), "SellValue": 90, "Image":"images/properties/P8.png"}, # Exide Batteries
        19: {"BuyPrice" : 200, "Rent": (16, 80, 220, 600, 800, 1000), "SellValue": 100, "Image":"images/properties/P10.png"}, # The Family Channel Primestar
        21: {"BuyPrice" : 220, "Rent": (18, 90, 250, 700, 875, 1050), "SellValue": 110, "Image":"images/properties/P5.png"}, # Circuit City
        23: {"BuyPrice" : 220, "Rent": (18, 90, 250, 700, 875, 1050), "SellValue": 110, "Image":"images/properties/P15.png"}, # Parts America
        24: {"BuyPrice" : 240, "Rent": (20, 100, 300, 750, 925, 1100), "SellValue": 120, "Image":"images/properties/P6.png"}, # Pennzoil
        25: {"BuyPrice" : 200, "Rent": (25, 50, 100, 200), "SellValue": 100, "Image":"images/properties/P27.png"}, # Charlotte Speedway
        26: {"BuyPrice" : 260, "Rent": (22, 110, 330, 800, 975, 1150), "SellValue": 130, "Image":"images/properties/P11.png"}, # Texaco 
        27: {"BuyPrice" : 260, "Rent": (22, 110, 330, 800, 975, 1150), "SellValue": 130, "Image":"images/properties/P12.png"}, # Tide
        28: {"BuyPrice" : 150, "Rent": (4, 10), "SellValue": 75, "Image":"images/properties/P25.png"}, # The Gas Company
        29: {"BuyPrice" : 280, "Rent": (24, 120, 360, 850, 1025, 1200), "SellValue": 140, "Image":"images/properties/P21.png"}, # Ford Quality Care
        31: {"BuyPrice" : 300, "Rent": (26, 130, 390, 900, 1100, 1275), "SellValue": 150, "Image":"images/properties/P26.png"}, # Valvoline
        32: {"BuyPrice" : 300, "Rent": (26, 130, 390, 900, 1100, 1275), "SellValue": 150, "Image":"images/properties/P3.png"}, # Kellog's
        34: {"BuyPrice" : 320, "Rent": (28, 150, 450, 1000, 1200, 1400), "SellValue": 160, "Image":"images/properties/P19.png"}, # Mcdonald's
        35: {"BuyPrice" : 200, "Rent": (25, 50, 100, 200), "SellValue": 100, "Image":"images/properties/P2.png"}, # Daytona Speedway
        37: {"BuyPrice" : 350, "Rent": (35, 175, 500, 1100, 1300, 1500), "SellValue": 175, "Image":"images/properties/P4.png"}, # Du Pont Automotive Finishes
        39: {"BuyPrice" : 400, "Rent": (50, 200, 600, 1400, 1700, 2000), "SellValue": 200, "Image":"images/properties/P20.png"} # Goodwrench Service Plus
    }
    
    # Property Constructor
    def __init__ (self, tileNumber: int, playersOnTile: Optional[List[Player]] = None):
        super().__init__(tileNumber, playersOnTile)
        self.buyPrice = self.PROPERTY_NUM_TO_INFO[tileNumber]["BuyPrice"]
        self.rentList = self.PROPERTY_NUM_TO_INFO[tileNumber]["Rent"]
        self.sellValue = self.PROPERTY_NUM_TO_INFO[tileNumber]["SellValue"]
        self.image = self.PROPERTY_NUM_TO_INFO[tileNumber]["Image"]

    # Abstract getRent function
    def getRent(self, owner: Player, currentPlayer: Player) -> int:
        pass
    
    #Default draw function with no upgrade level
    def draw(self, screen: pygame.Surface, x: int, y: int, circle_color: tuple = (0,0,0)):
        # Define circle properties
        outline_color = (0, 0, 0)  #Black circle
        circle_radius = 10  #radius size

        # Draw the circle with outline
        pygame.draw.circle(screen, outline_color, (x,y), circle_radius + 2)
        pygame.draw.circle(screen, circle_color, (x,y), circle_radius)

class ColorProperty(Property):
    # Define groups of tiles that belong to specific colors
    COLOR_GROUPS = {
        "PURPLE" : (1, 3),
        "CYAN" : (6, 8, 9),
        "MAGENTA" : (11, 13, 14),
        "ORANGE" : (16, 18, 19),
        "RED" : (21, 23, 24),
        "YELLOW" : (26, 27, 29),
        "GREEN" : (31, 32, 34),
        "BLUE" : (37, 39)
    }

    def __init__(self, tileNumber: int, playersOnTile: Optional[List[Player]] = None, upgradeLevel: int = 0):
        super().__init__(tileNumber, playersOnTile)
        # Handle upgradeLevel parameter
        if upgradeLevel < 0 or upgradeLevel > 5:
            raise ValueError("Exception: upgradeLevel" + upgradeLevel + " out of range")        
        else:
            self.upgradeLevel = upgradeLevel

        # Determine upgradeCost based on tile number (Each side of the board has a uniform upgrade cost incrementing by 50 from 50 to 200)
        self.upgradeCost = 50 + (50 * (tileNumber // 10))

        # Determine the color based on tile number
        self.color = None  # Initialize color to None
        for group_name, group_values in self.COLOR_GROUPS.items():
            if tileNumber in group_values:
                self.color = group_name
                break
        
        if self.color is None:
            raise ValueError(f"Invalid tile number {tileNumber} - no matching color group found")

    # Upgrades the property. Assumes player balance has already been verified to perform the upgrade
    def upgrade(self):
        if self.upgradeLevel == 5:
            raise Exception("Exception: Cannot upgrade past hotel (if upgradeLevel == 5)")   
        else:
            self.upgradeLevel += 1

    # Downgrades the property (if the player sells an upgrade)
    def downgrade(self):
        if self.upgradeLevel == 0:
            raise Exception("Exception: Cannot downgrade with no houses (if upgradeLevel == 0)")
        else:     
            self.upgradeLevel -= 1
    
    # Reset upgrades to 0 if ownership is transferred
    def resetUpgrade(self):
        self.upgradeLevel = 0
        
    # Override: Determine the rent due from landing on this spot given the player that owns the property
    def getRent(self, owner: Player, currentPlayer: Player) -> int:
        if owner.ownsPropertySet(self.color) and self.upgradeLevel == 0: # If the owner owns the property set but hasnt upgraded yet, return double the base rent (special case)
            return self.rentList[0] * 2
        else: # Else, just return the rent from the rentList at the upgradeLevel index
            return self.rentList[self.upgradeLevel]
    
    # Draw color properties with upgrade level
    def draw(self, screen: pygame.Surface, x: int, y: int, circle_color: tuple = (0,0,0)):
        # Define circle properties
        outline_color = (0, 0, 0)  # Black circle
        circle_radius = 10  #radius size

        # Draw the circle with outline
        pygame.draw.circle(screen, outline_color, (x,y), circle_radius + 2)
        pygame.draw.circle(screen, circle_color, (x,y), circle_radius)

        # Render the upgrade level number
        font = pygame.font.Font(None, 24)  # Example font size
        text = font.render(str(self.upgradeLevel + 1), True, outline_color)
        text_rect = text.get_rect(center=(x,y))
        screen.blit(text, text_rect)

class Utility(Property):
    def __init__(self, tileNumber: int, playersOnTile: Optional[List[Player]] = None):
        super().__init__(tileNumber, playersOnTile)

    # Override: Determine the rent due according to the diceRollTotal
    def getRent(self, owner: Player, currentPlayer: Player) -> int:
        # Count the number of utilities owned by the player to determine the resulting dice multiplication value from rentList
        utilityCount = 0
        for prop in owner.propertyList:
            if isinstance(prop, Utility):
                utilityCount += 1
                if utilityCount == 2:
                    break
        factor = self.rentList[utilityCount - 1]
        return factor * currentPlayer.lastDiceResult  # Multiply dice roll by the factor indicated by number of utilities owned (x4 or x10)


class Railroad(Property):
    def __init__(self, tileNumber: int, playersOnTile: Optional[List[Player]] = None):
        super().__init__(tileNumber, playersOnTile)

    # getRent override for railroads. counts railroads that the player owns
    def getRent(self, owner: Player, currentPlayer: Player) -> int:
        railroadCount = 0
        for prop in owner.propertyList:
            if isinstance(prop, Railroad):
                railroadCount += 1
                if railroadCount == 4:
                    break
        return 25 * pow(2, railroadCount - 1) # Corresponds to 25, 50, 100, 200 at 1, 2, 3, and 4 railroads owned
    
class Jail(Tile):
    def __init__(self, playersOnTile: Optional[List[Player]] = None, playersInJail: Optional[List[Player]] = None):
        super().__init__(10, playersOnTile)
        self.playersInJail = playersInJail if playersInJail is not None else []



    def arrest(self, player: Player):
        self.playersInJail.append(player)

    def release(self, player: Player):
        self.playersInJail.remove(player)
        
class Event:
    def __init__(self):
        self.events = {1:"Elected to racing hall of fame. Collect $100",2:"Sign associate sponsorship. Collect $100",3:"First Union race fund matures! Collect $100",4:"Won first pole position! Collect $20",5:"Collect $50 from ever player for guest passes.",6:"Go to jail!",7:"Get out of Jail free!",8:"You are assessed for track repairs. Pay $40 for every upgrade you've made.",9:"Car needs new tires. Pay $100",10:"Speeding on pit row. Pay $50",
        11:"Won first Race! Collect $200",12:"Pay driving school fee of $150",13:"Fastest pit crew! Receive $25 prize.",14:"From sale of surplus race equipment you get $45",15:"In second place collect $10",16:"Race over to go and collect $200",17:"Pay $25 for each upgrade you've made",18:"You make the cover story in Inside Nascar magazine! Collect $150",19:"Need new spark plugs. Advance to parts America.",20:"Advance token to the nearest Speedway and pay owner the rent. If the speedway is unowned, you may buy it.",
        21:"Cut off driver. Go back 3 spaces.",22:"Nascar winston cup scene names you driver of the year! Pay each player $50",23:"Go to jail.",24:"Get out of jail free",25:"Licensed souveniers pay. Pay $15",26:"Race over to QVC",27:"Free pit pass. Advance token to Goodwrench service plus.",28:"You qualified! Drive over to Charlotte Motor Speedway.",29:"Advance token to the nearest Speedway and pay owner the rent. If the speedway is unowned, you may buy it.",30:"Speed over to go and collect $200",
        31:"First Union pays you dividend of $50"}
        
        #initializing variables initially for future references 
        self.font = pygame.font.Font(None, 24) #sets font and size
        self.font_rect = None
        self.font_surface = None
        self.is_visible = False #sets up for the trigger function of the textbox to be shown or not

    def event_outcome(event_code: int, player: Player, gameBoard: Board):

        players = [player]
        current_turn = 0
        
        if(event_code == 1 or event_code == 2 or event_code == 3):
            player.addBalance(100)
            #gain $100
        elif (event_code == 4):
            player.addBalance(20)
            #gain $20
        elif (event_code == 5):
            for payer in gameBoard.playerTurnQueue:
                if payer is not player:
                    payer.payPlayer(50, player)
            #gain $50 from all players
        elif (event_code == 6 or event_code == 23):
            gameBoard.movePlayer(players, current_turn, moveAmount = None, jumpToTile = 10, passGoViable = False)
            player.putInJail()
            
            #go to jail
        elif (event_code == 7 or event_code == 24):
            player.numGetOutOfJailCards += 1
            #get out of jail
        elif (event_code == 8):
            upgradeCount = 0
            for prop in player.propertyList:
                if isinstance(prop, ColorProperty):
                    upgradeCount += prop.upgradeLevel
            player.removeBalance(40 * upgradeCount)
            #pay $40
        elif (event_code == 9):
            player.removeBalance(100)
            #pay $100
        elif (event_code == 10):
            player.removeBalance(50)
            #pay $50
        elif (event_code == 11):
            player.addBalance(200)
            #gain $200
        elif (event_code == 12):
            player.removeBalance(150)
            #pay $150
        elif (event_code == 13):
            player.addBalance(25)
            #gain $25
        elif (event_code == 14):
            player.addBalance(45)
            #gain $45
        elif (event_code == 15):
            player.addBalance(10)
            #gain $10
        elif (event_code == 16 or event_code == 30):
            gameBoard.movePlayer(players, current_turn, moveAmount = None, jumpToTile = 0, passGoViable = True)
            #advance to go
        elif (event_code == 17):
            upgradeCount = 0
            for prop in player.propertyList:
                if isinstance(prop, ColorProperty):
                    upgradeCount += prop.upgradeLevel
            player.removeBalance(25 * upgradeCount)
            #pay $25 for each upgrade
        elif (event_code == 18):
            player.addBalance(150)
            #gain $150
        elif (event_code == 19):
            gameBoard.movePlayer(players, current_turn, moveAmount = None, jumpToTile = 23, passGoViable = True)
            #advance to parts america
        elif (event_code == 20 or event_code == 29):
            # Move the player to the property
            gameBoard.movePlayer(players, current_turn, moveAmount = None, jumpToTile = player.nearestSpeedway(), passGoViable = True)

            #MAKE SURE TO PROCESS BUYING/AUCTIONING IF SPEEDWAY NOT OWNED
            #OR PROCESS PAYING DOUBLE RENT!!!
            
            #advance to nearest speedway and pay double rent or buy property
        elif (event_code == 21):
            gameBoard.movePlayer(moveAmount = -3)
            #go back 3 spaces
        elif (event_code == 22):
            for recipient in gameBoard.playerTurnQueue:
                player.payPlayer(50, recipient)
            #pay each player $50
        elif (event_code == 25):
            player.removeBalance(15)
            #pay 15
        elif (event_code == 26):
            gameBoard.movePlayer(jumpToTile = 23, passGoViable = True)
            #go to QVC
        elif (event_code == 27):
            gameBoard.movePlayer(jumpToTile = 39, passGoViable = True)
            #go to Goodwrench service plus
        elif (event_code == 28):
            gameBoard.movePlayer(jumpToTile = 15, passGoViable = True)
            #go to Charlotte Motor Speedway
        elif (event_code == 31):
            player.addBalance(50)
            #gain $50
    def show_event_message(self, event_code: int):
        """Display the event message and draw it to the screen."""
        message = self.events.get(event_code, "Unknown Event")
        self.font_surface = self.wrap_text(message, 250)  # Wrap text to fit a width of 250 pixels
        self.is_visible = True
        self.draw(pygame.display.get_surface())  # Get the current display surface and draw to it

    def draw(self, screen: pygame.Surface):
        """Draw the event message box and text to the screen."""
        if self.is_visible and self.font_surface:
            # Create semi-transparent overlay
            overlay = pygame.Surface((800, 800), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
            screen.blit(overlay, (0, 0))

            # Create message box
            font_rect = pygame.Rect(200, 250, 400, 300)  # Centered text box
            pygame.draw.rect(screen, (255, 255, 255), font_rect)  # White background
            pygame.draw.rect(screen, (0, 0, 0), font_rect, 2)  # Black border

            # Add a title
            title_font = pygame.font.Font(None, 36)
            title_surface = title_font.render("EVENT CARD", True, (0, 0, 0))
            title_rect = title_surface.get_rect(centerx=font_rect.centerx, top=font_rect.top + 20)
            screen.blit(title_surface, title_rect)

            # Draw each line of wrapped text
            total_height = sum(line.get_height() for line in self.font_surface)
            start_y = font_rect.centery - total_height // 2

            for i, line_surface in enumerate(self.font_surface):
                line_rect = line_surface.get_rect(centerx=font_rect.centerx, top=start_y + i * self.font.get_height())
                screen.blit(line_surface, line_rect)

    def wrap_text(self, text, max_width):
        """Wrap text to fit within a given width."""
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = self.font.render(word + " ", True, (0, 0, 0))
            word_width = word_surface.get_width()

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(" ".join(current_line))

        return [self.font.render(line, True, (0, 0, 0)) for line in lines]
    
    # Hides the event message
    def hide_event_message(self):
        self.is_visible = False