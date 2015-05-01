import functools
import unittest

from hask.lang.syntax import Syntax

from hask.stdlib.adt import make_data_const, make_type_const
from hask.stdlib.adt import derive_eq
from hask.stdlib.adt import derive_show
from hask.stdlib.adt import derive_read
from hask.stdlib.adt import derive_ord

from hask import in_typeclass, arity, sig, typ, H, sig2
from hask import guard, c, otherwise, NoGuardMatchException
from hask import caseof
from hask import __
from hask import data, d, deriving
from hask import List, L
from hask import F, const, flip, Func
from hask import map as hmap
from hask import filter as hfilter
from hask import id as hid
from hask import Maybe, Just, Nothing, in_maybe
from hask import Either, Left, Right, in_either
from hask import Typeable, Typeclass
from hask import Show, Eq, Ord, Bounded, Num
from hask import Enum, succ, pred
from hask import Functor, Applicative, Monad
from hask import Traversable, Ix, Foldable, Iterator


class TestTypeSystem(unittest.TestCase):

    def test_arity(self):
        self.assertEquals(0, arity(1))
        self.assertEquals(0, arity("foo"))
        self.assertEquals(0, arity([1, 2, 3]))
        self.assertEquals(0, arity((1, 1)))
        self.assertEquals(0, arity((lambda x: x + 1, 1)))
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
        self.assertEquals(1, arity(lambda x: lambda y: lambda z: x))
        self.assertEquals(2, arity(lambda x, z: lambda y: x))
        self.assertEquals(1, arity(functools.partial(lambda x,y: x+y, 2)))
        self.assertEquals(2, arity(functools.partial(lambda x,y: x+y)))
        self.assertEquals(2, arity(functools.partial(lambda x, y, z: x+y, 2)))

        class X0(object):
            def __init__(self):
                pass

        self.assertEquals(1, arity(X0.__init__))

        class X1(object):
            def __init__(self, a, b, c):
                pass

        self.assertEquals(4, arity(X1.__init__))

    def test_plain_sig(self):
        te = TypeError

        @sig(H() >> int >> int)
        def f1(x):
            return x + 4
        self.assertEquals(9, f1(5))
        with self.assertRaises(te): f1(1.0)
        with self.assertRaises(te): f1("foo")
        with self.assertRaises(te): f1(5, 4)
        with self.assertRaises(te): f1(5, "foo")
        with self.assertRaises(te): f1()

        @sig(H() >> int >> int >> float)
        def f2(x, y):
            return (x + y) / 2.0

        self.assertEquals(20.0, f2(20, 20))
        with self.assertRaises(te): f2(5, "foo")

        @sig(H() >> int >> int >> int >> float)
        def f3(x, y, z):
            return (x + y + z) / 3.0
        self.assertEquals(20.0, f3(20, 20, 20))
        with self.assertRaises(te): f3(5, "foo", 4)

        with self.assertRaises(te):
            @sig(int)
            def g(x):
                return x / 2

        with self.assertRaises(te):
            @sig(H() >> int >> int >> int)
            def g(x):
                return x / 2

        @sig2(H() >> float >> float)
        def g(x):
            return int(x / 2)
        with self.assertRaises(te): g(9.0)

        @sig(H() >> int >> int)
        def g(x):
            return x / 2.0
        with self.assertRaises(te): g(1)

    def test_curry_sig(self):
        te = TypeError

        @sig2(H() >> int >> int)
        def f1(x):
            return x + 4
        self.assertEquals(9, f1(5))
        with self.assertRaises(te): f1(1.0)
        with self.assertRaises(te): f1("foo")
        with self.assertRaises(te): f1(5, 4)
        with self.assertRaises(te): f1(5, "foo")

        @sig2(H() >> int >> int >> float)
        def f2(x, y):
            return (x + y) / 2.0
        self.assertEquals(15.0, f2(10, 20))
        self.assertEquals(15.0, f2(10)(20))

        @sig2(H() >> int >> int >> int >> float)
        def f3(x, y, z):
            return (x + y + z) / 3.0
        self.assertEquals(20.0, f3(20, 20, 20))
        with self.assertRaises(te): f3(5, "foo", 4)

        with self.assertRaises(te):
            @sig2(int)
            def g(x):
                return x / 2

        @sig2(H() >> float >> float)
        def g(x):
            return int(x / 2)
        with self.assertRaises(te): g(9.0)
        with self.assertRaises(te): g(9.0, 10.0)

        @sig2(H() >> int >> int)
        def g(x):
            return x / 2.0
        with self.assertRaises(te): g(1)


