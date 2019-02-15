# this is based on downloadChunks from: https://gist.github.com/gourneau/1430932
import os
import urllib2
import math
import logging
from src.gui_constants import DOWNLOAD_ERROR


def downloadLargeFile(url, dest, spinnerDialog):
    logging.debug("Large File Download starting")
    os.umask(0002)

    try:
        file = dest
        req = urllib2.urlopen(url)
        total_size = 0.0
        downloaded = 0.0
        chunked = False
        CHUNK = 256 * 10240

        if req.info()['Transfer-Encoding'] == "chunked":
            chunked = True
            spinnerDialog.hideProgressBar()
        else:
            total_size = int(req.info()['content-length'].strip())

        with open(file, 'wb') as fp:
            while True:
                chunk = req.read(CHUNK)
                if not chunk:
                    break
                downloaded += len(chunk)
                if chunked:
                    spinnerDialog.setLabelVal("Downloaded %0.2f MB" % (downloaded / 10**6))
                else:
                    spinnerDialog.setLabelVal(str(math.floor((downloaded / total_size) * 1000) / 10) + "% Downloaded")
                    spinnerDialog.setProgressVal(downloaded / total_size)
                fp.write(chunk)
            spinnerDialog.showProgressBar()
    except urllib2.HTTPError, e:
        if os.path.isfile(file):
            os.remove(file)
        spinnerDialog.destroy()
        print DOWNLOAD_ERROR
        return
    except urllib2.URLError, e:
        if os.path.isfile(file):
            os.remove(file)
        spinnerDialog.destroy()
        print DOWNLOAD_ERROR
        return

    spinnerDialog.destroy()
