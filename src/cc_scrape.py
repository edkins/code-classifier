import io
import panflute
import pypandoc
import requests

def action(elem, doc, links):
    if isinstance(elem, panflute.Link):
        links.append(elem.url)

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
    print('converting text with panflute')
    doc = panflute.convert_text(response.text, input_format=fmt, standalone=True)
    print('running filter')
    panflute.run_filter(action, prepare=prepare, doc=doc, links=links)
    print('done')
    return links
