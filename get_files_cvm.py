"""
Functions for downloading, unzipping and storing files.

@author: caiomts
@email: caiomts@gmail.com
"""


def download_from_url(url, file_name, path='', chunk_size=128):
    """
    Download a file from a specified url and save it in a given folder.

    Parameters
    ----------
    url: str,
    file_name: str,
    path: str,
    chunk_size: int.

    Returns
    -------
    None.
    """
    import requests
    import os
    r = requests.get(url, stream=True)
    if not r.status_code == 200:
        return ValueError
    try:
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
    except UnicodeError:
        return None
    if path != '':
        try:
            os.mkdir(path)
            os.replace(file_name, path + '/' + file_name)
        except FileExistsError:
            os.replace(file_name, path + '/' + file_name)


def extract_zip(file_name, folder):
    """Unzip a file and save it in a folder."""
    import zipfile
    with zipfile.ZipFile(file_name) as file:
        file.extractall(folder)


def get_files_cvm(folder_path=''):
    """
    Call three other functions: urls_cvm and download_from_url
    and extract_zip.
    For each key generated by urls_cvm it gets the date of last modification
    and the file name. If there is a file with the same name in
    the folder, it compares that date with the file's creation date and applies
    download_from_url only if it doesn't exist or is more recent. Apply
    extract_zip if required.

    Parameters
    ----------
    folder_path : str,
    Returns
    -------
    None.
    """
    from track_cvm_urls import urls_cvm
    import os
    import datetime
    urls = urls_cvm()
    keys = sorted(urls.keys())
    links = []
    names = []
    for key in keys:
        date_web = datetime.datetime.strptime(urls[key], '%Y-%m-%d %H:%M ')
        date_web_stamp = datetime.datetime.timestamp(date_web)
        file_web = key.split('/')[-1]
        try:
            date_local = os.path.getctime(folder_path + '/' + file_web)
            if not date_local > date_web_stamp:
                links.append(key)
                names.append(file_web)
            else:
                pass
        except FileNotFoundError:
            links.append(key)
            names.append(file_web)
    i = 0
    for link in links:
        try:
            download_from_url(link, names[i], folder_path)
            if '.zip' in names[i]:
                extract_zip(folder_path + '/' + names[i], folder_path)
            print(names[i])
        except Warning('error link: ' + link):
            pass
        i += 1