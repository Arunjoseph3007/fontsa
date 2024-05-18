def isNthBitOn(word: bytes, index: int) -> bool:
    return word[0] >> index & 1 == 1
