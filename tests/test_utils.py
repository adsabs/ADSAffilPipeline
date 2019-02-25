#!/usr/bin/env python

import os
import unittest
import filecmp
import json
import copy
import config_tests as config
from ADSAffil import utils


class TestUtils(unittest.TestCase):

    def test_file_io(self):

        aff_dict = utils.read_affils_file(config.AFFDICT_INFILE)
        canon_dict = utils.read_pcfacet_file(config.PC_INFILE)
        self.assertIsInstance(aff_dict, dict)
        self.assertIsInstance(canon_dict, dict)

        aff_dict_norm = utils.normalize_dict(aff_dict)
        utils.dump_pickle(config.PICKLE_OUTFILE, [aff_dict_norm, canon_dict])
        self.assertTrue(filecmp.cmp(config.PICKLE_FILE, config.PICKLE_OUTFILE))

        (aout, cout) = utils.read_pickle(config.PICKLE_OUTFILE)
        self.assertEqual(aout, aff_dict_norm)
        self.assertEqual(cout, canon_dict)

        with self.assertRaises(BaseException):
            utils.dump_pickle('notfile.txt', 'a', 'b')
        with self.assertRaises(BaseException):
            utils.dump_pickle('notfile.txt', ['a', 'b'])
        with self.assertRaises(BaseException):
            utils.dump_pickle('a', 'b')

    def test_aff_match_utils(self):
        (aout, cout) = utils.read_pickle(config.PICKLE_OUTFILE)
        test_strings = [u'CfA', u'Smithsonian Institution', u'School of hard knocks', u'gibberishjkaghdsfkjygasdf']
        test_ids = [u'A01400', u'A01397', u'0', u'0']
        for s, i in zip(test_strings, test_ids):
            ix = utils.affil_id_match(s, aout)
            self.assertEqual(i, ix)

    def test_write_unmatched(self):
        if os.path.exists(config.UNMATCHED_FILE):
            os.remove(config.UNMATCHED_FILE)
        testaff = u'This is a fake affiliation string.'
        unmatched = {testaff: u'0'}
        utils.output_unmatched(config.UNMATCHED_FILE, unmatched)
        lines = []
        with open(config.UNMATCHED_FILE, 'rU') as f:
            for l in f.readlines():
                lines.append(l.rstrip())
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], testaff)
