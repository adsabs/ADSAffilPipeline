import re
import bs4
import unidecode
import warnings
import json
import cPickle as pickle
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="unidecode")


srs = re.compile(r'[-!?.,;:/\\]')

def convert_unicode(s):
    try:
        lo = s.decode('utf-8').encode('ascii','xmlcharrefreplace')
    except UnicodeDecodeError:
        try:
            lo2 = s.decode('cp1252').encode('ascii','xmlcharrefreplace')
        except UnicodeDecodeError:
            pass
        else:
            s = lo2
    except AttributeError:
        pass
    else:
        s = lo
    return(s)

def back_convert_entities(rec):
    outrec = []
    output_block = bs4.BeautifulSoup(rec, "lxml").find_all('p')
    for l in output_block:
        if l != '':
            lo = unicode(l).replace('<p>','').replace('</p>','').lstrip('[').rstrip(']').replace('&amp;','&').replace('&gt;','>').replace('&lt;','<').lstrip().rstrip()
        else:
            lo = u''
        outrec.append(reencode_string(lo))
    return outrec

def reencode_string(s):
    try:
        s = unidecode.unidecode(unicode(s))
    except:
        pass
    return s

def normalize_string(s):
    # normalizing consists of
    # 3) removing all spaces and other punctuation with re
    # 4) converting all ascii chars to upper-case
    try:
        s = srs.sub(' ',s)
        s = " ".join(s.split())
    except:
        pass
    try:
        s = s.upper()
    except:
        pass
    return unicode(s)


def convert_strings(records):
    recs_converted = []
    maxlen = 50000
    while len(records) > 0:
        block1 = records[0:maxlen]
        block2 = records[maxlen:]
        records = block2
        input_block = "<p>".join(block1)
        recs_converted.extend(back_convert_entities(input_block))
    return recs_converted


def read_affils_file(filename):
    inputrecords=[]
    with open(filename,'rU') as fa:
        i=0
        for l in fa.readlines():
            i=i+1
            ll = convert_unicode(l)
            if len(ll.rstrip().split('\t')) == 2:
                inputrecords.append(ll.rstrip())
            else:
                logger.warn("Bad line in {0}: line {1}".format(filename,i))
    inputrecords = convert_strings(inputrecords)
    aff_dict = {}
    for l in inputrecords:
        (k,v) = l.strip().split('\t')
        aff_dict[v] = k
    return aff_dict


def read_pcfacet_file(filename):
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

    canon_dict = {}
    for i in ids:
        if i not in affil_parent:
            affil_parent[i] = ["-"]
        if i not in affil_child:
            affil_child[i] = ["-"]

        canon_dict[i] = {'canonical_name':affil_canonical[i],'facet_name':affil_abbrev[i],'parents':affil_parent[i],'children':affil_child[i]}

    return canon_dict


def affil_id_match(aff_str,aff_lib):
    s = normalize_string(aff_str)

    try:
        x = aff_lib[s]
    except:
        return u"0"
    else:
        return x




# PICKLE HANDLING: dump and read

# The pickle file contains pickled copies of two dictionaries: canon_dict,
# and aff_dict.  See URL:
# https://stackoverflow.com/questions/20716812/saving-and-loading-multiple-objects-in-pickle-file

def dump_pickle(outfile,list_of_dicts):
# outfile is the name of the pickle file you're writing to
# list_of_dicts is a list containing all of the dicts you're pickling

    try:
        if isinstance(list_of_dicts,list):
            for x in list_of_dicts:
                if not isinstance(x,dict):
                    raise BaseException("util.dump_pickle: one or more list items is not a dict")
            with open(outfile,'wb') as fp:
                for x in list_of_dicts:
                    pickle.dump(x,fp,pickle.HIGHEST_PROTOCOL)
        else:
            raise BaseException("util.dump_pickle: must be given a list of dicts")
    except BaseException as e:
        raise BaseException("util.dump_pickle failed: {0}".format(e))



def read_pickle(infile):
# infile is the name if the pickle file you're reading from
# this function returns a GENERATOR whose items are the dictionaries you
# pickled (e.g. canon_dict, aff_dict)
    try:
        with open(infile, "rb") as fp:
            while True:
                try:
                    yield pickle.load(fp)
                except EOFError:
                    break
    except BaseException as e:
        raise BaseException("util.read_pickle failed: {0}".format(e))
