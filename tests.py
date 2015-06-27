import unittest

from hask import H
from hask import sig
from hask import t
from hask import p, m, caseof, w, IncompletePatternError
from hask import has_instance
from hask import guard
from hask import c
from hask import otherwise
from hask import NoGuardMatchException
from hask import __
from hask import data
from hask import d
from hask import deriving
from hask import List
from hask import L
from hask import Ordering, LT, EQ, GT
from hask import Maybe, Just, Nothing, in_maybe
from hask import Either, Left, Right, in_either
from hask import Typeclass
from hask import Hask, Show, Eq, Ord, Bounded
from hask import Num, Real, RealFrac, Fractional, Floating, RealFloat
from hask import Enum, succ, pred
from hask import Functor
from hask import Applicative
from hask import Monad
from hask import Traversable
from hask import Foldable

from hask import Prelude

# internals
from hask.lang.syntax import Syntax

from hask.lang.type_system import make_fn_type
from hask.lang.type_system import build_sig_arg
from hask.lang.type_system import build_sig
from hask.lang.type_system import build_ADT
from hask.lang.type_system import typeof
from hask.lang.type_system import make_data_const
from hask.lang.type_system import make_type_const
from hask.lang.type_system import pattern_match
from hask.lang.type_system import Wildcard
from hask.lang.type_system import PatternMatchBind

from hask.lang.hindley_milner import Var
from hask.lang.hindley_milner import App
from hask.lang.hindley_milner import Lam
from hask.lang.hindley_milner import Let
from hask.lang.hindley_milner import TypeVariable
from hask.lang.hindley_milner import TypeOperator
from hask.lang.hindley_milner import Function
from hask.lang.hindley_milner import Tuple
from hask.lang.hindley_milner import analyze
from hask.lang.hindley_milner import unify


te = TypeError
se = SyntaxError


class TestHindleyMilner(unittest.TestCase):
    """Test the internals of the Hindley-Milner type inference engine"""

    def inference(self, expr):
        """Type inference succeeded using our toy environment"""
        self.assertIsNotNone(analyze(expr, self.env))
        return

    def not_inference(self, expr):
        """Type inference failed using our toy environment"""
        with self.assertRaises(te): analyze(expr, self.env)
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
        with self.assertRaises(te): self.typecheck(expr, expr_type)
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
                        App(Var("x"), Var("4"))),
                    App(Var("x"), Var("True")))))

        # \x -> ((f 4), (f True)) ==> TypeError (undefined symbol f)
        self.not_inference(
            App(
                App(Var("pair"), App(Var("f"), Var("4"))),
                App(Var("f"), Var("True"))))

        # \f -> (f f) ==> TypeError (recursive unification)
        self.not_inference(Lam("f", App(Var("f"), Var("f"))))

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

        # ((pair 1) 4) :: (a, b)
        self.typecheck(
            App(App(Var("pair"), Var("1")), Var("4")),
            TypeOperator("*", [TypeVariable(), TypeVariable()]))


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

    def test_build_sig_item(self):
        """Test type signature building internals - make sure that types are
           translated in a reasonable way"""

        class __test__(object):
            pass

        # type variables
        self.assertTrue(isinstance(build_sig_arg("a", {}), TypeVariable))
        self.assertTrue(isinstance(build_sig_arg("abc", {}), TypeVariable))

        # builtin/non-ADT types
        self.unified(build_sig_arg(str, {}), TypeOperator(str, []))
        self.unified(build_sig_arg(int, {}), TypeOperator(int, []))
        self.unified(build_sig_arg(float, {}), TypeOperator(float, []))
        self.unified(build_sig_arg(list, {}), TypeOperator(list, []))
        self.unified(build_sig_arg(__test__, {}), TypeOperator(__test__, []))

        # unit type (None)
        self.unified(build_sig_arg(None, {}), TypeOperator(None, []))

        # tuple
        self.unified(
                build_sig_arg((int, int), {}),
                Tuple([TypeOperator(int, []), TypeOperator(int, [])]))

        # list

        # adts

    def test_signature_build(self):
        """Make sure type signatures are built correctly"""
        # int -> int
        self.unified(
                make_fn_type(build_sig((H/ int >> int).sig)),
                Function(TypeOperator(int, []), TypeOperator(int, [])))

        # a -> a
        a = TypeVariable()
        self.unified(
                make_fn_type(build_sig((H/ "a" >> "a").sig)),
                Function(a, a))

        # a -> b
        a, b  = TypeVariable(), TypeVariable()
        self.unified(
                make_fn_type(build_sig((H/ "a" >> "b").sig)),
                Function(a, b))

        # (int -> int) -> int -> int
        self.unified(
                make_fn_type(build_sig((H/ (H/ int >> int) >> int >> int).sig)),
                Function(
                    Function(TypeOperator(int, []), TypeOperator(int, [])),
                    Function(TypeOperator(int, []), TypeOperator(int, []))))

    def test_builtins(self):
        """Make sure builtin types typecheck correctly"""

        self.unified(typeof(1), TypeOperator(int, []))

        self.unified(
                typeof(Nothing),
                TypeOperator(Maybe, [TypeVariable()]))

        self.unified(
                typeof(Just(1)),
                TypeOperator(Maybe, [TypeOperator(int, [])]))

        self.unified(
                typeof(Just(Just(Nothing))),
                TypeOperator(Maybe,
                    [TypeOperator(Maybe,
                        [TypeOperator(Maybe, [TypeVariable()])])]))

        self.unified(
                typeof(Right("error")),
                TypeOperator(Either, [TypeVariable(),
                    TypeOperator(str, [])]))

        self.unified(
                typeof(Left(2.0)),
                TypeOperator(Either,
                    [TypeOperator(float, []), TypeVariable()]))

    def test_builtin_HKT(self):
        self.unified(typeof(1), build_sig_arg(t(int), {}))
        self.unified(typeof(Nothing), build_sig_arg(t(Maybe, "a"), {}))
        self.unified(typeof(Just(1)), build_sig_arg(t(Maybe, int), {}))

        self.unified(
                typeof(Just(Just(Nothing))),
                build_sig_arg(t(Maybe, t(Maybe, t(Maybe, "a"))), {}))

        self.unified(
                typeof(Right("error")),
                build_sig_arg(t(Either, str, "a"), {}))

        self.unified(
                typeof(Left(2.0)),
                build_sig_arg(t(Either, "a", int), {}))


