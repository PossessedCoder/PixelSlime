import sys

import pygame

from constants import FPS, SCREEN_SIZE, UserEvents
from menu import Menu
from utils import catch_events


class Main:

    def __init__(self):
        self._screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        self._windows_stack = [Menu()]
        self._freezers = []

    def _eventloop(self):
        for event in catch_events():  # gets a new queue of events
            if event.type == pygame.QUIT or not self._windows_stack:
                sys.exit()  # terminates executing if pygame.quit() in run() didn't do it
            if event.type == UserEvents.SET_CWW and self._windows_stack[-1] != event.window:
                self._windows_stack.append(event.window)
            if event.type == UserEvents.CLOSE_CWW:
                self._windows_stack.pop()
            if event.type == UserEvents.FREEZE_CWW:
                self._freezers.append(event.freezer)
            if event.type == UserEvents.UNFREEZE_CWW:
                self._freezers.remove(event.freezer)

    def _mainloop(self):
        while True:
            current_working_window = self._windows_stack[-1]

            # if at least one freezer is active, cww is not handled
            if not self._freezers:
                current_working_window.handle()
            self._screen.blit(current_working_window, current_working_window.get_rect())

            for freezer in self._freezers:
                freezer.handle()
                self._screen.blit(freezer, freezer.get_rect())

            # eventloop should be called exactly after drawing cww, because freezer might be called immediately,
            # and we need to handle cww at least once before catching UserEvents.FREEZE_CWW event
            self._eventloop()

            pygame.display.flip()
            self._clock.tick(FPS)

    def run(self):
        try:
            self._mainloop()
        finally:
            pygame.quit()  # clear pygame stuff; make sure every running file will be closed correctly


if __name__ == '__main__':
    pygame.init()

    runner = Main()
    runner.run()
