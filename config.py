import os

# possible values: WARN, INFO, DEBUG
LOGGING_LEVEL = 'DEBUG'

# Celery related configuration
# All work we do is concentrated into one exchange (the queues are marked
# by topics, e.g. ads.orcid.claims); The queues will be created automatically
# based on the workers' definition. If 'durable' = True, it means that the 
# queue is created as permanent *AND* the worker will publish 'permanent'
# messages. Ie. if rabbitmq goes down/restarted, the uncomsumed messages will
# still be there 

CELERY_INCLUDE = ['ADSAffil.tasks']
ACKS_LATE=True
PREFETCH_MULTIPLIER=1
CELERYD_TASK_SOFT_TIME_LIMIT = 300

CELERY_DEFAULT_EXCHANGE = 'augment_pipeline'
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"

CELERY_BROKER = 'pyamqp://user:password@localhost:6672/augment_pipeline'
OUTPUT_CELERY_BROKER = 'pyamqp://user:password@localhost:5682/master_pipeline'

OUTPUT_TASKNAME = 'adsmp.tasks.task_update_record'

# Affiliation configuration files
AFFDICT_INFILE = '/proj/ads_abstracts/config/affils/Affils_v1.0.0'
PC_INFILE = '/proj/ads_abstracts/config/affils/parent_child.new'
PICKLE_FILE = 'data/aff.pickle'
UNMATCHED_FILE = 'output/unmatched.out'
DIRECT_RECORDS = 'output/direct.json'
