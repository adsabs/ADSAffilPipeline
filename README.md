# affil_match
Use scikit-learn to assign affiiations using machine learning based on an input model of affiliation ids and characteristics.

# Introduction

The most basic description of what this code does simple: take in an input string, and return two things: the best guess for the affiliation ID, and a score that provides basic assessment of how good the match is.

The material it learns is found in a tab-delimited file containing (at least) two columns: an ID string of any form (numeric, mixed alphanumeric, or anything that's a unique string), and some text data containing words that the algorithm might see for an affiliation matching the ID.

As an example, a learning model that might detect an affiliation with CfA could be:

```
ABC123  Harvard Smithsonian Center for Astrophysics Cambridge CfA Garden 60 Cambridge, MA 02138 Massachusetts CfA Center Astrophysics Harvard Harvard-Smithsonian Center for Astrophysics CfA CfA Center Astrophysics 60 Garden Street MS ..... [and so on]
```

Additional lines would have ID-text data pairs for a different institution (e.g. MIT, CalTech, GSFC, University of Delaware, and so on).  Currently the production model in use has over 5000 different affiliations with 15 MB of related text spread among those records.

These learning data are tokenized and analyzed using several scikit-learn routines to create a learning model, which is basically a matrix that will be used to transform incoming test data to obtain matches to institutional IDS and the statistical scores of these matches.  Currently the input and output are defined using the input files that CSG developed as part of the affiliation assignment project (2017), but the flexibility exists to change this or allow user-defined formats for any and all inputs as needed.

# Example

The code to be used for production is currently *affil_match.py*, and it is currently reading the file *config.py* to figure out where its input learning model and other data are located.  For the basic example, the learning model is located in *test/tiny_learner.txt* and the data to be tested are in *test/tiny_target.txt*; there is an additional file with affiliation parent-child relationships in *config/parent_child_facet_inst.tsv* that is also required.  All of these files are in the format defined in config.py:

```
#!/usr/bin/env python

PC_INFILE = 'config/parent_child_facet_inst.tsv'
LM_INFILE = 'test/tiny_learner.txt'

OUTPUT_FILE = 'matches.txt'

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
```

(Reconfiguring this will described later.)

To execute the code:
```
user% python affil_match.py test/tiny_target.txt
```

Execution of the example should take less than a second, and produce a file called **matches.txt**, shown below:

```
5972	5972	2017ABCD...17..128T	5/0	5.73
61814	8264	2017OPQR...19...43P	37/0	3.52
61814	8264	1948XYU.....1..999L	0/0	1.0
```

In order, the columns are: 
* Primary matching ID
* ID of parent if it exists, or self
* Input bibcode
* Author number in list (1st == 0) / Affiliation number per author if multiple (1 affiliation == 0)
* Match score: float with minimum value of 1.00 (max dependent on input learning model)

The primary matching IDs are obtained from the LM_COL_CODE column of the best match in test/tiny_learner.txt, while the parent ID comes from config/parent_child_facet_inst.tsv (LM_INFILE and PC_INFILE, respectively).  Note that the third result yields the same (and in this case incorrect) guess as another input test affiliation (61814), but its score is low (1.0) compared to the score (3.52) for the input affiliation that is a valid match.

# Scoring

The output scores are determined in part by the number of possible affiliations in the learning model, and is normalized by that number.  The scores are essentially relative likelihood that a given record is a match.  For example, if a learning model has 1000 affiliations, the raw score could be 0.00578, which is then normalized by (1/N(affils)), or 5.78.  A match with a score less than 1.25 is almost certainly wrong; a score of 1.00 technically means that any entry in the learning model is an equally good match.  Conversely a score of 5.0 is likely to be an extremely good (but not necessarily correct!) match.

The possibility exists for low-scoring matches to be right, and for high-scoring matches to be wrong.  It is a limitation of the method that cannot be overcome *except* by pruning the learning model to remove potential ambiguities.  As an example, consider an affiliation string given in a paper as **ALMA**.  That is likely to match a dictionary entry for the Atacama Large Millimeter Array, assuming it includes the acronym "ALMA" among the matching words.  However, it may also match an entry for "Alma College", a small liberal-arts institution in Michigan, United States.  The easiest solution for preventing exceptions like this are to remove the less-likely of two or more ambiguous entries, i.e. edit the learning model to remove "Alma College" as a possible entry.  This is less than ideal, but should provide us with more unambiguously correct answers (assuming more papers come from authors at Atacama than from Alma College).


