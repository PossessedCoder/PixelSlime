from account import AuthTabs
from constants import Media, SCREEN_WIDTH, SCREEN_HEIGHT, UserEvents
from levels import Levels
from source.editor import Editor
from templates import BaseWindow, Button
from utils import load_media, post_event


class Menu(BaseWindow):

    def __init__(self):
        super().__init__()

        w, h = SCREEN_WIDTH // 6, SCREEN_HEIGHT / 2.5
        # AuthTabs(SCREEN_WIDTH // 2 - w // 2, SCREEN_HEIGHT // 2 - h // 2, w, h, parent=self)
        self._title_frames = load_media(Media.TITLE)
        self._label_levels_frames = load_media(Media.LABEL_LEVELS)
        self._label_editor_frames = load_media(Media.LABEL_EDITOR)

        self._button_levels = Button(470, 450, 250, 250, parent=self)
        self._button_levels.set_hovered_view(load_media(Media.LEVELS_PREVIEW), background_color=(69, 69, 69),
                                             border_radius=15, scale_x=1.03, scale_y=1.03)
        self._button_levels.set_not_hovered_view(load_media(Media.LEVELS_PREVIEW), background_color=(78, 78, 78),
                                                 border_radius=19)
        self._button_editor = Button(1190, 450, 250, 250, parent=self)
        self._button_editor.set_hovered_view(load_media(Media.WRENCH), background_color=(69, 69, 69),
                                             border_radius=15, scale_x=1.03, scale_y=1.03)
        self._button_editor.set_not_hovered_view(load_media(Media.WRENCH), background_color=(78, 78, 78),
                                                 border_radius=19)
        self._button_editor.bind_press(lambda: post_event(UserEvents.RUN_WITH_UID, runner=Editor))
        self._button_levels.bind_press(lambda: post_event(UserEvents.RUN_WITH_UID, runner=Levels))
        self.back_button = Button(self.get_rect().centerx - 27, self.get_rect().h - 70, 55, 55, parent=self)
        self.back_button.set_hovered_view(load_media(Media.CLOSE_WINDOW), background_color=(102, 121, 213),
                                          border_radius=8, scale_x=1.03, scale_y=1.03)
        self.back_button.set_not_hovered_view(load_media(Media.CLOSE_WINDOW), background_color=(85, 106, 208),
                                              border_radius=10)
        self.back_button.bind_press(lambda: post_event(UserEvents.CLOSE_CWW))

    def draw(self):
        self.fill((54, 57, 62))

        self._button_levels.handle()
        self.blit(self._button_levels)
        self._button_editor.handle()
        self.blit(self._button_editor)
        self.back_button.handle()
        self.blit(self.back_button)

        frame = next(self._title_frames)
        self.blit(frame, rect=frame.get_rect(center=(self.get_rect().centerx, SCREEN_HEIGHT // 5)))
        frame_lvls = next(self._label_levels_frames)
        self.blit(frame_lvls, rect=(self._button_levels.get_rect().centerx - frame_lvls.get_width() // 2,
                                    self._button_levels.get_rect().bottom, *frame_lvls.get_size()))
        frame_ed = next(self._label_editor_frames)
        self.blit(frame_ed, rect=(self._button_editor.get_rect().centerx - frame_lvls.get_width() // 2,
                                  self._button_editor.get_rect().bottom, *frame_lvls.get_size()))
