import requests
import re

INTERNALS = 0
EXTERNALS = 1

# TODO: Also not match keywords in other languages other than English

# Returns (ints: Set, exts: List)
def get_links(url):
    content = requests.get(url=url, params=None).content.decode('utf-8')
    if content==None:
        return null
    links = list(map(lambda s: s[6:-1], re.findall('href="[^"]*"', content)))
    ints = set()
    exts = list()
    for link in links:
        # Other countries' Wikipedia domains - not traversed at the moment (only EN wiki pages)
        if re.match('(http|https|ftp)://[^.]*[.]wikipedia[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]mediawiki[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wikimedia[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wikidata[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wiktionary[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wikisource[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wikibooks[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wikiquote[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]wikimediafoundation[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wikivoyage[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wikinews[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wikiversity[.]org.*', link) or \
                re.match('(http|https|ftp)://[^.]*[.]wmflabs[.]org.*', link):
            continue
            # if re.match('.*[/]wiki[/].*', link):
                # ints.add(link)
        # External links
        elif re.match('(http|ftp).*', link):
            exts.append(get_domain(link))
        # en.wikipedia
        elif re.match('.*[/]wiki[/].*', link) \
                and not re.match('.*(Help|Special|User|Category|File|Template|Template_talk|Wikipedia|Track):.*', link):
            if link[0] != '/':
                link = '/' + link
                print(link)
            ints.add(get_protocol(url) + '://' + get_domain(url) + link)
    return (ints, exts)

# Assuming format: (http)|(https)|(ftp)://DOMAIN/?.*
def get_domain(url):
    tmp = re.search('://[^/]*/', url)
    # To deal with urls not ending in '/'
    if tmp == None:
        return re.search('://[^/]*', url).group()[3:]
    return tmp.group()[3:-1]

# Assuming format: (http)|(https)|(ftp)://DOMAIN/?.*
def get_protocol(url):
    return re.search('.*://', url).group()[:-3]

# Returns (visited: Set, exts: List) 
def index(url, visited=None):
    if visited == None:
        visited = set()
    # Realistic cap
    elif len(visited) >= 10000:
        return (set(), list())
    visited.add(url)
    print(len(visited))
    # Get links of this page
    (ints, exts) = get_links(url)
    # Recursively get links within internal links and append them
    for url in ints:
        if url in visited:
            continue
        (visited_tmp, exts_tmp) = index(url, visited)
        exts.extend(exts_tmp)
        visited = visited.union(visited_tmp)
    return (visited, exts)
 
def get_domain_visits(links):
    domains = {link:links.count(link) for link in links}
    domains = {k: v for k, v in sorted(domains.items(), key=lambda item: item[1], reverse=True)}
    return domains


base_url = 'https://en.wikipedia.org/wiki/Main_Page'
links = index(base_url)
print(get_domain_visits(links[EXTERNALS]))
