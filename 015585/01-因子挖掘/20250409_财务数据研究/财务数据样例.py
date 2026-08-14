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
ipo_data = IO.read_data([19000101, 20990101], alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5').reset_index()



df1 = IO.read_data([20100101,20250331],alt=path_dic['AShareBalanceSheet'])
df1_tmp = pd.merge(df1, ipo_data[['S_INFO_LISTDATE']], left_on='Ticker', right_on='Ticker')
df2 = IO.read_data([20100101,20250331],alt=path_dic['AShareCashFlow'])
df3 = IO.read_data([20100101,20250331],alt=path_dic['AShareIncome'])

start_date = '20230101'
end_date = '20250408'
lag = 300
start_date = str(s.tradingday(str(start_date), -lag)[0])
'''
以ANN_DT为INDEX，也需要SHIFT(1)，与其他数据类似
'''
fin_df = df1[(df1['ANN_DT'] <= int(end_date)) & (df1['ANN_DT'] >= int(start_date))] # 根据ANN_DT来控制未来信息
fin_df = fin_df[fin_df['STATEMENT_TYPE'] == 408001000] # 只取合并报表,此处的fin_df即为database提供给研究员的值
# 注意，这里和MD_DATA类似，不提供ANN_DT为最后一天的数据，框架统一去掉
'''
# 验证唯一性
fin_df['is_value'] = 1
print(fin_df.groupby(['dt','Ticker'])['is_value'].count().max()) # 为1，代表具有唯一性
'''
# 过去4期应收账款的和
factor_name = 'qyh_fin_test1'
fin_df[factor_name] = fin_df['ACCT_RCV'].unstack().rolling(4,1).sum().stack()
res = fin_df[['ANN_DT',factor_name]] # 即为返回结果，下面的步骤在框架中进行
# 将季频结果拉伸到日频，注意index会包含自然日
res = res.reset_index().sort_values(['ANN_DT','dt','Ticker'])
res['ANN_DT'] = res['ANN_DT'].apply(lambda x : pd.Timestamp(str(int(x))))
res = res.rename(columns = {'dt':'report_date','ANN_DT':'dt'}).set_index(['dt','Ticker'])
res = res.groupby(['dt','Ticker'])[[factor_name]].nth(-1) # 这一步因为有时候会同一天发两期报告（年报+次年一季报）
date_list = [pd.Timestamp(start_date) + datetime.timedelta(days=i) for i in range((pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1)]
res = res[factor_name].unstack().reindex(date_list).ffill().stack().to_frame(name = factor_name)

# 手动数据验证
## 以300373.SZ为例，其在2025年3月30日下午发布年报
'''
根据同花顺，应收账款为
2024年报：187535.36
2024三季报：174052.17
2024中报：167508.22
2024一季报：141572.77
求和 = 187535.36 + 174052.17 + 167508.22 + 141572.77 = 670668.52
'''
tmp = res.query('Ticker == "300373.SZ"')
print(tmp.tail(10))

'''
df[col_name] = df[col_name].fillna(fillna_value)
df['ANN_DT'] = df['ANN_DT'].apply(lambda x: pd.Timestamp(str(int(x))))
df_all_report = df[col_name].unstack().fillna(method='ffill', limit=1).stack().to_frame(name=col_name)
df_all_report['ANN_DT'] = df['ANN_DT']
df_all_report['report_date'] = df_all_report.index.get_level_values(0)
df_all_report.loc[df_all_report['ANN_DT'].isna(), 'ANN_DT'] = df_all_report.loc[df_all_report['ANN_DT'].isna(),'report_date'].apply(get_last_ann_dt)
'''







