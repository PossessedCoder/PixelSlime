import pygame

from abstractions import SupportsDraw
from utils import load_image


class Coordinates:

    def __init__(self, row, col):
        self._row, self._col = row, col

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        self._row = value

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, value):
        self._col = value

    def __iter__(self):  # unpack (e.g. "row, col = Coordinates(1, 1)")
        return iter((self.row, self.col))

    def __getitem__(self, idx):
        if idx not in (0, 1):
            raise ValueError('Index must be 0 - row or 1 - column')

        return self.row if idx == 0 else self.col

    def __setitem__(self, idx, value):
        if idx == 0:
            self.row = value
            return

        if idx == 1:
            self.col = value
            return

        raise ValueError('Index must be 0 - row or 1 - column')

    def __eq__(self, other):
        return (self.row, self.col) == (other[0], other[1])

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f'<Coordinates({self.row}, {self.col})>'


class Field(SupportsDraw):

    def __init__(self, surface, x, y, w, h):
        self._surface = surface

        self._x, self._y, self._w, self._h, self._rows, self._cols = x, y, w, h, 0, 0
        self._cells = []

        self._grid = None

    def _cleanup(self):
        for item in self._cells:
            if 1 < item[0][0] < self._rows and 1 < item[0][1] < self._cols:
                continue
            self._cells.remove(item)

    def calc_cell_size(self, width=..., height=..., rows=..., cols=...):
        width = width if isinstance(width, int) else self._w
        height = height if isinstance(height, int) else self._h
        rows = rows if isinstance(rows, int) else self._rows
        cols = cols if isinstance(cols, int) else self._cols

        try:
            return width / cols, height / rows
        except ZeroDivisionError:
            return

    def get_adjusted(self):
        """
        adjusts rows and cols while first non-empty cell will not occur

        :returns: tuple[tuple[int, int], tuple[int, int]] - left top point, right bottom point
        """

        if not self._cells:
            return Coordinates(1, 1), Coordinates(1, 1)

        min_row, min_col, max_row, max_col = self._rows, self._cols, 1, 1

        for row, col in self.get_cells(_map=lambda item: item[0]):
            if row < min_row:
                min_row = row
            if col < min_col:
                min_col = col
            if row > max_row:
                max_row = row
            if col > max_col:
                max_col = col

        return Coordinates(min_row, min_col), Coordinates(max_row, max_col)

    def get_cells(self, *positions, _map=None):
        return [_map(item) if callable(_map) else item for item in self._cells if not positions or item[0] in positions]

    def add_cells(self, *positions):  # Iterable[int, int] acceptable
        cell_size = self.calc_cell_size()

        for position in positions:
            self.remove_cells(position)
            self._cells.append((Coordinates(*position), Cell(self._surface, self._x + (position[1] - 1) * cell_size[0],
                                                             self._y + (position[0] - 1) * cell_size[1], *cell_size)))

    def remove_cells(self, *positions):  # removes all if not provided
        for item in self._cells:
            if not positions or item[0] in positions:
                self._cells.remove(item)

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
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, color):
        self._grid = color

    def draw(self):
        cell_size = self.calc_cell_size()

        for row in range(1, self._rows + 1):
            for col in range(1, self._cols + 1):
                cd = self.get_cells((row, col), _map=lambda item: item[1])
                if cd:
                    cell = cd[0]  # only one cell can be found on pos (row, col)
                    cell.w, cell.h = cell_size
                elif self.grid:
                    cell = Cell(self._surface, self._x + cell_size[0] * (row - 1),
                                self._y + cell_size[1] * (col - 1), *cell_size)
                    cell.set_border(self.grid, width=1)
                else:
                    continue
                cell.draw()


class Cell(pygame.Rect, SupportsDraw):

    def __init__(self, surface, x, y, w, h):
        super().__init__(x, y, w, h)

        self._surface = surface

        self._image = None
        self._fill = None
        self._border: dict[str, str | tuple[int, int, int] | None] = {
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
