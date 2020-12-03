import os
import unittest
from ADSAffil import tasks

stubdata_dir = os.path.dirname(tasks.__file__) + '/tests/stubdata'

class TestTasks(unittest.TestCase):

    def test_augment_affils(self):
        self.assertEqual(1,1)
