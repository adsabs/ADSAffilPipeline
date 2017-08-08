#!/usr/bin/env python
#
# amx (affil_match) -- M. Templeton
#
# Takes /proj/ads/abstracts/ast/update/AFFILS/Affiliations_all_clean.tsv
# as an input dictionary.  Tries to figure out unresolved references in
# /proj/ads/abstracts/ast/update/AFFILS/affils.ast.20170614_1156.srcu
# Uses a bag-of-words approach with scikit-learn.
#----------------------------------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
#from sklearn.linear_model import SGDClassifier




def read_data(lf,colnames):

# Reads in tab-delimited files into pandas data frames.  Note this is
# used for both the input dictionary and the data being analyzed, and
# requires that you give it the column names in advance.

    try:
        f=open(lf,'rU')
    except IOError:
        print("%s cannot be opened.  Exiting."%(lf))
        quit()
    else:
        df=pd.read_csv(f,sep='\t',names=colnames,dtype=str)
        f.close()
    print("Done read_data: %s\n"%lf)
    return(df)



def combine_dictionary(df):

# This function takes the contents of the input dataframe, and merges all
# rows having the same identifier.  The Affiliations_all_clean.tsv file
# consists of several hundred thousand rows with known affiliations and
# aliases for about 5000 Institutions.  All of the affil/alias lists are
# being condensed into a single, long-string (ltxt) or into a list of
# unique words (words; original method, not recommended).
#
# Note this step takes a long time to execute, and I suspect it's a problem
# with the code that's appending the row [id,ltxt] to tdf.  Is there a 
# better/faster way to add rows to a Pandas DataFrame?

    affil_codes=df['Affcode'].unique()
    tdf=pd.DataFrame(index=[],columns=['Affcode','Affil'])
    for id in affil_codes:
        all_words=[]
        try:
            mdf=affil_frame.loc[affil_frame.Affcode==id]
        except TypeError:
            print("I got a type error for id: %s"%(id))
        else:
            wgl=(mdf.Affil.tolist())
            ltxt=''
            for g in wgl:
                try:
                    ltxt+=' '+g
                except TypeError:
                    dummy=0
                else:
                    dummy=0
            all_words=ltxt.split()
            words=' '.join(list(set(all_words))).replace(",","").strip().rstrip()
            tdf.loc[tdf.shape[0]]=[id,ltxt]  #change ltxt to words if you want
    print("Done combine_dictionary.")
    return(tdf)


def column_to_list(df,colname):
    col_list=df[colname].values.astype('U').tolist()
    return col_list


def learn_dictionary(df):

# This function creates the framework that sklearn is using to learn the
# characteristics of the text.  The transforms are first created using the
# input data here, and then the resulting models are applied to the data
# to be matched (see match_entries below).  
#
# There is code here to use either word- or n-gram-based matching.  I have
# been using word based and I think it works ok.
#
# There's also code to switch from using MultinomialNB (bayesian) or
# SGDClassifier.  SGDClassifier hasn't been tested in the rewrite yet,
# use with caution here.
#
# This stage, and match_entries, currently take **enormous** amounts of RAM
# to the point that a machine with 24G wired may even start swapping.  These
# are supposed to use sparse-matrix solvers, so I wonder if the data frames
# are being formed without zeroes and it's really trying to solve a matrix
# as huge as these are....  Either way, if this crashes, it does so either
# here or in match_entries.

    alist=column_to_list(df,'Affil')

    cv=CountVectorizer(analyzer='word',decode_error='ignore')
#   cv=CountVectorizer(analyzer='char_wb',ngram_range=(2,6),
#                      decode_error='ignore')

    ac=cv.fit_transform(alist)

    tft=TfidfTransformer()
    cvf=tft.fit_transform(ac)

    clf=MultinomialNB().fit(cvf,df.index)
#   clf=SGDClassifier(loss='hinge', penalty='l1',alpha=1e-4,n_iter=1,
#                     random_state=3).fit(cvf,df.index)

    print("Done learn_dictionary.")
    return(cv,tft,clf,alist)



def print_results(df,printcol):

# Takes the resulting data frame of matched and unmatched entries and
# prints them to separate output files.  The unmatched files are output
# in (hopefully) the same format as the input file to facilitate retesting
# and rerunning with different matching criteria.
#
# The matched entries are identical, but have an extra column with a list
# of Affiliation codes from Affiliation_ast_clean.tsv that match the record.
#
    fm=open('aff_matched.txt','w')
    fu=open('aff_unmatched.txt','w')

    bmatch=df.Affcodes.apply(lambda x: len(x)!=0)
    df.loc[bmatch].to_csv(fm,sep='\t',index=False,header=False)
    df.loc[~bmatch].to_csv(fu,sep='\t',index=False,header=False,
                                columns=printcol)
    fm.close()
    fu.close()
    return



def match_entries(df,crit,cv,tft,clf):

# This is where the transforms created in learn_dictionary are applied
# to the data being matched.  Again, this may take an enormous amount of
# memory, so do not be surprised if it dies here.
#
# The variable crit is what I'm calling "minsigma" in the main body of the
# program.  This is a misnomer because I'm assuming probs are normally
# distributed, and they're not.  I need to read up on how to model this,
# but I believe it's better matched by a chi2 distribution.
#
# Regardless, increase "minsigma" in main to be much more strict about
# matches.  Lower sigma, more matches, with more false positives, and
# vice versa.

    ncv=cv.transform(match_namelist)
    ntf=tft.transform(ncv)
    predicted=clf.predict(ntf)
    probs=clf.predict_proba(ntf)
    pzero=probs.mean()
    pstd=probs.std()
    probs=abs((probs-pzero)/pstd)

    match_aflist=[]
    for p in probs:
        match_aflist.append(dict_frame.Affcode[p>crit].tolist())

    match_frame['Affcodes']=match_aflist
    print("Done matching.  Writing results...")

    print_results(match_frame,['RawAffil','Affil','BibCode'])
    return



# BEGIN MAIN

# user set params -- get via cmd line arguments, move to a function?

learn_file='Affiliations_all_clean.tsv'
target_file='affils.ast.20170614_1156.srcu'
minsigma=50.0

# Read the input file to be learned
affil_frame=read_data(learn_file,['Affcode','Affil'])

# Turn the input data into a dictionary-like dataframe
dict_frame=combine_dictionary(affil_frame)

# Model the dictionary using sklearn...
(cvec,transf,cveclfitr,affil_list)=learn_dictionary(dict_frame)

# Read the file with data to be matched
match_frame=read_data(target_file,['RawAffil','Affil','BibCode'])

# Create an array from match_frame containing the affiliations to be matched
match_namelist=column_to_list(match_frame,'Affil')

# Match, and print out the matches and non-matches separately
match_entries(match_namelist,minsigma,cvec,transf,cveclfitr)

print("Done!")
