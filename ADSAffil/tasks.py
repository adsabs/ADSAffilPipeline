from kombu import Queue
import os

from ADSAffil import app as app_module
from ADSAffil import utils
from adsmsg import AugmentAffiliationRequestRecord, AugmentAffiliationResponseRecord

import config

app = app_module.ADSAffilCelery('augment-pipeline', proj_home=os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

app.conf.CELERY_QUEUES = (
    Queue('augment-affiliation', app.exchange, routing_key='augment-affiliation'),
    Queue('output-record', app.exchange, routing_key='output-record')
)
logger = app.logger

app.load_dicts(config.PICKLE_FILE)



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


@app.task(queue='augment-affiliation')
def task_augment_affiliations_proto(rec):
    try:
        jrec = rec.toJSON(including_default_value_fields=True)
        logger.warning("Here's your jrec: %s",jrec)
        task_augment_affiliations_json(jrec)
    except:
        logger.warning("Error augmenting protobuf record.")


def task_output_unmatched(unmatched_string):
        try:
            if len(unmatched_string) > 0:
                with open(config.UNMATCHED_FILE,'a') as fo:
                    for l in unmatched_string.keys():
                        fo.write(l+"\n")
        except:
            logger.error("Failed to write unmatched strings to file.  No output.")
