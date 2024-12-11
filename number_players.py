import pygame


class PlayerNumberMenu:
    def __init__(self, screen):
        self.screen = screen
        self.menu_active = False
        
        # Define colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.HOVER_COLOR = (220, 220, 220)
        
        # Button properties
        self.button_width = 100
        self.button_height = 50
        self.button_margin = 20
        
        # Create buttons for 2-4 players
        self.buttons = []
        self.button_rects = []
        
        # Setup buttons
        for i in range(3):  # 2-4 players
            self.buttons.append({"label": f"{i+2}", "value": i+2, "hover": False})
            
        # Center buttons horizontally and vertically
        start_y = (800 - (3 * (self.button_height + self.button_margin))) // 2
        for i in range(3):
            x = (800 - self.button_width) // 2
            y = start_y + i * (self.button_height + self.button_margin)
            self.button_rects.append(pygame.Rect(x, y, self.button_width, self.button_height))
        
        self.font = pygame.font.Font(None, 36)
        self.selected_players = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_players = i + 2
                    self.menu_active = False
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            for i, rect in enumerate(self.button_rects):
                self.buttons[i]["hover"] = rect.collidepoint(mouse_pos)

    def draw(self):
        self.screen.fill(self.WHITE)
        
        # Draw title
        title = "Select Number of Players"
        title_surface = self.font.render(title, True, self.BLACK)
        title_rect = title_surface.get_rect(centerx=400, y=200)
        self.screen.blit(title_surface, title_rect)
        
        # Draw buttons
        for i, (button, rect) in enumerate(zip(self.buttons, self.button_rects)):
            color = self.HOVER_COLOR if button["hover"] else self.WHITE
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.BLACK, rect, 2)
            
            text_surface = self.font.render(button["label"], True, self.BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

    def isActive(self) -> bool:
        return self.menu_active

    def getPlayerCount(self) -> int:
        return self.selected_players



