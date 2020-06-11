"""
Read records.

@author: caiomts
@email: caiomts@gmail.com
"""


def read_records(path='', type='short'):
    """
    Read records.

    Parameters
    ----------
    path: str.
    type: str.
    DESCRIPTION
            short (default)
            columns = 'CNPJ_CIA', 'DENOM_SOCIAL', 'DENOM_COMERC', 'CD_CVM',
                    'SETOR_ATIV', 'PAIS', 'SIT'.
            long
            cols = all columns
    Returns
    -------
    Data.Frame
    """
    import pandas as pd

    if type == 'short':
        cad_df = pd.read_csv(path, sep=';', encoding='latin-1',
                             usecols=['CNPJ_CIA', 'DENOM_SOCIAL', 
                                      'DENOM_COMERC', 'CD_CVM', 'SETOR_ATIV',
                                      'PAIS', 'SIT', 'CATEG_REG'])
    if type == 'long':
        cad_df = pd.read_csv(path, sep=';', encoding='latin-1')
    # Companies allowed to trade shares
    cad_df = cad_df[(cad_df.SIT == 'ATIVO')
                    & (cad_df.CATEG_REG == 'Categoria A')]
    return cad_df


def records_from_list(list_of_firms, col='DENOM_COMERC', path='',
                      type='short'):
    """
    Read records from a list

    Parameters
    ----------
    list_of_firms: list,
    col: DENOM_COMERC (default)
    path: str.
    type: str.
    DESCRIPTION
            short (default)
            columns = 'CNPJ_CIA', 'DENOM_SOCIAL', 'DENOM_COMERC', 'CD_CVM',
                    'SETOR_ATIV', 'PAIS', 'SIT'.
            long
            cols = all columns
    Returns
    -------
    Data.Frame
    """
    records = read_records(path, type)
    return records[records[col].isin(list_of_firms)]
