import unittest

from pythaskell.syntax import guard
from pythaskell.syntax import c
from pythaskell.syntax import NoGuardMatchException as NGME

from pythaskell.types import Just
from pythaskell.types import Nothing
from pythaskell.types import Right
from pythaskell.types import Left
from pythaskell.types import in_maybe
from pythaskell.types import in_either

from pythaskell.types import parse_haskell_typestring
from pythaskell.types import parse_constraints
from pythaskell.types import parse_signature
from pythaskell.types import check_paren_balance
from pythaskell.types import TypeStringException as TSE


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


class TestMaybe(unittest.TestCase):

    def test_show(self):
        self.assertEqual("Just(3)", Just(3).show())
        self.assertEqual("Just(3)", Just(3).__repr__())

    def test_eq(self):
        self.assertEqual(Nothing, Nothing)
        self.assertEqual(Just(3), Just(3))
        self.assertEqual(Just("3"), Just("3"))

        self.assertNotEqual(Just(1), Just(3))
        self.assertNotEqual(Nothing, Just(3))

    def test_fmap(self):
        # add more
        self.assertEqual(Just(3), Just(2) * (lambda x: x + 1))
        self.assertEqual(Just("1"), Just(1) * str)

    def test_bind(self):
        # add more
        self.assertEqual(Just(10), Just(1) >> (lambda x: Just(x * 10)))
        self.assertEqual(Just("1"), Just(1) >> (lambda x: Just(str(x))))


class TestParse(unittest.TestCase):

    def setUp(self):
        # some aliases for readability
        self.psig = parse_signature
        self.assertNumArgs = lambda n,x: self.assertEqual(n, len(self.psig(x)))

        self.pcon = parse_constraints
        self.assertCons = lambda n,x: self.assertEqual(n, len(self.pcon(x)))

        self.parse = parse_haskell_typestring
        self.assertParseArgs = lambda n,x: self.assertEqual(n,len(self.parse(x)))


    def test_check_parens(self):
        self.assertTrue(check_paren_balance(""))
        self.assertTrue(check_paren_balance("()"))
        self.assertTrue(check_paren_balance("(())"))
        self.assertTrue(check_paren_balance("((()))(())"))
        self.assertTrue(check_paren_balance("()()()"))
        self.assertTrue(check_paren_balance("(()())()"))
        self.assertTrue(check_paren_balance("((()())(()(()))())"))

        self.assertFalse(check_paren_balance("("))
        self.assertFalse(check_paren_balance(")"))
        self.assertFalse(check_paren_balance("(()"))
        self.assertFalse(check_paren_balance("())"))
        self.assertFalse(check_paren_balance("())"))
        self.assertFalse(check_paren_balance("())"))
        self.assertFalse(check_paren_balance(")("))
        self.assertFalse(check_paren_balance(")()("))
        self.assertFalse(check_paren_balance("((()())(())()))())"))

    def test_parse_constraint(self):
        self.assertCons(1, "Monad m")
        self.assertCons(2, "Monad m,Functor f")
        self.assertCons(2, "Monad m, Functor f")
        self.assertCons(3, "Monad m,Functor f,Num a")
        self.assertCons(3, "Monad m, Functor f, Num a")
        self.assertCons(3, "Monad m, Functor m, Num a")

        with self.assertRaises(TSE): self.pcon("Monadm")
        with self.assertRaises(TSE): self.pcon("Monad m a")
        with self.assertRaises(TSE): self.pcon("Monad m a, Functor f")

    def test_parse_sig(self):
        self.assertNumArgs(1, "a")
        self.assertNumArgs(1, "m a")

        self.assertNumArgs(2, "a -> a")
        self.assertNumArgs(2, "a -> b")
        self.assertNumArgs(2, "a -> m a")
        self.assertNumArgs(2, "g a -> a")
        self.assertNumArgs(2, "g t b a -> m f a")
        self.assertNumArgs(2, "g -> (t -> b -> a -> m -> f a)")
        self.assertNumArgs(2, "g -> ((t -> b -> a) -> (m -> f a))")
        self.assertNumArgs(2, "g -> ((t -> (b -> a)) -> (m -> f a))")

        self.assertNumArgs(3, "a -> b -> b")
        self.assertNumArgs(3, "(a -> b) -> a -> b")
        self.assertNumArgs(3, "a -> (a -> b) -> b")
        self.assertNumArgs(3, "a -> b -> (a -> b)")
        self.assertNumArgs(3, "g -> (t -> b -> a) -> (m -> f a)")

        self.assertNumArgs(4, "a -> b -> c -> a")
        self.assertNumArgs(5, "a -> b -> c -> d -> a")
        self.assertNumArgs(100, "a -> " * 99 + "a")

    def test_whitespace(self):
        with self.assertRaises(TSE): self.parse(" f :: a -> a")
        with self.assertRaises(TSE): self.parse("f :: a -> a ")
        with self.assertRaises(TSE): self.parse("f  :: a -> a")
        with self.assertRaises(TSE): self.parse("f:: a -> a")
        with self.assertRaises(TSE): self.parse("f ::a -> a")
        with self.assertRaises(TSE): self.parse("f ::a -> a")
        with self.assertRaises(TSE): self.parse("f :: a-> b")
        with self.assertRaises(TSE): self.parse("f :: a ->b")
        with self.assertRaises(TSE): self.parse("f :: a->b")

    def test_structure(self):
        with self.assertRaises(TSE): self.parse("asdf")
        with self.assertRaises(TSE): self.parse("f ::")
        with self.assertRaises(TSE): self.parse("f-f ::")
        with self.assertRaises(TSE): self.parse("f f ::")
        with self.assertRaises(TSE): self.parse("f :: a => a")
        with self.assertRaises(TSE): self.parse("f :: (Num a) => a => a")

    def test_full_parse(self):
        self.assertParseArgs(1, "f :: a")
        self.assertParseArgs(1, "f :: (Monad m) => m a")
        self.assertParseArgs(1, "f :: (Monad m, Functor f) => m f a")


if __name__ == '__main__':
    unittest.main()
