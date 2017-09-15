from flask import Blueprint, request
import time

from util.api import API
from util.wiki import registry
import util.mixpanel as mp
from config import MP_ENABLED

bp = Blueprint('wikiracer', __name__)
api = API(bp, namespace='wikiracer')


@api.route('/path', methods=['GET'])
def path():
    src = request.args['src']
    dest = request.args['dest']
    src_node = registry.get_node(src)
    dest_node = registry.get_node(dest)

    mp.MpTracker.set('src', src)
    mp.MpTracker.set('dest', dest)

    now = time.time()
    path = src_node.find_path(dest_node)
    mp.MpTracker.set('time_elapsed', time.time() - now)

    if path:
        mp.MpTracker.set('path_size', len(path))

    # Since this can be a relatively expensive operation, let's not do it if we aren't tracking to mixpanel
    if MP_ENABLED:
        num_nodes, num_edges = registry.counts()
        mp.MpTracker.set('num_nodes', num_nodes)
        mp.MpTracker.set('num_edges', num_edges)

    return {'path': path}
