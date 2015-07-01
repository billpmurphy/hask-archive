from ..lang import H


# Typed wrappers for builtin Python functions.
# This makes it easier to chain lots of things together in function composition
# without having to manually add type signatures to Python builtins.


cmp = cmp ** (H/ "a" >> "a" >> int)
divmod = divmod ** (H/ "a" >> "b" >> ("c", "c"))
frozenset = frozenset ** (H/ "a" >> frozenset)
getattr = getattr ** (H/ "a" >> str >> "b")
hasattr = hasattr ** (H/ "a" >> str >> bool)
hash = hash ** (H/ "a" >> int)
hex = hex ** (H/ int >> str)
len = len ** (H/ "a" >> int)
oct = oct ** (H/ int >> str)
repr = repr ** (H/ "a" >> str)
sorted = sorted ** (H/ "a" >> list)
