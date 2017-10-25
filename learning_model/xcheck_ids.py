#!/usr/bin/env python

fids=open('parent_child_facet_inst_MT_2017Oct19.tsv','rU')
faff=open('Affiliations_all_MT_2017Oct19_ascii.tsv','rU')

parent=dict()
child=dict()
affil=dict()
for l in fids.readlines():
    (p,c,affshort,aff)=l.split('\t')
    if p != '' and p != 'PARENT':
        parent[p]=aff
    if c != '' and c != 'CHILD':
        child[c]=aff
fids.close()

for l in faff.readlines():
    (a,aff)=l.split('\t')
    if a != '':
        affil[a]=aff
faff.close()

parents=parent.keys()
children=child.keys()
affils=affil.keys()


#check that all parents have a "child" entry for themselves
for p in parents:
    try:
        child[p]
    except KeyError:
        print("Parent %s doesn't have a child entry: %s"%(p,parent[p].rstrip()))
        children.append(p)
    else:
        pass

#check that all children have an entry in affils
for c in children:
    try:
        affil[c]
    except KeyError:
        print("Child %s doesn't have an entry in affils: %s"%(c,child[c].rstrip()))
    else:
        pass
    
#check that all affils have an entry in children
for a in affils:
    try:
        child[a]
    except KeyError:
        print("Affil %s doesn't have an entry in child: %s"%(a,affil[a].rstrip()))
    else:
        pass
    
