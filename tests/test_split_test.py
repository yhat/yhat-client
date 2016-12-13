import unittest
import numpy as np
from yhat import Yhat, Variant, SplitTestModel
import os
import json

class TestModel(SplitTestModel):

    def setup_variants(self):
        return [
            Variant("a", "execute_a", 0.5),
            Variant("b", "execute_b", 0.5)
        ]

    def execute_a(self, data):
        return data

    def execute_b(self, data):
        return data

    def execute(self):
        return "THIS SHOULD NOT RUN"

class TestModelOneVariant(SplitTestModel):

    def setup_variants(self):
        return [
            Variant("a", "execute_a", 1.0),
        ]

    def execute_a(self, data):
        return data

class TestSplitTest(unittest.TestCase):

    def test_can_execute_splittest(self):
        t = TestModel()
        t.execute(1)
        self.assertTrue(True)

    def test_overrides_execute(self):
        t = TestModel()
        self.assertEqual(t.execute(1)['output'], 1)

    def test_applies_variant_label(self):
        t = TestModel()
        self.assertTrue('variant' in t.execute(1))
        self.assertTrue(t.execute(1)['variant'] in ['a', 'b'])
    
    def test_one_variant(self):
        t = TestModelOneVariant()
        self.assertEqual(t.execute(1)['variant'], "a")


if __name__=="__main__":
    unittest.main()
