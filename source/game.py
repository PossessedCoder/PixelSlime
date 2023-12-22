import pygame

from abstractions import AbstractSurface
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


class Field(AbstractSurface):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self._rows, self._cols = 0, 0
        self._cells = []

        self._grid = None

    def _cleanup(self):
        for item in self._cells:
            if 1 < item[0][0] < self._rows and 1 < item[0][1] < self._cols:
                continue
            self._cells.remove(item)

    def calc_cell_size(self, width=..., height=..., rows=..., cols=...):
        width = width if isinstance(width, int) else self.get_width()
        height = height if isinstance(height, int) else self.get_height()
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

        for row, col in map(lambda item: item[0], self.get_cells()):
            if row < min_row:
                min_row = row
            if col < min_col:
                min_col = col
            if row > max_row:
                max_row = row
            if col > max_col:
                max_col = col

        return Coordinates(min_row, min_col), Coordinates(max_row, max_col)

    def get_cells(self, *positions):
        return (item for item in self._cells if not positions or item[0] in positions)

    def add_cells(self, *positions):
        cell_size = self.calc_cell_size()

        for position in positions:
            self.remove_cells(position)  # if cell on this position already exists it will be replaced with new one
            self._cells.append(
                (
                    Coordinates(*position),
                    Cell((position[1] - 1) * cell_size[0], (position[0] - 1) * cell_size[1], *cell_size, parent=self)
                )
            )

        print(self._cells)

    def remove_cells(self, *positions):  # removes all if not provided
        # iterate through reversed enumerate (which doesn't support __iter__, so convert to tuple first)
        # since positions in self._cells changes on each self._cells.pop. self._cells.remove also leads to this bug
        for idx, item in reversed(tuple(enumerate(self._cells))):
            if not positions or item[0] in positions:
                self._cells.pop(idx)

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
        self.fill(self.parent.get_background_color())

        cell_size = self.calc_cell_size()
        for row in range(1, self._rows + 1):
            for col in range(1, self._cols + 1):
                cell = next(self.get_cells((row, col)), None)
                if cell:
                    cell = cell[1]
                    cell.w, cell.h = cell_size
                elif self.grid:
                    cell = Cell(cell_size[0] * (col - 1), cell_size[1] * (row - 1), *cell_size, parent=self)
                    cell.set_border(self.grid, width=1)
                else:
                    continue
                cell.draw()
                self.blit(cell)


class Cell(AbstractSurface):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self._color = None
        self._border: dict[str, str | tuple[int, int, int] | None] = {
            'left': None,
            'top': None,
            'right': None,
            'bottom': None
        }

    def draw(self):
        self.fill(self.parent.get_background_color())

        if self._color:
            pygame.draw.rect(self, self._color, self.get_rect())
        if self._border['left']:
            pygame.draw.line(
                self, self._border['left'][0], (0, 0), (0, self.get_height()), self._border['left'][1]
            )
        if self._border['top']:
            pygame.draw.line(
                self, self._border['top'][0], (0, 0), (self.get_width(), 0), self._border['top'][1]
            )
        if self._border['right']:
            pygame.draw.line(
                self, self._border['right'][0], (self.get_width() - self._border['right'][1], 0), (self.get_width() - self._border['right'][1], self.get_height()), self._border['right'][1]
            )
        if self._border['bottom']:
            pygame.draw.line(
                self, self._border['bottom'][0], (0, self.get_height() - self._border['bottom'][1]), (self.get_width(), self.get_height() - self._border['bottom'][1]), self._border['bottom'][1]
            )

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, clr):
        self._color = clr

    @property
    def border(self):
        return self._border

    def set_border(self, color, left=True, top=True, right=True, bottom=True, width=1):
        update = tuple((('left', 'top', 'right', 'bottom')[idx], (color, width))
                       for idx, val in enumerate((left, top, right, bottom)) if val)

        self._border.update(update)  # type: ignore


class ImageCell(pygame.sprite.Sprite, Cell):
    # Not tested, NOQA. Can work not as expected. Should be used later in editor.TilesPanel and game.Field

    def __init__(self, x, y, w, h, parent=None, sprite_groups=None):
        if sprite_groups is not None:
            super(pygame.sprite.Sprite, self).__init__(*sprite_groups)
        super(Cell, self).__init__(x, y, w, h, parent=parent)
        self._image = None

    @property
    def image(self):
        return self.image

    @image.setter
    def image(self, image_name):
        self._image = load_image(image_name)

    def draw(self):
        super().draw()

        if self._image:
            self.blit(self._image)

    def update(self, *args, **kwargs):
        ...
