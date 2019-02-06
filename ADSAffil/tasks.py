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
            utils.output_unmatched(config.UNMATCHED_FILE,u)
            task_output_augmented_record(rec)
        else:
            raise BaseException("Record does not have affil info.")
            logger.debug("Record does not have affiliation info: %s", rec['bibcode'])
            pass
    except Exception as e:
#       raise BaseException("PROBLEM: {0}".format(e))
        if isinstance(rec,dict) and 'bibcode' in rec:
            logger.warning("Could not augment record: %s\n%s", (rec['bibcode'],e))
        else:
            logger.warning("Exception: %s", e)


def task_augment_affiliations_proto(rec):
    try:
        jrec = rec.toJSON(including_default_value_fields=True)
        logger.warning("Here's your jrec: %s",jrec)
        task_augment_affiliations_json(jrec)
    except:
        logger.warning("Error augmenting protobuf record.")
