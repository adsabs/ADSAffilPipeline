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

def back_convert_entities(s):
    li = bs4.BeautifulSoup(s,"lxml").find_all('p')
    if s != '':
        lo = unicode(li[0]).replace('<p>','').replace('</p>','').lstrip('[').rstrip(']').replace('&amp;','&').replace('&gt;','>').replace('&lt;','<').lstrip().rstrip()
    else:
        lo = u''
    return lo

def encode_string(s):
    # encoding consists of
    # 0) cleaning mixed encoding (e.g. cp1252)
    # 1) converting all HTML/XML encodings to utf-8
    # 2) converting all utf-8 chars to ascii equiv

    try:
        s = convert_unicode(s)
    except:
        pass
    try:
        s = back_convert_entities(s)
    except:
        s = ''
        pass
    try:
        s = unidecode.unidecode(unicode(s))
    except:
        pass
    return unicode(s)

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
