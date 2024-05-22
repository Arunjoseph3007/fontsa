import pygame
import pygame.gfxdraw
from font import Font
from styles import Colors


class Renderer:
    screen: pygame.Surface
    width: int = 1000
    height: int = 650
    title: str = "Fontsa"
    running: bool
    font: Font
    fontSize = 0.05
    letterSpacing = 0.0
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

    def draw(self) -> None:
        self.screen.fill(Colors.BackGround.value)
        self.font.printString(
            self.screen,
            self.input,
            fontSize=self.fontSize,
            letterSpacing=self.letterSpacing,
            color=Colors.Primary.value,
        )

    def handleEvents(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.fontSize *= 0.95
                elif event.key == pygame.K_RIGHT:
                    self.fontSize *= 1.05
                elif event.key == pygame.K_DOWN:
                    self.letterSpacing -= 0.002
                elif event.key == pygame.K_UP:
                    self.letterSpacing += 0.002
                elif event.key == pygame.K_SPACE:
                    self.input = ""
                elif 97 <= event.key <= 122:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.input += chr(event.key - 32)
                    else:
                        self.input += chr(event.key)
