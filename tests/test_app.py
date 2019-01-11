#!/usr/bin/env python

import unittest
import filecmp
import run as app
from pandas.util.testing import assert_frame_equal
import json
from mock import patch
import mock, copy
import config_tests as config

(aff_list,aff_dict,canon_list) = app.tasks.task_load_dicts_from_file(config.PC_INFILE,config.AFFDICT_INFILE)

unmatched = app.tasks.task_read_unmatched_file(config.UNMATCHED_FILE)

class TestLoadData(unittest.TestCase):

    def test_affil_data_io(self):
        self.assertEqual(type(aff_list),list)
        self.assertEqual(len(aff_list),44)
        self.assertEqual(type(aff_dict),dict)
        self.assertEqual(type(canon_list),list)
        app.tasks.task_make_pickle_file(aff_dict,'tests/outputdata/test.pickle')
        self.assertTrue(filecmp.cmp(config.PICKLE_FILE,'tests/outputdata/test.pickle'))


#this won't work as is, see Import_Pipeline's test_tasks for setup of celery worker
#class TestDirectMatch(unittest.TestCase):
#
#    def test_augment_records(self):
#        (aff_list,aff_dict,canon_list) = app.tasks.task_load_dicts_from_file(PC_INFILE,AFFDICT_INFILE)
#        with open(DIRECT_RECORDS,'rU') as fj:
#            jdata = json.load(fj)
#            records = jdata['docs']
#        self.assertEqual(len(records),4)
#        ar = []
#        ax = app.tasks.app_module.ADSAffilCelery('mock-celery','')
#        for r in records:
#            ar.append(ax.augment_affiliations(r))
#        self.assertEqual(len(ar),4)
#        self.assertEqual(ar[0],{'lol':'wut'})

class TestDirectMatch(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.proj_home = os.path.join(os.path.dirname(__file__), '../..')
        self._app = tasks.app
        self.app = app_module.ADSAffilCelery('test',local_config={
            'SQLALCHEMY_URL': 'sqlite:///',
            'SQLALCHEMY_ECHO': False
            })
        tasks.app = self.app # monkey-patch the app object
        Base.metadata.bind = self.app._session.get_bind()
        Base.metadata.create_all()


    def tearDown(self):
        unittest.TestCase.tearDown(self)
        Base.metadata.drop_all()
        self.app.close_app()
        tasks.app = self._app


class TestMachineLearning(unittest.TestCase):

    def test_machine_learner(self):
        lmod = app.tasks.task_make_learning_model(aff_dict)
        app.tasks.task_resolve_unmatched(unmatched.keys(), lmod)
        self.assertTrue(filecmp.cmp(config.OUTPUT_FILE,'output/ml.out'))
