import time

import IO
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
import datetime
s = FactorData()

path_dic = {
    'AShareBalanceSheet': '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareBalanceSheet/AShareBalanceSheet.h5',
    'AShareCashFlow': "/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareCashFlow/AShareCashFlow.h5",
    'AShareIncome': '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareIncome/AShareIncome.h5',
}

df1 = IO.read_data([20100101,20250331],alt=path_dic['AShareBalanceSheet']).reset_index()
df1 = df1[~df1['Ticker'].str.startswith('A')].set_index(['dt', 'Ticker'])
df1 = df1[df1['STATEMENT_TYPE'] == 408001000]

df2 = IO.read_data([20100101,20250331],alt=path_dic['AShareCashFlow']).reset_index()
df2 = df2[~df2['Ticker'].str.startswith('A')].set_index(['dt', 'Ticker'])
df2 = df2[df2['STATEMENT_TYPE'] == 408001000]

df3 = IO.read_data([20100101,20250331],alt=path_dic['AShareIncome']).reset_index()
df3 = df3[~df3['Ticker'].str.startswith('A')].set_index(['dt', 'Ticker'])
df3 = df3[df3['STATEMENT_TYPE'] == 408001000]
basic_file = pd.read_hdf('/data/group/800463/data/projectZZ_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5')

start_date = '20180401'
end_date = '20180403'
lag = 1300
factor_name = 'qyh_neptune_caiwu_test3'

basic_file_filter = basic_file.loc[pd.Timestamp(start_date):pd.Timestamp(end_date)]
df1_filter = df1[['ANN_DT', 'STATEMENT_TYPE', 'FIX_ASSETS', 'TOT_CUR_ASSETS',]]
df3_filter =df3[['ANN_DT', 'STATEMENT_TYPE', 'OPER_REV',]]

time1 = time.localtime()
def f_calc_sum(factor_series):
    return factor_series[~np.isnan(factor_series)].sum()
df_factor = pd.DataFrame(index = basic_file_filter.index, columns = [factor_name])

index = basic_file_filter.index[1]
row = basic_file_filter.loc[index]
for index, row in basic_file_filter.iterrows():
    print(index)
    dt = index[0]
    Ticker = index[1]
    dt_lag_list = s.tradingday(dt.strftime('%Y%m%d'), -lag)
    dt_lag = str(dt_lag_list[0])
    dt_before = (dt-pd.Timedelta(days=1)).strftime('%Y%m%d')

    df_balancesheet_per = df1_filter.query(f'ANN_DT <= {dt_before} & ANN_DT >= {dt_lag}').query(f'Ticker == "{Ticker}"')
    df_income_per = df3_filter.query(f'ANN_DT <= {dt_before} & ANN_DT >= {dt_lag}').query(f'Ticker == "{Ticker}"')
    if len(df_balancesheet_per) != len(df_balancesheet_per):
        print('两张财务表长度不等',dt.strftime('%Y%m%d'),Ticker)
    df = pd.merge(df_balancesheet_per, df_income_per[['OPER_REV']], left_index=True, right_index=True)
    df[factor_name] = ((df['FIX_ASSETS'] + df['TOT_CUR_ASSETS']) / df['OPER_REV']).unstack().rolling(12, 1).apply(
        f_calc_sum).stack()
    res = df[factor_name].values[-1] if len(df) > 0 else 0
    # df_factor.loc[index,factor_name] = res
df_factor = df_factor.fillna(0)
time2 = time.localtime()
print(time2)
print(time1)
#
output_dir = '/data/user/015585/20240116_frame/'
df_factor_frame = pd.read_hdf(f'{output_dir}factor_value/neptune/{factor_name}.h5').loc[basic_file_filter.index]
delta = df_factor[factor_name] - df_factor_frame[factor_name]
delta[abs(delta) > 1e-8]

index = delta[abs(delta) > 1e-8].index[0]





