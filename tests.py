import unittest

from hask import in_typeclass

from hask import guard, c
from hask import caseof
from hask import data, typ

from hask import LazyList, l
from hask import Maybe, Just, Nothing, in_maybe
from hask import Either, Left, Right, in_either

from hask import Show
from hask import Eq
from hask import Num
from hask import Functor
from hask import Applicative
from hask import Monad
from hask import Traversable
from hask import Ix


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
        se = SyntaxError

        with self.assertRaises(se): data("My_ADT")
        with self.assertRaises(se): data(1, "a")
        with self.assertRaises(se): data("My_adt", 1)
        with self.assertRaises(se): data("my_adt", "a")
        with self.assertRaises(se): data("my_adt", chr(110))
        with self.assertRaises(se): data("My_ADT", "a", "a")
        with self.assertRaises(se): data("My_ADT", "a", "cc")
        with self.assertRaises(se): data("My_ADT", "a", "B")

        with self.assertRaises(se): data("My_ADT", "a") == "1"
        with self.assertRaises(se): data("My_ADT", "a") == typ("A") | "1"
        with self.assertRaises(se): data("My_ADT", "a") | typ("A")

        # wth is going on here?
        #with self.assertRaises(se): data("My_ADT", "a") == typ("A") == typ("B")

        self.assertIsNotNone(data("My_ADT", "a") == typ("A") | typ("B"))


class TestMaybe(unittest.TestCase):

    def test_instances(self):
        self.assertTrue(in_typeclass(Maybe, Show))
        self.assertTrue(in_typeclass(Maybe, Eq))
        self.assertTrue(in_typeclass(Maybe, Functor))
        self.assertTrue(in_typeclass(Maybe, Applicative))
        self.assertTrue(in_typeclass(Maybe, Monad))

        self.assertFalse(in_typeclass(Maybe, Num))

    def test_show(self):

        self.assertEqual("Just(3)", Just(3).__repr__())

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
        #self.assertTrue(in_typeclass(LazyList, Eq))
        self.assertTrue(in_typeclass(LazyList, Functor))
        self.assertTrue(in_typeclass(LazyList, Applicative))
        self.assertTrue(in_typeclass(LazyList, Monad))
        self.assertTrue(in_typeclass(LazyList, Traversable))
        self.assertTrue(in_typeclass(LazyList, Ix))

    def test_ix(self):
        self.assertEqual(3, LazyList(range(10))[3])
        self.assertEqual(3, LazyList(range(4))[-1])
        self.assertEqual(3, LazyList((i for i in range(10)))[3])
        self.assertEqual(3, LazyList((i for i in range(4)))[-1])
        self.assertEqual(2, LazyList([0, 1, 2, 3])[2])
        self.assertEqual(2, LazyList([0, 1, 2, 3])[-2])
        self.assertEqual(1, LazyList((0, 1, 2, 3))[1])
        self.assertEqual(1, LazyList((0, 1, 2, 3))[-3])

        with self.assertRaises(IndexError): LazyList((0, 1, 2))[3]
        with self.assertRaises(IndexError): LazyList((0, 1, 2))[-4]

    def test_eq(self):
        self.assertTrue(list(range(10)), list(LazyList(range(10))))

    def test_functor(self):
        test_f = lambda x: x ** 2 - 1

        self.assertEquals(map(test_f, range(9)),
                          list(LazyList(range(9)) * test_f))

    def test_list_comp(self):
        self.assertEquals(l[0, ...][:10], range(10)[:10])


if __name__ == '__main__':
    unittest.main()
