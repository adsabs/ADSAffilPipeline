import json
import os
import sys

from mock import patch, Mock, MagicMock
import unittest
from ADSAffil import tasks

stubdata_dir = os.path.dirname(tasks.__file__) + '/tests/stubdata'
tasks.app.conf.AFFIL_DATA_DIR = stubdata_dir

class TestTasks(unittest.TestCase):

    def test_augment_from_json(self):

        test_json = stubdata_dir + '/record.json'
        with open(test_json,'r') as fj:
            jdata = json.load(fj)
        rec = jdata['response']['docs'][0]
        with patch('ADSAffil.tasks.app.forward_message') as output:
            tasks.task_augment_affiliations_json(rec)
            self.assertTrue(output.called)
        with patch('ADSAffil.tasks.app.forward_message') as output:
            rec.pop('aff')
            print("fnord:",rec)
            tasks.task_augment_affiliations_json(rec)
            self.assertFalse(output.called)
        with patch('ADSAffil.tasks.app.forward_message') as output:
            rec = None
            tasks.task_augment_affiliations_json(rec)
            self.assertFalse(output.called)
