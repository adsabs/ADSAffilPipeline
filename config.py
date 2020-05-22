# possible values: WARN, INFO, DEBUG
LOGGING_LEVEL = 'INFO'
LOG_STDOUT = True

# Celery related configuration
# All work we do is concentrated into one exchange (the queues are marked
# by topics, e.g. ads.orcid.claims); The queues will be created automatically
# based on the workers' definition. If 'durable' = True, it means that the
# queue is created as permanent *AND* the worker will publish 'permanent'
# messages. Ie. if rabbitmq goes down/restarted, the uncomsumed messages will
# still be there

CELERY_INCLUDE = ['ADSAffil.tasks']
ACKS_LATE = True
PREFETCH_MULTIPLIER = 1000
CELERYD_TASK_SOFT_TIME_LIMIT = 300

CELERY_DEFAULT_EXCHANGE = 'augment_pipeline'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'

CELERY_BROKER = 'pyamqp://user:password@localhost:6672/augment_pipeline'
OUTPUT_CELERY_BROKER = 'pyamqp://user:password@localhost:5682/master_pipeline'

OUTPUT_TASKNAME = 'adsmp.tasks.task_update_record'

# Affiliation configuration files
# Note these filenames are symlinks to the current versions located in
# ./data/versions/current.vN.N.N
AFFDICT_INFILE = '/proj/ads_abstracts/config/affils/PIPELINE/data/affil_strings.txt'
PC_INFILE = '/proj/ads_abstracts/config/affils/PIPELINE/data/parent_child.txt'
PICKLE_FILE = '/proj/ads_abstracts/config/affils/PIPELINE/data/aff.pickle'

# Output file for unmatched affils.  Note these will be appended to each
# time this runs, and is not yet uniq'ed -- strings may appear multiple times

UNMATCHED_FILE = '/proj/ads_abstracts/config/affils/PIPELINE/output/unmatched.out'
