import random

from util.wiki.graph import WikiNode

# Maintains a mapping of nodes we've seen by title to the WikiNode object in memory.
_registry = {}


def get_node(title):
    if title not in _registry:
        _registry[title] = WikiNode(title)
    return _registry[title]


def clear():
    global _registry
    _registry = {}


def counts():
    num_nodes = len(_registry)
    num_edges = sum((len(node.links) + len(node.linkshere) for node in _registry.values()))
    return num_nodes, num_edges


def to_json(path=None, sample=None):
    path = path or []

    path_color = 'red'
    edge_color = '#D2E5FF'
    edges = []
    nodes = {}

    for title, node in _registry.items():
        for edge_node in node.links:
            if sample and random.random() > sample:
                continue
            edges.append({'from': node.id, 'to': edge_node.id, 'color': edge_color})
            nodes[node.id] = {'label': node.title}
            nodes[edge_node.id] = {'label': edge_node.title}

        for edge_node in node.linkshere:
            if sample and random.random() > sample:
                continue
            edges.append({'to': node.id, 'from': edge_node.id, 'color': edge_color})
            nodes[node.id] = {'label': node.title}
            nodes[edge_node.id] = {'label': edge_node.title}

    for i in range(0, len(path) - 1):
        node_src = _registry[path[i]]
        node_dest = _registry[path[i + 1]]
        edges.append({'from': node_src.id, 'to': node_dest.id, 'color': path_color})

    for title in path:
        node = _registry[title]
        nodes[node.id] = {'label': node.title, 'color': path_color}

    return {'nodes': [dict(id=id, **props) for id, props in nodes.items()], 'edges': edges}


def _sample(sample):
    d = {}

    for k, v in _registry.items():
        if random.random() < sample:
            d[k] = v

    return d
