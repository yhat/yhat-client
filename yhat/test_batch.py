import unittest
import tarfile
import os
import json
import nose
from deployment.save_session import save_function

import batch

# Function test whether the bundling code will 
def external_func():
    print("Hello from outside the class!")

class BatchTestCase(unittest.TestCase):

    test_archive = ".tmp_yhat_job_test.tar.gz"

    def setUp(self):
        # Create local file specifying mock install instructions
        with open("yhat.yaml", "w") as f:
            f.write("yum install lsof\necho 'Installs complete!'")
        # Create requirements.txt with mock python dependencies
        with open("requirements.txt", "w") as f:
            f.write("nose==1.3.7\nmock==1.3.0")

    # Remove test files that were created locally
    def tearDown(self):
        files = ["yhat.yaml", "requirements.txt", self.test_archive]
        for f in files:
            if os.path.isfile(f):
                os.remove(f)

    class TestBatchJob(batch.BatchJob):
        def execute():
            print("Hello")
            external_func()
            
    def test_create_bundle_tar(self):
        batch_job = self.TestBatchJob("test_job", username="bob", \
            apikey="123", url="http://localhost:9000")
        bundle = save_function(batch_job.__class__, globals(), \
            verbose=False)
        bundle_str = json.dumps(bundle)
        batch_job._BatchJob__create_bundle_tar(bundle_str, \
            self.test_archive)

        # Make sure the tar file includes all the correct files
        # and contents
        with tarfile.open(self.test_archive, "r:gz") as f:
            requirements = f.extractfile("requirements.txt").read()
            self.assertIn("nose==1.3.7", requirements)
            self.assertIn("mock==1.3.0", requirements)

            yaml_file = f.extractfile("yhat.yaml").read()
            self.assertIn("Installs complete!", yaml_file)
            self.assertIn("yum install lsof", yaml_file)

            bundle = f.extractfile("bundle.json").read()
            self.assertIn("""print(\\"Hello\\")""", bundle)
            self.assertIn("Hello from outside the class!", bundle)

if __name__ == '__main__':
    unittest.main()
