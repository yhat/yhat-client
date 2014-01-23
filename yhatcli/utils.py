import urllib2
from progressbar import ProgressBar, Bar, ETA, Percentage


def download_file(url, filename):
    """
    Downloads a file and displays a progress bar on the screen.

    url - URL of the file's source
    filename - location where the downloaded file should be saved
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

