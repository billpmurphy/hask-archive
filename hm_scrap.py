

#==================================================================#
# Example code to exercise the above


def tryExp(env, node):
    """Try to evaluate a type printing the result or reporting errors.

    Args:
        env: The type environment in which to evaluate the expression.
        node: The root node of the abstract syntax tree of the expression.

    Returns:
        None
    """
    print(str(node) + " :: ", end=' ')
    try:
        t = analyze(node, env)
        print(str(t))
    except TypeError as e:
        print(e)


def main():
    """The main example program.

    Sets up some predefined types using the type constructors TypeVariable,
    TypeOperator and Function.  Creates a list of example expressions to be
    evaluated. Evaluates the expressions, printing the type or errors arising
    from each.

    Returns:
        None
    """
    # some basic types and polymorphic typevars
    var1 = TypeVariable()
    var2 = TypeVariable()
    var3 = TypeVariable()
    var4 = TypeVariable()
    Pair = TypeOperator("*", (var1, var2))
    Bool = TypeOperator(bool.__name__, [])
    Integer = TypeOperator(int.__name__, [])
    NoneT = TypeOperator("None", [])

    # toy environment
    my_env = {"pair" : Function(var1, Function(var2, Pair)),
                "true"   : Bool,
                None   : NoneT,
                "id"   : Function(var4, var4),
                "cond" : Function(Bool, Function(var3,
                            Function(var3, var3))),
                "zero" : Function(Integer, Bool),
                "pred" : Function(Integer, Integer),
                "times": Function(Integer,
                            Function(Integer, Integer)),
                4      : Integer,
                1      : Integer, }

    pair = App(App(Var("pair"), App(Var("f"), Var(1))),
                                  App(Var("f"), Var("true")))
    compose = Lam("f", Lam("g", Lam("arg", App(Var("g"), App(Var("f"), Var("arg"))))))


    examples = [

            # Should fail:
            # fn x => (pair(x(3) (x(true)))
            Lam("x",
                App(
                    App(Var("pair"),
                        App(Var("x"), Var(4))),
                    App(Var("x"), Var("true")))),

            # pair(f(3), f(true))
            App(
                App(Var("pair"), App(Var("f"), Var(4))),
                App(Var("f"), Var("true"))),

            # let f = (fn x => x) in ((pair (f 4)) (f true))
            Let("f", Lam("x", Var("x")), pair),

            # fn f => f f (fail)
            Lam("f", App(Var("f"), Var("f"))),

            # let g = fn f => 5 in g g
            Let("g",
                Lam("f", Var(4)),
                App(Var("g"), Var("g"))),

            # example that demonstrates generic and non-generic variables:
            # \g -> let f = (\x -> g) in pair (f 4, f "true")
            Lam("g",
                   Let("f",
                       Lam("x", Var("g")),
                       App(
                            App(Var("pair"),
                                  App(Var("f"), Var(4))
                            ),
                            App(Var("f"), Var("true"))))),


            # Function composition
            # fn f (fn g (fn arg (f g arg)))
            Lam(Var("a"), Var(4)),
            Lam(Var("a"), Lam(Var("b"), Var(4))),
            compose,
            App(App(compose, Var("id")), Var("id")),
            Var("id"),
            Var("a"),
            Var(4),
            App(Var("pred"), Var(1)),
            App(Var("pred"), Var("a")),
            Lam("a", Lam("b", Lam("c", Lam("d", Var(None))))),
            App(Var("times"), Var(1)),
            App(Var("times"), Var("true")),
    ]

    for example in examples:
        tryExp(my_env, example)




