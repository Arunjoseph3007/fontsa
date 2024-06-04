from typing import Dict, List, Tuple
from file_reader import BinaryFileReader
from pygame import Surface
from tables import (
    CmapTable,
    HeadTable,
    List,
    MaxpTable,
    TableRecord,
    HmtxTable,
)
from glyph import SimpleGlyph, Glyph
from compound_glyph import CompundGlyph
from styles import Colors


class Font:
    fontDirectory: Dict[str, TableRecord] = {}
    cmapTable: CmapTable
    maxpTable: MaxpTable
    headTable: HeadTable
    hmtxTable: HmtxTable
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
        self.parseHmtxtable(reader)

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

        self.cmapTable = CmapTable(reader)

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
            numContours = reader.parseInt16()
            isSimple = numContours >= 0
            newGlyph = (
                SimpleGlyph(reader, numContours) if isSimple else CompundGlyph(reader)
            )
            self.glyphs.append(newGlyph)

    def parseHmtxtable(self, reader: BinaryFileReader) -> None:
        self.gotoTable("hhea", reader)
        reader.skip(34)
        numOfLongHorMetrics = reader.parseUint16()

        self.gotoTable("hmtx", reader)

        hMetrics: List[Tuple[int, int]] = []
        leftSideBearings: List[int] = []
        for i in range(numOfLongHorMetrics):
            advanceWidth = reader.parseUint16()
            leftSideBearing = reader.parseInt16()
            hMetrics.append((advanceWidth, leftSideBearing))

        for i in range(self.maxpTable.numGlyphs - numOfLongHorMetrics):
            leftSideBearings.append(reader.parseUint16())

        self.hmtxTable = HmtxTable(hMetrics=hMetrics, leftSideBearings=leftSideBearings)

    def printString(
        self,
        screen: Surface,
        message: str,
        fontSize=0.05,
        letterSpacing=0,
        color=Colors.Text.value,
    ) -> None:
        x = 100
        for i, letter in enumerate(message):
            glyphId = self.cmapTable.getGlyphId(ord(letter))
            advancedWidth, leftSideBearing = self.hmtxTable.getMetric(glyphId)
            x += leftSideBearing * (fontSize + letterSpacing)
            self.drawGlyf(screen, glyphId, (x, 80), fontSize=fontSize, color=color)
            # self.glyphs[glyphId].draw(screen, (x, 80), fontSize=fontSize, color=color)
            x += advancedWidth * (fontSize + letterSpacing)

    def drawGlyf(
        self,
        screen: Surface,
        glyphId: int,
        loc: Tuple[int, int],
        fontSize=0.05,
        color=Colors.Text.value,
    ):
        glyph = self.glyphs[glyphId]

        if glyph.isCompound:
            for component in glyph.components:
                self.drawGlyf(
                    screen, component.glyphIndex, loc, fontSize=fontSize, color=color
                )
        else:
            glyph.draw(screen, loc, fontSize=fontSize, color=color)
