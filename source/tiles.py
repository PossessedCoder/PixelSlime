import math

import pygame

from constants import Media
from game import Cell
from templates import BaseSurface
from utils import load_media, catch_events


class Hero(Cell):
    IMAGE_NAME = Media.HERO
    USAGE_LIMIT = 1

    class _ArrowVector(BaseSurface):  # Do not inherit from cell. Field.add_cells() will cause issues
        IMAGE_NAME = Media.ARROW_VECTOR

        def __init__(self, x, y, w, h, parent=None):
            super().__init__(x, y, w, h, parent=parent)

            self._angle = 0
            self._original_image = pygame.transform.scale(load_media(self.IMAGE_NAME), (w, h))
            self._image = self._original_image.copy()
            self._d_angle = -1
            self._fly = False

        def is_flying(self):
            return self._fly

        @property
        def image(self):
            return self._image.copy()

        @property
        def angle(self):
            return self._angle

        def rotate(self, angle):
            if self._fly:
                return
            if self.angle == 90 or self.angle == 270:
                self._d_angle *= -1
            self._angle = (self.angle + angle * self._d_angle) % 360
            self._image = pygame.transform.rotate(self._original_image, self._angle)

        def draw(self):
            self.fill((255, 255, 255, 0))
            self.blit(self._image)

    def __init__(self, field, coordinates, *groups, arrowed=True):
        super().__init__(field, coordinates, *groups)

        self._arrowed = arrowed
        self.speed = 10
        self.finished = False
        if self._arrowed:
            # will be moved in update (_get_arrow_vector_rect() relies on ArrowVector size)
            self._arrow_vector = self._ArrowVector(-1, -1, *self.get_size(), parent=field)

    def eventloop(self):
        for e in catch_events(False):
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self._arrow_vector._fly = True

    def _get_arrow_vector_rect(self):
        return pygame.Rect(
            self.get_rect().x - (self._arrow_vector.image.get_rect().w - self._arrow_vector.get_width()) / 2,
            self.get_rect().y - self.get_rect().h / 2 - (self._arrow_vector.image.get_rect().h -
                                                         self._arrow_vector.get_height()) / 2,
            *self.get_rect().size
        )

    def update(self, *events):
        self.move(self.get_rect().x, self.get_rect().y)
        self._arrow_vector.move(*self._get_arrow_vector_rect().topleft)
        if self._arrowed:
            self._arrow_vector.rotate(1.5)

        if self._arrow_vector.is_flying():
            angle = self._arrow_vector.angle % 360
            self.move(self.get_rect().x + (abs(math.sin(math.radians(angle))) if angle > 90
                                           else -abs(math.sin(math.radians(angle)))) * self.speed,
                      self.get_rect().y + -abs(math.cos(math.radians(angle))) * self.speed)

            if Spike in self._get_collided_tiles():
                self._death()
            elif Block in self._get_collided_tiles():
                self._arrow_vector._fly = False
            elif Exit in self._get_collided_tiles():
                self._arrow_vector._fly = False
                self.finished = True


    def handle(self):
        super().handle()

        self._arrow_vector.handle()
        self._field.blit(self._arrow_vector)

    def _get_collided_tiles(self):
        collided = dict()

        for t in self.parent.get_cells():
            if t == self or not self.get_rect().colliderect(t.get_rect()):
                continue
            if t.__class__ not in collided:
                collided[t.__class__] = []
            collided[t.__class__].append(t)

        return collided

    def _death(self):
        self.parent.remove_cells(self)


class Block(Cell):
    IMAGE_NAME = Media.BLOCK

    def __init__(self, field, coordinates, *groups):
        super().__init__(field, coordinates, *groups)

    def handle(self):
        super().handle()
        pygame.draw.rect(self._field, (255, 0, 0), self.get_rect(), border_radius=3, width=3)


class Spike(Cell):
    IMAGE_NAME = Media.SPIKE

    def __init__(self, field, coordinates, *groups):
        super().__init__(field, coordinates, *groups)

    def handle(self):
        super().handle()
        pygame.draw.rect(self._field, (255, 0, 0), self.get_rect(), border_radius=3, width=3)


class Exit(Cell):
    IMAGE_NAME = Media.TRASH_BIN

    def __init__(self, field, coordinates, *groups):
        super().__init__(field, coordinates, *groups)

    def handle(self):
        super().handle()
        pygame.draw.rect(self._field, (0, 255, 0), self.get_rect(), border_radius=3, width=3)
