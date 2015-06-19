[![Build Status](https://magnum.travis-ci.com/billpmurphy/pythaskell.svg?token=ReCFhAz7SQAeN6Fi4dBx&branch=master)](https://magnum.travis-ci.com/billpmurphy/pythaskell)

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

* More of the Haskell standard library (`Control.*` libraries)
* QuickCheck (property-based testing)
* Better support for polymorphic return types
* Monadic I/O


## Installation

1) `git clone https://github.com/billpmurphy/hask`
2) `python setup.py install`

To run the tests: `python tests.py`.


## Introduction

### Building 'Maybe'

```python
from hask import data, d, deriving
from hask import Read, Show, Eq, Ord

data . Maybe("a") == d.Nothing | d.Just("a") & deriving(Read, Show, Eq, Ord)
```

Let's break this down a bit. The syntax for defining a new type constructor is:

```python
data . Typename("typearg1", "typearg2")
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
and `Ord`.


Putting it all together, here is an sample implementation of `Either`:

```python
data . Either("a", "b") == d.Left("a") | d.Right("b") & deriving(Read, Show, Eq)
```

We can now use the data structures defined in a `data` statement to create instances of our new types. If our data structure takes no arguments, we can use it just like a variable.

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

#### Operator sections

Hask also supports operator sections (e.g. `(1+)` from Haskell), which create
`Func` objects for ease of composition.

```python
>>> from hask import __

>>> f = (__ - 20) * (2 ** __) * (__ + 3)
>>> f(10)
8172
```

Sections are just `TypedFunc` objects, so they are automagically curried and
typechecked. Double sections are also supported:

```python
>>> (__+__)(1, 2)
3
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
If no match is found (and an `otherwise` clause is not present), a
`NoGuardMatchException` will be raised. Guards will also play nicely with
sections:

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

If you need a more complex conditional, you can always use lambdas or functions
in your guard conditions.

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

#### Monadic error handling (of existing Python functions)

If you want to use `Maybe` and `Either` (or your own error-handling monad) to
handle errors raised by Python functions defined outside Hask, you can use the
decorators `in_maybe` and `in_either` to create functions that call the
original function and return the result inside the `Maybe` or `Either` monads.

```python
def a_problematic_function(cheese):
    if cheese <= 0:
        raise ValueError("Out of cheese error")
    return cheese - 1
```

If a function wrapped in `in_maybe` raises an exception, the wrapped function
will return `Nothing`. Otherwise, the result will be returned wrapped in a
`Just`.

```python
maybe_problematic = in_maybe(a_problematic_function)


>>> maybe_problematic(1)
Just(0)

>>> maybe_problematic(0)
Nothing
```

If a function wrapped in `in_either` raises an exception, the wrapped function
will return the exception wrapped in `Left`. Otherwise, the result will be
returned wrapped in `Right`.

```python
either_problematic = in_either(a_problematic_function)


>>> either_problematic(10)
Right(9)

>>> either_problematic(0)
Left(ValueError('Out of cheese error',))
```


You can also use `in_maybe` or `in_either` as decorators:

```python
@in_either
def my_fn_that_raises_errors(n):
    assert type(n) == int, "not an int!"

    if n < 0:
        raise ValueError("Too low!")

    return n + 10


>>> my_fn_that_raises_errors("hello")
Left(AssertionError('not an int!',))

>>> my_fn_that_raises_errors(-10)
Left(ValueError('Too low!',))

>>> my_fn_that_raises_errors(1)
Right(11)
```


#### Standard libraries

All of your favorite functions from `Prelude`, `Data.List`, `Data.Maybe`,
`Data.Either`, `Data.String`, and `Data.Tuple`, are implemented
too. Some highlights:


```python
```


## Contribute

Contributions are always welcome! Feel free to submit a pull request, open an
issue, or email me.


## Why did you make this?

It was fun!
