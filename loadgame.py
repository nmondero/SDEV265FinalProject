import pygame
import os
SAVEFILE_DIRECTORY_NAME = "savefiles/"


class LoadGame:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.files = os.listdir(SAVEFILE_DIRECTORY_NAME)
        self. = []

        for file in files:
