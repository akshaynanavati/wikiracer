import gevent
from gevent import queue

from config import MAX_DISTANCE
from util.wiki.fetch_pool import WikiFetchPool
import util.mixpanel as mp


class WikiNode(object):
    """
    Representation of a Wikpedia page as a graph of title to out links and in links. Also
    maintains *continue state which allows us to lazily fetch neighbors via the MediaWiki API.
    """
    def __init__(self, title):
        self.id = id(self)
        self.title = title
        self.links = []
        self.linkshere = []
        self.plcontinue = None
        self.lhcontinue = None

    def get_links(self):
        if self.plcontinue == 'DONE':
            return self.links
        else:
            return None

    def get_linkshere(self):
        if self.lhcontinue == 'DONE':
            return self.linkshere
        else:
            return None

    def find_path(src_node, dest_node):
        if src_node.title == dest_node.title:
            return [src_node.title]

        fetch_pool = WikiFetchPool()

        to_visit_a = queue.Queue()
        to_visit_a.put((src_node, 0))
        came_from_a = {src_node: None}

        to_visit_b = queue.Queue()
        to_visit_b.put((dest_node, 0))
        came_from_b = {dest_node: None}

        # Run this as a gevent thread so that we can short circuit when a path is found
        # and clean up the fetch_pool.
        def worker():
            while True:
                path = _process_next(to_visit_a, came_from_a, came_from_b, fetch_pool)
                if path:
                    return path
                path = _process_next(to_visit_b, came_from_b, came_from_a, fetch_pool, forward=False)
                if path:
                    return list(reversed(path))

        worker_thread = gevent.spawn(worker)
        gevent.joinall([worker_thread])
        fetch_pool.kill()

        return worker_thread.value

    def __eq__(self, other):
        if other is None:
            return False
        return self.id == getattr(other, 'id', None)

    def __hash__(self):
        return self.id


def _build_path(came_from, node, rev=False):
    cur = node
    path = []
    while came_from[cur]:
        path.append(cur.title)
        cur = came_from[cur]
    path.append(cur.title)
    if rev:
        return path
    return list(reversed(path))


def _process_next(to_visit, came_from, target_frontier, fetch_pool, forward=True):
    cur, distance = to_visit.get(timeout=5)
    mp.MpTracker.incr('num_visited')

    def enqueue_neighbors(neighbors):
        if distance > MAX_DISTANCE:
            return

        for neighbor in neighbors:
            if neighbor in came_from:
                continue
            came_from[neighbor] = cur
            to_visit.put((neighbor, distance + 1))

    if cur in target_frontier:
        return _build_path(came_from, cur) + _build_path(target_frontier, cur, rev=True)[1:]

    frontier = None
    if forward:
        frontier = cur.get_links()
    else:
        frontier = cur.get_linkshere()

    if frontier is None:
        if forward:
            fetch_pool.fetch_links(cur, enqueue_neighbors)
        else:
            fetch_pool.fetch_linkshere(cur, enqueue_neighbors)
    else:
        enqueue_neighbors(frontier)
