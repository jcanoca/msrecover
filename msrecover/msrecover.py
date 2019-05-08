# -*- coding: utf-8 -*-

import logging
from galoisfield import *
from polyring import *
from ftools import *

import split
import recover


# Treballem amb 256 bits per BIP39
# Mateix primer que a "ecp256k1"
PRIME = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1

# Paràmetres sobre les paraules nemotècniques
MIN_NUM_WORDS = 12
MAX_NUM_WORDS = 24

def main():
    '''Funció d'inici de l'aplicació msrecover. 
        Té dues funcionalitats bàsiques:
            * SPLIT el secret en n participacions amb un llindar de k participacions
            * RECOVER el secret a partir de k participacions
    '''

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
        # Definim un esquema (n,k)-threshold (5,3) per defecte
        k = int(args.threshold)
        n = int(args.nshares)

        # Si hem informat la llista de paraules des de linea de comandament 
        if args.bip39:
            word_list = args.bip39
        else:
            # Si no indiquen res demanem les dades per pantalla
            words = input("Insert nmonemic words (space between words): ")
            
            if words == "":
                print_user("There nust be al least 12 words")
                print_user("Exiting...")
                exit(0)
            
            word_list = words.split(" ")

        if len(word_list) < MIN_NUM_WORDS or len(word_list) > MAX_NUM_WORDS:
            print_user("Number of words incorrect")
            print_user("Exiting...")
            exit(0)

        # Idioma per defecte "en" (english)
        if not args.lang:
            lang = "en"
        else:
            lang = args.lang

        if validate_words(word_list, lang) != 0:
            print_user("Some word is wrong...")
            print_user("Exiting...")
            exit(0)

        secret_str = words2entropy(word_list, lang)
        
        print_user("You've chosen a ({}, {})-threshold Shamir's schema".format(args.nshares, args.threshold))

        # Generem els "n" trossos
        share_list = split.split(n, k, secret_str, args.checksum, F, K)

        if args.qrcode:
            print_user("Generating {} QR codes in files".format(n))
            for i in range(len(share_list)):
                print_user("Share -> {} ".format(share_list[i]))
        else:
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
        
        # Totes han de ser del mateix tipus!!
        if '-' in share_list[0]:
            checksum = False
        else:
            checksum = True
        
        secret = recover.recover(share_list, checksum, F, K)
        
        lang = "en"
        #print(secret)
        words = entropy2words(secret, lang)

        print_user("Secret: {}".format(words))
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
