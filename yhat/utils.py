import urllib2
import os

from progressbar import ProgressBar, Bar, ETA, Percentage


def download_file(url, filename):
    """
    Downloads a file and displays a progress bar on the screen.

    url: string
        URL of the file's source
    filename: string
        location where the downloaded file should be saved
    """
    file_conn = urllib2.urlopen(url)
    filesize = file_conn.headers['content-length']
    processed = 0
    pbar = ProgressBar(widgets=[Bar(), ' ', ETA(), ' ', Percentage()],
                       maxval=int(filesize)).start()
    with open(filename, "wb") as f:
        for line in file_conn:
            processed += len(line)
            pbar.update(processed)
            f.write(line)
    print


class file_with_callback(file):

    def __init__(self, path, mode, *args):
        file.__init__(self, path, mode)
        self.seek(0, os.SEEK_END)
        self._total = self.tell()
        self.seek(0)
        self.pbar = ProgressBar(widgets=[Bar(), ' ', ETA(), ' ', Percentage()],
                                maxval=self._total).start()
        self.processed = 0
        self._callback = self.pbar.update

    def __len__(self):
        return self._total

    def read(self, size):
        data = file.read(self, size)
        self.processed += len(data)
        self._callback(self.processed)
        return data


def upload_file(url, filename):
    stream = file_with_callback(filename, 'rb', filename)
    req = urllib2.Request(url, stream)
    urllib2.urlopen(req)
    print
