import sys

import pygame

from constants import FPS, SCREEN_SIZE
from editor import Editor


class Main:

    def __init__(self):
        pygame.init()

        self._screen = pygame.display.set_mode(SCREEN_SIZE)
        self._clock = pygame.time.Clock()

        # self._current_working_window = Menu()
        self._current_working_window = Editor()

    @staticmethod
    def _eventloop(*events):
        if pygame.QUIT in map(lambda event: event.type, events):
            sys.exit()  # terminates executing if pygame.quit() in run() didn't do it
        # other events should be processed by current working window

    def _handle(self):
        events = pygame.event.get()  # pygame clears stack after pygame.event.get()

        self._eventloop(*events)
        self._screen.blit(self._current_working_window, self._current_working_window.get_rect())

        self._current_working_window.eventloop(*events)
        self._current_working_window.draw()

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
