#!/usr/bin/env python

aff_file='affils_ascii.tsv'
pcf_file='pc_facet_ascii.tsv'
files=[aff_file,pcf_file]

ntab_count={aff_file:2,pcf_file:4}

for f in files:
    test=open(f,'r')
    badlines=list()
    i=0
    for l in test.readlines():
        ntab=l.split('\t')
        xout=''
        if len(ntab) != ntab_count[f]:
            xout=f+': '+str(i)+': '+l.rstrip()
            badlines.append(xout)
        i+=1
    for l in badlines:
        print(l)
    test.close()
