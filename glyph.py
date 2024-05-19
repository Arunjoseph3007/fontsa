from typing import List, Tuple
from utils import isNthBitOn
from file_reader import BinaryFileReader
import pygame.gfxdraw
import pygame


class Glyph:
    numberOfContours: int
    endPtsOfContours: List[int]
    flags: List[bytes]
    points: List[Tuple[int, int]]
    isComPound: bool

    def __init__(self, reader: BinaryFileReader) -> None:
        numberOfContours = reader.parseInt16()
        if numberOfContours < 0:
            # TODO Parse compound Glyf
            self.isComPound = True
            return

        self.isComPound = False
        xMin = reader.parseInt16()
        yMin = reader.parseInt16()
        xMax = reader.parseInt16()
        yMax = reader.parseInt16()

        endPtsOfContours: List[int] = []
        for _ in range(numberOfContours):
            endPtsOfContours.append(reader.parseUint16())

        numberOfPoints = endPtsOfContours[-1] + 1
        instructionLength = reader.parseUint16()
        instructions: List[int] = []
        for _ in range(instructionLength):
            instructions.append(reader.parseUint8())

        flags: List[bytes] = []

        while len(flags) < numberOfPoints:
            flag = reader.takeBytes(1)
            repeat = isNthBitOn(flag, 3)
            flags.append(flag)

            if repeat:
                repeatCount = reader.parseUint8()
                for _ in range(repeatCount):
                    flags.append(flag)

        xCoords: List[int] = []
        yCoords: List[int] = []
        xAcc: int = 0
        yAcc: int = 0

        for flag in flags:
            xShort = isNthBitOn(flag, 1)
            yOffset: int

            if xShort:
                yOffset = reader.parseUint8()
                isPositive = isNthBitOn(flag, 4)
                if not isPositive:
                    yOffset *= -1
            else:
                isRepeat = isNthBitOn(flag, 4)
                if isRepeat:
                    yOffset = 0
                else:
                    yOffset = reader.parseInt16()

            xAcc += yOffset
            xCoords.append(xAcc)

        for flag in flags:
            yShort = isNthBitOn(flag, 2)
            yOffset: int

            if yShort:
                yOffset = reader.parseUint8()
                isPositive = isNthBitOn(flag, 5)
                if not isPositive:
                    yOffset *= -1
            else:
                isRepeat = isNthBitOn(flag, 5)
                if isRepeat:
                    yOffset = 0
                else:
                    yOffset = reader.parseInt16()

            yAcc += yOffset
            yCoords.append(yAcc)

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
