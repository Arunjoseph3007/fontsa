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
            8451,
            18944,
            18944,
            34306,
            34110,
            34110,
            48188,
            109370,
            109370,
            156987,
            156975,
            215345,
            216367,
            216367,
            281392,
        ]
        y = [
            0,
            0,
            765,
            765,
            65538,
            110844,
            152833,
            154878,
            186880,
            217595,
            221949,
            221949,
            252922,
            253016,
            253622,
        ]
        s = 500
        # pygame.draw.polygon(
        #     self.screen, (0, 0, 255), [(x[i] / s, y[i] / s) for i in range(3 + 1)]
        # )
        # pygame.draw.polygon(
        #     self.screen, (0, 0, 255), [(x[i] / s, y[i] / s) for i in range(4, 6 + 1)]
        # )
        # pygame.draw.polygon(
        #     self.screen, (0, 0, 255), [(x[i] / s, y[i] / s) for i in range(7, 9 + 1)]
        # )
        # pygame.draw.polygon(
        #     self.screen, (0, 0, 255), [(x[i] / s, y[i] / s) for i in range(10, 15)]
        # )

        for i in range(15):
            pygame.draw.circle(self.screen, (0, 0, 255), (x[i] / s, y[i] / s), 10)

    def handleEvents(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
