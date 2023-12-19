import pygame

from abstractions import SupportsEventLoop
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Field, TilePanel, Tile


class Editor(Field, SupportsEventLoop):

    def __init__(self, surface):
        self._tiles_panel = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT // 8))

        y = 15
        w = h = SCREEN_HEIGHT - y - self._tiles_panel.get_height()
        x = (SCREEN_WIDTH - w) // 2

        super().__init__(surface, x, y, w, h)
        self.tile = TilePanel(self._tiles_panel, (Tile('brick.png'), ), 20)
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
            f_pos, f_size = self.get_adjusted()
            fx, fy = self._x + (f_pos[0] - 1) * cell_size[0], self._y + (f_pos[1] - 1) * cell_size[1]
            fw, fh = self._x + f_size[0] * cell_size[0] - fx, self._y + f_size[1] * cell_size[1] - fy
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

    def _get_position_by_mouse_pos(self, current_mouse_pos):
        cx, cy = current_mouse_pos

        if not (self._x < cx < self._x + self._w and self._y < cy < self._y + self._h):
            return

        return (cx - self._x) // int(self.calc_cell_size()[0]), (cy - self._y) // int(self.calc_cell_size()[1])

    def _onclick(self, start_mouse_pos, mouse_button):

        def _inner(current_mouse_pos):
            pos = self._get_position_by_mouse_pos(current_mouse_pos)
            adj = self.get_adjusted()
            print(pos)
            if pos is None:
                return
            if pos[1] in range(adj[0][1], adj[1][1] + 1):
                if not self.get_cells(pos) and mouse_button == 1:
                    self.add_cells(*((pos[0], col) for col in range(adj[0][1], adj[1][1] + 1)))
                elif self.get_cells(pos) and mouse_button == 3:
                    self.remove_cells(*((pos[0], col) for col in range(adj[0][1], adj[1][1] + 1)))
            else:
                if not self.get_cells(pos) and mouse_button == 1:
                    self.add_cells(*((row, pos[1]) for row in range(adj[0][0], adj[1][0] + 1)))
                elif self.get_cells(pos) and mouse_button == 3:
                    print(2)
                    self.remove_cells(*((pos[0], col) for col in range(adj[0][1], adj[1][1] + 1)))

        if self._is_colliding_field(start_mouse_pos, adjust=True, body=False):
            return _inner

    def eventloop(self, *events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._resizer = self._onclick(pygame.mouse.get_pos(), event.button)
            if event.type == pygame.MOUSEBUTTONUP and self._resizer:
                self._resizer = None
            if event.type == pygame.MOUSEMOTION and self._resizer:
                self._resizer(pygame.mouse.get_pos())
        if self._resizer:
            self.grid = (255, 192, 203)
        else:
            self.grid = None

    def draw(self):
        self.tile.draw()
        super().draw()
        for cell in self._cells:
            cell[1].set_border((114, 137, 218), width=3)
