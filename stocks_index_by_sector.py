"""
Download and format a DataFrame with companies by sector and tickers.

@author: caiomts
@email: caiomts@gmail.com
"""


def stocks_in_index_by_sector(index='IBrA', path=''):
    """
    Return a pandas.DataFrame with stocks belonging a given index with sector,
    site, name and yahoo ticker model.
    """
    import pandas as pd

    def index_by_sector(index, path=path):
        """Build a DataFrame from an index and a B3 table of sectors."""
        import pandas as pd
        import get_files_cvm as gfc
        import os
        # download and handle the index table.
        url = ('http://bvmf.bmfbovespa.com.br/indices/'
               'ResumoCarteiraTeorica.aspx?Indice='+index+'&idioma=en-us')
        b3_ind = pd.read_html(url)[0]
        b3_ind.dropna(inplace=True)
        b3_ind['Listing'] = b3_ind.Code.str[0:4]

        # download and tody sector file.
        url_sector = ('http://www.b3.com.br/lumis/portal/file/fileDownload'
                      '.jsp?fileId=8AA8D0975A2D7918015A3C804FA64C0B')
        gfc.download_from_url(url_sector, 'b3_sectors.zip',
                              path=path)
        gfc.extract_zip(path+'\\b3_sectors.zip',
                        path)
        name = os.listdir(path)[-1]

        df = pd.read_excel(path + '\\' + name,
                           skiprows=6, header=None,
                           names=['Sectors',
                                  'Subsectors', 'Companies',
                                  'Listing',
                                  'Type']).iloc[1:].drop_duplicates().dropna(
                               how='all')
        df.loc[pd.isna(df.Listing), 'Segments'] = df.Companies
        df.fillna(method='pad', inplace=True)
        df = df[(df.Sectors != 'SECTORS'
                 ) & (df.Listing != 'CODE'
                      ) & (df.Segments != df['Type']
                           )].drop_duplicates(subset='Listing')
        # Merge tables
        b3_df = pd.merge(b3_ind, df, how='inner',
                         on='Listing')[['Sectors', 'Subsectors', 'Segments',
                                        'Code', 'Companies', 'Type_x',
                                        'Part. (%)']]
        b3_df['y_ticker'] = b3_df.Code + '.SA'
        return b3_df

    def y_infos(tickers):
        """Scrape Yahoo Finance and get company business names and websites."""
        import pandas as pd

        def get_website(url):
            """get company name and website"""
            import requests
            from bs4 import BeautifulSoup as BS
            r = requests.get(url)
            if not r.status_code == 200:
                return ValueError
            try:
                page = BS(r.content, 'lxml')
                tags_h = page.find_all('h3')
                tags_a = page.find_all('a')
                return [tags_h[0].get_text(), tags_a[12].get_text()]
            except (TypeError, IndexError):
                return [None, None]

        l_names = {}
        for tk in tickers:
            web_url = 'https://finance.yahoo.com/quote/'+tk+'/profile'
            l_names[tk] = get_website(web_url)
        return pd.DataFrame(
            l_names).T.rename(columns={0: 'Business_name', 1: 'website'})

    return pd.merge(index_by_sector(index),
                    y_infos(index_by_sector(index)['y_ticker']),
                    left_on='y_ticker',
                    right_index=True, how='inner')
