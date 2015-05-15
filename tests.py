import functools

import unittest

from hask import in_typeclass, arity, sig, H, sig2
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

# internals
from hask.lang.syntax import Syntax

from hask.lang.adt import make_data_const, make_type_const
from hask.lang.adt import derive_eq
from hask.lang.adt import derive_show
from hask.lang.adt import derive_read
from hask.lang.adt import derive_ord

from hask.lang.hindley_milner import Var
from hask.lang.hindley_milner import App
from hask.lang.hindley_milner import Lam
from hask.lang.hindley_milner import Let
from hask.lang.hindley_milner import TypeVariable
from hask.lang.hindley_milner import TypeOperator
from hask.lang.hindley_milner import Function
from hask.lang.hindley_milner import ListType
from hask.lang.hindley_milner import Tuple
from hask.lang.hindley_milner import analyze
from hask.lang.hindley_milner import unify

from hask.lang.type_system import parse_sig_item


class TestHindleyMilner(unittest.TestCase):

    def inference(self, expr):
        """Type inference succeeded using our toy environment"""
        self.assertIsNotNone(analyze(expr, self.env))
        return

    def not_inference(self, expr):
        """Type inference failed using our toy environment"""
        with self.assertRaises(TypeError):
            analyze(expr, self.env)
        return

    def unified(self, t1, t2):
        """Two types are able to be unified"""
        self.assertIsNone(unify(t1, t2))
        return

    def typecheck(self, expr, expr_type):
        """Typecheck succeeded using our toy environment"""
        self.assertIsNone(unify(analyze(expr, self.env), expr_type))
        return

    def not_typecheck(self, expr, expr_type):
        """Typecheck failed, but inference succeeded using our toy environment"""
        self.inference(expr)
        with self.assertRaises(TypeError):
            self.typecheck(expr, expr_type)
        return

    def setUp(self):
        """Create some basic types and polymorphic typevars, a toy environment,
           and some AST nodes
        """
        self.var1 = TypeVariable()
        self.var2 = TypeVariable()
        self.var3 = TypeVariable()
        self.var4 = TypeVariable()
        self.Pair = TypeOperator("*", (self.var1, self.var2))
        self.Bool = TypeOperator("bool", [])
        self.Integer = TypeOperator("int", [])
        self.NoneT = TypeOperator("None", [])

        # toy environment
        self.env = {"pair" : Function(self.var1, Function(self.var2, self.Pair)),
                    "True" : self.Bool,
                    "None" : self.NoneT,
                    "id"   : Function(self.var4, self.var4),
                    "cond" : Function(self.Bool, Function(self.var3,
                                Function(self.var3, self.var3))),
                    "zero" : Function(self.Integer, self.Bool),
                    "pred" : Function(self.Integer, self.Integer),
                    "times": Function(self.Integer,
                                Function(self.Integer, self.Integer)),
                    "4"    : self.Integer,
                    "1"    : self.Integer }

        # some expressions to play around with
        self.compose = Lam("f", Lam("g", Lam("arg",
                            App(Var("g"), App(Var("f"), Var("arg"))))))
        self.pair = App(App(Var("pair"),
                         App(Var("f"), Var("1"))),
                         App(Var("f"), Var("True")))
        return

    def test_type_inference(self):
        """Basic type inference in our toy environment"""

        # (* True) ==> TypeError
        self.not_inference(App(Var("times"), Var("True")))

        # (* True) ==> TypeError (undefined symbol a)
        self.not_inference(App(Var("times"), Var("a")))

        # monomorphism restriction
        # \x -> ((x 4), (x True)) ==> TypeError
        self.not_inference(
            Lam("x",
                App(
                    App(Var("pair"),
                        App(Var("x"), Var(4))),
                    App(Var("x"), Var("True")))))

        # \x -> ((f 4), (f True)) ==> TypeError (undefined symbol f)
        self.not_inference(
            App(
                App(Var("pair"), App(Var("f"), Var(4))),
                App(Var("f"), Var("True"))))

        # \f -> (f f) ==> TypeError (recursive unification)
        self.not_inference(Lam("f", App(Var("f"), Var("f"))))
        return

    def test_type_checking(self):
        """Basic type checking in our toy environment"""

        # 1 :: Integer
        self.typecheck(Var("1"), self.Integer)

        # 1 :: Bool ==> TypeError
        self.not_typecheck(Var("1"), self.Bool)

        # (\x -> x) :: (a -> a)
        v = TypeVariable()
        self.typecheck(
                Lam("n", Var("n")),
                Function(v, v))

        # type(id) == type(\x -> x)
        self.typecheck(
                Lam("n", Var("n")),
                self.env["id"])

        # (\x -> x) :: (a -> b)
        self.typecheck(
                Lam("n", Var("n")),
                Function(TypeVariable(), TypeVariable()))

        # (id 1) :: Integer
        self.typecheck(App(Var("id"), Var("1")), self.Integer)

        # (id 1) :: Bool ==> TypeError
        self.not_typecheck(App(Var("id"), Var("1")), self.Bool)

        # pred :: (Integer -> Integer)
        self.typecheck(Var("pred"), Function(self.Integer, self.Integer))

        # (pred 4) :: Integer
        self.typecheck(
            App(Var("pred"), Var("1")),
            self.Integer)

        # (*) :: (Integer -> Integer -> Integer)
        self.typecheck(
            Var("times"),
            Function(self.Integer, Function(self.Integer, self.Integer)))

        # (* 4) :: (Integer -> Integer)
        self.typecheck(
            App(Var("times"), Var("4")),
            Function(self.Integer, self.Integer))

        # (* 4) :: (Bool -> Integer) ==> TypeError
        self.not_typecheck(
            App(Var("times"), Var("4")),
            Function(self.Bool, self.Integer))

        # (* 4) :: (Integer -> a) ==> TypeError
        self.not_typecheck(
            App(Var("times"), Var("4")),
            Function(self.Integer, TypeVariable))

        # ((* 1) 4) :: Integer
        self.typecheck(
            App(App(Var("times"), Var("1")), Var("4")),
            self.Integer)

        # ((* 1) 4) :: Bool ==> TypeError
        self.not_typecheck(
            App(App(Var("times"), Var("1")), Var("4")),
            self.Bool)

        # let g = (\f -> 5) in (g g) :: Integer
        self.typecheck(
            Let("g",
                Lam("f", Var("4")),
                App(Var("g"), Var("g"))),
            self.Integer)

        # (.) :: (a -> b) -> (b -> c) -> (a -> c)
        a, b, c = TypeVariable(), TypeVariable(), TypeVariable()
        self.typecheck(
                self.compose,
                Function(Function(a, b),
                         Function(Function(b, c), Function(a, c))))

        # composing `id` with `id` == `id`
        # ((. id) id) :: (a -> a)
        d = TypeVariable()
        self.typecheck(
            App(App(self.compose, Var("id")), Var("id")),
            Function(d, d))

        # basic closure
        #((\x -> (\y -> ((* x) y))) 1) :: (Integer -> Integer)
        self.typecheck(
                App(
                    Lam("x", Lam("y",
                        App(App(Var("times"), Var("x")), Var("y")))),
                    Var("1")),
                Function(self.Integer, self.Integer))

        # lambdas have lexical scope
        # (((\x -> (\x -> x)) True) None) :: NoneT
        self.typecheck(
                App(App(
                    Lam("x", Lam("x", Var("x"))),
                    Var("True")), Var("None")),
                self.NoneT)

        # basic let expression
        # let a = times in ((a 1) 4) :: Integer
        self.typecheck(
                Let("a", Var("times"), App(App(Var("a"), Var("1")), Var("4"))),
                self.Integer)

        # let has lexical scope
        # let a = 1 in (let a = None in a) :: NoneT
        self.typecheck(
                Let("a", Var("1"), Let("a", Var("None"), Var("a"))),
                self.NoneT)

        # let polymorphism
        # let f = (\x -> x) in ((f 4), (f True)) :: (Integer, Bool)
        self.typecheck(
            Let("f", Lam("x", Var("x")), self.pair),
            TypeOperator("*", [self.Integer, self.Bool]))

        # recursive let
        # (factorial 4) :: Integer
        self.typecheck(
            Let("factorial", # letrec factorial =
                Lam("n",    # fn n =>
                    App(
                        App(   # cond (zero n) 1
                            App(Var("cond"),     # cond (zero n)
                                App(Var("zero"), Var("n"))),
                            Var("1")),
                        App(    # times n
                            App(Var("times"), Var("n")),
                            App(Var("factorial"),
                                App(Var("pred"), Var("n")))
                        )
                    )
                ),      # in
                App(Var("factorial"), Var("4"))),
            self.Integer)

        return

    def test_extentions(self):
        self.unified(
                TypeOperator(list, [TypeOperator(int, [])]),
                ListType(TypeOperator(int, [])))
        self.unified(
                ListType(TypeOperator(int, [])),
                TypeOperator(list, [TypeOperator(int, [])]))

        #self.assertEqual("[int]", str(ListType(TypeOperator(int, []))))
        return

    def test_parse_sig_item(self):
        class __test__(object):
            pass

        # builtin/non-ADT types
        self.unified(parse_sig_item(int), TypeOperator(int, []))
        self.unified(parse_sig_item(float), TypeOperator(float, []))
        self.unified(parse_sig_item(type(None)), TypeOperator(type(None), []))
        self.unified(parse_sig_item(__test__), TypeOperator(__test__, []))

        # list
        self.unified(parse_sig_item([int]), ListType(TypeOperator(int, [])))
        self.unified(parse_sig_item([int]),
                TypeOperator(list, [TypeOperator(int, [])]))

        # tuple
        return


