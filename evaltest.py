class whatis(object):
    def __init__(self, n):
        print "init %s" % n
        self.n = n
    def __rshift__(self, other):
        print "rshift: %s >> %s" % (self, other)
        return self
    def __str__(self):
        return "(whatis %s)" % self.n
    def __or__(self, other):
        print "or: %s | %s" % (self, other)
        return self
