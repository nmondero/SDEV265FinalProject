from __future__ import annotations
import random
import pygame
from typing import Optional, List
import os

pygame.init()

class Dice:
    DICE_WIDTH = 50
    DICE_HEIGHT = 50
    #All dice face images preloaded in and scaled to 50x50 pixels as a static member
    #Note: It makes sense for all of the dice to be loaded in at once because each face will be retrieved frequently
    diceFaces = [
        pygame.transform.scale(pygame.image.load("images/1face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/2face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/3face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/4face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/5face.png").convert(), (DICE_WIDTH, DICE_HEIGHT)),
        pygame.transform.scale(pygame.image.load("images/6face.png").convert(), (DICE_WIDTH, DICE_HEIGHT))
    ]
    
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
    def roll(self) -> tuple[int, int]:
        self.dice1Val = random.randint(1, 6)
        self.dice2Val = random.randint(1, 6)
        self.dice1Img = self.diceFaces[self.dice1Val - 1]
        self.dice2Img = self.diceFaces[self.dice2Val - 1]
        return self.dice1Val, self.dice2Val
    
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
    def __init__(self, playerNumber: int, name: str, token: PlayerTokenImage, balance: int = 1500, position: int = 0, properties: Optional[List[Property]] = None, cards: Optional[List[Card]] = None, isInJail: bool = False, consecutiveDoubles: int = 0, turnsLeftInJail: int = 0, isBankrupt: bool = False):
        self.playerNumber = playerNumber
        self.playerName = name
        self.playerBalance = balance
        
        #Used to set and determine the content of the player's score card where the player's score rectangle is
        self.scoreTextFont = pygame.font.Font(pygame.font.get_default_font(), 12)
        self.scoreTextSurface = self.scoreTextFont.render(f"{self.playerName}\nBalance: ${self.playerBalance}", True, "Blue") #NOTE: We need to make sure playerBalance is changed whenever Player.player balance changes.
        self.scoreTextRect = self.scoreTextSurface.get_rect(center = self.PLAYER_SCORE_RECT_COORDINATES[self.playerNumber])

        self.token = token
        self.playerPosition = position
        self.propertyList = properties if properties is not None else []
        self.cardList = cards if cards is not None else []
        self.isInJail = isInJail
        self.consecutiveDoubles = consecutiveDoubles
        self.turnsLeftInJail = turnsLeftInJail
        self.isBankrupt = isBankrupt
        self.playerNumber = playerNumber

    def drawScore(self, screen: pygame.Surface):
        screen.blit(self.scoreTextSurface, self.scoreTextRect)

    #Add a property to player's property list
    def addProperty(self, propertyToAdd: Property) -> None:
        self.propertyList += propertyToAdd

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
        if (balanceToRemove <= 0): #Raise exception if invalid parameter
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

    '''
    I am thinking we simply just use this function to move the player by a specified amount (move amount) or move directly to a certain spot (jumpToTile) and a bool to specify if the jumpToTile should allow passing go
    ex. Move via dice roll (totalDiceVal = 6): 
        player1.movePlayer(moveAmount = totalDiceVal)
    ex. Pass directly to Go tile (index of zero)
        player1.movePlayer(jumpToTile = 0, passGoViable = True)
    ex. Go directly to jail, do not collect passing go money
        player1.movePlayer(jumpToTile = 10, passGoViable = False)
    '''
    def movePlayer(self, moveAmount: Optional[int] = None, jumpToTile: Optional[int] = None, passGoViable: Optional[bool] = None) -> None:
        #Raise exception if parameters are not provided (this function requires either moveAmount alone, or jumpToTile and passGoViable)
        if moveAmount == None and jumpToTile == None:
            raise ValueError("Exception: Function must have at least one parameter of the following parameters:\n(moveAmount = combined dice roll, jumpToTile = index of tile to jump to)")
        
        if moveAmount != None and jumpToTile != None:
            raise ValueError("Exception: Cannot include both a moveAmount and jumpToTile parameter")

        if jumpToTile != None and passGoViable == None:
            raise ValueError("Exception: A jumpToTile parameter must be accompanied by a passGoViable boolean parameter indicating whether the teleport allows the player to collect Passing Go money.")

        #If the parameter indicated an amount of spaces to move...
        if moveAmount != None: 
            self.playerPosition += moveAmount
            #Passing Go condition
            if self.playerPosition > 39: #39 is the last tile before the Go tile
                self.playerPosition %= 40
                self.playerBalance += 200

        #If the parameter indicated a tile to "teleport" to...
        else: 
            initialPosition = self.playerPosition
            self.playerPosition = jumpToTile
            #Passing Go check when jumping to a lower tile index
            if initialPosition > self.playerPosition and passGoViable:
                self.playerBalance += 200

        '''
        Must move token after player moves
        Find new coordinates based on new player position (Maybe we have a )
        self.token.moveToken(x_coordinate, y_coorindate)
        '''

