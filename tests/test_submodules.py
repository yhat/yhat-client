import unittest
import numpy as np
from yhat import Yhat, YhatModel
from yhat.submodules import detect_explicit_submodules
import json

class TestModel(YhatModel):
    FILES = [
        "tests/sub-sub-modules/run.py"
    ]

class TestYhatJson(unittest.TestCase):

    def test_detect_explicit_submodule(self):
        submodules = detect_explicit_submodules(TestModel)
        self.assertEqual(len(submodules), 3)

    def test_detect_submodule_in_deployment(self):
        yh = Yhat("greg", "test", "http://api.yhathq.com/")
        yh.deploy("TestModel", TestModel, globals(), sure=True, dry_run=True)

if __name__=="__main__":
    unittest.main()
