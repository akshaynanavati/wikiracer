from gevent import queue
import gevent

from config import NUM_FETCHERS
from util.wiki import api as wiki_api, registry


class WikiFetchPool(object):
    """
    A pool of workers listening on a queue to fetch links from MediaWiki and run a
    callback on the results.
    """
    def __init__(self):
        self.to_fetch = queue.Queue()
        self.fetcher_threads = [gevent.spawn(self._fetcher) for _ in range(NUM_FETCHERS)]

    def _fetcher(self):
        while True:
            prop, node, cb = self.to_fetch.get()
            if prop == 'links':
                fetcher = wiki_api.fetch_links
                cont_key = 'plcontinue'
            else:
                fetcher = wiki_api.fetch_linkshere
                cont_key = 'lhcontinue'

            while getattr(node, cont_key) != 'DONE':
                cont, frontier_titles = fetcher(node.title, getattr(node, cont_key))
                frontier = [registry.get_node(title) for title in frontier_titles]
                setattr(node, cont_key, cont)
                getattr(node, prop).extend(frontier)
                cb(frontier)

    def _fetch(self, prop, node, cb):
        if prop == 'links':
            continuation = node.plcontinue
        else:
            continuation = node.lhcontinue

        if continuation is None:
            self.to_fetch.put((prop, node, cb))
        elif continuation == 'DONE':
            cb(getattr(node, prop))
        else:
            cb(getattr(node, prop))
            self.to_fetch.put((prop, node, cb))

    def fetch_links(self, node, cb):
        self._fetch('links', node, cb)

    def fetch_linkshere(self, node, cb):
        self._fetch('linkshere', node, cb)

    def kill(self):
        gevent.killall(self.fetcher_threads)
