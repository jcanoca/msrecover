# Polynomial objects

def _dg(poly):
        for idx,item in enumerate(poly.coef[::-1]): # reversed list
            if item != 0:
                return len(poly.coef)-1-idx
        return 0

_p = 1613

class Poly():
    """
        
        Definition of polynomial over a field
        p(x) = a_0 + a_1*x + . . . + a_n*x^n <==> [a_0, a_1, ..., a_n] list of coeficients

    """

    def __init__(self, coef):
        """ Initizlization of a polynomial """
        # TODO: every element of coef must be an element of the field
        # TODO: last element a_n must be different to 0

        self.coef = [ele%_p for ele in coef]
        self.dg = _dg(self)
    
    # TODO:  review...
    def __str__(self):
        """ Pretty print of a polynoial """
        s = ''
        for i in range(self.dg + 1):
            if self.coef[i] != 0:
                if i == 0:
                    s = s + str(self.coef[i])
                elif i == 1:
                    s = s + str(self.coef[i]) + "*X"    
                else:
                    s = s + str(self.coef[i]) + "*X^" + str(i)
                if i < self.dg:
                    s = s + " + "
        return str(s)

    def __add__(self, other):
        """ 
        add two polynomials over GF(p): 
        [a0, a1, . . ., aN] + [b0, b1, . . ., bM] = [c0, c1, . . ., cP]
        where P = max(N, M)
        cI = (aI + bI) mod (p)
        """
        # TODO: self.field must be equal to other.field
        r = []
        for i in range(max(self.dg, other.dg)+1):
            if i <= self.dg:
                if i <= other.dg:
                    r.append((self.coef[i] + other.coef[i]) % _p )
                else:
                    r.append(self.coef[i])
            else:
                if i <= other.dg:
                    r.append(other.coef[i])
                else:
                    raise ValueError('Situation not possible!')

        return Poly(r)
    
    def __sub__(self, other):
        """ exit()
        add two polynomials over GF(p): 
        [a0, a1, . . ., aN] + [b0, b1, . . ., bM] = [c0, c1, . . ., cP]
        where P = max(N, M)
        cI = (aI - bI) mod (p)
        """
        # TODO: self.field must be equal to other.field
        r = []
        for i in range(max(self.dg, other.dg)+1):
            if i <= self.dg:
                if i <= other.dg:
                    r.append((self.coef[i] - other.coef[i]) % _p)
                else:
                    r.append(self.coef[i])
            else:
                if i <= other.dg:
                    r.append((0-other.coef[i])%_p)
                else:
                    raise ValueError('Error')

        return Poly(r)
    
    def __mul__(self, other):
        '''Polynomial multiplication over finite filed GF(p)'''
        r = [0 for i in range(self.dg + other.dg + 1)]
        for i in range(self.dg + 1):
            for j in range(other.dg + 1):
                r[i+j] = (r[i+j] + (self.coef[i]*other.coef[j])) % _p

        return Poly(r)

    def eval(self, a):
        '''Horner's method for evaluation of polynomials'''
        aux = 0
        for i in range(self.dg):
            aux = (aux + self.coef[self.dg-i]) % _p
            aux = (aux * a) % _p
        
        aux = (aux + self.coef[0]) % _p

        return aux
    
    @classmethod
    def interpolate(cls, *points):
        return Poly(r)

if __name__ == '__main__':
    # prime = 2**(521) - 1
    p = Poly([0])
    q = Poly([1,1])
    print("p(x) = ", Poly([3])*p, p.dg)
    print("q(x) = ", q, q.dg)
    #print("p(x)*q(x) = ", p*q, (p*q).dg)
    print("q(x)+q(x) = ", p+q, (p+q).dg)
    #print("p(x)-q(x) = ", p-q, (p-q).dg)
    #r = Poly([1,1])
    #for i in range(10):
    #    r *= p 
    #print(r, r.dg)