class TestADTInternals(unittest.TestCase):

    def setUp(self):
        # dummy type constructor and data constructors
        self.Type_Const = make_type_const("Type_Const", [])
        self.M1 = make_data_const("M1", [int], self.Type_Const)
        self.M2 = make_data_const("M2", [int, str], self.Type_Const)
        self.M3 = make_data_const("M3", [int, int, int], self.Type_Const)

    def test_adt(self):
        self.assertTrue(isinstance(self.M1(1), self.Type_Const))
        self.assertTrue(isinstance(self.M2(1, "abc"), self.Type_Const))
        self.assertTrue(isinstance(self.M3(1, 2, 3), self.Type_Const))

    def test_derive_eq_data(self):
        te = TypeError
        with self.assertRaises(te): self.M1(1) == self.M1(1)
        with self.assertRaises(te): self.M1(1) != self.M1(1)

        self.Type_Const = derive_eq(self.Type_Const)

        self.assertTrue(self.M1(1) == self.M1(1))
        self.assertTrue(self.M2(1, "b") == self.M2(1, "b"))
        self.assertTrue(self.M3(1, 2, 3) == self.M3(1, 2, 3))

        self.assertFalse(self.M1(1) != self.M1(1))
        self.assertFalse(self.M2(1, "b") != self.M2(1, "b"))
        self.assertFalse(self.M3(1, 2, 3) != self.M3(1, 2, 3))
        self.assertFalse(self.M1(1) == self.M1(2))
        self.assertFalse(self.M2(1, "b") == self.M2(4, "b"))
        self.assertFalse(self.M2(1, "b") == self.M2(1, "a"))
        self.assertFalse(self.M3(1, 2, 3) == self.M3(1, 9, 3))

    def test_derive_show_data(self):
        self.assertNotEquals("M1(1)", repr(self.M1(1)))

        self.Type_Const = derive_show(self.Type_Const)

        self.assertEquals("M1(1)", repr(self.M1(1)))

    def test_derive_read_data(self):
        pass

    def test_derive_ord_data(self):
        te = TypeError
        with self.assertRaises(te): self.M1(1) > self.M1(1)
        with self.assertRaises(te): self.M1(1) >= self.M1(1)
        with self.assertRaises(te): self.M1(1) < self.M1(1)
        with self.assertRaises(te): self.M1(1) <= self.M1(1)

        self.Type_Const = derive_ord(self.Type_Const)


class TestADT(unittest.TestCase):

    def test_data(self):
        se = SyntaxError
        self.assertEquals(("a",), (data . Maybe("a")).type_args)
        self.assertEquals(("a", "b"), (data . Maybe("a", "b")).type_args)
        self.assertEquals((), (data . Maybe).type_args)

    def test_d(self):
        pass

    def test_deriving(self):
        te = TypeError
        with self.assertRaises(te): deriving(Num)
        with self.assertRaises(te): deriving(Ord, Num)

    def test_holistic(self):
        pass


class TestEnum(unittest.TestCase):

    def test_str(self):
        self.assertEquals("b", succ("a"))
        self.assertEquals("a", pred("b"))

    def test_int(self):
        self.assertEquals(2, succ(1))
        self.assertEquals(1, pred(2))
        self.assertEquals(4, succ(succ(succ(1))))
        self.assertEquals(-1, pred(pred(pred(2))))


