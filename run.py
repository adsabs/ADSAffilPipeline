import adsputils
import argparse
import os
from adsputils import setup_logging, load_config, get_date
from ADSAffil import app, tasks, utils

proj_home = os.path.realpath(os.path.dirname(__file__))
config = load_config(proj_home=proj_home)
logger = setup_logging('run.py', proj_home=proj_home,
                        level=config.get('LOGGING_LEVEL', 'INFO'),
                        attach_stdout=config.get('LOG_STDOUT', False))

def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-mp',
                        '--make_pickle',
                        dest = 'mp',
                        action = 'store_true',
                        default = False,
                        help = 'Create pickle files only')
    parser.add_argument('-x',
                        '--exact',
                        dest = 'exact',
                        action = 'store_true',
                        default = False,
                        help = 'Return exact string matches only (no scoring)')
    return parser.parse_args()

        
def main():

    args = getargs()
    if args.mp:
        utils.make_affil_pickle(config['TEXT_AFFIL_DICT_FILENAME'],
                                config['TEXT_PC_DICT_FILENAME'],
                                config['AFFIL_PICKLE_FILENAME'],
                                config['MAX_PICKLE_PROTOCOL'])
        utils.make_clause_pickle(config['TEXT_AFFIL_DICT_FILENAME'],
                                 config['CLAUSE_PICKLE_FILENAME'],
                                 config['CLAUSE_SEPARATOR'],
                                 config['MAX_PICKLE_PROTOCOL'])
    else:
        (adict, cdict) = utils.load_affil_dict(config['AFFIL_PICKLE_FILENAME'])
        clausedict = utils.load_clause_dict(config['CLAUSE_PICKLE_FILENAME'])
        matcher = app.ADSAffilCelery('run.py')
        matcher.adict = adict
        matcher.cdict = cdict
        matcher.clausedict = clausedict


        input_test = ["Department of Physics, University of California - Berkeley, Berkeley, CA", "Department of Physics, University of the Witwatersrand, 1 Jan Smuts Avenue, Johannesburg 2000, RSA", "Earth, Planetary, and Space Sciences Department, University of California, 90095, Los Angeles, CA, USA", "Department of Physics & Astronomy, University of Delaware, Newark, DE 19716"]

        for affstring in input_test:
            result = matcher.find_matches(affstring)
            print("Input string: %s\nMatch: %s\n\n" % (affstring,result))


if __name__ == '__main__':
    main()
