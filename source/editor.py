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

        def _inner(current_mouse_pos):
            pos = self._get_position_by_mouse_pos(current_mouse_pos)
            adj = self.get_adjusted()

        if self._is_colliding_field(start_mouse_pos, adjust=True, body=False):
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
