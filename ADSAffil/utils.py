import re
import bs4
import unidecode
import warnings
import cPickle as pickle
import config
from ADSAffil.models import *
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="unidecode")

# TEXT CONVERSION UTILITIES

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
    except:
        pass
    try:
        s = s.upper()
    except:
        pass
    return unicode(s)

def affil_id_match(aff_str,aff_lib):
    s = normalize_string(aff_str)

    try:
        x = aff_lib[s]
    except:
        return u"0"
    else:
        return x


# FILE HANDLING

def load_affil_dict():
    try:
        dictionary = pickle.load(open(config.PICKLE_FILE,'rb'))
    except:
        raise BaseException("Failed to load pickle file.")
    else:
        return dictionary

