#!/usr/bin/env python

import os
import unittest
import filecmp
import run as app
from pandas.util.testing import assert_frame_equal
import json
from mock import patch
import mock, copy
import config_tests as config
from ADSAffil.models import *

(aff_list,aff_dict,canon_list) = app.tasks.task_load_dicts_from_file(config.PC_INFILE,config.AFFDICT_INFILE)

unmatched = app.tasks.task_read_unmatched_file(config.UNMATCHED_FILE)

class TestLoadData(unittest.TestCase):

    def test_aff_list_io(self):
        self.assertEqual(type(aff_list),list)
        self.assertEqual(len(aff_list),44)

    def test_aff_list_dict(self):
        self.assertEqual(type(aff_dict),dict)
        self.assertEqual(len(aff_dict.keys()),44)
        self.assertEqual(len(aff_dict.values()),44)
        self.assertEqual(len(set(aff_dict.values())),3)

    def test_canon_list_io(self):
        self.assertEqual(type(canon_list),list)

    def test_make_pickle_file(self):
        app.tasks.task_make_pickle_file(aff_dict,'tests/outputdata/test.pickle')
        self.assertTrue(filecmp.cmp(config.PICKLE_FILE,'tests/outputdata/test.pickle'))


class TestDirectMatch(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.proj_home = os.path.join(os.path.dirname(__file__), '../..')
        self._app = app.tasks.app_module
        self.app = app.tasks.app_module.ADSAffilCelery('test',local_config={
            'SQLALCHEMY_URL': 'sqlite:///',
            'SQLALCHEMY_ECHO': False
            })
        app.tasks.app = self.app # monkey-patch the app object
        Base.metadata.bind = self.app._session.get_bind()
        Base.metadata.create_all()


    def tearDown(self):
        unittest.TestCase.tearDown(self)
        Base.metadata.drop_all()
        self.app.close_app()
        app.tasks.app_module = self._app

    def test_direct_matching(self):
        with patch('ADSAffil.tasks.task_augment_affiliations_json', return_value=None) as next_task:
#           global adict
#           adict = app.utils.load_affil_dict(config.PICKLE_FILE)
            self.assertFalse(next_task.called) 
#           in_rec1 = {"bibcode":u"2109zyxwv......12X", "aff":u"Harvard-Smithsonian Center for Astrophysics"}
#           out_rec1 = self.app.augment_affiliations(in_rec1)
#           self.assertEqual(in_rec1,out_rec1)


class TestMachineLearning(unittest.TestCase):

    def test_machine_learner(self):
        lmod = app.tasks.task_make_learning_model(aff_dict)
        app.tasks.task_resolve_unmatched(unmatched.keys(), lmod)
        self.assertTrue(filecmp.cmp(config.OUTPUT_FILE,'output/ml.out'))
































