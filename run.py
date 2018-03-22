#!/usr/bin/env python


# export JOBLIB_MULTIPROCESSING=0

from affilmatch.affil_match import *
import pandas as pd
import config

def get_arguments():

    import argparse

    parser=argparse.ArgumentParser(description='Command line options.')

    parser.add_argument('-f',
                        '--filename',
                        dest='filename',
                        action='store',
                        required=True,
                        help='Name of file with affil records to be IDed')

    parser.add_argument('-o',
                        '--outfile',
                        dest='outfile',
                        action='store',
                        help='Name of file to write IDs to')

    parser.add_argument('-l',
                        '--learner',
                        dest='learner',
                        action='store',
                        help='Name of file with learning model data')


    parser.add_argument('-t',
                        '--family-tree',
                        dest='parentchild',
                        action='store',
                        help='Name of file with parent-children data')

    parser.add_argument('-r',
                        '--random-seed',
                        dest='random',
                        action='store',
                        help='Integer for classifier random seed (omit to use np.random)')

    parser.add_argument('-n',
                        '--num-threads',
                        dest='cpu',
                        action='store',
                        help='Integer number of allowed threads (-1 == system maximum)')

    args=parser.parse_args()
    return args

def main():



#   because sklearn is throwing an annoying FutureWarning in python3
    warnings.filterwarnings("ignore", category=FutureWarning)

    args = get_arguments()
    infile=args.filename

    if args.outfile:
        config.OUTPUT_FILE = args.outfile

    if args.learner:
        config.LM_INFILE = args.learner

    if args.parentchild:
        config.PC_INFILE = args.parentchild

    if args.random:
        config.SGDC_RANDOM_SEED = args.random

    if args.cpu:
        config.SGDC_PARAM_CPU = args.cpu

#   read the learning model and target data
    learning_frame=read_data(config.LM_INFILE,config.LM_COLS)
    # match_frame=read_data(infile,config.MATCH_COLS)
    match_frame = pd.DataFrame([{'bibcode': '2017ABCD...17..128D',
                                 'Affil': 'University Delaware',
                                 'Author': 'Doe, Jane',
                                 'sequence': '5/3'}])

#   transform learning model using sklearn
    (cvec,transf,cveclfitr,affil_list)=learning_model(learning_frame)

#   classify and output
    matched = match_entries(learning_frame,match_frame,cvec,transf,cveclfitr,config.MATCH_COLS)
    matched = matched.to_dict()
    print matched['Affcodes'][0]
    # print_output((1./len(learning_frame)),match_entries(learning_frame,match_frame,cvec,transf,cveclfitr,config.MATCH_COLS))


if __name__ == '__main__':
    main()