class TestSyntax(unittest.TestCase):

    def test_syntax(self):
        se = SyntaxError
        s = Syntax("err")

        with self.assertRaises(se): len(s)
        with self.assertRaises(se): s[0]
        with self.assertRaises(se): s[1]
        with self.assertRaises(se): del s["foo"]
        with self.assertRaises(se): iter(s)
        with self.assertRaises(se): reversed(s)
        with self.assertRaises(se): 1 in s
        with self.assertRaises(se): 1 not in s
        with self.assertRaises(se): s("f")
        with self.assertRaises(se):
            with s as b: pass
        with self.assertRaises(se): s > 0
        with self.assertRaises(se): s < 0
        with self.assertRaises(se): s >= 0
        with self.assertRaises(se): s <= 0
        with self.assertRaises(se): s == 0
        with self.assertRaises(se): s != 0
        with self.assertRaises(se): abs(s)
        with self.assertRaises(se): ~s
        with self.assertRaises(se): +s
        with self.assertRaises(se): -s

        with self.assertRaises(se): s + 1
        with self.assertRaises(se): s - 1
        with self.assertRaises(se): s * 1
        with self.assertRaises(se): s ** 1
        with self.assertRaises(se): s / 1
        with self.assertRaises(se): s % 1
        with self.assertRaises(se): divmod(s, 1)
        with self.assertRaises(se): s << 1
        with self.assertRaises(se): s >> 1
        with self.assertRaises(se): s & 1
        with self.assertRaises(se): s | 1
        with self.assertRaises(se): s ^ 1

        with self.assertRaises(se): 1 + s
        with self.assertRaises(se): 1 - s
        with self.assertRaises(se): 1 * s
        with self.assertRaises(se): 1 ** s
        with self.assertRaises(se): 1 / s
        with self.assertRaises(se): 1 % s
        with self.assertRaises(se): 1 << s
        with self.assertRaises(se): 1 >> s
        with self.assertRaises(se): 1 & s
        with self.assertRaises(se): 1 | s
        with self.assertRaises(se): 1 ^ s

        with self.assertRaises(se): s += 1
        with self.assertRaises(se): s -= 1
        with self.assertRaises(se): s *= 1
        with self.assertRaises(se): s **= 1
        with self.assertRaises(se): s /= 1
        with self.assertRaises(se): s %= 1
        with self.assertRaises(se): s <<= 1
        with self.assertRaises(se): s >>= 1
        with self.assertRaises(se): s &= 1
        with self.assertRaises(se): s |= 1
        with self.assertRaises(se): s ^= 1

    def test_section(self):
        # add more

        # basic sections
        self.assertEquals(4, (__ + 1)(3))
        self.assertEquals(4, (1 + __)(3))
        self.assertEquals(3, (__ - 5)(8))
        self.assertEquals(3, (8 - __)(5))
        self.assertEquals(8, (__ * 2)(4))
        self.assertEquals(8, (2 * __)(4))
        self.assertEquals(1, (__ % 4)(5))
        self.assertEquals(1, (5 % __)(4))

        self.assertTrue((__ < 4)(3))
        self.assertTrue((5 < __)(9))
        self.assertTrue((__ > 4)(5))
        self.assertTrue((5 > __)(4))
        self.assertTrue((__ == 4)(4))
        self.assertTrue((5 == __)(5))
        self.assertTrue((__ != 4)(3))
        self.assertTrue((5 != __)(8))
        self.assertTrue((__ >= 4)(5))
        self.assertTrue((5 >= __)(5))
        self.assertTrue((__ <= 4)(4))
        self.assertTrue((5 <= __)(8))
        self.assertFalse((__ < 4)(4))
        self.assertFalse((5 < __)(2))
        self.assertFalse((__ > 4)(3))
        self.assertFalse((5 > __)(5))
        self.assertFalse((__ == 4)(9))
        self.assertFalse((5 == __)(8))
        self.assertFalse((__ != 4)(4))
        self.assertFalse((5 != __)(5))
        self.assertFalse((__ >= 4)(1))
        self.assertFalse((5 >= __)(6))
        self.assertFalse((__ <= 4)(6))
        self.assertFalse((5 <= __)(4))

        # double sections
        self.assertEquals(3, (__+__)(1, 2))
        self.assertEquals(1, (__-__)(2, 1))
        self.assertEquals(4, (__*__)(1, 4))
        self.assertEquals(3, (__/__)(12, 4))

        # sections composed with `fmap`
        self.assertEquals(3, ((__+1) * (__+1) * (1+__))(0))
        self.assertEquals(3, (__+1) * (__+1) * (1+__) % 0)
        self.assertEquals(4, (__ + 1) * (__ * 3) % 1)

    def test_guard(self):
        # syntax checks
        se = SyntaxError
        me = NoGuardMatchException
        with self.assertRaises(se): c(lambda x: x == 10) + c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) - c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) * c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) / c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) % c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) ** c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) << c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) & c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x == 10) ^ c(lambda _: 1)

        with self.assertRaises(se): c(lambda x: x == 10) >> c(lambda _: 1)
        with self.assertRaises(se): c(lambda x: x > 1) | c(lambda x: x < 1)
        with self.assertRaises(se): otherwise() >> c(lambda _: 1)
        with self.assertRaises(se): otherwise() | c(lambda x: x < 1)
        with self.assertRaises(se): otherwise >> c(lambda _: 1)
        with self.assertRaises(se): otherwise | c(lambda x: x < 1)

        with self.assertRaises(se): c(lambda x: x == 10) >> "1" >> "2"
        with self.assertRaises(se): "1" >> c(lambda x: x == 10)
        with self.assertRaises(se): guard(1) | c(lambda x: x > 1)
        with self.assertRaises(se): guard(1) | (lambda x: x > 1)
        with self.assertRaises(se): ~guard(1) | (lambda x: x > 1)
        with self.assertRaises(se): ~guard(1)
        with self.assertRaises(se): otherwise() >> "1" >> "2"
        with self.assertRaises(se): "1" >> otherwise()
        with self.assertRaises(se): guard(1) | otherwise()
        with self.assertRaises(se): guard(1) | otherwise

        # matching checks
        self.assertTrue(~(guard(1)
            | c(lambda x: x == 1) >> True
            | otherwise()         >> False))
        self.assertFalse(~(guard(2)
            | c(lambda y: y == 1) >> True
            | otherwise()         >> False))
        self.assertFalse(~(guard(2)
            | otherwise() >> False))
        self.assertFalse(~(guard(2)
            | otherwise()         >> False
            | c(lambda x: x == 2) >> True))
        self.assertEquals("foo", ~(guard(1)
            | c(lambda x: x > 1)  >> "bar"
            | c(lambda x: x < 1)  >> "baz"
            | c(lambda x: x == 1) >> "foo"
            | otherwise()         >> "Err"))

        with self.assertRaises(me): ~(guard(1) | c(lambda x: x == 2) >> 1)

    def test_caseof(self):
        self.assertTrue(~(caseof(1) / 1 % True))