class TestTypeSystem(unittest.TestCase):

    def test_TypedFunc_builtin(self):
        """TypedFunc with builtin types"""

        @sig(H/ int >> int)
        def f(x):
            return x + 2

        @sig(H/ int >> int)
        def g(x):
            return x - 5

        # basic type checking
        self.assertEqual(2, f(g(5)))
        with self.assertRaises(te): f(4.0)
        with self.assertRaises(te): f("4")
        with self.assertRaises(te): f(1, 2)

        self.assertEqual(2, (f * g)(5))
        self.assertEqual(2, f * g % 5)

    def test_match(self):
        match_only = lambda v, p: pattern_match(v, p)[0]
        pb = PatternMatchBind
        w = Wildcard()

        # literal matches
        self.assertTrue(match_only(1, 1))
        self.assertTrue(match_only((1, "a"), (1, "a")))
        self.assertTrue(match_only(Nothing, Nothing))
        self.assertTrue(match_only(Just(1), Just(1)))
        self.assertFalse(match_only(2, 1))
        self.assertFalse(match_only(("a", 1), (1, "a")))
        self.assertFalse(match_only(("a", "b"), ["a", "b"]))
        self.assertFalse(match_only(Nothing, Just(Nothing)))
        self.assertFalse(match_only(Just(2), Just(1)))
        self.assertFalse(match_only(Right(2), Just(2)))
        self.assertFalse(match_only(Right(2), Left(2)))

        # matches with wildcard
        self.assertTrue(match_only(1, w))
        self.assertTrue(match_only(Nothing, w))
        self.assertTrue(match_only(Just("whatever"), Just(w)))
        self.assertTrue(match_only(Right(Just(5)), Right(Just(w))))
        self.assertTrue(match_only(("a", "b", "c"), ("a", w, "c")))
        self.assertFalse(match_only(("a", "b", "c"), ("1", w, "c")))
        self.assertFalse(match_only(("a", "b", "d"), ("a", w, "c")))

        # matches with variable binding
        self.assertEqual((True, {"a":1}), pattern_match(1, pb("a")))
        self.assertEqual((True, {"a":1, "b":2}),
                pattern_match((1, 2), (pb("a"), pb("b"))))
        self.assertEqual((True, {"a":8}),
                pattern_match(Just(8), Just(pb("a"))))
        self.assertEqual((True, {"a":"a"}),
                pattern_match(Right(Just("a")), Right(Just(pb("a")))))
        self.assertEqual((False, {"a":1}),
                pattern_match((2, 1), (3, pb("a"))))

        with self.assertRaises(se):
            pattern_match((1, 2), (pb("c"), pb("a")), {"c":1})
        with self.assertRaises(se):
            pattern_match((1, 2), (pb("c"), pb("a")), {"a":1})

        # putting it all together
        self.assertEqual((True, {"a":1, "b":2}),
                pattern_match((1, "a", 2), (pb("a"), w, pb("b"))))


