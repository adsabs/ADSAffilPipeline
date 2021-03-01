"""
run.py is used to test setup and debug pipeline operations. It's main
stand-alone use is to create pickle files for production
"""

import json
import os

import argparse
from adsputils import setup_logging, load_config
from ADSAffil import tasks, utils

proj_home = os.path.realpath(os.path.dirname(__file__))
config = load_config(proj_home=proj_home)
logger = setup_logging('run.py', proj_home=proj_home,
                       level=config.get('LOGGING_LEVEL', 'INFO'),
                       attach_stdout=config.get('LOG_STDOUT', False))

DEBUG_RECORD = '{"response": {"docs": [{"bibcode": "2002ApJ...576..963T", "aff": [ "Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101", "Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101", "Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101"]}]}}'

DEBUG_MATCH_STRINGS = ["Department of Physics, University of California - Berkeley, Berkeley, CA", "Department of Physics, University of the Witwatersrand, 1 Jan Smuts Avenue, Johannesburg 2000, RSA", "Earth, Planetary, and Space Sciences Department, University of California, 90095, Los Angeles, CA, USA", "Department of Physics & Astronomy, University of Delaware, Newark, DE 19716"]


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-mp',
                        '--make_pickle',
                        dest='mp',
                        action='store_true',
                        default=False,
                        help='Create pickle files only')
    parser.add_argument('-f',
                        '--json_file',
                        dest='input_json_file',
                        action='store',
                        help='Input JSON file of solr records to augment')
    parser.add_argument('-x',
                        '--exact',
                        dest='exact',
                        action='store_true',
                        default=False,
                        help='Return exact string matches only (no scoring)')
    parser.add_argument('-d',
                        '--debug',
                        dest='debug',
                        action='store_true',
                        default=False,
                        help='Send debug_record through pipeline')
    parser.add_argument('-dm',
                        '-debug_matching',
                        dest='dm',
                        action='store_true',
                        default=False,
                        help='Test string-matching')
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
    if args.dm:
        for affstring in DEBUG_MATCH_STRINGS:
            result = tasks.task_match_input_string(affstring, args.exact)
            logger.debug("Input string: %s\tMatch: %s" % (affstring, result))

    if args.debug:
        jdata = json.loads(DEBUG_RECORD)
        logger.info("Sending the debugging record: %s" % jdata)
    elif args.input_json_file:
        if os.path.isfile(args.input_json_file):
            try:
                with open(args.input_json_file, 'rU') as fp:
                    jdata = json.load(fp)
            except Exception as error:
                logger.error("Failed to read JSON file of records to augment. Stopping: %s", error)
                return
        else:
            logger.error("The JSON filename you supplied for records to augment doesn't exist. Stopping.")
            return

    # Does jdata (json object of records to augment) exist?
    # If so, send each record to task_augment_affiliations_json
    # If not, nothing to do, *end*
    try:
        records = jdata['response']['docs']
    except Exception as error:
        logger.info('No records for direct match.  Nothing to do.')
    else:
        logger.info('Starting augments....')
        for rec in records:
            tasks.task_augment_affiliations_json.delay(rec)
        logger.info('Finished augments')


if __name__ == '__main__':
    main()
