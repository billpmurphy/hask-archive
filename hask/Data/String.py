from ..lang.syntax import L


def lines(string):
    """
    lines :: String -> [String]

    lines breaks a string up into a list of strings at newline characters.
    The resulting strings do not contain newlines.
    """
    return L[string.split("\n")]


def words(string):
    """
    words :: String -> [String]

    words breaks a string up into a list of words, which were delimited by
    white space.
    """
    return L[string.split(" ")]


def unlines(strings):
    """
    lines :: [String] -> String

    unlines is an inverse operation to lines. It joins lines, after appending a
    terminating newline to each.
    """
    return "\n".join(strings)


def unwords(strings):
    """
    unwords :: [String] -> String

    unwords is an inverse operation to words. It joins words with separating
    spaces.
    """
    return " ".join(strings)
