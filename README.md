Remaining TODOs:
* Change type inference ending so it understands polymorphic HKTs
* Rewrite List type to work the way it should
* Write rest of Data.List and Prelude, and document everything undocumented
* Final refactor of everything
* Write rest of README
* Write tests for everything
* ???
* Profit
* Change type inference engine so that it is aware of typeclasses


# Hask

Hask is a pure-Python, zero-dependencies library that mimics most of the core
language tools from Haskell, including:

* Full Hindley-Milner type system (with typeclasses) that will typecheck any
  function decorated with a Hask type signature
* Easy creation of new algebraic data types and new typeclasses, with
  Haskell-like syntax
* Pattern matching with `case` expressions
* Automagical function currying/partial application and function composition
* Efficient, immutable, lazily evaluated `List` type with Haskell-style list
  comprehensions
* All your favorite syntax and control flow tools, including operator sections,
  monadic error handling, guards, and more
* Python port of (some of) the standard libraries from Haskell's `base`,
  including:
    * Algebraic datatypes from the Haskell `Prelude`, including `Maybe` and
      `Either`
    * Typeclasses from the Haskell `base` libraries, including `Functor`,
      `Applicative`, `Monad`, `Enum`, `Num`, and all the rest
    * Standard library functions from `base`, including all functions from
      `Prelude`, `Data.List`, `Data.Maybe`, and more


Features not yet implemented, but coming soon:

* Python 3 compatibility
* Better support for polymorphic return values/type defaulting
* Better support for lazy evaluation (beyond just the `List` type and pattern matching)
* Improved pattern matching, including pattern matching on Lists
* More of the Haskell standard library (`Control.*` libraries, QuickCheck, and more)
* Monadic, lazy I/O

**Note that all of this is still very much pre-alpha, and some things may be buggy!**

## Installation

1) `git clone https://github.com/billpmurphy/hask`

2) `python setup.py install`

To run the tests: `python tests.py`.


## Why did you make this?

My goal was to cram as much of Haskell into Python as possible while still
being 100% compatible with the rest of the language, just to see if any useful
ideas came out of the result. Also, it was fun!

Contributions, forks, and extensions to this experiment are always welcome!
Feel free to submit a pull request, open an issue, or email me. In the spirit
of this project, abusing the Python language as much as possible is encouraged.


## Features

Hask is a grab-bag of features that add up to one big pseudo-Haskell functional
programming library. The rest of this README lays out the basics.

I recommend playing around in the REPL while going through the examples. You
can import all the language features with `from hask import *`. To import the
Prelude, use `from hask.Prelude import *`.


### The List type and list comprehensions


Hask provides the `List` type, a lazy and statically-typed list, similar to
Haskell's standard list type.

To create a new `List`, just put the elements inside `L[` and `]` brackets, or
wrap an existing iterable inside `L[ ]`.

```python
>>> L[1, 2, 3]
L[1, 2, 3]

>>> my_list = ["a", "b", "c"]
>>> L[my_list]
L['a', 'b', 'c']

>>> L[(x**2 for xs in range(1, 11)]
L[1 ... ]
```

To add elements to the front of a List, use `^`, the cons operator.  To combine
two lists, use `+`, the concatenation operator.

```
>>> 1 ^ L[2, 3]
L[1, 2, 3]

>>> "goodnight" ^ ("sweet" ^ ("prince" ^ L[[]]))
L["goodnight", "sweet", "price"]

>>> "a" ^ L[1.0, 10.3]  # type error

>>> L[1, 2] + L[3, 4]
L[1, 2, 3, 4]
```

Lists are always evaluated lazily, and will only evaluate list elements as
needed, so you can use infinite Lists or put never-ending generators inside of a `List`. (Of course, you can still blow up the interpreter if you try
to evaluate the entirety of an infinite List, e.g. by trying to find the length
of the List with `len`.)

One way to create infinite lists is via list comprehensions. As in Haskell,
there are four basic type of list comprehensions:


```python
# list from 1 to infinity, counting by ones
L[1, ...]

# list from 1 to infinity, counting by twos
L[1, 3, ...]

# list from 1 to 10 (inclusive), counting by ones
L[1, ..., 20]

# list from 1 to 20 (inclusive), counting by fours
L[1, 5, ..., 20]
```

