# Galois Field objects

# Extended Eculidean Algorithm
# INPUT: a,b>0, a >= b
# OUTPU: d = gcd(a ,b) and x, y: a*x + b*y = d
def eea(a, b):
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

class GF():
    """Galois Field objects"""
    def __init__(self, p):
        # TODO: Validate p is prime
        self.p = p
        self.elements = range(p)
        
    def __str__(self):
        st = "{ "
        for el in self.elements:
            st = st + str(el) + ", "
        st = st[:-2] + " }"
        return st

    def getK(self):
        return self.p

    def gf(self,x):
        return x % self.p

    def __add__(self, x, y):
        return (x + y) % self.p
    
    def __sub__(self, x, y):
        return (x - y) % self.p

    def __mul__(self, x, y):
        return (x * y) % self.p

    def inv(self, a):
      
        d, _, y = eea(self.p, a) # (p,a)=1 ==> 1 = p*x + a*y ==> a*y = 1 (mod p)
        # '_' for dummy variable
        if d == 1:
            return y % self.p # 1 = p*x + a*y (mod p) ==> a*y = 1 ==> y inverse mod p
        else: 
            return d


if __name__ == '__main__':
    #p = 2**(521) - 1
    # p = 26815615859885194199148049996411692254958731641184786755447122887443528060147093953603748596333806855380063716372972101707507765623893139892867298012168351
    p = 7
    F = GF(p)
    print(F.gf(4)+F.gf(5))
    #print (F.add(13,4))
    #print (F.sub(3,14))
    #print (F.mul(7,4))
    #for i in range(1, F.getK()):
    #    print ("Inv de ", str(i), " es ", str(F.inv(i)), str((i*F.inv(i)) % F.getK() ) )
    a = p - 1
    print ("Inv de ", str(a), " es ", str(F.inv(a)), str((a*F.inv(a)) % F.getK() ) )
