import functools
import unittest

from hask import in_typeclass, arity, sig, typ

from hask import guard, c
from hask import caseof
from hask import data
from hask import LazyList, L
from hask import F, curry, const, flip
from hask import map as hmap
from hask import filter as hfilter
from hask import id as hid
from hask import Maybe, Just, Nothing, in_maybe
from hask import Either, Left, Right, in_either
from hask import Show, Eq, Ord, Bounded, Num
from hask import Functor, Applicative, Monad
from hask import Traversable, Ix, Foldable, Iterator


class TestTypeSystem(unittest.TestCase):

    def test_arity(self):
        self.assertEquals(0, arity(lambda: "foo"))
        self.assertEquals(1, arity(lambda **kwargs: kwargs))
        self.assertEquals(1, arity(lambda *args: args))
        self.assertEquals(1, arity(lambda x: 0))
        self.assertEquals(1, arity(lambda x, *args: 0))
        self.assertEquals(1, arity(lambda x, *args, **kw: 0))
        self.assertEquals(1, arity(lambda x: x + 1))
        self.assertEquals(2, arity(lambda x, y: x + y))
        self.assertEquals(2, arity(lambda x, y, *args: x + y + z))
        self.assertEquals(2, arity(lambda x, y, *args, **kw: x + y + z))
        self.assertEquals(3, arity(lambda x, y, z: x + y + z))
        self.assertEquals(3, arity(lambda x, y, z, *args: x + y + z))
        self.assertEquals(3, arity(lambda x, y, z, *args, **kw: x + y + z))

        self.assertEquals(1, arity(lambda x: lambda y: x))
        self.assertEquals(1, arity(functools.partial(lambda x,y: x+y, 2)))
        self.assertEquals(2, arity(functools.partial(lambda x,y: x+y)))
        self.assertEquals(2, arity(functools.partial(lambda x, y, z: x+y, 2)))

    def test_sig(self):
        te = TypeError

        @sig(int, int)
        def f(x):
            return x + 4

        self.assertEquals(9, f(5))
        with self.assertRaises(te): f(1.0)
        with self.assertRaises(te): f("foo")
        with self.assertRaises(te): f(5, 4)
        with self.assertRaises(te): f()

        with self.assertRaises(te):
            @sig(int)
            def g(x):
                return x / 2

        with self.assertRaises(te):
            @sig(int, int, int)
            def g(x):
                return x / 2

        with self.assertRaises(te):
            @sig(float, float)
            def g(x):
                return x / 2
            g(9)

        with self.assertRaises(te):
            @sig(int, int)
            def g(x):
                return x / 2.0
            g(1)


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

    def test_F(self):
        # regular version
        def sum3(x, y, z):
            return x * y * z

        @F # version wrapped using decorator
        def dsum3(x, y, z):
            return x * y * z

        self.assertEqual(sum3(1, 2, 3), F(sum3)(1, 2, 3))
        self.assertEqual(sum3(1, 2, 3), F(sum3)(1, 2)(3))
        self.assertEqual(sum3(1, 2, 3), F(sum3)(1)(2, 3))
        self.assertEqual(sum3(1, 2, 3), F(sum3)(1)(2)(3))

        self.assertEqual(sum3(1, 2, 3), dsum3(1, 2, 3))
        self.assertEqual(sum3(1, 2, 3), dsum3(1, 2)(3))
        self.assertEqual(sum3(1, 2, 3), dsum3(1)(2, 3))
        self.assertEqual(sum3(1, 2, 3), dsum3(1)(2)(3))

    def test_F_functor(self):
        f = lambda x: (x + 100) % 75
        g = lambda x: x * 21
        h = lambda x: (x - 31) / 3

        self.assertEquals(f(56), (hid * f)(56))
        self.assertEquals(f(g(h(56))), (hid * f * g * h)(56))

    def test_hid(self):
        self.assertEquals(3, hid(3))
        self.assertEquals(3, hid(hid(hid(3))))
        self.assertEquals(3, hid.fmap(hid).fmap(hid)(3))
        self.assertEquals(3, (hid * hid * hid)(3))

    def test_const(self):
        self.assertEquals(1, const(1, 2))
        self.assertEquals(1, const(1)(2))
        self.assertEquals("foo", const("foo", 2))
        self.assertEquals(1, (const(1) * const(2) * const(3))(4))

    def test_flip(self):
        test_f1 = lambda x, y: x - y
        test_f2 = lambda x, y, z: (x - y) / z

        self.assertEquals(test_f1(9, 1), flip(test_f1)(1, 9))
        #self.assertEquals(test_f1(9, 1), flip(test_f1)(1)(9))
        self.assertEquals(test_f2(91, 10, 2), flip(test_f2)(10, 91, 2))


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
        self.assertFalse(in_typeclass(Maybe, Iterator))

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
        #self.assertNotEqual(Nothing, None)

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
        self.assertEquals(list(range(10)), list(LazyList(range(10))))
        self.assertEquals(LazyList(range(10)), LazyList(range(10)))
        self.assertEquals(L[range(10)], LazyList(range(10)))
        self.assertEquals(LazyList(range(10)),
                          LazyList((i for i in range(10))))

    def test_functor(self):
        test_f = lambda x: x ** 2 - 1

        self.assertEquals(map(test_f, list(LazyList(range(9)))),
                          list(LazyList(range(9)) * test_f))
        self.assertEquals(map(test_f, LazyList(range(9))),
                          list(LazyList(range(9)) * test_f))
        self.assertEquals(map(test_f, range(9)),
                          list(LazyList(range(9)) * test_f))

    def test_list_comp(self):
        self.assertEquals(10, len(L[0, ...][:10]))
        self.assertEquals(L[0, ...][:10], range(10)[:10])
        self.assertEquals(L[-10, ...][:10], range(-10, 0)[:10])

        self.assertEquals(11, len(L[-5, ..., 5]))
        self.assertEquals(L[-5, ..., 5][:10], range(-5, 5)[:10])

    def test_hmap(self):
        test_f = lambda x: (x + 100) / 2
        self.assertEquals(map(test_f, range(20)), list(hmap(test_f, range(20))))

    def test_hfilter(self):
        test_f = lambda x: x % 2 == 0
        self.assertEquals(filter(test_f, range(20)), list(hfilter(test_f, range(20))))


if __name__ == '__main__':
    unittest.main()
