from typing import List, Tuple
import pygame


class Glyph:
    numberOfContours: int
    endPtsOfContours: List[int]
    flags: List[bytes]
    points: List[Tuple[int, int]]

    def __init__(
        self,
        numberOfContours: int,
        endPtsOfContours: List[int],
        flags: List[bytes],
        xCoords: List[int],
        yCoords: List[int],
    ) -> None:
        self.numberOfContours = numberOfContours
        self.endPtsOfContours = endPtsOfContours
        self.flags = flags
        self.points = [
            (xCoords[i], yCoords[i]) for i in range(endPtsOfContours[-1] + 1)
        ]

    def draw(self, screen: pygame.Surface, loc: Tuple[int, int]):
        locX, locY = loc
        newPoints = [(x * 0.1 + locX, y * 0.1 + locY) for x, y in self.points]

        # for p in newPoints:
        #     pygame.draw.circle(screen, (0, 0, 255), p, 5)

        startIndex = 0

        for endIndex in self.endPtsOfContours:
            pygame.draw.polygon(
                screen, (0, 0, 255), newPoints[startIndex : endIndex + 1], width=1
            )
            startIndex = endIndex + 1
