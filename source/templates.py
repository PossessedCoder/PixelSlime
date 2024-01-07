from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import pygame

from constants import FPS, UserEvents
from utils import catch_events, post_event


class BaseSurface(ABC, pygame.Surface):
    # Since BaseSurface class supports resizing, pygame.Surface.get_width(), pygame.Surface.get_height(),
    # pygame.Surface.get_size() methods return fake (initial) values, be careful with its usage. To get actual size of
    # any surface, use BaseSurface.get_rect() method

    def __init__(self, x, y, w, h, parent=None):
        # transparent surface (pygame.SRCALPHA). If surface is transformable, fill it with transparent rect (alpha=0)
        # on every update (e.g. self.fill(255, 255, 255, 0))
        pygame.Surface.__init__(self, (w, h), pygame.SRCALPHA)

        self._rect = self.get_rect(topleft=(x, y))
        self._parent = parent
        self._background = pygame.Color((0, 0, 0))

    @abstractmethod
    def handle(self):
        raise NotImplementedError('child-class must implement method "handle"')

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

    def fill(self, color, rect=None, special_flags=0):
        super().fill(color, rect, special_flags)
        self._background = pygame.Color(color)

    def get_background_color(self):
        return self._background

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

    def blit(self, source, rect=..., **kwargs):
        if rect == Ellipsis:
            try:
                rect = source.get_rect()
            except AttributeError:
                raise ValueError(
                    f'"rect" argument must be provided for classes which does not support "get_rect()" method '
                    f'(Could not get rect of "{source.__class__.__name__}" instance)'
                ) from None
        rect = pygame.Rect(*rect)
        super().blit(pygame.transform.scale(source, rect.size), rect, **kwargs)


class BaseWindow(BaseSurface):

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        post_event(UserEvents.SET_CWW, window=self)

    def handle(self):
        super().handle()


