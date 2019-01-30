from __future__ import absolute_import, unicode_literals
from kombu import Queue
import os
import config

from ADSAffil import app as app_module
from ADSAffil.curate import parent_child_facet as pcf
from ADSAffil.curate import affil_strings as af
from ADSAffil.models import *
from ADSAffil.learningmodel import affil_match as lm
from ADSAffil.learningmodel import make_learner as mkl
from adsmsg import AugmentAffiliationRequestRecord, AugmentAffiliationResponseRecord

import ADSAffil.utils as utils
import json

app = app_module.ADSAffilCelery('augment-pipeline', proj_home=os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

app.conf.CELERY_QUEUES = (
    Queue('augment-affiliation', app.exchange, routing_key='augment-affiliation'),
    Queue('output-record', app.exchange, routing_key='output-record') 
)
logger = app.logger



@app.task(queue='output-record')
def task_output_augmented_record(rec):

    msg = AugmentAffiliationResponseRecord(**rec)
    app.forward_message(msg)


@app.task(queue='augment-affiliation')
def task_augment_affiliations_json(rec):
    try:
        if 'aff' in rec:
            u = app.augment_affiliations(rec)
            task_output_unmatched(u)
            task_output_augmented_record(rec)
        else:
            logger.debug("Record does not have affiliation info: %s", rec['bibcode'])
            pass
    except Exception as e:
        logger.warning("Could not augment record: %s", rec['bibcode'])
        logger.warning("Exception: %s", e)


def task_augment_affiliations_proto(rec):
    try:
        jrec = rec.toJSON(including_default_value_fields=True)
        logger.warning("Here's your jrec: %s",jrec)
        task_augment_affiliations_json(jrec)
    except:
        logger.warning("Error augmenting protobuf record.")


def task_write_canonical_to_db(recs):
    if len(recs) > 0:
        try:
            app.write_canonical_to_db(recs)
        except:
            raise BaseException("Could not write canonical to db")


def task_write_affilstrings_to_db(recs):
    if len(recs) > 0:
        try:
            app.write_affilstrings_to_db(recs)
        except:
            raise BaseException("Could not write affilstrings to db")


def task_read_canonical_from_db():
    try:
        dictionary = app.read_canonical_from_db()
    except:
        raise BaseException("Could not read canonical from db")
    else:
        return dictionary


def task_read_affilstrings_from_db():
    try:
        dictionary = app.read_affilstrings_from_db()
    except:
        raise BaseException("Could not read canonical from db")
    else:
        return dictionary


def task_make_pickle_file(aff_dict,pickle_file):
    ad_pickle = {}
    try:
        for k,v in aff_dict.items():
            knew = utils.normalize_string(k)
            ad_pickle[knew] = v
    except:
        logger.error("Error creating pickle dictionary.")
        raise BaseException("Error creating pickle dictionary.")
    try:
        af.dump_affil_pickle(ad_pickle,pickle_file)
    except:
        logger.error("Could not write pickle file. Stopping.")
        raise BaseException("Error writing pickle file.")


def task_load_dicts_from_file(canon_file,aff_file):
    canon_dict = pcf.load_simple(canon_file)
    aff_list = af.load_simple(aff_file)
    aff_list = af.convert_strings(aff_list)
    aff_dict = {}
    for l in aff_list:
        (k,v) = l.strip().split('\t')
        aff_dict[v] = k
    return aff_list,aff_dict,canon_dict


def task_make_learning_model(aff_dict):
    learningmodel = mkl.make_learner(aff_dict)
    return learningmodel


def task_resolve_unmatched(stringdict,learningdict):
    try:
        e = lm.matcha(stringdict,learningdict)
    except:
        logger.error("Machine learning matching failed.  Stopping")
    else:
        if e != "":
            logger.error("Machine learning matching failed.  No output.")

def task_read_unmatched_file(unmatched_file):
    unmatched = {}
#   try:
    with open(unmatched_file,'rU') as fi:
        for l in fi.readlines():
            unmatched[l.strip()] = u"0"
#   except:
#       logger.error("Failed to read unmatched strings from file {0}".format(unmatched_file))
    return unmatched

def task_output_unmatched(unmatched_string):
        try:
            if len(unmatched_string) > 0:
                with open(config.UNMATCHED_FILE,'a') as fo:
                    for l in unmatched_string.keys():
                        fo.write(l+"\n")
        except:
            logger.error("Failed to write unmatched strings to file.  No output.")
