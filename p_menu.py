import pygame
from classes import PlayerTokenImage, Player

class Player_Menu:
    def __init__(self, screen):
        self.screen = screen
        self.player_setup_active = False
        self.current_player = 0
        self.total_players = 2
        self.players = []
        
        # Define colors
        self.WHITE = (200, 200, 200)
        self.BLACK = (0, 0, 0)
        self.DISABLED_COLOR = (120, 120, 120) #grey color for taken tokens
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Create Token instances & tracking if it is available 
        self.tokens = {
            0: {'token': PlayerTokenImage(0), 'taken': False},  # Modern Racecar
            1: {'token': PlayerTokenImage(1), 'taken': False},  # Helmet
            2: {'token': PlayerTokenImage(2), 'taken': False},  # NASCAR Logo
            3: {'token': PlayerTokenImage(3), 'taken': False},  # Trophy
            4: {'token': PlayerTokenImage(4), 'taken': False},  # Classic Racecar
            5: {'token': PlayerTokenImage(5), 'taken': False},  # Checkered Flags
            6: {'token': PlayerTokenImage(6), 'taken': False},  # Wheel
            7: {'token': PlayerTokenImage(7), 'taken': False}   # Steering Wheel
        }

        self.DEFAULT_TOKEN = -1
        self.token_id_selected = self.DEFAULT_TOKEN #Holds the id (the key in the self.tokens map) of the selected token. Default is -1 for no token selected

        # Create name input prompt surface
        self.prompt_surface = self.small_font.render("Select a token then click the box below to enter your name", True, self.BLACK)

        # Create variables to hold name entry info
        self.name_input_string = ""
        
        # Create surfaces and flags for error messages (Flags default to false so their error messages do not appear until the error arises)
        self.max_length_error_surface = self.small_font.render("Player name is at max length", True, self.RED)
        self.is_max_length = False
        
        self.empty_input_error_surface = self.small_font.render("Enter a player name first", True, self.RED)
        self.is_empty_input = False
        
        self.no_token_selected_error_surface = self.small_font.render("Select a token first", True, self.RED)
        self.no_token_selected = False

        # Create finalize player button
        self.finalize_player_surface = self.small_font.render("Finalize Player", True, self.BLACK)

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
        for i in range(len(self.tokens)):
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
            self.tokens[i]['token'].moveToken(token_x + token_size // 2, token_y + token_size // 2)

        # Create the prompt rect, name input rect, and finalize player rect under the token rects
        self.prompt_rect = pygame.Rect(400 - self.prompt_surface.get_width() // 2, self.token_rects[-1].bottom + 75, 200, 25)
        self.name_input_rect = pygame.Rect(300, self.prompt_rect.bottom + 25, 200, 25)
        self.finalize_player_rect = pygame.Rect(((800 + self.name_input_rect.right) // 2) - (self.finalize_player_surface.get_width() // 2), self.name_input_rect.top, self.finalize_player_surface.get_width() + 10, 25)

        # Create error rects positioned below the name input rect
        self.max_length_input_error_rect = pygame.Rect(400 - self.max_length_error_surface.get_width() // 2, self.name_input_rect.bottom + 25, 200, 25)
        self.empty_input_error_rect = pygame.Rect(400 - self.empty_input_error_surface.get_width() // 2, self.name_input_rect.bottom + 25, 200, 25)
        self.no_token_selected_error_rect = pygame.Rect(400 - self.no_token_selected_error_surface.get_width() // 2, self.name_input_rect.bottom + 25, 200, 25)

           

    def handle_event(self, event):
        # Handle clicking the mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get location of mouse click
            mouse_pos = event.pos
                
            # Handle clicking "Finalize Player"
            if self.finalize_player_rect.collidepoint(mouse_pos):
                # If you try to finalize a character with no token selected (token_id_selected == -1, the default value), turn on the error flag to print error during draw
                if self.token_id_selected == self.DEFAULT_TOKEN: 
                    self.no_token_selected = True

                # If you try to finalize a player with an empty name, turn on the error flag to print error during draw
                elif len(self.name_input_string) == 0: 
                    self.is_empty_input = True

                # Create new Player with name_input_string and a new token with the ID of the selected token
                else:
                    self.finalizePlayers()


            else: # Handle token selection
                for i, rect in enumerate(self.token_rects):
                    if rect.collidepoint(mouse_pos):
                        token_data = self.tokens[i]
                        if not token_data['taken']:  # Check taken status from dictionary
                            if self.token_id_selected is not self.DEFAULT_TOKEN: # Remember: DEFAULT_TOKEN (-1) is the value that denotes the player has not selected a token yet
                                self.tokens[self.token_id_selected]["taken"] = False
                                
                            token_data['taken'] = True  # Mark as taken in dictionary
                            self.token_id_selected = i # Assign selected index (the token ID)
                            self.no_token_selected = False # Reset no token selected error flag

                        # If the token clicked was already selected by current player, return token_id_selected to default value and deselect token
                        elif i == self.token_id_selected:
                            self.token_id_selected = self.DEFAULT_TOKEN
                            token_data['taken'] = False

        # Handle keyboard input for the name input box
        if event.type == pygame.KEYDOWN:
            # Handle pressing backspace
            if event.key == pygame.K_BACKSPACE:
                self.name_input_string = self.name_input_string[:-1] # Shave off the last character from the name string
                self.is_max_length = False # Reset error flag indicating name_input_string is no longer max length

            elif event.key == pygame.K_RETURN:
                if self.token_id_selected == self.DEFAULT_TOKEN: 
                    self.no_token_selected = True

                # If you try to finalize a player with an empty name, turn on the error flag to print error during draw
                elif len(self.name_input_string) == 0: 
                    self.is_empty_input = True

                # Create new Player with name_input_string and a new token with the ID of the selected token
                else:
                    self.finalizePlayers()

            # Handle pressing any other key
            elif self.name_input_surface.get_width() + 15 > self.name_input_rect.width: # If you try to input a character past the max length...
                self.is_max_length = True # ...set error flag for max name length
            else:
                self.name_input_string += event.unicode # Append the new character to the name string
                self.is_empty_input = False # Reset error flag that appears when you try to finalize a character with no name

                

    def draw(self):
        self.screen.fill(self.WHITE)

        # Draw title for player menu window (Player # Setup)
        title = f"Player {self.current_player + 1} Setup"
        title_surface = self.font.render(title, True, self.BLACK)
        title_rect = title_surface.get_rect(centerx=400, y=100)
        self.screen.blit(title_surface, title_rect)

        # Draw "Select Token" section
        token_text = self.font.render("Select Token:", True, self.BLACK)
        token_rect = token_text.get_rect(centerx = 400, y = 150)
        self.screen.blit(token_text, token_rect)

        # Draw tokens and names
        for i in range(len(self.tokens)):
            # Draw token box
            color = self.DISABLED_COLOR if self.tokens[i]['taken'] else self.WHITE #marks grey if taken or white for available
            pygame.draw.rect(self.screen, color, self.token_rects[i])
            pygame.draw.rect(self.screen, self.BLACK, self.token_rects[i], 2)
        
            # Draw token name with better spacing
            token = self.tokens[i]['token']
            token_name = token.tokenName
            text_surface = self.small_font.render(token_name, True, self.BLACK)
            name_rect = text_surface.get_rect(midtop = (self.token_rects[i].centerx, self.token_rects[i].bottom + 5))
            self.screen.blit(text_surface, name_rect)

            # Draw token image
            token.draw(self.screen)

        # Draw name input prompt
        self.screen.blit(self.prompt_surface, self.prompt_rect)

        pygame.draw.rect(self.screen, (255, 255, 255), self.name_input_rect)
        
        #Draw the name input box
        self.name_input_surface = self.small_font.render(self.name_input_string, True, self.BLACK)
        self.screen.blit(self.name_input_surface, (self.name_input_rect.x + 5, self.name_input_rect.y + 5))

        # Draw the finalize player box
        pygame.draw.rect(self.screen, self.GREEN, self.finalize_player_rect)
        self.screen.blit(self.finalize_player_surface, (self.finalize_player_rect.x + 5, self.finalize_player_rect.y + 5))

        if self.no_token_selected:
            self.screen.blit(self.no_token_selected_error_surface, self.no_token_selected_error_rect)
        elif self.is_max_length:
            self.screen.blit(self.max_length_error_surface, self.max_length_input_error_rect)
        elif self.is_empty_input:
            self.screen.blit(self.empty_input_error_surface, self.empty_input_error_rect)

    def isActive(self) -> bool:
        return self.player_setup_active

    def getPlayers(self) -> list:
        return self.players
    
    def finalizePlayers(self):
        if len(self.players) < self.current_player + 1:
            self.current_player += 1
            self.players.append(Player(self.current_player, self.name_input_string, PlayerTokenImage(self.token_id_selected)))
            if self.current_player >= self.total_players:
                self.player_setup_active = False
                            
            # Reset selections and error flags to default
            self.token_id_selected = self.DEFAULT_TOKEN
            self.name_input_string = ""
            self.is_max_length = False
            self.is_empty_input = False
            self.no_token_selected = False