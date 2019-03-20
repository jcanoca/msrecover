import argparse
import hashlib
import secrets
from galoisfield import *
from polyring import *

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
    ms_rec = to_hex(p0)
    hash_ms_rec = to_hex(sha512(ms_rec))
    hash_ms_eva = to_hex(p1)
    
    print("p(1) = {}".format(hash_ms_eva))
    print("sha512(p(0)) = {}".format(hash_ms_rec))

    if hash_ms_rec == hash_ms_eva:
        return True
    else:
        return False

def main():
    
    parser = argparse.ArgumentParser(description="Backup and recover master seed HDW")

    # Optional and mutually exclusive arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r", "--recover", action="store_true")
    group.add_argument("-s", "--split",   action="store_true")

    # Positional arguments
    #parser.add_argument("x", type=int, help="the base")
    #parser.add_argument("y", type=int, help="the exponent")
    #args = parser.parse_args()
    #answer = args.x**args.y

    #if args.quiet:
    #    print(answer)
    #elif args.verbose:
    #    print("{} to the power {} equals {}".format(args.x, args.y, answer))
    #else:
    #    print("{}^{} == {}".format(args.x, args.y, answer))


    # TODO: Manage sys arguments

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
