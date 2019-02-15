import sys
import time
import logging

from socketio import socketio_manage
from socketio.mixins import BroadcastMixin
from socketio.namespace import BaseNamespace

from DataAggregation.webdata_aggregator import getAvailableWorkshops


logger = logging.getLogger(__name__)
std_out_logger = logging.StreamHandler(sys.stdout)
logger.addHandler(std_out_logger)


def broadcast_msg(server, ns_name, event, *args):
    pkt = dict(type="event",
               name=event,
               args=args,
               endpoint=ns_name)

    for sessid, socket in server.sockets.iteritems():
        socket.send_packet(pkt)


def workshops_monitor(server):
    sizes = []
    workshops = getAvailableWorkshops()
    for w in workshops:
        tmp = [w.workshopName, w.q.qsize()]
        sizes.append(tmp)
        broadcast_msg(server, '', "sizes", tmp)

    while True:
        logger.info("Participants viewing frontend:" + str(len(server.sockets)))
        workshops_available = []
        curr_workshops = getAvailableWorkshops()
        for w in curr_workshops:
            workshops_available.append([w.workshopName, w.q.qsize()])
            wq = filter(lambda x: x[0] == w.workshopName, sizes)[0]
            if wq[1] != w.q.qsize():
                wq[1] = w.q.qsize()
                logging.info("client_updater: New update being pushed to clients: " + str(wq))
                broadcast_msg(server, '', 'sizes', wq)
        logger.info("Workshops available:" + str(workshops_available))
        time.sleep(1)


class RequestHandlerApp(object):
    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith('/socket.io'):
            socketio_manage(environ, {'': QueueStatusHandler})


class QueueStatusHandler(BaseNamespace, BroadcastMixin):
    def on_connect(self):
        sizes = []
        workshops = getAvailableWorkshops()
        for w in workshops:
            tmp = [w.workshopName, w.q.qsize()]
            sizes.append(tmp)
            self.emit('sizes', tmp)