List comprehensions can be used on ints, longs, floats, one-character strings,
or any other instance of the `Enum` typeclass (more on this later).

Hask provides all of the Haskell functions for List manipulation (`take`,
`drop`, `takeWhile`, etc.), or you can also use Python-style indexing.


```python
>>> L[1, ...]
L[1 ...]


>>> from hask.Data.List import take
>>> take(5, L["a", "b", ...])
L['a', 'b', 'c', 'd', 'e']


>>> L[1,...][5:10]
L[6, 7, 8, 9, 10]


>>> from hask.Data.List import map
>>> from hask.Data.Char import chr
>>> letters = map(chr, L[97, ...])
>>> letters[:9]
L['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']


>>> len(L[1, 3, ...])  # uh oh
```

Otherwise, you can use `List` just like you would use a regular Python list.

```python
for i in L[0, ...]:
    print i


>>> 55 in L[1, 3, ...]
True
```

### Abstract Data Types

Hask allows you to define [algebraic
datatypes](https://wiki.haskell.org/Algebraic_data_type), which are immutable
objects with a fixed number of typed, unnamed fields.

Here is the definition for the infamous `Maybe` type:

```python
from hask import data, d, deriving
from hask import Read, Show, Eq, Ord

Maybe, Nothing, Just =\
    data.Maybe("a") == d.Nothing | d.Just("a") & deriving(Read, Show, Eq, Ord)
```

Let's break this down a bit. The syntax for defining a new type constructor is:

```python
data.TypeName("type param", "type param 2" ... "type param n")
```

This defines a new algebraic datatype with type parameters.

To define data constructors for this type, use `d.` The name of the data
constructor goes first, followed by its fields. Multiple data constructors
should be separted by `|`. If your data constructor has no fields, you can omit
the parens. For example:

```python
FooBar, Foo, Bar =\
    data.FooBar("a", "b") == d.Foo("a", "b", str) | d.Bar
```

To automagically derive typeclass instances for the type, add `&
deriving(...typeclasses...)` after the data constructor declarations.
Currently, the only typeclasses that can be derived are `Eq`, `Show`, `Read`,
`Ord`, and `Bounded`.

Putting it all together, here is the definition of `Either`:

```python
Either, Left, Right =\
    data.Either("a", "b") == d.Left("a") | d.Right("b") & deriving(Read, Show, Eq)
```

We can now use the data constructors defined in a `data` statement to create
instances of our new types. If our data constructor takes no arguments, we can
use it just like a variable.

```python
>>> Just(10)
Just(10)

>>> Nothing
Nothing

>>> Just(Just(10))
Just(Just(10))

>>> Left(1)
Left(1)

>>> Foo(1, 2, "hello")
Foo(1, 2, 'hello')
```

You can view the type of an object with `_t` (equivalent to `:t` in ghci).

```python
>>> from hask import _t

>>> _t(1)
int

>>> _t(Just("soylent green")
Maybe str

>>> _t(Right(("a", 1)))
Either a (str, int)

>>> _t(Just)
(a -> Maybe a)

>>> _t(L[1, 2, 3, 4])
[int]
```


### The type system and typed functions

So what's up with those types? Hask operates its own shadow Hindley-Milner type
system on top of Python's type system; `_t` is showing you the Hask type of a
particular object.


There are two ways to create `TypedFunc` objects:

1) Use the `sig` decorator to decorate the function with the type signature

```python
@sig(H/ "a" >> "b" >> "a")
def const(x, y):
    return x
```

2) Use the `**` operator (similar to `::` in Haskell) to provide the type.
Useful for turning functions or lambdas into `TypedFunc` objects in the REPL,
or wrapping already-defined Python functions.

```python
def const(x, y):
    return x

const = const ** (H/ "a" >> "b" >> "a")
```

`TypedFunc` objects have several special properties.  First, they are type
checked--when arguments are supplied, the type inference engine will check
whether their types match the type signature, and raise a `TypeError` if there
is a discrepancy.