class TestADTInternals_Enum(unittest.TestCase):

    def setUp(self):
        """
        Dummy type constructors and data constructors for an ADT with all
        enum data constructors
        """
        ds =  [("E1", []), ("E2", []), ("E3", [])]
        self.Type_Const, self.E1, self.E2, self.E3 =\
                build_ADT("Type_Const", [], ds, [])

    def test_adt(self):
        self.assertEqual(list(self.Type_Const.__constructors__),
                         [self.E1, self.E2, self.E3])
        self.assertTrue(isinstance(self.E1, self.Type_Const))
        self.assertTrue(isinstance(self.E2, self.Type_Const))
        self.assertTrue(isinstance(self.E3, self.Type_Const))

    def test_derive_eq_data(self):
        with self.assertRaises(te): self.E1 == self.E1
        with self.assertRaises(te): self.E1 != self.E1

        Eq.derive_instance(self.Type_Const)

        self.assertTrue(self.E1 == self.E1)
        self.assertTrue(self.E2 == self.E2)
        self.assertTrue(self.E3 == self.E3)

    def test_derive_show_data(self):
        self.assertNotEquals("E1", str(self.E1))

        Show.derive_instance(self.Type_Const)

        self.assertEqual("E1", str(self.E1))
        self.assertEqual("E2", str(self.E2))
        self.assertEqual("E3", str(self.E3))

    def test_derive_ord_data(self):
        with self.assertRaises(te): self.E1 > self.E1
        with self.assertRaises(te): self.E1 >= self.E1
        with self.assertRaises(te): self.E1 < self.E1
        with self.assertRaises(te): self.E1 <= self.E1

        Eq.derive_instance(self.Type_Const)
        Ord.derive_instance(self.Type_Const)

        self.assertTrue(self.E1 < self.E2)
        self.assertFalse(self.E1 > self.E2)

    def test_derive_bounded_data(self):
        Bounded.derive_instance(self.Type_Const)


class TestADTInternals_Builtin(unittest.TestCase):

    def setUp(self):
        """
        Dummy type constructors and data constructors for an ADT with all
        builtin (non-polymorphic) fields
        """
        ds =  [("M1", [int]), ("M2", [int, str]), ("M3", [int, int, int])]
        self.Type_Const, self.M1, self.M2, self.M3 =\
                build_ADT("Type_Const", [], ds, [])

    def test_adt(self):
        self.assertTrue(isinstance(self.M1(1), self.Type_Const))
        self.assertTrue(isinstance(self.M2(1, "abc"), self.Type_Const))
        self.assertTrue(isinstance(self.M3(1, 2, 3), self.Type_Const))

    def test_derive_eq_data(self):
        with self.assertRaises(te): self.M1(1) == self.M1(1)
        with self.assertRaises(te): self.M1(1) != self.M1(1)

        Eq.derive_instance(self.Type_Const)

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
        self.assertNotEquals("M1(1)", str(self.M1(1)))

        Show.derive_instance(self.Type_Const)

        self.assertEqual("M1(1)", str(self.M1(1)))
        self.assertEqual("M2(1, \'a\')", str(self.M2(1, "a")))
        self.assertEqual("M3(1, 2, 3)", str(self.M3(1, 2, 3)))

    def test_derive_ord_data(self):
        with self.assertRaises(te): self.M1(1) > self.M1(1)
        with self.assertRaises(te): self.M1(1) >= self.M1(1)
        with self.assertRaises(te): self.M1(1) < self.M1(1)
        with self.assertRaises(te): self.M1(1) <= self.M1(1)

        Eq.derive_instance(self.Type_Const)
        Ord.derive_instance(self.Type_Const)

        self.assertTrue(self.M1(1) < self.M1(2))
        self.assertTrue(self.M1(1) <= self.M1(2))
        self.assertTrue(self.M1(2) <= self.M1(2))
        self.assertFalse(self.M1(3) < self.M1(2))
        self.assertFalse(self.M1(3) <= self.M1(2))

        self.assertTrue(self.M1(2) > self.M1(1))
        self.assertTrue(self.M1(2) >= self.M1(1))
        self.assertTrue(self.M1(2) >= self.M1(2))
        self.assertFalse(self.M1(1) > self.M1(2))
        self.assertFalse(self.M1(1) >= self.M1(2))

    def test_derive_bounded_data(self):
        with self.assertRaises(te):
            Bounded.derive_instance(self.Type_Const)


