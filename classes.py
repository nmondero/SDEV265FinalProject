import random
import pygame
from typing import Optional, List
from __future__ import annotations

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
    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.dice1Img, self.dice1Rect)
        surface.blit(self.dice2Img, self.dice2Rect)

class Player:
    #Constructor (Only playerName and token are required. All other values have default values for creating players at the start of the game)
    def __init__(self, name: str, token: PlayerToken, balance: int = 1500, position: int = 0, properties: Optional[List[Property]] = None, cards: Optional[List[Card]] = None, isInJail: bool = False, consecutiveDoubles: int = 0, turnsLeftInJail: int = 0, isBankrupt: bool = False):
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

    #Add an amount to player balance
    def addBalance(self, balanceToAdd):
        self.playerBalance += balanceToAdd

    #Remove an amount from player balance
    def removeBalance(self, balanceToRemove):
        self.playerBalance -= balanceToRemove
        if self.playerBalance < 0:
            self.isBankrupt = True

    #Add a property to player's property list
    def addProperty(self, propertyToAdd):
        self.properties += propertyToAdd

    #Remove a property from player's property list
    def removeProperty(self, propertyToRemove):
        if propertyToRemove not in self.properties:
            raise ValueError("Exception: Property to remove is not in player's property list.")
        else: 
            self.properties.remove(propertyToRemove)

    #Return the player's balance
    def getBalance(self) -> int:
        return self.playerBalance

    '''
    I am thinking we simply just use this function to move the player by a specified amount (move amount) or move directly to a certain spot (jumpToTile) and a bool to specify if the jumpToTile should allow passing go
    ex. Move via dice roll (totalDiceVal = 6): 
        player1.movePlayer(moveAmount = totaLDiceVal)
    ex. Pass directly to Go tile (index of zero)
        player1.movePlayer(jumpToTile = 0, passGoViable = True)
    ex. Go directly to jail, do not collect passing go money
        player1.movePlayer(jumpToTile = 10, passGoViable = False)
    '''
    def movePlayer(self, moveAmount = None, jumpToTile = None, passGoViable = None):
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

        
class PlayerToken:
    pass
