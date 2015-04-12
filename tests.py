import unittest

from hask import in_typeclass

from hask import guard, c
from hask import caseof
from hask import data

from hask import curry
from hask import F

from hask import LazyList, L
from hask import Maybe, Just, Nothing, in_maybe
from hask import Either, Left, Right, in_either

from hask import Show
from hask import Eq
from hask import Ord
from hask import Bounded
from hask import Num
from hask import Functor
from hask import Applicative
from hask import Monad
from hask import Traversable
from hask import Ix
from hask import Foldable


class TestSyntax(unittest.TestCase):

    def test_guard(self):
        # syntax checks
        se = SyntaxError
        with self.assertRaises(se): c(lambda x: x == 10) + c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) - c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) << c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) & c(lambda _: 1)

        with self.assertRaises(se): c(lambda x: x > 1) | c(lambda x: x < 1)
        with self.assertRaises(se): c(lambda x: x == 10) >> "1" >> "2"
        with self.assertRaises(se): "1" >> c(lambda x: x == 10)
        with self.assertRaises(se): guard(1) | c(lambda x: x > 1)
        with self.assertRaises(se): guard(1) | (lambda x: x > 1)
        with self.assertRaises(se): ~guard(1) | (lambda x: x > 1)
        with self.assertRaises(se): ~guard(1)

        # matching checks

    def test_caseof(self):
        pass

    def test_data(self):
        # come back to this after building out type_system
        se = SyntaxError

        with self.assertRaises(se): data("My_ADT")
        with self.assertRaises(se): data(1, "a")
        with self.assertRaises(se): data("My_adt", 1)
        with self.assertRaises(se): data("my_adt", "a")
        with self.assertRaises(se): data("my_adt", chr(110))
        with self.assertRaises(se): data("My_ADT", "a", "a")
        with self.assertRaises(se): data("My_ADT", "a", "cc")
        with self.assertRaises(se): data("My_ADT", "a", "B")

        #with self.assertRaises(se): data("My_ADT", "a") == "1"
        #with self.assertRaises(se): data("My_ADT", "a") == typ("A") | "1"
        #with self.assertRaises(se): data("My_ADT", "a") | typ("A")
        #with self.assertRaises(se): data("My_ADT", "a") == typ("A") == typ("B")
        #self.assertIsNotNone(data("My_ADT", "a") == typ("A") | typ("B"))


class TestHOF(unittest.TestCase):

    def test_curry(self):

        # regular version
        def prod3(x, y, z):
            return x * y * z

        # curried version
        cprod3 = curry(prod3)

        @curry # curried version using decorator
        def dprod3(x, y, z):
            return x * y * z

        self.assertEqual(prod3(1, 2, 3), cprod3(1, 2, 3))
        self.assertEqual(prod3(1, 2, 3), cprod3(1, 2)(3))
        self.assertEqual(prod3(1, 2, 3), cprod3(1)(2, 3))
        self.assertEqual(prod3(1, 2, 3), cprod3(1)(2)(3))
        self.assertEqual(prod3(1, 2, 3), dprod3(1, 2, 3))
        self.assertEqual(prod3(1, 2, 3), dprod3(1, 2)(3))
        self.assertEqual(prod3(1, 2, 3), dprod3(1)(2, 3))
        self.assertEqual(prod3(1, 2, 3), dprod3(1)(2)(3))


class TestMaybe(unittest.TestCase):

    def test_instances(self):
        self.assertTrue(in_typeclass(Maybe, Show))
        self.assertTrue(in_typeclass(Maybe, Eq))
        self.assertTrue(in_typeclass(Maybe, Functor))
        self.assertTrue(in_typeclass(Maybe, Applicative))
        self.assertTrue(in_typeclass(Maybe, Monad))

        self.assertFalse(in_typeclass(Maybe, Num))
        self.assertFalse(in_typeclass(Maybe, Foldable))
        self.assertFalse(in_typeclass(Maybe, Traversable))
        self.assertFalse(in_typeclass(Maybe, Ix))

    def test_show(self):
        self.assertEqual("Just(3)", Just(3).__repr__())
        self.assertEqual("Nothing", Nothing.__repr__())

    def test_eq(self):
        self.assertEqual(Nothing, Nothing)
        self.assertEqual(Just(3), Just(3))
        self.assertEqual(Just("3"), Just("3"))

        self.assertNotEqual(Just(1), Just(3))
        self.assertNotEqual(Just(1), Just("1"))
        self.assertNotEqual(Nothing, Just(3))

        self.assertTrue(Nothing == Nothing or Nothing != Nothing)
        self.assertTrue(Just(1) == Just(1) or Just(1) != Just(1))
        self.assertFalse(Nothing == Nothing and Nothing != Nothing)
        self.assertFalse(Just(1) == Just(1) and Just(1) != Just(1))

    def test_fmap(self):
        # add more
        self.assertEqual(Just(3), Just(2) * (lambda x: x + 1))
        self.assertEqual(Just("1"), Just(1) * str)

    def test_bind(self):
        # add more
        self.assertEqual(Just(10), Just(1) >> (lambda x: Just(x * 10)))
        self.assertEqual(Just("1"), Just(1) >> (lambda x: Just(str(x))))


class TestLazyList(unittest.TestCase):

    def test_instances(self):
        self.assertTrue(in_typeclass(LazyList, Show))
        self.assertTrue(in_typeclass(LazyList, Eq))
        self.assertTrue(in_typeclass(LazyList, Functor))
        self.assertTrue(in_typeclass(LazyList, Applicative))
        self.assertTrue(in_typeclass(LazyList, Monad))
        self.assertTrue(in_typeclass(LazyList, Traversable))
        self.assertTrue(in_typeclass(LazyList, Ix))

    def test_ix(self):
        ie = IndexError
        self.assertEqual(3, LazyList(range(10))[3])
        self.assertEqual(3, LazyList(range(4))[-1])
        self.assertEqual(3, LazyList((i for i in range(10)))[3])
        self.assertEqual(3, LazyList((i for i in range(4)))[-1])
        self.assertEqual(2, LazyList([0, 1, 2, 3])[2])
        self.assertEqual(2, LazyList([0, 1, 2, 3])[-2])
        self.assertEqual(1, LazyList((0, 1, 2, 3))[1])
        self.assertEqual(1, LazyList((0, 1, 2, 3))[-3])

        with self.assertRaises(ie): LazyList((0, 1, 2))[3]
        with self.assertRaises(ie): LazyList((0, 1, 2))[-4]
        with self.assertRaises(ie): LazyList((i for i in range(3)))[3]
        with self.assertRaises(ie): LazyList((i for i in range(3)))[-4]

    def test_eq(self):
        self.assertTrue(list(range(10)), list(LazyList(range(10))))

    def test_functor(self):
        test_f = lambda x: x ** 2 - 1

        self.assertEquals(map(test_f, LazyList(range(9))),
                          list(LazyList(range(9)) * test_f))
        self.assertEquals(map(test_f, range(9)),
                          list(LazyList(range(9)) * test_f))

    def test_list_comp(self):
        self.assertEquals(10, len(L[0, ...][:10]))
        self.assertEquals(L[0, ...][:10], range(10)[:10])
        self.assertEquals(L[-10, ...][:10], range(-10, 0)[:10])

        #self.assertEquals(11, len(L[-5, ..., 5]))
        self.assertEquals(L[-5, ..., 5][:10], range(-5, 5)[:10])


if __name__ == '__main__':
    unittest.main()
