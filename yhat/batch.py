try:
    from urllib.request import urlopen
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urlparse import urlparse, urljoin
    from urllib import urlopen

try:
    import StringIO as bufio
except ImportError:
    import io as bufio

import json
import base64
import os
import sys
import os.path
import re
import tarfile
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoderMonitor, MultipartEncoder
from progressbar import ProgressBar, Percentage, Bar, FileTransferSpeed, ETA

from .deployment.save_session import save_function

class BatchJob(object):

    def __init__(self, name, **kwargs):
        if not re.match("^[a-z0-9_]+$", name):
            raise ValueError(
                "Job name must contain only [a-z0-9_]. Got: {}".format(name)
            )
        self.name = name
        for key in ["username", "apikey", "url"]:
            if not key in kwargs:
                raise ValueError("{} not specified".format(key))
            setattr(self, key, kwargs[key])

    def __create_bundle_tar(self, bundle, filename):
        buf = bufio.StringIO()
        buf.write(bundle)
        buf.seek(0)
        bundle_tarinfo = tarfile.TarInfo("bundle.json")
        bundle_tarinfo.size = len(bundle)

        # make sure old files are gone from previous job
        if os.path.isfile(filename):
            os.remove(filename)

        archive = tarfile.open(filename, "w:gz")
        archive.addfile(tarinfo=bundle_tarinfo, fileobj=buf)
        if os.path.isfile("yhat.yaml"):
            archive.add("yhat.yaml")
        if os.path.isfile("requirements.txt"):
            archive.add("requirements.txt")
        archive.close()

    def __post_file(self, filename, url, username, job_name, apikey):

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

        # Create the headers for the request
        auth = "{}:{}".format(username, apikey)
        base64string = base64.encodestring(auth).replace('\n', '')
        headers = {
            'Content-Type': encoder.content_type,
            'Authorization': 'Basic %s' % base64string
        }
        callback = createCallback(encoder)
        monitor = MultipartEncoderMonitor(encoder, callback)

        # Actually do the request, and get the response
        try:
            r = requests.post(url=url, data=monitor, headers=headers)
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

    def deploy(self, session, sure=False, verbose=False):
        bundle = save_function(self.__class__, session, verbose=verbose)
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
