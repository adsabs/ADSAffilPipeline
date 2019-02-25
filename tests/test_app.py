#!/usr/bin/env python

import os
import unittest
import filecmp
import json
import copy
import config_tests as config
from ADSAffil import tasks


class TestApp(unittest.TestCase):

    def test_app(self):
        testapp = tasks.app
        testapp.load_dicts(config.PICKLE_OUTFILE)
# record 0: no affil data at all
        rec = {'bibcode': 'rec0', 'aff': []}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'], recx['bibcode'])
        self.assertNotEqual(rec.keys(), recx.keys())
# record 1: unmatched affil
        rec = {'bibcode': 'rec1', 'aff': ['test1']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'], recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'], [u'-'])
# record 2: one author: two affils, one unmatched
        rec = {'bibcode': 'rec1', 'aff': ['test1; CfA']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'], recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'], [u'-; Harvard Smithsonian Center for Astrophysics'])
# record 3: one author: two affils, both unmatched
        rec = {'bibcode': 'rec1', 'aff': ['test1; test2']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'], recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'], [u'-; -'])
# record 4: two authors: one unmatched affil each
        rec = {'bibcode': 'rec1', 'aff': ['test1', 'test2']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'], recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'], [u'-', u'-'])
# record 4: two authors: one matched affil each
        rec = {'bibcode': 'rec1', 'aff': ['Harvard University, Cambridge, MA 02138 USA', 'CfA']}
        recx = copy.deepcopy(rec)
        u = testapp.augment_affiliations(rec)
        self.assertEqual(rec['bibcode'], recx['bibcode'])
        self.assertEqual(rec[u'aff_canonical'], [u'Harvard University, Massachusetts', u'Harvard Smithsonian Center for Astrophysics'])
