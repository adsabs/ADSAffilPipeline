import json
from datetime import datetime


def load_simple(filename):

    affil_canonical = {}
    affil_abbrev = {}
    affil_parent = {}
    affil_child = {}

    with open(filename,'rU') as fpc:
        for l in fpc.readlines():
            try:
                (parent,child,shortform,longform) = l.rstrip().split('\t')
            except:
                print "Line error: ",l
            else:
                if str(child) not in affil_canonical:
                    affil_canonical[str(child)] = longform
                    affil_abbrev[str(child)] = shortform
                
                if str(parent) != "":
                    if str(child) not in affil_parent:
                        affil_parent[str(child)] = [str(parent)]
                    else:
                        affil_parent[str(child)].append(str(parent))
                    if str(parent) not in affil_child:
                        affil_child[str(parent)] = [str(child)]
                    else:
                        affil_child[str(parent)].append(str(child))

    ids = affil_canonical.keys()
    print "There are %s unique canonical affids."%len(ids)
    ids.sort()
    records = []

    for i in ids:
        if i not in affil_parent:
            affil_parent[i] = ["-"]
        if i not in affil_child:
            affil_child[i] = ["-"]

        affil_parent[i] = '{"parents":'+str(affil_parent[i]).replace('\'','"')+'}'
        affil_child[i] = '{"children":'+str(affil_child[i]).replace('\'','"')+'}'

        record = (i,affil_canonical[i],affil_abbrev[i],affil_parent[i],affil_child[i])
        records.append(record)

    return records
