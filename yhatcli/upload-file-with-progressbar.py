import os, urllib2
from progressbar import ProgressBar, Bar, ETA, Percentage



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

url = "http://localhost:3000/"
path = 'myfile.txt'
stream = file_with_callback(path, 'rb', path)
req = urllib2.Request(url, stream)
res = urllib2.urlopen(req)
print
