from flask import Blueprint, request, render_template, make_response

from util.api import API
from util.wiki import registry

bp = Blueprint('wikigraph', __name__)
api = API(bp, namespace='wikigraph')


@api.route('/display', methods=['GET'])
def display():
    src = request.args.get('src')
    dest = request.args.get('dest')
    path = None

    if src and dest:
        src_node = registry.get_node(src)
        dest_node = registry.get_node(dest)
        path = src_node.find_path(dest_node)

    sample = request.args.get('sample')
    if sample:
        sample = float(sample)

    json = registry.to_json(path=path, sample=sample)
    return make_response(
        render_template('graph.html', **json),
        200,
        {'Content-Type': 'text/html; charset=utf-8'}
    )


@api.route('/json', methods=['GET'])
def json():
    sample = request.args.get('sample')
    if sample:
        sample = float(sample)

    return registry.to_json(sample=sample)


@api.route('/clear', methods=['GET'])
def clear():
    registry.clear()
    return {
        'status': 'ok'
    }
