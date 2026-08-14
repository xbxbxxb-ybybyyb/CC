# coding: utf-8
# Author：fengchi863
# Date ：2023/1/18 19:11

"""
分析双姐给的股票列表是否属于黑名单
"""
import pandas as pd
import numpy as np
from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_windcode2int as W2Int
from tqdm import tqdm

shared_path = '/data/user/015614/shared/wys_shared/'
file_name = '20230118是否为异常波动.xlsx'
black_path = '/data/group/800463/stock_list/abnormal_notice_list/'
path_group = '/data/group/800463/stock_list/'

sj_file = pd.read_excel(shared_path + file_name)
sj_file['dt'] = sj_file['dt'].apply(lambda x: int(x.strftime('%Y%m%d')))
manual_black = pd.read_excel(path_group + 'black_other_list/手动调整黑名单.xlsx')
manual_black['出池时间'] = manual_black['出池时间'].apply(lambda x: int(x.strftime('%Y%m%d')) if type(x) != pd._libs.tslibs.nattype.NaTType else np.nan)
manual_black['入池时间'] = manual_black['入池时间'].apply(lambda x: int(x.strftime('%Y%m%d')) if type(x) != pd._libs.tslibs.nattype.NaTType else np.nan)
manual_black['出池时间'] = manual_black['出池时间'].fillna(20990101)

sj_file['是否是异常波动'] = ''
sj_file['是否在手动黑名单'] = ''
for idx in tqdm(range(len(sj_file))):
    index = sj_file.iloc[idx].name
    dat = sj_file.iloc[idx]['dt']
    stk_code = sj_file.iloc[idx]['Ticker']

    cur_black = pd.read_excel(black_path + f'abnormal_notice_list_{dat}.xlsx')
    if W2Int(stk_code) in cur_black['证券代码'].tolist():
        sj_file.loc[index, '是否是异常波动'] = True

    manual_list = manual_black[(manual_black['入池时间'] < dat) & (manual_black['出池时间'] > dat)]
    manual_list['证券代码'] = manual_list['证券代码'].astype(int)
    if W2Int(stk_code) in manual_list['证券代码'].tolist():
        sj_file.loc[index, '是否在手动黑名单'] = True

from dataApi.sendInfo import send_file
send_file(sj_file)




