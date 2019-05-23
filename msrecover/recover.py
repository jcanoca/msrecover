# -*- coding: utf-8 -*-

import logging
from polyring import *
from ftools import *

def recover(share_list, checksum, F, K):
     
    points = []
    # Recuperem punt (x, p(x)) del share
    for i in range(len(share_list)):
        if checksum:
            x = int(share_list[i].split('#')[0])
            y = int(share_list[i].split('#')[1],16)
        else:
            x = int(share_list[i].split('-')[0])
            y = int(share_list[i].split('-')[1],16)

        points.append((x, y))
        
    # Generem Polinomi Interpolador de Lagrange
    polyInt = F.interpolate(points, K)
    logging.debug(polyInt)
    logging.debug(points)

    if checksum:
        if check_ms(polyInt.eval(0).n,polyInt.eval(1).n):
            print_user("Mater Seed integrity OK", 0)
        else:
            print_user("Mater Seed integrity NOK", 2)
            print_user("Exiting...", 1)
            exit(1)
    else:
        print_user("No need to check integrity", 1)

    secret = to_hex(polyInt.eval(0).n)
    secret = secret.zfill(32)
    
    return secret
