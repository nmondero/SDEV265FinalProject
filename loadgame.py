import pygame, os, re
SAVEFILE_DIRECTORY_NAME = "savefiles/"


class LoadGame:
    def __init__(self, screen: pygame.Surface):
        # Basic class properties
        self.screen = screen
        self.load_game_active = False
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 24)
        self.BACKGROUND_WHITE = (200, 200, 200)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        
        # Get the list of files in the savefiles folder
        self.file_names = os.listdir(SAVEFILE_DIRECTORY_NAME)

        # Declare the input string variable. This will contain the full final file name after clicking finalize
        self.input_string = ""

        # Create input prompt surfaces/rects
        self.prompt_text = self.font.render("Enter the name of the save file to load", True, self.BLACK)
        self.prompt_rect = pygame.Rect(400 - self.prompt_text.get_width() // 2, 300, self.prompt_text.get_width(), 36)

        # Create input box rectangle
        self.input_surface = self.small_font.render(self.input_string, True, self.BLACK) # Create the initial input_surface
        self.input_rect = pygame.Rect(270, self.prompt_rect.bottom + 50, 260, 24) # Create a fixed size input rectangle

        # Create finalization box
        self.finalize_name_surface = self.small_font.render("Finalize", True, self.BLACK)
        self.finalize_rect = pygame.Rect(400 - self.finalize_name_surface.get_width() // 2, self.input_rect.bottom + 50, self.finalize_name_surface.get_width(), 24)

        # Create max length error text and boolean flag
        self.max_length_error_surface = self.small_font.render("Save file name is at max length", True, self.RED)
        self.max_length_error_rect = pygame.Rect(400 - self.max_length_error_surface.get_width() // 2, self.finalize_rect.bottom + 50, self.max_length_error_surface.get_width(), 24)
        self.is_max_length = False
        
        # Create empty input error text and boolean flag
        self.empty_input_error_surface = self.small_font.render("Enter a save file name first", True, self.RED)
        self.empty_input_error_rect = pygame.Rect(400 - self.empty_input_error_surface.get_width() // 2, self.finalize_rect.bottom + 50, self.empty_input_error_surface.get_width(), 24)
        self.is_empty_input = False

        # Create file not found error text and boolean flag
        self.file_not_found_surface = self.small_font.render("Cannot find the file", True, self.RED)
        self.file_not_found_rect = pygame.Rect(400 - self.file_not_found_surface.get_width() // 2, self.finalize_rect.bottom + 50, self.file_not_found_surface.get_width(), 24)
        self.is_invalid_file = False

        self.x_text = self.font.render("X", True, self.BLACK)
        self.close_button_rect = pygame.Rect(770, 20, 20, 20)
        self.x_clicked = False

    def get_file_name(self):
        return self.input_string
    
    def handle_event(self, event):
        # Handle typing for name input
        if event.type == pygame.KEYDOWN:
            # Handle delete key
            if event.key == pygame.K_BACKSPACE:
                self.input_string = self.input_string[:-1]
                self.is_max_length = False
                self.is_invalid_file = False

            elif event.key == pygame.K_RETURN:
                if len(self.input_string) == 0:
                    self.is_empty_input = True
                elif not self.file_exists():
                    self.is_invalid_file = True
                else:
                    self.finalize_save_file_name()

            # Handle typing while at max length
            elif self.input_surface.get_width() + 45 > self.input_rect.width: # If you try to input a character past the max length...
                self.is_max_length = True # ...set error flag for max name length

            # Handle valid typing event
            else:
                self.input_string += event.unicode # Append the new character to the name string
                self.is_empty_input = False # Reset error flag that appears when you try to finalize a save game with no name
                self.is_invalid_file = False

        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle clicking finalize
            if self.finalize_rect.collidepoint(event.pos):
                # Handle INCORRECTLY trying to finalize save file name entry with nothing inputted (turn on the error flag for error output)
                if len(self.input_string) == 0:
                    self.is_empty_input = True
                elif not self.file_exists():
                    self.is_invalid_file = True
                # Handle CORRECTLY finalizing a valid save file name
                else:
                    self.finalize_save_file_name()
            
            elif self.close_button_rect.collidepoint(event.pos):
                self.load_game_active = False
                self.x_clicked = True

    # Draw each element to the screen  
    def draw(self):
        self.screen.fill(self.BACKGROUND_WHITE) # Draw the screen white
        self.screen.blit(self.prompt_text, self.prompt_rect) # Draw the prompt

        pygame.draw.rect(self.screen, self.WHITE, self.input_rect) # Draw a white rectangle for the input rect
        self.input_surface = self.small_font.render(self.input_string, True, self.BLACK) # Create the current text based on current input
        self.screen.blit(self.input_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        
        self.screen.blit(self.input_surface, (self.input_rect.x + 5, self.input_rect.y + 5)) # Draw the current input text
        pygame.draw.rect(self.screen, self.GREEN, self.finalize_rect) # Draw the finalization button border
        self.screen.blit(self.finalize_name_surface, (self.finalize_rect.x, self.finalize_rect.y + 5))

        self.screen.blit(self.x_text, self.close_button_rect)
        
        # Check for errors and draw them (only one at a time)
        if self.is_max_length:
            self.screen.blit(self.max_length_error_surface, self.max_length_error_rect)
        elif self.is_empty_input:
            self.screen.blit(self.empty_input_error_surface, self.empty_input_error_rect)

    # Create finalize the save file name by appending necessary extra things and deactivate the load game screen
    def finalize_save_file_name(self):
        files = os.listdir(SAVEFILE_DIRECTORY_NAME) # List of save file names in the savefiles folder
        pattern = r"\.txt$"
        regex_match = re.search(pattern, self.input_string)
        # Append the .txt extension to the filename if the filename does not have .txt
        if not regex_match:
            self.input_string += ".txt"

        # Insert the savefile directory name before the .txt file name
        self.input_string = SAVEFILE_DIRECTORY_NAME + self.input_string

        # Deactivate the name selection screen to continue logic in main
        self.load_game_active = False

    # Check if a file name exists
    def file_exists(self) -> bool:
        pattern = r"\.txt$"
        regex_match = re.search(pattern, self.input_string)
        if not regex_match:
            self.input_string += ".txt"
        
        for file in self.file_names:
            if file == self.input_string:
                return True
            
        return False
    
    def isActive(self) -> bool:
        return self.load_game_active