class Board:
    def __init__(self, tileArray: List[Tile], turnOrder: List[Player], eventCardDeck: List[Card], turnNumber: int):
        self.tileArray = tileArray
        self.turnOrder = turnOrder
        self.evenCardDeck = eventCardDeck
        self.turnNumber = turnNumber

    def drawEvent(self, drawPlayer: Player) -> None:
        pass
    
    def removePlayer(self, playerToRemove: Player) -> None:
        self.turnOrder.remove(playerToRemove)

    def incrementTurnCounter(self):
        self.turnNumber += 1

class PlayerTokenImage:
    TOKEN_WIDTH = 40
    TOKEN_HEIGHT = 40
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
    def __init__(self, tokenID: int):
        self.tokenID = tokenID
        self.tokenName = self.ID_TO_TOKEN_NAME[tokenID]
        self.tokenImg = pygame.transform.scale(pygame.image.load(self.ID_TO_IMAGE_PATH[tokenID]).convert_alpha(), (self.TOKEN_WIDTH, self.TOKEN_HEIGHT))
        self.x_pos = 700
        self.y_pos = 700
        self.tokenRect = self.tokenImg.get_rect(center = (self.x_pos, self.y_pos))

    #Draw token image to screen using token rectangle position
    def draw(self, screen: pygame.Surface):
        screen.blit(self.tokenImg, self.tokenRect)

    #Change token rectangle position
    def moveToken(self, x_pos: int, y_pos: int):
        #Raise exception if new token rectangle center would put any part of the rectangle outside of the screen dimensions
        if ((x_pos - self.TOKEN_WIDTH / 2 < 0) or (x_pos + self.TOKEN_WIDTH / 2 > 800) or (y_pos - self.TOKEN_HEIGHT / 2 < 0) or (y_pos + self.TOKEN_HEIGHT / 2 > 800)):
            raise ValueError("Exception: New token center is outside of the bounds of the window.")
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.tokenRect.center = (self.x_pos, self.y_pos)
    
    # def is_taken(self):
    #     return getattr(self, 'taken', False)

    # def set_taken(self, value):
    #     self.taken = value

    # def get_name(self):
    #     return self.tokenName



class Card:
    pass

class Tile:
    '''
    Tile Dimensions:
    Resolution: 300px / in
    Tile: 55px x 90px
    Corner Tile: 90px x 90px
    Color bar: 55px x 23px
    '''
    TILE_NUM_TO_INFO = {
        0: "GO",
        1: "Tile 2 Name",
        2: "Event",
        3: "Tile Name",
        4: "Income Tax",
        5: "Tile Name",
        6: "Tile Name",
        7: "Event",
        8: "Tile Name",
        9: "Tile Name",
        10: "Jail",
        11: "Tile Name",
        12: "Tile Name",
        13: "Tile Name",
        14: "Tile Name",
        15: "Tile Name",
        16: "Tile Name",
        17: "Event",
        18: "Tile Name",
        19: "Tile Name",
        20: "Free Parking",
        21: "Tile Name",
        22: "Event",
        23: "Tile Name",
        24: "Tile Name",
        25: "Tile Name",
        26: "Tile Name",
        27: "Tile Name",
        28: "Tile Name",
        29: "Tile Name",
        30: "Go To Jail",
        31: "Tile Name",
        32: "Tile Name",
        33: "Event",
        34: "Tile Name",
        35: "Tile Name",
        36: "Event",
        37: "Tile Name",
        38: "Luxury Tax",
        39: "Tile Name"
    }
    
    def __init__(self, tileNumber: int, playersOnTile: Optional[List[Player]] = None):
        self.tileNumber = tileNumber
        self.playersOnTile = playersOnTile if playersOnTile is not None else []
        self.tileName = self.TILE_NUM_TO_INFO[tileNumber]

class Property(Tile):
    def __init__ (self, tileNumber: int, playersOnTile: Optional[List[Player]] = None):
        super(tileNumber, playersOnTile)
        pass

class ColorProperty(Property):
    pass

