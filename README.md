[![Build Status](https://magnum.travis-ci.com/billpmurphy/pythaskell.svg?token=ReCFhAz7SQAeN6Fi4dBx&branch=master)](https://magnum.travis-ci.com/billpmurphy/pythaskell)

# Hask

Wish you could use all those elegant Haskell features in Python? All you have
to do is `import hask`!

Hask is a pure-Python library that mimics most of the core language tools from
Haskell, including:

* Python port of Haskell's type system that supports type checking, function
  type signatures, algebraic data types, and typeclasses
* Easy creation of new algebraic datatypes and typeclasses (immutable, of
  course)
* Pattern matching
* Automagical function currying/partial application
* Typeclasses from the Haskell `base` libraries, including `Functor`, `Monad`,
  and all the rest
* Algebraic datatypes from the Haskell `Prelude`, including `Maybe` and `Either`
* Efficient, immutable, lazily evaluated `List` type with Haskell-style list
  comprehensions
* Easier function composition and application, operator sections, guards, and
  other nifty control flow tools
* Full Python port of (some of) the standard libraries from Haskell's `base`,
  including `Prelude`, `Control.Monad`, `Data.List`, and many more


## Installation

Just `git clone https://github.com/billpmurphy/hask` and then
`python setup.py install`.

To run the tests, just `python tests.py`.


## Introduction

### Building 'Maybe'

```python
from hask import data, d, deriving
from hask import Read, Show, Eq, Ord

data("Maybe", "a") == "Nothing" | d("Just", "a") \
                      & deriving(Read, Show, Eq, Ord)
```

Let's break this down a bit. The syntax for defining a new type constructor is:

```python
data("Type name", ...type arguments...)
```

This defines a new datatype (i.e., a class) with type parameters.

To define data constructors for this type, use `d`. The name of the data
constructor goes first, followed by its fields. Multiple data constructors
should be separted by `|`. If your data constructor has no fields, you can omit
`d`. There is no limit to the number of data constructors you can define, and
there is no limit to the number of fields that each data constructor can have.


```python
d("Data constructor 1", "arg1") | d("Data constructor 2", "arg1")

d("DC1", "arg1") | "DC2" | d("DC3, "arg1", "arg2", "arg3")

```


To automagically derive typeclass instances for the new ADT, just add `&
deriving(...typeclasses...)` after the data constructor declarations.
Currently, the only typeclasses that can be derived are `Eq`, `Show`, `Read`,
and `Ord`.


Putting it all together, here is an sample implementation of `Either`:

```python
data("Either", "a", "b") == d("Left", "a") | d("Right", "b") \
                            & deriving(Read, Show, Eq)
```

We can now use the data structures defined in a `data` statement to create instances of our new types. If our data structure takes no arguments, we can use it just like a variable.

```python
>>> Just(10)
Just(10)

>>> Nothing
Nothing


>>> Just(Just(10))
Just(Just(10))

>>> L(1)
L(1)


>>> R("a")
R("a")
```

You can view the type of an object with `_t` (equivalent to `:t` in ghci).

```python
>>> from hask import _t

>>> _t(1)
int

>>> _t(Just("soylent green")
Maybe str
```

```python
>>> def maybe_fmap(maybe_value, fn):
>>>     result =  ~(caseof(maybe_value)
...         | Nothing         >> Nothing
...         | m(Just, p("x")) >> Just(fn(p("x")))
...     )
...     return result

>>> maybe_fmap(Just(10), lambda x: x * 2)
Just(20)

>>> maybe_fmap(Nothing, lambda x: x * 2)
Nothing
```

We can now make `Maybe` an instance of `Functor`. This will modify the class
`Maybe`, adding a method called `fmap` that will be set equal to our
`maybe_fmap` function.

```python
>>> Functor(Maybe, maybe_fmap)

>>> Just(10).fmap(float)
Just(10.0)

>>> Just(10).fmap(float).fmap(lambda x: x / 2)
Just(5.0)
```

Any instance of `Functor` can be used with the infix `fmap` operator, `*`:

```python
>>> Just("hello") * (lambda x: x.upper()) * (lambda x: x + "!")
Just('HELLO!')
```

If we have an instance of `Functor`, we can make it an instance of
`Applicative` and then an instance of `Monad` by defining the appropriate
methods. To implement `Applicative`, we just need to provide `pure`, which
wraps a value in our type. To implement `Monad`, we need to provide `bind`.

```python
>>> from hask import Applicative, Monad

>>> Applicative(Maybe, lambda x: Just(x))

>>> def maybe_bind(maybe_value, fn):
...     return ~(caseof(maybe_value)
...         | Nothing         >> Nothing
...         | m(Just, p("x")) >> fn(p("x")))
...

>>> Monad(Maybe, maybe_bind)
```

Of course, `bind` also has an infix form, which is `>>` in Hask.

```python
>>> f = lambda x: Nothing if x > 5 else Just(x + 5)
>>> g = lambda x: Nothing if x < 1 else Just(2 * x)
>>> h = lambda x: Nothing if x > 0 else Just(10)

>>> Just(3) >> f >> g
Just(16)

>>> Nothing >> f >> g
Nothing

>>> Just(3) >> f >> h >> g
Nothing
```

### Other fun stuff

Hask also supports operator sections (e.g. `(1+)` from Haskell), which create
`Func` objects for ease of composition.

```python
>>> from hask import __

>>> f = (__ - 20) * (2 ** __) * (__ + 3)
>>> f(10)
8172
```


If you don't need the full power of pattern matching and just want a neater
switch statement, you can use guards, which also happen to play nicely with
sections.

```python
>>> from hask import guard, c, otherwise

>>> porridge_tempurature = 80

>>> ~(guard(porridge_tempurature)
...     | c(__ < 20)  >> "Porridge is too cold!"
...     | c(__ < 90)  >> "Porridge is just right!"
...     | c(__ < 150) >> "Porridge is too hot!"
...     | otherwise() >> "Porridge has gone thermonuclear"
... )
'Porridge is just right!'
```

If no match is found (and an `otherwise()` clause is not present), a
`NoGuardMatchException` will be raised. For more complex guards, you can also
use lambdas or functions in your guard conditions.

```python
>>> def examine_password_security(password):
...     analysis = ~(guard(password)
...         | c(lambda x: len(x) > 20) >> "Wow, that's one secure password"
...         | c(lambda x: len(x) < 5)  >> "You made Bruce Schneier cry"
...         | c(__ == "12345")         >> "Same combination as my luggage!"
...         | otherwise()              >> "Hope it's not `password`"
...     )
...     return analysis
...

>>> nuclear_launch_code = "12345"

>>> examine_password_security(nuclear_lanch_code)
'Same combination as my luggage!'
```

All of your favorite functions from `Prelude`, `Data.List`, `Data.Maybe`, `Data.Either`, `Data.String`, `Data.Tuple`, and `Control.Monad` are implemented too.


```python
```

-------------------------------------------


***Notes y'all***

This is still in "throw everything at the wall" phase. Goal here is to push the
boundaries as far as physically possible, to get as close to Haskell as Python
can go, then strip out all the hideous hacks and see if there's an actually
useful Haskell-features-and-syntax-that-aren't-ugly-in-Python kinda library in
there.

What needs work:
* the type system. this is #1 priority. need to design datatypes to represent
  higher-kinded types, type signatures, and do some basic typechecking to get
  things rolling, just to make sure no redesign of typeclasses is needed
* ADTs - work on this after type system is built out
* pattern matching (case of) - is there a better way of handling local binidng
  that horrid global state? in general, need to clean this filth up
* laziness everywhere - can generators/coroutines-made-from-generators do this?
* immutable variables - can we mess with `globals()` to prevent regular
  assignment? or use coroutines somehow?
* pattern matching in regular assignment
* other monads/functors
* tail call optimization - again, read fn.py's decorator
* port more Haskell standard libraries (probably want to wait for later to do
  this)
* arrows


More notes:

`import hask` should give you everything in the language (including all
typeclasses) plus everything in the Prelude. Therefore, you can do `hask.map`
but not `hask.permutations`. To import things in the Base libraries that are
not also in the Prelude, use `from hask import Data` and then
`Data.List.permutations`.


Add more corner case tests for LazyList indexing.


Haskell API status table

| Haskell Feature        | Pythaskell Name | Status |
| :--------------------- | :-------------- | :----: |
| *Syntax*               |                 |        |
| type signatures        | sig             | part   |
| pattern matching (case)| caseof          | idea   |
| data (defining ADTs)   | data            | part   |
| type (type synonym)    |                 | ?      |
| newtype (type wrapper) |                 | nix    |
| list comprehensions    | L (see below)   | part   |
| slicing (e.g. `(+1)`)  | `(__+1)`        |        |
| guards                 | guard           | good   |
| *Typeclasses*          |                 |        |
| Show                   | Show            | good   |
| &nbsp;&nbsp;show       | &nbsp;&nbsp;show|        |
| Read                   |                 | ?      |
| Eq                     | Eq              | good   |
| Ord                    | Ord             | good   |
| Enum                   | Enum            |        |
| Bounded                | Bounded         |        |
| Num                    | Num             | part   |
| Integral               |                 | ?      |
| Fractional             |                 | ?      |
| Floating               |                 | ?      |
| RealFloat              |                 | ?      |
| Real                   |                 | ?      |
| RealFrac               |                 | ?      |
| Functor                | Functor         | good   |
|   fmap                 |   fmap          | good   |
| Applicative            | Applicative     | good   |
|   pure                 |   pure          | good   |
| Monad                  | Monad           | good   |
|   >>=                  | >> / bind       | good   |
| Foldable               | Foldable        |        |
| Traversable            | Traversable     | good   |
| Ix                     | Ix              | good   |
|                        | _Iterator_      | good   |
| *Prelude*              |                 |        |
|                        |                 |        |
| *Control.Applicative*  |                 |        |
|                        |                 |        |
| *Control.Monad*        |                 |        |
| >>=                    | >>              | good   |
| >>                     |                 | ?      |
| return                 | pure            | import |
| fail                   |                 |        |
| MonadPlus              |                 |        |
|   mzero                |                 |        |
|   mplus                |                 |        |
| mapM                   |                 |        |
| mapM\_                 |                 |        |
| forM                   |                 |        |
| forM\_                 |                 |        |
| sequence               |                 |        |
| sequence\_             |                 |        |
| =<<                    |                 |        |
| >=>                    |                 |        |
| forever                |                 |        |
| void                   |                 |        |
| join                   |                 |        |
| msum                   |                 |        |
| mfilter                |                 |        |
| filterM                |                 |        |
| mapAndUnzipM           |                 |        |
| zipWithM               |                 |        |
| zipWithM\_             |                 |        |
| foldM                  |                 |        |
| foldM\_                |                 |        |
| replicateM             |                 |        |
| replicateM\_           |                 |        |
| guard                  |                 |        |
| when                   |                 |        |
| unless                 |                 |        |
| liftM                  |                 |        |
| liftM2 .. liftM5       |                 |        |
| ap                     |                 |        |
| <\$!>                  |                 |        |
| *Data.Either*          |                 |        |
| Either                 | Either          |        |
| Left a                 | Left(a)         |        |
| Right a                | Right(a)        |        |
| either                 |                 |        |
| lefts                  |                 |        |
| rights                 |                 |        |
| isLeft                 |                 |        |
| isRight                |                 |        |
| partitionEithers       |                 |        |
| *Data.List*            |                 |        |
| ++                     |                 |        |
| head                   |                 |        |
| last                   |                 |        |
| tail                   |                 |        |
| init                   |                 |        |
| uncons                 |                 |        |
| null                   |                 |        |
| length                 |                 |        |
| map                    |                 |        |
| reverse                |                 |        |
| intersperse            |                 |        |
| intercalate            |                 |        |
| transpose              |                 |        |
| subsequences           |                 |        |
| permutations           |                 |        |
| foldl                  |                 |        |
| foldl'                 |                 |        |
| foldl1                 |                 |        |
| foldr                  |                 |        |
| foldr1                 |                 |        |
| concat                 |                 |        |
| and                    |                 |        |
| or                     |                 |        |
| any                    |                 |        |
| all                    |                 |        |
| sum                    |                 |        |
| product                |                 |        |
| maximum                |                 |        |
| minimum                |                 |        |
| scanl                  |                 |        |
| scanl'                 |                 |        |
| scanl1                 |                 |        |
| scanr                  |                 |        |
| scanr1                 |                 |        |
| mapAccumL              |                 |        |
| mapAccumR              |                 |        |
| iterate                |                 |        |
| repeat                 |                 |        |
| replicate              |                 |        |
| cycle                  |                 |        |
| unfoldr                |                 |        |
| take                   |                 |        |
| drop                   |                 |        |
| splitAt                |                 |        |
| takeWhile              |                 |        |
| dropWhile              |                 |        |
| dropWhileEnd           |                 |        |
| span                   |                 |        |
| break                  |                 |        |
| stripPrefix            |                 |        |
| group                  |                 |        |
| inits                  |                 |        |
| tails                  |                 |        |
| isPrefixOf             |                 |        |
| isSuffixOf             |                 |        |
| isInfixOf              |                 |        |
| isSubsequenceOf        |                 |        |
| elem                   |                 |        |
| notElem                |                 |        |
| lookup                 |                 |        |
| find                   |                 |        |
| filter                 |                 |        |
| partition              |                 |        |
| !!                     |                 | python |
| elemIndex              |                 |        |
| elemIndicies           |                 |        |
| findIndex              |                 |        |
| findIndicies           |                 |        |
| zip                    |                 |        |
| zip3 .. zip7           |                 |        |
| zipWith                |                 |        |
| zipWith3 .. zipWith7   |                 |        |
| unzip                  |                 |        |
| unzip3 .. unzip7       |                 |        |
| lines                  | lines           | import |
| words                  | words           | import |
| unlines                | unlines         | import |
| unwords                | unwords         | import |
| nub                    |                 |        |
| delete                 |                 |        |
| \\\\                   |                 |        |
| union                  |                 |        |
| intersect              |                 |        |
| sort                   |                 |        |
| sortOn                 |                 |        |
| insert                 |                 |        |
| nubBy                  |                 |        |
| deleteBy               |                 |        |
| deleteFirstBy          |                 |        |
| unionBy                |                 |        |
| intersectBy            |                 |        |
| groupBy                |                 |        |
| sortBy                 |                 |        |
| insertBy               |                 |        |
| maximumBy              |                 |        |
| minimumBy              |                 |        |
| genericLength          |                 | nix    |
| genericTake            |                 | nix    |
| genericDrop            |                 | nix    |
| genericSplitAt         |                 | nix    |
| genericIndex           |                 | nix    |
| genericReplicate       |                 | nix    |
| *Data.Maybe*           |                 |        |
| Maybe                  | Maybe           | import |
| Nothing                | Nothing         | import |
| Just a                 | Just(a)         | import |
| maybe                  | maybe           |        |
| isJust                 | isJust          |        |
| isNothing              | isNothing       |        |
| fromJust               | fromJust        |        |
| fromMaybe              | fromMaybe       |        |
| listToMaybe            | listToMaybe     |        |
| maybeToList            | maybeToList     |        |
| catMaybes              | catMaybes       |        |
| mapMaybe               | mapMaybe        |        |
| *Data.String*          |                 |        |
| lines                  | lines           |        |
| words                  | words           |        |
| unlines                | unlines         |        |
| unwords                | unwords         |        |
| *Data.Tuple*           |                 |        |
| fst                    | fst             |        |
| snd                    | snd             |        |
| curry                  | curry           |        |
| uncurry                | uncurry         |        |
| swap                   | swap            |        |
