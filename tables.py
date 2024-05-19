from typing import NamedTuple, List, Dict
from file_reader import BinaryFileReader


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
    glyphIndexMap: Dict[int, int] = {}
    segCount: int

    def __init__(self, reader: BinaryFileReader) -> None:
        version = reader.parseUint16()
        numberSubtables = reader.parseUint16()

        encodingRecords: List[EncodingRecord] = []

        for i in range(numberSubtables):
            platformID = reader.parseUint16()
            encodingID = reader.parseUint16()
            offset = reader.parseUint32()

            encodingRecords.append(
                EncodingRecord(
                    offset=offset, platformID=platformID, encodingID=encodingID
                )
            )

        format = reader.parseUint16()
        length = reader.parseUint16()
        language = reader.parseUint16()
        segCount2x = reader.parseUint16()
        self.segCount = int(segCount2x / 2)
        searchRange = reader.parseUint16()
        entrySelector = reader.parseUint16()
        rangeShift = reader.parseUint16()

        for i in range(self.segCount):
            self.endCodes.append(reader.parseUint16())

        reservedPad = reader.parseUint16()

        for i in range(self.segCount):
            self.startCodes.append(reader.parseUint16())

        for i in range(self.segCount):
            self.idDeltas.append(reader.parseInt16())

        idRangeOffsetsStart = reader.index

        for i in range(self.segCount):
            self.idRangeOffsets.append(reader.parseUint16())

        # Copy pasted code please beware
        for i in range(1, self.segCount):
            glyphIndex = 0
            endCode = self.endCodes[i]
            startCode = self.startCodes[i]
            idDelta = self.idDeltas[i]
            idRangeOffset = self.idRangeOffsets[i]

            for c in range(startCode, endCode):
                if idRangeOffset != 0:
                    startCodeOffset = (c - startCode) * 2
                    currentRangeOffset = i * 2
                    glyphIndexOffset = (
                        idRangeOffsetsStart
                        + currentRangeOffset
                        + idRangeOffset
                        + startCodeOffset
                    )

                    reader.goto(glyphIndexOffset)
                    glyphIndex = reader.parseUint16()
                    if glyphIndex != 0:
                        glyphIndex = (glyphIndex + idDelta) & 0xFFFF
                else:
                    glyphIndex = (c + idDelta) & 0xFFFF
                self.glyphIndexMap[c] = glyphIndex

    def getGlyphId(self, charCode: int) -> int:
        return self.glyphIndexMap[charCode]
