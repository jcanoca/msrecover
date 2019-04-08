# -*- coding: utf-8 -*-

import argparse
import hashlib
import secrets
import datetime
import logging

# TODO: Afegir més comentaris al codi

def initialize_logging(verbose):
    
    _NO_LOG = 100
    
    # Inicitalitzant el logging
    if verbose == None:
        level_log = _NO_LOG
    else:
        if verbose == 0:
            level_log = logging.DEBUG
        elif verbose == 1:
            level_log = logging.INFO
        elif verbose == 2:
            level_log = logging.WARNING
        elif verbose == 3:
            level_log = logging.ERROR
        else:
            level_log = logging.CRITICAL
    
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(module)s - %(funcName)s]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S', level=level_log)
    

def words2ms(password, passphrase):
    ''' 
    Transforma les n paraules nemotècniques + password (BIP39) en la llavor mestre
        Entrada: Paraules i password
        Sortida: Llavor mestre en format HEX
    
    Nota: Utilitza la funció HMAC de derivació de calus PBKDF2 (itera 2048 vegades, seguint especificació BIP-0039)
    '''
    
    salt = "mnemonic"+passphrase
    logging.debug(password)
    logging.debug(salt)
    ms = hashlib.pbkdf2_hmac('sha512', password.encode('ascii'), salt.encode('ascii'), 2048)

    return ms.hex()

def print_user(message):
    '''
    Treu per pantalla el missatger amb la data i hora del moment format ISO 8601  
    Entrada: Qualsevol dada
    Sortida: Mostra per pantalla [YYYY-MM-DD HH:MM:SS.ddd] <missatge>
    
    Nota: El missatge es converteix a string
    '''
        
    print("[{}] {}".format(datetime.datetime.now().isoformat(' ', timespec='milliseconds'), str(message)))

def sha512(s):
    ''' sha512 ssimplificat transforma str to int '''

    m = hashlib.sha512()
    m.update(s.encode('ascii'))
    return int(m.hexdigest(), 16)

def to_hex(m):
    ''' Integer to hex sense '0x' '''
    return hex(m).lstrip('0x')

def check_ms(p0, p1):
    ''' Validem si 
        p(1) == sha512(master seed = p(0))
    '''
    ms_rec = to_hex(p0)
    hash_ms_rec = to_hex(sha512(ms_rec))
    hash_ms_eva = to_hex(p1)
    
    logging.debug("p(1) = {}".format(hash_ms_eva))
    logging.debug("sha512(p(0)) = {}".format(hash_ms_rec))

    if hash_ms_rec == hash_ms_eva:
        return True
    else:
        return False


def get_parser():

    # Creem un ArgumentParser objecte    
    parser = argparse.ArgumentParser(description='Master seed of a HDW backup and recover tool')

    # Add optional arguments of msrecover
    parser.add_argument('--version', action="store_true",
                        help='version of %(prog)s')
    parser.add_argument('-v', '--verbose', type=int, choices=[0, 1, 2, 3, 4],
                        help='version of %(prog)s')

    # Add subparsers
    subparsers = parser.add_subparsers(title='Functions', description='Valid functions', dest='subcommand')

    # msrecover split parser
    parser_split = subparsers.add_parser('split', help='split help')
    parser_split.add_argument('shares', type=int, help="Number of shares to generate")
    parser_split.add_argument('threshold', type=int, help="Threshold")
    parser_split.add_argument('--check', action='store_true', help="Put check mark on shares")
    parser_split.add_argument('--bip39', action='store_true', help="Master Seed in BIP-0039 format")

    # msrecover recover parser
    parser_recover = subparsers.add_parser('recover', help='Recover master seed form "k" shares')
    parser_recover.add_argument('nshares', type=int, help="Number of shares to recover the master seed")
    parser_recover.add_argument('--qrcode', action='store_true', help="Read shares from QR files") #need filenames as arguments!

    return parser