class TestTypeSystem(unittest.TestCase):

    def test_arity(self):
        self.assertEqual(0, arity(1))
        self.assertEqual(0, arity("foo"))
        self.assertEqual(0, arity([1, 2, 3]))
        self.assertEqual(0, arity((1, 1)))
        self.assertEqual(0, arity((lambda x: x + 1, 1)))
        self.assertEqual(0, arity(lambda: "foo"))
        self.assertEqual(1, arity(lambda **kwargs: kwargs))
        self.assertEqual(1, arity(lambda *args: args))
        self.assertEqual(1, arity(lambda x: 0))
        self.assertEqual(1, arity(lambda x, *args: 0))
        self.assertEqual(1, arity(lambda x, *args, **kw: 0))
        self.assertEqual(1, arity(lambda x: x + 1))
        self.assertEqual(2, arity(lambda x, y: x + y))
        self.assertEqual(2, arity(lambda x, y, *args: x + y + z))
        self.assertEqual(2, arity(lambda x, y, *args, **kw: x + y + z))
        self.assertEqual(3, arity(lambda x, y, z: x + y + z))
        self.assertEqual(3, arity(lambda x, y, z, *args: x + y + z))
        self.assertEqual(3, arity(lambda x, y, z, *args, **kw: x + y + z))

        self.assertEqual(1, arity(lambda x: lambda y: x))
        self.assertEqual(1, arity(lambda x: lambda y: lambda z: x))
        self.assertEqual(2, arity(lambda x, z: lambda y: x))
        self.assertEqual(1, arity(functools.partial(lambda x,y: x+y, 2)))
        self.assertEqual(2, arity(functools.partial(lambda x,y: x+y)))
        self.assertEqual(2, arity(functools.partial(lambda x, y, z: x+y, 2)))

        class X0(object):
            def __init__(self):
                pass

        self.assertEqual(1, arity(X0.__init__))

        class X1(object):
            def __init__(self, a, b, c):
                pass

        self.assertEqual(4, arity(X1.__init__))

    def test_plain_sig(self):
        te = TypeError

        @sig(H() >> int >> int)
        def f1(x):
            return x + 4
        self.assertEqual(9, f1(5))
        with self.assertRaises(te): f1(1.0)
        with self.assertRaises(te): f1("foo")
        with self.assertRaises(te): f1(5, 4)
        with self.assertRaises(te): f1(5, "foo")
        with self.assertRaises(te): f1()

        @sig(H() >> int >> int >> float)
        def f2(x, y):
            return (x + y) / 2.0

        self.assertEqual(20.0, f2(20, 20))
        with self.assertRaises(te): f2(5, "foo")

        @sig(H() >> int >> int >> int >> float)
        def f3(x, y, z):
            return (x + y + z) / 3.0
        self.assertEqual(20.0, f3(20, 20, 20))
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


