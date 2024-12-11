import pygame, os, re

SAVEFILE_DIRECTORY_NAME = "savefiles/"

class NameSaveFile:

    def __init__(self, screen):
        # Basic class properties
        self.screen = screen
        self.name_savegame_active = False # Says if the save game naming screen is active
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.BACKGROUND_WHITE = (200, 200, 200)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)

        # Create input string variable. This will contain the full final file name after clicking the finalize button
        self.input_string = "" 

        # Create input prompt surfaces/rects
        self.prompt_text = self.font.render("Enter the name of the save file", True, self.BLACK)
        self.prompt_rect = pygame.Rect(400 - self.prompt_text.get_width() // 2, 300, self.prompt_text.get_width(), 36)
        
        # Create input box rectangle
        self.input_surface = self.small_font.render(self.input_string, True, self.BLACK) # Create the initial input_surface
        self.input_rect = pygame.Rect(300, self.prompt_rect.bottom + 50, 200, 24) # Create a fixed size input rectangle

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

    # Handle an event (event caught in main)
    def handle_event(self, event):

        # Handle typing for name input
        if event.type == pygame.KEYDOWN:
            # Handle delete key
            if event.key == pygame.K_BACKSPACE:
                self.input_string = self.input_string[:-1]
                self.is_max_length = False

            elif event.key == pygame.K_RETURN:
                if len(self.input_string) == 0:
                    self.is_empty_input = True
                else:
                    self.finalize_save_file_name()

            # Handle typing while at max length
            elif self.input_surface.get_width() + 15 > self.input_rect.width: # If you try to input a character past the max length...
                self.is_max_length = True # ...set error flag for max name length

            # Handle valid typing event
            else:
                self.input_string += event.unicode # Append the new character to the name string
                self.is_empty_input = False # Reset error flag that appears when you try to finalize a save game with no name

        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle clicking finalize
            if self.finalize_rect.collidepoint(event.pos):
                # Handle INCORRECTLY trying to finalize save file name entry with nothing inputted (turn on the error flag for error output)
                if len(self.input_string) == 0:
                    self.is_empty_input = True

                # Handle CORRECTLY finalizing a valid save file name
                else:
                    self.finalize_save_file_name()

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
        
        # Check for errors and draw them (only one at a time)
        if self.is_max_length:
            self.screen.blit(self.max_length_error_surface, self.max_length_error_rect)
        elif self.is_empty_input:
            self.screen.blit(self.empty_input_error_surface, self.empty_input_error_rect)

    # Return true if this menu is active
    def isActive(self):
        return self.name_savegame_active
    
    # Return the name of the savefile
    def get_save_name(self):
        return self.input_string
    
    # 
    def finalize_save_file_name(self):
        files = os.listdir(SAVEFILE_DIRECTORY_NAME) # List of save file names in the savefiles folder
        pattern = fr"^{re.escape(self.input_string)}(?:\((\d+)\))?\.txt$" # Regex to capture file names in the savefiles folder matching the current input (including duplicate file designators: ex. duplicate_file(1).txt)
                    
        # Count duplicate file names, including duplicates with duplicate numbers (ex. duplicate_file.txt vs duplicate_file(1).txt) to determine the final save file name
        duplicate_filename_count = 0
        for file in files:
            regex_match = re.search(pattern, file)
            if regex_match:
                duplicate_filename_count += 1

        # IF the save file name entered is already present, make sure to add the appropriate duplicate number in parentheses
        if duplicate_filename_count > 0:
            self.input_string += f"({duplicate_filename_count})"

        # Append the .txt extension to the filename
        self.input_string += ".txt"

        # Insert the savefile directory name before the .txt file name
        self.input_string = SAVEFILE_DIRECTORY_NAME + self.input_string

        # Deactivate the name selection screen to continue logic in main
        self.name_savegame_active = False