```python
>>> f = (lambda x, y: x + y) ** (H/ int >> int >> int)

>>> f(2, 3)
5

>>> f(9, 1.0)  # type error
```

Second, `TypedFunc` objects can be partially applied:

```python
>>> g = (lambda a, b, c: a / (b + c)) ** (H/ int >> int >> int >> int)

>>> g(10, 2, 3)
2

>>> part_g = g(12)

>>> part_g(2, 2)
3

>>> g(20, 1)(4)
4
```

`TypedFunc` objects also have two special infix operators, the `*` and `%`
operators. `*` is the compose operator (equivalent to `(.)` in Haskell), so
`f * g` is equivalent to `lambda x: f(g(x))`. `%` is just the apply operator,
which applies a `TypedFunc` to one argument (equivalent to `($)` in Haskell).

```python
```

The convinience of this notation (when combined with partial application) cannot be overstated--you can get rid of a ton of nested parenthesis this way.

The compose operation is also typed-checked, which makes it appealing to
write programs in the Haskell style of chaining together lots of functions with
composition and relying on the type system to catch programming errors.

As you would expect, data constructors are also just `TypedFunc` objects:

```python
>>> Just * Just * Just * Just % 77
Just(Just(Just(Just(77))))
```

The type signature syntax is very simple, and consists of a few basic
primitives:

| Primitive | Syntax/examples |
| --------- | --------------- |
| Type literal for Python builtin type or user-defined class | `int`, `float`, `set`, etc |
| Type variable | `"a"`, `"b"`, `"zz"`, etc |
| `List` of some type | `[int]`, `["a"]`, etc |
| Tuple type | `(int, int)`, `("a", "b", "c")`, etc |
| ADT with type parameters | `t(Maybe, "a")`, `t(Either, "a", str)`, etc |
| Unit type (`None`) | `None` |
| Untyped Python function | `func` |
| Typeclass constraint | `H[(Eq, "a")]/`, `H[(Functor, "f"), (Show, "f")]/`, etc |

Some examples:

```python
# add two ints together
@sig(H/ int >> int >> int)
def add(x, y):
    return x + y


# reverse order of arguments to a function
@sig(H/ (H/ "a" >> "b" >> "c") >> "b" >> "a" >> "c")
def flip(f, b, a):
    return f(a, b)


# map a Python (untyped) function over a Python (untyped) set
@sig(H/ func >> set >> set)
def set_map(fn, lst):
    return set((fn(x) for x in lst))


# map a typed function over a List
@sig(H/ (H/ "a" >> "b") >> ["a"] >> ["b"])
def map(f, xs):
    return L[(f(x) for x in xs)]


# type signature with an Eq constraint
@sig(H[(Eq, "a")]/ "a" >> ["a"] >> bool)
def not_in(y, xs):
    return not any((x == y for x in xs))


# type signature with a type constructor (Maybe) that has type arguments
@sig(H/ int >> int >> t(Maybe, int))
def safe_div(x, y):
    return Nothing if y == 0 else Just(x/y)


# type signature for a function that returns nothing
@sig(H/ int >> None)
def launch_missiles(num_missiles):
    print "Launching {0} missiles! Bombs away!" % num_missiles
```

It is also possible to create type synonyms using `t`. For example, check out the definition of `Rational`:

```python
Ratio, R =\
        data.Ratio("a") == d.R("a", "a") & deriving(Eq)


Rational = t(Ratio, int)


@sig(H/ Rational >> Rational >> Rational)
def addRational(rat1, rat2):
    ...
```

### Pattern matching


Here is a function that uses pattern matching to compute the fibonacci sequence:

```python
def fib(x):
    return ~(caseof(x)
                | m(0)   >> 1
                | m(1)   >> 1
                | m(m.n) >> fib(p.n - 1) + fib(p.n - 2)
            )

>>> fib(1)
1

>>> fib(6)
13
```

Notice that in the above example, we are pattern matching on a recursive
function without a hitch.

Pattern matching on iterables (`list`, `tuple`, `list`, etc.) is just as easy:

```python
```

