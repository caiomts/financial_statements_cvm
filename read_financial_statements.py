"""
Functions for reading the financial statements and cleaning them.

@author: caiomts
@email: caiomts@gmail.com
"""


def import_f_statements(f_statements, path='', type='short'):
    """
    Read all financial statements of the same type.

    Parameters
    ----------
    f_statements: str.
        bpa, bpb, dfc_md, dfc_mi, dmpl, dre, dva or itr*[fin_st]
    path: str. default Working Directory
        folder where the files are
    type: str. short default usecols=['CNPJ_CIA', 'DT_REFER', 'DENOM_CIA',
             'CD_CVM', 'ORDEM_EXERC', 'CD_CONTA',
             'DS_CONTA',
             'VL_CONTA'],
        short, long
    Returns
    -------
    Data.Frame with information for the entire period
    """
    import pandas as pd
    import os
    import fnmatch as fn

    pattern = f_statements + '*.csv'
    files = fn.filter(os.listdir(path), pattern)
    if type == 'short':
        df = (pd.read_csv(path + f, sep=';',
                          encoding='latin-1',
                          usecols=['CNPJ_CIA', 'DT_REFER', 'DENOM_CIA',
                                   'CD_CVM', 'ORDEM_EXERC', 'CD_CONTA',
                                   'DS_CONTA',
                                   'VL_CONTA'],
                          parse_dates=['DT_REFER'],
                          infer_datetime_format=True) for f in files)
    if type == 'long':
        df = (pd.read_csv(path + f, sep=';',
                          encoding='latin-1',
                          parse_dates=['DT_REFER'],
                          infer_datetime_format=True) for f in files)
    return pd.concat(df).reindex()


def f_statements_pivot_date(cd_cvm, f_statements, path=''):
    """
    Apply import_f_statements function and pivot the Data.frame by date.

    Parameters
    ----------
    cd_cvm: int,
        firm cvm code
    f_statements: str.
        bpa, bpb, dfc_md, dfc_mi, dmpl, dre, dva or itr*[fin_st]
    path: str. default Working Directory
        folder where the files are

    Returns
    -------
    Pivoted Data.Frame with information for the entire period
    """
    import pandas as pd
    df = import_f_statements(f_statements, path)
    df = df[(df.CD_CVM == cd_cvm)
            & (df.ORDEM_EXERC == 'ÚLTIMO')].reset_index(drop=True)
    df = df[['CD_CONTA', 'DS_CONTA', 'DT_REFER', 'VL_CONTA']]
    # last statement format
    list_index = df.loc[df.DT_REFER == max(df.DT_REFER),
                        ['CD_CONTA', 'DS_CONTA']]
    df = df[df.CD_CONTA.isin(list_index['CD_CONTA'])]
    df_pivoted = df.pivot_table(index=['CD_CONTA'],
                                columns='DT_REFER', values='VL_CONTA')
    return pd.merge(list_index, df_pivoted,
                    on='CD_CONTA',
                    right_index=True).set_index('CD_CONTA').drop_duplicates()


def tidy_f_statement_data(file, path=''):
    """Return a tidy pandas.DataFrame with dates by companies as observation"""
    df = import_f_statements(file, path, type='short')
    df = df[(df.ORDEM_EXERC == 'ÚLTIMO')]
    # getting last layout as a model
    item_index = df.loc[df.DT_REFER == max(df.DT_REFER),
                        ['CD_CONTA', 'DS_CONTA']].set_index('CD_CONTA')
    df = df[df.CD_CONTA.isin(item_index.index)]
    df_pivoted = df.pivot_table(index=['DT_REFER', 'DENOM_CIA', 'CD_CVM'],
                                columns='CD_CONTA',
                                values='VL_CONTA').reset_index()
    return df_pivoted.set_index('DT_REFER', inplace=True), item_index


def read_files(path):
    """Create a list of files, read them and return a concatenated dataframe."""    
    import pandas as pd
    import os

    files = os.listdir(path)
    df = (pd.read_csv(path + f, sep=';',
                      encoding='latin-1',
                      usecols=['DT_REFER', 'DENOM_CIA', 'ORDEM_EXERC',
                               'CD_CVM', 'CD_CONTA', 
                               'DS_CONTA',
                               'VL_CONTA'], parse_dates=['DT_REFER'],
                      infer_datetime_format=True) for f in files)
    df = pd.concat(df).reindex()
    return df[df.ORDEM_EXERC == 'ÚLTIMO']


def pivot_df(df, length=4):
    """Get the dataframe pivoted."""
    df = df[(df.CD_CONTA.str.len() <= length)]
    # Getting last layout as a model
    cod_conta = df.loc[df.DT_REFER == max(df.DT_REFER),
                      ['CD_CONTA']]
    df = df[df.CD_CONTA.isin(cod_conta.CD_CONTA)]
    df_pivoted = df.pivot_table(index=['DT_REFER', 'CD_CVM'], 
                                columns=['CD_CONTA'], values=['VL_CONTA'])
    df_pivoted.columns = df_pivoted.columns.droplevel()
    return df_pivoted.dropna(axis=1, how='all')