class TestADT(unittest.TestCase):

    def test_data(self):
        # these are not syntactically valid
        with self.assertRaises(se): data.N("a", "a")
        with self.assertRaises(se): data.N(1, "b")
        with self.assertRaises(se): data.N("a")("b")
        with self.assertRaises(se): data.N()

        # these should all work fine
        self.assertIsNotNone(data.N)
        self.assertIsNotNone(data.N("a"))
        self.assertIsNotNone(data.N("a", "b"))

    def test_d(self):
        # these are not syntactically valid
        with self.assertRaises(se): d.A | deriving(Eq)
        with self.assertRaises(se): deriving(Eq, Show) | d.B

        # these should all work fine
        self.assertIsNotNone(d.A)
        self.assertIsNotNone(d.A("a"))
        self.assertIsNotNone(d.A("a", "b", "c"))
        self.assertIsNotNone(d.A("a") | d.B("b"))
        self.assertIsNotNone(d.A("a") | d.B)
        self.assertIsNotNone(d.B | d.A("a"))
        self.assertIsNotNone(d.B | d.A)
        self.assertIsNotNone(d.A("a") | d.B("b") | d.C("a"))
        self.assertIsNotNone(d.A("a", "b") & deriving(Eq, Show))
        self.assertIsNotNone(d.A("a") | d.B("b") & deriving(Eq, Show))

    def test_holistic(self):
        T, M1, M2, M3 =\
        data.T("a", "b") == d.M1("a") | d.M2("b") | d.M3 & deriving(Show, Eq)

        self.assertTrue(M1(20) == M1(20))
        self.assertTrue(M1(20) != M1(21))
        self.assertTrue(M2(20) == M2(20))
        self.assertTrue(M2(20) != M2(21))
        self.assertTrue(M3 == M3)
        self.assertFalse(M3 != M3)


class TestBuiltins(unittest.TestCase):

    def test_enum(self):
        self.assertEqual("b", succ("a"))
        self.assertEqual("a", pred("b"))
        self.assertEqual(2, succ(1))
        self.assertEqual(1, pred(2))
        self.assertEqual(4, succ(succ(succ(1))))
        self.assertEqual(-1, pred(pred(pred(2))))

    def test_num(self):
        self.assertTrue(has_instance(float, Num))
        self.assertTrue(has_instance(float, Num))


