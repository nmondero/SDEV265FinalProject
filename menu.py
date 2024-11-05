import pygame

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.menu_active = True
        self.overlay_active = False  # Track if the overlay is visible

        # Define colors
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.BLACK = (0, 0, 0)
        self.OVERLAY_COLOR = (250, 250, 250)  # Semi-transparent color for overlay

        # Define button properties
        self.button_width, self.button_height = 200, 50
        self.button_margin = 20
        self.buttons = [
            {"label": "Start Game", "action": "start_game"},
            {"label": "Load Game", "action": "load_game"},
            {"label": "How to Play", "action": "how_to_play"},
        ]

        self.font = pygame.font.Font(None, 24)
        
        # Calculate button positions to center them
        self.box_rect = pygame.Rect(0, 0, 800, 800)
        self.button_rects = []
        for i, button in enumerate(self.buttons):
            x = (self.box_rect.width - self.button_width) // 2
            y = (self.box_rect.height - self.button_height) // 2 + i * (self.button_height + self.button_margin)
            self.button_rects.append(pygame.Rect(x, y, self.button_width, self.button_height))

        # Define overlay properties
        self.overlay_rect = pygame.Rect(150, 150, 500, 500)
        self.close_button_rect = pygame.Rect(self.overlay_rect.right - 30, self.overlay_rect.top + 10, 20, 20)

    def handle_event(self, event):
        # Check for mouse click on buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.menu_active and not self.overlay_active:
                # Check if any main menu button was clicked
                for i, button_rect in enumerate(self.button_rects):
                    if button_rect.collidepoint(mouse_pos):
                        action = self.buttons[i]["action"]
                        if action == "start_game":
                            self.menu_active = False  # Hide menu on "Start Game"
                        elif action == "how_to_play":
                            self.overlay_active = True  # Show overlay for "How to Play"
            elif self.overlay_active:
                # Check if close button on overlay was clicked
                if self.close_button_rect.collidepoint(mouse_pos):
                    self.overlay_active = False  # Hide overlay

    def draw(self):
        # Draw the main menu if active
        if self.menu_active:
            self.screen.fill(self.WHITE)
            pygame.draw.rect(self.screen, self.GRAY, self.box_rect)  # Draw the box
            for i, button_rect in enumerate(self.button_rects):
                pygame.draw.rect(self.screen, self.BLACK, button_rect, 2)  # Button border
                font = pygame.font.Font(None, 36)
                text_surface = font.render(self.buttons[i]["label"], True, self.BLACK)
                text_rect = text_surface.get_rect(center=button_rect.center)
                self.screen.blit(text_surface, text_rect)  # Draw button text

        # Draw the overlay if active
        if self.overlay_active:
            overlay_surface = pygame.Surface((self.overlay_rect.width, self.overlay_rect.height), pygame.SRCALPHA)
            overlay_surface.fill(self.OVERLAY_COLOR)
            self.screen.blit(overlay_surface, self.overlay_rect.topleft)

            # Draw close button
            pygame.draw.rect(self.screen, self.WHITE, self.close_button_rect)
            font = pygame.font.Font(None, 24)
            x_text = font.render("X", True, self.BLACK)
            self.screen.blit(x_text, x_text.get_rect(center=self.close_button_rect.center))

            # Draw placeholder text
            placeholder_text = "Starting the game: The player with the highest total after rolling the dice goes first. Moving around the board: Players take turns rolling the dice and moving their token clockwise around the board. Landing on spaces: What a player does when they land on a space depends on the space: Unowned property: The player can buy the property or start an auction. Owned property: The player must pay rent to the owner. GO: The player receives £200 from the bank. Jail: The player goes to jail. Event Space: The player draws a card. Rolling doubles: If a player rolls doubles, they move their token and act on the space they landed on. They then roll the dice again and take another turn. If they roll doubles three times in a row, they go straight to jail. Winning the game: The last player with money wins. Unlike normal Monopoly, you can sell properties for their bought value back to the bank. You cannot trade."
            wrapped_text_surfaces = self.wrap_text(placeholder_text, self.overlay_rect.width - 40)
            y_offset = self.overlay_rect.top + 50  # Start 50 pixels down from top of overlay
            for line_surface in wrapped_text_surfaces:
                text_rect = line_surface.get_rect(centerx=self.overlay_rect.centerx, y=y_offset)
                self.screen.blit(line_surface, text_rect)
                y_offset += line_surface.get_height() + 5  # Add spacing between lines
        
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
            
    def checkMenu(self) -> bool:
        return self.menu_active


        
    