import pygame

from abstractions import SupportsEventLoop
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Field, Coordinates


class Editor(Field, SupportsEventLoop):

    def __init__(self, surface):
        self._tiles_panel = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT // 8))

        y = 15
        w = h = SCREEN_HEIGHT - y - self._tiles_panel.get_height()
        x = (SCREEN_WIDTH - w) // 2

        super().__init__(surface, x, y, w, h)

        self._resizer = None

    def _is_colliding_field(self, current_mouse_pos, adjust=False, body=True, border=True, border_extra_space=10):
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
            fx, fy = self._x + (topleft.col - 1) * cell_size[0], self._y + (topleft.row - 1) * cell_size[1]
            fw, fh = self._x + bottomright.col * cell_size[0] - fx, self._y + bottomright.row * cell_size[1] - fy
        else:
            fx, fy, fw, fh = self._x, self._y, self._w, self._h

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

    def _get_position_by_mouse_pos(self, mouse_pos):
        cx, cy = mouse_pos

        if not self._is_colliding_field(mouse_pos, border=False):
            return

        return Coordinates(
            (cy - self._y) // int(self.calc_cell_size()[1]) + 1, (cx - self._x) // int(self.calc_cell_size()[0]) + 1
        )

    def _onclick(self, start_mouse_pos):
        start_pos = self._get_position_by_mouse_pos(start_mouse_pos)
        start_adj = self.get_adjusted()
        prev_pos = start_pos

        def _inner(current_mouse_pos):
            nonlocal prev_pos

            pos = self._get_position_by_mouse_pos(current_mouse_pos)
            topleft, bottomright = self.get_adjusted()

            if pos is None or pos == prev_pos:
                return  # ignores mouse move if mouse is out of field or previous pos == current pos

            callback = (self.remove_cells if next(self.get_cells(pos), None) else self.add_cells)

            # _is_colliding_field() method provides a border extra space feature,
            # so adjacent cells must also be checked to avoid visual bugs. If you want to expand border_extra_size,
            # you should calculate current cell size and rely on it when check these intersections, but while we're
            # using default spacing, we can just check start_pos[idx] - 1 and start_pos[idx] + 1 cells
            if start_adj[0].col in (start_pos.col, start_pos.col + 1)\
                    or start_adj[1].col in (start_pos.col, start_pos.col - 1):
                point = bottomright if pos.col >= bottomright.col or pos.col >= topleft.col\
                                       and start_adj[1].col in (start_pos.col, start_pos.col - 1) else topleft
                callback(  # type: ignore
                    *(
                        (row, col)
                        for row in range(topleft.row, bottomright.row + 1)
                        for col in range(min(pos.col, point.col), max(pos.col, point.col) + 1)
                    )
                )

            topleft, bottomright = self.get_adjusted()

            if start_adj[0].row in (start_pos.row, start_pos.row + 1)\
                    or start_adj[1].row in (start_pos.row, start_pos.row - 1):
                point = bottomright if pos.row >= bottomright.row or pos.row >= topleft.row\
                                       and start_adj[1].row in (start_pos.row, start_pos.row - 1) else topleft
                callback(  # type: ignore
                    *(
                        (row, col)
                        for row in range(min(pos.row, point.row), max(pos.row, point.row) + 1)
                        for col in range(topleft.col, bottomright.col + 1)
                    )
                )

            if not self._cells:
                self.add_cells(pos)

            prev_pos = pos

        if self._is_colliding_field(start_mouse_pos, adjust=True, body=False) and start_pos is not None:
            return _inner

    def eventloop(self, *events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._resizer = self._onclick(pygame.mouse.get_pos())
                if self._resizer:
                    self.grid = (255, 255, 255)
            if event.type == pygame.MOUSEBUTTONUP and self._resizer:
                self._resizer = None
                self.grid = None
            if event.type == pygame.MOUSEMOTION and self._resizer:
                self._resizer(pygame.mouse.get_pos())

    def add_cells(self, *positions):
        super().add_cells(*positions)

        for cell in self.get_cells(*positions, _map=lambda item: item[1]):
            cell.set_border((114, 137, 218), width=3)
