import json
import logging
import os
import os.path
import re
import sys
import tarfile
from builtins import input

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
    try:
        import StringIO as io
    except ImportError:
        import io as io

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoderMonitor, MultipartEncoder
from progressbar import ProgressBar, Percentage, Bar, FileTransferSpeed, ETA

from .deployment.save_session import save_function

class BatchJob(object):

    def __init__(self, name, **kwargs):
        if not re.match("^[a-zA-Z0-9_]+$", name):
            raise ValueError(
                "Job name must contain only [a-zA-Z0-9_]. Got: {}".format(name)
            )
        self.name = name
        for key in ["username", "apikey", "url"]:
            if not key in kwargs:
                raise ValueError("{} not specified".format(key))
            setattr(self, key, kwargs[key])

    def __create_bundle_tar(self, bundle, filename):
        logging.debug("creating batch job tarfile...")
        # Write a bundle file
        f = open('bundle.json', 'w')
        f.write(bundle)
        f.close()

        # make sure old files are gone from previous job
        if os.path.isfile(filename):
            os.remove(filename)

        archive = tarfile.open(filename, "w:gz")
        archive.add('bundle.json')

        if os.path.isfile("yhat.yaml"):
            archive.add("yhat.yaml")
        if os.path.isfile("requirements.txt"):
            archive.add("requirements.txt")
        archive.close()
        # remove the bundle file
        os.unlink('bundle.json')

    def __post_file(self, filename, url, username, job_name, apikey):
        logging.debug("sending batch job to server...")
        def createCallback(encoder):
            # Stuff for progress bar setup
            widgets = ['Transfering Model: ', Bar(), Percentage(), ' ', ETA(), ' ', FileTransferSpeed()]
            pbar = ProgressBar(max_value=encoder.len, widgets=widgets).start()
            def callback(monitor):
                current = monitor.bytes_read
                pbar.update(current)
            return callback

        # Create the Multi-Part encoder
        data = open(filename, "rb")
        encoder = MultipartEncoder(
            fields={'job_name': job_name, 'job': (filename, data, 'application/x-tar')}
        )

        headers = {
            'Content-Type': encoder.content_type,
        }
        callback = createCallback(encoder)
        monitor = MultipartEncoderMonitor(encoder, callback)

        # Actually do the request, and get the response
        try:
            r = requests.post(url=url, data=monitor, headers=headers, auth=(username, apikey))
            if r.status_code != requests.codes.ok:
                r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            text = r.text
            sys.stderr.write("\nServer error: {}".format(text))
            return
        except Exception as e:
            sys.stderr.write("\nError: {}".format(e))
            return
        response_text = r.text

    def deploy(self, session, sure=False, verbose=0):
        """
        Deploy your batch model to the yhat server

        Parameters
        -----
        session: globals()
            your Python's session variables (i.e. "globals()")
        sure: boolean
            if true, then this will force a deployment (like -y in apt-get).
            if false or blank, this will ask you if you're sure you want to
            deploy
        verbose: int
            Relative amount of logging info to display (higher = more logs)
        """
        # Setup logging
        levels = {
            0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG
        }
        if verbose > 2:
            verbose = 2
        logging.basicConfig(format='[%(levelname)s]: %(message)s', level=levels[verbose])

        bundle = save_function(self.__class__, session)
        bundle["class_name"] = self.__class__.__name__
        bundle["language"] = "python"
        bundle_str = json.dumps(bundle)
        filename = ".tmp_yhat_job.tar.gz"
        self.__create_bundle_tar(bundle_str, filename)
        url = urljoin(self.url, "/batch/deploy")
        print(("deploying batch job to: " +  str(url)))
        if not sure:
            sure = input("Are you sure you want to deploy? (y/N): ")
            if sure.lower() != "y":
                print("Deployment canceled")
                sys.exit()
        self.__post_file(filename, url, self.username, self.name, self.apikey)
        os.remove(filename)
