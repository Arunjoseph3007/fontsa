import pygame
import pygame.gfxdraw
from font import Font


class Renderer:
    screen: pygame.Surface
    width: int = 1000
    height: int = 650
    title: str = "Fontsa"
    running: bool
    font: Font
    input: str = ""

    def __init__(self, parser: Font) -> None:
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.running = True
        self.font = parser

    def mainloop(self) -> None:
        while self.running:
            self.update()
            self.draw()
            self.handleEvents()
            pygame.display.update()

    def update(self) -> None:
        pass

    def printString(self, message: str) -> None:
        for i, letter in enumerate(message):
            glyphId = self.font.cmapTable.getGlyphId(ord(letter))
            self.font.glyphs[glyphId].draw(self.screen, (i * 60, 80))

    def draw(self) -> None:
        self.screen.fill((255, 0, 255))
        self.printString(self.input)

    def handleEvents(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.input = ""
                elif 97 <= event.key <= 122:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.input += chr(event.key - 32)
                    else:
                        self.input += chr(event.key)
