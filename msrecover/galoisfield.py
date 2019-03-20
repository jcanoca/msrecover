# Galois Field objects

def GF(p):
    class GaloisField():
        """Galois Field objects"""

        def __init__(self, n):
            # TODO: Validate p is prime
            self.n = n % p
            self.field = GaloisField

        def __add__(self, other):
            return GaloisField(self.n + other.n)
    
        def __sub__(self, other):
            return GaloisField(self.n - other.n)

        def __mul__(self, other):
            return GaloisField(self.n * other.n)

        def __pow__(self, m):
            if m < 0:
                return GaloisField(self.__inv()**(-m))
            else:
                return GaloisField(self.n ** m)

        def __mod__(self, m):
                return self.n % m

        def __eq__(self, other):
            return self.n == other.n

        def __ne__(self, other):
            return not self.__eq__(other)

        def __inv(self):
            d, _, y = self.__eea(self.p, self.n) # (p,a)=1 ==> 1 = p*x + a*y ==> a*y = 1 (mod p)
            # '_' for dummy variable
            if d == 1:
                return y # 1 = p*x + a*y (mod p) ==> a*y = 1 ==> y inverse mod p
            else: 
                return d
        
        @staticmethod
        def __eea(a, b):
            '''
            Extended Eculidean Algorithm
                INPUT: a,b>0, a >= b
                OUTPU: d = gcd(a ,b) and x, y: a*x + b*y = d
            '''
            if a < 0 or b < 0:
                return (-1, a, b)
            if a < b:
                return (-1, a, b)
            if b == 0:
                d = a; x = 1; y = 0
                return (d, x, y)
    
            x2 = 1; x1 = 0; y2 = 0; y1 = 1
    
            while b > 0:
                q = a//b; r = a - b*q; x = x2 - q*x1; y = y2 - q*y1
                a = b; b = r; x2 = x1; x1 = x; y2 = y1; y1 = y

            d=a; x=x2; y=y2
            return(d, x, y) # 'y' is not usefull

        def __str__(self):
            return str(self.n) # + " (mod %d)" % (p)

    GaloisField.p = p
    GaloisField.__name__ = "G(%d)" % (p)
    return GaloisField

if __name__ == '__main__':
    #p = 2**(521) - 1
    # p = 26815615859885194199148049996411692254958731641184786755447122887443528060147093953603748596333806855380063716372972101707507765623893139892867298012168351
    p = 13
    F = GF(p)
    print("suma  {} + {} = {}".format(str(F(3)), str(F(5)), str(F(3) + F(5))))
    print("resta {} - {} = {}".format(str( F(3) ), str( F(5) ) , str( F(3) - F(5) )))
    print("prod  {} * {} = {}".format(str(F(3)), str(F(5)), str(F(3) * F(5))))
    print("inv   {} ^ {} = {}".format(str(F(11)), str(-1), str(F(11)**(-1))))
    print("inv2  {} ^ {} = {}".format(str(F(11)), str(-2), str(F(11)**(-2))))
    print("pow   {} ^ {} = {}".format(str(F(11)), str(2), str(F(11)**(2))))
    print("mod   {} mod {} = {}".format(str(F(7)), str(5), str(F(7)%5) ))
    print("F(F(15)) = {} ".format(str(F(F(15)))))
    print(int(str(F(5))))

    
