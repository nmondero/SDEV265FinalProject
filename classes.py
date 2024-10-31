from __future__ import annotations
import random
import pygame
from typing import Optional, List


pygame.init()

class Dice:
    #Constructor
    def __init__(self):
        #All dice face images preloaded in and scaled to 50x50 pixels
        self.diceFaces = [
            pygame.transform.scale(pygame.image.load("images/1face.png").convert(), (50, 50)),
            pygame.transform.scale(pygame.image.load("images/2face.png").convert(), (50, 50)),
            pygame.transform.scale(pygame.image.load("images/3face.png").convert(), (50, 50)),
            pygame.transform.scale(pygame.image.load("images/4face.png").convert(), (50, 50)),
            pygame.transform.scale(pygame.image.load("images/5face.png").convert(), (50, 50)),
            pygame.transform.scale(pygame.image.load("images/6face.png").convert(), (50, 50))
        ]

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
    #Constructor (Only playerName and token are required. All other values have default values for creating players at the start of the game)
    def __init__(self, name: str, token: PlayerTokenImage, balance: int = 1500, position: int = 0, properties: Optional[List[Property]] = None, cards: Optional[List[Card]] = None, isInJail: bool = False, consecutiveDoubles: int = 0, turnsLeftInJail: int = 0, isBankrupt: bool = False):
        self.playerName = name
        self.token = token
        self.playerBalance = balance
        self.playerPosition = position
        self.propertyList = properties if properties is not None else []
        self.cardList = cards if cards is not None else []
        self.isInJail = isInJail
        self.consecutiveDoubles = consecutiveDoubles
        self.turnsLeftInJail = turnsLeftInJail
        self.isBankrupt = isBankrupt

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
            raise ValueError("Exception: Balance to add ({balanceToAdd}) is not greater than 0.")
        self.playerBalance += balanceToAdd #Add specified amount to player balance

    #Remove an amount from player balance
    def removeBalance(self, balanceToRemove: int) -> None:
        if (balanceToRemove <= 0): #Raise exception if invalid parameter
            raise ValueError("Exception: Balance to remove ({balanceToRemove}) is not greater than 0.")

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
        #Raise exception if parameters are not provided (this function requires one of the parameters to be defined)
        if moveAmount == None and jumpToTile == None:
            raise ValueError("Exception: Function must have at least one parameter of the following parameters:\n(moveAmount = combined dice roll, jumpToTile = index of tile to jump to)")
        
        if moveAmount != None and jumpToTile != None:
            raise ValueError("Exception: Cannot include both a moveAmount and jumpToTile parameter")

        if jumpToTile != None and passGoViable == None:
            raise ValueError("Exception: A jumpToTile parameter must be accompanied by a passGoViable boolean parameter indicating whether the teleport allows the player to collect Passing Go money.")

        if moveAmount != None: 
            self.playerPosition += moveAmount
            #Passing Go condition
            if self.playerPosition > 39: #39 is the last tile before the Go tile
                self.playerPosition %= 40
                self.playerBalance += 200

        else: 
            initialPosition = self.playerPosition
            self.playerPosition = jumpToTile
            #Passing Go check when jumping to a lower tile index
            if initialPosition > self.playerPosition and passGoViable:
                self.playerBalance += 200


class Board:
    def __init__(self, tileArray: List[Tile], turnOrder: List[Player], eventCardDeck: List[Card], turnNumber: int):
        self.tileArray = tileArray
        self.turnOrder = turnOrder
        self.evenCardDeck = eventCardDeck
        self.turnNumber = turnNumber

    def drawEvent(self, drawPlayer: Player) -> None:
        pass
    
    def removePlayer(playerToRemove: Player) -> None:
        pass

class PlayerTokenImage:
    pass

class Tile:
    pass

class Card:
    pass

class Property(Tile):
    def __init__ (self, propertyName, propertyPrice, rent):
        self.name = propertyName
        self.price = propertyPrice

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

    def event_outcome(event_code: int, player):

        if(event_code == 1 or event_code == 2 or event_code == 3):
            pass
            #gain $100
        elif (event_code == 4):
            pass
            #gain $20
        elif (event_code == 5):
            pass
            #gain $50 from all players
        elif (event_code == 6 or event_code == 23):
            pass
            #go to jail
        elif (event_code == 7 or event_code == 24):
            pass
            #get out of jail
        elif (event_code == 8):
            pass
            #pay $40
        elif (event_code == 9):
            pass
            #pay $100
        elif (event_code == 10):
            pass
            #pay $50
        elif (event_code == 11):
            pass
            #gain $200
        elif (event_code == 12):
            pass
            #pay $150
        elif (event_code == 13):
            pass
            #gain $25
        elif (event_code == 14):
            pass
            #gain $45
        elif (event_code == 15):
            pass
            #gain $10
        elif (event_code == 16 or event_code == 30):
            pass
            #advance to go
        elif (event_code == 17):
            pass
            #pay $25 for each upgrade
        elif (event_code == 18):
            pass
            #gain $150
        elif (event_code == 19):
            pass
            #advance to parts america
        elif (event_code == 20 or event_code == 29):
            pass
            #advance to nearest speedway and pay double rent or buy property
        elif (event_code == 21):
            pass
            #go back 3 spaces
        elif (event_code == 22):
            pass
            #pay each player $50
        elif (event_code == 25):
            pass
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
            pass
            #gain $50
        elif (event_code == 32):
            pass
            #go to nearest speedway. Pay 10x of dice value or buy property
    
    #creates a pop_up message when triggered to show player the event card message
    def show_event_message(self, event_code: int):
        message = self.events.get(event_code, "Unknown Event")

        #rendering the text box on the surface
        self.font_surface = self.font.render(message, True, (0,0,0)) #passes through the message in black text
        self.font_rect = self.font_surface.get_rect(center = (400, 400)) #centering the rect of the screen
        self.is_visible = True # shows the message when message is triggered by the event code 
    
    #hides the event message
    def hide_event_message(self):
        self.is_visible = False #hides the message box when FALSE
    
    #draws the event card on the screen
    def draw(self, screen: pygame.Surface):
        if self.is_visible and self.font_surface:

            font_rect = pygame.Rect(250,  300, 300, 200) #text box size (LEFT, TOP, WIDTH, HEIGHT) all changeable based on how we want to do it
            pygame.draw.rect(screen, (255, 255, 255), font_rect) # white background box
            pygame.draw.rect(screen, (0,0,0), font_rect, 2) #black borderline

            screen.blit(self.font_surface, self.font_rect)