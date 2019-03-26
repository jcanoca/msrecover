import argparse
import hashlib
import secrets
import datetime


def words2ms(password, passphrase):
    ''' TODO '''
    
    salt = "mnemonic"+passphrase
    print(password)
    print(salt)
    ms = hashlib.pbkdf2_hmac('sha512', password.encode('ascii'), salt.encode('ascii'), 2048)

    return ms.hex()

def print_trace(title, text):
    ''' TODO '''

    s = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    print("[{}] - {} - {}".format(s, title, text))

def sha512(s):
    ''' sha512 simplified str to int '''

    m = hashlib.sha512()
    m.update(s.encode('ascii'))
    return int(m.hexdigest(), 16)

def to_hex(m):
    ''' Integer to hex without '0x' '''
    return hex(m).lstrip('0x')

def check_ms(p0, p1):
    ''' Validate if 
        p(1) == sha512(master seed = p(0))
    '''
    ms_rec = to_hex(p0)
    hash_ms_rec = to_hex(sha512(ms_rec))
    hash_ms_eva = to_hex(p1)
    
    #print("p(1) = {}".format(hash_ms_eva))
    #print("sha512(p(0)) = {}".format(hash_ms_rec))

    if hash_ms_rec == hash_ms_eva:
        return True
    else:
        return False


def get_parser():

    # Step 1: Create an ArgumentParser object with description
    # Define object
    parser = argparse.ArgumentParser(description='Master seed of a HDW backup and recover tool')

    # Add optional arguments of msrecover
    parser.add_argument('--version', action="store_true",
                        help='version of %(prog)s')
    parser.add_argument('--verbose', action="store_true",
                        help='version of %(prog)s')

    # Add subparsers
    subparsers = parser.add_subparsers(title='Functions', description='Valid functions', dest='subcommand')

    # msrecover split parser
    parser_split = subparsers.add_parser('split', help='split help')
    parser_split.add_argument('--validation', action='store_true', help="Put validation mark on shares")
    parser_split.add_argument('--bip39', action='store_true', help="Master Seed in BIP-0039 format")

    # msrecover recover parser
    parser_recover = subparsers.add_parser('recover', help='Recover master seed form "k" shares')
    parser_recover.add_argument('--qrcode', action='store_true', help="Read shares from QR files") #need filenames as arguments!

    return parser



