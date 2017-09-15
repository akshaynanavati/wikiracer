import copy
import time
import gevent
from gevent import queue
from mixpanel import Mixpanel

from config import MP_PROJECT_TOKEN, MP_ENABLED

_mp = Mixpanel(MP_PROJECT_TOKEN)
to_send = queue.Queue()


class MpTracker(object):
    _mp_data = {}

    @staticmethod
    def reset():
        MpTracker._mp_data = {}
        MpTracker._mp_data['num_visited'] = 0
        MpTracker._mp_data['num_api_requests'] = 0
        MpTracker._mp_data['time'] = time.time()

    @staticmethod
    def get():
        return copy.deepcopy(MpTracker._mp_data)

    @staticmethod
    def set(k, v):
        MpTracker._mp_data[k] = v

    @staticmethod
    def incr(k):
        MpTracker._mp_data[k] += 1


def worker():
    if not MP_ENABLED:
        return

    while True:
        try:
            event_type, data = to_send.get()
            if data['num_visited'] == 0:
                continue
            _mp.track('1', event_type, data)
        except Exception as e:
            print(e)
            continue


def send(event_type, data):
    if not MP_ENABLED:
        return

    if 'time' not in data:
        data['time'] = int(time.time())
    to_send.put((event_type, data))


mp_thread = gevent.spawn(worker)
