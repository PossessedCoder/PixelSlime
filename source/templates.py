from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import pygame

from constants import FPS


class BaseSurface(pygame.Surface):
    # Since BaseSurface class supports resizing, pygame.Surface.get_width(), pygame.Surface.get_height(),
    # pygame.Surface.get_size() methods return fake (initial) values, be careful with its usage. To get actual size of
    # any surface, use BaseSurface.get_rect() method

    def __init__(self, x, y, w, h, parent=None):
        # transparent surface (pygame.SRCALPHA). If surface is transformable, fill it with transparent rect (alpha=0)
        # on every update (e.g. self.fill(255, 255, 255, 0))
        super().__init__((w, h), pygame.SRCALPHA)

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
            rect = super().get_rect(**kwargs)
            try:
                rect.w, rect.h = self._rect.size
            finally:
                return rect
        return self._rect.copy()

    # fake
    def move(self, x=..., y=...):
        if x != Ellipsis:
            self._rect.x = x
        if y != Ellipsis:
            self._rect.y = y

    # fake
    def resize(self, w=..., h=...):  # anchors to center (center of the new rect will have the same center)
        # This method just resizes the rect of the surface, not the surface itself.
        # Real resize happens in the blit() method, which scales a surface to its rect size
        center = self._rect.center
        if w != Ellipsis:
            self._rect.w = w
        if h != Ellipsis:
            self._rect.h = h
        self._rect.center = center

    def get_absolute_rect(self):
        x, y = self._rect.topleft
        parent = self._parent

        while hasattr(parent, 'parent') and parent.parent:
            try:
                addx, addy = parent.get_rect().topleft
                x += addx
                y += addy
            finally:
                parent = parent.parent

        return pygame.Rect(x, y, self._rect.w, self._rect.h)

    def blit(self, source, rect=..., **kwargs):
        if rect == Ellipsis:
            try:
                rect = source.get_rect()
            except AttributeError:
                raise ValueError(
                    f'"rect" argument must be provided for classes which does not support "get_rect()" method '
                    f'(Could not get rect of "{source.__class__.__name__}" instance)'
                ) from None
        super().blit(pygame.transform.scale(source, rect.size), rect, **kwargs)


class BaseWindow(ABC, BaseSurface):

    @abstractmethod
    def eventloop(self, *events):
        raise NotImplemented(f'classes inherited from "{self.__class__.__name__}" must implement method "eventloop"')

    @abstractmethod
    def draw(self):
        raise NotImplemented(f'classes inherited from "{self.__class__.__name__}" must implement method "draw"')


class _SupportsHover(BaseSurface):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self._content_hovered, self._scale_x_hovered, self._scale_y_hovered, self._border_radius_hovered, self._cursor_hovered = None, 1, 1, 0, pygame.SYSTEM_CURSOR_HAND
        self._content_not_hovered, self._scale_x_not_hovered, self._scale_y_not_hovered, self._border_radius_not_hovered = None, 1, 1, 0

    def set_hovered_view(self, content, scale_x=1.0, scale_y=1.0, border_radius=0, cursor=pygame.SYSTEM_CURSOR_HAND):
        self._content_hovered, self._scale_x_hovered, self._scale_y_hovered, self._border_radius_hovered, self._cursor_hovered = content.copy(), scale_x, scale_y, border_radius, cursor

    def set_not_hovered_view(self, content, scale_x=1.0, scale_y=1.0, border_radius=0):
        self._content_not_hovered, self._scale_x_not_hovered, self._scale_y_not_hovered, self._border_radius_not_hovered = content.copy(), scale_x, scale_y, border_radius

    def draw(self):
        self.fill((255, 255, 255, 0))

        # draw on an initial surface (pygame.Surface) and then resize in parent blit() method
        if self.get_absolute_rect().collidepoint(*pygame.mouse.get_pos()):
            self.resize(self.get_width() * self._scale_x_hovered, self.get_height() * self._scale_y_hovered)
            if self._content_hovered:
                self.blit(self._content_hovered, rect=pygame.Rect(0, 0, *self.get_size()))
                border = pygame.Surface(self.get_size(), pygame.SRCALPHA)
                pygame.draw.rect(border, (255, 255, 255), (0, 0, *self.get_size()),
                                 border_radius=self._border_radius_hovered)
                self.blit(border, rect=pygame.Rect(0, 0, *self.get_size()), special_flags=pygame.BLEND_RGBA_MIN)
            pygame.mouse.set_cursor(self._cursor_hovered)  # CHECKME
        else:
            self.resize(self.get_width() * self._scale_x_not_hovered, self.get_height() * self._scale_y_not_hovered)
            if self._content_not_hovered:
                self.blit(self._content_not_hovered, rect=pygame.Rect(0, 0, *self.get_size()))
                border = pygame.Surface(self.get_size(), pygame.SRCALPHA)
                pygame.draw.rect(border, (255, 255, 255), (0, 0, *self.get_size()),
                                 border_radius=self._border_radius_not_hovered)
                self.blit(border, rect=pygame.Rect(0, 0, *self.get_size()), special_flags=pygame.BLEND_RGBA_MIN)


class Panel(BaseSurface):

    def __init__(self, minimized_rect, maximized_rect, resize_time=0.0, parent=None):
        super().__init__(*minimized_rect, parent)

        self._minimized_rect = pygame.Rect(*minimized_rect)
        self._maximized_rect = pygame.Rect(*maximized_rect)

        self._additions = tuple(
            (param_maximized - param_minimized) / (resize_time * FPS if resize_time != 0 else 1)
            for param_maximized, param_minimized in zip(self._maximized_rect, self._minimized_rect)
        )

        self._show_till = datetime.now()

    def maximize(self, duration=float('inf')):
        self._show_till = datetime.now() + timedelta(seconds=duration) if duration != float('inf') else datetime.max

    def minimize(self):
        self._show_till = datetime.now()

    def is_maximized(self):
        return self._is_referenced(maximized=True)

    def is_minimized(self):
        return self._is_referenced(maximized=False)

    def _is_referenced(self, maximized):
        rect = self._maximized_rect if maximized else self._minimized_rect

        return all(
            self._additions[idx] == 0 or abs(param - rect[idx]) < abs(self._additions[idx])
            for idx, param in enumerate(self.get_rect())
        )

    def _is_active(self):
        return self.get_absolute_rect().collidepoint(*pygame.mouse.get_pos()) or self._show_till > datetime.now()

    def draw(self):
        if self._is_active() and not self.is_maximized():
            additions = self._additions
        elif not (self._is_active() or self.is_minimized()):
            additions = tuple(-addition for addition in self._additions)
        else:
            additions = (0,) * 4

        rect = pygame.Rect(tuple(param + additions[idx] for idx, param in enumerate(self.get_rect())))

        self.resize(*rect.size)
        self.move(*rect.topleft)
