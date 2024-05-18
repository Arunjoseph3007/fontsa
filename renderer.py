import pygame
from fparser import FontParser


class Renderer:
    screen: pygame.Surface
    width: int = 1000
    height: int = 650
    title: str = "Fontsa"
    running: bool
    parser: FontParser
    index: int = 0

    def __init__(self, parser: FontParser) -> None:
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.running = True
        self.parser = parser

    def mainloop(self) -> None:
        while self.running:
            self.update()
            self.draw()
            self.handleEvents()
            pygame.display.update()

    def update(self) -> None:
        pass

    def draw(self) -> None:
        self.screen.fill((255, 0, 255))
        self.parser.glyphs[self.index].draw(self.screen, (30, 60))

    def handleEvents(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.index += 1
                if event.key == pygame.K_LEFT:
                    self.index -= 1
