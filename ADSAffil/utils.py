import html
import os
import pickle
import re


class FixSemicolonsException(Exception):
    pass


class CleanStringException(Exception):
    pass


class NormalizeStringException(Exception):
    pass


class NormalizeDictException(Exception):
    pass


class SplitClausesException(Exception):
    pass


class AffilTextFileException(Exception):
    pass


class PCTextFileException(Exception):
    pass


class CreateClauseDictException(Exception):
    pass


class DumpPickleException(Exception):
    pass


class MakeClausePickleException(Exception):
    pass


class MakeAffilPickleException(Exception):
    pass


class LoadPickleException(Exception):
    pass


regex_norm_semicolon = re.compile(r";\s*;")
regex_norm_punct = re.compile(r'[-!?.,;:/\\]')


def fix_semicolons(string):
    try:
        string_x = regex_norm_semicolon.sub(';', string).strip()
        if string_x != string:
            return fix_semicolons(string_x)
        else:
            return string_x
    except Exception as err:
        raise FixSemicolonsException('Error in fix_semicolons: %s' % err)

def clean_string(string):
    try:
        string = html.unescape(string)
        string = fix_semicolons(string)
        string = string.strip(';').strip()
        return string
    except Exception as err:
        raise CleanStringException('Error in clean_string: %s' % err)

def normalize_string(string):
    # normalizing consists of
    # 3) removing all spaces and other punctuation with re
    # 4) converting all ascii chars to upper-case
    try:
        string = regex_norm_punct.sub(' ', string)
        string = ' '.join(string.split())
        string = string.upper()
        return string
    except Exception as err:
        raise NormalizeStringException('Error in normalize_string: %s' % err)

def normalize_dict(dictionary):
    dictionary_norm = {}
    try:
        for (k, v) in dictionary.items():
            kn = normalize_string(k)
            dictionary_norm[kn] = v
        return dictionary_norm
    except Exception as err:
        raise NormalizeDictException('Error in normalize_dict: %s' % err)

def split_clauses(string, separator):
    try:
        clauses = string.strip().split(separator)
        clauses = [x.strip() for x in clauses]
        return clauses
    except Exception as err:
        raise SplitClausesException('Error in split_clauses: %s' % err)

def create_clause_dict(affdict, separator=','):
    try:
        clausedict = dict()
        for k, v in affdict.items():
            clauses = split_clauses(k, separator)
            for c in clauses:
                c = normalize_string(clean_string(c.strip()))
                if c:
                    if c in clausedict:
                        clausedict[c].append(v)
                        # clausedict[c] = list(set(clausedict[c]))
                        clausedict[c] = list(dict.fromkeys(clausedict[c]))
                    else:
                        clausedict[c] = [v]
        return clausedict
    except Exception as err:
        raise CreateClauseDictException('Error in make_clause_dict: %s' % err)

# file loading & writing utils

def load_affils_affdict_file(aff_filename):
    if os.path.exists(aff_filename):
        affdict = dict()
        with open(aff_filename,'r') as fa:
            for l in fa.readlines():
                try:
                    (idkey, idstring) = l.strip().split('\t')
                    idstring = clean_string(idstring)
                    affdict[idstring] = idkey
                except Exception as err:
                    pass
        return affdict
    else:
        raise AffilTextFileException('No such file: %s' % aff_filename)

def load_affils_pcdict_file(pc_filename):
    affil_canonical = {}
    affil_abbrev = {}
    affil_parent = {}
    affil_child = {}

    if os.path.exists(pc_filename):
        with open(pc_filename, 'r') as fpc:
            for l in fpc.readlines():
                try:
                    (parent, child, shortform, longform) = l.rstrip().split('\t')
                except:
                    pass
                else:
                    if str(child) not in affil_canonical:
                        affil_canonical[str(child)] = longform
                        affil_abbrev[str(child)] = shortform

                    if str(parent) != '':
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
                affil_parent[i] = ['-']
            if i not in affil_child:
                affil_child[i] = ['-']

            canon_dict[i] = {'canonical_name': affil_canonical[i],
                             'facet_name': affil_abbrev[i],
                             'parents': affil_parent[i],
                             'children': affil_child[i]}

        return canon_dict
    else:
        raise PCTextFileException('No such file: %s' % pc_filename)

def pickle_clause_dict(clausedict, clause_pickle_file,
                       protocol=pickle.HIGHEST_PROTOCOL):
    try:
        with open(clause_pickle_file,'wb') as fp:
            pickle.dump(clausedict, fp, protocol)
    except Exception as err:
        raise DumpPickleException('Error: %s' % err)

def pickle_affil_dict(affdict_norm, pcdict, affil_pickle_filename,
                      protocol=pickle.HIGHEST_PROTOCOL):
    try:
        with open(affil_pickle_filename,'wb') as fp:
            pickle.dump(affdict_norm, fp, protocol)
            pickle.dump(pcdict, fp, protocol)
    except Exception as err:
        raise DumpPickleException('Error: %s' % err)


def make_clause_pickle(aff_filename, clause_pickle_filename, separator,
                       protocol):
    try:
        affdict = load_affils_affdict_file(aff_filename)
        clausedict = create_clause_dict(affdict, separator)
        pickle_clause_dict(clausedict, clause_pickle_filename, protocol)
    except Exception as err:
        raise MakeClausePickleException('Error: %s' % err)


def make_affil_pickle(aff_filename, pc_filename, affil_pickle_filename,
                      protocol):
    try:
        affdict = load_affils_affdict_file(aff_filename)
        affdict_norm = normalize_dict(affdict)
        pcdict = load_affils_pcdict_file(pc_filename)
        pickle_affil_dict(affdict_norm, pcdict, affil_pickle_filename,
                          protocol)
    except Exception as err:
        raise MakeAffilPickleException('Error: %s' % err)

def load_clause_dict(filename):
    try:
        with open(filename,'rb') as fp:
            data = pickle.load(fp)
            return data
    except Exception as err:
        raise LoadPickleException('Error: %s' % err)


def load_affil_dict(filename):
    try:
        with open(filename,'rb') as fp:
            dictionaries = []
            while True:
                try:
                    dictionaries.append(pickle.load(fp))
                except EOFError:
                    break
        return dictionaries
    except Exception as err:
        raise LoadPickleException('Error: %s' % err)
