import os
import json

import config
import ADSAffil.utils as utils
import ADSAffil.tasks as tasks

# ============================= INITIALIZATION ==================================== #

from adsputils import setup_logging, load_config
proj_home = os.path.realpath(os.path.dirname(__file__))
config = load_config(proj_home=proj_home)
logger = setup_logging('run.py', proj_home=proj_home,
                        level=config.get('LOGGING_LEVEL', 'INFO'),
                        attach_stdout=config.get('LOG_STDOUT', False))

debug_record = '{"response": {"docs": [{"bibcode": "2002ApJ...576..963T", "aff": [ "Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101", "Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101", "Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101"]}]}}'


# =============================== FUNCTIONS ======================================= #

class FatalException(Exception):
    #   Throw this generic exception wherever a failure should stop
    #   processing immediately and exit.
    pass


def get_arguments():

    import argparse

    parser = argparse.ArgumentParser(description='Command line options:')

    parser.add_argument('-d',
                        '--debug',
                        dest='debug',
                        action='store_true',
                        help='Send debug_record through pipeline')

    parser.add_argument('-mp',
                        '--makepickle',
                        dest='makepickle',
                        action='store_true',
                        help='Pickle INFILEs')

    parser.add_argument('-f',
                        '--json_file',
                        dest='input_json_file',
                        action='store',
                        help='Input JSON file of solr records to augment')

    args = parser.parse_args()
    return args


def main():

    args = get_arguments()

    if args.makepickle:
        try:
            aff_dict = utils.read_affils_file(config['AFFDICT_INFILE'])
            canon_dict = utils.read_affils_file(config['PC_INFILE'])
            aff_dict_norm = utils.normalize_dict(aff_dict)
            utils.dump_pickle(config['PICKLE_FILE'], [aff_dict_norm, canon_dict])
        except Exception as e:
            logger.error("Could not create affiliation data pickle file: %s" % e)
            raise FatalException("Could not create affiliation data pickle file: %s" % e)

    # These are the only two sources of records to augment if you
    # run from the command line: debug record, and a JSON file of
    # records.  Lacking either, jdata will not exist, and this will
    # generate an information message and the program will end.
    if args.debug:
        jdata = json.loads(debug_record)
    elif args.input_json_file:
        if os.path.isfile(args.input_json_file):
            try:
                with open(args.input_json_file, 'rU') as fp:
                    jdata = json.load(fp)
            except Exception as e:
                logger.error("Failed to read JSON file of records to augment. Stopping: %s" % e)
                raise FatalException("Error reading input JSON file.")
        else:
            logger.error("The JSON filename you supplied for records to augment doesn't exist. Stopping.")
            raise FatalException("The JSON file with the given filename doesn't exist.")

    # Does jdata (json object of records to augment) exist?
    # If so, send each record to task_augment_affiliations_json
    # If not, nothing to do, *end*
    try:
        records = jdata['response']['docs']
    except Exception as e:
        print('No records for direct match.  Nothing to do.')
        logger.info('No records for direct match.  Nothing to do.')
    else:
        logger.info('Starting augments....')
        for rec in records:
            tasks.task_augment_affiliations_json.delay(rec)
        logger.info('Finished augments')


if __name__ == '__main__':
    main()
