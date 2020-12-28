# Getting Financial Statements on CVM website
Download Financial Statements from the CVM website and get the data tidy for fundamental analysis.

# Applying Tidy Data from scratch to financial statements
## Introduction
It might be counter-intuitive, and financial practitioners can be shocked, but the best way to deal with a large amount of financial statements is pivoting them around the date. The aim here is to put you in touch with the Tidy Data framework. Applying it with Python to the Financial Statements of publicly traded Brazilian companies, I'll show you why this approach saves time and effort and should be used to prepare data for analysis. 
  
The Tidy Data Framework was formulated by [Wickham][1] one of the exponents in the R's world, but his concept is suitable for any type of programming language applied to data analysis. Keep in mind that when we talk about Tidy Data we need rectangular shaped datasets or relational datasets, each rectangular as well. As far as I know, this is how most of the data are available in the wild.  

Tidy datasets aren't the best way to store data, present data, nor efficient for computing operations. So, why should I bother with it? 

Cleaning and preparing data for analysis takes time. Indeed it's sometimes a daunting task, so a standard way of doing part of it is definitely welcome.  In addition, most of the tools to explore, visualize and modelling are input-tidy, basically because tidy datasets are similars, whether we're looking for economics or chemicals data.

So, what is a tidy dataset? 

### The Basic Struture of Tidy Datasets
- *Column* stores a *variable*
- *Row* represents an *observation*
- *Table* aggregates *one type of observations* and their variables

Datasets are collections of informations or values, each one belongs to an observation and a variable. Variables store informations or values that represent a specific attribute of observations. To find out where the variables are - when you bump into a dataset - they usually have a functional relationship. We can think either about measures of the same experiment or part of a whole, such as revenue and cost of revenue or length and width. Observations store all attributes of the same unit. We are usually interested in comparing observations across some variable or summarizing a group of observations.

## The Data
All data are available on [CVM][2], but it isn't our aim here to show how automate this process (It could be another post...), thus we already have all required data locally. We'll work only with Balance Sheets and Income Statements, because they are by far the most used statements for Fundamental Analysis. 

### Reading data
First we have to set our goals... They might be: calculate financial ratios, compare these ratios between companies throughout years, forecast next periods...  With our goals in mind, we can now find out how our tidy dataset should look.

**Ratios represent a relationship between the items** belonging to the financial statements, so **they are variables** that have functional relationship with other variables. 

**We can compare variables grouped whether by companies on a specific date, or a company over time**. Thus, we can define an observation as a value for each financial statement item of a certain company in a specific moment.

**The unit of observation could be the items by company over time or items by companies on a specific date.**  

Below I sketched which structure we'd like to get.  

Period|Company|Item 1|Item 2|...
-|-|-|-|-
t0|companie A|value x1|value y1|...
t0|companie B|value x2|value y2|...
...|...|...|...|...|
tn|companie Z|value xn|value yn|...

But we can go further. The ROIC (Return on Invested Capital), for instance, is one of the most important ratios to assess the company's efficiency in terms of capital allocation, but to calculate it requires items from two different financial statements. Although the difference in the origin, these items belong to the same unit of observation, I mean, each company has a value for each item in each period, regardless of whether the item comes from  the balance sheet or the income statement.

To clarify the ideas, have a look at our CVM data.

### One type of observation in multiples tables
The first problem we are facing with these data is: they are spread over 60 files divided by type of financial statement and period. However the datasets are structurally similar, in fact, they have the same columns that we're interest in. So let's read the files. 

    path = 'raw_data//'
    def read_files(path):
        """Create a list of files, read them and return a concatenated dataframe."""    
        import pandas as pd
        import os

        files = os.listdir(path)
        df = (pd.read_csv(path + f, sep=';',
                          encoding='latin-1',
                          usecols=['DT_REFER', 'DENOM_CIA', 'ORDEM_EXERC',
                                   'CD_CVM', 'CD_CONTA', 'DS_CONTA',
                                   'VL_CONTA'], parse_dates=['DT_REFER'],
                        infer_datetime_format=True) for f in files)
        df = pd.concat(df).reindex()
        return df[df.ORDEM_EXERC == 'ÚLTIMO']

This function reads a list of files from a path and creates a list of dataframes by applying a list comprehension method. Like a loop, this method takes each file, read it with read_csv function and appends it to a list. As we've selected a group of columns, we get similar datasets and we can concatenate them into a single dataframe that contains all the data from our 60 files. Before returning the output we filter only the lastest version of each statement per year.

