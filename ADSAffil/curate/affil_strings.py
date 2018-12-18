import json
from datetime import datetime
from ADSAffil import utils
import cPickle as pickle

def load_simple(filename):
    inputrecords = []
    with open(filename,'rU') as fa:
        i=0
        for l in fa.readlines():
            i=i+1
            ll = utils.convert_unicode(l)
            try:
                (aff_id,aff_string) = ll.rstrip().split('\t')
            except:
                raise BaseException("Fatal line read error in affil_strings.load, line: %s"%i)
            else:
                inputrecords.append(ll)
    return inputrecords

#           if aff_string.strip() != '':
#               try:
#                   aff_string = utils.encode_string(aff_string)
#               except:
#                   print ("encoding problem on line %s, skipping."%i)
#               else:
#                   record = (aff_id,aff_string,False,False,True,0,0)
#                   records.append(record)
#           else:
#               print ("empty affil string ignored")
#
#   return records

def dump_affil_pickle(aff_dict,filename):
    if len(aff_dict.keys())>0:
        try:
            with open(filename,'wb') as fp:
                pickle.dump(aff_dict,fp,pickle.HIGHEST_PROTOCOL)
#               pickle.dump(aff_dict,fp,-1)
        except:
            raise BaseException("Error writing to pickle file %s"%filename)
    else:
        print ("Warning: aff_dict is empty!")
