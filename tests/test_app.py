#!/usr/bin/env python

import os
import unittest
import filecmp
import run as appx
import json
import copy
import config_tests as config




class TestThingerdoo(unittest.TestCase):

    def test_args(self):
        args = appx.get_arguments()
        attribs = args.__dict__
        self.assertTrue(len(attribs.keys())==5)
        arglist = [u'debug',u'loadfiles',u'makepickle',u'loadpickle',u'input_json_file']
        for k,v in attribs.items():
            self.assertTrue(k in arglist)
            self.assertFalse(v)

    def test_load(self):
        aff_dict = appx.utils.read_affils_file(config.AFFDICT_INFILE)
        canon_dict = appx.utils.read_pcfacet_file(config.PC_INFILE)
        self.assertIsInstance(aff_dict,dict)
        self.assertIsInstance(canon_dict,dict)
        aff_dict_norm = appx.utils.normalize_dict(aff_dict)
        appx.utils.dump_pickle(config.PICKLE_OUTFILE,[aff_dict_norm,canon_dict])
        self.assertTrue(filecmp.cmp(config.PICKLE_FILE,config.PICKLE_OUTFILE))
        (aout,cout) = appx.utils.read_pickle(config.PICKLE_OUTFILE)
        self.assertEqual(aout,aff_dict_norm)
        self.assertEqual(cout,canon_dict)

# simple test of matching
    def test_utils(self):
        (aout,cout) = appx.utils.read_pickle(config.PICKLE_OUTFILE)
        test_strings = [u'CfA', u'Smithsonian Institution', u'School of hard knocks', u'gibberishjkaghdsfkjygasdf']
        test_ids = [u'A01400',u'A01397',u'0',u'0']
        for s,i in zip(test_strings,test_ids):
            ix = appx.utils.affil_id_match(s,aout)
            self.assertEqual(i,ix)

    def test_app(self):
        testapp = appx.app
        testapp.load_dicts(config.PICKLE_OUTFILE)
# record 0: no affil data at all
        rec = {'bibcode':'rec0','aff':[]}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'],recx['bibcode'])
        self.assertNotEqual(rec.keys(),recx.keys())
# record 1: unmatched affil
        rec = {'bibcode':'rec1','aff':['test1']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'],recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'],[u'-'])
# record 2: one author: two affils, one unmatched
        rec = {'bibcode':'rec1','aff':['test1; CfA']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'],recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'],[u'-; Harvard Smithsonian Center for Astrophysics'])
# record 3: one author: two affils, both unmatched
        rec = {'bibcode':'rec1','aff':['test1; test2']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'],recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'],[u'-; -'])
# record 4: two authors: one unmatched affil each
        rec = {'bibcode':'rec1','aff':['test1','test2']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'],recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'],[u'-',u'-'])
# record 4: two authors: one matched affil each
        rec = {'bibcode':'rec1','aff':['Harvard University, Cambridge, MA 02138 USA','CfA']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'],recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'],[u'Harvard University, Massachusetts',u'Harvard Smithsonian Center for Astrophysics'])



#       aff_dict = utils.read_affils_file(config.AFFDICT_INFILE)
#       canon_dict = utils.read_pcfacet_file(config.PC_INFILE)
