import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_SIZE, UserEvents, Images
from game import Field
from templates import Button, BaseWindow, LowerPanel
from utils import load_image, get_tiles, post_event, catch_events


class TilesPanel(LowerPanel):

    def __init__(self, minimized_rect, maximized_rect, resize_time, parent=None):
        super().__init__(minimized_rect, maximized_rect, resize_time, parent=parent)

        buttons_data = (
            (Images.CLOSE_WINDOW, (lambda: post_event(UserEvents.CLOSE_CWW),)),
        )

        for image_name, callbacks in buttons_data:
            self.add_button(self.build_default_button(load_image(image_name), *callbacks))

        self._available_tiles = []
        self._get_available_tiles()

    # CHECKME: conceptual method, should be changed when db API will be ready
    def _get_available_tiles(self):
        tls = get_tiles()

        x, y = 10 + SCREEN_WIDTH // 5, 35
        for tile in tls.values():
            img = pygame.transform.scale(load_image(tile.IMAGE_NAME), (45, 45))
            btn = Button(x, y, *img.get_rect().size, parent=self)
            btn.set_not_hovered_view(img)
            btn.set_hovered_view(img, 1.05, 1.05)
            btn.bind_press(
                (lambda b, t: lambda: post_event(UserEvents.TILE_CAPTURED, tile=t) or setattr(b, 'captured', True) or
                    [delattr(b_, 'captured') for b_ in self._available_tiles if hasattr(b_, 'captured') and b_ != b])
                (btn, tile)
            )
            self._available_tiles.append(btn)
            x += 65
            if x + btn.get_rect().w > self.get_rect().w:
                y += 65
                x = 10 + SCREEN_WIDTH // 5

    def handle(self):
        super().handle()

        if self.is_minimized():
            return

        for tile in self._available_tiles:
            tile.handle()
            self.blit(tile)
            if hasattr(tile, 'captured'):
                pygame.draw.rect(self, (42, 199, 186), tile.get_rect(), width=3)


class Editor(BaseWindow):

    def __init__(self):
        super().__init__(0, 0, *SCREEN_SIZE)

        self._tiles_panel = TilesPanel(
            (0, SCREEN_HEIGHT // 18 * 17, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            (0, SCREEN_HEIGHT // 6 * 5, SCREEN_WIDTH, SCREEN_HEIGHT // 6),
            resize_time=0.3,
            parent=self
        )

        # self._notifications = NotificationsPanel(
        #     (SCREEN_WIDTH, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 8, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
        #     (SCREEN_WIDTH // 6 * 5, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 8, SCREEN_WIDTH // 6, SCREEN_HEIGHT // 8),
        #     resize_time=0.5,
        #     parent=self
        # )

        y = 15
        w = h = SCREEN_HEIGHT - y * 2 - (SCREEN_HEIGHT - self._tiles_panel.get_rect().y)
        x = (SCREEN_WIDTH - w) // 2

        self._field = Field(x, y, w, h, parent=self)

        self._field.rows, self._field.cols = 15, 15
        self._field.grid = (255, 255, 255)

        self._captured_tile = None
        self._buttoned_cells = []
        self._field_updater = self._get_field_updater()

    def _eventloop(self):
        for event in catch_events(False):
            if event.type == UserEvents.TILE_CAPTURED:
                self._captured_tile = event.tile

            # LMB pressed and colliding field and not colliding tiles panel and any tile captured
            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                continue
            if not self._field.is_colliding_field(pygame.mouse.get_pos(), border=False):
                continue
            if self._tiles_panel.get_rect().collidepoint(*pygame.mouse.get_pos()):
                continue
            if not self._captured_tile:
                continue

            # initialize real tile
            cell = self._captured_tile(self._field, self._field.get_position_by_mouse_pos(pygame.mouse.get_pos()))
            # make a copy of a real tile converting it into a button, so we can easily detect RMB press
            fake_tile = Button(*cell.get_rect(), parent=cell.parent)
            fake_tile.bind_press(lambda: self._buttoned_cells.remove(fake_tile), button='R')
            # setting view of a button (same in both hovered and not hovered)
            fake_tile.set_hovered_view(cell.image)
            fake_tile.set_not_hovered_view(cell.image)
            # save the factory in the .tile attribute to access it on field save
            fake_tile.tile = self._captured_tile
            for r in self._buttoned_cells:
                # if there is any tile on position of the new tile, old one will be removed
                if fake_tile.get_rect().colliderect(r.get_rect()):
                    self._buttoned_cells.remove(r)
                    break
            self._buttoned_cells.append(fake_tile)

    def _get_field_updater(self):
        # Since no actions happen on the field in the editor mode, there is no need to draw it every frame,
        # and we can only update it on addition/deletion of a new fake tile

        self._field.handle()  # draw grid
        previous_buttoned_cells = self._buttoned_cells.copy()

        def _updater():
            nonlocal previous_buttoned_cells

            if self._buttoned_cells != previous_buttoned_cells:  # skip drawing if there is no changes
                self._field.handle()
                for ft in self._buttoned_cells:
                    ft.handle()
                    self._field.blit(ft)

            previous_buttoned_cells = self._buttoned_cells.copy()

            for ft in self._buttoned_cells:  # force events handling
                ft.handle(partial=True)

            self.blit(self._field)

        return _updater

    def handle(self):
        self.fill((54, 57, 62))

        self._field_updater()

        # if there are FPS issues, optimize the code below with lazy callees only on update (change of the rect)
        self._tiles_panel.handle()
        self.blit(self._tiles_panel)

        self._eventloop()
