import requests
import time
import re

# TODO: Also not match keywords in other languages other than English

TARGET = 100
ENG_ARTICLES = 6000000

def get_links(url, externals):
    content = requests.get(url=url, params=None).content.decode("utf-8")
    if content==None:
        return null
    links = list(map(lambda s: s[6:-1], re.findall('href="[^"]*"', content)))
    ints = set()
    for link in links:
        # Other countries' Wikipedia domains - not traversed at the moment (only ENG wiki pages)
        if re.match("(http|https|ftp)://[^.]*[.]wikipedia[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]mediawiki[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wikimedia[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wikidata[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wiktionary[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wikisource[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wikibooks[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wikiquote[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]wikimediafoundation[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wikivoyage[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wikinews[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wikiversity[.]org.*", link) or \
                re.match("(http|https|ftp)://[^.]*[.]wmflabs[.]org.*", link):
            continue
        # External links
        elif re.match("(http|ftp).*", link):
            domain = get_domain(link)
            if domain in externals:
                externals[domain] += 1
            else:
                externals[domain] = 1
        # en.wikipedia
        elif re.match(".*[/]wiki[/].*", link) \
                and not re.match(".*(Help|Special|User|Category|File|Template|Template_talk|Wikipedia|Track):.*", link):
            if link[0] != "/":
                link = "/" + link
            ints.add(get_protocol(url) + "://" + get_domain(url) + link)
    return ints

def get_domain(url):
    ''' Assuming format: (http)|(https)|(ftp)://DOMAIN/?.* '''
    tmp = re.search("://[^/]*/", url)
    # To deal with urls not ending in "/"
    if tmp == None:
        return re.search("://[^/]*", url).group()[3:]
    return tmp.group()[3:-1]

def get_protocol(url):
    ''' Assuming format: (http)|(https)|(ftp)://DOMAIN/?.* '''
    return re.search(".*://", url).group()[:-3]

def index(base_url):
    visited = set()
    to_visit = [base_url]  # implemented as a queue
    externals = {}

    while len(visited) < TARGET:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        internals = get_links(url, externals)
        to_visit.extend(internals)

    return externals
 
def main():
    start = time.time()
    base_url = "https://en.wikipedia.org/wiki/Main_Page"
    links = index(base_url)
    elapsed = time.time() - start
    print(sorted(links.items(), key=lambda x: x[1], reverse=True), end="\n\n")
    print("Time to index", TARGET, "links:", "{:.2f}".format(elapsed), "seconds", end="\n\n")
    print("It would take", "{:.2f}".format(elapsed * (ENG_ARTICLES/TARGET) / 86400), "days to index the entire English Wikipedia", end="\n\n")

if __name__ == "__main__":
    main()

