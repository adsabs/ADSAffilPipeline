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
                        help='File of affil records to be IDed')

    args=parser.parse_args()
    return args

def main():


#   because sklearn is throwing an annoying FutureWarning in python3
    warnings.filterwarnings("ignore", category=FutureWarning)


    args = get_arguments()

    if args.filename:
        infile=args.filename
    else:
        infile='test_data'

#   read the learning model and target data
    learning_frame=read_data(LM_INFILE,LM_COLS)
    match_frame=read_data(infile,MATCH_COLS)

#   transform learning model using sklearn
    (cvec,transf,cveclfitr,affil_list)=learning_model(learning_frame)

#   classify and output
    print_output((1./len(learning_frame)),match_entries(learning_frame,match_frame,cvec,transf,cveclfitr,MATCH_COLS))


if __name__ == '__main__':
    main()
