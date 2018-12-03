#! /usr/bin/env python

import config

# THIS IS TIME INTENSIVE: TRY WRITING SOMETHING FASTER!
def make_learner(aff_dict):
    aff_split = {}
# invert the affiliation dictionary: keys are the aff_id's, and lists of the
# strings are values.
    for k,v in aff_dict.items():
        if v in aff_split:
            aff_split[v].append(k)
        else:
            aff_split[v] = [k]

# for each affiliation, remove any strings that are substrings of another
# (to save on size)
    for k,v in aff_split.items():
        newlist = []
        for x in v:
            keep = True
            for y in v:
                if x != y:
                    if x in y:
                        keep = False
            if keep:
                newlist.append(x)
            vout = (" ".join(newlist))[0:(config.LM_TEXTLEN-1)]

        aff_split[k] = vout[0:vout.rfind(' ')].rstrip()

# aff_split is now your learning model dictionary with affil_ids as keys
    return aff_split
