import pygame

from constants import Media
from templates import BaseWindow, Button
from utils import load_media, post_event
from constants import UserEvents


class Levels(BaseWindow):

    def __init__(self):
        super().__init__()
        self._but_w, self._but_h = 100, 100
        self._buttons = []
        self.font = pygame.font.SysFont('serif', 100)
        self.back_button = Button(0, 0, self._but_w, self._but_h)
        self.back_button.set_hovered_view(load_media(Media.BACK), background_color=(69, 69, 69),
                                          border_radius=15, scale_x=1.03, scale_y=1.03)
        self.back_button.set_not_hovered_view(load_media(Media.BACK), background_color=(78, 78, 78),
                                              border_radius=25)
        self.user_levels_list_button = Button(self.get_width() - self._but_w * 5, self.get_height() - self._but_h,
                                              self._but_w * 5, self._but_h)
        self.user_levels_list_button.set_hovered_view(self.font.render(f' Пользовательские уровни ', False, (255 // 2, 255 // 2, 255 // 2)), background_color=(69, 69, 69),
                                                      border_radius=15, scale_x=1.03, scale_y=1.03)
        self.user_levels_list_button.set_not_hovered_view(self.font.render(f' Пользовательские уровни ', False, (255, 255, 255)), background_color=(78, 78, 78),
                                                          border_radius=25)
        c = 1
        for y in range(self._but_h * 4, self.get_height() - self._but_h, self._but_h + self._but_h // 2):
            for x in range(self._but_w, self.get_width() - self._but_w,
                           self._but_w + self._but_w // 2):

                a = Button(x, y, self._but_w, self._but_h, parent=self)
                a.set_not_hovered_view(self.font.render(f' {c} ', False, (255, 255, 255)),
                                       background_color=(78, 78, 78),
                                       border_radius=25)
                a.set_hovered_view(self.font.render(f' {c} ', False, (255 // 2, 255 // 2, 255 // 2)), background_color=(78, 78, 78),
                                   border_radius=25)
                self._buttons.append(a)
                c += 1
                if c == 21:
                    break
            if c == 21:
                break

        self.back_button.bind_press(lambda: post_event(UserEvents.CLOSE_CWW))

    def eventloop(self):
        for button in self._buttons:
            button.eventloop()

    def draw(self):
        self.fill((54, 57, 62))
        for button in self._buttons:
            button.handle()
            self.blit(button)
        self.back_button.handle()
        self.blit(self.back_button)
        self.user_levels_list_button.handle()
        self.blit(self.user_levels_list_button)
