from typing import List, Tuple

import pygame.gfxdraw
from utils import isNthBitOn
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
        steps = 20
        blue = (0, 0, 255)
        green = (0, 255, 0)
        locX, locY = loc
        newPoints = [(x * 0.2 + locX, 300 - y * 0.2 + locY) for x, y in self.points]

        for i, p in enumerate(newPoints):
            onTheCurve = isNthBitOn(self.flags[i], 0)
            pygame.draw.circle(screen, blue if onTheCurve else green, p, 3)

        startIndex = 0

        spline: List[Tuple[int, int]] = []
        for endIndex in self.endPtsOfContours:
            spline = []
            for _i, p in enumerate(newPoints[startIndex : endIndex + 1]):
                i = _i + startIndex
                onTheCurve = isNthBitOn(self.flags[i], 0)
                if not onTheCurve:
                    spline.append(p)
                elif len(spline) == 1:
                    pygame.draw.aaline(screen, blue, spline[0], p)
                    spline = [p]
                elif len(spline) > 1:
                    spline.append(p)
                    pygame.gfxdraw.bezier(screen, spline, steps, blue)
                    spline = [p]
                else:
                    spline.append(p)
            # Last countour with starting point
            if len(spline) == 1:
                pygame.draw.aaline(screen, blue, spline[0], newPoints[startIndex])
            else:
                spline.append(newPoints[startIndex])
                pygame.gfxdraw.bezier(screen, spline, steps, blue)

            startIndex = endIndex + 1
