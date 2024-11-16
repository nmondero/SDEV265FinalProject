import pygame


#this function is setting the font, text, background, render the text but also displays it when it is called in the main loop
def show_turn_message(screen, player_name):
    font = pygame.font.Font(None, 36)
    text_color = (0, 0, 0)  # Black text
    background_color = (200, 200, 200)  # Light gray background

    # Render the message and get a centered rect
    text_surface = font.render(f"{player_name}'s Turn", True, text_color)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 50))  # position above game board
    
    # Draw a background rect, then the text
    pygame.draw.rect(screen, background_color, text_rect.inflate(20, 20))  # Slight padding around text
    screen.blit(text_surface, text_rect)

    #update the display to show th message after being called in main loop
    pygame.display.update()

    #keep the message for a specific amount of time on screen
    pygame.time.delay(2000)