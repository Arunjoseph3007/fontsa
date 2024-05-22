from typing import List, Tuple, NamedTuple
from utils import isNthBitOn
from file_reader import BinaryFileReader
from styles import Colors
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

    def drawSpline(
        self,
        screen: pygame.Surface,
        points: List[Tuple[int, int]],
        color,
    ):
        steps = 1000
        startPoint = points[0]
        for i, point in enumerate(points[1:-1]):
            pb = points[i + 2]
            midPoint = (point[0] + pb[0]) / 2, (point[1] + pb[1]) / 2
            pygame.gfxdraw.bezier(screen, [startPoint, point, midPoint], steps, color)
            startPoint = midPoint

        pygame.gfxdraw.bezier(
            screen, [startPoint, points[-2], points[-1]], steps, color
        )

    def draw(
        self,
        screen: pygame.Surface,
        loc: Tuple[int, int],
        fontSize=0.05,
        color=Colors.Text,
    ):
        if self.isComPound:
            return

        locX, locY = loc
        newPoints = [
            (x * fontSize + locX, 300 - y * fontSize + locY) for x, y in self.points
        ]

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
                    pygame.draw.aaline(screen, color, spline[0], p)
                    spline = [p]
                elif len(spline) > 1:
                    spline.append(p)
                    self.drawSpline(screen, spline, color)
                    spline = [p]
                else:
                    spline.append(p)
            # Last countour with starting point
            if len(spline) == 1:
                pygame.draw.aaline(screen, color, spline[0], newPoints[startIndex])
            else:
                spline.append(newPoints[startIndex])
                self.drawSpline(screen, spline, color)

            startIndex = endIndex + 1


class CompoundGlyphComponent(NamedTuple):
    a: int
    b: int
    c: int
    d: int
    e: int
    f: int

    def getTanrsformed(self, x: int, y: int) -> Tuple[int, int]:
        m = max(abs(self.a), abs(self.b))
        n = max(abs(self.c), abs(self.d))

        if abs(abs(self.a) - abs(self.c)) <= 33 / 65536:
            m *= 2
        if abs(abs(self.b) - abs(self.d)) <= 33 / 65536:
            n *= 2

        _x = self.a * x + self.c * y + self.e * m
        _y = self.b * x + self.d * y + self.f * n
        return _x, _y


class CompoundGlyph:
    def __init__(self, reader: BinaryFileReader) -> None:
        hasMoreComponents = True
        while hasMoreComponents:
            flags = reader.parseUint16()
            glyphIndex = reader.parseUint16()

            argsAreWord = isNthBitOn(flags, 0)
            hasMoreComponents = isNthBitOn(flags, 5)
            hasAScale = isNthBitOn(flags, 3)
            hasDifferentScaleForXAndY = isNthBitOn(6)
