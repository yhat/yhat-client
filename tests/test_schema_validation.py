from __future__ import absolute_import
import unittest
from schema import Schema, And, Or, Use, Optional, SchemaUnexpectedTypeError
from yhat import validate


mySchema = Schema({
    'name': And(str, len),
    'age':  And(Use(int), lambda n: 18 <= n <= 99),
    Optional('sex'): And(str, Use(str.lower), lambda s: s in ('male', 'female'))})
class TestClass(object):
    @validate(mySchema)
    def myMethod(self, data):
        return data

t = TestClass()

class SchemaTest(unittest.TestCase):


    def testValidateObject(self):
        data = {'name': 'Sue', 'age': 28, 'sex': 'female'}
        self.assertEquals(data, t.myMethod(data))

    def testValidationFail(self):
        with self.assertRaises(SchemaUnexpectedTypeError):
            t.myMethod("foo")


if __name__ == '__main__':
    unittest.main()
