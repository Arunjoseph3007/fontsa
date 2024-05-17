from pathlib import Path
from typing import Self, NamedTuple, Dict, List


def isNthBitOn(word: bytes, index: int) -> bool:
    return word[0] >> index & 1 == 1


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


class FontParser:
    file: str
    buf: bytes
    index: int
    fontDirectory: Dict[str, TableRecord] = {}
    cmapTable: CmapTable
    maxpTable: MaxpTable
    headTable: HeadTable
    locaTable: List[int] = []

    def __init__(self, file: str) -> None:
        self.file = file
        self.buf = Path(self.file).read_bytes()
        self.index = 0

    def parseFontDirectory(self) -> None:
        sfntVersion = self.parseUint32()
        numTables = self.parseUint16()
        searchRange = self.parseUint16()
        entrySelector = self.parseUint16()
        rangeShift = self.parseUint16()

        for i in range(numTables):
            tag = self.parseTag()
            checksum = self.parseUint32()
            offset = self.parseUint32()
            length = self.parseUint32()

            self.fontDirectory[tag] = TableRecord(
                tag=tag, checksum=checksum, length=length, offset=offset
            )

        self.parseHeadTable()
        self.parseMaxpTable()
        self.parseCmapTable()
        self.parseLocaTable()
        self.parseGlyphTable()

    def gotoTable(self, tableName: str) -> TableRecord:
        tableRecord = self.fontDirectory[tableName]

        if not tableRecord:
            raise NameError(f"{tableName} Table not found")
        self.goto(tableRecord.offset)
        return tableRecord

    def parseCmapTable(self) -> None:
        self.gotoTable("cmap")

        version = self.parseUint16()
        numberSubtables = self.parseUint16()

        encodingRecords: List[EncodingRecord] = []

        for i in range(numberSubtables):
            platformID = self.parseUint16()
            encodingID = self.parseUint16()
            offset = self.parseUint32()

            encodingRecords.append(
                EncodingRecord(
                    offset=offset, platformID=platformID, encodingID=encodingID
                )
            )

        format = self.parseUint16()
        length = self.parseUint16()
        language = self.parseUint16()
        segCount2x = self.parseUint16()
        segCount = int(segCount2x / 2)
        searchRange = self.parseUint16()
        entrySelector = self.parseUint16()
        rangeShift = self.parseUint16()

        endCodes: List[int] = []
        startCodes: List[int] = []
        idDeltas: List[int] = []
        idRangeOffsets: List[int] = []
        for i in range(segCount):
            endCodes.append(self.parseUint16())

        reservedPad = self.parseUint16()

        for i in range(segCount):
            startCodes.append(self.parseUint16())

        for i in range(segCount):
            idDeltas.append(self.parseInt16())

        for i in range(segCount):
            idRangeOffsets.append(self.parseUint16())

        self.cmapTable = CmapTable(
            start=startCodes, end=endCodes, delta=idDeltas, offset=idRangeOffsets
        )

    def parseMaxpTable(self) -> None:
        self.gotoTable("maxp")

        self.maxpTable = MaxpTable(
            version=self.parseUint32(),
            numGlyphs=self.parseUint16(),
            maxPoints=self.parseUint16(),
            maxContours=self.parseUint16(),
            maxCompositePoints=self.parseUint16(),
            maxCompositeContours=self.parseUint16(),
            maxZones=self.parseUint16(),
            maxTwilightPoints=self.parseUint16(),
            maxStorage=self.parseUint16(),
            maxFunctionDefs=self.parseUint16(),
            maxInstructionDefs=self.parseUint16(),
            maxStackElements=self.parseUint16(),
            maxSizeOfInstructions=self.parseUint16(),
            maxComponentElements=self.parseUint16(),
            maxComponentDepth=self.parseUint16(),
        )

    def parseHeadTable(self) -> None:
        self.gotoTable("head")

        self.headTable = HeadTable(
            majorVersion=self.parseUint16(),
            minorVersion=self.parseUint16(),
            fontRevision=self.parseUint32(),
            checksumAdjustment=self.parseUint32(),
            magicNumber=self.parseUint32(),
            flags=self.parseUint16(),
            unitsPerEm=self.parseUint16(),
            created=self.parseLongDateTime(),
            modified=self.parseLongDateTime(),
            xMin=self.parseInt16(),
            yMin=self.parseInt16(),
            xMax=self.parseInt16(),
            yMax=self.parseInt16(),
            macStyle=self.parseUint16(),
            lowestRecPPEM=self.parseUint16(),
            fontDirectionHint=self.parseInt16(),
            indexToLocFormat=self.parseInt16(),
            glyphDataFormat=self.parseInt16(),
        )

    def parseLocaTable(self) -> None:
        self.gotoTable("loca")

        isShort = self.headTable.indexToLocFormat == 0

        for _ in range(self.maxpTable.numGlyphs + 1):
            self.locaTable.append(
                self.parseUint16() * 2 if isShort else self.parseUint32()
            )

    def parseGlyphTable(self) -> None:
        glyfTableRecord = self.gotoTable("glyf")

        for offset in self.locaTable[:1]:
            self.goto(glyfTableRecord.offset + offset)
            numberOfContours = self.parseInt16()
            xMin = self.parseInt16()
            yMin = self.parseInt16()
            xMax = self.parseInt16()
            yMax = self.parseInt16()

            endPtsOfContours: List[int] = []

            for _ in range(numberOfContours):
                endPtsOfContours.append(self.parseUint16())

            numberOfPoints = endPtsOfContours[-1]
            instructionLength = self.parseUint16()
            instructions: List[int] = []
            for _ in range(instructionLength):
                instructions.append(self.parseUint8())

            flags: List[bytes] = []

            while len(flags) < numberOfPoints:
                flag = self.takeBytes(1)
                repeat = isNthBitOn(flag, 3)
                flags.append(flag)

                if repeat:
                    repeatCount = self.parseUint8()
                    print(f"{repeatCount}")
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
                    yOffset = self.parseUint8()
                    isPositive = isNthBitOn(flag, 4)
                    if not isPositive:
                        yOffset *= -1
                else:
                    isRepeat = isNthBitOn(flag, 4)
                    if isRepeat:
                        yOffset = 0
                    else:
                        yOffset = self.parseUint16()

                xAcc += yOffset
                xCoords.append(xAcc)

            for flag in flags:
                yShort = isNthBitOn(flag, 2)
                yOffset: int

                if yShort:
                    yOffset = self.parseUint8()
                    isPositive = isNthBitOn(flag, 5)
                    if not isPositive:
                        yOffset *= -1
                else:
                    isRepeat = isNthBitOn(flag, 5)
                    if isRepeat:
                        yOffset = 0
                    else:
                        yOffset = self.parseUint16()

                yAcc += yOffset
                yCoords.append(yAcc)

            print(endPtsOfContours, xCoords, yCoords, sep="\n")

    def goto(self, index: int) -> Self:
        self.index = index
        return self

    def skip(self, skipBytes: int) -> Self:
        self.index += skipBytes
        return self

    def getBytes(self, noOfBytes: int) -> bytes:
        return self.buf[self.index : self.index + noOfBytes]

    def parseTag(self) -> str:
        data = self.getBytes(4).decode("utf-8")
        self.index += 4
        return data

    def parseUint32(self) -> int:
        data = int.from_bytes(self.getBytes(4), signed=False)
        self.index += 4
        return data

    def parseUint16(self) -> int:
        data = int.from_bytes(self.getBytes(2), signed=False)
        self.index += 2
        return data

    def parseUint8(self) -> int:
        data = int.from_bytes(self.getBytes(1), signed=False)
        self.index += 1
        return data

    def parseInt16(self) -> int:
        data = int.from_bytes(self.getBytes(2), signed=True)
        self.index += 2
        return data

    def parseLongDateTime(self) -> int:
        data = int.from_bytes(self.getBytes(8), signed=True)
        self.index += 8
        return data

    def takeBytes(self, length: int) -> bytes:
        data = self.getBytes(length)
        self.index += length
        return data
