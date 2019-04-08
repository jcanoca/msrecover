# -*- coding: utf-8 -*-

import logging
import secrets
from galoisfield import *
from polyring import *
from ftools import *


def split(n, k, master_seed_str, check, F, K):

    # Validem coherencia n,k
    if k > n:
        print_user("The number of shares must be greater than the threshold")
        print_user("Exiting...")
        exit(0)

    # Convertim master_seed a integer
    master_seed_int = int(master_seed_str, 16)
        
    if check == True:
        points = []
            
        # Fem p(0) = ms
        points.append((0, master_seed_int))

        # Fem p(1) = sha512(ms)
        points.append((1, sha512(master_seed_str)))

        # Generem k-2 punts aleatoris y_i de 512-bits
        for i in range(k-2):
            y_str = secrets.token_hex(64) # TODO: parametritzar??
            y = int(y_str, 16)
            points.append((i+2, y)) # No guardem i=0,1 

        # Generem dos punts més, generem primer el polinomi interpolador
        logging.debug("Generating Lagrange Interpolation")
        poly = F.interpolate(points, K)
        
        logging.debug((poly))

        # Check p(1) = sha512(p(0))
        if check_ms(poly.eval(0).n, poly.eval(1).n) :
            print_user("Mater Seed integrity ok")
    else:
        coef = []
        coef.append(master_seed_int) # a_0 = ms
        for i in range(1, k):
            coef.append(int(secrets.token_hex(64),16)) # k-1 coeficients
            
        poly = F(coef)
        logging.debug(poly)
        
    # Generem n shares (i=2,...,n+2)
    share_list = []
    for i in range(2, n+2):
        share = str(i) + '-' + to_hex(poly.eval(i).n)
        share_list.append(share)

    return share_list