Inspecting it:

    df = read_files(path)
    df.info()
Output:  

    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 1727833 entries, 1 to 25653
    Data columns (total 7 columns):
    #   Column       Dtype         
    ---  ------       -----         
    0   DT_REFER     datetime64[ns]
    1   DENOM_CIA    object        
    2   CD_CVM       int64         
    3   ORDEM_EXERC  object        
    4   CD_CONTA     object        
    5   DS_CONTA     object        
    6   VL_CONTA     float64       
    dtypes: datetime64[ns](1), float64(1), int64(1), object(4)
    memory usage: 105.5+ MB

### Variables are stored in rows
After inspected our dataframe we noticed some variables are stored in rows. **DT_REFER** stores dates, **DENOM_CIA** and **CD_CVM** store companies names and codes, **ORDEM_EXERC** stores statements version number, **CD_CONTA** and **DS_CONTA** store variables, they are the codes and the names the items belonging to the statements and **VL_CONTA** stores their values. Therefore, our aim here is to unstack this variables into columns with their values.

    def pivot_df(df, length=4):
        """Get the dataframe pivoted."""
        df = df[(df.CD_CONTA.str.len() <= length)]
        # Getting last layout as a model
        cod_conta = df.loc[df.DT_REFER == max(df.DT_REFER),
                        ['CD_CONTA']]
        df = df[df.CD_CONTA.isin(cod_conta.CD_CONTA)]
        df_pivoted = df.pivot_table(index=['DT_REFER', 'CD_CVM'], columns=['CD_CONTA'],
                                    values=['VL_CONTA'])
        df_pivoted.columns = df_pivoted.columns.droplevel()
        return df_pivoted.dropna(axis=1, how='all')