class TestHOF(unittest.TestCase):

    def test_F(self):
        te = TypeError

        # regular version
        def sum3(x, y, z):
            return x * y * z

        @F # version wrapped using decorator
        def dsum3(x, y, z):
            return x * y * z

        self.assertEqual(sum3(1, 2, 3), F(sum3, 1, 2)(3))
        self.assertEqual(sum3(1, 2, 3), F(sum3, 1)(2, 3))
        self.assertEqual(sum3(1, 2, 3), F(sum3, 1)(2)(3))
        self.assertEqual(sum3(1, 2, 3), F(sum3, 1, 2, 3))
        self.assertEqual(sum3(1, 2, 3), F(sum3)(1, 2, 3))
        self.assertEqual(sum3(1, 2, 3), F(sum3)(1, 2)(3))
        self.assertEqual(sum3(1, 2, 3), F(sum3)(1)(2, 3))
        self.assertEqual(sum3(1, 2, 3), F(sum3)(1)(2)(3))

        self.assertEqual(sum3(1, 2, 3), dsum3(1, 2, 3))
        self.assertEqual(sum3(1, 2, 3), dsum3(1, 2)(3))
        self.assertEqual(sum3(1, 2, 3), dsum3(1)(2, 3))
        self.assertEqual(sum3(1, 2, 3), dsum3(1)(2)(3))

        self.assertEqual(sum3(1, 2, 3), F(dsum3, 1, 2)(3))
        self.assertEqual(sum3(1, 2, 3), F(dsum3, 1)(2, 3))
        self.assertEqual(sum3(1, 2, 3), F(dsum3, 1)(2)(3))
        self.assertEqual(sum3(1, 2, 3), F(dsum3, 1, 2, 3))
        self.assertEqual(sum3(1, 2, 3), F(dsum3)(1, 2, 3))
        self.assertEqual(sum3(1, 2, 3), F(dsum3)(1, 2)(3))
        self.assertEqual(sum3(1, 2, 3), F(dsum3)(1)(2, 3))
        self.assertEqual(sum3(1, 2, 3), F(dsum3)(1)(2)(3))

        self.assertEquals(5, F(lambda x: lambda y: y + x)(1)(4))
        self.assertEquals(5, F(lambda x: lambda y: y + x)(1, 4))
        self.assertEquals(5, F(lambda x: lambda y: y + x, 1, 4))
        self.assertEquals(5, F(lambda x: lambda y: y + x, 1)(4))

        self.assertEquals(5, F(lambda x: F(lambda y: y + x))(1)(4))
        self.assertEquals(5, F(lambda x: F(lambda y: y + x))(1, 4))
        self.assertEquals(5, F(lambda x: F(lambda y: y + x), 1, 4))
        self.assertEquals(5, F(lambda x: F(lambda y: y + x), 1)(4))

        self.assertEquals(7, F(lambda x: lambda y,z: y + x + z, 1, 4, 2))
        self.assertEquals(7, F(lambda x: lambda y,z: y + x + z, 1, 4)(2))
        self.assertEquals(7, F(lambda x: lambda y,z: y + x + z, 1)(4, 2))
        self.assertEquals(7, F(lambda x: lambda y,z: y + x + z, 1)(4)(2))
        self.assertEquals(7, F(lambda x: lambda y,z: y + x + z)(1, 4, 2))
        self.assertEquals(7, F(lambda x: lambda y,z: y + x + z)(1, 4)(2))
        self.assertEquals(7, F(lambda x: lambda y,z: y + x + z)(1)(4, 2))
        self.assertEquals(7, F(lambda x: lambda y,z: y + x + z)(1)(4)(2))

        self.assertEquals(7, F(lambda x: F(lambda y,z: y + x + z), 1, 4, 2))
        self.assertEquals(7, F(lambda x: F(lambda y,z: y + x + z), 1, 4)(2))
        self.assertEquals(7, F(lambda x: F(lambda y,z: y + x + z), 1)(4, 2))
        self.assertEquals(7, F(lambda x: F(lambda y,z: y + x + z), 1)(4)(2))
        self.assertEquals(7, F(lambda x: F(lambda y,z: y + x + z))(1, 4, 2))
        self.assertEquals(7, F(lambda x: F(lambda y,z: y + x + z))(1, 4)(2))
        self.assertEquals(7, F(lambda x: F(lambda y,z: y + x + z))(1)(4, 2))
        self.assertEquals(7, F(lambda x: F(lambda y,z: y + x + z))(1)(4)(2))

        self.assertEquals(7, F(lambda x,y: lambda z: y + x + z)(1, 4, 2))
        self.assertEquals(7, F(lambda x,y: lambda z: y + x + z)(1, 4)(2))
        self.assertEquals(7, F(lambda x,y: lambda z: y + x + z)(1)(4, 2))
        self.assertEquals(7, F(lambda x,y: lambda z: y + x + z)(1)(4)(2))
        self.assertEquals(7, F(lambda x,y: lambda z: y + x + z, 1, 4, 2))
        self.assertEquals(7, F(lambda x,y: lambda z: y + x + z, 1, 4)(2))
        self.assertEquals(7, F(lambda x,y: lambda z: y + x + z, 1)(4, 2))
        self.assertEquals(7, F(lambda x,y: lambda z: y + x + z, 1)(4)(2))

        self.assertTrue(isinstance(F(lambda x, y: x + y, 1), Func))
        self.assertTrue(isinstance(F(lambda x, y: x + y)(1), Func))
        self.assertTrue(isinstance(F(lambda x: lambda y: x + y, 1), Func))
        self.assertTrue(isinstance(F(lambda x: lambda y: x + y)(1), Func))

        self.assertEquals(4, F(lambda: 4))
        self.assertEquals(4, F(lambda: lambda: 4))
        self.assertEquals(4, F(lambda: lambda: lambda: lambda: lambda: 4))
        self.assertEquals(4, F(F(lambda: lambda: lambda: 4)))
        self.assertEquals(4, F(4))
        self.assertEquals(4, F(F(F(4))))

        # too many arguments
        with self.assertRaises(te): F(lambda: 1)(1, 2)
        with self.assertRaises(te): F(lambda x: x)(1, 2)
        with self.assertRaises(te): F(lambda x, y: x)(1, 2, 3)

    def test_F_functor(self):
        te = TypeError
        f = lambda x: (x + 100) % 75
        g = lambda x: x * 21
        h = lambda x: (x - 31) / 3

        self.assertEquals(f(56), (hid * f)(56))
        self.assertEquals(f(g(h(56))), (hid * f * g * h)(56))
        self.assertEquals(f(g(h(56))), ((hid * f) * g * h)(56))
        self.assertEquals(f(g(h(56))), ((hid * f * g) * h)(56))

        f2, g2, h2 = map(F, (f, g, h))
        self.assertEquals(f(56), (hid * f2)(56))
        self.assertEquals(f2(56), (hid * f2)(56))
        self.assertEquals(f2(g2(h2(56))), (hid * f * g * h2)(56))
        self.assertEquals(f2(g2(h2(56))), (hid * f * g2 * h)(56))
        self.assertEquals(f2(g2(h2(56))), (hid * f * g2 * h2)(56))
        self.assertEquals(f2(g2(h2(56))), (hid * f2 * g * h)(56))
        self.assertEquals(f2(g2(h2(56))), (hid * f2 * g * h2)(56))
        self.assertEquals(f2(g2(h2(56))), (hid * f2 * g2 * h)(56))
        self.assertEquals(f2(g2(h2(56))), (hid * f2 * g2 * h2)(56))

        with self.assertRaises(te):
            self.assertEquals(f2(g2(h2(56))), (f * g * h2)(56))
        self.assertEquals(f2(g2(h2(56))), (f * g2 * h)(56))
        self.assertEquals(f2(g2(h2(56))), (f * g2 * h2)(56))
        self.assertEquals(f2(g2(h2(56))), (f2 * g * h)(56))
        self.assertEquals(f2(g2(h2(56))), (f2 * g * h2)(56))
        self.assertEquals(f2(g2(h2(56))), (f2 * g2 * h)(56))
        self.assertEquals(f2(g2(h2(56))), (f2 * g2 * h2)(56))

        f3, g3, h3 = map(F, (f2, g2, h2))
        self.assertEquals(f(56), (hid * f3)(56))
        self.assertEquals(f3(56), (hid * f3)(56))
        self.assertEquals(f3(g3(h3(56))), (hid * f * g * h3)(56))
        self.assertEquals(f3(g3(h3(56))), (hid * f * g3 * h)(56))
        self.assertEquals(f3(g3(h3(56))), (hid * f * g3 * h3)(56))
        self.assertEquals(f3(g3(h3(56))), (hid * f3 * g * h)(56))
        self.assertEquals(f3(g3(h3(56))), (hid * f3 * g * h3)(56))
        self.assertEquals(f3(g3(h3(56))), (hid * f3 * g3 * h)(56))
        self.assertEquals(f3(g3(h3(56))), (hid * f3 * g3 * h3)(56))

        with self.assertRaises(te):
            self.assertEquals(f3(g3(h3(56))), (f * g * h3)(56))

        self.assertEquals(f3(g3(h3(56))), (f * g3 * h)(56))
        self.assertEquals(f3(g3(h3(56))), (f * g3 * h3)(56))
        self.assertEquals(f3(g3(h3(56))), (f3 * g * h)(56))
        self.assertEquals(f3(g3(h3(56))), (f3 * g * h3)(56))
        self.assertEquals(f3(g3(h3(56))), (f3 * g3 * h)(56))
        self.assertEquals(f3(g3(h3(56))), (f3 * g3 * h3)(56))

        self.assertEquals(f3(g3(h3(56))), (f3 * g * h2)(56))
        self.assertEquals(f3(g3(h3(56))), (f3 * g2 * h)(56))
        self.assertEquals(f3(g3(h3(56))), (f3 * g2 * h3)(56))

    def test_F_apply(self):
        f = lambda x: (x + 100) % 75
        g = lambda x: x * 21
        h = lambda x: (x - 31) / 3

        self.assertEquals(f(56), hid * f % 56)
        self.assertEquals(f(g(h(56))), hid * f * g * h % 56)
        self.assertEquals(f(g(h(56))), (hid * f) * g * h % 56)
        self.assertEquals(f(g(h(56))), (hid * f * g) * h % 56)

        f2, g2, h2 = map(F, (f, g, h))
        self.assertEquals(f(56), hid * f2 % 56)
        self.assertEquals(f2(56), hid * f2 % 56)
        self.assertEquals(f2(g2(h2(56))), hid * f2 * g * h % 56)
        self.assertEquals(f2(g2(h2(56))), hid * (f2 * g) * h % 56)
        self.assertEquals(f2(g2(h2(56))), hid * f * g * h2 % 56)
        self.assertEquals(f2(g2(h2(56))), hid * f2 * g * h2 % 56)
        self.assertEquals(f2(g2(h2(56))), hid * (f2 * g) * h2 % 56)

        f3, g3, h3 = map(F, (f2, g2, h2))
        self.assertEquals(f(56), hid * f3 % 56)
        self.assertEquals(f3(56), hid * f3 % 56)
        self.assertEquals(f3(g3(h3(56))), hid * f3 * g * h % 56)
        self.assertEquals(f3(g3(h3(56))), hid * f * g * h3 % 56)
        self.assertEquals(f3(g3(h3(56))), hid * f3 * g * h3 % 56)
        self.assertEquals(f3(g3(h3(56))), hid * f3 * g2 * h3 % 56)

    def test_id(self):
        self.assertEquals(3, hid(3))
        self.assertEquals(3, hid(hid(hid(3))))
        self.assertEquals(3, hid.fmap(hid).fmap(hid)(3))
        self.assertEquals(3, (hid * hid * hid)(3))
        self.assertEquals(3, hid * hid * hid % 3)
        self.assertEquals(3, hid * hid * hid % hid(3))

    def test_const(self):
        self.assertEquals(1, const(1, 2))
        self.assertEquals(1, const(1)(2))
        self.assertEquals("foo", const("foo", 2))
        self.assertEquals(1, (const(1) * const(2) * const(3))(4))
        self.assertEquals(1, const(1) * const(2) * const(3) % 4)

        self.assertEquals(1, const(hid, 2)(1))
        self.assertEquals(1, const(hid)(2)(1))
        self.assertEquals(1, const(hid)(2) % 1)

    def test_flip(self):
        test_f1 = lambda x, y: x - y
        self.assertEquals(test_f1(9, 1), flip(flip(test_f1))(9, 1))
        self.assertEquals(test_f1(9, 1), flip(test_f1)(1, 9))
        self.assertEquals(test_f1(9, 1), flip(test_f1, 1)(9))
        self.assertEquals(test_f1(9, 1), flip(test_f1, 1, 9))
        self.assertEquals(test_f1(9, 1), flip(test_f1)(1)(9))

        self.assertEquals(test_f1(9, 1), flip(flip(F(test_f1)))(9, 1))
        self.assertEquals(test_f1(9, 1), flip(F(test_f1))(1, 9))
        self.assertEquals(test_f1(9, 1), flip(F(test_f1), 1)(9))
        self.assertEquals(test_f1(9, 1), flip(F(test_f1), 1, 9))
        self.assertEquals(test_f1(9, 1), flip(F(test_f1))(1)(9))

        test_f2 = lambda x, y, z: (x - y) / z
        self.assertEquals(test_f2(9, 1, 2), flip(F(test_f2))(1, 9)(2))
        self.assertEquals(test_f2(9, 1, 2), flip(F(test_f2), 1)(9)(2))
        self.assertEquals(test_f2(9, 1, 2), flip(F(test_f2), 1, 9)(2))
        self.assertEquals(test_f2(9, 1, 2), flip(F(test_f2))(1)(9)(2))
        self.assertEquals(test_f2(9, 1, 2), flip(F(test_f2))(1, 9, 2))
        self.assertEquals(test_f2(9, 1, 2), flip(F(test_f2), 1)(9, 2))
        self.assertEquals(test_f2(9, 1, 2), flip(F(test_f2), 1, 9, 2))
        self.assertEquals(test_f2(9, 1, 2), flip(F(test_f2))(1)(9, 2))

        self.assertEquals(test_f2(9, 1, 2), flip(test_f2)(1, 9, 2))
        self.assertEquals(test_f2(9, 1, 2), flip(test_f2)(1, 9)(2))
        self.assertEquals(test_f2(9, 1, 2), flip(test_f2)(1)(9, 2))
        self.assertEquals(test_f2(9, 1, 2), flip(test_f2)(1)(9)(2))
        self.assertEquals(test_f2(9, 1, 2), flip(test_f2, 1, 9, 2))
        self.assertEquals(test_f2(9, 1, 2), flip(test_f2, 1, 9)(2))
        self.assertEquals(test_f2(9, 1, 2), flip(test_f2, 1)(9, 2))
        self.assertEquals(test_f2(9, 1, 2), flip(test_f2, 1)(9)(2))


