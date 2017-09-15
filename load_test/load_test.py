from urllib import request, parse
import sys
import random

HOST = 'http://localhost:5001'
PATH_BASE_URL = HOST + '/wikiracer/v1/path?src={src}&dest={dest}'
CLEAR_BASE_URL = HOST + '/wikigraph/v1/clear'

TITLE_FILE = 'titles.txt'


def clear_cache():
    url = CLEAR_BASE_URL
    request.urlopen(url)


def do(src, dest):
    url = PATH_BASE_URL.format(src=parse.quote(src), dest=parse.quote(dest))
    try:
        request.urlopen(url)
    except:
        return


def main():
    clear_cache()

    seeds = [
        ('Scuba_diving', 'USB'),
        ('San_Francisco', 'Beijing'),
        ('President', 'Entropy'),
    ]
    for src, dest in seeds:
        do(src, dest)

    titles = []
    with open(TITLE_FILE) as f:
        for i, line in enumerate(f):
            if i % 10 == 0:
                titles.append(line.strip())

    n = int(sys.argv[1])
    for i in range(n):
        src = titles[random.randint(0, len(titles) - 1)]
        dest = titles[random.randint(0, len(titles) - 1)]
        do(src, dest)


if __name__ == '__main__':
    main()
