from pathlib import Path


class BinaryFileReader:
    file: str
    buf: bytes
    index: int

    def __init__(self, file: str) -> None:
        self.file = file
        self.buf = Path(self.file).read_bytes()
        self.index = 0

    def goto(self, index: int) -> None:
        self.index = index

    def skip(self, skipBytes: int) -> None:
        self.index += skipBytes

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
