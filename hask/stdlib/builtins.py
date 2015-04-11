from ..lang.typeclasses import Show
from ..lang.typeclasses import Eq
from ..lang.typeclasses import Num


# Builtin type typeclass instances

Show.register(int)
Show.register(float)
Show.register(complex)

Eq.register(int)
Eq.register(float)
Eq.register(complex)

Num.register(int)
Num.register(float)
Num.register(complex)