class TestSyntax(unittest.TestCase):

    def test_syntax(self):
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
        # TODO: add partially applied double sections
        self.assertEqual(3, (__+__)(1, 2))
        self.assertEqual(1, (__-__)(2, 1))
        self.assertEqual(4, (__*__)(1, 4))
        self.assertEqual(3, (__/__)(12, 4))

        # sections composed with `fmap`
        self.assertEqual(3, ((__+1) * (__+1) * (1+__))(0))
        self.assertEqual(3, (__+1) * (__+1) * (1+__) % 0)
        self.assertEqual(4, (__ + 1) * (__ * 3) % 1)

    def test_guard(self):
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
        with self.assertRaises(se): c(lambda x: x == 10) >> 2 >> 2
        with self.assertRaises(se): c(lambda x: x > 1) | c(lambda x: x < 1)
        with self.assertRaises(se): otherwise >> c(lambda _: 1)
        with self.assertRaises(se): otherwise | c(lambda x: x < 1)
        with self.assertRaises(se): otherwise >> c(lambda _: 1)
        with self.assertRaises(se): otherwise | c(lambda x: x < 1)
        with self.assertRaises(se):
            ~(guard(2) | c(lambda x: x == 2) >> 1 | c(lambda y: y == 2))
        with self.assertRaises(se): c(lambda x: x == 10) >> "1" >> "2"
        with self.assertRaises(se): "1" >> c(lambda x: x == 10)
        with self.assertRaises(se): guard(1) | c(lambda x: x > 1)
        with self.assertRaises(se): guard(1) | (lambda x: x > 1)
        with self.assertRaises(se): ~guard(1) | (lambda x: x > 1)
        with self.assertRaises(se): ~guard(1)
        with self.assertRaises(se): otherwise >> "1" >> "2"
        with self.assertRaises(se): "1" >> otherwise

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

    def test_caseof(self):
        # literal matching
        self.assertEqual(1,
                ~(caseof("a")
                    | m("a") >> 1))
        self.assertEqual(1,
                ~(caseof(2.0)
                    | m(2.0) >> 1
                    | m(2.0) >> 2))
        self.assertEqual("x",
                ~(caseof(Just("x"))
                    | m(Nothing)   >> False
                    | m(Just("x")) >> "x"))
        self.assertEqual(1,
                ~(caseof([1, 2])
                    | m((1, 2)) >> 2
                    | m([1, 2]) >> 1))
        self.assertEqual(True,
                ~(caseof(GT)
                    | m(LT) >> False
                    | m(EQ) >> False
                    | m(GT) >> True))

        with self.assertRaises(IncompletePatternError):
            ~(caseof(1) | m(2) >> 2)

        # matches with wildcard
        self.assertEqual(1,
                ~(caseof(1)
                    | m(w) >> 1
                    | m(1) >> 2))
        self.assertEqual(True,
                ~(caseof(GT)
                    | m(LT) >> False
                    | m(EQ) >> False
                    | m(w) >> True))
        self.assertEqual(False,
                ~(caseof(GT)
                    | m(LT) >> False
                    | m(w)  >> False
                    | m(GT) >> True))
        self.assertEqual(2,
                ~(caseof((1, 2, 3))
                    | m((2, 1, 3)) >> 1
                    | m((1, w, 3)) >> 2
                    | m((1, 2, 3)) >> 3))

        # variable bind
        self.assertEqual(("b", "a"),
                ~(caseof(("a", "b"))
                    | m((m.x, m.y)) >> (p.y, p.x)
                    | m(w)          >> None))
        self.assertEqual(1,
                ~(caseof(Just(1))
                    | m(Just(m.x)) >> p.x
                    | m(Nothing)   >> 0))
        self.assertEqual(Just(0),
                ~(caseof(Nothing)
                    | m(Just(m.x)) >> Just(p.x + 1)
                    | m(Nothing)   >> Just(0)))
        self.assertEqual(1, ~(caseof(2) # somewhat questionable behavior
                | m((m.a, m.a)) >> p.a
                | m(2)          >> 1))

        with self.assertRaises(se):
            ~(caseof((1, 2))
                | m((m.a, m.a)) >> p.a
                | m(1)          >> 1)



class TestMaybe(unittest.TestCase):

    def test_instances(self):
        self.assertTrue(has_instance(Maybe, Show))
        self.assertTrue(has_instance(Maybe, Eq))
        self.assertTrue(has_instance(Maybe, Functor))
        self.assertTrue(has_instance(Maybe, Applicative))
        self.assertTrue(has_instance(Maybe, Monad))

        self.assertFalse(has_instance(Maybe, Typeclass))
        self.assertFalse(has_instance(Maybe, Num))
        self.assertFalse(has_instance(Maybe, Foldable))
        self.assertFalse(has_instance(Maybe, Traversable))

    def test_show(self):
        self.assertEqual("Just(3)", str(Just(3)))
        self.assertEqual("Nothing", str(Nothing))

    def test_eq(self):
        self.assertEqual(Nothing, Nothing)
        self.assertEqual(Just(3), Just(3))
        self.assertEqual(Just("3"), Just("3"))

        self.assertNotEqual(Just(1), Just(3))
        self.assertNotEqual(Just(1), Just("1"))
        self.assertNotEqual(Just(3), Nothing)
        self.assertNotEqual(Nothing, Just(0))
        self.assertNotEqual(Nothing, None) # type error
        self.assertNotEqual(Nothing, 1) # type error
        self.assertNotEqual(Just(1), 1) # type error

        self.assertTrue(Just(1) == Just(1))
        self.assertFalse(Just(1) == Just(2))

        self.assertTrue(Nothing == Nothing or Nothing != Nothing)
        self.assertTrue(Just(1) == Just(1) or Just(1) != Just(1))
        self.assertFalse(Nothing == Nothing and Nothing != Nothing)
        self.assertFalse(Just(1) == Just(1) and Just(1) != Just(1))

    def test_ord(self):
        # add more
        self.assertTrue(Nothing < Just(0))
        self.assertTrue(Nothing < Just(-float("inf")))

    def test_fmap(self):
        # add more
        self.assertEqual(Just(3), Just(2) * (lambda x: x + 1))
        self.assertEqual(Just("1"), Just(1) * str)

    def test_bind(self):
        # add more
        self.assertEqual(Just("1"), Just(1) >> (lambda x: Just(str(x))))
        self.assertEqual(Just(10), Just(1) >> (lambda x: Just(x * 10)))
        #self.assertEqual(Just(10), Just(1) >> F(lambda x: Just(x * 10)))
        #self.assertEqual(Just(1000), Just(1) >>
        #        (lambda x: Just(x * 10)) >>
        #        (lambda x: Just(x * 10)) >>
        #        (lambda x: Just(x * 10)))