You can also deconstruct an iterable using `^`, the cons operator. The variable
before the `^` is bound to the first element of the iterable, and the variable
after the `^` is bound to the rest of the iterable. Here is a function that
adds the first two elements of any iterable, returning `Nothing` if there are
less than two elements:

```python
@sig(H[(Num, "a")]/ ["a"] >> t(Maybe, "a"))
def add_first_two(x):
    return ~(caseof(lst)
                | m(m.x ^ (m.y ^ m.z)) >> Just(p.y + .py)
                | m(m.x)               >> Nothing


>>> add_first_two([1, 2, 3, 4, 5])
Just(3)

>>> add_first_two([9.0])
Nothing
```

Pattern matching is also very useful for deconstructing ADTs and assigning
their fields to temporary variables.

```python
def default_to_zero(x):
    return ~(caseof(x)
                | m(Just(m.x)) >> p.x
                | m(Nothing)   >> 0)


>>> default_to_zero(Just(27))
27


>>> default_to_zero(Nothing)
0
```

If you find pattern matching on ADTs too cumbersome, you can also use numeric
indexing on ADT fields. An `IndexError` will be thrown if you mess something
up.

```python
>>> Just(20.0)[0]
20.0

>>> Left("words words words words")[0]
'words words words words'

>>> Nothing[0]  # IndexError
```


### Typeclasses and typeclass instances


Typeclasses allow you to add additional functionality to your ADTs. Hask
implements all of the major typeclasses from Haskell (see the Appendix for a
full list) and provides syntax for creating new typeclass instances.

As an example, let's add a `Monad` instance for the `Maybe` type.  First, we
need to add `Functor` and `Applicative` instances.


```python
def maybe_fmap(maybe_value, fn):
    """Apply a function to the value inside of a (Maybe a) value"""
    return ~(caseof(x)
                | m(Nothing)   >> Nothing
                | m(Just(m.x)) >> Just(fn(p.x)))


instance(Functor, Maybe).where(
    fmap = maybe_fmap
)
```

`Maybe` is now an instance of `Functor`. This allows us to call `fmap`
and map any function of type `a -> b` into a value of type `Maybe a`.

```python
>>> times2 = (lambda x: x) ** (H/ int >> int)
>>> toFloat = float ** (H/ int >> float))

>>> fmap(Just(10), toFloat)
Just(10.0)

>>> fmap(fmap(Just(25), times2), toFloat)
Just(50.0)
```

Lots of nested calls to `fmap` get unwieldy very fast. Fortunately, any
instance of `Functor` can be used with the infix `fmap` operator, `*`. This is
equivalent to `<$>` in Haskell. Rewriting our example from above:

```python
>>> (toFloat * times2) * Just(25)
Just(50.0)

>>> (toFloat * times2) * Nothing
Nothing
```

Note that in this example we use `*` as both the function compose operator and
as `fmap`, to lift functions into a `Maybe` value. If this seems confusing,
remember that `fmap` for functions is just function composition!


Now that we have made `Maybe` an instance of `Functor`, we can make it an
instance of `Applicative` and then an instance of `Monad` by defining the
appropriate function implementations. To implement `Applicative`, we just need
to provide `pure`. To implement `Monad`, we need to provide `bind`.


```python
>>> from hask import Applicative, Monad

>>> instance(Applicative, Maybe).where(
...     pure = Just
... )

>>> instance(Monad, Maybe).where(
...     bind = lambda x, f: ~(caseof(x)
...                             | m(Just(m.a)) >> f(p.a)
...                             | m(Nothing)   >> Nothing)
... )
```

The `bind` function also has an infix form, which is `>>` in Hask.

```python
>>> f = (lambda x: Just(x + 10)) ** (H/ int >> t(Maybe, int))
>>> g = (lambda x: Just(x + 3)) ** (H/ int >> t(Maybe, int))
>>> h = (lambda _: Nothing) ** (H/ "a" >> t(Maybe, "a"))

>>> Just(3) >> f >> g
Just(16)

>>> Nothing >> f >> g
Nothing

>>> Just(3) >> f >> h >> g
Nothing
```

As in Haskell, `List` is also a monad, and `bind` for the `List` type is just
`concatMap`.

