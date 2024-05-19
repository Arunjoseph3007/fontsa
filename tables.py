from typing import NamedTuple, List


class TableRecord(NamedTuple):
    tag: str
    checksum: int
    offset: int
    length: int


class EncodingRecord(NamedTuple):
    platformID: int
    encodingID: int
    offset: int


class HeadTable(NamedTuple):
    majorVersion: int
    minorVersion: int
    fontRevision: int
    checksumAdjustment: int
    magicNumber: int
    flags: int
    unitsPerEm: int
    created: int
    modified: int
    xMin: int
    yMin: int
    xMax: int
    yMax: int
    macStyle: int
    lowestRecPPEM: int
    fontDirectionHint: int
    indexToLocFormat: int
    glyphDataFormat: int


class MaxpTable(NamedTuple):
    version: int
    numGlyphs: int
    maxPoints: int
    maxContours: int
    maxCompositePoints: int
    maxCompositeContours: int
    maxZones: int
    maxTwilightPoints: int
    maxStorage: int
    maxFunctionDefs: int
    maxInstructionDefs: int
    maxStackElements: int
    maxSizeOfInstructions: int
    maxComponentElements: int
    maxComponentDepth: int


class CmapTable:
    startCodes: List[int] = []
    endCodes: List[int] = []
    idDeltas: List[int] = []
    idRangeOffsets: List[int] = []
    segCount: int

    def __init__(
        self, start: List[int], end: List[int], delta: List[int], offset: List[int]
    ) -> None:
        self.startCodes = start
        self.endCodes = end
        self.idDeltas = delta
        self.idRangeOffsets = offset
        self.segCount = len(start)

    def getGlyphId(self, charCode: int) -> int:
        segIndex: int
        for i, j in enumerate(self.startCodes):
            if j >= charCode:
                if self.startCodes[i] > charCode:
                    return 0
                segIndex = i
                break

        if self.idRangeOffsets[segIndex] == 0:
            return charCode + self.idDeltas[segIndex]

        return 0
        # TODO: implement format 4 of cmap tables https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html
        # return (
        #     int(self.idRangeOffsets[segIndex] / 2)
        #     + charCode
        #     - self.startCodes[segIndex]
        #     + self.idRangeOffsets[segIndex]
        # )
