import pygame
from game import Block


class Editor:

    def __init__(self):
        self.RES = self.W, self.H = 800, 800
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.cell_size = 50
        self.screen = pygame.display.set_mode(self.RES)

    def event_catch(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)

    def draw(self):
        self.screen.fill(0)
        for y in range(0, self.W, self.cell_size):
            for x in range(0, self.H, self.cell_size):
                pygame.draw.line(self.screen, (255, 255, 255), (x, y), (x, self.H), 1)
            pygame.draw.line(self.screen, (255, 255, 255), (0, y), (self.W, y), 1)
        pygame.display.flip()

    def run(self):
        while True:
            self.event_catch()
            self.draw()
            self.clock.tick(self.FPS)


if __name__ == '__main__':
    app = Editor()
    app.run()
