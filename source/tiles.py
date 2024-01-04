import pygame

from templates import BaseSurface
from game import Cell
from utils import load_image


class Hero(Cell):
    IMAGE_NAME = 'test_tile.png'

    class _ArrowVector(BaseSurface):  # Do not inherit from cell. Field.add_cells() will cause issues
        IMAGE_NAME = 'arrow_vector.png'

        def __init__(self, x, y, w, h, parent=None):
            super().__init__(x, y, w, h, parent=parent)
            self._angle = 0
            self._image = None
            self._original_image = pygame.transform.scale(load_image(self.IMAGE_NAME), (w, h))

        @property
        def angle(self):
            return self._angle

        # no need in this property. Image is only used in instances of _ArrowVector
        # @property
        # def image(self):
        #     return self._image.copy()

        def rotate(self, angle):
            self._angle = (self._angle + angle) % 360  # Value will repeat after 359. This prevents angle to overflow.
            self._image = pygame.transform.rotate(self._original_image, self._angle)

        def draw(self):
            self.fill((255, 255, 255, 0))
            self.blit(self._image)

    def __init__(self, field, coordinates, *groups, arrowed=True):
        super().__init__(field, coordinates, *groups)
        self._arrowed = arrowed

        if self._arrowed:
            self._arrow_vector = self._ArrowVector(*self._get_arrow_vector_rect(), parent=field)

    def _get_arrow_vector_rect(self):
        return pygame.Rect(self.get_rect().x, self.get_rect().y - self.get_height(), *self.get_size())

    def update(self, *events) -> None:
        self.move(self.get_rect().x + 1, self.get_rect().y + 1)
        self._arrow_vector.move(*self._get_arrow_vector_rect().topleft)

    def draw(self):
        super().draw()

        if self._arrowed:
            self._arrow_vector.rotate(1.5)
            self._arrow_vector.draw()
            self._field.blit(self._arrow_vector)
