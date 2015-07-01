from ..lang import H
from ..lang import sig


@sig(H/ str >> str)
def toUpper(s):
    return s.upper()


@sig(H/ str >> str)
def toLower(s):
    return s.lower()


chr = chr ** (H/ int >> str)
ord = ord ** (H/ str >> int)
