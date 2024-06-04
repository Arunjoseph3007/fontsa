from file_reader import BinaryFileReader
from glyph import Glyph
from typing import NamedTuple, List


class CompoundGlyphComponent(NamedTuple):
    glyphIndex: int
    flags: bytes
    scaleX: float
    scaleY: float
    offsetX: float
    offsetY: float


class CompundGlyph(Glyph):
    components: List[CompoundGlyphComponent] = []

    def __init__(self, reader: BinaryFileReader) -> None:
        super().__init__(True)
        self.components = []
        xMin = reader.parseInt16()
        yMin = reader.parseInt16()
        xMax = reader.parseInt16()
        yMax = reader.parseInt16()

        hasMoreComponents = 1
        while hasMoreComponents:
            flags = reader.parseUint16()
            glyphIndex = reader.parseUint16()

            argsAreWord = flags & 1
            areSignedValues = flags & (1 << 1)
            hasAScale = flags & (1 << 3)
            hasMoreComponents = flags & (1 << 5)
            hasXYScale = flags & (1 << 6)
            has2by2 = flags & (1 << 7)

            scaleX = 1.0
            scaleY = 1.0
            offsetX = 0.0
            offsetY = 0.0

            if areSignedValues:
                if argsAreWord:
                    offsetX = reader.parseInt16()
                    offsetY = reader.parseInt16()
                else:
                    offsetX = reader.parseInt8()
                    offsetY = reader.parseInt8()

            if hasAScale:
                scaleX = scaleY = reader.parseInt16()
            elif hasXYScale:
                scaleX = reader.parseInt16()
                scaleY = reader.parseInt16()
            elif has2by2:
                reader.parseInt16()
                reader.parseInt16()
                reader.parseInt16()
                reader.parseInt16()

            self.components.append(
                CompoundGlyphComponent(
                    flags=flags,
                    glyphIndex=glyphIndex,
                    scaleX=scaleX,
                    scaleY=scaleY,
                    offsetX=offsetX,
                    offsetY=offsetY,
                )
            )
