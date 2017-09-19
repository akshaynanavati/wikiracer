#!/usr/bin/env python3

from gevent import monkey
import argparse
import json
import os
import sys
import jinja2

dir_path = os.path.dirname(os.path.realpath(__file__))
SRC_DIR = os.path.join(dir_path, '..', 'src')
TEMPLATES_DIR = os.path.join(SRC_DIR, 'templates')
sys.path.append(SRC_DIR)

from util.wiki import registry # NOQA


def main():
    parser = argparse.ArgumentParser('python wikiracer.py')
    parser.add_argument(
        '--dump-graph', dest='output_file', metavar='OUTPUT_FILE',
        help='JSON file path to dump the graph to'
    )
    parser.add_argument(
        '--sample', dest='sample', metavar='SAMPLE', type=float,
        help='Edge sample frequency for graph dump'
    )
    parser.add_argument('--src', help='Comma separated list of wikipedia source titles', default='')
    parser.add_argument('--dest', help='Comma separated list of wikipedia destination titles', default='')
    parser.add_argument(
        '--visualize', dest='input_file', metavar='INPUT_FILE',
        help='JSON file path of graph to visualize'
    )

    args = parser.parse_args()

    if args.input_file:
        loader = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR))
        with open(args.input_file) as f:
            graph = json.load(f)
            template = loader.get_template('graph.html')
            output = template.render(**graph)
            with open('graph_vis.html', 'w') as f:
                f.write(output)
        sys.exit(0)

    for src, dest in zip(args.src.split(','), args.dest.split(',')):
        src_node = registry.get_node(src.strip())
        dest_node = registry.get_node(dest.strip())
        path = src_node.find_path(dest_node)
        if path:
            print('Found path for {} -> {}: {}'.format(src, dest, path))
        else:
            print('No path found for {} -> {}'.format(src, dest))

    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(registry.to_json(sample=args.sample), f)


if __name__ == '__main__':
    monkey.patch_all()
    main()
