import pygame

from abstractions import AbstractWindow, Panel
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_SIZE
from game import Field
from tiles import Hero
from utils import load_image


class TilesPanel(Panel):

    def onclick(self):
        ...

    def draw(self):
        self.fill((40, 43, 48))
        super().draw()


class Editor(AbstractWindow):

    def __init__(self):
        super().__init__(0, 0, *SCREEN_SIZE)

        self._tiles_panel = TilesPanel(0, SCREEN_HEIGHT // 6 * 5, SCREEN_WIDTH, SCREEN_HEIGHT // 6, parent=self)
        self._tiles_panel.add_buttons(load_image('test_tile.png'))

        y = 15
        w = h = SCREEN_HEIGHT - y * 2 - self._tiles_panel.get_height()
        x = (SCREEN_WIDTH - w) // 2

        self._field = Field(x, y, w, h, parent=self)

        self._field.rows, self._field.cols = 20, 20
        self._field.grid = (255, 255, 255)
        hero = Hero(self._field, (5, 5))
        self._field.add_cells(hero)
        hero.image = load_image('test_tile.png')

    def eventloop(self, *events):
        ...

    def draw(self):
        self.fill((54, 57, 62))
        self._field.draw()
        self._tiles_panel.draw()
        self.blit(self._field)
        self.blit(self._tiles_panel)
