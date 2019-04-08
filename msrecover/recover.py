# -*- coding: utf-8 -*-

import logging
from polyring import *
from ftools import *

def recover(share_list, F, K):
     
    points = []
    # Recuperem punt (x, p(x)) del share
    for i in range(len(share_list)):
        x = int(share_list[i].split('-')[0])
        y = int(share_list[i].split('-')[1],16)
        points.append((x, y))
        
    # Generem Polinomi Interpolador de Lagrange
    polyInt = F.interpolate(points, K)
    logging.debug(polyInt)
    logging.debug(points)

    if check_ms(polyInt.eval(0).n,polyInt.eval(1).n) :
        print_user("Mater Seed integrity ok")
    
    master_seed = to_hex(polyInt.eval(0).n)

    return master_seed
