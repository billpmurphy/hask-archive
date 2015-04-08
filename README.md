***Notes yall***

This is still in "throw everything at the wall" phase. Goal here is to push the
boundaries as far as physically possible, to get as close to Haskell as Python
can go, then strip out all the hideous hacks and see if there's an actually
useful Haskell-features-and-syntax-that-aren't-ugly-in-Python kinda library in
there.

Top priority:
* change this absolutely awful name

Things that are reasonably well explored so far, but do not have definitive
implementation details:
* guards - is there a way to clean up the syntax?
* Maybe - needs work on decorator/wrapper, reconsider design choices
* Either - needs work on decorator/wrapper, reconsider design choices
* infix function composition with "\*" - works great, just need better way of
  having curried functions
* reimplementing Haskell standard library functions
* using regular classes to represent the functor/applicative/monad heirarchy -
  not sure if this is the way to go

Things that need to be explored more, in importance order:
* currying/composition/lambda syntax - study
  [fn.py](https://github.com/kachayev/fn.py), because their implementation is
  nice (this is crucial, need this to fix up Maybe/Either monad wrappers, and
  do a lot of other stuff). might end up mostly ripping it off, although I
  think there are some things we can improve
* immutable data strucures - again look at fn.py, but I think we can do better
  here. would be nice to have an immutable linked list similar to fn.py, and
  also a lazy list stream datatype built out of LLs
* typeclasses/type heirarchy - must be some better way of doing this. `abc`
  module hacks maybe?
* ADTs - is there some way to do this metaclasses? metaclasses that represent
  Sum/Product, that can turn strings into a bunch of classes that represents an
  ADT?
* pattern matching (case of) - is there a better way of handling local binidng
  that horrid global state? in general, need to clean this filth up
* types and type assertions - ~~is there some way to abuse decorators to do this?
  or the function docstring? might want to look around~~ decorators are the way to go - would be awesome to implement full Hindley-Milner in python
* port more Haskell standard libraries
* other monads/functors
* immutable variables - can we mess with `globals()` to prevent regular assignment?
* pattern matching in regular assignment
* tail call optimization - again, read fn.py's decorator
* arrows


Key features of Haskell I am forgetting:
* ???????


(Some of the) things that currently work and look pretty good:

Maybe

```python
>>> from pythaskell.types import Just, Nothing

>>> Nothing
Nothing

>>> Just(1)
Just(1)

>>> Just("hello")
Just(hello)

>>> Just("hello") * (lambda x: x + " world")  # fmap
Just(hello world)

>>> Nothing * (lambda x: x + " world")
Nothing

>>> Just(1) >> (lambda x: Just(x + 1)) >> (lambda x: Just(x + 1)) # bind
Just(3)

>>> Nothing >> (lambda x: Just(x + 1)) >> (lambda x: Just(x + 1))
Nothing

>>> from pythaskell.data.maybe import catMaybes, fromJust

>>> catMaybes([Just(1), Just(2), Nothing, Just(4)])
[Just(1), Just(2), Just(4)]

>>> fromJust(Just(4))
4
```

Guards

```python
>>> from pythaskell.syntax import guard, c, otherwise

>>> a = 8
>>> ~(guard(a)
...     | c(lambda x: x < 5)  >> "a is < 5"
...     | c(lambda x: x < 10) >> "a is < 10"
...     | otherwise           >> "a is huge"
... )
'a is < 10'

>>> ~(guard(10)
        | c(lambda x: x < 5) >> "x is < 5")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "pythaskell/syntax.py", line 159, in __invert__
    raise NoGuardMatchException("No match found in guard")
pythaskell.syntax.NoGuardMatchException: No match found in guard
```

(will do demos of the rest when I'm less lazy/busy)
