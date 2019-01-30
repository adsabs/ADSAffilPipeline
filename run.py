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

app = tasks.app
logger = setup_logging('run.py')


# Database access
def read_canonical_from_db():
    dictionary = {}
    with app.session_scope() as session:
        for record in session.query(CanonicalAffil.aff_id,CanonicalAffil.canonical_name,CanonicalAffil.facet_name,CanonicalAffil.parents_list,CanonicalAffil.children_list):
            pj = json.loads(record.parents_list)
            cj = json.loads(record.children_list)
            (p,c) = pj['parents'],cj['children']
            dictionary[record.aff_id] = {'canonical_name':record.canonical_name,'facet_name':record.facet_name,'parents':p,'children':c}
    return dictionary


def read_affilstrings_from_db():
    with app.session_scope() as session:
        dictionary = {}
        for record in session.query(AffStrings.aff_id,AffStrings.aff_string).order_by(AffStrings.aff_id):
            s = record.aff_string
            a = record.aff_id
            if s in dictionary:
                if dictionary[s] != a:
                    pass
#                   logger.info("Not overwriting existing key pair {0}: {1} with {2}".format(s,dictionary[s],a))
            else:
                dictionary[s] = a
        return dictionary


def write_canonical_to_db(recs):
    with app.session_scope() as session:
        outrecs = []
        for r in recs:
            outrecs.append(CanonicalAffil(aff_id=r[0],canonical_name=r[1],facet_name=r[2],parents_list=r[3],children_list=r[4]))
        session.bulk_save_objects(outrecs)
        session.commit()


def write_affilstrings_to_db(self, recs):
    maxlen = 50000
    with app.session_scope() as session:
        while len(recs) > 0:
            outrecs = recs[0:maxlen]
            remainder = recs[maxlen:]
            recs = remainder
            db_outrec = []
            for r in outrecs:
                try:
                    (affid,affstring)=r.split('\t')
                except:
                    pass
                else:
                    db_outrec.append(AffStrings(aff_id=affid,aff_string=affstring,orig_pub=False,orig_ml=False,orig_ads=True,ml_score=0,ml_version=0))
            session.bulk_save_objects(db_outrec)
            session.commit()




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

    parser.add_argument('-cf',
                        '--load-configs',
                        dest='configfiles_load',
                        action='store_true',
                        help='Load from config files, not postgres db.')

    parser.add_argument('-lu',
                        '--load-unmatched',
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

    if args.configfiles_load:
        try:
            (aff_list,aff_dict,canon_list) = tasks.task_load_dicts_from_file(config.PC_INFILE,config.AFFDICT_INFILE)
        except:
            logger.error('Could not read affil data from files.')
            raise BaseException('Could not read affil data from files.')

# OPTIONAL
# load the dictionary of canonical pc facet info
    if args.load_canonical_pc_facet:
        if len(canon_list) > 0:
                logger.info('Inserting {0} canonical affiliations into db'.format(len(canon_list)))
                write_canonical_to_db(canon_list)
            

# OPTIONAL
# load the dictionary of string - affil_id matches
    if args.load_affil_strings:
        if len(aff_list) > 0:
            logger.info('Inserting {0} IDed affiliation strings'.format(len(aff_list)))
            write_affilstrings_to_db(aff_list)


# OPTIONAL
# pickle the dictionary of affil strings pulled from the database
    if args.pickle_filename:
        aff_dict = read_affilstrings_from_db()
        ad_pickle = {}
        try:
            tasks.task_make_pickle_file(aff_dict,args.pickle_filename)
        except:
            logger.error("Could not write pickle file. Stopping.")
            raise BaseException("Error writing pickle file.")

# Get records to Augment:
# args.filename is the JSON file containing Solr records to augment.
    records = []
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

# load aff_dict and canon_dict here:
#       aff_dict = utils.load_affil_dict(config.PICKLE_FILE)
        aff_dict = read_affilstrings_from_db()
        canon_dict = read_canonical_from_db()
                
        logger.info("Starting augments")
        for rec in records:
            tasks.task_augment_affiliations_json.delay(rec)
        logger.info("Finished augments")
            

        unmatched = {}
        if args.unmatched:
            unmatched = tasks.task_read_unmatched_file(args.unmatched)
            args.resolve = True

        if len(unmatched) > 0:
            if args.resolve:
                try:
                    lmod = tasks.task_make_learning_model(aff_dict)
                except:
                    logger.error("Failed to create learning model, stopping.")

                try:
                    tasks.task_resolve_unmatched(unmatched.keys(), lmod)
                except:
                    logger.error("Problem using learning model, failed.")
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

