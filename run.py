from time import time
import os
import config
import json
import logging
from ADSAffil import tasks
from ADSAffil import utils
from ADSAffil.curate import affil_strings as af
from ADSAffil.curate import parent_child_facet as pcf
from ADSAffil.models import *
from adsmsg import AugmentAffiliationRequestRecord, AugmentAffiliationRequestRecordList
from adsputils import setup_logging, get_date

global logger, unmatched
logger = setup_logging('run.py')
unmatched = {}

def get_arguments():

    import argparse
    logging.captureWarnings(True)

    parser=argparse.ArgumentParser(description='Command line options.')

    parser.add_argument('-f',
                        '--filename',
                        dest='filename',
                        action='store',
                        help='Input JSON file of solr records to augment')

    parser.add_argument('-d',
                        '--diagnose',
                        dest='diagnose',
                        action='store_true',
                        help='Queue hard coded request for affiliation')

    parser.add_argument('-la',
                        '--load-affildict',
                        dest='load_affil_strings',
                        action='store',
                        nargs='?',
                        const=config.AFFDICT_INFILE,
                        type=str,
                        help='Curation: Load the list of affiliation-affil id pairs into db')

    parser.add_argument('-lc',
                        '--load-canonical',
                        dest='load_canonical_pc_facet',
                        action='store',
                        nargs='?',
                        const=config.PC_INFILE,
                        type=str,
                        help='Curation: Load the list of canonical affil-parent-child facet data into db')

    parser.add_argument('-cp',
                        '--create-pickle',
                        dest='pickle_filename',
                        action='store',
                        nargs='?',
                        const=config.PICKLE_FILE,
                        type=str,
                        help='Curation: Write the records in the affil-dict db to a picklefile')

    parser.add_argument('-m',
                        '--machine-resolver',
                        dest='resolve',
                        action='store_true',
                        help='Send unmatched strings to the machine learner')

    parser.add_argument('-lu',
                        '-load-unmatched',
                        dest='unmatched',
                        action='store',
                        nargs='?',
                        const=config.UNMATCHED_FILE,
                        type=str,
                        help='Curation: Load a list of unmatched strings for the machine learner.  Note: triggers -m.')

    parser.add_argument('-r',
                        '--records',
                        dest='records',
                        action='store',
                        nargs='?',
                        type=str,
                        help='One or more records to be processed')

    args=parser.parse_args()
    return args


def main():

    logging.captureWarnings(True)

    args = get_arguments()

# OPTIONAL
# load the dictionary of canonical pc facet info
    if args.load_canonical_pc_facet:
        try:
            recs = pcf.load_simple(args.load_canonical_pc_facet)
        except:
            raise BaseException("Could not load affiliation string dictionary from file.")
        else:
            if len(recs) > 0:
                logger.info('Inserting {0} canonical affiliations'.format(len(recs)))
                tasks.task_write_canonical_to_db(recs)

# OPTIONAL
# load the dictionary of string - affil_id matches
    if args.load_affil_strings:
        try:
            recs = af.load_simple(args.load_affil_strings)
            recs_converted = []
            maxlen = 50000
            while len(recs) > 0:
                block1 = recs[0:maxlen]
                block2 = recs[maxlen:]
                recs = block2
                input_block = "<p>".join(block1)
                recs_converted.extend(utils.back_convert_entities(input_block))
            recs = recs_converted


        except:
            raise BaseException("Could not load affiliation string dictionary from file.")
        if len(recs) > 0:
            logger.info('Inserting {0} IDed affiliation strings'.format(len(recs)))
            tasks.task_write_affilstrings_to_db(recs)


# OPTIONAL
# pickle the dictionary of affil strings pulled from the database
    if args.pickle_filename:
        aff_dict = tasks.task_read_affilstrings_from_db()
        ad_pickle = {}
        try:
            for k,v in aff_dict.items():
                knew = utils.normalize_string(k)
                ad_pickle[knew] = v
        except:
            logger.error("Could not read Affil strings from postgres. Stopping.")
            raise BaseException("Error reading Affil strings from db.")
        try:
            af.dump_affil_pickle(ad_pickle,args.pickle_filename)
        except:
            logger.error("Could not write pickle file. Stopping.")
            raise BaseException("Error writing pickle file.")

# Get records to Augment:
# args.filename is the JSON file containing Solr records to augment.
    records = []
    if args.records:
        r = AugmentAffiliationRecordRequestList.toJSON(args.records)
        print "type(r),r from cmd line are: %s,%s"%(type(r),r)
        quit()


# code that receives records to augment here....



        print "I would get messages from master pipeline here...."
        pass






    else:
        if args.filename:
            if os.path.isfile(args.filename):
                try:
                    with open(args.filename,'rU') as fp:
                        jdata = json.load(fp)
                        records = jdata['response']['docs']
                except:
                    logger.error("Failed to read JSON file of records to augment. Stopping.")
                    raise BaseException("Error reading input JSON file.")
            else:
                logger.error("The JSON filename you supplied for records to augment doesn't exist. Stopping.")
                raise BaseException("The JSON file with the given filename doesn't exist.")



# only continue if you have records, no point otherwise.
    if len(records) == 0 and not args.unmatched:
        logger.warn("No records to process, stopping now.")
    else:
                
        logger.info("Starting augments")
        for rec in records:
            tasks.task_augment_affiliations.delay(rec)
        logger.info("Finished augments")
            

#testing: print output records
# you need to add code to send these to MP instead....
#       if len(records) > 0:
#            with open(config.DIRECT_RECORDS,'w') as fo:
#                dout = {}
#                dout["docs"] = records
#                json.dump(dout,fo, sort_keys=True, indent=4)

        if args.unmatched:
            try:
                with open(args.unmatched,'rU') as fi:
                    for l in fi.readlines():
                        unmatched[l.strip()] = u"0"
            except:
                logger.error("Failed to read unmatched strings from file.  No input.")
            else:
                args.resolve = True

        if len(unmatched) > 0:
            if args.resolve:
                try:
                    aff_dict = tasks.task_db_readall_affstrings()
                except:
                    logger.error("Failed to load aff_dict from postgres, stopping.")
                    raise BaseException("Could not load aff_dict from db.")

                try:
                    lmod = tasks.task_make_learning_model(aff_dict)
                except:
                    logger.error("Failed to create learning model, stopping.")
                    raise BaseException("Could not make learning model.")

                try:
                    tasks.task_resolve_unmatched(unmatched.keys(), lmod)
                except:
                    logger.error("Problem using learning model, failed.")
                    raise BaseException("Machine learning model failed.")
            else:
                try:
                    output = unmatched.keys()
                    if len(output) > 0:
                        with open(config.UNMATCHED_FILE,'a') as fo:
                            for l in output:
                                fo.write(l+"\n")
                except:
                    logger.error("Failed to write unmatched strings to file.  No output.")
        else:
            logger.warn("No unmatched strings to resolve, stopping now.")



if __name__ == '__main__':
    main()

