# affil_match
Use scikit-learn to assign affiiations using machine learning based on an input model of affiliation ids and characteristics.

# Requirements
* Python 2.7+
* External Modules: pandas, sklearn (and their dependencies)
* Note: will take advantage of multiple cores/threads if available

# Introduction

A basic description of what this code does is: 

* input unknown affiliation metadata
* output the best guess for the affiliation's canonical ID, and 
* output a score that provides basic assessment of how good the match is.

Guesses for affiliation are made based on material it learns from a tab-delimited file containing (at least) two columns: an ID string of any form (numeric, mixed alphanumeric, or anything that's a unique string), and some text data containing words that the algorithm might see for an affiliation matching the ID.  This learning step appears once, before any guesses are made, and then all guessing is done in bulk for one or more input affiliation metadata strings.  The learning data were generated by CSG, with editing and postprocessing by MT.

As an example, a learning model entry that might detect an affiliation with CfA could be:

```
ABC123  Harvard Smithsonian Center for Astrophysics Cambridge CfA Garden 60 Cambridge, MA 02138 Massachusetts CfA Center Astrophysics Harvard Harvard-Smithsonian Center for Astrophysics CfA CfA Center Astrophysics 60 Garden Street MS-83 Cambridge CfA Cntr for Astrophys Harvard ..... [and so on]
```

Additional lines would have ID-text data pairs for a different institution (e.g. MIT, CalTech, GSFC, University of Delaware, and so on).  Currently the production model in use has over 5000 different affiliations with 15 MB of related text spread among those records.

These learning data are tokenized and analyzed using several scikit-learn routines to create a learning model, which is basically a matrix that will be used to invert a matrix of tokenized incoming test data to obtain matches to institutional IDS and the statistical scores of these matches.  Currently the input and output are defined using the input files that CSG developed as part of the affiliation assignment project (2017), but the flexibility exists to change this or allow user-defined formats for any and all inputs as needed.  Custom learning models can also be developed and substituted.

# Basic/Test Example

The code to be used for production is currently *affil_match.py*, and it is currently reading the file *config.py* to figure out where its input learning model and other data are located.  For this simple example, the learning model is located in *test/tiny_learner.txt* and the data to be tested are in *test/tiny_target.txt*; there is an additional file with affiliation parent-child relationships in *config/parent_child_facet_inst.tsv* that is also required.  All of these files are in the format defined in config.py:

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
(Modifying config.py will discussed later.)

Now consider the following learning model, test/tiny_learner.txt:
```
61814	Harvard-Smithsonian Center for Astrophysics CfA Harvard University Cambridge Massachusetts
5972	University of Delaware UD Newark DE
4423	New Mexico State University NMSU Las Cruces NM 88003
DEFG	Orange Julius, The Mall, like, oh my gawd!
EFGH	Charcoal Pit, Concord Pike, Wilmington, DE
FGHI	Massachusetts Audubon Society Mass Audubon 208 South Great Road, Lincoln, MA
5112	X-Division Los Alamos National Laboratory National Nuclear Security Administration New Mexico 87545
```
and target data, test/tiny_target.txt:

```
2017ABCD...17..128T	University of Delaware	Tucker, Orenthal	5/0
2017OPQR...19...43P	CfA, Cambridge, MA 02138	Poda, D.	37/0
1948XYU.....1..999L	Miskatonic U.	Lovecraft, H.P.	0/0
```

By eye, you can guess that the target records have the following affiliations

* 5972 (University of Delaware)
* 61814 (CfA)
* (none of the above)

Using config.py as shown above, execute the following at the command line:

```
user@host% python affil_match.py test/tiny_target.txt
```

Execution of the example should take about a second, and produce a file called **matches.txt**, shown below:

```
5972	5972	2017ABCD...17..128T	5/0	5.73
61814	8264	2017OPQR...19...43P	37/0	3.52
61814	8264	1948XYU.....1..999L	0/0	1.0
```

In order, the tab-delimited columns are: 
* Primary matching ID
* ID of parent if it exists, or the primary ID if not
* Input bibcode
* Author number in list (1st == 0) / Affiliation number per author if multiple (1 affiliation == 0)
* Match score: float with minimum value of 1.00 (max dependent on input learning model)

The primary matching IDs are obtained from the LM_COL_CODE column of the best match in test/tiny_learner.txt, while the parent ID comes from config/parent_child_facet_inst.tsv (LM_INFILE and PC_INFILE, respectively).  Note that the third result yields the same (and in this case incorrect) guess as another input test affiliation (61814), but its score is low (1.0) compared to the score (3.52) for the input affiliation that is a valid match.  It could've returned any of the others as a (bad) match, but happened to return Harvard-Smithsonian CfA in this case.

# Scoring

The output scores are determined by several factors including the number of different entries in the learning model, the number and frequency of words in each record, and the number and frequency of words across all records.  The scores are essentially relative likelihood that a given record is a match, and normalized by the number of possible matches.  For example, if a learning model has 1000 affiliations, the raw score could be 0.00578, which is then normalized by (1/N(affils)), giving 5.78.  A match with a score less than 1.25 is almost certainly wrong; a score of 1.00 technically means that any entry in the learning model is an equally good match.  Conversely a score of 5.0 is likely to be an extremely good (but not necessarily correct!) match.

The possibility exists for low-scoring matches to be right, and for high-scoring matches to be wrong.  It is a limitation of the method that cannot be overcome *except* by pruning the learning model to remove potential ambiguities.  As an example, consider an affiliation string given in a paper simply as **ALMA**, with no additional disambiguating text like an address.  That is likely to match an entry for the Atacama Large Millimeter Array, assuming the learning model includes the acronym "ALMA" among the possible matching words.  However, it may also match an entry for "Alma College", a small liberal-arts institution in Michigan, United States.  The easiest solution for preventing exceptions like this are to remove the less-likely of two or more ambiguous entries, i.e. edit the learning model to remove "Alma College" as a model entry.  This is less than ideal, but should provide us with more unambiguously correct answers (assuming more papers come from authors at Atacama than from Alma College).  Just realize that you will never be able to match 100 percent of all affiliations in that case, *and* that the possibility exists for legitimate entries for Alma College to then be classified as affiliated with Atacama.  The latter case becomes less likely the more additional data is included in both the learning model affiliation strings and the input test strings (e.g. Department name, street address, mail stop, state, country, etc).  Obviously, it would benefit the authors themselves if they give more complete/canonical affiliation data in their papers, but we don't control that.

A suggested way of selecting how matches are dealt with based on score is:

* Score > 2.5: accept with no changes
* 1.5 > Score > 2.5: try some other means of verification (select parent, try word counts or close matches)
* Score < 1.5: reject

Again, you will see examples where things with Score > 2.5 are wrong and Score < 1.5 are right.  The only solution to this is to validate, clean, and prune the input learning model as thoroughly as possible.

(Further discussion of the learning model is outside the scope of this README.)

# Production Example

To see a real-life application, do the following:

* Uncompress the files *config/learning_model.dat.gz*, *config/parent_child_facet_inst.tsv.gz*, and *test/test_data.gz*
* Edit *config.py* and set LM_INFILE = 'config/learning_model.dat'
* From the command line, execute
```
user@host% python affil_match.py test/test_data
```

Results will be in matches.txt; I recommend sorting this file using sort -n -r -k 5 -t '[TAB]'.  Note: if you would like to see this file with the actual affiliation strings instead of just IDs, use *am_test.py* instead of *affil_match.py*.  The results should be otherwise identical.