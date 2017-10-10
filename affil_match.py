#!/usr/bin/env python
#
# amp_beta -- M. Templeton, September 27, 2017
#
# beta testing for the production code
#----------------------------------------------------------------------------

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier


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
        df=pd.read_csv(f,sep='\t',names=colnames)
        f.close()
    print("Done read_data: %s"%lf)
    return(df)



def column_to_list(df,colname):
    col_list=df[colname].astype('U',errors='ignore').values.tolist()
    return col_list



def learn_dictionary(df):

# This function creates the framework that sklearn is using to learn the
# characteristics of the text.  The transforms are first created using the
# input data here, and then the resulting models are applied to the data
# to be matched (see match_entries below).
#

    alist=column_to_list(df,'Affil')

    cv=CountVectorizer(analyzer='word', decode_error='replace')
    ac=cv.fit_transform(alist)
    tft=TfidfTransformer()
    cvf=tft.fit_transform(ac)
    clf=SGDClassifier(loss='log', penalty='elasticnet',
                      alpha=1.e-4).fit(cvf,df.index)
    print("Done learn_dictionary.")
    return(cv,tft,clf,alist)



def match_entries(dict_frame,match_frame,cv,tft,clf,colnames):

# This is where the transforms created in learn_dictionary are applied
# to the data being matched.
#

    match_namelist=column_to_list(match_frame,'Affil')

    ncv=cv.transform(match_namelist)
    ntf=tft.transform(ncv)
    predicted=clf.predict(ntf)
    probs=clf.predict_proba(ntf)

    match_aflist=[]
    match_afscore=[]
    match_dict_nwords=[]
    match_dict_nuniq=[]
    match_score_diff=[]
    nids=len(dict_frame)
    minprob=1./float(nids)
    for p,ip in zip(probs,predicted):
        p.sort()
        psig=p.std()
        difcrit=(psig*3.0)
        match_aflist.append(dict_frame.Affcode[ip])
        match_afscore.append(p.max())
        match_dict_nwords.append(len(dict_frame.Affil[ip].split()))
        match_dict_nuniq.append(len(set(dict_frame.Affil[ip].split())))
        match_score_diff.append((p[-1]-p[-2])-difcrit)

    match_frame['Affcodes']=match_aflist
    match_frame['Affscore']=match_afscore
    match_frame['Dnwords']=match_dict_nwords
    match_frame['Dnuniq']=match_dict_nuniq
    match_frame['ScoreD']=match_score_diff
    return match_frame
    


def parents_children():
    infile='ids_canonical_MT_2017Oct10.tsv'
    f=open(infile,'rU')

    children=dict([])
    parents=dict()
    canonical=dict()
    clist=[]

    for l in f.readlines():
        (p,c,cn)=l.split('\t')
        clist.append(c)
        if len(str(p)) > 0:
            try:
                children[str(p)]
            except KeyError:
                children[str(p)]=[str(c)]
            else:
                children[str(p)].append(str(c))
            parents[str(c)]=str(p)
        canonical[str(c)]=cn
    f.close()

    return children,parents,canonical

def get_parent(affil,parents):
    try:
        parents[affil]
    except KeyError:
        return affil
    else:
        return get_parent(parents[affil],parents)


def print_output(prob_min,match_frame):
    affil_string=match_frame['Affil'].tolist()
    bibcode_string=match_frame['bibcode'].tolist()
    sequence_string=match_frame['sequence'].tolist()
    test_answers=match_frame['Affcodes'].tolist()
    test_scores=match_frame['Affscore'].tolist()
    test_nword=match_frame['Dnwords'].tolist()
    test_nuniq=match_frame['Dnuniq'].tolist()
    test_scored=match_frame['ScoreD'].tolist()
    outfile=open('answers.txt','w')
    (children,parents,canonical)=parents_children()
    for a,ta,bib,seq,ts in zip(affil_string,test_answers,bibcode_string,sequence_string,test_scores):
        try:
            canonical[ta]
        except KeyError:
            b="ERROR:Bad Key!"
        else:
            b=canonical[ta].strip()
        if (ts >= 2.*prob_min):
            outfile.write("YES\t%s\t%s\t%s\t%s\t%s\t%f16.10\n"%(a,ta,b,bib,seq,ts))
        else:
            outfile.write("NO\t%s\t%s\t%s\t%s\t%s\t%f16.10\n"%(a,ta,b,bib,seq,ts))
    outfile.close()
    return



def get_options():
    import argparse
    parser=argparse.ArgumentParser(description='Affil matching w/sklearn')
    parser.add_argument('infile',type=str,nargs=1,help='file name of input'
                        +' dictionary')
    parser.add_argument('testfile',type=str,nargs=1,help='file name of'
                        +' data to be tested')
    args=parser.parse_args()
    return args.infile[0],args.testfile[0]



def main():
#   get user inputs for filenames
    (learn_file,target_file)=get_options()

#   read the dictionary data
    dict_frame=read_data(learn_file,['Affcode','Affil'])

#   transform dictionary using sklearn
    (cvec,transf,cveclfitr,affil_list)=learn_dictionary(dict_frame)

    match_columns=['bibcode','Affil','Author','sequence']

#   read the target data
    match_frame=read_data(target_file,match_columns)

#   classify and output
    print_output((1./len(dict_frame)),match_entries(dict_frame,match_frame,cvec,transf,cveclfitr,match_columns))


#   END


if __name__ == '__main__':
    main()
    print("Done!")
