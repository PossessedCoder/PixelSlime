import sys

import pygame

from constants import FPS, SCREEN_SIZE, UserEvents
from editor import Editor
from utils import catch_events


class Main:

    def __init__(self):
        self._screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        # self._windows_stack = [Menu()]
        self._windows_stack = [Editor()]

    def _eventloop(self):
        for event in catch_events():  # gets a new queue of events
            if event.type == UserEvents.SET_CWW and self._windows_stack[-1] != event.window:
                self._windows_stack.append(event.window)
            if event.type == UserEvents.CLOSE_CWW:
                self._windows_stack.pop()
            if event.type == pygame.QUIT or not self._windows_stack:
                sys.exit()  # terminates executing if pygame.quit() in run() didn't do it

    def _handle(self):
        self._eventloop()

        current_working_window = self._windows_stack[-1]
        self._screen.blit(current_working_window, current_working_window.get_rect())
        current_working_window.handle()

    def run(self):
        try:
            while True:
                self._handle()

                pygame.display.flip()
                self._clock.tick(FPS)
        finally:
            pygame.quit()  # clear pygame stuff; make sure every running file will be closed correctly


if __name__ == '__main__':
    runner = Main()
    runner.run()
