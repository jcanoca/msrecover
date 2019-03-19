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

_p = 1613

class GF2():
    """Galois Field objects"""
    def __init__(self, x):
        self.x = x % _p
        
    def __str__(self):
        return str(self.x)

    def __add__(self, other):
        return GF2((self.x + other.x))
    
    def __sub__(self, other):
        return GF2((self.x - other.x))

    def __mul__(self, other):
        return GF2((self.x * other.x))
    
    def _inv(self):
      
        d, _, y = eea(_p, self.x) # (p,a)=1 ==> 1 = p*x + a*y ==> a*y = 1 (mod p)
        # '_' for dummy variable
        if d == 1:
            return y # 1 = p*x + a*y (mod p) ==> a*y = 1 ==> y inverse mod p
        else: 
            return d

    def __pow__(self, n):
        if n < 0:
            return GF2(self._inv())
        else:
            return GF2(self.x ** n)

    
if __name__ == '__main__':
    
    print((GF2(-1)**(-1)))
    print((GF2(-2)**(-1)))
    print(GF2(1612)*GF2(806))
    #s1 = GF2(4)+GF2(5)
    #print("s1= ", s1)
    
    #s2 = GF2(4) - GF2(5)
    #print("s2= ", s2)

    #s3 = GF2(4) * GF2(5)
    #print("s3= ", s3)
    
    #for i in range(_p):
    #    inv1 = GF2(i)**(-1) 
    #    print (i, inv1, (GF2(i)*inv1).x)
    #    print("===")
    
    
    
