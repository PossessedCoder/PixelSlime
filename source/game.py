import pygame
from pygame import Rect
from pygame.sprite import Sprite

from utils import load_image


class Field(Sprite):

    def __init__(self, surface, x, y, w, h):
        super().__init__()
        self._surface = surface

        self._x, self._y, self._w, self._h, self._rows, self._cols = x, y, w, h, 0, 0
        self._cells = []

        self._grid_enabled = False

    def _cleanup(self):
        for item in self._cells:
            if 1 < item[0][0] < self._rows and 1 < item[0][1] < self._cols:
                continue
            self._cells.remove(item)

    def _calc_cell_size(self):
        return self._w / self.rows, self._h / self.cols

    def get_cells(self, *positions):
        return list(item for item in self._cells if item[0] in positions) if positions else self._cells

    def set_cells(self, cells):
        self._cells = list(tuple(item) for item in cells)

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        self._rows = value
        self._cleanup()

    @property
    def cols(self):
        return self._cols

    @cols.setter
    def cols(self, value):
        self._cols = value
        self._cleanup()

    @property
    def grid_enabled(self):
        return self._grid_enabled

    @grid_enabled.setter
    def grid_enabled(self, state):
        self._grid_enabled = state

    def draw(self):
        cell_size = self._calc_cell_size()

        for row in range(1, self._rows + 1):
            for col in range(1, self._cols + 1):
                cd = self.get_cells((row, col))
                if cd:
                    cell: Cell = cd[0][1]
                    cell.w, cell.h = cell_size
                elif self.grid_enabled:
                    cell = Cell(self._surface, self._x + cell_size[0] * (col - 1),
                                self._y + cell_size[1] * (row - 1), *cell_size)
                    cell.set_border('white')  # TODO: change color
                else:
                    continue
                cell.draw()


class Cell(Sprite, Rect):

    def __init__(self, surface, x, y, w, h):
        Sprite.__init__(self)
        Rect.__init__(self, x, y, w, h)

        self._surface = surface

        self._image = None
        self._fill = None
        self._border: dict[str, str | tuple[int, int, int]] | dict[str, None] = {
            'left': None,
            'top': None,
            'right': None,
            'bottom': None
        }

    def draw(self):
        if self._image:
            self._surface.blit(self._image, self)
        if self._fill:
            pygame.draw.rect(self._surface, self._fill, self)
        if self._border['left']:
            pygame.draw.line(
                self._surface, self._border['left'][0], self.bottomleft, self.topleft, self._border['left'][1]
            )
        if self._border['top']:
            pygame.draw.line(
                self._surface, self._border['top'][0], self.topleft, self.topright, self._border['top'][1]
            )
        if self._border['right']:
            pygame.draw.line(
                self._surface, self._border['right'][0], self.topright, self.bottomright, self._border['right'][1]
            )
        if self._border['bottom']:
            pygame.draw.line(
                self._surface, self._border['bottom'][0], self.bottomleft, self.bottomright, self._border['bottom'][1]
            )

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image_name):
        self._image = load_image(image_name)

    @property
    def fill(self):
        return self._fill

    @fill.setter
    def fill(self, color):
        self._fill = color

    @property
    def border(self):
        return self._border

    def set_border(self, color, left=True, top=True, right=True, bottom=True, width=1):
        update = tuple((('left', 'top', 'right', 'bottom')[idx], (color, width))
                       for idx, val in enumerate((left, top, right, bottom)) if val)

        self._border.update(update)  # type: ignore

    # def is_covered(mouse_pos):  # No need in this method. self.collidepoint(*mouse_pos) does the same stuff
    #     ...                     # Should be removed

    # override
    # def update(self, *args, **kwargs):  # use this method to update class attributes
    #     ...
