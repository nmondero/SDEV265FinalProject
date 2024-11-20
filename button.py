import pygame

#class to initialize the properties needed
class Button:
    def __init__(self, x, y, width, height, color, hover_color, label, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.label = label
        self.font = font

    def draw(self, screen):
        #draws button with the names of button
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        label_surface = self.font.render(self.label, True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=self.rect.center)
        screen.blit(label_surface, label_rect)

#class that is imported to main file for appearance and functionality (not yet implemented)
class Buttons:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)  # Smaller font for buttons

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
        self.roll_dice_button = Button(
            start_x, y_position, button_width, button_height, (0, 0, 255), (173, 216, 230), "Roll Dice", self.font
        )
        self.sell_property_button = Button(
            start_x + button_width + button_gap, y_position, button_width, button_height, (0, 0, 255), (173, 216, 230), "Sell Property", self.font
        )
        self.upgrade_button = Button(
            start_x + (button_width + button_gap) * 2, y_position, button_width, button_height, (0, 0, 255), (173, 216, 230), "Upgrade", self.font
        )
        ## for now it shows up with no function, all buttons have no functionality yet but the goal is to have this pop up AFTER player has rolled dice
        self.end_turn_button = Button(
            start_x + (button_width + button_gap) * 3, y_position, button_width, button_height, (0, 0, 255), (173, 216, 230), "End Turn", self.font
        )

    def draw_buttons(self):
        #draws all the buttons on the window
        self.roll_dice_button.draw(self.screen)
        self.sell_property_button.draw(self.screen)
        self.upgrade_button.draw(self.screen)
        self.end_turn_button.draw(self.screen)
