import sys

import pygame

from constants import FPS, SCREEN_SIZE


class Main:

    def __init__(self):
        pygame.init()

        self._screen = pygame.display.set_mode(SCREEN_SIZE)
        self._clock = pygame.time.Clock()

        # self._current_working_window = ...  # Redefine on every window switch
        #                                     # (e.g. menu -> editor, editor -> menu etc.) for convenient render
        #                                     # in self.run method.
        #                                     # Abstract class having method "render" should be implemented

    def _eventloop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def run(self):
        while True:
            self._eventloop()

            pygame.display.flip()
            self._clock.tick(FPS)


if __name__ == '__main__':
    runner = Main()
    runner.run()
