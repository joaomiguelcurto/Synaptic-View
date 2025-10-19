import pygame
from core import config

class Grid:
    """
    Manages the visual rendering of the top-down simulation grid.
    """
    def __init__(self):
        # Grid dimensions are pulled from the central config
        self.cell_size = config.CELL_SIZE
        self.width = config.GRID_WIDTH
        self.height = config.GRID_HEIGHT

    def draw(self, screen: pygame.Surface):
        """
        Draws the checkerboard pattern representing walkable areas.
        """
        for row in range(self.height):
            for col in range(self.width):
                # Determine color based on cell position (checkerboard pattern)
                color = config.GRID_COLOR_1 if (row + col) % 2 == 0 else config.GRID_COLOR_2
                
                # Calculate the screen rectangle coordinates
                rect = pygame.Rect(
                    col * self.cell_size, 
                    row * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
                
                pygame.draw.rect(screen, color, rect)

    def screen_to_grid(self, x: float, y: float) -> tuple[int, int]:
        """ Converts continuous screen coordinates to grid indices (col, row). """
        return int(x // self.cell_size), int(y // self.cell_size)

    def grid_to_screen_center(self, col: int, row: int) -> tuple[float, float]:
        """ Converts grid indices (col, row) to the center pixel coordinates. """
        center_x = col * self.cell_size + self.cell_size / 2
        center_y = row * self.cell_size + self.cell_size / 2
        return center_x, center_y
