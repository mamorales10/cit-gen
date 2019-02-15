import os
import logging
import threading
import time
# nocache imports
from functools import update_wrapper, wraps

from flask import (Flask, jsonify, make_response, render_template,
                   send_from_directory)
from gevent.lock import BoundedSemaphore

from DataAggregation.webdata_aggregator import (checkoutUnit,
                                                getAvailableWorkshops,
                                                putOnHold, zip_files)
from manager_constants import THREAD_TIME, ZIP_CLEAR_TIME, SOCKET_IO_PORT

app = Flask(__name__)
threadsToRun = []
threadsToRunSem = threading.Semaphore(1)
threadHandlerSem = threading.Semaphore(1)
zipSem = BoundedSemaphore(1)
i = 0


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        # response.headers['Last-Modified'] = datetime.now()
        response.headers[
            'Cache-Control'] = 'public, no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return update_wrapper(no_cache, view)


@app.route('/WorkshopData/<path:filename>', methods=['GET', 'POST'])
@nocache
def download(filename):
    logging.info("flask_server: Download initiated for " + filename)
    downloads = os.path.join(app.root_path, "../WorkshopData/")
    return send_from_directory(directory=downloads, as_attachment=True, filename=filename, mimetype='application/octet-stream')


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@nocache
def catch_all(path):
    """ Handles all requests to the main index page of the Web Server. """
    logging.info("flask_server: Serving HTML page to client.")
    return render_template('index.html', workshops=getAvailableWorkshops(), socket_io_port=SOCKET_IO_PORT)


@app.route('/checkout/<type>/<workshopName>')
def checkout(type, workshopName):
    logging.info("flask_server: New checkout for Workshop:" + workshopName + " | Type: " + type)
    global i
    workshop = filter(lambda x: x.workshopName == workshopName, getAvailableWorkshops())[0]
    if workshop.q.qsize():
        threadsToRunSem.acquire()
        unit = workshop.q.get()
        putOnHold(unit)
        logging.info("flask_server: Initiated checkoutUnit().")
        threadsToRun.append(threading.Thread(target=checkoutUnit, args=(unit,)))
        threadsToRunSem.release()

        file_paths = []
        if type == "ms-rdp":
            file_paths = unit.rdp_files
        if type == "rdesktop":
            file_paths = unit.rdesktop_files

        if len(file_paths) is 1:
            logging.info("flask_server: Initiating redirect to download page with remote desktop file.")
            return render_template('download.html', download_path=file_paths[0], download_type=type, zip=False)

        zipSem.acquire()
        zip_file_name = "Workshop" + str(i) + ".zip"
        zip_file_path = os.path.join("WorkshopData", workshopName, zip_file_name)
        i += 1
        zip_files(file_paths, zip_file_path)
        threadsToRun.append(threading.Thread(target=clearZip, args=(zip_file_path,)))
        zipSem.release()
        logging.info("flask_server: Initiating redirect to download page with remote desktop files archive.")
        return render_template('download.html', download_path=zip_file_path, download_type=type, zip=True)
    else:
        logging.info("flask_server: Checkout was unsuccessful as no workshops are available.")
        return "Sorry, there are no workshops available."


def clearZip(zip_file_name):
    time.sleep(ZIP_CLEAR_TIME)
    logging.info("flask_server: Clearing zip file: " + zip_file_name)
    os.remove(zip_file_name)


def threadHandler():
    while True:
        threadHandlerSem.acquire()
        if len(threadsToRun):
            for thread in threadsToRun:
                t = thread
                threadsToRun.remove(thread)
                t.start()
        threadHandlerSem.release()
        time.sleep(THREAD_TIME)
