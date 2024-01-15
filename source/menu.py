from account import AuthTabs
from constants import Media, SCREEN_WIDTH, SCREEN_HEIGHT
from editor import Editor
from levels import Levels
from templates import BaseWindow, Button
from utils import load_media


class Menu(BaseWindow):

    def __init__(self):
        super().__init__()
        w, h = SCREEN_WIDTH // 6, SCREEN_HEIGHT / 2.5
        AuthTabs(SCREEN_WIDTH // 2 - w // 2, SCREEN_HEIGHT // 2 - h // 2, w, h, parent=self)
        self._title_frames = load_media(Media.TITLE)
        self._label_levels_frames = load_media(Media.LABEL_LEVELS)
        self._label_editor_frames = load_media(Media.LABEL_EDITOR)

        self._button_levels = Button(470, 450, 300, 200, parent=self)
        self._button_levels.set_hovered_view(load_media(Media.LEVELS_PREVIEW), background_color=(69, 69, 69),
                                             border_radius=15, scale_x=1.03, scale_y=1.03)
        self._button_levels.set_not_hovered_view(load_media(Media.LEVELS_PREVIEW), background_color=(78, 78, 78),
                                                 border_radius=21)
        self._button_editor = Button(1150, 450, 300, 200, parent=self)
        self._button_editor.set_hovered_view(load_media(Media.WRENCH), background_color=(69, 69, 69),
                                             border_radius=15, scale_x=1.03, scale_y=1.03)
        self._button_editor.set_not_hovered_view(load_media(Media.WRENCH), background_color=(78, 78, 78),
                                                 border_radius=21)
        self._button_editor.bind_press(lambda: Editor())
        self._button_levels.bind_press(lambda: Levels())

    def draw(self):
        self.fill((54, 57, 62))

        self._button_levels.handle()
        self.blit(self._button_levels)
        self._button_editor.handle()
        self.blit(self._button_editor)

        frame = next(self._title_frames)
        self.blit(frame, rect=frame.get_rect(center=(self.get_rect().centerx, SCREEN_HEIGHT // 5)))
        frame_lvls = next(self._label_levels_frames)
        self.blit(frame_lvls, rect=(self._button_levels.get_rect().centerx - frame_lvls.get_width() // 2,
                                    self._button_levels.get_rect().bottom, *frame_lvls.get_size()))
        frame_ed = next(self._label_editor_frames)
        self.blit(frame_ed, rect=(self._button_editor.get_rect().centerx - frame_lvls.get_width() // 2,
                                  self._button_editor.get_rect().bottom, *frame_lvls.get_size()))
