import pygame

from abstractions import AbstractSurface, AbstractWindow
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_SIZE
from game import Field, Coordinates


class TilesPanel(AbstractSurface):

    def eventloop(self, *events):
        ...

    def draw(self):
        self.fill((40, 43, 48))


class EditorField(Field):

    def _get_position_by_mouse_pos(self, mouse_pos):
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


class Editor(AbstractWindow):

    def __init__(self):
        super().__init__(0, 0, *SCREEN_SIZE)

        self._tiles_panel = TilesPanel(0, SCREEN_HEIGHT // 6 * 5, SCREEN_WIDTH, SCREEN_HEIGHT // 6, parent=self)

        y = 15
        w = h = SCREEN_HEIGHT - y - self._tiles_panel.get_height()
        x = (SCREEN_WIDTH - w) // 2

        self._field = EditorField(x, y, w, h, parent=self)

        test_positions = (1, 2), (15, 15), (14, 2), (24, 9), (25, 25)
        self._field.rows, self._field.cols = 25, 25
        self._field.grid = (255, 255, 255)
        self._field.add_cells(*test_positions)
        for cl in map(lambda item: item[1], self._field.get_cells(*test_positions)):
            cl.set_border((114, 137, 218), width=3)

    def eventloop(self, *events):
        ...

    def draw(self):
        self.fill((54, 57, 62))
        self._field.draw()
        self._tiles_panel.draw()
        self.blit(self._field)
        self.blit(self._tiles_panel)
