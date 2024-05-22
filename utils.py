def isNthBitOn(word: bytes, index: int) -> bool:
    wordNo = index // 8
    bitNo = index % 8
    return word[wordNo] >> bitNo & 1 == 1
