# -*- coding: utf-8 -*-

import logging
import secrets
from galoisfield import *
from polyring import *
from ftools import *


def split(n, k, secret_str, checksum, F, K):
    '''Funció per dividir el secret en "n" parts amb un llindar de "t" participacions'''

    # Validem coherencia n,k
    if k > n:
        print_user("The number of shares must be greater than the threshold")
        print_user("Exiting...")
        exit(0)

    # n < PRIME
    if n > K.p:
        print_user("The number of shares is too large")
        print_user("Exiting...")
        exit(0)

    # Convertim entropy a integer
    secret_int = int(secret_str, 2)
    
    # master seed < PRIME
    if secret_int > K.p:
        print_user("Secret is too large")
        print_user("Exiting...")
        exit(0)
        
    if checksum == True:
        points = []
            
        # Fem p(0) = ms
        points.append((0, secret_int))

        # Fem p(1) = shaNNN(secret)
        p_1 = SHA(to_hex(secret_int))
        points.append((1, p_1))

        # Generem k-2 punts aleatoris y_i de 256-bits = 32-bytes
        long_bytes = 32
        
        for i in range(k-2):
            y_str = secrets.token_hex(long_bytes)
            y = int(y_str, 16)
            points.append((i+2, y)) # No guardem i=0,1 

        # Generem dos punts més, generem primer el polinomi interpolador
        logging.debug("Generating Lagrange Interpolation")
        poly = F.interpolate(points, K)
        
        logging.debug((poly))

        # Check p(1) = sha512(p(0))
        if check_ms(poly.eval(0).n, poly.eval(1).n) :
            print_user("Mater Seed integrity OK")
        else:
            print_user("Mater Seed integrity NOK!!!")
    else:
        coef = []
        coef.append(secret_int) # a_0 = ms
        for i in range(1, k):
            coef.append(int(secrets.token_hex(64),16)) # k-1 coeficients
            
        poly = F(coef)
        logging.debug(poly)
        
    # Generem n shares (i=2,...,n+2)
    share_list = []
    for i in range(2, n+2):
        if checksum == True:
            share = str(i) + '#' + to_hex(poly.eval(i).n)
        else:
            share = str(i) + '-' + to_hex(poly.eval(i).n)
        share_list.append(share)

    return share_list