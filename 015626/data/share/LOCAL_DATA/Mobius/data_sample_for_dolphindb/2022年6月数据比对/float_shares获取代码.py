from xquant.factordata import FactorData
s = FactorData()

ashare_total = s.get_factor_value('WIND_AShareCapitalization', factors = ['S_INFO_WINDCODE','CHANGE_DT', 'FLOAT_A_SHR']).rename(columns = {'S_INFO_WINDCODE':'Ticker'}).set_index('Ticker')
ashare_total['CHANGE_DT'] = ashare_total['CHANGE_DT'].astype('int')
temp_fs = pd.DataFrame([20220601, 50900], index = ashare_total.columns, columns = ['689009.SH']).T
temp_fs['CHANGE_DT'] = temp_fs['CHANGE_DT'].astype('int')
temp_fs2 = pd.DataFrame([20210602, 50900], index = ashare_total.columns, columns = ['689009.SH']).T
temp_fs2['CHANGE_DT'] = temp_fs2['CHANGE_DT'].astype('int')
ashare_total = pd.concat([ashare_total, temp_fs, temp_fs2])
temp_fs = pd.DataFrame([20050505, np.nan], index = ashare_total.columns, columns = ['000022.SZ']).T
temp_fs['CHANGE_DT'] = temp_fs['CHANGE_DT'].astype('int')
temp_fs2 = pd.DataFrame([20060606, np.nan], index = ashare_total.columns, columns = ['000022.SZ']).T
temp_fs2['CHANGE_DT'] = temp_fs2['CHANGE_DT'].astype('int')
ashare_total = pd.concat([ashare_total, temp_fs, temp_fs2])
temp_fs = pd.DataFrame([20050505, np.nan], index = ashare_total.columns, columns = ['000043.SZ']).T
temp_fs['CHANGE_DT'] = temp_fs['CHANGE_DT'].astype('int')
temp_fs2 = pd.DataFrame([20060606, np.nan], index = ashare_total.columns, columns = ['000043.SZ']).T
temp_fs2['CHANGE_DT'] = temp_fs2['CHANGE_DT'].astype('int')
ashare_total = pd.concat([ashare_total, temp_fs, temp_fs2])
del(s)

# 如何获取每只股票每天的float_shares 以供参考
def add_turnover_rate_and_adj(df, stock):
    if 'float_shares' in df.columns:
        df = df.drop(['float_shares'], axis = 1)
    if 'adjfactor' in df.columns:
        df = df.drop(['adjfactor'], axis = 1)
    df = df.reset_index()
    df['CHANGE_DT'] = df.dt.apply(lambda x:int(str(x.date()).replace('-','')))
    ashare = ashare_total.loc[stock].reset_index(drop = True).sort_values(by = 'CHANGE_DT')
    temp = df[['CHANGE_DT']]
    temp2 = pd.merge(temp, ashare, on=['CHANGE_DT'], how = 'outer')
    temp2 = temp2.sort_values(['CHANGE_DT'])
    temp2['FLOAT_A_SHR'] = temp2['FLOAT_A_SHR'].fillna(method = 'ffill')
    temp2 = temp2[temp2.CHANGE_DT >= 20100101]
    temp2 = temp2.drop_duplicates(keep = 'last')

    _adj_df = adj_df.xs(stock, level = 1).reset_index().rename(columns = {'dt':'CHANGE_DT'})
    _adj_df['CHANGE_DT'] = _adj_df.CHANGE_DT.apply(lambda x:int(str(x.date()).replace('-','')))
    totaldf = pd.merge(df, temp2, on=['CHANGE_DT'], how = 'left')
    totaldf = pd.merge(totaldf, _adj_df, on=['CHANGE_DT'], how = 'left')
    

    totaldf = totaldf.drop(['CHANGE_DT'], axis = 1)
    totaldf.rename(columns = {'FLOAT_A_SHR':'float_shares'}, inplace = True)

    if ('volume' not in totaldf.columns) or ('float_shares' not in totaldf.columns):
        totaldf['turnover_rate'] = np.nan
    else:
        totaldf['turnover_rate'] = totaldf.volume / totaldf.float_shares / 100
    totaldf = totaldf.set_index(['dt'])
    totaldf = totaldf.sort_index()

    return totaldf