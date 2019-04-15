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
        if args.bip39:
            words = input("Insert nmonemic words (space between words): ")
            
            if words == "":
                print_user("There nust be al least 1 word")
                print_user("Exiting...")
                exit(0)

            # TODO: validar que totes les paraules siguin les de la llista
            #       implica saber l'idioma d'entrada... i tenir tots el fitxers de wordlist
            
            passphrase = input("Insert your passphrase: ")
            ms_str = words2ms(words, passphrase)
        else:
            ms_str = input("Insert master seed of your HDW: ")

        print_user("You've chosen a ({}, {})-threshold Shamir's schema".format(args.shares, args.threshold))

        # Generem els "n" trossos
        share_list = split.split(n, k, ms_str, args.checksum, F, K)

        # TODO: Tractament soritda del "n" trossos (per pantalla, per fitxer,...)
        for i in range(len(share_list)):
            print_user("Share -> {} ".format(share_list[i]))
        
    elif args.subcommand == 'recover':
        # Recover master seed form 'k' shares
        share_list = []

        # Validar format de les particions
        nshares = int(args.nshares)

        i = 0
        while i < nshares:
            share = input("Insert share #{} : ".format(str(i)))
            
            if not check_share(share):
                print_user("Format error, please repeat or exit using Ctrl-C...")
            else:
                share_list.append(share)
                i += 1
        # TODO: Detectem tipus de share
        # Ull: totes han de ser del mateix tipus!!
        if '-' in share_list[0]:
            checksum = False
        else:
            checksum = True
        
        master_seed = recover.recover(share_list, checksum, F, K)
        # TODO: Tractament soritda del "n" trosso (per pantalla, per fitxer,...)
        print_user("Master Seed recovered: {}".format(master_seed))
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
