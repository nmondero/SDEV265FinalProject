import pygame
from classes import Property, Player
from typing import Optional, Tuple

# Constants for screen size, colors, and font size
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
FONT_SIZE = 24
BOX_COLOR = (230, 230, 230)
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (200, 200, 200)
BUTTON_TEXT_COLOR = (50, 50, 50)
BID_BUTTONS = [10, 25, 50]

class Auction:
    def __init__(self, players, property1, current_player_index):
        """
        Initializes the auction.

        Args:
            players (list): List of players participating in the auction.
            property1 (Property): The property being auctioned.
            current_player_index (int): The index of the player starting the auction.
        """
        self.players = players.copy()  # Make a copy of the players list
        self.auction_property = property1
        self.current_bid = 0
        self.bids = []
        self.current_player_index = current_player_index
        self.running = True
        self.exceded = False
        self.property_image = pygame.image.load(self.auction_property.image)
        self.winner = None
        self.winning_bid = 0

    def load_property_image(self):
        """Load the image for the auctioned property (placeholder here)."""
        # For now, return a placeholder, you can later replace this with actual property images
        return pygame.Surface((100, 100))  # placeholder surface

    def is_running(self):
        """Returns whether the auction is still running."""
        return self.running

    def make_bid(self, bid_amount):
        """Handles a player's bid."""
        self.exceded = False
        player_Balance = self.players[self.current_player_index].playerBalance
        if(bid_amount+self.current_bid <= player_Balance):
            self.current_bid = self.current_bid + bid_amount
            self.bids.append((self.players[self.current_player_index], bid_amount))
            self.next_player()
        else:
            self.exceded = True

    def next_player(self):
        """Moves to the next player."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def withdraw_player(self):
        """Removes the current player from the auction if they withdraw."""
        self.players.pop(self.current_player_index)
        self.next_player()  # Move to the next player after withdrawal

    def finish_auction(self):
        """Finishes the auction and determines the winner."""
        self.running = False
        self.winner = self.players[self.current_player_index]  # Last bid is the winning bid
        self.winning_bid = self.current_bid

    def run_auction(self, screen) -> Tuple[Optional[Player], int]:
        """
        Runs the auction and returns the winner and winning bid.
        
        Returns:
            tuple: (winner: Player or None, winning_bid: int)
        """
        self.auction_screen(screen)
        return self.winner, self.winning_bid

    def auction_screen(self, screen):
        while len(self.players) > 1 and self.running:
            screen.fill(BOX_COLOR)
            font = pygame.font.SysFont("Arial", FONT_SIZE)
            
            current_player_text = font.render(f"Current Player: {self.players[self.current_player_index].playerName}", True, TEXT_COLOR)
            screen.blit(current_player_text, (SCREEN_WIDTH // 2 - current_player_text.get_width() // 2, 50))
            
            current_player_balance = font.render(f"Balance: {self.players[self.current_player_index].playerBalance}", True, TEXT_COLOR)
            screen.blit(current_player_balance, (SCREEN_WIDTH // 2 - current_player_balance.get_width() // 2, 85))
            
            bid_text = font.render(f"Current Bid: ${self.current_bid}", True, TEXT_COLOR)
            screen.blit(bid_text, (SCREEN_WIDTH // 2 - bid_text.get_width() // 2, 120))
            
            screen.blit(self.property_image, (SCREEN_WIDTH // 2 - self.property_image.get_width() // 2, 150))
            
            button_10 = pygame.Rect(SCREEN_WIDTH // 4 * (0 + 1) - 50, SCREEN_HEIGHT - 150 + 20, 100, 50)
            pygame.draw.rect(screen, BUTTON_COLOR, button_10)
            bid_button_text = font.render(f"$10", True, BUTTON_TEXT_COLOR)
            screen.blit(bid_button_text, (button_10.centerx - bid_button_text.get_width() // 2, button_10.centery - bid_button_text.get_height() // 2))
            
            button_25 = pygame.Rect(SCREEN_WIDTH // 4 * (1 + 1) - 50, SCREEN_HEIGHT - 150 + 20, 100, 50)
            pygame.draw.rect(screen, BUTTON_COLOR, button_25)
            bid_button_text = font.render(f"$25", True, BUTTON_TEXT_COLOR)
            screen.blit(bid_button_text, (button_25.centerx - bid_button_text.get_width() // 2, button_25.centery - bid_button_text.get_height() // 2))
            
            button_50 = pygame.Rect(SCREEN_WIDTH // 4 * (2 + 1) - 50, SCREEN_HEIGHT - 150 + 20, 100, 50)
            pygame.draw.rect(screen, BUTTON_COLOR, button_50)
            bid_button_text = font.render(f"$50", True, BUTTON_TEXT_COLOR)
            screen.blit(bid_button_text, (button_50.centerx - bid_button_text.get_width() // 2, button_50.centery - bid_button_text.get_height() // 2))
            
            withdraw_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100 + 20, 100, 50)
            pygame.draw.rect(screen, BUTTON_COLOR, withdraw_button)
            withdraw_text = font.render("Withdraw", True, BUTTON_TEXT_COLOR)
            screen.blit(withdraw_text, (withdraw_button.centerx - withdraw_text.get_width() // 2, withdraw_button.centery - withdraw_text.get_height() // 2))
            
            if(self.exceded):
                exceded_text = font.render("You cannot bid that much as it exceeds your current balance", True, (255,0,0))
                screen.blit(exceded_text, (SCREEN_WIDTH // 2 - (exceded_text.get_width()//2), withdraw_button.bottom + 5))
            
            pygame.display.update()
            print("In loop")
            waitforinput = True
            while(waitforinput):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        if withdraw_button.collidepoint(mouse_pos):
                            self.withdraw_player()
                            waitforinput = False
                        if button_10.collidepoint(mouse_pos):
                            self.make_bid(10)
                            waitforinput = False
                        if button_25.collidepoint(mouse_pos):
                            self.make_bid(25)
                            waitforinput = False
                        if button_50.collidepoint(mouse_pos):
                            self.make_bid(50)
                            waitforinput = False
            
        self.finish_auction()