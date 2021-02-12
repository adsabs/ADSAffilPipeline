import os
from kombu import Queue
from adsmsg import AugmentAffiliationRequestRecord, AugmentAffiliationResponseRecord
from ADSAffil import app as app_module
from ADSAffil import utils

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
app = app_module.ADSAffilCelery('augment-pipeline', proj_home=proj_home, config=globals().get('config', {}), local_config=globals().get('local_config', {}))
logger = app.logger

app.conf.CELERY_QUEUES = (
    Queue('augment-affiliation', app.exchange, routing_key='augment-affiliation'),
    Queue('output-record', app.exchange, routing_key='output-record'),
    Queue('update-record', app.exchange, routing_key='update-record'),
    Queue('api-matcher', app.exchange, rounting_key='match-affil')
)

try:
    (app.adict, app.cdict) = utils.load_affil_dict(app.conf.AFFIL_PICKLE_FILENAME)
    app.clausedict = utils.load_clause_dict(app.conf.CLAUSE_PICKLE_FILENAME)
except Exception as err:
    logger.warning('Unable to load adict/cdict! %s', err)

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
    if isinstance(rec, AugmentAffiliationRequestRecord):
        try:
            rec = rec.toJSON(including_default_value_fields=True)
        except Exception as e:
            logger.warning("Could not convert proto to JSON: %s", e)
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
        logger.warning("Exception: %s", e)


@app.task(queue='api-matcher')
def task_match_input_string(rec, exact_matches_only):
    app.exact = exact_matches_only
    output = app.find_matches(rec)
    return output
