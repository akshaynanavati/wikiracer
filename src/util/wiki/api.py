from urllib import request, parse
import json
import util.mixpanel as mp

BASE_URL = 'https://en.wikipedia.org/w/api.php?action=query&format=json'


def fetch_links(page_title, cont=None):
    url = BASE_URL + '&titles={title}'.format(title=parse.quote(page_title)) + '&prop=links&pllimit=500'
    if cont:
        url += '&plcontinue={cont}'.format(cont=parse.quote(cont))
    return _fetch(url, 'plcontinue', 'links')


def fetch_linkshere(page_title, cont=None):
    url = BASE_URL + '&titles={title}'.format(title=parse.quote(page_title)) + '&prop=linkshere&lhlimit=500'
    if cont:
        url += '&lhcontinue={cont}'.format(cont=parse.quote(cont))
    return _fetch(url, 'lhcontinue', 'linkshere')


def _fetch(url, cont_key, prop):
    mp.MpTracker.incr('num_api_requests')
    response = request.urlopen(url)
    body = json.loads(response.read())
    try:
        cont = body['continue'][cont_key]
    except KeyError:
        cont = None
    links = _get_links(body, prop)
    return (cont or 'DONE', links)


def _include_title(title):
    return True


def _get_links(body, prop):
    pages = body['query']['pages']
    assert len(pages) == 1

    for _, v in pages.items():
        if prop not in v:
            return []
        return [d['title'] for d in v[prop] if _include_title(d['title'])]
