#!/usr/bin/env python

import os
import unittest
import filecmp
from mock import patch
import json
import copy
import config_tests as config
from ADSAffil import tasks


class TestTasks(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.proj_home = os.path.join(os.path.dirname(__file__), '../..')
        self._app = tasks.app_module
        self.app = tasks.app_module.ADSAffilCelery('test')
        tasks.app = self.app

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.app.close_app()
        tasks.app_module = self._app

    def test_tasks(self):
#       with patch('ADSAffil.tasks.task_augment_affiliations_json', return_value=None) as augment, patch('ADSAffil.tasks.task_output_augmented_record', return_value=None) as update:
#       self.assertFalse(augment.called)
#       self.assertFalse(update.called)
        self.app.load_dicts(config.PICKLE_FILE)
        a = self.app.cdict['A01400']
        self.assertEqual(a['facet_name'],'CfA')

        rec0 = None
        with self.assertRaises(BaseException):
            tasks.task_augment_affiliations_json(rec0)

        rec1 = {'bibcode':'rec1','not_aff':['CfA']}
        with self.assertRaises(BaseException):
            tasks.task_augment_affiliations_json(rec1)

     
#       rec2 = {'bibcode':'rec2','aff':['CfA']}
#       tasks.task_augment_affiliations_json(rec2)
#       self.assertEqual(rec2,'lol')
#       self.assertTrue(augment.called)
#           self.assertEqual(rec,{'lol':'butts'})
#           self.assertTrue(update.called)
