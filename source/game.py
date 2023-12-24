import pygame
from dataclasses import dataclass

from abstractions import AbstractSurface, AbstractTile


@dataclass(eq=True, slots=True)
class Coordinates:
    row: int
    col: int

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


class Field(AbstractSurface):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        # different number of rows and cols is available but highly not recommended
        self._rows, self._cols = 0, 0
        self._cells = pygame.sprite.Group()

        self._grid = None

    def _cleanup(self):
        for cell in self._cells:  # remove cells created outside the field
            if not (1 <= cell.start_coordinates.row <= self.rows and 1 <= cell.start_coordinates.col <= self.cols):
                self.remove_cells(cell)
        cell_size = self.calc_cell_size()
        if cell_size:
            self.resize(cell_size[0] * self.cols, cell_size[1] * self.rows)

    def get_position_by_mouse_pos(self, mouse_pos):
        cx, cy = mouse_pos

        if not self.is_colliding_field(mouse_pos, border=False):
            return

        return Coordinates(
            (cy - self.get_rect().y) // int(self.calc_cell_size()[1]) + 1,
            (cx - self.get_rect().x) // int(self.calc_cell_size()[0]) + 1
        )

    def is_colliding_field(self, current_mouse_pos, adjust=False, body=True, border=True, border_extra_space=10):
        """
        Checks if specified parts of field are covered by mouse

         .. note::
             border_extra_space works if only border=True

        :param current_mouse_pos: current mouse position, can be got with pygame.mouse.get_pos()
        :param adjust: checks collision with field has minimal number of rows and cols
        :param body: checks collision with cells
        :param border: checks collision with border
        :param border_extra_space: adds extra border space when checks border collision

        :returns: :class:`bool`
        """

        cx, cy = current_mouse_pos

        cell_size = self.calc_cell_size()
        if adjust:
            topleft, bottomright = self.get_adjusted()
            fx = self.get_rect().x + (topleft.col - 1) * cell_size[0]
            fy = self.get_rect().y + (topleft.row - 1) * cell_size[1]
            fw = self.get_rect().x + bottomright.col * cell_size[0] - fx
            fh = self.get_rect().y + bottomright.row * cell_size[1] - fy
        else:
            fx, fy, fw, fh = self.get_rect()

        if body and fx < cx < fx + fw and fy < cy < fy + fh:
            return True
        if border:
            return (
                    fx - border_extra_space < cx < fx + border_extra_space and fy < cy < fy + fh
                    or fy - border_extra_space < cy < fy + border_extra_space and fx < cx < fx + fw
                    or fx + fw - border_extra_space < cx < fx + fw + border_extra_space and fy < cy < fy + fh
                    or fy + fh - border_extra_space < cy < fy + fh + border_extra_space and fx < cx < fx + fw
            )

        return False

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

        for row, col in map(lambda cell: cell.coordinates, self.get_cells()):
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
        return (cell for cell in self._cells.sprites() if not positions or cell.coordinates in positions)

    def add_cells(self, *cells):
        for cell in cells:
            self.remove_cells(cell.start_coordinates)  # replaces cell on cell.coordinates if it's already exists
            self._cells.add(cell)  # type: ignore
        self._cleanup()

    def remove_cells(self, *cells):  # removes all if not provided
        # iterate through reversed enumerate (which doesn't support __iter__, so convert to tuple first)
        # since positions in self._cells changes on each self._cells.pop. self._cells.remove also leads to this bug
        self._cells.remove(*cells)

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

    def _draw_grid(self):
        for row in range(1, self._rows + 1):
            for col in range(1, self._cols + 1):
                cell = Cell(self, (row, col))
                cell.border = self.grid
                cell.draw()
                self.blit(cell)

    def _draw_cells(self):
        for cell in self._cells:
            cell.update()
            cell.draw()
            self.blit(cell)

    def draw(self):
        self.fill(self.parent.get_background_color())

        if self.grid:
            self._draw_grid()
        self._draw_cells()


class Cell(pygame.sprite.Sprite, AbstractTile):

    def __init__(self, field, coordinates, *groups):
        self._field = field

        self._start_coordinates = Coordinates(*coordinates)
        w, h = field.calc_cell_size()
        x, y = (self._start_coordinates.col - 1) * w, (self._start_coordinates.row - 1) * h

        pygame.sprite.Sprite.__init__(self, *groups)
        AbstractTile.__init__(self, x, y, w, h, parent=field)

        self._image = None
        self._color = None
        self._border = None

    @property
    def start_coordinates(self):
        return self._start_coordinates
