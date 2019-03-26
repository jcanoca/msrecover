from galoisfield import *
from polyring import *
from ftools import *

#import split
#import recover

PRIME = 2**521 - 1


def main():
    
    # Read arguments from command line
    parser = get_parser()
    args = parser.parse_args()
    
    print(args)

    K = GF(PRIME)
    F = PolyRing(K) # PolyRing over GaloisField(p)
    
    if args.subcommand == 'split':

        # Input MS in bip39 format or hex text
        if args.bip39 == True:
            words = input("Insert nmonemic words (space between words): ")
            passphrase = input("Insert your passphrase: ")
            ms_str = words2ms(words, passphrase)
        else:
            ms_str = input("Insert master seed of your HDW: ")
        
        ms_int = int(ms_str, 16)
        ms_str = to_hex(ms_int)

        # Input (n, k)-threshold parameters
        threshold  = input("Insert threshold: ")
        k = int(threshold)
        
        num_shares = input("Insert number of shares: ")
        n = int(num_shares)
        
        print("You've chosen a ({}, {})-threshold Shamir's schema".format(threshold, num_shares))

        if args.validation == True:
            points = []
            # p(0) = ms
            points.append((0, ms_int))
            # p(1) = sha512(ms)
            points.append((1, sha512(ms_str)))

            # Generate k-2 random points
            for i in range(k-2):
                y_str = secrets.token_hex(64)
                y = int(y_str, 16)
                points.append((i+2, y)) # i=0,1 out

            # we need 2 points more, so we generate the polynomial interpolation
            print_trace("Splitting secret","Generating Lagrange Interpolation")
            polyInt = F.interpolate(points, K)
            #print(polyInt)

            # Check p(1) = sha512(p(0))
            if check_ms(polyInt.eval(0).n,polyInt.eval(1).n) :
                print_trace("Checking shares","master seed recovered succesfully!")
            
            # Generate n shares (i=2,...,n+2)
            for i in range(n+2):
                print("Share -> {}#{}".format(str(i),to_hex(polyInt.eval(i).n)))
        else:
            coef = []
            coef.append(ms_int) # a_0 = ms
            for i in range(1, k):
                coef.append(int(secrets.token_hex(64),16)) # k-1 coeficinets
            
            poly = F(coef)
            #print(poly)
            # Generate n shares (i=2,...,n+2)
            for i in range(n):
                print("Share -> {}#{}".format(str(i),to_hex(poly.eval(i).n)))

    elif args.subcommand == 'recover':
        threshold_str = input("Insert number of shares: ")
        threshold = int(threshold_str)

        shares = []
        points = []

        #TODO: check share format nnn#hex_number
        
        for i in range(threshold):
            shares.append(input("Insert share #{} :".format(str(i))))
        
        for i in range(threshold):
            x = int(shares[i].split('#')[0])
            y = int(shares[i].split('#')[1],16)
            points.append((x, y))
        
        # Generate Lagrange Interpolation
        polyInt = F.interpolate(points, K)
        #print(polyInt)
        #print(points)

        if check_ms(polyInt.eval(0).n,polyInt.eval(1).n) :
            print_trace("Checking shares","master seed recovered succesfully!")

        print("Master seed recovered: {}".format(to_hex(polyInt.eval(0).n)))
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