This function has two inputs, dataframe and length. Length is an item aggregation parameter (I'll explain later). It sets the last layout as a model and than pivot the dataframe with date, company code and items as variables.

Inspecting  it: 

    df_pivoted = pivot_df(df, length=4)
    df_pivoted.info()

Output:  

    <class 'pandas.core.frame.DataFrame'>
    MultiIndex: 6379 entries, (Timestamp('2010-12-31 00:00:00'), 94) to (Timestamp('2019-12-31 00:00:00'), 80179)
    Data columns (total 30 columns):
    #   Column  Non-Null Count  Dtype  
    ---  ------  --------------  -----  
    0   1       6379 non-null   float64
    1   1.01    6379 non-null   float64
    2   1.02    6379 non-null   float64
    3   1.03    414 non-null    float64
    4   1.04    194 non-null    float64
    5   1.05    194 non-null    float64
    6   1.06    194 non-null    float64
    7   1.07    194 non-null    float64
    8   2       6379 non-null   float64
    9   2.01    6379 non-null   float64
    10  2.02    6379 non-null   float64
    11  2.03    6379 non-null   float64
    12  2.04    194 non-null    float64
    13  2.05    414 non-null    float64
    14  2.06    194 non-null    float64
    15  2.07    194 non-null    float64
    16  2.08    194 non-null    float64
    17  3.01    6372 non-null   float64
    18  3.02    6372 non-null   float64
    19  3.03    6372 non-null   float64
    20  3.04    6372 non-null   float64
    21  3.05    6372 non-null   float64
    22  3.06    6372 non-null   float64
    23  3.07    6372 non-null   float64
    24  3.08    6372 non-null   float64
    25  3.09    6372 non-null   float64
    26  3.10    6356 non-null   float64
    27  3.11    6356 non-null   float64
    28  3.12    23 non-null     float64
    29  3.13    420 non-null    float64
    dtypes: float64(30)
    memory usage: 1.5 MB

You may have noticed the meaning of the item aggregation parameter. It is just items and sub-items of financial statements. In this example The Column 1 are the "Assets" and The Column 1.01 are "Current Assets".

    def cod_items(df, length=4):
        df = df[(df.CD_CONTA.str.len() <= length)]
        return df[['CD_CONTA',
                'DS_CONTA']].set_index('CD_CONTA')['DS_CONTA'].sort_index().to_dict()

This function filters dataframe by the length of the items code and returns a dictionary with the name and code of these items. And we can do almost the same with companies names.

    def cod_names():
    return df[['CD_CVM',
               'DENOM_CIA']].set_index('CD_CVM')['DENOM_CIA'].sort_index().to_dict()

    cod_items(df, length=4)

Output:

    {'1': 'Ativo Total',
    '1.01': 'Ativo Circulante',
    '1.02': 'Ativo Não Circulante',
    '1.03': 'Ativo Permanente',
    '1.04': 'Tributos Diferidos',
    '1.05': 'Outros Ativos',
    '1.06': 'Investimentos',
    '1.07': 'Imobilizado',
    '1.08': 'Intangível',
    '2': 'Passivo Total',
    '2.01': 'Passivo Circulante',
    '2.02': 'Passivo Não Circulante',
    '2.03': 'Patrimônio Líquido Consolidado',
    '2.04': 'Provisões',
    '2.05': 'Passivos Fiscais',
    '2.06': 'Outros Passivos',
    '2.07': 'Passivos sobre Ativos Não Correntes a Venda e Descontinuados',
    '2.08': 'Patrimônio Líquido Consolidado',
    '3.01': 'Receita de Venda de Bens e/ou Serviços',
    '3.02': 'Custo dos Bens e/ou Serviços Vendidos',
    '3.03': 'Resultado Bruto',
    '3.04': 'Despesas/Receitas Operacionais',
    '3.05': 'Resultado Antes do Resultado Financeiro e dos Tributos',
    '3.06': 'Resultado Financeiro',
    '3.07': 'Resultado Antes dos Tributos sobre o Lucro',
    '3.08': 'Provisão para IR e Contribuição Social',
    '3.09': 'Resultado Líquido das Operações Continuadas',
    '3.10': 'Resultado Líquido de Operações Descontinuadas',
    '3.11': 'Reversão dos Juros sobre Capital Próprio',
    '3.12': 'Resultado Líquido de Operações Descontinuadas',
    '3.13': 'Lucro/Prejuízo do Período'}


### Multiple types in one table
After pivoting our dataframe a new parameters appeared: a MultiIndex. Unlike the standard Tidy Data framework - that supports one table to each unit of observation and relational datasets are required to deal with more than one unit of observation, the MultiIndex is the tidy way For Pandas to handle multiples types in one dataframe.

I would like to explore this concept further, but in brief, this principle is named data normalization and it's useful for tidying and eliminating inconsistencies. However, there are few tools for working with relational datasets and analyzes are usually done with denormalized datasets.

By the end of the day we have a dataframe like this one:

    print(df_pivoted.sample(20).iloc[:,0:5])
Output:

    CD_CONTA                     1        1.01         1.02
    DT_REFER   CD_CVM                                      
    2011-12-31 5983        25784.0      3107.5      22676.5
    2016-12-31 14613       17600.0        37.0      17563.0
    2012-12-31 22390         101.0       101.0          0.0
    2013-12-31 20524     3851074.5   1744848.0    2106226.5
    2010-12-31 2909       522417.0    286444.5     235972.5
    2016-12-31 21520      822446.5     91631.0     730815.5
    2012-12-31 22934       57217.0     57217.0          0.0
    2010-12-31 20974     1257475.5    422941.0     834534.5
            5410      5523579.0   2773280.5    2750298.5
    2011-12-31 5410      6461108.0   3225753.0    3235355.0
    2013-12-31 6343      4338218.5   1691015.0    2647203.5
    2015-12-31 22217      463843.5     55821.5     408022.0
            2437    122404301.5  21898276.5  100506025.0
    2010-12-31 21059         273.0       273.0          0.0
            8451      2583033.0   1651135.5     931897.5
    2014-12-31 14605     4402872.0   1368666.0    3034206.0
    2013-12-31 20451     1854207.5   1043785.5     810422.0
    2017-12-31 23531    36287877.5   4055277.0   32232600.5
    2015-12-31 8451      4402756.0   2490593.5    1912162.5
    2018-12-31 21997     2863113.0     40363.0    2822750.0

Each row represents the financial statements of a company on a specific date. We can subset rows to compare companies or apply functions like groupby. On the other hand we could also create new columns to calculate ratios for all companies as easily as that:

    df_pivoted['Current_Ratio'] = df_pivoted['1.01']/df_pivoted['2.01']
    df_pivoted['Current_Ratio']

Output:  

    DT_REFER    CD_CVM
    2010-12-31  94        2.366105
                140       1.679680
                701       5.773780
                906       1.261044
                922       0.762841
                            ...   
    2019-12-31  24880     1.054207
                80020     8.745793
                80047     1.491686
                80152          NaN
                80179     1.355918
    Length: 6379, dtype: float64

I hope you enjoyed it and find out how to apply this framework in your own analysis as well.

[1]: https://www.jstatsoft.org/article/view/v059i10
[2]: http://dados.cvm.gov.br/dados/CIA_ABERTA/