class Event:
    def __init__(self):
        self.events = {1:"Elected to racing hall of fame. Collect $100",2:"Sign associate sponsorship. Collect $100",3:"First Union race fund matures! Collect $100",4:"Won first pole position! Collect $20",5:"Collect $50 from ever player for guest passes.",6:"Go to jail!",7:"Get out of Jail free!",8:"You are assessed for track repairs. Pay $40 for every upgrade you've made.",9:"Car needs new tires. Pay $100",10:"Speeding on pit row. Pay $50",
        11:"Won first Race! Collect $200",12:"Pay driving school fee of $150",13:"Fastest pit crew! Receive $25 prize.",14:"From sale of surplus race equipment you get $45",15:"In second place collect $10",16:"Race over to go and collect $200",17:"Pay $25 for each upgrade you've made",18:"You make the cover story in Inside Nascar magazine! Collect $150",19:"Need new spark plugs. Advance to parts America.",20:"Advance token to the nearest Speedway and pay owner twice the rent. If the speedway is unowned, you may buy it.",
        21:"Cut off driver. Go back 3 spaces.",22:"Nascar winston cup scene names you driver of the year! Pay each player $50",23:"Go to jail.",24:"Get out of jail free",25:"Licensed souveniers pay. Pay $15",26:"Race over to QVC",27:"Free pit pass. Advance token to Goodwrench service plus.",28:"You qualified! Drive over to Charlotte Motor Speedway.",29:"Advance token to the nearest Speedway and pay owner twice the rent. If the speedway is unowned, you may buy it.",30:"Speed over to go and collect $200",
        31:"First Union pays you dividend of $50",32:"Advance to nearest utility. If unowned, you may buy it. Otherwise pay the owner 10x the amount thrown on the dice."}
        
        #initializing variables initially for future references 
        self.font = pygame.font.Font(None, 24) #sets font and size
        self.font_rect = None
        self.font_surface = None
        self.is_visible = False #sets up for the trigger function of the textbox to be shown or not

    def event_outcome(event_code: int, player: Player):

        if(event_code == 1 or event_code == 2 or event_code == 3):
            player.addBalance(100)
            #gain $100
        elif (event_code == 4):
            player.addBalance(20)
            #gain $20
        elif (event_code == 5):
            pass
            #gain $50 from all players
        elif (event_code == 6 or event_code == 23):
            player.movePlayer(jumpToTile = 10, passGoViable = False)
            #go to jail
        elif (event_code == 7 or event_code == 24):
            pass
            #get out of jail
        elif (event_code == 8):
            player.removeBalance(40)
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
            player.movePlayer(jumpToTile = 0, passGoViable = True)
            #advance to go
        elif (event_code == 17):
            pass
            #pay $25 for each upgrade
        elif (event_code == 18):
            player.addBalance(150)
            #gain $150
        elif (event_code == 19):
            pass
            #advance to parts america
        elif (event_code == 20 or event_code == 29):
            pass
            #advance to nearest speedway and pay double rent or buy property
        elif (event_code == 21):
            player.movePlayer(moveAmount = -3)
            #go back 3 spaces
        elif (event_code == 22):
            pass
            #pay each player $50
        elif (event_code == 25):
            player.removeBalance(15)
            #pay 15
        elif (event_code == 26):
            pass
            #go to QVC
        elif (event_code == 27):
            pass
            #go to Goodwrench service plus
        elif (event_code == 28):
            pass
            #go to Charlotte Motor Speedway
        elif (event_code == 31):
            player.addBalance(50)
            #gain $50
        elif (event_code == 32):
            pass
            #go to nearest speedway. Pay 10x of dice value or buy property
    
    #creates a pop_up message when triggered to show player the event card message
    def show_event_message(self, event_code: int):
        message = self.events.get(event_code, "Unknown Event")
        self.font_surface = self.wrap_text(message, 250)  # Wrap text to fit a width of 300 pixels
        self.is_visible = True

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        
        for word in words:
            # Check if adding the next word exceeds the max width
            test_line = current_line + (word if not current_line else ' ' + word)
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                # If the current line is not empty, add it to lines
                if current_line:
                    lines.append(current_line)
                current_line = word  # Start a new line with the current word
                
        # Add the last line if it's not empty
        if current_line:
            lines.append(current_line)
            
        # Render each line and create a surface to hold all lines
        surfaces = [self.font.render(line, True, (0, 0, 0)) for line in lines]
        return surfaces

    # Hides the event message
    def hide_event_message(self):
        self.is_visible = False

# Draws the event card on the screen
    def draw(self, screen: pygame.Surface):
        if self.is_visible and self.font_surface:
            font_rect = pygame.Rect(250, 300, 300, 200)  # Text box size (LEFT, TOP, WIDTH, HEIGHT)
            pygame.draw.rect(screen, (255, 255, 255), font_rect)  # White background box
            pygame.draw.rect(screen, (0, 0, 0), font_rect, 2)  # Black border

            # Draw each line of wrapped text
            for i, line_surface in enumerate(self.font_surface):
                line_rect = line_surface.get_rect(topleft=(font_rect.x + 10, font_rect.y + 70 + i * self.font.get_height()))
                screen.blit(line_surface, line_rect)
    