import pandas as pd
import numpy as np
import IO

output_dir = '/data/user/015585/20240116_frame/'
factor_name = 'qyh_finance_new_test1'

df1 = IO.read_data([20100331,20201231],alt='/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareBalanceSheet/AShareBalanceSheet.h5')
columns = ['ANN_DT', 'STATEMENT_TYPE', 'FIX_ASSETS', 'TOT_CUR_ASSETS',]
df1 = df1[df1['STATEMENT_TYPE'] == 408001000][columns]
df1 = df1.reset_index()
df1 = df1[~df1['Ticker'].str.startswith('A')].set_index(['dt', 'Ticker'])
df1_filter = df1.query('Ticker == "300444.SZ"')
df1_filter['factor'] = (df1_filter['FIX_ASSETS'] + df1_filter['TOT_CUR_ASSETS']).rolling(4,1).sum()

basic_file = pd.read_hdf('/data/group/800463/data/projectZZ_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5')
precheck = pd.read_pickle(f'{output_dir}precheck/neptune/result/{factor_name}.pkl')
print(precheck)
print(precheck['因子值一致性检查'])
# 核查因子值
df_value = pd.read_hdf(f'{output_dir}factor_value/neptune/{factor_name}.h5')
df_value_new = pd.read_hdf(f'{output_dir}factor_value/neptune/qyh_finance_new_test3.h5')
tmp = df_value[factor_name] - df_value_new['qyh_finance_new_test3']
print(tmp[abs(tmp) > 1e-5])
#
df_value_long = pd.read_pickle(f'{output_dir}precheck/neptune/same_test/931_{factor_name}_20160101_20191231.pkl')
date = '20180601'
df_20191231 = pd.read_pickle(f'{output_dir}precheck/neptune/same_test/931_{factor_name}_{date}_{date}.pkl')

tmp1 = df_value_long[factor_name].loc[pd.Timestamp(date)]
tmp2 = df_20191231[factor_name].loc[pd.Timestamp(date)]
delta = tmp1 - tmp2
print(abs(delta)[abs(delta) > 1e-8])
# 000418.SZ


'''
factor_name = 'qyh_neptune_caiwu_test1'
def f_calc_sum(factor_series):
    return factor_series[~np.isnan(factor_series)].sum()
df_balancesheet = df1.copy()
df_balancesheet[factor_name] = (df_balancesheet['FIX_ASSETS'] + df_balancesheet['TOT_CUR_ASSETS']).unstack().rolling(4,1).apply(f_calc_sum).stack()
res = df_balancesheet[['ANN_DT', factor_name]]  # 必须返回ANN_DT和因子值两列

df = res.copy()
col_name = factor_name
fillna_value=0
df[col_name] = df[col_name].fillna(fillna_value) # 步骤1
# .query('Ticker == "000047.SZ"')
df['ANN_DT'] = df['ANN_DT'].apply(lambda x: pd.Timestamp(str(int(x))))
df_all_report = df[col_name].unstack().fillna(fillna_value).stack().to_frame(name=col_name) # 步骤1
df_all_report['ANN_DT'] = df['ANN_DT']
df_all_report['report_date'] = df_all_report.index.get_level_values(0)
df_all_report.loc[df_all_report['ANN_DT'].isna(), 'ANN_DT'] = df_all_report.loc[
    df_all_report['ANN_DT'].isna(), 'report_date'].apply(get_last_ann_dt) # 步骤2
df_all_report = df_all_report.drop(['report_date'], axis=1)


'''
# 8.309796e+10

'''
备份
    df[col_name] = df[col_name].fillna(fillna_value) # 步骤1
    df['ANN_DT'] = df['ANN_DT'].apply(lambda x: pd.Timestamp(str(int(x))))
    df_all_report = df[col_name].unstack().fillna(method='ffill', limit=1).fillna(fillna_value).stack().to_frame(name=col_name) # 步骤2
    df_all_report['ANN_DT'] = df['ANN_DT']
    df_all_report['report_date'] = df_all_report.index.get_level_values(0)
    df_all_report.loc[df_all_report['ANN_DT'].isna(), 'ANN_DT'] = df_all_report.loc[
        df_all_report['ANN_DT'].isna(), 'report_date'].apply(get_last_ann_dt) # 步骤3
    df_all_report = df_all_report.drop(['report_date'], axis=1)

    df_all_report = df_all_report.reset_index().sort_values(['ANN_DT', 'dt', 'Ticker'])
    df_all_report = df_all_report.rename(columns={'dt': 'report_date', 'ANN_DT': 'dt'}).set_index(['dt', 'Ticker'])
    date_list = [pd.Timestamp(start_date) + datetime.timedelta(days=i) for i in
                 range((pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1)]
    df_all_report = df_all_report.groupby(['dt', 'Ticker']).nth(-1)  # 这一步因为有时候会同一天发两期报告（年报+次年一季报）
    df_all_report = df_all_report[col_name].unstack().reindex(date_list).ffill().stack().to_frame(name=col_name)
'''

# test4 = test3 / 自行计算的AMT
md_data = IO.read_data([20150101,20191231],
                       alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
                       columns=['amt'])
md_data['factor'] = md_data['amt'].unstack().rolling(5,1).max().shift(1).stack().fillna(0)

df_value = pd.read_hdf(f'{output_dir}factor_value/neptune/qyh_finance_new_test4.h5')
df_value_new = pd.read_hdf(f'{output_dir}factor_value/neptune/qyh_finance_new_test3.h5')
df_value_new['md'] = md_data['factor']
df_value_new['qyh_finance_new_test4'] = (df_value_new['qyh_finance_new_test3'] / df_value_new['md'].replace(0,np.nan)).fillna(0)
tmp = abs(df_value_new['qyh_finance_new_test4'] - df_value['qyh_finance_new_test4'])
tmp[tmp>1e-8]


