#!/usr/bin/env python

def get_options():
    import argparse
    parser=argparse.ArgumentParser(description='Convert a file to ascii line by line')
    parser.add_argument('infile',type=str,nargs=1,help='file name to be converted')
    args=parser.parse_args()
    return args.infile[0]

def main(infile):

    filename=open(infile,'rU')
    for l in filename.readlines():
         converter(l.rstrip())

def converter(line):
    try:
        lo=line.decode('utf-8').encode('ascii','xmlcharrefreplace')
    except UnicodeDecodeError:
        try:
            lo2=line.decode('cp1252').encode('ascii','xmlcharrefreplace')
        except UnicodeDecodeError:
            print("Unconvertable line.")
        else:
            print(lo2)
    except AttributeError:
            print("Unconvertable line.")
    else:
        print(lo)
    return

if __name__ == '__main__':
    main(get_options())