class TestMaybe(unittest.TestCase):

    def test_instances(self):
        self.assertTrue(in_typeclass(Maybe, Typeable))
        self.assertTrue(in_typeclass(Maybe, Show))
        self.assertTrue(in_typeclass(Maybe, Eq))
        self.assertTrue(in_typeclass(Maybe, Functor))
        self.assertTrue(in_typeclass(Maybe, Applicative))
        self.assertTrue(in_typeclass(Maybe, Monad))

        self.assertFalse(in_typeclass(Maybe, Typeclass))
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
        self.assertNotEqual(Just(3), Nothing)
        self.assertNotEqual(Nothing, Just(0))
        self.assertNotEqual(Nothing, None)

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
        self.assertEqual(Just("1"), Just(1) >> (lambda x: Just(str(x))))
        self.assertEqual(Just(10), Just(1) >> (lambda x: Just(x * 10)))
        self.assertEqual(Just(10), Just(1) >> F(lambda x: Just(x * 10)))
        self.assertEqual(Just(1000), Just(1) >>
                (lambda x: Just(x * 10)) >>
                (lambda x: Just(x * 10)) >>
                (lambda x: Just(x * 10)))
        self.assertEqual(Nothing, Nothing >>
                F(lambda x: Just(x * 10)) >>
                F(lambda x: Just(x * 10)))
        self.assertEqual(Nothing, Just(1) >>
                F(lambda x: Nothing) >>
                F(lambda x: Just(x * 10)))


