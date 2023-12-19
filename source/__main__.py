import sys

import pygame

from abstractions import SupportsDraw, SupportsEventLoop
from constants import FPS, SCREEN_SIZE
from editor import Editor


class Main:

    def __init__(self):
        pygame.init()

        self._screen = pygame.display.set_mode(SCREEN_SIZE)
        self._clock = pygame.time.Clock()

        # self._current_working_window = ...

        self._current_working_window = Editor(self._screen)
        self._current_working_window.rows, self._current_working_window.cols = 25, 25
        self._current_working_window.grid_enabled = True
        self._current_working_window.add_cells(*((i, k) for i in range(11, 16) for k in range(11, 16)))

    def _eventloop(self, *events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def _handle(self):
        self._screen.fill(pygame.Color(70, 71, 71))
        events = pygame.event.get()

        self._eventloop(*events)
        if isinstance(self._current_working_window, SupportsEventLoop):
            self._current_working_window.eventloop(*events)
        if isinstance(self._current_working_window, SupportsDraw):
            self._current_working_window.draw()

    def run(self):
        while True:
            self._handle()

            pygame.display.flip()
            self._clock.tick(FPS)


if __name__ == '__main__':
    runner = Main()
    runner.run()
