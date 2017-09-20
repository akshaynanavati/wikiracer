# Wikiracer

## Overview
Wikiracer is a Python web service to solve the [wikirace](https://en.wikipedia.org/wiki/Wikipedia:Wikirace) game. It
takes a source wikipedia page title and a destination wikipedia page title and returns json data containing a path
from source to destination. While it usually returns the shortest path, it is optimized for speed and therefore is not
guaranteed to return the shortest path.

Note that this respository _requires_ Python 3.6+ to run.

## Installation

### Method One - Docker

There is a Dockerfile that can be built and run on your machine if you have [docker](https://www.docker.com/). You can
follow the instructions [here](https://docs.docker.com/get-started/) to do so.

### Method Two - Python Server

You could also just run the server on your machine. Assuming you have a network connection, everything should work
out of the box.

Assuming you have [fabric](https://get.fabric.io/), Python 3.6 installed at `/usr/local/bin/python3.6`,
[virtualenv](https://virtualenv.pypa.io/en/stable/), and [pip](https://pip.pypa.io/en/stable/installing/)
installed, you can just run `fab install server` to get the server running.

### Method Three - Python CLI

Use `fab install` to install all dependenices into a venv (or get the dependencies in some other way). Make sure you
have either sourced the venv or the dependencies are available when the script is run. Then, the CLI can be run as
follows (note that `--dump-graph` is optional and `--sample` is only used by `--dump-graph`):

```
# Sample input and output
# This will also dump a graph to graph.json by randomly picking 5% of the edges

$ ./bin/wikiracer.py \
    --src "Beijing,USB,San Francisco" \
    --dest "Mike Tyson,Scuba Diving,Tokyo" \
    --dump-graph graph.json --sample 0.05

Found path for Beijing -> Mike Tyson: ['Beijing', '1928 Winter Olympics', 'Romania', 'Diego Maradona', 'Mike Tyson']
Found path for USB -> Scuba Diving: ['USB', 'Barnes & Noble', 'Indonesia', 'Manta ray', 'Scuba Diving']
Found path for San Francisco -> Tokyo: ['San Francisco', 'Barcelona', 'Tokyo']
```

You can also use the CLI to visualize the graph (assuming the graph was dumped via `--dump-graph`; note that you cannot
pass `--src` and `--dest` and also visualize the graph):

```
# This will produce an output file graph_vis.html which can then be viewed in the browser

$ ./bin/wikiracer.py --visualize graph.json
$ open graph_viz.html
```



CLI Help Message:

```
usage: python wikiracer.py [-h] [--dump-graph OUTPUT_FILE] [--sample SAMPLE]
                           [--src SRC] [--dest DEST] [--visualize INPUT_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --dump-graph OUTPUT_FILE
                        JSON file path to dump the graph to
  --sample SAMPLE       Edge sample frequency for graph dump
  --src SRC             Comma separated list of wikipedia source titles
  --dest DEST           Comma separated list of wikipedia destination titles
  --visualize INPUT_FILE
                        JSON file path of graph to visualize
```

### Mixpanel

This service supports Mixpanel tracking. However, due to security I have redacted my own Mixpanel access token. If you
wish to use Mixpanel tracking, you must update the project token in the
[config](https://github.com/akshaynanavati/wikiracer/blob/master/src/config.py) file and set `MP_ENABLED = True`.
This will send the following data points to Mixpanel under the event type `request` with user id `'1'`:

- The number of nodes in the graph
- The number of edges in the graph
- The number of nodes visited in the request
- Time elapsed to arrive at a solution (only includes time taken to do the BFS including the asynchronous I/O to
media wiki, but is not the end to end latency)
- Length of the found path
- Number of wiki media api requests completed in order to find the solution

The Mixpanel tracking happens asynchronously - events get pushed onto a queue and there is a greenlet reading off
the queue and sending data to Mixpanel.

## API Specification

The API endpoints are structured as `http://<host>:<port>/<namespace>/v<version>/<path>`. The below docs will specify
the URL from namespace onwards. Note that this API is not exactly defined to handle edge cases (e.g. malformed input,
networking errors, etc) and

### Namespace: wikiracer

`GET /wikiracer/v1/path?src=<title>&dest=<title>`
Returns a JSON blob containing the path from src to dest as a list of titles if it exists, or null otherwise.

Arguments:

- `src`: The title of the source page
- `dest`: The title of the dest page

Example:

Request: `GET /wikiracer/v1/path?src=Segment&dest=Career`

Response:

```
{
  "data": {
    "path": [
      "Segment",
      "Fruit anatomy",
      "Botany",
      "Scientist",
      "Career"
    ]
  },
  "error": null
}
```

### Namespace: wikigraph

This namepsace provides endpoints to monitor the state of the in memory wikipedia graph.

`GET /wikigraph/v1/display?[sample=<float>&][src=<title>&dest=<title>]`

Returns an interactive HTML page visualizing the wikipedia graph using [vis.js](http://visjs.org/).

Arguments:

- `src`: The title of the source page. If both src and dest are set, a path will be found from src to dest
and highlighted in the graph.
- `dest`: The title of the dest page. If both src and dest are set, a path will be found from src to dest
and highlighted in the graph.
- `sample`: The edges included in the visualization will randomly be sampled with this frequency
(between 0 and 1). E.g. if sample = 0.1, an edge will be included 10% of the time. A node will
only be included if at least one edge to or from the node is included. This naturally biases nodes
with higher degree being included in the visualization. **It is highly recommended that you set a
sample parameter when calling this as the number of edges can grow quite large and this endpoint will
crash your browser if it's rendering too many edges**

Example:

Request: `GET /wikigraph/v1/display?sample=0.05&src=San%20Francisco&dest=Mike%20Tyson`

![Graph Demo](https://media.githubusercontent.com/media/akshaynanavati/wikiracer/master/media/graph-demo.gif)

`GET /wikigraph/v1/clear`

Clears the entire in memory graph.

Example:

Request: `GET /wikigraph/v1/clear`

Response:

```
{
  "data": {
    "status": "ok"
  },
  "error": null
}
```

`GET /wikigraph/v1/json[?sample=<float>]`

Returns the JSON representation of the graph as a list of nodes and edges.

Arguments:

- `sample`: The edges included in the visualization will randomly be sampled with this frequency
(between 0 and 1). E.g. if sample = 0.1, an edge will be included 10% of the time. A node will
only be included if at least one edge to or from the node is included. This naturally biases nodes
with higher degree being included in the visualization.

Example (truncated for brevity):

Request: `GET /wikigraph/v1/json`

Response:

```
{
  "data": {
    "edges": [
      {
        "color": "#D2E5FF",
        "from": 4427453440,
        "to": 4427398896
      },
      ...
    ],
    "nodes": [
      {
        "id": 4425259048,
        "label": "Adonis Stevenson"
      },
      ...
    ]
  },
  "error": null
}
```

## Implementation

The service uses the [MediaWiki](https://www.mediawiki.org/wiki/API:Main_page) API to fetch link data about a page
and performs a bidirectional BFS from the src and from the dest till they visit a common page. This works because
the MediaWiki api provides a way of fetching links from a page and also links to a page. The in memory graph maintains
links to a given title as well as links from a given title. It is a single threaded service that handles one request
at a time, but could easily be distributed across many processes nodes. However, they currently do not share the
in memory graph.

It is implemented using [gevent](http://www.gevent.org/), a library for Python that provides lightweight coroutines
and asynchronous I/O.

When a request comes in, a pool of fetch workers are spawned which will listen on a queue of titles that need neighbors
to be fetched from MediaWiki. When the request completes, a callback is called on the neighbors which will enqueue
the neighbors onto the to visit queue for the BFS, update the came from mapping for the BFS, and cache the results
to the graph in memory. Initially the queue of things to be fetched is empty.

There is a single worker which performs the BFS. It maintains 2 to visit queues (one for the forward search from src
and another for the backwards search from dest) which are both seeded with src and dest respectively. It also maintains
2 came from mappings (again one for forward and the other for the reverse bfs) that keeps track of the parent for each
node visited in the BFS. It pops one node off the forward to visit set. If there are neighbors in memory it enqueues
them, otherwise it enqueues the node to the fetch queue. It alternates between the forward search and the reverse search.

Currently the service keeps the full wikipedia page graph in memory. There are two potential issues with this which I
will address here:

1) The graph will keep growing larger till it runs out of memory.

   There are currently only about
   [5 million wikipedia pages](https://en.wikipedia.org/wiki/Wikipedia:Size_of_Wikipedia). If
   we assume that wikipedia titles are on average 200 bytes, storing just the links in memory would take up 1GB.
   The edges can simply be pointers to nodes (8bytes). If each node on average has 375 out and in edges, the edges
   can be stored in 15 GB which means the whole wikipedia graph would take at worst 16 GB. However, we will likely
   not need the whole graph to make most queries fast, so this probably should be okay. In the Future Work section,
   I discuss ways to support eviction.

2) The nodes are never evicted so we could have stale links in memory.

   This is true, however I have chosen not to handle that in this implementation as pages probably change quite
   infrequently. In the Future Work section I address ways to account for this.

### Future Work

1) Shared cache

   If we truly wanted to distribute this service across multiple processes or machines, it would make sense to have a
   shared cache. We could use [Redis](redis.io) to store the graph. Then, the BFS would first check to see if it has a
   cached subset of this in memory and if not, the fetchers would check Redis and then finally make a call to MediaWiki.
   This would also allow us not to store the whole graph in memory but rather let redis store the cache on a machine
   with enough RAM.

2) Evicting nodes

   In order to keep the results as up to date as possible it would make sense to partially invalidate the cache
   periodically. One way of supporting this is to set a TTL. When a node is accessed, if it's neighbors are expired,
   they will be re-fetched from MediaWiki. Redis supports this out of the box, but in memory we would have to do a bit
   more work to implement TTL correctly.

3) More intelligent search

   Performing offline analysis on the graph could provide insight that makes the search more efficient. One way of doing
   this is to do analysis on the graph and find well connected nodes (e.g. the top 10,000 nodes based on the sum of in
   and out edges). The paths between these nodes can be pre-computed and then the problem reduces to finding a
   path from source into this sub-graph or dest into this sub-graph.

   Another possibility is to use NLP, word similarity measures, or some other heuristics to inteligently sort the nodes
   in the to visit queue using a heap. This could allow us to reach a path quicker as it will only search things
   approaching the dest.

4) Using a language better suited to the task

   I used Python to solve this problem because it is the language I am most familliar with. However, I believe
   [Golang](https://golang.org/) is probably better suited to solve a problem like this. The only reason this is
   reasonably efficient in Python despite the GIL is because of Gevent. Gevent provides co-routines which are very
   similar to go routines and an asynchronous queue similar to a channel in Go. As I have architected the code around
   this paradigm, re-writing it in Go should not be terribly challenging.

## Benchmarking Methodology

All benchmark statistics in this document were run on an AWS t2.micro instance in the following way: The server
was run in a single process on the machine with `fab server` and I used
[this load testing script](https://github.com/akshaynanavati/wikiracer/blob/master/load_test/load_test.py) to select
random src, dest pairs and hit the locally running API. Note that the load_test.py script "seeds" the graph initially
by making requests to a few pre-picked src dest pairs. On each request, the server sent the following statistics
to Mixpanel:

- The number of nodes in the graph
- The number of edges in the graph
- The number of nodes visited in the request
- Time elapsed to arrive at a solution (only includes time taken to do the BFS including the asynchronous I/O to
media wiki, but is not the end to end latency)
- Length of the found path
- Number of wiki media api requests completed in order to find the solution

There are Dockerfiles that will execute the above in any environment if run with:

```
docker run -P segment
docker run --link <name-of-segment-container>:segment-api segment_load_test
```

Note that you might have to change the host in the load_test.py file to be `http://segment-api:80` if you go down this
route.

The raw data with some charts from the benchmarks can be found
[here](https://docs.google.com/spreadsheets/d/1_NrliQuI6-Ye39LHecfxc7QNgTjGqskQIbN4owjwpjc/edit#gid=1632399110).

## Performance
On each request, the web service caches the Wikipedia graph in memory and lazily builds it up. Therefore on average
subsequent requets should be faster than earlier requests as there are fewer required network calls to get to the
solution.

Below are the raw latency numbers for about 100 random src/dest results:

| Statistic | Time (s) |
| --- | --- |
| Average | 1.10 |
| Standard Deviation | 0.54 |
| 50th Percentile | 1.00 |
| 95th Percentile | 2.01 |
| 99th Percentle | 2.79 |
| Min | 0.32 |
| Max | 3.44 |

The distribution is illustrated by this histogram:

![Time Elapsed Distribution](https://docs.google.com/spreadsheets/d/e/2PACX-1vTRjJ1F49mrgs7Hi-EmVVwkGTrcK0giIlBgxrNKHCBs3-WMA-XcX1qvDpPsUVYInKgXFQlV-bUJ5GJC/pubchart?oid=1557691184&format=image)

## The Wikipedia Graph
While running the benchmark, there were a few interesting insights I gained about the traversal of the wikipedia graph.

This chart shows that the number of nodes and edges cached grew linearly. In fact, on average the number
of edges was approximately twice the number of nodes:

![Nodes vs Edges](https://docs.google.com/spreadsheets/d/e/2PACX-1vTRjJ1F49mrgs7Hi-EmVVwkGTrcK0giIlBgxrNKHCBs3-WMA-XcX1qvDpPsUVYInKgXFQlV-bUJ5GJC/pubchart?oid=324926198&format=image)

Furthermore, we see here that the size of the graph in memory reaches an asymptote:

![Graph Size Over Time](https://docs.google.com/spreadsheets/d/e/2PACX-1vTRjJ1F49mrgs7Hi-EmVVwkGTrcK0giIlBgxrNKHCBs3-WMA-XcX1qvDpPsUVYInKgXFQlV-bUJ5GJC/pubchart?oid=1772041664&format=image)
