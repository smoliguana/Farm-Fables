import pygame, sys
from settings import *
from level import Level
from support import *

#NOTE TO SELF W TO CHANGE SEED, Q CHANGE TOOL, SPACE USE TOOL, SHIFT TO USE SEED
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width,screen_height))
        pygame.display.set_caption('Farm-Fables')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick() / 1000.0
            self.level.run(dt)
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()