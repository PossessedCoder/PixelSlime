from abc import ABC, abstractmethod

import pygame


class AbstractSurface(pygame.Surface):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__((w, h))

        self._rect = self.get_rect(topleft=(x, y))
        self._parent = parent
        self._background = pygame.Color((0, 0, 0))

    def fill(self, color, rect=None, special_flags=0):
        super().fill(color, rect, special_flags)
        self._background = pygame.Color(color)

    def get_background_color(self):
        return self._background

    @property
    def parent(self):
        return self._parent

    def get_rect(self, **kwargs):
        if kwargs:
            return super().get_rect(**kwargs)
        return self._rect

    def move(self, x=..., y=...):
        if x != Ellipsis:
            self._rect.x = x
        if y != Ellipsis:
            self._rect.y = y

    def resize(self, w=..., h=...):
        if w != Ellipsis:
            self._rect.w = w
        if h != Ellipsis:
            self._rect.h = h

    def blit(self, source, rect=..., **kwargs):
        if rect == Ellipsis:
            try:
                rect = source.get_rect()
            except AttributeError:
                raise ValueError(
                    f'"rect" argument must be provided for classes which does not support "get_rect()" method '
                    f'(Could not get rect of "{source.__class__.__name__}" instance)'
                ) from None
        super().blit(source, rect, **kwargs)


class AbstractWindow(ABC, AbstractSurface):

    @abstractmethod
    def eventloop(self, *events):
        raise NotImplemented(f'classes inherited from "{self.__class__.__name__}" must implement method "eventloop"')

    @abstractmethod
    def draw(self):
        raise NotImplemented(f'classes inherited from "{self.__class__.__name__}" must implement method "draw"')
