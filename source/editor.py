import pygame

from constants import SCREEN_SIZE
from game import Field


class Editor(Field):

    def __init__(self, surface):
        super().__init__(surface, 0, 0, *SCREEN_SIZE)


if __name__ == '__main__':
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    editor = Editor(screen)
    editor.rows, editor.cols = 30, 30
    editor.grid_enabled = True

    while True:
        editor.draw()

        pygame.display.flip()
        clock.tick(60)
