import os
import logging
import json

import config
import ADSAffil.utils as utils
import ADSAffil.tasks as tasks

from adsputils import setup_logging


app = tasks.app
logger = setup_logging('run.py')

debug_record = '{"response":{"docs":[{"bibcode":"2002ApJ...576..963T", "aff":[ "Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101", "Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101", "Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101"]}]}}'


def get_arguments():

    import argparse
    logging.captureWarnings(True)

    parser=argparse.ArgumentParser(description='Command line options:')

    parser.add_argument('-d',
                        '--debug',
                        dest='debug',
                        action='store_true',
                        help='Send debug_record through pipeline')

    parser.add_argument('-lf',
                        '--loadfiles',
                        dest='loadfiles',
                        action='store_true',
                        help='Load config.AFFDICT_INFILE and PC_INFILE')

    parser.add_argument('-mp',
                        '--makepickle',
                        dest='makepickle',
                        action='store_true',
                        help='Pickle INFILEs')


    parser.add_argument('-lp',
                        '--loadpickle',
                        dest='loadpickle',
                        action='store_true',
                        help='Load data from pickle file')

    parser.add_argument('-f',
                        '--json_file',
                        dest='input_json_file',
                        action='store',
                        help='Input JSON file of solr records to augment')

    args = parser.parse_args()
    return args



def main():

    logging.captureWarnings(True)

    args = get_arguments()

    if args.loadfiles:

        aff_dict = utils.read_affils_file(config.AFFDICT_INFILE)
        canon_dict = utils.read_pcfacet_file(config.PC_INFILE)
        if args.makepickle:
            aff_dict_norm = {}
            for (k,v) in aff_dict.items():
                kn = utils.normalize_string(k)
                aff_dict_norm[kn] = v
            utils.dump_pickle(config.PICKLE_FILE,[aff_dict_norm,canon_dict])


    if args.debug:
        jdata = json.loads(debug_record)
    elif args.input_json_file:
        if os.path.isfile(args.input_json_file):
            try:
                with open(args.input_json_file,'rU') as fp:
                    jdata = json.load(fp)
            except:
                logger.error("Failed to read JSON file of records to augment. Stopping.")
                raise BaseException("Error reading input JSON file.")
        else:
            logger.error("The JSON filename you supplied for records to augment doesn't exist. Stopping.")
            raise BaseException("The JSON file with the given filename doesn't exist.")
    try:
        records = jdata['response']['docs']
    except:
        print "No records for direct match."
    else:
        logger.info("Starting augments....")
        for rec in records:
            tasks.task_augment_affiliations_json.delay(rec)
        logger.info("Finished augments")


if __name__ == '__main__':
    main()