class _SupportsHover(BaseSurface):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self._default_data = {
            'content': None,
            'scale_x': 1,
            'scale_y': 1,
            'border_radius': 0,
            'cursor': pygame.SYSTEM_CURSOR_ARROW
        }

        self._hover_data = self._default_data.copy()
        self._no_hover_data = self._default_data.copy()

    def get_param(self, key, hover):
        c = self._hover_data if hover else self._no_hover_data

        try:
            return c[key]
        except KeyError:
            keys = ', '.join(f'"{k}"' for k in c)
            raise KeyError(f'Unknown key "{key}", available keys: {keys}') from None

    @staticmethod
    def _set_view(collection, *args, **kwargs):
        collection_copy = collection.copy()

        for kw in kwargs:
            collection[kw] = kwargs[kw]
            collection_copy.pop(kw)

        for k, v in zip(collection_copy, args):
            collection[k] = v

    def set_hovered_view(self, content, scale_x=1.0, scale_y=1.0, border_radius=0, cursor=pygame.SYSTEM_CURSOR_ARROW):
        self._set_view(self._hover_data, content.copy(), scale_x, scale_y, border_radius, cursor)

    def set_not_hovered_view(self, content, scale_x=1.0, scale_y=1.0, border_radius=0):
        self._set_view(self._no_hover_data, content.copy(), scale_x, scale_y, border_radius)

    def _draw(self, content, scale_x, scale_y, border_radius):
        self.fill((255, 255, 255, 0))

        self.resize(self.get_width() * scale_x, self.get_height() * scale_y)

        # draw on an initial surface (pygame.Surface) and then resize in parent blit() method
        self.blit(content, rect=pygame.Rect(0, 0, *self.get_size()))
        border = pygame.Surface(self.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(border, (255, 255, 255), (0, 0, *self.get_size()), border_radius=border_radius)
        self.blit(border, rect=pygame.Rect(0, 0, *self.get_size()), special_flags=pygame.BLEND_RGBA_MIN)

    def handle(self):
        if self.get_absolute_rect().collidepoint(*pygame.mouse.get_pos()):
            draw_data = self._hover_data
        else:
            draw_data = self._no_hover_data

        try:
            self._draw(*tuple(draw_data.values())[:-1])
            pygame.mouse.set_cursor(draw_data.get('cursor'))
        except (ValueError, TypeError):
            return


class Button(_SupportsHover):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        # Left, Wheel, Right. Keep this order, it's used in draw()
        self._callbacks_press = {'L': (), 'W': (), 'R': ()}
        self._callbacks_hold = {'L': (), 'W': (), 'R': ()}
        self._callbacks_release = {'L': (), 'W': (), 'R': ()}

        self._held = []

    @staticmethod
    def _get_callbacks(collection, button):
        return collection.get(button, ())

    def get_press_callbacks(self, button):
        return self._get_callbacks(self._callbacks_press, button)

    def get_hold_callbacks(self, button):
        return self._get_callbacks(self._callbacks_hold, button)

    def get_release_callbacks(self, button):
        return self._get_callbacks(self._callbacks_release, button)

    @staticmethod
    def _set_callbacks(collection, button, *callbacks):
        if button not in collection:
            raise ValueError(
                'Literals equality check failed '
                f'(invalid value for "button": expected Literal["L", "W", "R"], got Literal["{button}"] instead)'
            )
        collection[button] = callbacks

    def press(self, button):
        if button in self._held:
            return

        self._invoke(*self._callbacks_press[button])
        self._held.append(button)

    def release(self, button):
        if button not in self._held:
            return

        self._invoke(*self._callbacks_release[button])
        self._held.remove(button)

    def bind_press(self, *callbacks, button='L'):
        self._set_callbacks(self._callbacks_press, button, *callbacks)

    def bind_hold(self, *callbacks, button='L'):
        self._set_callbacks(self._callbacks_hold, button, *callbacks)

    def bind_release(self, *callbacks, button='L'):
        self._set_callbacks(self._callbacks_release, button, *callbacks)

    @staticmethod
    def _invoke(*callbacks):
        for callback in callbacks:
            callback()

    def _eventloop(self):
        for event in catch_events(False):
            try:
                button = tuple(self._callbacks_press.keys())[event.button - 1]
            except (IndexError, AttributeError):
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and self.get_absolute_rect().collidepoint(*pygame.mouse.get_pos()):
                self.press(button)
            if event.type == pygame.MOUSEBUTTONUP:
                self.release(button)
        for hb in self._held:
            self._invoke(*self._callbacks_hold[hb])

    def handle(self, partial=False):
        self._eventloop()
        if not partial:
            super().handle()


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

    def handle(self):
        if self._is_active() and not self.is_maximized():
            additions = self._additions
        elif not (self._is_active() or self.is_minimized()):
            additions = tuple(-addition for addition in self._additions)
        else:
            return

        rect = pygame.Rect(tuple(param + additions[idx] for idx, param in enumerate(self.get_rect())))

        self.resize(*rect.size)
        self.move(*rect.topleft)


class LowerPanel(Panel):

    def __init__(self, minimized_rect, maximized_rect, resize_time, parent=None):
        super().__init__(minimized_rect, maximized_rect, resize_time, parent=parent)

        self._buttons = []
        self._separator_points = ((self.get_rect().w / 5, 0),
                                  (self.get_rect().w / 8, self.get_rect().h))
        self._button_view_not_hovered = (1, 1, 14)
        self._button_view_hovered = (1.05, 1.05, 11)

    @property
    def separator_points(self):
        return self._separator_points

    @property
    def buttons(self):
        return self._buttons.copy()

    # builds standard-setup button with provided content and callbacks (.bind_press(button='L'))
    def build_default_button(self, content, *callbacks):
        btn = Button(*self._calc_button_constraints(), parent=self)
        btn.set_hovered_view(content, *self._button_view_hovered)
        btn.set_not_hovered_view(content, *self._button_view_not_hovered)
        btn.bind_press(*callbacks)
        return btn

    def add_button(self, button):
        self._buttons.append(button)

    def remove_button(self, button):
        # self._calc_button_constraints relies on the length of self._buttons, so we need to clear an array to calculate
        # appropriate position for every button (excluding one to be removed) and push them to the self._buttons array
        self._buttons.remove(button)
        buttons_copy = self._buttons.copy()
        self._buttons.clear()

        for button in buttons_copy:
            button.move(*self._calc_button_constraints()[:2])
            self.add_button(button)

    def _calc_button_constraints(self):
        button_size = self._separator_points[1][0] / 5
        space_between_buttons = button_size / 2
        ttl_btn_size = (space_between_buttons + button_size)
        buttons_surface_width = self._separator_points[1][0]
        buttons_surface_height = self.get_rect().h
        buttons_in_row = int((buttons_surface_width + space_between_buttons) / ttl_btn_size)
        buttons_in_col = int((buttons_surface_height + space_between_buttons) / ttl_btn_size)
        indent_x = (buttons_surface_width - ttl_btn_size * buttons_in_row + space_between_buttons) / 2
        indent_y = (buttons_surface_height - ttl_btn_size * buttons_in_col + space_between_buttons) / 2
        x = indent_x + ttl_btn_size * (len(self._buttons) % buttons_in_row)
        y = indent_y + ttl_btn_size * (max(len(self._buttons) - 1, 0) // buttons_in_col)

        return x, y, button_size, button_size

    def _draw(self):
        self.fill((40, 43, 48))

        pygame.draw.line(self, (98, 98, 98), *self._separator_points)

        for button in self._buttons:
            button.handle()
            self.blit(button)
            if hasattr(button, 'captured'):
                pygame.draw.rect(self, (10, 141, 242), button.get_rect(), width=3)

        if self.is_minimized():
            self.fill(self.get_background_color())

        pygame.draw.line(self, (98, 98, 98), (0, 0), (self.get_rect().w, 0))

    def handle(self):
        super().handle()
        self._draw()
