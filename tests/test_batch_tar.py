from __future__ import absolute_import
import unittest
import tarfile
import os
import json

from yhat.deployment.save_session import save_function
from yhat import batch

# Function test whether the bundling code will
def external_func():
    print("Hello from outside the class!")

class BatchTestCase(unittest.TestCase):

    test_archive = ".tmp_yhat_job_test.tar.gz"

    def setUp(self):
        # Create local file specifying mock install instructions
        print("creating tar...")
        with open("yhat.yaml", "w") as f:
            f.write("yum install lsof\necho 'Installs complete!'")
        # Create requirements.txt with mock python dependencies
        with open("requirements.txt", "w") as f:
            f.write("nose==1.3.7\nmock==1.3.0")

    # Remove test files that were created locally
    def tearDown(self):
        os.remove(self.test_archive)

        files = ["yhat.yaml", "requirements.txt"]
        for f in files:
            if os.path.isfile(f):
                os.remove(f)

    # Create a new batch job class with an execute method
    class TestBatchJob(batch.BatchJob):
        def execute():
            print("Hello")
            external_func()

    # Test for creation of the bundle tar
    def test_create_bundle_tar(self):
        batch_job = self.TestBatchJob("test_job", username="bob", \
            apikey="123", url="http://localhost:9000")
        bundle = save_function(batch_job.__class__, globals(), \
            verbose=False)
        bundle_str = json.dumps(bundle)

        print("checking tar contents...")
        # Create the bundle tar using the function from batch
        batch_job._BatchJob__create_bundle_tar(bundle_str, \
            self.test_archive)

        # Make sure the tar file includes all the correct files
        # and contents
        with tarfile.open(self.test_archive, "r:gz") as f:
            requirements = f.extractfile("requirements.txt").read()
            print("checking requirements...")
            self.assertIn(b"nose==1.3.7", requirements)
            self.assertIn(b"mock==1.3.0", requirements)

            print("checking yaml...")
            yaml_file = f.extractfile("yhat.yaml").read()
            self.assertIn(b"Installs complete!", yaml_file)
            self.assertIn(b"yum install lsof", yaml_file)

            print("checking bundle...")
            bundle = f.extractfile("bundle.json").read()
            self.assertIn(b"""print(\\"Hello\\")""", bundle)
            self.assertIn(b"Hello from outside the class!", bundle)

if __name__ == '__main__':
    unittest.main()
