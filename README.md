[![Build Status](https://magnum.travis-ci.com/billpmurphy/pythaskell.svg?token=ReCFhAz7SQAeN6Fi4dBx&branch=master)](https://magnum.travis-ci.com/billpmurphy/pythaskell)


Remaining TODOs:
* Fix TypedFunc so it actually typechecks each argument, and is curried; then
  kill hof.py
* Change type inference engine so that it is aware of typeclasses
* Write rest of Data.List and Prelude, and document everything undocumented
* Final refactor of everything
* Write rest of README
* Write tests for everything
* ???
* Profit


# Hask

Wish you could use all those elegant Haskell features in Python? All you have
to do is `import hask`.

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
    * Typeclasses from the Haskell `base` libraries, including `Functor`,
      `Applicative`, `Monad`, `Enum`, `Num`, and all the rest
    * Algebraic datatypes from the Haskell `Prelude`, including `Maybe` and
      `Either`
    * Standard library functions from `base`, including all functions from
      `Prelude`, `Data.List`, `Data.Maybe`, and more


Features not yet implemented, but coming soon:

* More (and better) documentation
* Better support for polymorphic return values/type defaulting
* Better support for lazy evaluation (beyond just the `List` type)
* More of the Haskell standard library (`Control.*` libraries)
* Monadic, lazy I/O
* QuickCheck (property-based testing)


## Installation

1) `git clone https://github.com/billpmurphy/hask`
2) `python setup.py install`

To run the tests: `python tests.py`.


## Introduction

### Defining Abstract Data Types

```python
from hask import data, d, deriving
from hask import Read, Show, Eq, Ord

Maybe, Nothing, Just =\
    data.Maybe("a") == d.Nothing | d.Just("a") & deriving(Read, Show, Eq, Ord)
```

Let's break this down a bit. The syntax for defining a new type constructor is:

```python
```

This defines a new algebraic datatype with type parameters.

To define data constructors for this type, use `d.` The name of the data
constructor goes first, followed by its fields. Multiple data constructors
should be separted by `|`. If your data constructor has no fields, you can omit
`d`. There is no limit to the number of data constructors you can define, and
there is no limit to the number of fields that each data constructor can have.


```python
d.DC1("a", "b")

d.DC1("a", "b")
```

To automagically derive typeclass instances for the new ADT, just add `&
deriving(...typeclasses...)` after the data constructor declarations.
Currently, the only typeclasses that can be derived are `Eq`, `Show`, `Read`,
`Ord`, and `Bounded`.


Putting it all together, here is the definition of `Either`:

```python
Either, Left, Right =\
    data.Either("a", "b") == d.Left("a") | d.Right("b") & deriving(Read, Show, Eq)
```

We can now use the data constructors defined in a `data` statement to create instances of our new types. If our data constructor takes no arguments, we can use it just like a variable.

```python
>>> Just(10)
Just(10)

>>> Nothing
Nothing


>>> Just(Just(10))
Just(Just(10))

>>> Left(1)
Left(1)


>>> Right("a")
Right("a")
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
```


### Pattern matching

Now that we have our `Maybe` type, let's take it for a spin. Suppose we want to implement a function `safeDiv`, which attempt to divide two values


### Typeclasses and typeclass instances


```python
>>> def maybe_fmap(maybe_value, fn):
>>>     return ~(caseof(maybe_value)
...         | m(Nothing)   >> Nothing
...         | m(Just(m.x)) >> Just(fn(p.x)))

```

```python
>>> instance(Functor, Maybe).where(
...     fmap = maybe_fmap
...  )
```

```python
>>> maybe_fmap(Just(10), lambda x: x * 2)
Just(20)
```

We can now make `Maybe` an instance of `Functor`. This allows us to call `fmap`
and map any function of type `a -> b` into a value of type `Maybe a`.

