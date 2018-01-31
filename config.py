#!/usr/bin/env python

#ADD Documentation to make it clear what these variables are!

# These infiles are input model data. 
# * LM specifies the file that maps institutional IDs to words that you
#   may see.
# * PC specifies relationship between parent IDs (e.g. University of CA),
#   and child IDs (UC Berkeley, IGPP, UCLA, etc.)
LM_INFILE = 'config/learning_model.dat'
PC_INFILE = 'config/pc_facet_ascii.tsv'



# This is the file where your output goes
OUTPUT_FILE = 'aff_match_OUT.txt'



# These are column headings used in the learning model file.  These are used
# in the case where the structure of a learning model file may be different,
# than a simple two column format with 'Affcode' and 'Affil' in that order.
# In that case, the input file should have a column with the same name as
# LM_COL_CODE, LM_COL_AFFL, and an array that defines where those columns
# are relative to the whole document (e.g. ['foo','bar',LM_COL_AFFL,'baz',
# 'LM_COL_CODE','lol']
LM_COL_CODE = 'Affcode'
LM_COL_AFFL = 'Affil'
LM_COLS = [LM_COL_CODE,LM_COL_AFFL]



MATCH_COL_BIB = 'bibcode'
MATCH_COL_AFFL = 'Affil'
MATCH_COL_AUTH = 'Author'
MATCH_COL_AISQ = 'sequence'
MATCH_COLS = [MATCH_COL_BIB,MATCH_COL_AFFL,MATCH_COL_AUTH,MATCH_COL_AISQ]

CV_PARAM_ANALYZER = 'word'
CV_PARAM_DECERR = 'replace'

SGDC_PARAM_LOSS = 'log'
SGDC_PARAM_PENALTY = 'elasticnet'
SGDC_PARAM_ALPHA = 1.e-4
#SGDC_PARAM_RANDOM = None
SGDC_PARAM_RANDOM = 12345
#SGDC_PARAM_CPU = 4
#SGDC_PARAM_CPU = 1
SGDC_PARAM_CPU=-1

