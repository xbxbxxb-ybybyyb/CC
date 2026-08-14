import pandas as pd
import IO
import numpy as np
from xquant.factordata import FactorData
s = FactorData()

start_date = '20160101'
end_date = '20191231'
basic_file = pd.read_hdf('/data/group/800463/data/projectZZ_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5')
tradingday_list = s.tradingday(start_date, end_date)

path_dic = {
    'AShareBalanceSheet': '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareBalanceSheet/AShareBalanceSheet.h5',
    'AShareCashFlow': "/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareCashFlow/AShareCashFlow.h5",
    'AShareIncome': '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareIncome/AShareIncome.h5',
}
df1 = IO.read_data([20090101,int(end_date)],alt=path_dic['AShareBalanceSheet']).reset_index()
df1 = df1[~df1['Ticker'].str.startswith('A')]
df1 = df1[df1['STATEMENT_TYPE'] == 408001000]

df2 = IO.read_data([20090101,int(end_date)],alt=path_dic['AShareCashFlow']).reset_index()
df2 = df2[~df2['Ticker'].str.startswith('A')]
df2 = df2[df2['STATEMENT_TYPE'] == 408001000]

df3 = IO.read_data([20090101,int(end_date)],alt=path_dic['AShareIncome']).reset_index()
df3 = df3[~df3['Ticker'].str.startswith('A')]
df3 = df3[df3['STATEMENT_TYPE'] == 408001000]

ipo_data = IO.read_data([19000101, 20990101], alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5').reset_index()
ipo_data = ipo_data[~ipo_data['S_INFO_LISTDATE'].isna()]

df1 = pd.merge(df1, ipo_data[['S_INFO_LISTDATE','S_INFO_DELISTDATE','Ticker']], left_on='Ticker', right_on='Ticker', how='left')
df2 = pd.merge(df2, ipo_data[['S_INFO_LISTDATE','S_INFO_DELISTDATE','Ticker']], left_on='Ticker', right_on='Ticker', how='left')
df3 = pd.merge(df3, ipo_data[['S_INFO_LISTDATE','S_INFO_DELISTDATE','Ticker']], left_on='Ticker', right_on='Ticker', how='left')

# 补充修改股票代码的对应关系
dic_change_ticker = {
    '000043.SZ': '001914.SZ',
    '000022.SZ': '001872.SZ',
    '200022.SZ': '201872.SZ',
    '601313.SH': '601360.SH',
    '300114.SZ': '302132.SZ',
}
for old_ticker in dic_change_ticker.keys():
    new_ticker = dic_change_ticker[old_ticker]
    new_ticker_S_INFO_LISTDATE = ipo_data[ipo_data['Ticker'] == new_ticker]['S_INFO_LISTDATE'].values[0] if len(ipo_data[ipo_data['Ticker'] == new_ticker]['S_INFO_LISTDATE'].values) > 0 else np.nan
    print(old_ticker, new_ticker, new_ticker_S_INFO_LISTDATE)
    df1.loc[df1['Ticker'] == old_ticker, 'S_INFO_LISTDATE'] = new_ticker_S_INFO_LISTDATE
    df2.loc[df2['Ticker'] == old_ticker, 'S_INFO_LISTDATE'] = new_ticker_S_INFO_LISTDATE
    df3.loc[df3['Ticker'] == old_ticker, 'S_INFO_LISTDATE'] = new_ticker_S_INFO_LISTDATE

df1 = df1.set_index(['dt','Ticker'])
df2 = df2.set_index(['dt','Ticker'])
df3 = df3.set_index(['dt','Ticker'])

file_dic = {
    'xdb_balancesheet': df1,
    'xdb_cashflow': df2,
    'xdb_income': df3
}

save_path = '/dfs/group/800463/data/xdb_data_lag3_new/'
strategy = 'neptune'
# for tradingday in tradingday_list:
def get_finance_date(tradingday, strategy, type, save_path):
    try:
        print(tradingday, strategy, type)
        basic_file_date = basic_file.loc[pd.Timestamp(tradingday):pd.Timestamp(tradingday)]
        stock_list = list(set(basic_file_date.index.get_level_values(1)))
        df_finance = file_dic[type]
        df_finance_date = df_finance[df_finance['ANN_DT'].apply(lambda x : int(x) if not pd.isna(x) else np.nan) < int(tradingday)].reset_index()
        df_finance_date = df_finance_date[df_finance_date['Ticker'].isin(stock_list)]
        df_finance_date = df_finance_date.rename(columns = {'dt':'MDDate'})
        df_finance_date['MDDate'] = df_finance_date['MDDate'].apply(lambda x : x.strftime('%Y%m%d'))
        df_finance_date['dt'] = pd.Timestamp(tradingday)
        df_finance_date = df_finance_date.set_index(['dt','Ticker'])
        df_finance_date = df_finance_date.sort_values(['dt','Ticker'])
        df_finance_date.to_pickle(f'{save_path}{strategy}/{type}/{tradingday}.pkl')
    except:
        print(tradingday, strategy, type, '未成功保存，请检查！！！！')
    return
from multiprocessing import Pool
pool = Pool(30)
task_list = []

for tradingday in tradingday_list:
    for type in ['xdb_balancesheet', 'xdb_cashflow', 'xdb_income']:
        task_list.append(pool.apply_async(get_finance_date, args=(tradingday, strategy, type, save_path)))
pool.close()
pool.join()

