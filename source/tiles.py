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

            self.angle = 0
            self._original_image = pygame.transform.scale(load_media(self.IMAGE_NAME), (w, h))
            self._image = self._original_image.copy()
            self.d_angle = -1
            self.border_1, self.border_2 = 90, 270
            self._fly = False
            self.direction_rl, self.direction_ud = 1, 1

        @property
        def flying(self):
            return self._fly

        @flying.setter
        def flying(self, value):
            self._fly = value

        @property
        def image(self):
            return self._image.copy()

        @property
        def angle(self):
            return self._angle

        def rotate(self, angle):
            if self._fly:
                return
            if self.angle == self.border_1 or self.angle == self.border_2:
                self.d_angle *= -1
            self.angle = (self.angle + angle * self.d_angle) % 360
            self._image = pygame.transform.rotate(self._original_image, self.angle)

        def draw(self):
            self.fill((255, 255, 255, 0))
            self.blit(self._image)

    def __init__(self, field, coordinates, *groups, arrowed=True):
        super().__init__(field, coordinates, *groups)

        self._arrowed = arrowed
        self._speed = 10
        self._finished = False
        self._dead = False
        self.angle = 0
        if self._arrowed:
            # will be moved in update (_get_arrow_vector_rect() relies on ArrowVector size)
            self._arrow_vector = self._ArrowVector(-1, -1, *self.get_size(), parent=field)

    @property
    def finished(self):
        return self._finished

    @property
    def dead(self):
        return self._dead

    def eventloop(self):
        for e in catch_events(False):
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self._arrow_vector.flying = True

    def _get_arrow_vector_rect(self):
        return pygame.Rect(
            self.get_rect().x - (self._arrow_vector.image.get_rect().w - self._arrow_vector.get_width()) / 2,
            self.get_rect().y - self.get_rect().h / 2 - (self._arrow_vector.image.get_rect().h -
                                                         self._arrow_vector.get_height()) / 2,
            *self.get_rect().size
        )

    def update(self):
        self.move(self.get_rect().x, self.get_rect().y)
        self._arrow_vector.move(*self._get_arrow_vector_rect().midleft)
        if self._arrowed:
            self._arrow_vector.rotate(1.5)

        if self._arrow_vector.flying:
            if self._arrow_vector.border_1 == 90:
                angle = self._arrow_vector.angle - 90 % 360
                self.move(self.get_rect().x + -math.cos(math.radians(angle)) * self._speed,
                          self.get_rect().y + math.sin(math.radians(angle)) * self._speed)
            else:
                angle = self._arrow_vector.angle % 360
                self.move(self.get_rect().x + -math.sin(math.radians(angle)) * self._speed,
                          self.get_rect().y + -math.cos(math.radians(angle)) * self._speed)
            # self.move(self.get_rect().x + (
            #     abs(math.sin(math.radians(angle))) if angle > 90
            #     else -abs(math.sin(math.radians(angle)))) * self._speed,
            #           self.get_rect().y + -abs(math.cos(math.radians(angle))) * self._speed)

            if Spike in self._get_collided_tiles():
                self._dead = True
                self._arrow_vector.flying = False
            elif Exit in self._get_collided_tiles():
                self._arrow_vector.flying = False
                self._finished = True
            elif Block in self._get_collided_tiles():
                self._arrow_vector.flying = False

                o, s = self._get_collided_tiles()[Block][0].get_rect(), self.get_rect()
                for el in self._get_collided_tiles()[Block]:
                    if el.get_rect().collidepoint(s.midtop) or el.get_rect().collidepoint(s.midright) \
                            or el.get_rect().collidepoint(s.midleft) or el.get_rect().collidepoint(s.midbottom):
                        o = el.get_rect()
                if o.collidepoint(s.midleft) or o.collidepoint(s.midright):
                    if o.collidepoint(s.midright):
                        self.right_collide(s, o)
                    else:
                        self.left_collide(s, o)
                elif o.collidepoint(s.midbottom) or o.collidepoint(s.midtop):
                    if o.collidepoint(self.get_rect().midbottom):
                        self.bottom_collide(s, o)
                    else:
                        self.top_collide(s, o)

                else:
                    print(s, o)
                    print(s.left, s.bottom, s.right, s.top)
                    print(o.left, o.bottom, o.right, o.top)
                    if o.collidepoint(s.topright):
                        print('1')
                        if abs(o.left - s.right) > abs(o.bottom - s.top):
                            self.right_collide(s, o)
                        else:
                            self.top_collide(s, o)
                    elif o.collidepoint(s.topleft):
                        print('2')
                        if abs(o.left - s.left) > abs(o.bottom - s.top):
                            self.left_collide(s, o)
                        else:
                            self.top_collide(s, o)
                    elif o.collidepoint(s.bottomleft):
                        print('3')
                        if abs(o.right - s.left) > abs(o.top - s.bottom):
                            self.left_collide(s, o)
                        else:
                            self.bottom_collide(s, o)
                    elif o.collidepoint(s.bottomright):
                        print('4')
                        if abs(o.left - s.right) > abs(o.top - s.bottom):
                            self.right_collide(s, o)
                        else:
                            self.bottom_collide(s, o)

            for cord in (self.get_absolute_rect().topleft, self.get_absolute_rect().topright,
                         self.get_absolute_rect().bottomleft, self.get_absolute_rect().bottomright):
                if not self.parent.is_colliding_field(cord, border=False):
                    self._dead = True

    def right_collide(self, s, o):
        self._image = pygame.transform.scale(load_media(Media.HERO_RIGHT),
                                             (self.get_rect().w, self.get_rect().h))
        self._arrow_vector.angle = 90
        print('right')
        self._arrow_vector.border_1, self._arrow_vector.border_2 = 0, 180
        self._arrow_vector.direction_ud = 1

        self.move(o.left - o.width, s.y)

    def left_collide(self, s, o):
        self._image = pygame.transform.scale(load_media(Media.HERO_LEFT),
                                             (self.get_rect().w, self.get_rect().h))
        print('left')
        self._arrow_vector.angle = 270
        self._arrow_vector.border_1, self._arrow_vector.border_2 = 0, 180
        # self._arrow_vector.direction_rl = -1
        self.move(o.right, s.y)

    def bottom_collide(self, s, o):
        self._arrow_vector.angle = 0
        self._image = pygame.transform.scale(load_media(Media.HERO),
                                             (self.get_rect().w, self.get_rect().h))
        self.angle = 0
        print('bottom')
        self._arrow_vector.border_1, self._arrow_vector.border_2 = 90, 270
        self._arrow_vector.direction_ud = 1
        self.move(s.x, o.top - o.h)

    def top_collide(self, s, o):
        self._arrow_vector.angle = 180
        self.angle = 180
        self._image = pygame.transform.scale(load_media(Media.HERO_TOP),
                                             (self.get_rect().w, self.get_rect().h))
        print('top')
        self._arrow_vector.border_1, self._arrow_vector.border_2 = 90, 270
        self._arrow_vector.direction_ud = -1
        self.move(s.x, o.bottom)

    def draw(self):
        self.fill((255, 255, 255, 0))
        super().draw()

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


class Block(Cell):
    IMAGE_NAME = Media.BLOCK


class Spike(Cell):
    IMAGE_NAME = Media.SPIKE

    def __init__(self, field, coordinates, *groups):
        super().__init__(field, coordinates, *groups)
        x, y, w, h = self.get_rect()

    def draw(self):
        super().draw()
        pygame.draw.rect(self._field, (255, 0, 0), self._rect, border_radius=3, width=3)


class Exit(Cell):
    IMAGE_NAME = Media.END_LEVEL
    USAGE_LIMIT = 1
    MIN_USAGE = 1