```python
>>> from Data.List import replicate
>>> L[1, 2] >> replicate(2) >> replicate(2)
L[1, 1, 1, 1, 2, 2, 2, 2]
```

You can also define typeclass instances for classes that are not ADTs:

```python
class Person(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age


instance(Eq, Person).where(
    eq = lambda p1, p2: p1.name == p2.name and p1.age == p2.age
)

>>> Person("Philip Wadler", 59) == Person("Simon Peyton Jones", 57)
False
```

If you want instances of the `Show`, `Eq`, `Read`, `Ord`, and `Bounded`
typeclasses for your ADTs, it is adviseable to use `deriving` to automagically
generate instances rather than defining them manually.


Defining your own typeclasses is pretty easy--take a look at `help(Typeclass)`
and look at the typeclasses defined in `Data.Functor` and `Data.Traversable` to
see how it's done.


### Operator sections

Hask also supports operator sections (e.g. `(1+)` in Haskell). Sections are
just `TypedFunc` objects, so they are automagically curried and typechecked.

```python
>>> from hask import __

>>> f = (__ - 20) * (2 ** __) * (__ + 3)
>>> f(10)
8172

>>> ((90/__) * (10+__)) * Just(20)
Just(3)

>>> from hask.Data.List import takeWhile
>>> takeWhile(__<5, L[1, ...])
L[1, 2, 3, 4]
```

Double sections are also supported:

```python
>>> (__+__)('Hello ', 'world')
'Hello world'

>>> (__**__)(2)(10)
1024
```

As you can see, this much easier than using `lambda` and adding a type
signature with the `(lambda x: ...) ** (H/ ...)` syntax.


### Guards

If you don't need the full power of pattern matching and just want a neater
switch statement, you can use guards. The syntax for guards is almost identical
to the syntax for pattern matching.

```python
~(guard(expr_to_test)
    | c(test_1) >> return_value_1
    | c(test_2) >> return_value_2
    | otherwise >> return_value_3
)
```

As in Haskell, `otherwise` will always evaluate to `True` and can be used as a
catch-all in guard expressions. If no match is found (and an `otherwise` clause
is not present), a `NoGuardMatchException` will be raised.

Guards will also play nicely with sections:

```python
>>> from hask import guard, c, otherwise

>>> porridge_tempurature = 80

>>> ~(guard(porridge_tempurature)
...     | c(__ < 20)  >> "Porridge is too cold!"
...     | c(__ < 90)  >> "Porridge is just right!"
...     | c(__ < 150) >> "Porridge is too hot!"
...     | otherwise   >> "Porridge has gone thermonuclear"
... )
'Porridge is just right!'
```

If you need a more complex conditional, you can always use lambdas, regular
Python functions, or any other callable in your guard condition.

```python
def examine_password_security(password):
    analysis = ~(guard(password)
        | c(lambda x: len(x) > 20) >> "Wow, that's one secure password"
        | c(lambda x: len(x) < 5)  >> "You made Bruce Schneier cry"
        | c(__ == "12345")         >> "Same combination as my luggage!"
        | otherwise                >> "Hope it's not 'password'"
    )
    return analysis


>>> nuclear_launch_code = "12345"

>>> examine_password_security(nuclear_launch_code)
'Same combination as my luggage!'
```

### Monadic error handling (of Python functions)

If you want to use `Maybe` and `Either` to handle errors raised by Python
functions defined outside Hask, you can use the decorators `in_maybe` and
`in_either` to create functions that call the original function and return the
result wrapped inside a `Maybe` or `Either` value.

If a function wrapped in `in_maybe` raises an exception, the wrapped function
will return `Nothing`. Otherwise, the result will be returned wrapped in a
`Just`.

```python
def eat_cheese(cheese):
    if cheese <= 0:
        raise ValueError("Out of cheese error")
    return cheese - 1

maybe_eat = in_maybe(eat_cheese)

>>> maybe_eat(1)
Just(0)

>>> maybe_eat(0)
Nothing
```

Note that this is equivalent to lifting the original function into the Maybe
monad. That is, we have changed its type from `function` to `a -> Maybe b`.
This makes it easier to use the convineient monad error handling style commonly
seen in Haskell with existing Python functions.

