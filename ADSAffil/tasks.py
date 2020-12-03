import adsputils
import os
from kombu import Queue
from ADSAffil import app as app_module
from ADSAffil import utils
from adsmsg import AugmentAffiliationRequestRecord, AugmentAffiliationResponseRecord

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
app = app_module.ADSAffilCelery('augment-pipeline', proj_home=proj_home, config=globals().get('config', {}), local_config=globals().get('local_config', {}))
logger = app.logger

app.conf.CELERY_QUEUES = (
    Queue('augment-affiliation', app.exchange, routing_key='augment-affiliation'),
    Queue('output-record', app.exchange, routing_key='output-record'),
    Queue('api-matcher', app.exchange, rounting_key='match-affil'),
    Queue('update-record', app.exchange, routing_key='update-record')
)

(app.adict, app.cdict) = utils.load_affil_dict(app.conf.AFFIL_PICKLE_FILENAME)

# ===================================TASKS=================================== #
@app.task(queue='update-record')
def task_update_record(msg):
    logger.debug('in update record with {}'.format(str(msg.toJSON())))
    task_augment_affiliations_json(msg)


@app.task(queue='output-record')
def task_output_augmented_record(rec):
    msg = AugmentAffiliationResponseRecord(**rec)
    app.forward_message(msg)


@app.task(queue='augment-affiliation')
def task_augment_affiliations_json(rec):
    if app.adict is None or app.cdict is None:
        logger.warn("pickled dictionaries not already loaded!")
        (app.adict, app.cdict) = utils.load_affil_dict(app.conf.get('PICKLE_FILE'))
    if isinstance(rec, AugmentAffiliationRequestRecord):
        try:
            xrec = rec.toJSON(including_default_value_fields=True)
        except Exception as e:
            logger.warn("Could not convert proto to JSON: %s", e)
            # rec = {}
        else:
            rec = xrec
    try:
        if 'aff' in rec:
            u = app.augment_affiliations(rec)
            task_output_augmented_record(rec)
        else:
            logger.debug("Record does not have affiliation info: %s", rec['bibcode'])
            pass
    except Exception as e:
        if isinstance(rec, dict) and 'bibcode' in rec:
            logger.debug("Could not augment record: %s", rec['bibcode'])
        else:
            pass
        logger.warn("Exception: %s", e)


@app.task(queue='api-matcher')
def task_match_input_string(rec):
    output = app.find_matches(rec)
    # MAKE A JAZZ NOISE HERE
