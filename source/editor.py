__all__ = (
    'Editor',
)

import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, UserEvents, Media
from game import Field
from level import Level
from templates import Button, BaseWindow, LowerPanel, StyledForm, Freezer, NotificationsPanel
from utils import load_media, post_event, catch_events, get_tiles, DataBase


class FormLevelInfo(StyledForm, Freezer):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)
        self.title = 'Сохранение уровня'

        self.freeze()

        self.add_field(placeholder='Название')

    def draw(self):
        super().draw()

    def validate(self):
        for fld in self.fields:
            fld.errors.clear()

        if not self.as_tuple()[0]:
            self.fields[0].errors.append('Не может быть пустым')

        self.parent.save_level(self.as_tuple()[0])
        return True

    def on_success(self):
        super().on_success()
        self.unfreeze()


class TilesPanel(LowerPanel):

    def __init__(self, uid, minimized_rect, maximized_rect, resize_time, parent=None):
        super().__init__(minimized_rect, maximized_rect, resize_time, parent=parent)
        self._uid = uid

        buttons_not_hovered_view = {'scale_x': 1, 'scale_y': 1, 'border_radius': 24}
        buttons_hovered_view = {'scale_x': 1.05, 'scale_y': 1.05, 'border_radius': 21}
        buttons_data = (
            (Media.RUN, (self.parent.run_level_from_data,)),
            (Media.CLEAR, (lambda: setattr(self.parent, '_buttoned_cells', list()),)),
            (Media.SAVE, (lambda: self.parent.request_level_info(),)),
            # actually bad practice to use setattr for parent's private attributes, but cannot use events everywhere,
            # because pygame has limitations on user events number: maximum 9 (with ids from 24 to 32)
            (Media.CLOSE_WINDOW, (lambda: post_event(UserEvents.CLOSE_CWW),))
        )

        for image_name, callbacks in buttons_data:
            btn = Button(-1, -1, 100, 100, parent=self)
            buttons_hovered_view['content'] = load_media(image_name)
            buttons_not_hovered_view['content'] = load_media(image_name)
            btn.set_hovered_view(**buttons_hovered_view, background_color=(102, 121, 213))
            btn.set_not_hovered_view(**buttons_not_hovered_view, background_color=(85, 106, 208))
            btn.bind_press(*callbacks)
            self.add_button(btn)

        self._captured_tile_index = None
        self._available_tiles = []

        self._buttons_change_pack = []
        x = self.get_rect().centerx - (len(self.parent.packs) // 2) * 35
        y = self.get_rect().h - 45
        for k, t in self.parent.packs.items():
            block = pygame.transform.scale(load_media(Media.BLOCK.format(t)), (35, 35))
            btn = Button(x, y, *block.get_size(), parent=self)
            btn.set_hovered_view(block, scale_x=1.1, scale_y=1.1)
            btn.set_not_hovered_view(block)
            btn.bind_press((lambda p, b: lambda: [b_.remove_hover() for b_ in self._buttons_change_pack if b_.hovered]
                            and b.emit_hover(True) or self.parent.set_pack(p))(k, btn))
            if t == self.parent.current_pack:
                btn.emit_hover(True)
            self._buttons_change_pack.append(btn)
            x += 35

    @property
    def captured_tile(self):
        if self._captured_tile_index is not None:
            return self._available_tiles[self._captured_tile_index].factory

    def _get_available_tiles(self):
        self._available_tiles.clear()
        tls = DataBase().get_unlocked_tiles(self._uid)

        x, y = 10 + SCREEN_WIDTH // 5, 35
        for tile in tls.values():
            img = pygame.transform.scale(load_media(tile.IMAGE_NAME.format(self.parent.current_pack)), (100, 100))
            btn = Button(x, y, 48, 48, parent=self)
            btn.set_not_hovered_view(img)
            btn.set_hovered_view(img, 1.09, 1.09)
            btn.bind_press(
                (lambda t: lambda: setattr(self, '_captured_tile_index',
                                           tuple(map(lambda k: k.factory, self._available_tiles)).index(t)))(tile)
            )
            btn.factory = tile
            self._available_tiles.append(btn)
            x += 65
            if x + btn.get_rect().w > self.get_rect().w:
                y += 65
                x = 10 + SCREEN_WIDTH // 5

    def draw(self):
        super().draw()

        if self.is_minimized():
            return

        self._get_available_tiles()
        for tile in self._available_tiles:
            tile.handle()
            self.blit(tile)
        if self._captured_tile_index is not None:
            pygame.draw.rect(self, (42, 199, 186), self._available_tiles[self._captured_tile_index].get_rect(), width=3)

        for btn in self._buttons_change_pack:
            btn.handle()
            self.blit(btn)


class Editor(BaseWindow):

    def __init__(self, uid):
        super().__init__()

        self.packs = {
            0: Media.LAVA_PACK,
            1: Media.ROCK_PACK,
            2: Media.SKY_PACK,
            3: Media.PURPLE_PACK
        }
        self.current_pack = self.packs[0]
        self._bg = ...

        self._tiles_panel = TilesPanel(
            uid,
            (0, SCREEN_HEIGHT // 18 * 17, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            (0, SCREEN_HEIGHT // 6 * 5, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            resize_time=0.3,
            parent=self
        )

        self._notifications_panel = NotificationsPanel(
            (SCREEN_WIDTH, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 8, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
            (SCREEN_WIDTH // 6 * 5, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 8, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
            resize_time=0.5,
            parent=self
        )

        self._field = Field(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 18 * 17, parent=self)

        self._field.rows, self._field.cols = 10, 20
        self._field.grid = (255, 255, 255)

        self._buttoned_cells = []
        self._field_updater = self._get_field_updater()

        self.set_pack(0)

    def _check_min_usages(self):
        tfd = tuple(t_[1] for t_ in self.to_field_data())

        for t in get_tiles().values():
            if t.MIN_USAGE > 0 and tfd.count(t) < t.MIN_USAGE:
                if self._notifications_panel.is_empty():
                    self._notifications_panel.add_notification('Недостаточное количество',
                                                               load_media(t.IMAGE_NAME.format(self.current_pack)),
                                                               text='Минимально: 1',
                                                               duration=3)
                return False

        return True

    def run_level_from_data(self):
        if self._check_min_usages():
            Level.from_data(self.to_field_data(), self.current_pack)

    def request_level_info(self):
        if self._check_min_usages():
            w, h = SCREEN_WIDTH // 6, SCREEN_HEIGHT / 2.5
            FormLevelInfo(SCREEN_WIDTH // 2 - w // 2, SCREEN_HEIGHT // 2 - h // 2, w, h, parent=self)

    def set_pack(self, idx):
        self.current_pack = self.packs[idx]
        self._bg = pygame.transform.scale(load_media(Media.BACKGROUND.format(self.current_pack), keep_alpha=False),
                                          self._field.get_rect().size)
        for cl in self._buttoned_cells:
            cl.instance.set_pack(self.current_pack)
            cl.set_hovered_view(cl.instance.image)
            cl.set_not_hovered_view(cl.instance.image)
            cl.draw()
            self._field.blit(cl)

    def save_level(self, name):
        data = tuple((f'{pos.row} {pos.col}', factory.__name__, angle) for pos, factory, angle in self.to_field_data())
        post_event(UserEvents.SAVE_LEVEL, name=name, fdata=data, pack=self.current_pack)
        self._notifications_panel.add_notification('Уровень сохранен', load_media(Media.SUCCESS),
                                                   text=f'Название: {name}', duration=3)

    def to_field_data(self):
        data = []

        for bc in self._buttoned_cells:
            data.append(
                (self._field.get_position_by_mouse_pos(bc.get_absolute_rect().center),
                 bc.factory,
                 bc.angle)
            )

        return data

    def eventloop(self):
        for event in catch_events(False):
            # LMB pressed and colliding field and not colliding tiles panel and any tile captured
            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                continue
            if not self._field.is_colliding_field(pygame.mouse.get_pos(), border=False):
                continue
            if self._tiles_panel.get_rect().collidepoint(*pygame.mouse.get_pos()):
                continue
            for r in self._buttoned_cells:
                # if there is any tile on position of the new tile, old one will be removed
                if r.get_rect().collidepoint(pygame.mouse.get_pos()):
                    self._buttoned_cells.remove(r)
                    return
            if not self._tiles_panel.captured_tile:
                continue
            if self._tiles_panel.captured_tile.USAGE_LIMIT is not None:
                # times tile has been used on the field + 1 (current tile, if it will pass checks)
                n = len(tuple(t.factory for t in self._buttoned_cells
                              if t.factory == self._tiles_panel.captured_tile)) + 1
                if n > self._tiles_panel.captured_tile.USAGE_LIMIT:
                    continue

            # init real cell
            cell = self._tiles_panel.captured_tile(
                self._field, self._field.get_position_by_mouse_pos(pygame.mouse.get_pos())
            )
            cell.set_pack(self.current_pack)
            # make a copy of a real tile converting it into a button, so we can easily detect RMB press
            fake_tile = Button(*cell.get_rect(), parent=cell.parent)
            # setting view of a button (same in both hovered and not hovered)
            fake_tile.set_hovered_view(cell.image)
            fake_tile.set_not_hovered_view(cell.image)
            # save the factory in the .tile attribute to access it on field save
            fake_tile.factory = self._tiles_panel.captured_tile
            fake_tile.instance = cell
            fake_tile.angle = 0
            fake_tile.bind_press(lambda: setattr(fake_tile, 'angle', (fake_tile.angle - 90) % 360), button='R')
            self._buttoned_cells.append(fake_tile)

    def _get_field_updater(self):
        # Since no actions happen on the field in the editor mode, there is no need to draw it every frame,
        # and we can only update it on addition/deletion of a new fake tile

        self._field.handle()  # draw grid
        previous_buttoned_cells = self._buttoned_cells.copy()

        def _compare():
            if len(previous_buttoned_cells) != len(self._buttoned_cells):
                return False
            for prev, cur in zip(previous_buttoned_cells, self._buttoned_cells):
                if prev != cur or prev.angle != cur.angle:
                    return False
            return True

        def _updater():
            nonlocal previous_buttoned_cells

            if _compare():  # skip drawing if there is no changes
                self._field.handle()
                for ft in self._buttoned_cells:
                    ft.draw()
                    rotated = pygame.transform.rotate(ft, ft.angle)
                    self._field.blit(rotated, ft.get_rect())

            previous_buttoned_cells = self._buttoned_cells.copy()

            for ft in self._buttoned_cells:  # force events handling even if field is not updated
                ft.eventloop()

            self.blit(self._field)

        return _updater

    def draw(self):
        self.blit(self._bg)

        self._field_updater()

        self._tiles_panel.handle()
        self.blit(self._tiles_panel)
        self._notifications_panel.handle()
        if not self._notifications_panel.is_minimized():
            self.blit(self._notifications_panel)
