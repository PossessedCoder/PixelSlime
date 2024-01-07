from queue import Queue

import pygame

from game import Field
from templates import Panel
from utils import get_tiles


class NotificationsPanel(Panel):

    def __init__(self, minimized_rect, maximized_rect, resize_time, parent=None):
        super().__init__(minimized_rect, maximized_rect, resize_time, parent=parent)

        self._text_surface = pygame.Surface(self._maximized_rect.size, pygame.SRCALPHA)
        self._queue = Queue()

        self._current_notification = (pygame.Surface((0, 0)), pygame.Surface((0, 0)), pygame.Surface((0, 0)))

        # for tile in get_tiles().values():
        #    self.add_notification('Вы открыли новый тайл', 'Доступен в редакторе уровней', load_image(tile.IMAGE_NAME))

    @property
    def current_title(self):
        return self._current_notification[0]

    @property
    def current_text(self):
        return self._current_notification[1]

    @property
    def current_image(self):
        return self._current_notification[2]

    def add_notification(self, title=..., text=..., image=...):
        title = pygame.font.SysFont('serif', 18).render(title if isinstance(title, str) else '', True, (0, 0, 0))
        text = pygame.font.SysFont(
            'arial', 11, italic=True).render(text if isinstance(text, str) else '', True, (69, 69, 69))
        image = pygame.transform.scale(image.copy(), (self.get_height() // 2, self.get_height() // 2)) \
            if isinstance(image, pygame.Surface) else pygame.Surface((0, 0))
        self._queue.put((title, text, image))

    def handle(self):
        if self.is_minimized():
            try:
                self._current_notification = next(self)
                self.maximize(duration=3)
            except StopIteration:
                return

        super().handle()

        self.fill((204, 191, 190))
        self._text_surface.fill((255, 255, 255, 0))

        self._text_surface.blit(
            self.current_title,
            ((self._text_surface.get_width() - self.current_title.get_width() + self.current_image.get_width()) // 2,
             (self._text_surface.get_height() - self.current_title.get_height() - self.current_text.get_height()) // 2)
        )
        self._text_surface.blit(
            self.current_text,
            ((self._text_surface.get_width() - self.current_text.get_width() + self.current_image.get_width()) // 2,
             (self._text_surface.get_height() - self.current_text.get_height() + self.current_title.get_height()) // 2)
        )
        self._text_surface.blit(
            self.current_image,
            (self.current_image.get_width() // 4, self.current_image.get_height() // 2)
        )
        self.blit(
            self._text_surface,
            pygame.Rect(self.get_rect().w - self.get_width(), self.get_rect().h - self.get_height(), *self.get_size())
        )

    def __next__(self):
        if self._queue.empty():
            raise StopIteration('Notifications queue is empty') from None
        return self._queue.get()


class LevelField(Field):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

    # data: dict[str, str | Type[Cell]]
    def setup(self, data):
        cells = []

        for coordinates, factory in data.items():
            factory = get_tiles(factory) if isinstance(factory, str) else factory
            cells.append(factory(self, map(int, coordinates.split())))

        self.add_cells(*cells)
