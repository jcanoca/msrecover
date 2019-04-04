import logging
from galoisfield import *
from polyring import *
from ftools import *

#import split
#import recover

# Treballem amb 521 bits (mínim 512)
PRIME = 2**521 - 1
#_PRIME = '10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004b'
_NO_LOG = 100

def main():
    '''Funció d'inici de l'aplicació msrecover '''

    # Llegim els arguments de la linea de comandaments
    parser = get_parser()
    args = parser.parse_args()
    
    # Inicitalitzant el logging
    if args.verbose == None:
        level_log = _NO_LOG
    else:
        if args.verbose == 0:
            level_log = logging.DEBUG
        elif args.verbose == 1:
            level_log = logging.INFO
        elif args.verbose == 2:
            level_log = logging.WARNING
        elif args.verbose == 3:
            level_log = logging.ERROR
        else:
            level_log = logging.CRITICAL
    
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(module)s - %(funcName)s]: %(message)s',datefmt='%Y-%m-%d %H:%M:%S', level=level_log)
    
    
    logging.debug(args)
    logging.critical(args)

    # Inicialitzem cos finit i anell de polinomis sobre aquest cos finit
    K = GF(PRIME)
    F = PolyRing(K)
    
    # Funcionalitas segons el subcomandament executat
    if args.subcommand == 'split':
        
        # Validem paràmetres d'entrada del comandament "split"

        # Definim un esquema (n,k)-threshold
        k = int(args.threshold)
        n = int(args.shares)

        # Validem coherencia n,k
        if k > n:
            print_user("The number of shares must be greater than the threshold")
            print_user("Exiting...")
            exit(0)

        # Input MS in bip39 format or hex text
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
        
        ms_int = int(ms_str, 16)
        ms_str = to_hex(ms_int)

        print_user("You've chosen a ({}, {})-threshold Shamir's schema".format(args.shares, args.threshold))

        # Generem els "n" trossos
        # share_list = split(m, k, master_seed, check)

        if args.check == True:
            points = []
            
            # Fem p(0) = ms
            points.append((0, ms_int))

            # Fem p(1) = sha512(ms)
            points.append((1, sha512(ms_str)))

            # Generem k-2 punts aleatoris y_i de 512-bits
            for i in range(k-2):
                y_str = secrets.token_hex(64)
                y = int(y_str, 16)
                points.append((i+2, y)) # i=0,1 out

            # we need 2 points more, so we generate the polynomial interpolation
            print_trace("Splitting secret","Generating Lagrange Interpolation")
            polyInt = F.interpolate(points, K)
            
            logging.debug((polyInt))

            # Check p(1) = sha512(p(0))
            if check_ms(polyInt.eval(0).n,polyInt.eval(1).n) :
                print_trace("Checking shares","master seed recovered succesfully!")
            
            # Generate n shares (i=2,...,n+2)
            for i in range(n+2):
                print("Share -> {}-{}".format(str(i),to_hex(polyInt.eval(i).n)))
        else:
            coef = []
            coef.append(ms_int) # a_0 = ms
            for i in range(1, k):
                coef.append(int(secrets.token_hex(64),16)) # k-1 coeficinets
            
            poly = F(coef)
            #print(poly)
            # Generate n shares (i=2,...,n+2)
            for i in range(n):
                print("Share -> {}-{}".format(str(i),to_hex(poly.eval(i).n)))

    elif args.subcommand == 'recover':
        #share_list = split(m, k, master_seed, check)
        #threshold_str = input("Insert number of shares: ")
        #threshold = int(threshold_str)
        nshares = int(args.nshares)

        shares = []
        points = []

        #TODO: check share format nnn#hex_number
        
        for i in range(nshares):
            shares.append(input("Insert share #{} :".format(str(i))))
        
        # Recuperem punt (x, p(x)) del share
        for i in range(nshares):
            x = int(shares[i].split('-')[0])
            y = int(shares[i].split('-')[1],16)
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