```python
>>> Functor(Maybe, maybe_fmap)

>>> toFloat = float ** (H/ int >> float))
>>> fmap(Just(10), toFloat)
Just(10.0)

>>> fmap(fmap(Just(25), times2), toFloat)
Just(50.0)
```

Lots of nested calls to `fmap` get unwieldy very fast. Fortunately, any
instance of `Functor` can be used with the infix `fmap` operator, `*`. This is
equivalent to `<*>` in Haskell. Rewriting our example from above:

```python
>>> Just(25) * times2 * toFloat
Just(50.0)

>>> Nothing * times2 * toFloat
Nothing
```

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

Of course, `bind` also has an infix form, which is `>>` in Hask.

```python
>>> f = (lambda x: x + 10)
>>>
>>> h = (lambda _: Nothing) ** (H/ "a" >> Maybe "a")

>>> Just(3) >> f >> g
Just(16)

>>> Nothing >> f >> g
Nothing

>>> Just(3) >> f >> h >> g
Nothing
```

### Other fun stuff


#### List type



#### Operator sections

Hask also supports operator sections (e.g. `(1+)` in Haskell). Sections are
just `TypedFunc` objects, so they are automagically curried and typechecked.

```python
>>> from hask import __

>>> f = (__ - 20) * (2 ** __) * (__ + 3)
>>> f(10)
8172

>>> Just(20) * (__+10) * (90/__)
Just(3)
```

Double sections are also supported:

```python
>>> (__+__)('Hello ', 'world')
'Hello world'

>>> (__**__)(2)(10)
1024
```

#### Guards

If you don't need the full power of pattern matching and just want a neater
switch statement, you can use guards. The syntax for guards is as follows:

```python
~(guard(<expr to test>)
    | c(<test 1>) >> <return value 1>
    | c(<test 2>) >> <return value 2>
    | otherwise   >> <return value 3>
)
```

As in Haskell, `otherwise` will always evaluate to `True` and can be used as a
catch-all in guard statements. If no match is found (and an `otherwise` clause
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
>>> def examine_password_security(password):
...     analysis = ~(guard(password)
...         | c(lambda x: len(x) > 20) >> "Wow, that's one secure password"
...         | c(lambda x: len(x) < 5)  >> "You made Bruce Schneier cry"
...         | c(__ == "12345")         >> "Same combination as my luggage!"
...         | otherwise                >> "Hope it's not `password`"
...     )
...     return analysis
...

>>> nuclear_launch_code = "12345"

>>> examine_password_security(nuclear_launch_code)
'Same combination as my luggage!'
```

#### Monadic error handling (of Python functions)

If you want to use `Maybe` and `Either` to handle errors raised by Python
functions defined outside Hask, you can use the decorators `in_maybe` and
`in_either` to create functions that call the original function and return the
result inside the `Maybe` or `Either` monads.

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
monad. That is, we have changed its type from `function` to `a -> Maybe b`. This
makes it easier to implement the convineient monad error handling commonly seen
in Haskell with your existing Python functions.

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

Similarly, if a function wrapped in `in_either` raises an exception, the
wrapped function will return the exception wrapped in `Left`. Otherwise, the
result will be returned wrapped in `Right`.

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
@in_either
def picky_add_10(n):
    assert type(n) == int, "not an int!"

    if n < 0:
        raise ValueError("Too low!")

    return n + 10


>>> picky_add_10("hello")
Left(AssertionError('not an int!',))

>>> picky_add_10(-10)
Left(ValueError('Too low!',))

>>> picky_add_10(1)
Right(11)
```


#### Standard libraries

All of your favorite functions from `Prelude`, `Data.List`, `Data.Maybe`,
`Data.Either`, `Data.Monoid`, and more are implemented too. Some highlights:

```python
```


## Contribute

Contributions are always welcome! Feel free to submit a pull request, open an
issue, or email me. In the spirit of this project, wild experimentation is
encouraged.


## Why did you make this?

It was fun!