class TestADTInternals(unittest.TestCase):

    def setUp(self):
        """Dummy type constructor and data constructors"""
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

        self.assertEqual("M1(1)", repr(self.M1(1)))

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
        self.assertEqual(("a",), (data . Maybe("a")).type_args)
        self.assertEqual(("a", "b"), (data . Maybe("a", "b")).type_args)
        self.assertEqual((), (data . Maybe).type_args)

    def test_d(self):
        pass

    def test_deriving(self):
        te = TypeError
        with self.assertRaises(te): deriving(Num)
        with self.assertRaises(te): deriving(Ord, Num)

    def test_holistic(self):
        pass


class TestEnum(unittest.TestCase):

    def test_enum_str(self):
        self.assertEqual("b", succ("a"))
        self.assertEqual("a", pred("b"))

    def test_enum_int(self):
        self.assertEqual(2, succ(1))
        self.assertEqual(1, pred(2))
        self.assertEqual(4, succ(succ(succ(1))))
        self.assertEqual(-1, pred(pred(pred(2))))


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
        """Operator sections (e.g. `(1+__)` )"""
        # add more

        # basic sections
        self.assertEqual(4, (__ + 1)(3))
        self.assertEqual(4, (1 + __)(3))
        self.assertEqual(3, (__ - 5)(8))
        self.assertEqual(3, (8 - __)(5))
        self.assertEqual(8, (__ * 2)(4))
        self.assertEqual(8, (2 * __)(4))
        self.assertEqual(1, (__ % 4)(5))
        self.assertEqual(1, (5 % __)(4))

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
        self.assertEqual(3, (__+__)(1, 2))
        self.assertEqual(1, (__-__)(2, 1))
        self.assertEqual(4, (__*__)(1, 4))
        self.assertEqual(3, (__/__)(12, 4))

        # sections composed with `fmap`
        self.assertEqual(3, ((__+1) * (__+1) * (1+__))(0))
        self.assertEqual(3, (__+1) * (__+1) * (1+__) % 0)
        self.assertEqual(4, (__ + 1) * (__ * 3) % 1)

    def test_guard(self):
        se = SyntaxError
        me = NoGuardMatchException

        self.assertTrue(~(guard(1)
            | c(lambda x: x == 1) >> True
            | otherwise           >> False))
        self.assertFalse(~(guard(2)
            | c(lambda y: y == 1) >> True
            | otherwise           >> False))
        self.assertFalse(~(guard(2)
            | otherwise >> False))
        self.assertFalse(~(guard(2)
            | otherwise           >> False
            | c(lambda x: x == 2) >> True))
        self.assertEqual("foo", ~(guard(1)
            | c(lambda x: x > 1)  >> "bar"
            | c(lambda x: x < 1)  >> "baz"
            | c(lambda x: x == 1) >> "foo"
            | otherwise           >> "Err"))

        with self.assertRaises(me): ~(guard(1) | c(lambda x: x == 2) >> 1)

        # syntax checks
        self.assertTrue(~(guard(1)
            | otherwise >> 1))
        self.assertFalse(otherwise.has_return_value())

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
        with self.assertRaises(se): otherwise >> c(lambda _: 1)
        with self.assertRaises(se): otherwise | c(lambda x: x < 1)
        with self.assertRaises(se): otherwise >> c(lambda _: 1)
        with self.assertRaises(se): otherwise | c(lambda x: x < 1)

        with self.assertRaises(se): c(lambda x: x == 10) >> "1" >> "2"
        with self.assertRaises(se): "1" >> c(lambda x: x == 10)
        with self.assertRaises(se): guard(1) | c(lambda x: x > 1)
        with self.assertRaises(se): guard(1) | (lambda x: x > 1)
        with self.assertRaises(se): ~guard(1) | (lambda x: x > 1)
        with self.assertRaises(se): ~guard(1)
        with self.assertRaises(se): otherwise >> "1" >> "2"
        with self.assertRaises(se): "1" >> otherwise


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

        self.assertEqual(5, F(lambda x: lambda y: y + x)(1)(4))
        self.assertEqual(5, F(lambda x: lambda y: y + x)(1, 4))
        self.assertEqual(5, F(lambda x: lambda y: y + x, 1, 4))
        self.assertEqual(5, F(lambda x: lambda y: y + x, 1)(4))

        self.assertEqual(5, F(lambda x: F(lambda y: y + x))(1)(4))
        self.assertEqual(5, F(lambda x: F(lambda y: y + x))(1, 4))
        self.assertEqual(5, F(lambda x: F(lambda y: y + x), 1, 4))
        self.assertEqual(5, F(lambda x: F(lambda y: y + x), 1)(4))

        self.assertEqual(7, F(lambda x: lambda y,z: y + x + z, 1, 4, 2))
        self.assertEqual(7, F(lambda x: lambda y,z: y + x + z, 1, 4)(2))
        self.assertEqual(7, F(lambda x: lambda y,z: y + x + z, 1)(4, 2))
        self.assertEqual(7, F(lambda x: lambda y,z: y + x + z, 1)(4)(2))
        self.assertEqual(7, F(lambda x: lambda y,z: y + x + z)(1, 4, 2))
        self.assertEqual(7, F(lambda x: lambda y,z: y + x + z)(1, 4)(2))
        self.assertEqual(7, F(lambda x: lambda y,z: y + x + z)(1)(4, 2))
        self.assertEqual(7, F(lambda x: lambda y,z: y + x + z)(1)(4)(2))

        self.assertEqual(7, F(lambda x: F(lambda y,z: y + x + z), 1, 4, 2))
        self.assertEqual(7, F(lambda x: F(lambda y,z: y + x + z), 1, 4)(2))
        self.assertEqual(7, F(lambda x: F(lambda y,z: y + x + z), 1)(4, 2))
        self.assertEqual(7, F(lambda x: F(lambda y,z: y + x + z), 1)(4)(2))
        self.assertEqual(7, F(lambda x: F(lambda y,z: y + x + z))(1, 4, 2))
        self.assertEqual(7, F(lambda x: F(lambda y,z: y + x + z))(1, 4)(2))
        self.assertEqual(7, F(lambda x: F(lambda y,z: y + x + z))(1)(4, 2))
        self.assertEqual(7, F(lambda x: F(lambda y,z: y + x + z))(1)(4)(2))

        self.assertEqual(7, F(lambda x,y: lambda z: y + x + z)(1, 4, 2))
        self.assertEqual(7, F(lambda x,y: lambda z: y + x + z)(1, 4)(2))
        self.assertEqual(7, F(lambda x,y: lambda z: y + x + z)(1)(4, 2))
        self.assertEqual(7, F(lambda x,y: lambda z: y + x + z)(1)(4)(2))
        self.assertEqual(7, F(lambda x,y: lambda z: y + x + z, 1, 4, 2))
        self.assertEqual(7, F(lambda x,y: lambda z: y + x + z, 1, 4)(2))
        self.assertEqual(7, F(lambda x,y: lambda z: y + x + z, 1)(4, 2))
        self.assertEqual(7, F(lambda x,y: lambda z: y + x + z, 1)(4)(2))

        self.assertTrue(isinstance(F(lambda x, y: x + y, 1), Func))
        self.assertTrue(isinstance(F(lambda x, y: x + y)(1), Func))
        self.assertTrue(isinstance(F(lambda x: lambda y: x + y, 1), Func))
        self.assertTrue(isinstance(F(lambda x: lambda y: x + y)(1), Func))

        self.assertEqual(4, F(lambda: 4))
        self.assertEqual(4, F(lambda: lambda: 4))
        self.assertEqual(4, F(lambda: lambda: lambda: lambda: lambda: 4))
        self.assertEqual(4, F(F(lambda: lambda: lambda: 4)))
        self.assertEqual(4, F(4))
        self.assertEqual(4, F(F(F(4))))

        # too many arguments
        with self.assertRaises(te): F(lambda: 1)(1, 2)
        with self.assertRaises(te): F(lambda x: x)(1, 2)
        with self.assertRaises(te): F(lambda x, y: x)(1, 2, 3)

    def test_F_functor(self):
        te = TypeError
        f = lambda x: (x + 100) % 75
        g = lambda x: x * 21
        h = lambda x: (x - 31) / 3

        self.assertEqual(f(56), (hid * f)(56))
        self.assertEqual(f(g(h(56))), (hid * f * g * h)(56))
        self.assertEqual(f(g(h(56))), ((hid * f) * g * h)(56))
        self.assertEqual(f(g(h(56))), ((hid * f * g) * h)(56))

        f2, g2, h2 = map(F, (f, g, h))
        self.assertEqual(f(56), (hid * f2)(56))
        self.assertEqual(f2(56), (hid * f2)(56))
        self.assertEqual(f2(g2(h2(56))), (hid * f * g * h2)(56))
        self.assertEqual(f2(g2(h2(56))), (hid * f * g2 * h)(56))
        self.assertEqual(f2(g2(h2(56))), (hid * f * g2 * h2)(56))
        self.assertEqual(f2(g2(h2(56))), (hid * f2 * g * h)(56))
        self.assertEqual(f2(g2(h2(56))), (hid * f2 * g * h2)(56))
        self.assertEqual(f2(g2(h2(56))), (hid * f2 * g2 * h)(56))
        self.assertEqual(f2(g2(h2(56))), (hid * f2 * g2 * h2)(56))

        with self.assertRaises(te):
            self.assertEqual(f2(g2(h2(56))), (f * g * h2)(56))
        self.assertEqual(f2(g2(h2(56))), (f * g2 * h)(56))
        self.assertEqual(f2(g2(h2(56))), (f * g2 * h2)(56))
        self.assertEqual(f2(g2(h2(56))), (f2 * g * h)(56))
        self.assertEqual(f2(g2(h2(56))), (f2 * g * h2)(56))
        self.assertEqual(f2(g2(h2(56))), (f2 * g2 * h)(56))
        self.assertEqual(f2(g2(h2(56))), (f2 * g2 * h2)(56))

        f3, g3, h3 = map(F, (f2, g2, h2))
        self.assertEqual(f(56), (hid * f3)(56))
        self.assertEqual(f3(56), (hid * f3)(56))
        self.assertEqual(f3(g3(h3(56))), (hid * f * g * h3)(56))
        self.assertEqual(f3(g3(h3(56))), (hid * f * g3 * h)(56))
        self.assertEqual(f3(g3(h3(56))), (hid * f * g3 * h3)(56))
        self.assertEqual(f3(g3(h3(56))), (hid * f3 * g * h)(56))
        self.assertEqual(f3(g3(h3(56))), (hid * f3 * g * h3)(56))
        self.assertEqual(f3(g3(h3(56))), (hid * f3 * g3 * h)(56))
        self.assertEqual(f3(g3(h3(56))), (hid * f3 * g3 * h3)(56))

        with self.assertRaises(te):
            self.assertEqual(f3(g3(h3(56))), (f * g * h3)(56))

        self.assertEqual(f3(g3(h3(56))), (f * g3 * h)(56))
        self.assertEqual(f3(g3(h3(56))), (f * g3 * h3)(56))
        self.assertEqual(f3(g3(h3(56))), (f3 * g * h)(56))
        self.assertEqual(f3(g3(h3(56))), (f3 * g * h3)(56))
        self.assertEqual(f3(g3(h3(56))), (f3 * g3 * h)(56))
        self.assertEqual(f3(g3(h3(56))), (f3 * g3 * h3)(56))

        self.assertEqual(f3(g3(h3(56))), (f3 * g * h2)(56))
        self.assertEqual(f3(g3(h3(56))), (f3 * g2 * h)(56))
        self.assertEqual(f3(g3(h3(56))), (f3 * g2 * h3)(56))

    def test_F_apply(self):
        f = lambda x: (x + 100) % 75
        g = lambda x: x * 21
        h = lambda x: (x - 31) / 3

        self.assertEqual(f(56), hid * f % 56)
        self.assertEqual(f(g(h(56))), hid * f * g * h % 56)
        self.assertEqual(f(g(h(56))), (hid * f) * g * h % 56)
        self.assertEqual(f(g(h(56))), (hid * f * g) * h % 56)

        f2, g2, h2 = map(F, (f, g, h))
        self.assertEqual(f(56), hid * f2 % 56)
        self.assertEqual(f2(56), hid * f2 % 56)
        self.assertEqual(f2(g2(h2(56))), hid * f2 * g * h % 56)
        self.assertEqual(f2(g2(h2(56))), hid * (f2 * g) * h % 56)
        self.assertEqual(f2(g2(h2(56))), hid * f * g * h2 % 56)
        self.assertEqual(f2(g2(h2(56))), hid * f2 * g * h2 % 56)
        self.assertEqual(f2(g2(h2(56))), hid * (f2 * g) * h2 % 56)

        f3, g3, h3 = map(F, (f2, g2, h2))
        self.assertEqual(f(56), hid * f3 % 56)
        self.assertEqual(f3(56), hid * f3 % 56)
        self.assertEqual(f3(g3(h3(56))), hid * f3 * g * h % 56)
        self.assertEqual(f3(g3(h3(56))), hid * f * g * h3 % 56)
        self.assertEqual(f3(g3(h3(56))), hid * f3 * g * h3 % 56)
        self.assertEqual(f3(g3(h3(56))), hid * f3 * g2 * h3 % 56)

    def test_id(self):
        self.assertEqual(3, hid(3))
        self.assertEqual(3, hid(hid(hid(3))))
        self.assertEqual(3, hid.fmap(hid).fmap(hid)(3))
        self.assertEqual(3, (hid * hid * hid)(3))
        self.assertEqual(3, hid * hid * hid % 3)
        self.assertEqual(3, hid * hid * hid % hid(3))

    def test_const(self):
        self.assertEqual(1, const(1, 2))
        self.assertEqual(1, const(1)(2))
        self.assertEqual("foo", const("foo", 2))
        self.assertEqual(1, (const(1) * const(2) * const(3))(4))
        self.assertEqual(1, const(1) * const(2) * const(3) % 4)

        self.assertEqual(1, const(hid, 2)(1))
        self.assertEqual(1, const(hid)(2)(1))
        self.assertEqual(1, const(hid)(2) % 1)

    def test_flip(self):
        test_f1 = lambda x, y: x - y
        self.assertEqual(test_f1(9, 1), flip(flip(test_f1))(9, 1))
        self.assertEqual(test_f1(9, 1), flip(test_f1)(1, 9))
        self.assertEqual(test_f1(9, 1), flip(test_f1, 1)(9))
        self.assertEqual(test_f1(9, 1), flip(test_f1, 1, 9))
        self.assertEqual(test_f1(9, 1), flip(test_f1)(1)(9))

        self.assertEqual(test_f1(9, 1), flip(flip(F(test_f1)))(9, 1))
        self.assertEqual(test_f1(9, 1), flip(F(test_f1))(1, 9))
        self.assertEqual(test_f1(9, 1), flip(F(test_f1), 1)(9))
        self.assertEqual(test_f1(9, 1), flip(F(test_f1), 1, 9))
        self.assertEqual(test_f1(9, 1), flip(F(test_f1))(1)(9))

        test_f2 = lambda x, y, z: (x - y) / z
        self.assertEqual(test_f2(9, 1, 2), flip(F(test_f2))(1, 9)(2))
        self.assertEqual(test_f2(9, 1, 2), flip(F(test_f2), 1)(9)(2))
        self.assertEqual(test_f2(9, 1, 2), flip(F(test_f2), 1, 9)(2))
        self.assertEqual(test_f2(9, 1, 2), flip(F(test_f2))(1)(9)(2))
        self.assertEqual(test_f2(9, 1, 2), flip(F(test_f2))(1, 9, 2))
        self.assertEqual(test_f2(9, 1, 2), flip(F(test_f2), 1)(9, 2))
        self.assertEqual(test_f2(9, 1, 2), flip(F(test_f2), 1, 9, 2))
        self.assertEqual(test_f2(9, 1, 2), flip(F(test_f2))(1)(9, 2))

        self.assertEqual(test_f2(9, 1, 2), flip(test_f2)(1, 9, 2))
        self.assertEqual(test_f2(9, 1, 2), flip(test_f2)(1, 9)(2))
        self.assertEqual(test_f2(9, 1, 2), flip(test_f2)(1)(9, 2))
        self.assertEqual(test_f2(9, 1, 2), flip(test_f2)(1)(9)(2))
        self.assertEqual(test_f2(9, 1, 2), flip(test_f2, 1, 9, 2))
        self.assertEqual(test_f2(9, 1, 2), flip(test_f2, 1, 9)(2))
        self.assertEqual(test_f2(9, 1, 2), flip(test_f2, 1)(9, 2))
        self.assertEqual(test_f2(9, 1, 2), flip(test_f2, 1)(9)(2))


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
        self.assertNotEqual(Nothing, None) # questionable

        self.assertTrue(Just(1) == Just(1))
        self.assertFalse(Just(1) == Just(2))

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
        self.assertEqual(list(range(10)), list(List(range(10))))
        self.assertEqual(List(range(10)), List(range(10)))
        self.assertEqual(L[range(10)], List(range(10)))
        self.assertEqual(List(range(10)),
                          List((i for i in range(10))))

    def test_functor(self):
        test_f = lambda x: x ** 2 - 1
        test_g = F(lambda y: y / 4 + 9)

        # functor laws
        self.assertEqual(List(range(10)), List(range(10)) * hid)
        self.assertEqual(List(range(20)) * (test_f * test_g),
                          (List(range(20)) * test_g * test_f))

        # `fmap` == `map` for Lists
        self.assertEqual(map(test_f, list(List(range(9)))),
                          list(List(range(9)) * test_f))
        self.assertEqual(map(test_f, List(range(9))),
                          list(List(range(9)) * test_f))
        self.assertEqual(map(test_f, range(9)),
                          list(List(range(9)) * test_f))

    def test_list_comp(self):
        # numeric lists
        self.assertEqual(10, len(L[0, ...][:10]))
        self.assertEqual(L[0, ...][:10], range(10)[:10])
        self.assertEqual(L[-10, ...][:10], range(-10, 0)[:10])
        self.assertEqual(11, len(L[-5, ..., 5]))
        self.assertEqual(list(L[-5, ..., 5]), list(range(-5, 6)))
        self.assertEqual(list(L[-5, -4, ..., 5]), list(range(-5, 6)))
        self.assertEqual(list(L[-5, -3, ..., 5]), list(range(-5, 6, 2)))
        self.assertEqual(L[1, 3, 5, 7], L[1, 3, ...][:4])
        self.assertEqual(L[3, 5, 7], L[1, 3, ...][1:4])
        self.assertEqual(L[5, 7], L[1, 3, ...][2:4])
        self.assertEqual([], list(L[1, 3, ...][4:4]))
        self.assertEqual([], list(L[1, 3, ...][5:4]))
        self.assertEqual(L[1, 3, 5, 7], L[1, 3, ..., 7])
        self.assertEqual(L[1, 3, 5, 7], L[1, 3, ..., 8])
        self.assertEqual([], list(L[6, ..., 4]))
        self.assertEqual([], list(L[2, 3, ..., 1]))

        # character lists
        self.assertEqual(10, len(L["a", ...][:10]))
        self.assertEqual("abcdefghij", "".join(L["a", ...][:10]))
        self.assertEqual(11, len(L["a", ..., "k"]))

    def test_hmap(self):
        test_f = lambda x: (x + 100) / 2

        # `map` == `hmap` for Lists
        self.assertEqual(map(test_f, range(20)),
                          list(hmap(test_f, range(20))))
        self.assertEqual(map(test_f, range(20)),
                          map(test_f, range(20)))


    def test_hfilter(self):
        test_f = lambda x: x % 2 == 0
        self.assertEqual(filter(test_f, range(20)),
                          list(hfilter(test_f, range(20))))
        self.assertEqual(filter(test_f, range(20)),
                          filter(test_f, range(20)))

    def test_len(self):
        self.assertEqual(0, len(L[None]))
        self.assertEqual(1, len(L[None,]))
        self.assertEqual(3, len(L[1, 2, 3]))


