import util.mixpanel as mp


class Middleware(object):
    def pre(self):
        pass

    def post(self, data, error):
        pass


class MixpanelMiddleware(Middleware):
    def pre(self):
        mp.MpTracker.reset()

    def post(self, *_):
        mp.send('request', mp.MpTracker.get())


MIDDLEWARE = [MixpanelMiddleware()]
