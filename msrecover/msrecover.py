# -*- coding: utf-8 -*-

import logging
from galoisfield import *
from polyring import *
from ftools import *

import split
import recover

# Treballem amb 521 bits (mínim 512)
#PRIME = 2**521 - 1
PRIME = 0x10000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000004_b

def main():
    '''Funció d'inici de l'aplicació msrecover '''

    # Llegim els arguments de la linea de comandaments
    parser = get_parser()
    args = parser.parse_args()
    
    initialize_logging(args.verbose)

    logging.debug(args)

    # Inicialitzem cos finit i anell de polinomis sobre aquest cos finit
    K = GF(PRIME)
    F = PolyRing(K)

    # Funcionalitas segons el subcomandament executat
    if args.subcommand == 'split':
        
        # Definim un esquema (n,k)-threshold
        k = int(args.threshold)
        n = int(args.shares)

        # TODO: Treure tractament master seed a mòdul ftools o funció a msrecover...

        # Master Seed en format BIP-0039 o text en HEX
        if args.bip39 == True:
            words = input("Insert nmonemic words (space between words): ")
            
            if words == "":
                print_user("There nust be al least 1 word")
                print_user("Exiting...")
                exit(0)

            passphrase = input("Insert your passphrase: ")
            ms_str = words2ms(words, passphrase)
        else:
            ms_str = input("Insert master seed of your HDW: ")
        #ms_int = int(ms_str, 16)
        #ms_str = to_hex(ms_int) # Dubte...
        #
        print_user("You've chosen a ({}, {})-threshold Shamir's schema".format(args.shares, args.threshold))

        # Generem els "n" trossos
        share_list = split.split(n, k, ms_str, args.check, F, K)

        # TODO: Tractament soritda del "n" trosso (per pantalla, per fitxer,...)
        for i in range(len(share_list)):
            print_user("Share -> {} ".format(share_list[i]))
        
    elif args.subcommand == 'recover':
        # Recover master seed form 'k' shares
        share_list = []

        #TODO: validar format de les particions
        nshares = int(args.nshares)
        for i in range(nshares):
            share_list.append(input("Insert share #{} : ".format(str(i))))

        master_seed = recover.recover(share_list, F, K)
        # TODO: Tractament soritda del "n" trosso (per pantalla, per fitxer,...)
        print_user("Master Seed recovered: {}".format(master_seed))
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
