import unittest

from pythaskell.syntax import guard
from pythaskell.syntax import c
from pythaskell.syntax import NoGuardMatchException as NGME
from pythaskell.types import Just
from pythaskell.types import Nothing


class TestSyntax(unittest.TestCase):

    def test_guard(self):
        # syntax checks
        se = SyntaxError
        with self.assertRaises(se): c(lambda x: x > 1) | c(lambda x: x < 1)
        with self.assertRaises(se): c(lambda x: x == 10) >> "1" >> "2"

        with self.assertRaises(se): c(lambda x: x == 10) + 1
        with self.assertRaises(se): c(lambda x: x == 10) - 1
        with self.assertRaises(se): c(lambda x: x == 10) << 2

        with self.assertRaises(se): "1" >> c(lambda x: x == 10)
        with self.assertRaises(se): guard(1) | c(lambda x: x > 1)

        # matching checks

    def test_caseof(self):
        pass


class TestTypes(unittest.TestCase):
    pass


class TestHOF(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
