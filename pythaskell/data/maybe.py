### Data.Maybe

def isJust(maybe_a):
    return not maybe_a is Nothing

def isNothing(maybe_a):
    return not isJust(maybe_a)

def fromJust(maybe_a):
    if isJust(maybe_a):
        return maybe_a._value
    else:
        raise ValueError("Cannot call fromJust on Nothing.")

def listToMaybe(list_a):
    if list_a:
        return Just(list_a)
    else:
        return Nothing

def maybeToList(maybe_a):
    if isJust(maybe_a):
        return [fromJust(maybe_a)]
    else:
        return []

def catMaybes(list_maybes):
    return [maybe_item for maybe_item in list_maybes if isJust(maybe_item)]

def mapMaybe(fn, list_a):
    maybes = (fn(a) for a in list(a))
    return [fromJust(b) for b in maybes if isJust(b)]


