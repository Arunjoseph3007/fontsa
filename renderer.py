import pygame


class Renderer:
    screen: pygame.Surface
    width: int = 1000
    height: int = 650
    title: str = "Fontsa"
    running: bool

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(self.title)
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.running = True

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
        # pygame.draw.circle(self.screen, (0, 0, 255), (250, 250), 75)
        ends = [3, 6, 9, 12, 15]
        x = [
            808,
            100,
            100,
            808,
            754,
            754,
            480,
            154,
            154,
            422,
            194,
            709,
            451,
            451,
            709,
            194,
        ]
        y = [
            0,
            0,
            1456,
            1456,
            84,
            1371,
            728,
            1359,
            96,
            728,
            54,
            54,
            660,
            796,
            1402,
            1402,
        ]

        co = lambda i: (x[i] * 0.4 + 40, y[i] * 0.4 + 40)
        # pygame.draw.polygon(self.screen, (0, 0, 255), [co(i) for i in range(3 + 1)],width=1)
        # pygame.draw.polygon(self.screen, (0, 0, 255), [co(i) for i in range(4, 6 + 1)],width=1)
        # pygame.draw.polygon(self.screen, (0, 0, 255), [co(i) for i in range(7, 9 + 1)],width=1)
        pygame.draw.polygon(self.screen, (0, 0, 255), [co(i) for i in range(10, 16)],width=1)

        for i in range(15):
            pygame.draw.circle(self.screen, (0, 0, 255), co(i), 5)

    def handleEvents(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
