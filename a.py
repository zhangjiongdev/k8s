class Vector:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def __str__(self):
        # return "<{},{}>".format(self.a,self.b)
        return "<%d,%d>"%(self.a,self.b)
    
    __repr__=__str__
    
    def __add__(self,other):
        return Vector(self.a + other.a, self.b + other.b)



