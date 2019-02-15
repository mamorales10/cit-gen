import logging
import signal

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
from socketio.server import SocketIOServer

import DataAggregation.webdata_aggregator
import VMStateManager.vbox_monitor
from WebServer.flask_server import app, threadHandler
from RequestHandler.client_updater import RequestHandlerApp, workshops_monitor
from manager_constants import FLASK_PORT, SOCKET_IO_PORT

gevent.monkey.patch_all()


def signal_handler(signal, frame):
    try:
        logging.info("Killing webserver...")
        httpServer.stop()
        logging.info("Killing threads...")
        gevent.kill(srvGreenlet)
        gevent.kill(ioGreenlet)
        gevent.kill(stateAssignmentThread)
        gevent.kill(restoreThread)
        gevent.kill(threadHandler)
        VMStateManager.vbox_monitor.cleanup()

        exit()
    except Exception as e:
        logging.error("Error during cleanup"+str(e))
        exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    logging.getLogger().setLevel(logging.DEBUG)

    httpServer = WSGIServer(('0.0.0.0', FLASK_PORT), app)
    sio_server = SocketIOServer(('0.0.0.0', SOCKET_IO_PORT), RequestHandlerApp(), namespace="socket.io")
    stateAssignmentThread = gevent.spawn(VMStateManager.vbox_monitor.manageStates)
    restoreThread = gevent.spawn(VMStateManager.vbox_monitor.makeRestoreToAvailableState)
    srvGreenlet = gevent.spawn(httpServer.start)
    ioGreenlet = gevent.spawn(sio_server.serve_forever)
    dataAggregator = gevent.spawn(DataAggregation.webdata_aggregator.aggregateData)
    threadHandler = gevent.spawn(threadHandler)
    clientHandlerThread = gevent.spawn(workshops_monitor, sio_server)

    try:
        # Let threads run until signal is caught
        gevent.joinall([srvGreenlet, stateAssignmentThread, restoreThread, dataAggregator, threadHandler, ioGreenlet, clientHandlerThread])
    except Exception as e:
        logging.error("An error occurred in threads" + str(e))
        exit()
