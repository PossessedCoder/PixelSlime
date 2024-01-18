from datetime import datetime

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, Media, UserEvents
from game import Field, Coordinates
from templates import NotificationsPanel, BaseWindow, LowerPanel, Button
from tiles import Hero
from utils import load_media, post_event, DataBase, get_tiles, catch_events


class StartPanel(LowerPanel):

    def __init__(self, is_author, minimized_rect, maximized_rect, resize_time=0.0, parent=None):
        super().__init__(minimized_rect, maximized_rect, resize_time, parent=parent)
        if self._maximized_rect.collidepoint(pygame.mouse.get_pos()):
            self.move(*self._maximized_rect.topleft)

        buttons_not_hovered_view = {'scale_x': 1, 'scale_y': 1, 'border_radius': 24}
        buttons_hovered_view = {'scale_x': 1.05, 'scale_y': 1.05, 'border_radius': 21}
        buttons_data = [
            (Media.CLEAR, (self.parent.field_to_initial, self.parent.restart)),
            (Media.CLOSE_WINDOW, (lambda: post_event(UserEvents.CLOSE_CWW),))
        ]
        if is_author:
            buttons_data.append((Media.TRASH_BIN, (self.parent.remove,)))

        for image_name, callbacks in buttons_data:
            btn = Button(-1, -1, 100, 100, parent=self)
            buttons_hovered_view['content'] = load_media(image_name)
            buttons_not_hovered_view['content'] = load_media(image_name)
            btn.set_hovered_view(**buttons_hovered_view, background_color=(102, 121, 213))
            btn.set_not_hovered_view(**buttons_not_hovered_view, background_color=(85, 106, 208))
            btn.bind_press(*callbacks)
            self.add_button(btn)


class Level(BaseWindow):

    def __init__(self, level_id, uid, *, _d=None):
        super().__init__()

        self._level_id = level_id
        self._uid = uid

        self._start_panel = StartPanel(
            DataBase().get_level_by_id(level_id)[2] == uid,
            (0, SCREEN_HEIGHT // 18 * 17, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            (0, SCREEN_HEIGHT // 6 * 5, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            resize_time=0.3,
            parent=self
        )

        self._notifications_panel = NotificationsPanel(
            (SCREEN_WIDTH, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 4, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
            (SCREEN_WIDTH // 6 * 5, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 4, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
            resize_time=0.5,
            parent=self
        )

        self._notifications_panel2 = NotificationsPanel(
            (SCREEN_WIDTH, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 10, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
            (SCREEN_WIDTH // 6 * 5, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 10, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
            resize_time=0.5,
            parent=self
        )

        y = 15
        w = h = SCREEN_HEIGHT - y * 2 - (SCREEN_HEIGHT - SCREEN_HEIGHT // 18 * 17)
        x = (SCREEN_WIDTH - w) // 2

        self._field = Field(x, y, w, h, parent=self)

        self._field.rows, self._field.cols = 15, 15
        self._field.grid = (255, 255, 255)

        self._setup_field(DataBase().get_level_field_data(level_id) if _d is None else _d)

        self._best_time = None
        self._start_time = None

        self._wait_until_invoked = False

        self.restart()

    def remove(self):
        DataBase().delete_level(self._level_id)
        post_event(UserEvents.CLOSE_CWW)

    def field_to_initial(self):
        for cl in self._field.get_cells():
            cl.to_initial()

    def restart(self):
        self._notifications_panel.add_notification('Нажмите любую кнопку', image=load_media(Media.CLOCK))
        self._start_time = None
        self._field.handle()
        self._wait_until_invoked = True

    @classmethod
    def from_data(cls, data):
        return cls(-1, -1, _d=data)

    def _setup_field(self, data):
        cells = []

        for coordinates, factory in data:
            coordinates = Coordinates(*map(int, coordinates.split())) if isinstance(coordinates, str) else coordinates
            factory = get_tiles()[factory] if isinstance(factory, str) else factory
            cells.append(factory(self._field, coordinates))

        self._field.add_cells(*cells)

    def eventloop(self):
        if not self._wait_until_invoked:
            self._field.handle()
            if self._notifications_panel.is_maximized():
                self._notifications_panel.minimize()
        for event in catch_events(False):
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self._wait_until_invoked = False
                # clearing queue of notifications panel since multiple waiter notifications might be added
                while True:
                    try:
                        next(self._notifications_panel)
                    except StopIteration:
                        return

    def draw(self):
        self.fill((54, 57, 62))

        self.blit(self._field)
        self._start_panel.handle()
        self.blit(self._start_panel)
        self._notifications_panel.handle()
        if not self._notifications_panel.is_minimized():
            self.blit(self._notifications_panel)
        self._notifications_panel2.handle()
        if not self._notifications_panel2.is_minimized():
            self.blit(self._notifications_panel2)

    def handle(self):
        self.eventloop()
        self.draw()

        if self._start_time is None:
            self._start_time = datetime.now()

        if (hero := next(filter(lambda x: isinstance(x, Hero), self._field.get_cells()), None)) is None:
            return

        if hero.finished:
            for tl in DataBase().get_new_tiles(self._uid, self._level_id).values():
                self._notifications_panel2.add_notification('Открыт новый блок',
                                                            'Доступен в редакторе', load_media(tl.IMAGE_NAME),
                                                            duration=3)
            completed_in = (datetime.now() - self._start_time).total_seconds()
            if not self._best_time or completed_in < self._best_time:
                self._best_time = completed_in
            if self._uid != -1:
                DataBase().save_completion(self._level_id, self._uid, completed_in)
                post_event(UserEvents.LEVEL_COMPLETED, level_id=self._level_id, time=completed_in)

        if hero.dead or hero.finished:
            self.field_to_initial()
            self.restart()
