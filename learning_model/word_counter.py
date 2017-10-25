#!/usr/bin/env python
import pandas as pd

def counter_files(filename):
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
    butts=pd.DataFrame(wdict.items(),columns=['Word','Count'])
    butts.sort_values('Count',ascending=False,inplace=True)
    words=butts['Word'].tolist()
    counts=butts['Count'].tolist()
    wlist=[]
    maxcount=max(counts)
    for w,c in zip(words,counts):
        cx=1./(maxcount*0.02)
        if (float(c)*cx) >= 1.:
            outs=(w+' ')*int(c*cx)
            wlist.append(outs)
    oaff.write("%s\t%s\n"%(a," ".join(wlist)))
    oaff.close()
    return

def main():
    import glob
    dirs=['A', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    for d in dirs:
        dfind=d+'/*'
        files=glob.glob(dfind)
        for f in files:
            counter_files(f)
    return

if __name__ == '__main__':
    main()
