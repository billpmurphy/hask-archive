import re
from collections import defaultdict

# some static typing ideas

def t(obj):
    """
    Return the type of an object.
    """
    return obj.__type__() if hasattr(obj, "__type__") else type(obj)


class TypeStringException(Exception):
    pass


class TypeSig(object):
    def __init__(self, func_name, constraints, sig_args):
        self.func_name = func_name
        self.constraints = constraints
        self.sig_args = sig_args

        self.lookup = defaultdict(lambda: set())
        for c in self.constraints:
            self.lookup[c[1]].add(c[0])

    def __len__(self):
        return len(self.sig_args)


def split_typestring(typestring):
    """
    Check the typestring for cosmetic errors before we begin parsing, and split
    it into the function name, constraints, and signature.
    """
    if typestring.rstrip() != typestring:
        raise TypeStringException("Trailing whitespace in typestring")

    if typestring.lstrip() != typestring:
        raise TypeStringException("Leading whitespace in typestring")

    if re.search("[ ]{2,}", typestring):
        raise TypeStringException("Extra whitespace in typestring")

    # enforce spaces between arrows and types
    if re.search("[^ ]->|->[^ ]", typestring):
        raise TypeStringException("Typestring arrows need surrounding spaces")

    head_match = re.match("^(\w+) :: (.*)$", typestring)
    if not head_match:
        raise TypeStringException("Typestring format incorrect")

    func_name, rest = head_match.group(1), head_match.group(2)
    return func_name, rest


def parse_constraints(const_str):
    """
    Parse the constraint string section of a type signature. Each constraint is
    parsed into a tuple.
    """
    constraints = const_str.split(",")

    for i, c in enumerate(constraints):
        c = c.strip()
        const_match = re.match("^(\w+) (\w+)$", c)
        if not const_match:
            raise TypeStringException("Invalid constraint: %s" % c)
        constraints[i] = (const_match.group(1), const_match.group(2))

    return constraints


def split_constraints(typesig):
    """
    Check the type signature part of the string for constraint clauses.
    If they exist, parse them into tuples.
    """
    constraint_match = re.match("^\((.+?)\) => (.*)$", typesig)

    if constraint_match:
        constraints = parse_constraints(constraint_match.group(1))
        sig = constraint_match.group(2)
    else:
        constraints = []
        sig = typesig

    if "=>" in sig:
        # checking this specifically because it's a common error
        raise TypeStringException("Invalid `=>` in typestring")

    return constraints, sig


def check_paren_balance(string):
    """
    Check whether the parenthesis in a string are balanced. Useful for giving a
    more informative error message from our parser.
    """
    balance = 0
    for ch in string:
        if balance < 0:
            return False
        if ch == "(":
            balance += 1
        elif ch == ")":
            balance -= 1

    if balance != 0:
        return False

    return True


def find_inside_parens(string, initial_pos):
    """
    Given a string and an initial position, find the closing paren that matches
    the open one at the initial position.
    """
    balance = 1
    position = initial_pos
    for j, _ in enumerate(string):
        if j <= initial_pos:
            continue
        position += 1

        if string[j] == ")":
            balance -= 1
        elif string[j] == "(":
            balance += 1

        if balance == 0:
            break
    return string[initial_pos+1:position], string[position+1:]


def parse_signature(sig):
    """
    Recursive decent parser for type signature.
    """
    if sig == "":
        return []

    # Start moving along the string
    for i,c in enumerate(sig):

        # If we encounter an open paren, find the closing paren and parse
        # everything in between
        if sig[i] == "(":
            enclosed, rest = find_inside_parens(sig, i)
            return [parse_signature(enclosed)] + parse_signature(rest)

        # If we encounter an arrow, we can split the string straighforwardly
        elif sig[i:i+4] == " -> ":
            return parse_signature(sig[:i]) + parse_signature(sig[i+4:])
    return [sig]


def parse_haskell_typestring(typestring):
    fn_name, typesig = split_typestring(typestring)
    constraints, sig = split_constraints(typesig)
    signature = parse_signature(sig)

    if not check_paren_balance(sig):
        raise TypeStringException("Unbalanced parens in typestring")

    return TypeSig(fn_name, constraints, signature)
