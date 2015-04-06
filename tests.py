import unittest

from pythaskell.syntax import caseof
from pythaskell.syntax import __
from pythaskell.syntax import _p
from pythaskell.syntax import NoCaseMatchException
from pythaskell.types import Just
from pythaskell.types import Nothing


class TestCaseOf(unittest.TestCase):

    def setUp(self):
        pass

    def test_no_double_slash(self):
        with self.assertRaises(SyntaxError):
            m = ~(caseof(4)
                    / 1 % 4
                    / 4 / 3)

    def test_no_double_mod(self):
        with self.assertRaises(SyntaxError):
            m = ~(caseof(4)
                    / 1 % 4 % 4
                    / 4 / 3)

    def test_no_matches_tried(self):
        with self.assertRaises(SyntaxError):
            m = ~caseof(4)

    def test_primitive_value_match(self):
        m = ~(caseof(1) / 1 % "match")
        self.assertEquals("match", m)

    def test_primitive_no_match(self):
        with self.assertRaises(NoCaseMatchException):
             ~(caseof(1)
                    / 2 % 2
                    / 3 % 3)

    def test_wildcard(self):
        m = ~(caseof(2) / __ % "match")
        self.assertEquals("match", m)

    def test_primitive_first_match(self):
        m = ~(caseof(1)
                / 1  % "1"
                / 1  % "2"
                / __ % "3")
        self.assertEquals("1", m)

    def test_obj_match(self):
        class Person(object):
            def __init__(self, name):
                self.name = name
            def __eq__(self, other):
                return self.name == other.name

        bob1 = Person("Bob")
        bob2 = Person("Bob")
        m = ~(caseof(bob1) / bob2 % "match")
        self.assertEquals("match", m)

    def test_obj_no_match(self):
        class Person(object):
            def __init__(self, name):
                self.name = name

        bob1 = Person("Bob")
        bob2 = Person("Bob")
        with self.assertRaises(NoCaseMatchException):
            ~(caseof(bob1) / bob2 % "match")

    def test_primitive_type_match(self):
        m = ~(caseof(9.0)
                / int   % "int"
                / str   % "str"
                / float % "float")
        self.assertEquals("float", m)

    def test_maybe_match(self):
        m = ~(caseof(Just(10))
                / Nothing % "nothing"
                / Just    % "just")
        self.assertEquals("just", m)

    def test_single_bind(self):
        m = ~(caseof((1, 2))
                / (2, _p("foo")) % (_p("foo") + " bar")
                / (1, _p("foo")) % _p("foo"))
        self.assertEquals(m, 2)

    def test_mult_bind(self):
        m = ~(caseof((1, 2, 3))
                / (0, _p(1), _p(2)) % (_p(2), _p(1))
                / (1, _p(1), _p(2)) % (_p(2), _p(1)))
        self.assertEquals(m, (3, 2))

    def test_nested_case(self):
        m = ~(caseof((1, 3))
                / (1, ~(caseof(2) / 2 % 3)) % "match")
        self.assertEquals(m, "match")


class TestGuard(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
