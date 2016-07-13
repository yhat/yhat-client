import os
import sys
import urllib2
from cStringIO import StringIO

def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])

class Progress(object):
    def __init__(self):
        s = getTerminalSize()[0]
        self._size = 80 - 15 if s > 80 else s - 15
        self._seen = 0
        sys.stdout.write("\r[>%s]" % (" " * (self._size-1)))
        sys.stdout.flush()
        self._last = 0

    def update(self, total, size):
        if size == 0:
            return
        self._seen += size
        n = self._size * self._seen / total
        if n > self._last:
            blank = " " * (self._size-(n+1))
            seenKiB = self._seen / 1024
            totalKiB = total / 1024
            sys.stdout.write("\r[%s>%s] %d/%d KiB" % ("-" * n, blank, seenKiB, totalKiB))
            sys.stdout.flush()
            self._last = n
        if total == self._seen:
            sys.stdout.write("\n")

class stream_with_callback(file):
    def __init__(self, data, callback, *args):
        self._file = StringIO(data)
        self._file.seek(0, os.SEEK_END)
        self._total = self._file.tell()
        self._file.seek(0)
        self._callback = callback
        self._args = args

    def __len__(self):
        return self._total

    def read(self, size):
        data = self._file.read(size)
        self._callback(self._total, len(data), *self._args)
        return data

def progressbarify(data):
    progress = Progress()
    return stream_with_callback(data, progress.update)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def create_tests(df, output_file, columns=None):
    """
    Creates ScienceOps compatible (JSON Line Format) smoke test files from your dataframes.
    Once created, these files can be uploaded directly to your model via ScienceOps --> '/models/{model}/unit-tests'

    Parameters
    ----------
    df: dataframe
        the dataframe you wish to pull test inputs from
    output_file: string
        the name you will give your exported test file
    columns: array of strings
        the columns in your df which will be made into inputs

    Example
    -------
    Let's say you've built a book recommender model that takes 2 inputs - title & page count:

    from yhat.utils import create_tests
    books =  pd.read_csv('./book_data.csv')
    create_tests(books, "book_model_inputs.ldjson", columns=["title","pages"])
    * That's it! *
    --> book_model_inputs.ldjson {"title":"harry potter","pages":"800"}\\n{"title":"war and peace","pages":"875"}\\n{"title":"lord of the rings","pages":"500"}

      """
    # if the user doesn't specify columns, then we'll assume they want them all!
    if columns is None:
        columns = df.columns
    with open(output_file, "wb") as f:
        for _, row in df[columns].iterrows():
            f.write(row.to_json() + '\n')
