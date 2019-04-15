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

    # TODO: Modificar nom rutina "check_ms" per "checksum_ms"
    if checksum:
        if check_ms(polyInt.eval(0).n,polyInt.eval(1).n):
            print_user("Mater Seed integrity ok")
        else:
            print_user("Mater Seed integrity NOK")
            print_user("Exiting...")
            exit(0)
    
    master_seed = to_hex(polyInt.eval(0).n)

    # En el cas de master seed començant per 0's, completem amb 0s per davant
    if len(master_seed) < 128:
        print_user("Master seed incomplete!")
        master_seed = '0'*(128-len(master_seed)) + master_seed

    return master_seed