class TestEither(unittest.TestCase):

    def test_instances(self):
        self.assertTrue(has_instance(Either, Show))
        self.assertTrue(has_instance(Either, Eq))
        self.assertTrue(has_instance(Either, Functor))
        self.assertTrue(has_instance(Either, Applicative))
        self.assertTrue(has_instance(Either, Monad))

        self.assertFalse(has_instance(Either, Typeclass))
        self.assertFalse(has_instance(Either, Num))
        self.assertFalse(has_instance(Either, Foldable))
        self.assertFalse(has_instance(Either, Traversable))

    def test_functions(self):
        from hask.Data.Either import either
        from hask.Data.Either import isRight
        from hask.Data.Either import isLeft
        from hask.Data.Either import lefts
        from hask.Data.Either import rights
        from hask.Data.Either import partitionEithers

        f = (lambda x: x + " world") ** (H/ str >> str)
        g = (lambda x: x * 10) ** (H/ int >> int)

        #self.assertEqual(20, either(f, g, Right(2)))
        #self.assertEqual("hello world", either(f, g, Left("hello ")))
        self.assertTrue(isLeft(Left(1)))
        self.assertTrue(isRight(Right("a")))
        self.assertFalse(isLeft(Right("a")))
        self.assertFalse(isRight(Left(1)))

        self.assertEqual(L[1, 3],
                rights(L[Right(1), Left(2), Right(3), Left(4)]))
        self.assertEqual(L[2, 4],
                lefts(L[Right(1), Left(2), Right(3), Left(4)]))
        self.assertEqual((L[2, 4], L[1, 3]),
                partitionEithers(L[Right(1), Left(2), Right(3), Left(4)]))


class TestList(unittest.TestCase):

    def test_instances(self):
        self.assertTrue(has_instance(List, Show))
        self.assertTrue(has_instance(List, Eq))
        self.assertTrue(has_instance(List, Functor))
        self.assertTrue(has_instance(List, Applicative))
        self.assertTrue(has_instance(List, Monad))
        #self.assertTrue(has_instance(List, Foldable))
        #self.assertTrue(has_instance(List, Traversable))

    def test_indexing(self):
        # add more corner cases

        ie = IndexError
        self.assertEqual(3, L[range(10)][3])
        self.assertEqual(3, L[range(4)][-1])
        self.assertEqual(3, L[(i for i in range(10))][3])
        self.assertEqual(3, L[(i for i in range(4))][-1])
        self.assertEqual(2, L[[0, 1, 2, 3]][2])
        self.assertEqual(2, L[[0, 1, 2, 3]][-2])
        self.assertEqual(1, L[(0, 1, 2, 3)][1])
        self.assertEqual(1, L[(0, 1, 2, 3)][-3])

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
        #test_g = F(lambda y: y / 4 + 9)

        # functor laws
        #self.assertEqual(List(range(10)), List(range(10)) * hid)
        #self.assertEqual(List(range(20)) * (test_f * test_g),
        #                  (List(range(20)) * test_g * test_f))

        # `fmap` == `map` for Lists
        #self.assertEqual(map(test_f, list(List(range(9)))),
        #                  list(List(range(9)) * test_f))
        #self.assertEqual(map(test_f, List(range(9))),
        #                  list(List(range(9)) * test_f))
        #self.assertEqual(map(test_f, range(9)),
        #                  list(List(range(9)) * test_f))

    def test_hmap(self):
        from hask.Data.List import map as hmap

        test_f = sig(H/ int >> int)(lambda x: (x + 100) / 2)

        # `map` == `hmap` for Lists
        self.assertEqual(map(test_f, range(20)),
                          list(hmap(test_f, L[range(20)])))
        self.assertEqual(map(test_f, range(20)),
                          map(test_f, L[range(20)]))


    def test_hfilter(self):
        from hask.Data.List import filter as hfilter

        test_f = sig(H/ int >> bool)(lambda x: x % 2 == 0)
        self.assertEqual(filter(test_f, range(20)),
                          list(hfilter(test_f, L[range(20)])))
        self.assertEqual(filter(test_f, range(20)),
                          filter(test_f, L[range(20)]))

    def test_len(self):
        self.assertEqual(0, len(L[None]))
        self.assertEqual(1, len(L[None,]))
        self.assertEqual(3, len(L[1, 2, 3]))


