import pygame

from abstractions import AbstractSurface
from game import Cell
from utils import load_image
from math import sin, cos, radians


class Hero(Cell):
    class _ArrowVector(AbstractSurface):  # Do not inherit from cell. Field.add_cells() will cause issues

        def __init__(self, x, y, w, h, parent=None):
            super().__init__(x, y, w, h, parent=parent)
            self._angle = 0
            self._image = None
            self._original_image = None

        @property
        def image(self):
            return self._image

        @image.setter
        def image(self, loaded):
            self._image = pygame.transform.scale(loaded, self.get_size())
            self._original_image = self._image.copy()

        def rotate_pivot(self, angle, pivot: tuple):
            self.rotate_center(angle)
            self.move(pivot[0] - cos(radians(angle)) * self.get_rect().centerx,
                      pivot[1] - sin(radians(angle)) * self.get_rect().centery)

        def rotate_center(self, angle):
            self._angle = (self._angle + angle) % 360  # Value will repeat after 359. This prevents angle to overflow.
            self._image = pygame.transform.rotate(self._original_image, self._angle)
            self.resize(*self._image.get_size())

        def draw(self):
            self.fill((255, 255, 255, 0))

            self.blit(self.image)

    def __init__(self, field, coordinates, *groups, arrowed=True):
        super().__init__(field, coordinates, *groups)
        self._arrowed = arrowed

        if self._arrowed:
            self._arrow_vector = self._ArrowVector(*self._get_arrow_vector_rect(), parent=field)
            self._arrow_vector.image = load_image('arrow_vector.svg')

    def _get_arrow_vector_rect(self):
        return pygame.Rect(self.get_rect().x, self.get_rect().y - self.get_height(), *self.get_size())

    def update(self, *events) -> None:
        # self.move(self.get_rect().x + 1, self.get_rect().y + 1)
        self._arrow_vector.move(self._get_arrow_vector_rect().x, self._get_arrow_vector_rect().y)
        ...

    def draw(self):
        super().draw()

        if self._arrowed:
            # self._arrow_vector.rotate_pivot(1.5, self.get_rect().center)
            self._arrow_vector.draw()
            self._field.blit(self._arrow_vector)
