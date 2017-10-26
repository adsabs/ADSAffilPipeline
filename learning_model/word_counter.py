#!/usr/bin/env python
import pandas as pd

def parents_children(infile):
    f=open(infile,'rU')

    children=dict([])
    parents=dict()
    canonical=dict()
    short_canon=dict()
    clist=[]

    for l in f.readlines():
        (p,c,mcn,cn)=l.rstrip().split('\t')
        clist.append(c)
        if len(p) > 0:
            try:
                children[p]
            except KeyError:
                children[p]=[c]
            else:
                children[p].append(c)
            parents[c]=p
        canonical[c]=cn
        short_canon[c]=mcn
    f.close()

    return children,parents,canonical,short_canon


def counter_files(filename,canonical,short_canon):
    faff=open(filename,'r')
    outfile=filename+".count"
    aff=''
    wdict=dict()
    cdict=dict()
    for l in faff.readlines():
        l=l.rstrip()
        (a,s)=l.split('\t')
        s=s.replace(',','').replace('-','')
        words=s.split()
        for w in list(set(words)):
            try:
                wdict[w]
            except KeyError:
                wdict[w]=s.count(w)
            else:
                wdict[w]=wdict[w]+s.count(w)
    faff.close()
    oaff=open(outfile,'w')
    word_frame=pd.DataFrame(wdict.items(),columns=['Word','Count'])
    word_frame.sort_values('Count',ascending=False,inplace=True)
    words=word_frame['Word'].tolist()
    counts=word_frame['Count'].tolist()
    wlist=[]
    maxcount=max(counts)
    for w,c in zip(words,counts):
        cx=1./(maxcount*0.02)
        if (float(c)*cx) >= 1.:
            outs=(w+' ')*int(c*cx)
            wlist.append(outs)
    try:
        canonical[a]
    except KeyError:
        print("No key: %s"%a)
    else:
        for i in range(0,30):
            wlist.append(canonical[a])
            wlist.append(short_canon[a])
    oaff.write("%s\t%s\n"%(a," ".join(wlist)))
    oaff.close()
    return

def main():
    import glob
    dirs=['A', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    (children,parents,canonical,short_canon)=parents_children('pc_facet_ascii.tsv')
    for d in dirs:
        dfind=d+'/*'
        files=glob.glob(dfind)
        for f in files:
            counter_files(f,canonical,short_canon)
    return

if __name__ == '__main__':
    main()
