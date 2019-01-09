import copy
from mock import patch
import os
import sys
import unittest

#from ADSAffil import tasks
#from ADSAffil import app as app_module
#from ADSAffil.models import Base
#from tests.testdata import directdata
#
#class TestWorkers(unittest.TestCase):
#
#    def setUp(self):
#        unittest.TestCase.setUp(self)
#        self.proj_home = os.path.join(os.path.dirname(__file__), '../..')
#        self._app = tasks.app
#        self.app = app_module.ADSImportPipelineCelery('test', local_config={
#            'SQLALCHEMY_URL': 'sqlite:///',
#            'SQLALCHEMY_ECHO': False
#            })
#        tasks.app = self.app  # monkey-patch the app object
#        Base.metadata.bind = self.app._session.get_bind()
#        Base.metadata.create_all()
#
#    def tearDown(self):
#        unittest.TestCase.tearDown(self)
#        Base.metadata.drop_all()
#        self.app.close_app()
#        tasks.app = self._app
