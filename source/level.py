import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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
            (Media.CLEAR, (self.parent.restart,)),
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

    def __init__(self, level_id, uid, *, _d=None, _p=None):
        super().__init__()

        self._level_id = level_id
        self._uid = uid
        self._level_info = DataBase().get_level_by_id(level_id)
        self._user_info = DataBase().get_user(uid)
        if self._level_info:
            self._author_info = DataBase().get_user(self._level_info[2])
        else:
            self._author_info = None

        self._start_panel = StartPanel(
            self._level_info[2] == uid if self._level_info else False,
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

        self._pack = ...

        self._field = Field(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 18 * 17, parent=self)
        self._field.rows, self._field.cols = 10, 20
        self._setup_field(DataBase().get_level_field_data(level_id) if _d is None else _d,
                          self._level_info[3] if _p is None else _p)

        self._best_time = DataBase().get_best_time(level_id, uid)
        self._start_time = None

        self._bg = pygame.transform.scale(
            load_media(Media.BACKGROUND.format(self._level_info[3] if _p is None else _p)), self._field.get_rect().size
        )

        self._wait_until_invoked = False
        self.restart()

    @property
    def best_time(self):
        return self._best_time

    @property
    def current_time(self):
        if self._start_time:
            return round((datetime.now() - self._start_time).total_seconds(), 2)

    def remove(self):
        post_event(UserEvents.DELETE_LEVEL, level_id=self._level_id)
        post_event(UserEvents.CLOSE_CWW)

    def _field_to_initial(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            for cl in self._field.get_cells():
                executor.submit(cl.to_initial)

    def restart(self):
        self._notifications_panel.add_notification('Нажмите любую кнопку', load_media(Media.CLOCK))
        self._start_time = None
        self._field_to_initial()
        self._field.handle()
        self._wait_until_invoked = True

    @classmethod
    def from_data(cls, data, pack):
        return cls(-1, -1, _d=data, _p=pack)

    def _setup_field(self, data, pack):
        tls = get_tiles()

        for coordinates, factory, angle in data:
            if isinstance(coordinates, str):
                # finds groups of digits (at least one digit in group) and throws them into Coordinates instance
                coordinates = Coordinates(
                    *map(lambda match: int(match.group(0)), re.finditer(re.compile(r'\d+'), coordinates))
                )
            if isinstance(factory, str):
                factory = tls[factory]
            cell = factory(self._field, coordinates)
            cell.set_pack(pack)
            if isinstance(cell, Hero):
                cw, ch = self._field.calc_cell_size()

                s = cell.get_rect().copy()
                o = s.copy()
                if angle == 180:
                    o.top -= ch
                    cell.top_collide(s, o)
                elif angle == 90:
                    o.right += cw
                    cell.right_collide(s, o)
                elif angle == 0:
                    o.bottom += ch
                    cell.bottom_collide(s, o)
                elif angle == 270:
                    o.left -= cw
                    cell.left_collide(s, o)
            else:
                cell.rotate(angle)
            self._field.add_cells(cell)

        self._pack = pack

    def eventloop(self):
        for event in catch_events(False):
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if self._wait_until_invoked:
                    self._start_time = datetime.now()
                self._wait_until_invoked = False
                # clearing queue of notifications panel since multiple waiter notifications might be added
                self._notifications_panel.clear()

    def draw(self):
        self.blit(self._bg)

        self.blit(self._field)
        self._start_panel.handle()
        if not self._start_panel.is_minimized():
            font = pygame.font.SysFont('arial', 16, bold=True)

            texts = [f'Ваше лучшее время: {self.best_time if self.best_time else "-"}']
            if self._level_info:
                texts.insert(0, f'Название уровня: {self._level_info[1]}')
            if self._uid > 0:
                texts.insert(0, f'Создатель уровня: {self._author_info[1]}')
            if self.current_time:
                ct = str(self.current_time)
                if len(ct.split('.')[-1]) == 1:
                    ct += '0'
                texts.append(f'Ваше текущее время: {ct}')

            y = 25
            for t in texts:
                t1, t2 = t.split(': ')
                rendered1 = font.render(t1 + ': ', True, (143, 143, 143))
                rendered2 = font.render(t2, True, (194, 194, 194))
                text_surface = pygame.Surface((rendered1.get_width() + rendered2.get_width(), font.get_height()),
                                              pygame.SRCALPHA)
                text_surface.blit(rendered1, (0, 0))
                text_surface.blit(rendered2, (rendered1.get_width(), 0))
                self._start_panel.blit(text_surface, (self._start_panel.get_rect().w - text_surface.get_width() - 15,
                                                      y, *text_surface.get_size()))
                y += text_surface.get_height() + 5
        self.blit(self._start_panel)
        self._notifications_panel.handle()
        if not self._notifications_panel.is_minimized():
            self.blit(self._notifications_panel)
        self._notifications_panel2.handle()
        if not self._notifications_panel2.is_minimized():
            self.blit(self._notifications_panel2)

    def handle(self):
        if not self._wait_until_invoked:
            self._field.handle()
            if self._notifications_panel.is_maximized():
                self._notifications_panel.minimize()

        if (hero := next(filter(lambda x: isinstance(x, Hero), self._field.get_cells()), None)) is None:
            return

        if hero.finished:
            if not self._best_time or self.current_time < self._best_time:
                self._best_time = self.current_time
                if self._uid != -1:
                    DataBase().save_completion(self._level_id, self._uid, self.current_time)
                    post_event(UserEvents.LEVEL_COMPLETED, level_id=self._level_id, time=self.current_time)
            if self._author_info and self._author_info[0] == 0:
                for tl in DataBase().get_new_tiles(self._uid, self._level_id).values():
                    pk = (load_media(tl.IMAGE_NAME.format(pack)) for pack in (Media.LAVA_PACK, Media.ROCK_PACK,
                                                                              Media.SKY_PACK, Media.ROCK_PACK))
                    self._notifications_panel2.add_notification('Открыт новый блок',
                                                                *pk,
                                                                text='Доступен в редакторе',
                                                                duration=3)

        if hero.dead or hero.finished:
            self.restart()

        self.eventloop()
        self.draw()
