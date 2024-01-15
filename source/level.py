from queue import Queue

import pygame

from game import Field
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, Media, UserEvents
from templates import Panel, BaseWindow, LowerPanel, Button
from utils import get_tiles, load_media, post_event


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


class StartPanel(LowerPanel):

    def __init__(self, minimized_rect, maximized_rect, resize_time=0.0, parent=None):
        super().__init__(minimized_rect, maximized_rect, resize_time, parent=parent)
        if self._maximized_rect.collidepoint(pygame.mouse.get_pos()):
            self.move(*self._maximized_rect.topleft)

        buttons_not_hovered_view = {'scale_x': 1, 'scale_y': 1, 'border_radius': 14}
        buttons_hovered_view = {'scale_x': 1.05, 'scale_y': 1.05, 'border_radius': 11}
        buttons_data = (
            (Media.CLOSE_WINDOW, (lambda: post_event(UserEvents.CLOSE_CWW),)),
        )

        for image_name, callbacks in buttons_data:
            btn = Button(-1, -1, 50, 50, parent=self)
            buttons_hovered_view['content'] = load_media(image_name)
            buttons_not_hovered_view['content'] = load_media(image_name)
            btn.set_hovered_view(**buttons_hovered_view)
            btn.set_not_hovered_view(**buttons_not_hovered_view)
            btn.bind_press(*callbacks)
            self.add_button(btn)


class Level(BaseWindow):

    def __init__(self, data):
        super().__init__()

        self._start_panel = StartPanel(
            (0, SCREEN_HEIGHT // 18 * 17, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            (0, SCREEN_HEIGHT // 6 * 5, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            resize_time=0.3,
            parent=self
        )

        y = 15
        w = h = SCREEN_HEIGHT - y * 2 - (SCREEN_HEIGHT - SCREEN_HEIGHT // 18 * 17)
        x = (SCREEN_WIDTH - w) // 2

        self._field = Field(x, y, w, h, parent=self)

        self._field.rows, self._field.cols = 15, 15
        self._field.grid = (255, 255, 255)

        self._setup_field(data)

    # data: dict[str, str | Type[Cell]]
    def _setup_field(self, data):
        g = get_tiles()
        cells = []

        for coordinates, factory in data:
            cells.append(factory(self._field, coordinates))

        self._field.add_cells(*cells)

    def draw(self):
        self.fill((54, 57, 62))

        self._field.handle()
        self.blit(self._field)
        self._start_panel.handle()
        self.blit(self._start_panel)
