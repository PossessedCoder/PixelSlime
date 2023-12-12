from mixins import ArrangementMixin


class Cell(ArrangementMixin):

    def __init__(self, x, y, w, h, image):
        self.image = image
        super().__init__(x, y, w, h)
