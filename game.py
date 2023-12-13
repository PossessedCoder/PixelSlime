import pygame

from mixins import ArrangementMixin
from pygame import Rect


class Cell(ArrangementMixin):

    def __init__(self, x, y, w, h, image):
        self.image = image
        super().__init__(x, y, w, h)

    def get_rect(self):
        return pygame.Rect(self._x, self._y, self._w, self._h)


class Block(Cell):
    def __init__(self, x, y, w, h, image):
        super().__init__(x, y, w, h, image)

    def collision(self, other):
        # type(other) == pygame.Rect
        return Rect.colliderect(self.get_rect(), other)
