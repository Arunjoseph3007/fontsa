from typing import NamedTuple, Dict, List, Union
from file_reader import BinaryFileReader
from glyph import Glyph
from utils import isNthBitOn


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


class Font:
    fontDirectory: Dict[str, TableRecord] = {}
    cmapTable: CmapTable
    maxpTable: MaxpTable
    headTable: HeadTable
    locaTable: List[int] = []
    glyphs: List[Glyph] = []

    def __init__(self, file: str) -> None:
        reader = BinaryFileReader(file)

        self.parseFontDirectory(reader)
        self.parseHeadTable(reader)
        self.parseMaxpTable(reader)
        self.parseCmapTable(reader)
        self.parseLocaTable(reader)
        self.parseGlyphTable(reader)

    def parseFontDirectory(self, reader: BinaryFileReader) -> None:
        sfntVersion = reader.parseUint32()
        numTables = reader.parseUint16()
        searchRange = reader.parseUint16()
        entrySelector = reader.parseUint16()
        rangeShift = reader.parseUint16()

        for i in range(numTables):
            tag = reader.parseTag()
            checksum = reader.parseUint32()
            offset = reader.parseUint32()
            length = reader.parseUint32()

            self.fontDirectory[tag] = TableRecord(
                tag=tag, checksum=checksum, length=length, offset=offset
            )

    def gotoTable(self, tableName: str, reader: BinaryFileReader) -> TableRecord:
        tableRecord = self.fontDirectory[tableName]

        if not tableRecord:
            raise NameError(f"{tableName} Table not found")
        reader.goto(tableRecord.offset)
        return tableRecord

    def parseCmapTable(self, reader: BinaryFileReader) -> None:
        self.gotoTable("cmap", reader)

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
        segCount = int(segCount2x / 2)
        searchRange = reader.parseUint16()
        entrySelector = reader.parseUint16()
        rangeShift = reader.parseUint16()

        endCodes: List[int] = []
        startCodes: List[int] = []
        idDeltas: List[int] = []
        idRangeOffsets: List[int] = []
        for i in range(segCount):
            endCodes.append(reader.parseUint16())

        reservedPad = reader.parseUint16()

        for i in range(segCount):
            startCodes.append(reader.parseUint16())

        for i in range(segCount):
            idDeltas.append(reader.parseInt16())

        for i in range(segCount):
            idRangeOffsets.append(reader.parseUint16())

        self.cmapTable = CmapTable(
            start=startCodes, end=endCodes, delta=idDeltas, offset=idRangeOffsets
        )

    def parseMaxpTable(self, reader: BinaryFileReader) -> None:
        self.gotoTable("maxp", reader)

        self.maxpTable = MaxpTable(
            version=reader.parseUint32(),
            numGlyphs=reader.parseUint16(),
            maxPoints=reader.parseUint16(),
            maxContours=reader.parseUint16(),
            maxCompositePoints=reader.parseUint16(),
            maxCompositeContours=reader.parseUint16(),
            maxZones=reader.parseUint16(),
            maxTwilightPoints=reader.parseUint16(),
            maxStorage=reader.parseUint16(),
            maxFunctionDefs=reader.parseUint16(),
            maxInstructionDefs=reader.parseUint16(),
            maxStackElements=reader.parseUint16(),
            maxSizeOfInstructions=reader.parseUint16(),
            maxComponentElements=reader.parseUint16(),
            maxComponentDepth=reader.parseUint16(),
        )

    def parseHeadTable(self, reader: BinaryFileReader) -> None:
        self.gotoTable("head", reader)

        self.headTable = HeadTable(
            majorVersion=reader.parseUint16(),
            minorVersion=reader.parseUint16(),
            fontRevision=reader.parseUint32(),
            checksumAdjustment=reader.parseUint32(),
            magicNumber=reader.parseUint32(),
            flags=reader.parseUint16(),
            unitsPerEm=reader.parseUint16(),
            created=reader.parseLongDateTime(),
            modified=reader.parseLongDateTime(),
            xMin=reader.parseInt16(),
            yMin=reader.parseInt16(),
            xMax=reader.parseInt16(),
            yMax=reader.parseInt16(),
            macStyle=reader.parseUint16(),
            lowestRecPPEM=reader.parseUint16(),
            fontDirectionHint=reader.parseInt16(),
            indexToLocFormat=reader.parseInt16(),
            glyphDataFormat=reader.parseInt16(),
        )

    def parseLocaTable(self, reader: BinaryFileReader) -> None:
        self.gotoTable("loca", reader)

        isShort = self.headTable.indexToLocFormat == 0

        for _ in range(self.maxpTable.numGlyphs):
            self.locaTable.append(
                reader.parseUint16() * 2 if isShort else reader.parseUint32()
            )

        endAddress = reader.parseUint16() * 2 if isShort else reader.parseUint32()

    def parseGlyphTable(self, reader: BinaryFileReader) -> None:
        glyfTableRecord = self.gotoTable("glyf", reader)

        for offset in self.locaTable:
            reader.goto(glyfTableRecord.offset + offset)
            newGlyph = self.parseGlyph(reader)
            if newGlyph:
                self.glyphs.append(newGlyph)

    def parseGlyph(self, reader: BinaryFileReader) -> Union[Glyph, None]:
        numberOfContours = reader.parseInt16()
        if numberOfContours < 0:
            # TODO Parse compound Glyf
            return None

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

        return Glyph(
            numberOfContours=numberOfContours,
            endPtsOfContours=endPtsOfContours,
            flags=flags,
            xCoords=xCoords,
            yCoords=yCoords,
        )