class Test_README_Examples(unittest.TestCase):
    """Make sure the README examples are all working"""

    def test_sections(self):
        pass

    def test_guard(self):
        otherwise.reset()
        porridge_tempurature = 80
        self.assertEqual(
                ~(guard(porridge_tempurature)
                    | c(__ < 20)  >> "Porridge is too cold!"
                    | c(__ < 90)  >> "Porridge is just right!"
                    | c(__ < 150) >> "Porridge is too hot!"
                    | otherwise   >> "Porridge has gone thermonuclear"
                ),
                'Porridge is just right!')

        def examine_password_security(password):
            analysis = ~(guard(password)
                | c(lambda x: len(x) > 20) >> "Wow, that's one secure password"
                | c(lambda x: len(x) < 5)  >> "You made Bruce Schneier cry"
                | c(__ == "12345")         >> "Same combination as my luggage!"
                | otherwise                >> "Hope it's not `password`"
            )
            return analysis

        nuclear_launch_code = "12345"
        self.assertEqual(
                examine_password_security(nuclear_launch_code),
                'Same combination as my luggage!')
        return

    def test_decorators(self):
        def a_problematic_function(cheese):
            if cheese <= 0:
                raise ValueError("Out of cheese error")
            return cheese - 1

        maybe_problematic = in_maybe(a_problematic_function)
        self.assertEqual(maybe_problematic(1), Just(0))
        self.assertEqual(maybe_problematic(0), Nothing)

        either_problematic = in_either(a_problematic_function)
        self.assertEqual(either_problematic(10), Right(9))
        #self.assertEqual(either_problematic(0)
        #                 Left(ValueError('Out of cheese error',)))

        @in_either
        def my_fn_that_raises_errors(n):
            assert type(n) == int, "not an int!"

            if n < 0:
                raise ValueError("Too low!")

            return n + 10

        #self.assertEqual(my_fn_that_raises_errors("hello"),
        #                 Left(AssertionError('not an int!',)))
        #self.assertEqual(my_fn_that_raises_errors(-10),
        #                 Left(ValueError('Too low!',)))
        self.assertEqual(my_fn_that_raises_errors(1), Right(11))
        return


if __name__ == '__main__':
    unittest.main()
