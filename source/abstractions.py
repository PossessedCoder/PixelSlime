from abc import ABC, abstractmethod

import pygame


class AbstractSurface(pygame.Surface):

    def __init__(self, x, y, w, h, parent=None):
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
            return super().get_rect(**kwargs)
        return self._rect

    def move(self, x=..., y=...):
        if x != Ellipsis:
            self._rect.x = x
        if y != Ellipsis:
            self._rect.y = y

    def resize(self, w=..., h=...):
        if w != Ellipsis:
            self.move(x=self._rect.x + (self._rect.w - w) // 2)
            self._rect.w = w
        if h != Ellipsis:
            self.move(y=self._rect.y + (self._rect.h - h) // 2)
            self._rect.h = h

    def scale(self, coefficient_width=1.0, coefficient_height=1.0):
        self.resize(self.get_width() * coefficient_width, self.get_height() * coefficient_height)

    def get_absolute_rect(self):
        x, y = self.get_rect().topleft
        parent = self._parent

        while hasattr(parent, 'parent') and parent.parent:
            try:
                addx, addy = parent.get_rect().topleft
                x += addx
                y += addy
            except AttributeError:
                continue
            finally:
                parent = parent.parent

        return pygame.Rect(x, y, self.get_width(), self.get_height())

    def is_covered(self, pos):
        return self.get_absolute_rect().collidepoint(*pos)

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


class AbstractWindow(ABC, AbstractSurface):

    @abstractmethod
    def eventloop(self, *events):
        raise NotImplemented(f'classes inherited from "{self.__class__.__name__}" must implement method "eventloop"')

    @abstractmethod
    def draw(self):
        raise NotImplemented(f'classes inherited from "{self.__class__.__name__}" must implement method "draw"')


class AbstractTile(AbstractSurface):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self._image = None
        self._color = None
        self._border = None

    def draw(self):

        if self._color:
            pygame.draw.rect(self, self._color, self.get_rect())
        if self._border:
            pygame.draw.rect(self, self._border, (0, 0, self.get_width(), self.get_height()), 1)
        if self._image:
            self.blit(pygame.transform.scale(self._image, self.get_size()))

    @property
    def image(self):
        return self.image

    @image.setter
    def image(self, loaded):
        self._image = loaded

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, clr):
        self._color = clr

    @property
    def border(self):
        return self._border

    @border.setter
    def border(self, clr):
        self._border = clr

    # CHECKME
    # def set_border(self, clr, left=True, top=True, right=True, bottom=True, width=1):
    #     # Different width of border leads to draw issues:
    #     # Surface's size is constrained, but rectangles' outline needs additional space
    #     # adding partial (left, top, right, bottom) border also causes many problems,
    #     # mainly because of the issue described above.
    #     # Calculating indent for every side looks ugly and bugging even though
    #     raise NotImplemented


class _SupportsHover(AbstractSurface):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)
        self._content_hovered, self._scale_x_hovered, self._scale_y_hovered, self._border_radius_hovered = None, 0, 1, 1
        self._content_not_hovered, self._scale_x_not_hovered, self._scale_y_not_hovered, self._border_radius_not_hovered = None, 0, 1, 1

    def set_content_hovered(self, content, scale_x=1, scale_y=1, border_radius=0):
        self._content_hovered, self._border_radius_hovered, self._scale_x_hovered, self._scale_y_hovered = content, scale_x, scale_y, border_radius

    def set_content_not_hovered(self, content, scale_x=1, scale_y=1, border_radius=0):
        self._content_not_hovered, self._scale_x_not_hovered, self._scale_y_not_hovered, self._border_radius_not_hovered = content, scale_x, scale_y, border_radius

    def draw(self):  # CHECKME: not implemented
        self.fill(self.parent.get_background_color())

        if self.is_covered(pygame.mouse.get_pos()):
            if self._content_hovered:
                self.blit(self._content_hovered)
            self.scale(1 + self._scale_x, 1 + self._scale_y)
            return

        if self._content_not_hovered:
            self.blit(self._content_not_hovered)
        self.scale(1 - self._scale_x, 1 - self._scale_y)


class Panel(ABC, AbstractSurface):

    class _Button(AbstractSurface):

        def __init__(self, x, y, w, h, parent=None, text=None, view=None):
            super().__init__(x, y, w, h, parent=parent)

            self.text = text
            self.view = view
            self.border_color = None
            self.border_radius = 0

        def draw(self):
            self.fill(self.parent.get_background_color())

            if self.is_covered(pygame.mouse.get_pos()):
                fill = (87, 100, 230)
                self.border_radius = 14
                self.scale(1.5, 1.5)
            else:
                fill = (98, 106, 189)
                self.border_radius = 15
                self.scale(0.5, 0.5)
            pygame.draw.rect(self, fill, (0, 0, *self.get_size()), border_radius=self.border_radius)

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)

        self._buttons = []
        self._content = None
        self._additional = None

    def add_buttons(self, *images):
        for image in images:
            self._buttons.append(self._Button(5, 5, 45, 45, self, view=image))

    def remove_buttons(self, *buttons):
        ...

    def draw(self):
        for button in self._buttons:
            button.draw()
            self.blit(button)