class TestList(unittest.TestCase):

    def test_instances(self):
        self.assertTrue(in_typeclass(List, Show))
        self.assertTrue(in_typeclass(List, Eq))
        self.assertTrue(in_typeclass(List, Functor))
        self.assertTrue(in_typeclass(List, Applicative))
        self.assertTrue(in_typeclass(List, Monad))
        self.assertTrue(in_typeclass(List, Traversable))
        self.assertTrue(in_typeclass(List, Ix))

    def test_ix(self):
        # add more corner cases

        ie = IndexError
        self.assertEqual(3, List(range(10))[3])
        self.assertEqual(3, List(range(4))[-1])
        self.assertEqual(3, List((i for i in range(10)))[3])
        self.assertEqual(3, List((i for i in range(4)))[-1])
        self.assertEqual(2, List([0, 1, 2, 3])[2])
        self.assertEqual(2, List([0, 1, 2, 3])[-2])
        self.assertEqual(1, List((0, 1, 2, 3))[1])
        self.assertEqual(1, List((0, 1, 2, 3))[-3])

        with self.assertRaises(ie): List((0, 1, 2))[3]
        with self.assertRaises(ie): List((0, 1, 2))[-4]
        with self.assertRaises(ie): List((i for i in range(3)))[3]
        with self.assertRaises(ie): List((i for i in range(3)))[-4]

    def test_eq(self):
        self.assertEquals(list(range(10)), list(List(range(10))))
        self.assertEquals(List(range(10)), List(range(10)))
        self.assertEquals(L[range(10)], List(range(10)))
        self.assertEquals(List(range(10)),
                          List((i for i in range(10))))

    def test_functor(self):
        test_f = lambda x: x ** 2 - 1
        test_g = F(lambda y: y / 4 + 9)

        # functor laws
        self.assertEquals(List(range(10)), List(range(10)) * hid)
        self.assertEquals(List(range(20)) * (test_f * test_g),
                          (List(range(20)) * test_g * test_f))

        # `fmap` == `map` for Lists
        self.assertEquals(map(test_f, list(List(range(9)))),
                          list(List(range(9)) * test_f))
        self.assertEquals(map(test_f, List(range(9))),
                          list(List(range(9)) * test_f))
        self.assertEquals(map(test_f, range(9)),
                          list(List(range(9)) * test_f))

    def test_list_comp(self):
        # numeric lists
        self.assertEquals(10, len(L[0, ...][:10]))
        self.assertEquals(L[0, ...][:10], range(10)[:10])
        self.assertEquals(L[-10, ...][:10], range(-10, 0)[:10])
        self.assertEquals(11, len(L[-5, ..., 5]))
        self.assertEquals(list(L[-5, ..., 5]), list(range(-5, 6)))
        self.assertEquals(list(L[-5, -4, ..., 5]), list(range(-5, 6)))
        self.assertEquals(list(L[-5, -3, ..., 5]), list(range(-5, 6, 2)))
        self.assertEquals(L[1, 3, 5, 7], L[1, 3, ...][:4])
        self.assertEquals(L[3, 5, 7], L[1, 3, ...][1:4])
        self.assertEquals(L[5, 7], L[1, 3, ...][2:4])
        self.assertEquals([], list(L[1, 3, ...][4:4]))
        self.assertEquals([], list(L[1, 3, ...][5:4]))
        self.assertEquals(L[1, 3, 5, 7], L[1, 3, ..., 7])
        self.assertEquals(L[1, 3, 5, 7], L[1, 3, ..., 8])
        self.assertEquals([], list(L[6, ..., 4]))
        self.assertEquals([], list(L[2, 3, ..., 1]))

        # character lists
        self.assertEquals(10, len(L["a", ...][:10]))
        self.assertEquals("abcdefghij", "".join(L["a", ...][:10]))
        self.assertEquals(11, len(L["a", ..., "k"]))

    def test_hmap(self):
        test_f = lambda x: (x + 100) / 2

        # `map` == `hmap` for Lists
        self.assertEquals(map(test_f, range(20)),
                          list(hmap(test_f, range(20))))
        self.assertEquals(map(test_f, range(20)),
                          map(test_f, range(20)))


    def test_hfilter(self):
        test_f = lambda x: x % 2 == 0
        self.assertEquals(filter(test_f, range(20)),
                          list(hfilter(test_f, range(20))))
        self.assertEquals(filter(test_f, range(20)),
                          filter(test_f, range(20)))

    def test_len(self):
        self.assertEquals(0, len(L[None]))
        self.assertEquals(3, len(L[1, 2, 3]))


if __name__ == '__main__':
    unittest.main()
