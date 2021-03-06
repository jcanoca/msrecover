# -*- coding: utf-8 -*-

import argparse
import hashlib
import secrets
import datetime
import logging
import re
import pyqrcode
import os
from os import listdir
from os.path import isfile, join
from PIL import Image
from pyzbar.pyzbar import decode
from pathlib import Path
from termcolor import colored

# Logging

def initialize_logging(verbose):
    '''Funció per inicialitzar el logging a l'aplicació'''
    
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
    
# Funcions que implementen BIP39

def words2entropy(words, language):
    '''A partir de les n paraules nemotècniques trobem la entropia original'''
    N = len(words)

    # Recover entropy from words
    wordlist = load_words_bip39(language)
    index_list = [bin(wordlist.index(word)).lstrip('0b').zfill(11) for word in words]
    CL = N // 3
    entropy_cs  = "".join(index_list)
    
    entropy = entropy_cs[:-CL]
    CS = entropy_cs[-CL:]

    # Validem si el checksum de la llista de paraules coincideix amb el calculat
    m = hashlib.sha256()
    entropy_hex = hex(int(entropy,2)).lstrip('0x').zfill(len(entropy)//4)
    
    m.update(bytes.fromhex(entropy_hex))
    hexdigest_int = int(m.hexdigest(),16)
    hexdigest_bin = bin(hexdigest_int).lstrip('0b').zfill(256)
    
    # Prenem els primers CL bits del sha256 calculat com a checksum
    checksum = hexdigest_bin[:CL]

    if CS == checksum:
        return entropy
    else:
        return None    

def entropy2words(entropy, language):
    '''A partir del valor d'entropia generem les n words nemotècniques
       entropy en bits
    '''
    # Entropia en format hexadecimal (str)
    
    # Carreguem la llista de paraules mnemotècniques segons idioma
    wordlist = load_words_bip39(language)

    # Convertim l'entropia a una seqüència binaria
    ENT = bin(int(entropy,16)).lstrip('0b')
    
    # Normalitzem longitud de la entropia en bits
    if len(ENT) <= 128:
        N = 128
    elif len(ENT) <= 160:
        N = 160
    elif len(ENT) <= 192:
        N = 192
    elif len(ENT) <= 224:
        N = 224
    else:
        N = 256
    
    ENT = ENT.zfill(N)
    
    # Longitud del checksum
    CL = N//32
    
    # Calculem el checksum
    m = hashlib.sha256()
    entropy = entropy.zfill(N//4)
    m.update(bytes.fromhex(entropy))
    
    hexdigest_int = int(m.hexdigest(),16)
    hexdigest_bin = bin(hexdigest_int).lstrip('0b').zfill(256)
    
    # Prenem els primers CL bits del sha256 calculat com a checksum
    checksum = hexdigest_bin[:CL]
        
    # Concatenem entropia original amb longitud normalitzada i el chechsum calculat
    c = ENT + checksum
    
    # La longitud de "c" és sempre múltiple de 11
    # len(ENT) + len(checksum) = len(c)
    # N + N/32 = 33N/32 = 11 * (3N/32)    
    # Cada 11 bits de la cadena c, el prenem com índex i cerquem la paraula per
    # guardar-la en una llista
    laux = [wordlist[int(c[i:i+11],2)] for i in range(0,len(c),11)]
    
    # Retornem la llista de paraules en un string separades per un espai en blanc
    return " ".join(laux)

def words2ms(words, passphrase):
    ''' 
    Transforma les n paraules nemotècniques + password (BIP39) en la llavor mestre
        Entrada: Paraules i password
        Sortida: Llavor mestre en format BIP39 (512 bits en hexadecimal)
    
    Nota: Utilitza la funció HMAC de derivació de claus PBKDF2 (itera 2048 vegades, seguint especificació BIP39)
    '''
    str_words = " ".join(words)
    salt = "mnemonic"+passphrase
    logging.debug(str_words)
    logging.debug(salt)
    ms = hashlib.pbkdf2_hmac('sha512', str_words.encode('utf-8'), salt.encode('utf-8'), 2048)

    return ms.hex()


# Validacions

def detect_language(word):
    '''Detecció automàtica de l'idioma a partir de la primera paraula.
    Segons BIP39 no hi ha barreja de paraules entre diferents idiomes'''

    # Cerquem tots els fitxers d'idiomes que hi hagi
    wordlist_files = os.listdir('./wordlists')
    
    # Cerquem la paraula als fitxers, si el trobem sortim i retornem l'idioma
    for wordlist_file in wordlist_files:
        wordlist_folder = Path("./wordlists")
        wordlist_path = wordlist_folder / wordlist_file
        
        with open(wordlist_path) as f:
            wordlist = f.read()
        f.close()

        if word in wordlist:
            return wordlist_file

    # Idioma no detectat
    return None

def load_words_bip39(language):
    '''Carrega les paraules nemotècniques i les torna en una llista en funció de l'idioma escollit'''
    
    wordlist_folder = Path("./wordlists")
    wordlist_path = wordlist_folder / language

    with open(wordlist_path) as f:
        words = f.read()
    f.close()

    return words.split("\n")

def print_user(message, tipo):
    '''
    Treu per pantalla informació per l'usuari
    Entrada: Qualsevol dada
    Sortida: Mostra per pantalla [*] missYYYY-MM-DD HH:MM:SS.ddd] <missatge>
    
    Nota: El missatge es converteix a string
    '''
    color1 = "magenta"

    if tipo == 0:
        color2 = "white"
    elif tipo == 1:
        color2 = "blue"
    else:
        color2 = "red"

    print(colored("[+]", color1), colored(str(message), color2, attrs=['bold']))


def SHA(s):
    ''' sha embolcall segons longitud del secret'''

    if len(s) <= 256:
       return sha256(s)
    else:
        return sha512(s)

def sha512(s):
    ''' sha512 ssimplificat transforma str to int '''

    m = hashlib.sha512()
    m.update(s.encode('ascii')) # hex digits són ascii
    return int(m.hexdigest(), 16)

def sha256(s):
    ''' sha256 ssimplificat transforma str to int '''

    m = hashlib.sha256()
    m.update(s.encode('ascii')) # hex digits són ascii
    return int(m.hexdigest(), 16)

def to_hex(m):
    ''' Integer to hex sense '0x' '''
    return hex(m).lstrip('0x')


# Validacions

def check_ms(p0, p1):
    ''' Validem si 
        p(1) == sha256(secret = p(0))
        p0, p1 integers
    '''

    ms_rec = to_hex(p0)
    
    hash_ms_rec = to_hex(SHA(ms_rec))
    hash_ms_eva = to_hex(p1)
    
    logging.debug("p(1) = {}".format(hash_ms_eva))
    logging.debug("sha256(p(0)) = {}".format(hash_ms_rec))

    if hash_ms_rec == hash_ms_eva:
        return True
    else:
        return False

def validate_words(words, language):
    '''Valida que les paraules informades siguin vàlides BIP39'''
    
    coderror = 0
    wordlist = load_words_bip39(language)
    for w in words:
        if w not in wordlist:
            s = "Wrong word " + str(w)
            print_user(s, 2)
            coderror = -1
    
    return coderror

def check_share(share):
    ''' Funció per validar formalment el format de una participació  '''

    regex = re.compile('[0-9]+[-#][0-9abcdef]+')

    if "PRIME=" in share:
        lshare = share.index("PRIME=") - 1
    else:
        lshare = len(share)
    
    # Validem longitud share y = p(x), ha de ser 64 digits hex (32 bytes)
    if '-' in share:
        idy = share.index('-')
    else:
        idy = share.index('#')

    if lshare - idy - 1 < 64:
        print_user("Share too short...", 2)
        return False
    
    if lshare - idy - 1 > 64:
        print_user("Share too larger...", 2)
        return False

    m = regex.match(share)
    
    if m:
        if regex.match(share).end() - regex.match(share).start() == lshare:
            print_user("Format OK {}".format(share), 1)
        else:
            print_user("Format NOK {}".format(regex.match(share).group()), 2)
            return False
    else:   
        print_user("There are some strange characters in some share", 2)
        return False
    
    return True


# Tractament E/S QR

def list_shares_qrfiles(share_list, directory):
    '''Funció que retorna la llista de fitxers de participacions en format QR '''
    share_list_files = []

    for share in share_list:
        filename = share2qr(share, directory)
        share_list_files.append(filename)
    
    return share_list_files

def share2qr(share, directory):
    '''Funció que crea un QR code amb la informació del text d'entrada i retorna el nom del fitxer creat'''
    qr = pyqrcode.create(share)
    filename = str(SHA(share))[0:16]+".png"
    qr.png(join(directory, filename), scale=6)
    return join(directory, filename)

def list_qrfiles(directory):
    ''' A partir d'un directori d'entrada llegeix tots els fitxers PNG amb QR Code'''
    PNGfiles = [join(directory, pngfile) for pngfile in listdir(directory) if isfile(join(directory, pngfile)) and "png" in pngfile]
    list_shares = []
    for png in PNGfiles:
        share = qr2share(png)
        list_shares.append(share)
    
    return list_shares

def qr2share(qrFile):
    '''Funció que a partir d'una imatge d'un QR, extreu la informació en text que guarda'''
    data = decode(Image.open(qrFile))
    share = data[0].data.decode('utf-8')
    return share

# Tractament entrada CLI

def get_parser():
    '''Implementa l’ ́ús del mòdul "argparse" per validar, analitzar i interpretar 
    les dades d’entrada provinents de la línia de comandament'''

    # Creem un ArgumentParser objecte    
    parser = argparse.ArgumentParser(description='Master seed of a HDW backup and recover tool')

    # Add optional arguments of msrecover
    parser.add_argument('--version', action="store_true",
                        help='version of %(prog)s')
    parser.add_argument('-v', '--verbose', type=int, choices=[0, 1, 2, 3, 4],
                        help='level of verbosity')

    # Add subparsers
    subparsers = parser.add_subparsers(title='Functions', description='Valid functions', dest='subcommand')

    # msrecover split parser
    parser_split = subparsers.add_parser('split', help="Split BIP39 Mnemonic in 'n' shares")
    parser_split.add_argument('-n','--nshares', type=int, help="Number of shares to generate", required=True)
    parser_split.add_argument('-t','--threshold', type=int, help="Threshold", required=True)
    parser_split.add_argument('-c','--checksum', action='store_true', help="Checksum on shares")
    parser_split.add_argument('-b','--bip39', nargs='+', help="BIP39 Mnemonic")
    parser_split.add_argument('-l','--lang', type=str, choices=['en', 'es'], help="ISO 639-1 language of wordlist")
    parser_split.add_argument('-q','--qrcode', type=str, help="Path to write shares in QR format to files")

    # msrecover recover parser
    parser_recover = subparsers.add_parser('recover', help="Recover BIP39 Mnemonic from 'k' shares")
    parser_recover.add_argument('-k','--kshares', type=int, help="Number of shares to recover BIP39 Mnemonic", required=True)
    parser_recover.add_argument('-q','--qrcode', type=str, help="Path to read from files with shares in QR format")
    parser_recover.add_argument('-l','--lang', type=str, choices=['en', 'es'], help="ISO 639-1 language of wordlist")

    # msrecover derive parser
    parser_derive = subparsers.add_parser('derive', help="Derive BIP39 Master seed from BIP39 Mnemonic and Passphrase")
    parser_derive.add_argument('-w','--words', nargs='+', help="BIP39 Mnemonic", required=True)
    parser_derive.add_argument('-p','--passphrase', type=str, help="BIP39 Passphrase")

    return parser