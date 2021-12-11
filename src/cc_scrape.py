import io
import panflute
import requests

def panflute_to_string(container):
    string = ''
    for elem in container:
        if isinstance(elem, panflute.Str):
            string += elem.text
        elif isinstance(elem, panflute.Space):
            string += ' '
    return string

def action(elem, doc, links):
    if isinstance(elem, panflute.Link):
        name = panflute_to_string(elem.content)
        links.append((name, elem.url))

def prepare(doc):
    pass

def scrape_listing_url(url):
    links = []
    if url.endswith('.md'):
        fmt = 'markdown'
    else:
        raise Exception('unknown format')

    print(f'fetching {url}')
    response = requests.get(url)
    response.raise_for_status()
    doc = panflute.convert_text(response.text, input_format=fmt, standalone=True)
    panflute.run_filter(action, prepare=prepare, doc=doc, links=links)
    return links
