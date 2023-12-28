import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_SIZE, Images
from game import Field
from templates import BaseWindow, Panel, _SupportsHover
from tiles import Hero
from utils import load_image


class TilesPanel(Panel):

    def __init__(self, minimized_rect, maximized_rect, resize_time, parent=None):
        super().__init__(minimized_rect, maximized_rect, resize_time, parent=parent)

        self._buttons = []
        self._content = None
        self._additional = None

        # TODO: remove code below. Test of buttons
        btn = _SupportsHover(35, 35, 45, 45, parent=self)
        btn.set_not_hovered_view(load_image(Images.BACK), border_radius=14)
        btn.set_hovered_view(load_image(Images.BACK), 1.05, 1.05, border_radius=11)
        self._buttons.append(btn)
        btn = _SupportsHover(100, 35, 45, 45, parent=self)
        btn.set_not_hovered_view(load_image(Images.FORWARD), border_radius=14)
        btn.set_hovered_view(load_image(Images.FORWARD), 1.05, 1.05, border_radius=11)
        self._buttons.append(btn)
        btn = _SupportsHover(35, 100, 45, 45, parent=self)
        btn.set_not_hovered_view(load_image(Images.CLOSE), border_radius=14)
        btn.set_hovered_view(load_image(Images.CLOSE), 1.05, 1.05, border_radius=11)
        self._buttons.append(btn)

    def draw(self):
        self.fill((40, 43, 48))
        super().draw()

        if self.is_minimized():
            return

        for button in self._buttons:
            button.draw()
            self.blit(button, rect=pygame.Rect(self.get_rect().w - self.get_width() + button.get_rect().x,
                                               self.get_rect().h - self.get_height() + button.get_rect().y,
                                               *button.get_rect().size))


class NotificationsPanel(Panel):

    def __init__(self, minimized_rect, maximized_rect, resize_time, parent=None):
        super().__init__(minimized_rect, maximized_rect, resize_time, parent=parent)

        self._text_surface = pygame.Surface(self._maximized_rect.size, pygame.SRCALPHA)
        self._queue = []

        self._current_notification = (pygame.Surface((0, 0)), pygame.Surface((0, 0)), pygame.Surface((0, 0)))

        # TODO: remove code below. Test of notifications
        self.add_notification('Вы открыли новый тайл', 'Доступен в редакторе уровней', load_image(Images.HERO))
        self.add_notification('Вы открыли новый тайл', 'Доступен в редакторе уровней', load_image(Images.BACK))

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
        image = pygame.transform.scale(image.copy(), (self.get_height() // 2, self.get_height() // 2))\
            if isinstance(image, pygame.Surface) else pygame.Surface((0, 0))
        self._queue.append((title, text, image))

    def draw(self):
        if self.is_minimized():
            try:
                self._current_notification = next(self)
                self.maximize(duration=3)
            except StopIteration:
                return

        super().draw()

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
        try:
            return self._queue.pop(0)
        except IndexError:
            raise StopIteration('Notifications queue is empty') from None


class Editor(BaseWindow):

    def __init__(self):
        super().__init__(0, 0, *SCREEN_SIZE)

        self._tiles_panel = TilesPanel(
            (0, SCREEN_HEIGHT // 18 * 17, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            (0, SCREEN_HEIGHT // 6 * 5, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            resize_time=0.3,
            parent=self
        )

        self._notifications = NotificationsPanel(
            (SCREEN_WIDTH, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 8, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
            (SCREEN_WIDTH // 6 * 5, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 8, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
            resize_time=0.5,
            parent=self
        )

        y = 15
        w = h = SCREEN_HEIGHT - y * 2 - (SCREEN_HEIGHT - self._tiles_panel.get_rect().y)
        x = (SCREEN_WIDTH - w) // 2

        self._field = Field(x, y, w, h, parent=self)

        self._field.rows, self._field.cols = 20, 20
        self._field.grid = (255, 255, 255)

        # TODO: TODO: remove code below. Test of hero
        hero = Hero(self._field, (5, 5))
        self._field.add_cells(hero)
        hero.image = load_image(Images.HERO)

    def eventloop(self, *events):
        ...

    def draw(self):
        self.fill((54, 57, 62))
        self._field.draw()
        self._tiles_panel.draw()
        self._notifications.draw()
        self.blit(self._field)
        self.blit(self._tiles_panel)
        self.blit(self._notifications)