class TestDataList(unittest.TestCase):

    def test_infinite_lists(self):
        plus_one = (lambda x: x + 1) ** (H/ int >> int)
        #self.assertEquals(iterate(plus_one, 0)[:10], L[range(10)])


class TestPrelude(unittest.TestCase):

    def test_imports(self):
        """Prelude imports from Data.* modules; make sure things get loaded in
           correctly
        """
        # tuples
        from hask.Prelude import fst
        from hask.Prelude import snd
        from hask.Prelude import curry
        from hask.Prelude import uncurry

        # strings
        from hask.Prelude import lines
        from hask.Prelude import words
        from hask.Prelude import unlines
        from hask.Prelude import unwords

        # Maybe
        from hask.Prelude import Maybe
        from hask.Prelude import Just
        from hask.Prelude import Nothing
        from hask.Prelude import maybe

        # Either
        from hask.Prelude import Either
        from hask.Prelude import Left
        from hask.Prelude import Right
        from hask.Prelude import either

        # List

        # Ordering
        from hask.Prelude import Ordering
        from hask.Prelude import LT
        from hask.Prelude import EQ
        from hask.Prelude import GT
        from hask.Prelude import max
        from hask.Prelude import min
        from hask.Prelude import compare


    def test_until(self):
        from hask.Prelude import until

        self.assertEquals(1, until((__>0), (__+1), -20))

    def test_error(self):
        from hask.Prelude import error

        with self.assertRaises(Exception): error("")

        msg = "OUT OF CHEESE ERROR"
        try:
            error(msg)
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(msg, e.message)


class TestDataMaybe(unittest.TestCase):

    def test_all(self):
        from hask.Data.Maybe import maybe
        from hask.Data.Maybe import isJust
        from hask.Data.Maybe import isNothing
        from hask.Data.Maybe import fromJust
        from hask.Data.Maybe import listToMaybe
        from hask.Data.Maybe import maybeToList
        from hask.Data.Maybe import catMaybes
        from hask.Data.Maybe import mapMaybe

        self.assertTrue(isJust(Just(1)))
        self.assertTrue(isJust(Just(Nothing)))
        self.assertFalse(isJust(Nothing))
        self.assertFalse(isNothing(Just(1)))
        self.assertFalse(isNothing(Just(Nothing)))
        self.assertTrue(isNothing(Nothing))

        self.assertEqual(fromJust(Just("bird")), "bird")
        self.assertEqual(fromJust(Just(Nothing)), Nothing)


class TestDataEither(unittest.TestCase):

    def test_all(self):
        from hask.Data.Either import either
        from hask.Data.Either import lefts
        from hask.Data.Either import rights
        from hask.Data.Either import isLeft
        from hask.Data.Either import isRight
        from hask.Data.Either import partitionEithers