Continuing with our silly example, we can try to eat three pieces of cheese,
returning `Nothing` if the attempt was unsuccessful:

```python
>>> cheese = 10
>>> cheese_left = maybe_eat(cheese) >> maybe_eat >> maybe_eat
>>> cheese_left
Just(7)

>>> cheese = 1
>>> cheese_left = maybe_eat(cheese) >> maybe_eat >> maybe_eat
>>> cheese_left
Nothing
```

Notice that we have taken a regular Python function that throws Exceptions, and
are now handling it in a type-safe, monadic way.

The `in_either` function works just like `in_maybe`. If an Exception is thrown,
the wrapped function will return the exception wrapped in `Left`. Otherwise,
the result will be returned wrapped in `Right`.

```python
either_eat = in_either(eat_cheese)

>>> either_eat(10)
Right(9)

>>> either_eat(0)
Left(ValueError('Out of cheese error',))
```

Chained cheese-eating in the `Either` monad is left as an exercise for
the reader.

You can also use `in_maybe` or `in_either` as decorators:

```python
@in_maybe
def some_function(x, y):
    ...
```


### Standard libraries

All of your favorite functions from `Prelude`, `Data.List`, `Data.Maybe`,
`Data.Either`, `Data.Monoid`, and more are implemented too. Everything is
pretty well documented, so if you're not sure about some function or typeclass,
use `help` liberally. See the Appendix below for a full list of modules. Some
highlights:

```python
>>> from Data.List import mapMaybe
>>> mapMaybe * safe_div(12) % L[0, 1, 3, 0, 6]
L[12, 4, 2]


>>> from Data.List import isInfixOf
>>> isInfixOf(L[2, 8], L[1, 4, 6, 2, 8, 3, 7])
True
```

Hask also has wrappers some existing Python functions in TypedFunc objects, for
ease of compatibity. (Eventually, Hask will have typed wrappers for much of the
Python standard library.)

```python
>>> from hask.Prelude import flip
>>> from hask.Data.Tuple import snd
>>> from hask.Python.builtins import divmod, hex

>>> hexMod = hex * snd * flip(divmod, 16)
>>> hexMod(24)
'0x8'
```


That's all, folks!


## Appendix

**Table 1.** Overview of Hask typeclasses.

| Typeclass | Superclasses | Required functions | Optional functions | Magic Methods |
| --------- | ------------ | ------------------ | ------------------ | ------------- |
| `Show` | | `show` | | `str` |
| `Read` | | `read` | | |
| `Eq` | | `eq` | `ne` | `==`, `!=` | |
| `Ord` | `Eq` | `lt` | `gt`, `le`, `ge` | `<`, `<`, `=<`, `=>` | |
| `Enum` | | `toEnum`, `fromEnum` | `enumTo`, `enumFromTo`, `enumFromThen`, `enumFromThenTo` | |
| `Bounded` | | `minBound`, `maxBound` | | |
| `Functor` | | `fmap` | | `*` |
| `Applicative` | `Functor` | `pure` | | |
| `Monad` | `Applicative` | `bind` | | `>>` |
| `Monoid` | | `mappend`, `mempty` |  `mconcat` | `+` |
| `Foldable` | `Functor` | `foldr` | `fold`, `foldMap`, `foldr_`, `foldl`, `foldl_`, `foldr1`, `foldl1`, `toList`, `null`, `length`, `elem`, `maximum`, `minimum`, `sum`, `product` | `len` |
| `Traversable` | `Foldable`, `Functor` | `traverse` | `sequenceA`, `mapM`, `sequence` | |
| `Num` | `Show`, `Eq` | `abs`, `signum`, `fromInteger`, `negate` | | `+`, `-`, `*` |
| `Real` | `Num`, `Ord` | `toRational` | |
| `Integral` | `Real`, `Enum` | `quotRem`, `toInteger` | `quot`, `rem`, `div`, `mod`, `toInteger` | `/`, `%` |
| `Fractional` | `Num` | `fromRational`, `recip` |  | `/` |
| `Floating` | `Fractional` | `pi`, `exp`, `log`, `sin`, `cos`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `asinh`, `cosh`, `atanh` | |
| `RealFrac` | `Real`, `Fractional` | `properFraction` `truncate`, `round`, `ceiling`, `floor` |
| `RealFloat` | `Floating`, `RealFrac` | `floatRadix`, `floatDigits`, `floatRange`, `decodeFloat`, `encodeFloat`, `exponent`, `significand`, `scaleFloat`, `isNaN`, `isInfinite`, `isDenormalized`, `isNegativeZero`, `isIEEE`, `atan2` |


