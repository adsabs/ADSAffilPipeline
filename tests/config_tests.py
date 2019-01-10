PC_INFILE = 'tests/testdata/pc_dict.txt'
AFFDICT_INFILE = 'tests/testdata/aff_dict.txt'
PICKLE_FILE = 'tests/testdata/aff.pickle'
OUTPUT_FILE = 'tests/testdata/ml.out'
UNMATCHED_FILE = 'tests/testdata/unmatched.txt'
DIRECT_RECORDS = 'tests/testdata/records.json'

LM_COL_CODE = 'Affcode'
LM_COL_AFFL = 'Affil'
LM_COLS = [LM_COL_CODE,LM_COL_AFFL]
LM_TEXTLEN = 8192
LM_THRESHOLD = -0.0

MATCH_COL_AFFL = 'Affil'
MATCH_COLS = [MATCH_COL_AFFL]

CV_PARAM_ANALYZER = 'word'
CV_PARAM_DECERR = 'replace'
CV_PARAM_NGRAMRANGE = (1,4)

SGDC_PARAM_LOSS = 'log'
SGDC_PARAM_PENALTY = 'elasticnet'
SGDC_PARAM_ALPHA = 7.e-8
SGDC_PARAM_RANDOM = 12345
SGDC_PARAM_CPU = 1
