import pygame

#class that is imported to main file for appearance and functionality (not yet implemented)
class Buttons:
    def __init__(self, screen):
        self.canIrollDice = True
        self.canIendTurn = False
        self.doubles = False
        self.screen = screen
        font = pygame.font.Font(None, 24)  # Smaller font for buttons

        # Button dimensions
        button_width = 150
        button_height = 50
        button_gap = 10  # Gap between buttons

        # Button positions (aligned horizontally at the bottom)
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Calculate the starting x-position for evenly spaced buttons
        total_width = (button_width * 4) + (button_gap * 3)  # Total width of all buttons with gaps
        start_x = (screen_width - total_width) // 2  # Center the buttons horizontally
        y_position = screen_height - button_height - 20  # 20px margin from the bottom
    
        # Initialize buttons
        self.roll_dice_button = pygame.Rect(start_x, y_position, button_width, button_height)
        self.dice_text = font.render(f"Roll Dice", True, (0, 0, 255))
        
        self.sell_property_button = pygame.Rect(start_x + button_width + button_gap, y_position, button_width, button_height)
        self.property_text = font.render(f"Sell Property", True, (0, 0, 255))
       
        self.upgrade_button = pygame.Rect(start_x + (button_width + button_gap) * 2, y_position, button_width, button_height)
        self.upgrade_text = font.render(f"Upgrade", True, (0, 0, 255))
        
        self.end_turn_button = pygame.Rect(start_x + (button_width + button_gap) * 3, y_position, button_width, button_height)
        self.end_text = font.render(f"End Turn", True, (0, 0, 255))
        
        
    def draw_buttons(self, is_doubles: bool):
        # Clear the button area for refreshing
        self.doubles = is_doubles
        button_area_rect = pygame.Rect(0, self.screen.get_height() - 100, self.screen.get_width(), 150)
        self.screen.fill((200, 200, 200), button_area_rect)  # Use the same background color

        #draws all the buttons on the window
        if self.canIrollDice or self.doubles:
            self.screen.blit(self.dice_text, (self.roll_dice_button.centerx - self.dice_text.get_width() // 2, self.roll_dice_button.centery - self.dice_text.get_height() // 2))
        if self.canIendTurn and not self.doubles:
            self.screen.blit(self.end_text, (self.end_turn_button.centerx - self.end_text.get_width() // 2, self.end_turn_button.centery - self.end_text.get_height() // 2))
            
        self.screen.blit(self.property_text, (self.sell_property_button.centerx - self.property_text.get_width() // 2, self.sell_property_button.centery - self.property_text.get_height() // 2))
        self.screen.blit(self.upgrade_text, (self.upgrade_button.centerx - self.upgrade_text.get_width() // 2, self.upgrade_button.centery - self.upgrade_text.get_height() // 2))
        
        pygame.display.update()

    
    def getInput(self) -> int: 
        waitforinput = True
        while(waitforinput):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if self.roll_dice_button.collidepoint(mouse_pos):
                        if(self.canIrollDice or self.doubles):
                            waitforinput = False
                            self.canIrollDice = False
                            self.canIendTurn = True
                            return 1
                    if self.sell_property_button.collidepoint(mouse_pos):
                        waitforinput = False
                        return 2
                    if self.upgrade_button.collidepoint(mouse_pos):
                        waitforinput = False
                        return 3
                    if self.end_turn_button.collidepoint(mouse_pos):
                        if(self.canIendTurn and not self.doubles):
                            waitforinput = False
                            self.canIendTurn = False
                            self.canIrollDice = True
                            return 4