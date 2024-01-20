import pygame

from constants import Media, SCREEN_HEIGHT, SCREEN_WIDTH, UserEvents
from level import Level
from templates import BaseWindow, Button, Freezer, BaseSurface
from utils import load_media, post_event, DataBase, catch_events


class UserLevelsSurface(BaseSurface, Freezer):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)
        self.freeze()

        self._total_pages = DataBase().get_pages_num(items_on_page=15)
        self._current_page = 1

        self._buttons = []

        self._button_next_page = Button(self.get_rect().w // 2 + 10, self.get_rect().h - 60, 48, 48, parent=self)
        self._button_next_page.set_hovered_view(load_media(Media.FORWARD), background_color=(102, 121, 213),
                                                border_radius=4, scale_x=1.03, scale_y=1.03)
        self._button_next_page.set_not_hovered_view(load_media(Media.FORWARD),
                                                    background_color=(85, 106, 208),
                                                    border_radius=6)
        self._button_next_page.bind_press(
            lambda: self.load_page(self._current_page + 1) if self._current_page != self._total_pages else None
        )

        self._button_previous_page = Button(self.get_rect().w // 2 - 58, self.get_rect().h - 60, 48, 48, parent=self)
        self._button_previous_page.set_hovered_view(load_media(Media.BACK), background_color=(102, 121, 213),
                                                    border_radius=4, scale_x=1.03, scale_y=1.03)
        self._button_previous_page.set_not_hovered_view(load_media(Media.BACK),
                                                        background_color=(85, 106, 208),
                                                        border_radius=6)
        self._button_previous_page.bind_press(
            lambda: self.load_page(self._current_page - 1) if self._current_page != 1 else None
        )

        self.load_page(self._current_page)

    def load_page(self, page):
        self._buttons.clear()

        self._current_page = page
        btn_height = (self.get_rect().h - 110) / 15
        e = enumerate(DataBase().load_page(self._current_page, items_on_page=15))
        for idx, (level_id, level_name, author_id, author_name) in e:
            surf = BaseSurface(10, 40 + idx * btn_height, self.get_rect().w - 20, btn_height, parent=self)
            font = pygame.font.SysFont('arial', 15)
            n = font.render(level_name, True, (169, 169, 169))
            surf.blit(n, rect=(2, (surf.get_rect().h - n.get_height()) // 2, *n.get_size()))
            c = font.render(f'от {author_name}', True, (169, 169, 169))
            surf.blit(c, rect=(self.get_rect().w - 22 - c.get_width(),
                               (surf.get_rect().h - n.get_height()) // 2, *c.get_size()))
            btn = Button(*surf.get_rect(), parent=self)
            btn.set_hovered_view(surf, background_color=(73, 74, 73))
            btn.set_not_hovered_view(surf)
            btn.bind_press(self.unfreeze, (lambda lid, aid: lambda: Level(lid, aid))(level_id, author_id))
            self._buttons.append(btn)

    def draw(self):
        self.fill((54, 53, 53))

        pygame.draw.rect(self, (202, 202, 202), (5, 5, self.get_rect().width - 10, 30))
        pygame.draw.rect(self, (105, 105, 105), (5, 5, self.get_rect().width - 10, self.get_rect().height - 10),
                         width=1)
        font = pygame.font.SysFont('arial', 16)
        ttl = font.render('Пользовательские уровни', True, (109, 109, 109))
        self.blit(ttl, rect=(10, 10, *ttl.get_size()))

        surf = BaseSurface(self.get_rect().w - 30, 10, 20, 20)
        pygame.draw.line(surf, (117, 119, 119), (1, 1), surf.get_size())
        pygame.draw.line(surf, (117, 119, 119), (0, surf.get_height()), (surf.get_width(), 0))

        btn = Button(*surf.get_rect(), parent=self)
        btn.bind_press(lambda: post_event(UserEvents.UNFREEZE_CWW, freezer=self))
        btn.set_hovered_view(surf)
        btn.set_not_hovered_view(surf)
        btn.handle()
        self.blit(btn)

        self._button_next_page.handle()
        self.blit(self._button_next_page)
        self._button_previous_page.handle()
        self.blit(self._button_previous_page)

        for b in self._buttons:
            b.handle()
            self.blit(b)


class Levels(BaseWindow):

    def __init__(self, uid):
        super().__init__()
        self._uid = uid

        self._but_w, self._but_h = 100, 100
        self._buttons = []
        self.font = pygame.font.SysFont('serif', 100)
        self.back_button = Button(self.get_rect().centerx + 15, self.get_rect().h - self._but_w * 0.55 - 15,
                                  self._but_w * 0.55, self._but_h * 0.55, parent=self)
        self.back_button.set_hovered_view(load_media(Media.CLOSE_WINDOW), background_color=(102, 121, 213),
                                          border_radius=8, scale_x=1.03, scale_y=1.03)
        self.back_button.set_not_hovered_view(load_media(Media.CLOSE_WINDOW), background_color=(85, 106, 208),
                                              border_radius=10)
        self.user_levels_list_button = Button(self.get_rect().centerx - self._but_w * 0.55 - 15,
                                              self.get_rect().h - self._but_w * 0.55 - 15,
                                              self._but_w * 0.55, self._but_h * 0.55, parent=self)
        self.user_levels_list_button.set_hovered_view(load_media(Media.DOCUMENT), background_color=(102, 121, 213),
                                                      border_radius=8, scale_x=1.03, scale_y=1.03)
        self.user_levels_list_button.set_not_hovered_view(load_media(Media.DOCUMENT),
                                                          background_color=(85, 106, 208),
                                                          border_radius=10)

        self._buttons_per_row = 10
        self._icon_completed, self._icon_unlocked, self._icon_locked = (
            pygame.transform.scale(load_media(i), (self._but_w // 4, self._but_h // 4))
            for i in (Media.SUCCESS, Media.UNLOCKED, Media.LOCKED)
        )
        self._setup_levels_buttons()

        self.back_button.bind_press(lambda: post_event(UserEvents.CLOSE_CWW))
        w, h = SCREEN_WIDTH // 6, SCREEN_HEIGHT / 2
        self.user_levels_list_button.bind_press(
            lambda: UserLevelsSurface(SCREEN_WIDTH // 2 - w // 2, SCREEN_HEIGHT // 2 - h // 2, w, h, parent=self)
        )

    def _setup_levels_buttons(self):
        system_levels = DataBase().get_system_levels()
        unlocked_num = DataBase().get_unlocked_levels_num(self._uid)

        x, y = 0, self.get_rect().centery - self._but_w * 3
        for idx, (level_id, _) in enumerate(system_levels):
            if idx % self._buttons_per_row == 0:
                y += self._but_h * 1.5
                x = self.get_rect().centerx - self._but_w\
                    * (self._buttons_per_row / 2 + 0.5 * (self._buttons_per_row / 2 - 1))
            else:
                x += self._but_w * 1.5

            if idx < unlocked_num - 1:
                icon = self._icon_completed
            elif idx == unlocked_num - 1:
                icon = self._icon_unlocked
            else:
                icon = self._icon_locked

            surf = BaseSurface(x, y, self._but_w, self._but_h)
            surf.blit(icon,
                      rect=(self._but_w - icon.get_width() - 8, self._but_h - icon.get_height() - 8, *icon.get_size()))

            btn = Button(*surf.get_rect(), parent=self)
            btn.bind_press((lambda lid: lambda: Level(lid, self._uid))(level_id))

            surf.blit(self.font.render(f' {idx + 1} ', False, (220, 220, 220)),
                      rect=(5, 5, surf.get_width() - icon.get_width(), surf.get_height() - icon.get_height()))
            btn.set_not_hovered_view(surf,
                                     background_color=(78, 78, 78),
                                     border_radius=25)
            surf.blit(self.font.render(f' {idx + 1} ', False, (250, 250, 250)),
                      rect=(5, 5, surf.get_width() - icon.get_width(), surf.get_height() - icon.get_height()))
            if idx < unlocked_num:
                btn.set_hovered_view(surf,
                                     background_color=(78, 78, 78),
                                     border_radius=22,
                                     scale_x=1.03,
                                     scale_y=1.03)
            else:
                btn.set_hovered_view(**btn.get_params(hover=False))
                btn.bind_press()
            self._buttons.append(btn)

    def eventloop(self):
        # update info about system levels on any Level close,
        # will be also called on self close, but window will be instantly shut down after that
        if UserEvents.CLOSE_CWW in map(lambda event: event.type, catch_events(False)):
            self._buttons.clear()
            self._setup_levels_buttons()

    def draw(self):
        self.fill((54, 57, 62))

        for button in self._buttons:
            button.handle()
            self.blit(button)

        self.back_button.handle()
        self.blit(self.back_button)
        self.user_levels_list_button.handle()
        self.blit(self.user_levels_list_button)
