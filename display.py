import pygame
import numpy as np

class Display():

    COLORS = {
        0: [212, 252, 217],
        1: [71, 115, 77]
    }

    size = 10
    width = 64
    height = 32

    def __init__(self, name='Chip-8 Emulator'):
        self.grid = np.zeros(shape=(self.height, self.width))

        pygame.init()
        self.disp = pygame.display.set_mode([self.width * self.size, self.height * self.size])
        pygame.display.set_caption(name)
        self.disp.fill(self.COLORS[0])
        pygame.display.flip()

    def get(self, x, y):
        return self.grid[y, x]

    def set(self, x, y, value):
        self.grid[y, x] = value


    def clear(self):
        """
        Clear the display, i.e. set all grid elements to 0
        """
        self.grid = np.zeros(shape=(self.height, self.width))
        # self.draw()

    def draw(self):
        """
        Draw the display according to the grid
        """
        for i in range(self.height):
            for j in range(self.width):
                cell = self.COLORS[self.grid[i, j]]
                pygame.draw.rect(self.disp, cell, [j * self.size, i * self.size, self.size, self.size], 0)

        pygame.display.flip()