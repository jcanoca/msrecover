# -*- coding: utf-8 -*-

# Exigim Python 3
import sys
if sys.version_info[0] < 3:
    raise Exception("Sorry, you need Python 3 to run this application")

# Des d'aquí usem Python 3
import logging
from galoisfield import *
from polyring import *
from ftools import *
from termcolor import colored
import split
import recover

# Treballem amb 256 bits per BIP39
# Mateix primer que a "secp256k1"
PRIME = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1

# Paràmetres sobre les paraules nemotècniques
MIN_NUM_WORDS = 12
MAX_NUM_WORDS = 24

def banner():
        print(colored('''
 _______ _______  ______ _______ _______  _____  _    _ _______  ______
 |  |  | |______ |_____/ |______ |       |     |  \  /  |______ |_____/
 |  |  | ______| |    \_ |______ |_____  |_____|   \/   |______ |    \_
        ''', 'green'),
        colored('''
         Author: Javier Cano (jcanoca@uoc.edu)\n
             logo by http://patorjk.com/\n
        ''','white'))


def main():
    '''Funció d'inici de l'aplicació msrecover. 
        Té tres funcionalitats bàsiques:
            * SPLIT el secret en n participacions amb un llindar de k participacions
            * RECOVER el secret a partir de k participacions
            * DERIVE la master seed a partir de les paraules mnemotècniques i la passphrase (opcional)
    '''

    # Llegim els arguments de la linea de comandaments
    parser = get_parser()
    args = parser.parse_args()
    
    initialize_logging(args.verbose)

    logging.debug(args)
    
    # Versió del mòdul
    if args.version:
        print_user("msrecover 1.0.0", 1)
        exit(0)

    # Inicialitzem cos finit i anell de polinomis sobre aquest cos finit
    K = GF(PRIME)
    F = PolyRing(K)
    
    # Funcionalitas segons el subcomandament executat
    if args.subcommand == 'split':
        # Definim un esquema (n,k)-threshold (5,3) per defecte
        k = int(args.threshold)
        n = int(args.nshares)

        # Validem que el número de participacions a generar sigui més gran que 1
        if n < 2:
            print_user("Number of shares to generate must be greater than 1", 2)
            print_user("Exiting...", 1)
            exit(0)

        # Validem que el llindar ha de ser més petit o igual que el número de participacions
        if n < k:
            print_user("Number of shares 'n' must be greater than threshold 't'", 2)
            print_user("Exiting...", 1)
            exit(0)
        
        # Validem que el llindar ha de ser més gran que 1.
        # És possible però no té cap sentit
        if k < 2:
            print_user("Threshold 't' must bebe greater than threshold 1", 2)
            print_user("Exiting...", 1)
            exit(0)

        # Si hem informat la llista de paraules des de linea de comandament 
        if args.bip39:
            word_list = args.bip39
        else:
            # Si no indiquen res demanem les dades per pantalla
            words = input("Insert nmonemic words (space between words): ")
            
            if words == "":
                print_user("There nust be al least 12 words", 2)
                print_user("Exiting...", 1)
                exit(0)
            
            word_list = words.split(" ")

        if len(word_list) < MIN_NUM_WORDS or len(word_list) > MAX_NUM_WORDS:
            print_user("Number of words incorrect. Must be between 12 and 24 words.", 2)
            print_user("Exiting...", 1)
            exit(0)

        # Idioma per defecte "en" (english)
        if not args.lang:
            # Detectem idioma amb la primera paraula
            word = word_list[0]
            lang = detect_language(word)
        else:
            if args.lang == 'en':
                lang = 'english.txt'
            elif args.lang == 'es':
                lang = 'spanish.txt'
            else:
                print_user("Language not suported", 2)
                print_user("Exiting...", 1)
                exit(0)

        if validate_words(word_list, lang) != 0:
            print_user("Some word is wrong...", 2)
            print_user("Exiting...", 1)
            exit(0)

        secret_str = words2entropy(word_list, lang)
        
        print_user("You've chosen a ({}, {})-threshold Shamir's schema".format(args.nshares, args.threshold), 1)

        # Generem els "n" trossos
        share_list = split.split(n, k, secret_str, args.checksum, F, K)

        if args.qrcode:
            print_user("Generating {} QR codes in files".format(n), 1)
            directory = args.qrcode
            share_list_files = list_shares_qrfiles(share_list, directory)
            for i in range(len(share_list_files)):
                print_user("Files -> {} ".format(share_list_files[i]), 0)
        else:
            for i in range(len(share_list)):
                print_user("Share -> {} ".format(share_list[i]), 0)
        
    elif args.subcommand == 'recover':
        # Recover master seed form 'k' shares
        share_list = []

        # Validar format de les particions
        nshares = int(args.nshares)

        # Entrada de les participacions per QR codes (fitxers) o manual
        if args.qrcode:
            directory = args.qrcode
            share_list = list_qrfiles(directory)
            if len(share_list) < nshares:
                print_user("The number of shares is less than the threshold...", 2)
                print_user("Exiting...", 1)
                exit(0) 
            if len(share_list) > nshares:
                print_user("The number of files is greater than the threshold...", 2)
                print_user("Exiting...", 1)
                exit(0)   
        else: # Entrada manual de les participacions
            i = 0
            while i < nshares:
                share = input("Insert share #{} : ".format(str(i)))    
                share_list.append(share)
                i += 1
        
        # Validem format de les participacions llegides
        for share in share_list:
            if not check_share(share):
                print_user("Format error, please repeat or exit using Ctrl-C...", 2)
                print_user("Exiting", 1)
                exit(0)

        # Totes han de ser del mateix tipus!!
        if '-' in share_list[0]:
            checksum = False
        else:
            checksum = True
        
        secret = recover.recover(share_list, checksum, F, K)
        
        # Idioma per defecte "en" (english)
        if not args.lang:
            lang = "english.txt"
        else:
            if args.lang == 'en':
                lang = 'english.txt'
            elif args.lang == 'es':
                lang = 'spanish.txt'
            else:
                print_user("Language not suported", 2)
                print_user("Exiting...", 1)
                exit(0)
        
        sout = "Language used recovering your secret is...{}".format(lang[:-4])
        print_user(sout, 1)
        words = entropy2words(secret, lang)

        print_user("Secret: {}".format(words), 0)
    elif args.subcommand == 'derive':
        
        word_list = args.words

        if len(word_list) < MIN_NUM_WORDS or len(word_list) > MAX_NUM_WORDS:
            print_user("Number of words incorrect. Must be between 12 and 24 words.", 2)
            print_user("Exiting...", 1)
            exit(0)

        # Detectem idioma amb la primera paraula
        word = word_list[0]
        lang = detect_language(word)
        
        if validate_words(word_list, lang) != 0:
            print_user("Some word is wrong...", 2)
            print_user("Exiting...", 1)
            exit(0)
        
        if args.passphrase:
            print_user("Passphrase used",1)
            passphrase = args.passphrase
        else:
            print_user("No passphrase used",1)
            passphrase = ""
        
        # Derive ms from words+passphrase amd display master seed
        print_user("Master Seed derived: {}".format(words2ms(word_list, passphrase)),0)
    else:
        parser.print_usage()


if __name__ == '__main__':
    banner()
    main()
