import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
import IO

path_dic = {
    'AShareBalanceSheet': '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareBalanceSheet/AShareBalanceSheet.h5',
    'AShareCashFlow': "/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareCashFlow/AShareCashFlow.h5",
    'AShareIncome': '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareIncome/AShareIncome.h5',
}
ipo_data = IO.read_data([19000101, 20990101], alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5').reset_index()
ipo_data = ipo_data[~ipo_data['S_INFO_LISTDATE'].isna()]
ipo_data['S_INFO_LISTDATE'] = ipo_data['S_INFO_LISTDATE'].apply(lambda x : pd.Timestamp(str(int(x))))
ipo_data['S_INFO_DELISTDATE'] = ipo_data['S_INFO_DELISTDATE'].fillna('20991231').apply(lambda x : pd.Timestamp(str(int(x))))

df = IO.read_data([20100101,20250331],alt=path_dic['AShareBalanceSheet'])
df = df[df['STATEMENT_TYPE'] == 408001000]
df = df.reset_index()
df = df[~df['Ticker'].str.startswith('A')]

df = pd.merge(df, ipo_data[['S_INFO_LISTDATE','S_INFO_DELISTDATE','Ticker']], left_on='Ticker', right_on='Ticker', how='left') # 添加上市日期
df = df[~df['S_INFO_LISTDATE'].isna()]

df = df[(df['ANN_DT'].apply(lambda x : pd.Timestamp(str(int(x)))) >= df['S_INFO_LISTDATE'])]
df = df[(df['ANN_DT'].apply(lambda x : pd.Timestamp(str(int(x)))) <= df['S_INFO_DELISTDATE'])]
df = df.set_index(['dt', 'Ticker'])
# 检查是否有靠后报告期的报告先发布的
df['ANN_DT_BEFORE'] = df['ANN_DT'].unstack().shift(1).stack()
tmp = df[df['ANN_DT_BEFORE'] > df['ANN_DT']]['ANN_DT'].to_frame()
print(tmp.head())
df.query('Ticker == "000005.SZ"')[['ANN_DT','ANN_DT_BEFORE']]


