"""
Get URL from CVM website.

@author: caiomts
@email: caiomts@gmail.com
"""


def urls_cvm(url='http://dados.cvm.gov.br/dados/CIA_ABERTA/',
             ver='2017-09-16 12:54  '):
    """
    Acess to CVM website from the default URL,
    access all directories and get links to download the files
    with the date of the last modification. Returns a dictionary,
    whose key is the link and the variable is the date.

    Parameters
    ----------
    url: str,
    ver: str, The default is '2017-09-16 12:54  '

    Returns
    -------
    Dict
        Dict keys: links,
        variable: last modification date
    """
    import requests
    from bs4 import BeautifulSoup as BS
    urls_dict = {url: ver}
    links_dict = {}
    urls = [url]
    for url in urls:
        if url.endswith(('.zip', '.txt', '.csv')) is False:
            r = requests.get(url, stream=True)
            if not r.status_code == 200:
                return ValueError
            try:
                page = BS(r.content, 'lxml')
                tags = page.find_all('a')
                lastmods = page.find_all('td', class_='indexcollastmod')
                names = [tag.get_text() for tag in tags]
                links = [url + tag.get('href') for tag in tags]
                dates = [lastmod.get_text() for lastmod in lastmods]
                i = names.index('Parent Directory') + 1
                j = 1
                while True:
                    if not i < names.index('conjunto de dados'):
                        break
                    urls_dict[links[i]] = dates[j]
                    urls.append(links[i])
                    i += 1
                    j += 1
            except AttributeError('get tag error'):
                return None
        else:
            links_dict[url] = urls_dict[url]
    return links_dict
