#!/usr/bin/env python
#
# affil_match_new -- M. Templeton, August 10, 2017
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
    print("Done read_data: %s"%lf)
    return(df)



def combine_dictionary(df):

# This function takes the contents of the input dataframe, and merges all
# rows having the same identifier.  The Affiliations_all_clean.tsv file
# consists of several hundred thousand rows with known affiliations and
# aliases for about 5000 Institutions.  All of the affil/alias lists are
# being condensed into a single, long-string (ltxt) or into a list of
# unique words (words; original method, not recommended).
#
# Note this step takes a long time to execute, because of the join.  The
# string variable 'ltxt' is very long for most records, and I think I am
# using the most efficient method for concatenating records in the Affil
# column.

    affil_codes=df['Affcode'].unique()
    data=[]
    for id in affil_codes:
        mdf=df.loc[df.Affcode==id]
        ltxt=' '.join(mdf.Affil.astype('U',errors='ignore').values.tolist())
        data.append({'Affcode':id,'Affil':ltxt})
    tdf=pd.DataFrame.from_dict(data,dtype=str)
    print("Done combine_dictionary.")
    return(tdf)



def column_to_list(df,colname):
    col_list=df[colname].astype('U',errors='ignore').values.tolist()
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
# to the point that a machine with 24G wired may even start swapping.
# What does it is the application of TfidTransformer in the line
#
#        cvf=tft.fit_transform(ac)
#
# These are supposed to use sparse-matrix solvers, so I wonder if this is
# just an indication of how large the matrix is. Regardless, this is a known
# issue related to the method being used.  The only other option is using
# some kind of incremental learning method.

    alist=column_to_list(df,'Affil')

    cv=CountVectorizer(analyzer='word',decode_error='ignore')
#   cv=CountVectorizer(ngram_range=(2,2),analyzer='word',decode_error='ignore')
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



def match_entries(dict_frame,match_frame,crit,cv,tft,clf,colnames):

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

    match_namelist=column_to_list(match_frame,'Affil')

    ncv=cv.transform(match_namelist)
    ntf=tft.transform(ncv)
    predicted=clf.predict(ntf)
    probs=clf.predict_proba(ntf)

#!This should be split into two functions, where the code below should
#!be in its own function, like "analyze_stats".  It's more than likely
#!this may be automated separately to do some kind of comparison of
#!different crit values.

    match_aflist=[]
#   fs=open('statprint.dat','w')
    for p in probs:
        pzero=p.mean()
        pstd=p.std()
        if (pstd != 0.):
            p=abs((p-pzero)/pstd)
#       fs.write("\n\n%.6e,%.6e\n"%(pzero,pstd))
#       for x in p:
#           fs.write("%.6e\n"%x)
        match_aflist.append(dict_frame.Affcode[p>crit].tolist())

    match_frame['Affcodes']=match_aflist
    print("Done matching.  Writing results...")

    print_results(match_frame,colnames)
    return




def get_options():
    import argparse
    parser=argparse.ArgumentParser(description='Affil matching w/sklearn')
    parser.add_argument('infile',type=str,nargs=1,help='file name of input'
                        +' dictionary')
    parser.add_argument('testfile',type=str,nargs=1,help='file name of'
                        +' data to be tested')
    parser.add_argument('crit',type=float,nargs='?',default=30.0,
                        help='threshold crit for positive matching')
    args=parser.parse_args()
    return args.infile[0],args.testfile[0],args.crit



def main():
#   get user inputs for filenames, crit value
    (learn_file,target_file,minsigma)=get_options()

#   read the dictionary data
    affil_frame=read_data(learn_file,['Affcode','Affil'])

#   merge the dictionary data by Affiliation code
    dict_frame=combine_dictionary(affil_frame)

#   transform dictionary using sklearn
    (cvec,transf,cveclfitr,affil_list)=learn_dictionary(dict_frame)

#   columns in the target data: this is wonky, assumes test file form = const
    match_columns=['RawAffil','Affil','BibCode']

#   read the target data
    match_frame=read_data(target_file,match_columns)

#   classify and output
    match_entries(dict_frame,match_frame,minsigma,cvec,transf,cveclfitr,match_columns)

#   END


if __name__ == '__main__':
    main()
    print("Done!")
