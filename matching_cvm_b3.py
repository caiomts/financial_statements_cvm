"""
This script creates a dataset based on the cvm records and the dataset with
information on stocks by sectors that belong to the B3 IBrA index.

@author: caiomts
@email: caiomts@gmail.com
"""


def b3_to_cvm(rec_path, proj_path, datasets_path, index_b3='IBrA'):
    """
    Create a dataset from CVM records and a specific B3 index
    grouped by sectors.

    Parameters
    ----------
    rec_path: records path
    proj_path: project path
    datasets_path: dataset will be created in this path
    index_b3: Some b3 index. By default IBrA

    Returns
    -------
    Creates a dataset and return a pandas.DataFrame
    """
    import stocks_index_by_sector as stindexsec
    import read_records as readrec
    import pandas as pd
    from fuzzywuzzy import process

    ibra_stocks = stindexsec.stocks_in_index_by_sector(path=proj_path,
                                                       index=index_b3)
    cvm_records = readrec.read_records(rec_path)

    def matching(rec_path):
        """matching CVM code with companies names by B3"""
        import requests
        from bs4 import BeautifulSoup as BS
        import read_records as readrec
        import datetime as dt
        import pandas as pd

        ano = str(dt.date.today().year)
        cvm_codes = readrec.read_records(rec_path)['CD_CVM']
        df = pd.DataFrame(data=0, index=cvm_codes, columns=['companies'])
        for cod in cvm_codes:
            cvm_cod = str(cod)
            url = ('http://bvmf.bmfbovespa.com.br/pt-br/mercados/acoes/'
                   'empresas/'
                   'ExecutaAcaoConsultaInfoEmp.asp?CodCVM='+cvm_cod+'&'
                   'ViewDoc=1&AnoDoc='+ano+'&VersaoDoc=1&NumSeqDoc=90583#a')
            r = requests.get(url)
            if not r.status_code == 200:
                return ValueError
            try:
                page = BS(r.content, 'lxml')
                tag = page.find_all('td')[1].get_text()
                df[df.index == cod] = tag
            except (TypeError, IndexError):
                df[df.index == cod] = None
        return df

    matches = matching(rec_path)
    cvm_names_mer = pd.merge(cvm_records, matches,
                             left_on='CD_CVM', right_index=True)
    companies = {
        'companie_name': [process.extract(string,
                          matches.companies, limit=1)[0][0]
                          for string in ibra_stocks.Companies],
        'companie_match': [process.extract(string,
                           matches.companies, limit=1)[0][1]
                           for string in ibra_stocks.Companies],
        'Companies': [string for string in ibra_stocks.Companies]
                           }
    companies = pd.DataFrame(data=companies)

    comp_cvm = pd.merge(companies, cvm_names_mer, how='inner',
                        left_on='companie_name', right_on='companies')
    df = pd.merge(ibra_stocks,
                  comp_cvm, how='inner',
                  on='Companies')
    df.drop_duplicates(inplace=True)
    df.to_csv(datasets_path, index=False)
    return df[['Sectors', 'Subsectors', 'Segments', 'y_ticker',
              'companies', 'CD_CVM']]
