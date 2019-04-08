# -*- coding: utf-8 -*-

# Polynomial objects
# TODO: Afegir més comentaris al codi
import logging
from galoisfield import *

def PolyRing(K):

    
    class Poly():
        """
            Definició d'un polinomi sobre un cos finit
            p(x) = a_0 + a_1*x + . . . + a_n*x^n <==> [a_0, a_1, ..., a_n] llista de coeficients
        """

        def __init__(self, coef):
            """ Inicialització d'un polinomi amb coef a K"""
            
            self.coef = [K(ele) for ele in coef]
            self.dg = self.__dg()
        
        # TODO:  review...
        def __str__(self):
            """ Com mostrem el polinomi (str) """
            s = ''
            for i in range(self.dg + 1):
                if self.coef[i] != K(0):
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
            Suma de dos polinomis sobre K: 
            [a0, a1, . . ., aN] + [b0, b1, . . ., bM] = [c0, c1, . . ., cP]
            on P = max(N, M)
            cI = (aI + bI) mod (p)
            """
            r = []
            for i in range(max(self.dg, other.dg)+1):
                if i <= self.dg:
                    if i <= other.dg:
                        r.append(self.coef[i] + other.coef[i])
                    else:
                        r.append(self.coef[i])
                else:
                    if i <= other.dg:
                        r.append(other.coef[i])
                    else:
                        raise ValueError('Error') # TODO: Millorar tractament

            return Poly(r)
        
        def __sub__(self, other):
            """ 
            Resta de 2 polinomis sobre K: 
            [a0, a1, . . ., aN] - [b0, b1, . . ., bM] = [c0, c1, . . ., cP]
            where P = max(N, M)
            cI = (aI - bI) mod (p)
            """
            r = []
            for i in range(max(self.dg, other.dg)+1):
                if i <= self.dg:
                    if i <= other.dg:
                        r.append(self.coef[i] - other.coef[i])
                    else:
                        r.append(self.coef[i])
                else:
                    if i <= other.dg:
                        r.append(K(0)-other.coef[i] )
                    else:
                        raise ValueError('Error') # TODO: Millorar tractament

            return Poly(r)
        
        def __mul__(self, other):
            '''Producte de 2 polinomis amb coeficients a K'''
            r = [K(0) for i in range(self.dg + other.dg + 1)]
            for i in range(self.dg + 1):
                for j in range(other.dg + 1):
                    r[i+j] = r[i+j] + (self.coef[i]*other.coef[j]) 

            return Poly(r)

        def __dg(self):
            ''' Càlcul grau d'un polinomi'''

            for idx,item in enumerate(self.coef[::-1]): # reversed list
                if item != K(0):
                    return len(self.coef)-1-idx
            return 0

        def eval(self, a):
            '''Implementació mètode de Horner per avaluar polinomi a x=a'''

            aux = K(0)
            for i in range(self.dg):
                aux = (aux + self.coef[self.dg-i]) 
                aux = (aux * K(a))

            aux = (aux + self.coef[0])

            return aux
        
        @classmethod
        def interpolate(cls, points, K):
            ''' Càlcul polinomi interpolador que passa pels punts "points" '''
            
            F = PolyRing(K)

            x=[]; y=[]
            for a, b in points:
                x.append(a)
                y.append(b)
            
            lp = []
            pi = F([0])
            
            logging.debug(type(pi))

            l = len(points)
            for k in range(l):
                r = F([1])
                for j in range(l):
                    if j != k:
                        inverso = K((x[k]-x[j]))**(-1) 
                        r *= F([-x[j],1]) * F([inverso])
                lp.append(r)
                pi += F([y[k]]) * r
            
            return pi
                
    
    return Poly

if __name__ == '__main__':
    
    T = GF(1613)
    print(type(T(1)))
    F = PolyRing(T) # PolyRing over GaloisField(p)
    print(type(F([0])))
    #p = F([3,2])
    #q = F([1,1])
    #print("p(x) = ", p)
    #print("q(x) = ", q)
    #print("dg of p(x) = ", p.dg)
    #print("dg of q(x) = ", q.dg)

    #print("q(x)+q(x) = ", p+q)
    #print("p(x)-q(x) = ", p-q)
    #print("p(x)*q(x) = ", p*q)
    
    #print("dg of (p+q)(x) = ", (p+q).dg)
    #print("dg of (p-q)(x) = ", (p-q).dg)
    #print("dg of (p*q)(x) = ", (p*q).dg)

    #for i in range(5):
    #    print ("p({})={}".format(str(i), str(p.eval(i))))
    
    # Lagrange Interpolation
    points = [(1,1494), (2,329), (3,965)]
    print("Interpolation 1")
    polyInt = F.interpolate(points, T)
    print(polyInt)

    points = [(4,176), (5,1188), (6,775)]
    print("Interpolation 2")
    polyInt = F.interpolate(points, T)
    print(polyInt)