class TestDataString(unittest.TestCase):

    def test_string(self):
        from hask.Data.String import lines
        from hask.Data.String import words
        from hask.Data.String import unlines
        from hask.Data.String import unwords

        self.assertEqual(lines("a\nb \n\nc"), L[["a", "b ", "", "c"]])
        self.assertEqual(lines(""), L[[]])
        self.assertEqual(unlines(L[["a", "b ", "", "c"]]), "a\nb \n\nc")
        self.assertEqual(unlines(L[[]]), "")
        self.assertEqual(words(" 1 2  4"), L[["", "1", "2", "", "4"]])
        self.assertEqual(unwords(L[["", "1", "2", "", "4"]]), " 1 2  4")


class TestDataTuple(unittest.TestCase):

    def test_tuple(self):
        from hask.Data.Tuple import fst
        from hask.Data.Tuple import snd
        from hask.Data.Tuple import curry
        from hask.Data.Tuple import uncurry
        from hask.Data.Tuple import swap

        self.assertEqual(1, fst((1, 2)))
        self.assertEqual(("a", "b"), fst((("a", "b"), ("c", "d"))))
        self.assertEqual("a", fst(fst((("a", "b"), ("c", "d")))))

        self.assertEqual(2, snd((1, 2)))
        self.assertEqual(("c", "d"), snd((("a", "b"), ("c", "d"))))
        self.assertEqual("b", snd(fst((("a", "b"), ("c", "d")))))
        self.assertEqual("c", fst(snd((("a", "b"), ("c", "d")))))

        self.assertEqual(swap(swap((1, 2))), (1, 2))
        self.assertEqual(swap((1, "a")), ("a", 1))

        @sig(H/ (str, str) >> str)
        def uncurried_fn(tup):
            return tup[0] + tup[1]

        @sig(H/ list >> list >> list)
        def curried_fn(x, y):
            return x + y

        self.assertEqual(uncurry(curried_fn, ([1, 2], [3, 4])), [1, 2, 3, 4])
        self.assertEqual(curry(uncurried_fn, "a", "b"), "ab")
        #self.assertEqual(uncurry(curry(uncurried_fn), ("a","b")), "ab")
        #self.assertEqual(curry(uncurry(curried_fn), ["a"], ["b"]), ["a","b"])


class TestDataOrd(unittest.TestCase):

    def test_ord(self):
        from hask.Data.Ord import max as hmax
        from hask.Data.Ord import min as hmin
        from hask.Data.Ord import compare as compare
        from hask.Data.Ord import comparing as comparing

        self.assertEqual(hmax(1, 2), 2)
        self.assertEqual(hmin(1, 2), 1)
        self.assertEqual(compare(1, 2), LT)

        from hask.Data.Tuple import fst, snd
        self.assertEqual(comparing(fst, (1, 2), (3, 0)), LT)
        self.assertEqual(comparing(snd, (1, 2), (3, 0)), GT)


class Test_README_Examples(unittest.TestCase):
    """Make sure the README examples are all working"""
    def test_match(self):

        @sig(H/ int >> int)
        def fib(x):
            if x < -5:
                raise ValueError()

            return ~(caseof(x)
                        | m(0)   >> 1
                        | m(1)   >> 1
                        | m(m.n) >> fib(p.n - 1)#fib(p.n - 1) + fib(p.n - 2)
                    )

        self.assertEqual(1, fib(0))
        #self.assertEqual(1, fib(1))
        #self.assertEqual(8, fib(6))


    def test_sections(self):
        pass

    def test_guard(self):
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

    def test_decorators(self):
        def eat_cheese(cheese):
            if cheese <= 0:
                raise ValueError("Out of cheese error")
            return cheese - 1

        maybe_eat = in_maybe(eat_cheese)
        self.assertEqual(maybe_eat(1), Just(0))
        self.assertEqual(maybe_eat(0), Nothing)
        self.assertEqual(Just(7), maybe_eat(10) >> maybe_eat >> maybe_eat)
        self.assertEqual(Nothing, maybe_eat(1) >> maybe_eat >> maybe_eat)

        either_eat = in_either(eat_cheese)
        self.assertEqual(either_eat(10), Right(9))
        self.assertTrue(isinstance(either_eat(0)[0], ValueError))

        @in_either
        def picky_add_10(n):
            assert type(n) == int, "not an int!"

            if n < 0:
                raise ValueError("Too low!")

            return n + 10

        self.assertTrue(isinstance(picky_add_10("hello")[0], AssertionError))
        self.assertTrue(isinstance(picky_add_10(-10)[0], ValueError))
        self.assertEqual(picky_add_10(1), Right(11))


if __name__ == '__main__':
    unittest.main()
