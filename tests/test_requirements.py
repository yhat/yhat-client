from __future__ import absolute_import
import unittest

from pip._vendor.pkg_resources import Requirement, RequirementParseError
from yhat.requirements import parseUserRequirementsList

class RequirementsTest(unittest.TestCase):


    def testPipFreeze(self):
        """
        testPipFreeze will test that we can parse a requirements.txt file
        from pip freeze
        """
        # Set the requirments to our test requirments list
        REQUIREMENTS = ['./testdata/realtime/test_reqs.txt']
        # Run this through the parser
        userReqs = parseUserRequirementsList(REQUIREMENTS)
        assertReqs = [Requirement.parse('scikit-learn==0.16.1'),
             Requirement.parse('pandas==0.17.1'),
             Requirement.parse('dill==0.2.5'),
             Requirement.parse('terragon==0.3.0'),
             Requirement.parse('progressbar2==3.10.1'),
             Requirement.parse('requests'),
             Requirement.parse('requests-toolbelt')]
        self.assertTrue(userReqs, assertReqs)

    def testCondaList(self):
        """
        testCondaList will test that we can parse a requirements.txt file
        that comes from conda list
        """
        pass

    def testRequirmentsString(self):
        """
        testRequirmentsString will test a normal requirments list
        """
        REQUIREMENTS = ['scikit-learn==0.16.1', 'pandas==0.17.1']
        userReqs = parseUserRequirementsList(REQUIREMENTS)
        assertReqs = [Requirement.parse('scikit-learn==0.16.1'),
             Requirement.parse('pandas==0.17.1')]
        self.assertTrue(userReqs, assertReqs)

if __name__ == '__main__':
    unittest.main()
