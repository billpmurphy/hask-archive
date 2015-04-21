[![Build Status](https://magnum.travis-ci.com/billpmurphy/pythaskell.svg?token=ReCFhAz7SQAeN6Fi4dBx&branch=master)](https://magnum.travis-ci.com/billpmurphy/pythaskell)


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
* the LazyList - tests are failing, figure out why and fix it. Also, do some
  profiling and improve efficiency of some operations *(yo max you got this)*
* HOF - needs more work, coming along though
* ADTs - work on this after type system is built out
* pattern matching (case of) - is there a better way of handling local binidng
  that horrid global state? in general, need to clean this filth up
* immutable data strucures - again look at fn.py, but I think we can do better
  here.
* laziness everywhere - can generators/coroutines-made-from-generators do this?
* immutable variables - can we mess with `globals()` to prevent regular
  assignment? or use coroutines somehow?
* pattern matching in regular assignment
* other monads/functors
* tail call optimization - again, read fn.py's decorator
* port more Haskell standard libraries (probably want to wait for later to do
  this)
* arrows


Key features of Haskell I am forgetting:
* ???????


Haskell API status table

| Thing       | Status |
| :---------- | :----: |
| Typeclasses |        |
| ----------- | ------ |
| Show        | x      |
| Read        | ?      |
| Eq          | x      |
| Ord         | x      |
| Enum        |        |
| Bounded     |        |
| Num         | part   |
| Integral    | ?      |
| Functor     | x      |
| Applicative | x      |
| Monad       | x      |
| Foldable    |        |
| Traversable | x      |
| Ix          | x      |
| _Iterator_  | x      |
| Prelude     |        |
| ----------- | ------ |
