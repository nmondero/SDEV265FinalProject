import pygame
from classes import PlayerTokenImage

class Player_Menu:
    def __init__(self, screen):
        self.screen = screen
        self.player_setup_active = True
        self.current_player = 0
        self.total_players = 2
        self.players = []
        
        # Define colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.DISABLED_COLOR = (160, 160, 160) #grey color for taken tokens

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create Token instances & tracking if it is available 
        self.tokens = [
            {'token': PlayerTokenImage(1), 'taken': False},  # Modern Racecar
            {'token': PlayerTokenImage(2), 'taken': False},  # Helmet
            {'token': PlayerTokenImage(3), 'taken': False},  # NASCAR Logo
            {'token': PlayerTokenImage(4), 'taken': False},  # Trophy
            {'token': PlayerTokenImage(5), 'taken': False},  # Classic Racecar
            {'token': PlayerTokenImage(6), 'taken': False},  # Checkered Flags
            {'token': PlayerTokenImage(7), 'taken': False},  # Wheel
            {'token': PlayerTokenImage(8), 'taken': False}   # Steering Wheel
        ]

        # Setup interface elements
        self.setup_player_interface()

    def setup_player_interface(self):
        # Token selection grid
        self.token_rects = []
        tokens_per_col = 4
        token_size = 40 #had to increase to look better than what 20x20, when it was 20x20 it was so small.
        box_size = 60
        margin_x = 120
        margin_y = 80
        name_spacing = 25
        
        # Calculate grid position
        grid_width = 2 * (token_size + margin_x)
        start_x = (800 - grid_width) // 2 + 50 
        start_y = 200
        
        # Create rectangles and set positions for tokens
        for i, token_data in enumerate(self.tokens):
            col = i // tokens_per_col
            row = i % tokens_per_col
        
            # Box position
            box_x = start_x + col * (box_size + margin_x)
            box_y = start_y + row * (margin_y + name_spacing)
        
            # Create larger box
            rect = pygame.Rect(box_x, box_y, box_size, box_size)
            self.token_rects.append(rect)
        
            # Center token within the larger box
            token_x = box_x + (box_size - token_size) // 2
            token_y = box_y + (box_size - token_size) // 2
            token_data['token'].moveToken(token_x + token_size//2, token_y + token_size//2)
            

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Handle token selection
            for i, rect in enumerate(self.token_rects):
                if rect.collidepoint(mouse_pos):
                    token_data = self.tokens[i]
                    if not token_data['taken']:  # Check taken status from dictionary
                        if len(self.players) < self.current_player + 1:
                            self.players.append({
                                "name": f"Player {self.current_player + 1}",
                                "token": token_data['token']
                            })
                            token_data['taken'] = True  # Mark as taken in dictionary
                            self.current_player += 1
                            if self.current_player >= self.total_players:
                                self.player_setup_active = False

    def draw(self):
        self.screen.fill(self.WHITE)

        # Draw title for player menu window (Player # Setup)
        title = f"Player {self.current_player + 1} Setup"
        title_surface = self.font.render(title, True, self.BLACK)
        title_rect = title_surface.get_rect(centerx=400, y=100)
        self.screen.blit(title_surface, title_rect)

        # Draw "Select Token" section
        token_text = self.font.render("Select Token:", True, self.BLACK)
        token_rect = token_text.get_rect(centerx=400, y=150)
        self.screen.blit(token_text, token_rect)

        # Draw tokens and names
        for i, (token_data, rect) in enumerate(zip(self.tokens, self.token_rects)):
            # Draw token box
            color = self.DISABLED_COLOR if token_data['taken'] else self.WHITE #marks grey if taken or white for available
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2)
        
            # Draw token name with better spacing
            token = token_data['token']
            token_name = token.tokenName
            text_surface = self.small_font.render(token_name, True, self.BLACK)
            name_rect = text_surface.get_rect(
                midtop=(rect.centerx, rect.bottom + 5)
            )
            self.screen.blit(text_surface, name_rect)

            # Draw token image
            token.draw(self.screen)

    def checkMenu(self) -> bool:
        return self.player_setup_active

    def getPlayers(self) -> list:
        return self.players