**Table 2.** Hask library structure.

| Module | Dependencies | Exported functions |
| ------ | ------------ | ------------------ |
| `hask` | | |
| `hask.Prelude` | `hask.lang` |
| `hask.Data.Maybe` | `hask.lang`, `hask.Data.Eq`, `hask.Data.Ord`, `hask.Data.Functor`, `hask.Control.Applicative`, `hask.Control.Monad` |
| `hask.Data.Either` | `hask.lang`, `hask.Data.Eq`, `hask.Data.Ord`, `hask.Data.Functor`, `hask.Control.Applicative`, `hask.Control.Monad` |
| `hask.Data.List` | `hask.lang`
| `hask.Data.String` | `hask.lang` | `words`, `unwords`, `lines`, `unlines` |
| `hask.Data.Tuple` | `hask.lang` | `fst`, `snd`, `swap`, `curry`, `uncurry` |
| `hask.Data.Char` | `hask.lang` | `isControl`, `isSpace`, `isLower`, `isUpper`, `isAlpha`, `isAlphaNum`, `isPrint`, `isDigit`, `isOctDigit`, `isHexDigit`, `isLetter`, `isMark`, `isNumber`, `isPunctuation`, `isSymbol`, `isSeparator`, `isAscii`, `isLatin1`, `isAsciiUpper`, `toLower`, `toUpper`, `toTitle`, `digitToInt`, `intToDigit`, `chr`, `ord` |
| `hask.Data.Eq` | `hask.lang` | `Eq` (`==`, `!=`)
| `hask.Data.Ord` | `hask.lang`, `hask.Data.Eq` | `Ord` (`>`, `<`, `>=`, `<=`), `Ordering` (`LT`, `EQ`, `GT`), `max`, `min`, `compare`, `comparing` |
| `hask.Data.Functor` | `hask.lang` | `Functor` (`fmap`, `*`),  |
| `hask.Data.Foldable` | `hask.lang` | `Foldable` (`foldr`, `foldl`, `foldl_`, `foldl1`, `foldl1_`, `foldr`, `foldr1`), `concat`, `concatMap`, `and_`, `or_`, `any`, `all`, `sum`, `product`, `minimum`, `maximum` |
| `hask.Data.Traversable` | `hask.lang`
| `hask.Data.Monoid` | `hask.lang` | `Monoid` (`mappend`, `mempty`, `mconcat`) |
| `hask.Data.Ratio` | `hask.lang` | `Integral`, `Ratio` (`R`), `Rational`, `toRatio`, `toRational`, `numerator`, `denominator` |
| `hask.Data.Num` | `hask.lang` |
| `hask.Control.Applicative` | `hask.lang` | `Applicative` |
| `hask.Control.Monad` | `hask.lang` |
| `hask.Python.builtins` | `hask.lang` | `callable`, `cmp`, `delattr`, `divmod`, `frozenset`, `getattr`, `hasattr`, `hash`, `hex`, `isinstance`, `issubclass`, `len`, `oct`, `repr`, `setattr`, `sorted`, `unichr` |
| `hask.lang` |
| `hask.lang.hindley_milner` |
| `hask.lang.type_system` | `hask.lang.hindley_milner`
| `hask.lang.syntax` | `hask.lang.type_system`
| `hask.lang.typeclasses` | `hask.lang.type_system`, `hask.lang.syntax`
| `hask.lang.lazylist` | `hask.lang.type_system`, `hask.lang.hindley_milner`, `hask.lang.syntax`, `hask.lang.typeclasses` | `L`, `List` |
