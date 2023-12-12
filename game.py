class ArrangementMixin:

    def __init__(self, x, y, w, h):
        self._x, self._y, self._w, self._h = x, y, w, h

    def is_covered(self, mouse_pos):
        return self._x < mouse_pos[0] < self._x + self._w and self._y < mouse_pos[1] < self._y + self._h


class Cell(ArrangementMixin):

    def __init__(self, x, y, w, h, image):
        self.image = image
        super().__init__(x, y, w, h)
