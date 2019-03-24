import argparse
import hashlib
import secrets

from galoisfield import *
from polyring import *
import split
import recover

PRIME = 2**521 - 1

def sha512(s):
    ''' sha512 simplified str to int '''

    m = hashlib.sha512()
    m.update(s.encode('ascii'))
    return int(m.hexdigest(), 16)

def to_hex(m):
    ''' Integer to hex without '0x' '''
    return hex(m).lstrip('0x')

def validate_ms(p0, p1):
    ''' Validate if 
        p(1) == sha512(master seed = p(0))
    '''
    ms_rec = to_hex(p0)
    hash_ms_rec = to_hex(sha512(ms_rec))
    hash_ms_eva = to_hex(p1)
    
    print("p(1) = {}".format(hash_ms_eva))
    print("sha512(p(0)) = {}".format(hash_ms_rec))

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
    parser_split.set_defaults(func=split)

    # msrecover recover parser
    parser_recover = subparsers.add_parser('recover', help='Recover master seed form "k" shares')
    parser_recover.add_argument('--qrcode', action='store_true', help="Read shares from QR files") #need filenames as arguments!
    parser_recover.set_defaults(func=recover)

    return parser

def main():
    
    # Read arguments from command line
    parser = get_parser()
    args = parser.parse_args()
    
    print(args)

    if args.subcommand == 'split':
        # Do split things:
            # get_master_seed
                # from hex format
                # from bip-39 words
            # if shares_signed:
                # Generate k+1 point to get a p(x) of degree k
                    # p0 = (0, ms) and p1 = (1, sha512(ms))
                    # get (i, x_i) i=2,...,k
                # Build p(x) Lagrange Interpolation
            # else:
                # Generate k coeficients a_i i=1,...,k and a_0 = ms
                # Build p(x) = a_0 + a_1*X + ... + a_k*X^k

            # Evaluate n points of p(x): (i, p(i)) i=2,...,n+2
            # Generate n shares (i+p(i))
            # Format of n shares
                # share_signed
                # bip-39
            # Output of n shares
                # QR format (n files)
                # text format (screen or files)

    elif args.subcommand = 'recover':
        # Do recover things:
            # get_k_shares in hex format
                # from qr (files)
                # from text (screen or files)
            # Generate points from k shares (i, p(i)) i = 2,..., k+2
            # Generate p(x) Lagrange Interpolation
                # evaluate p(0)
                # evaluate p(1) == sha512(p(0))
            # Output of p(0)
    else:
        parser.print_usage()

    #ms_str = input("Insert master seed of your HDW: ")
    ms_str = secrets.token_hex(64)

    # There are problems if the master seed begins by 0's
    #ms_str = "063b7e17ca3a83a319d176e9e2c02ffabeffa6f121d1fdbae73a058ae9ef99302bda5e8b8269d3d0d3da2ecce3ab5fefb48305952dd26dad4f6392cf196de101"
    print("ms_str = {}".format(ms_str))

    ms_int = int(ms_str, 16)
    ms_str = to_hex(ms_int)
    print("ms_str = {}".format(ms_str))

    # p(0) = master_seed (512-bit)
    # p(1) = hash512(master_seed) (512-bit)

    K = GF(PRIME)
    F = PolyRing(K) # PolyRing over GaloisField(p)

    #threshold  = input("Insert threshold: ")
    threshold = "4"
    k = int(threshold)
    #num_shares = input("Insert number of shares: ")
    num_shares = "8"
    n = int(num_shares)

    print("You have chosen a ({}, {})-threshold Shamir's schema".format(threshold, num_shares))

    # if validation ON
    points = []
    points.append((0, ms_int))
    points.append((1, sha512(ms_str)))

    # Generate k-2 points (shares)
    for i in range(k-2):
        y_str = secrets.token_hex(64)
        y = int(y_str, 16)
        points.append((i+2, y))

    print("Lagrange Interpolation 1")
    #[print(ele) for ele in points]
    polyInt = F.interpolate(points, K)
    #print(polyInt)

    # Validate if sha512(p(0)) == p(1)
    if validate_ms(polyInt.eval(0).n,polyInt.eval(1).n):
        print("master seed recovered succesfully!")


    # Generate k random points of p(x)
    print("Lagrange Interpolation 2")
    new_points = [(i, polyInt.eval(i).n) for i in range(10,14)]
    #[print(ele) for ele in new_points]
    polyInt2 = F.interpolate(new_points, K)
    #print(polyInt2)
    
    # Validate if sha512(p(0)) == p(1)
    if validate_ms(polyInt2.eval(0).n,polyInt2.eval(1).n):
        print("master seed recovered succesfully!")


if __name__ == '__main__':
    main()
