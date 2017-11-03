#!/usr/bin/env python

from affil_match import *
from config import *

def get_arguments():

    import argparse

    parser=argparse.ArgumentParser(description='Command line options.')

    parser.add_argument('-f',
                        '--filename',
                        dest='filename',
                        action='store',
                        required=True,
                        help='File of affil records to be IDed')

    parser.add_argument('-o',
                        '--outfile',
                        dest='outfile',
                        action='store',
                        help='Name of file to write IDs to')

    parser.add_argument('-r',
                        '--random-seed',
                        dest='random',
                        action='store',
                        help='Integer for classifier random seed (omit to use np.random)')

    args=parser.parse_args()
    return args

def main():


#   because sklearn is throwing an annoying FutureWarning in python3
    warnings.filterwarnings("ignore", category=FutureWarning)


    args = get_arguments()
    infile=args.filename


# This is wonky.  Ideally it'd be great if you could instead send args.outfile
# to the existing definition within the scope of config, affil_match -- this
# isn't that.
#
# You'll really have a problem if you add a switch to tell it whether or
# not to use a random seed for classification....
#
    if args.outfile:
        outfile=args.outfile
    else:
        outfile='OUTPUT_FILE'

    print (MATCH_COLS)
    print (outfile)

#   read the learning model and target data
    learning_frame=read_data(LM_INFILE,LM_COLS)
    match_frame=read_data(infile,MATCH_COLS)

    print(LM_INFILE,LM_COLS)

#   transform learning model using sklearn
    (cvec,transf,cveclfitr,affil_list)=learning_model(learning_frame)

#   classify and output
    print_output((1./len(learning_frame)),match_entries(learning_frame,match_frame,cvec,transf,cveclfitr,MATCH_COLS),outfile)


if __name__ == '__main__':
    main()
