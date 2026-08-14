# coding: utf-8
# Author：fengchi863
# Date ：2022/4/20 14:18

"""
剔除上证50的结果
"""

import pandas as pd
import numpy as np
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from SimiStock.dataApi import getData, tradeDate, indName, stockList
from xquant.factordata import FactorData

fd = FactorData()
sz50_df = fd.get_factor_value('WIND_AIndexMembers',
                              S_INFO_WINDCODE='000016.SH')
sz50_list = list(map(lambda x: stockList.trans_windcode2int(x), sz50_df.query('CUR_SIGN == 1')['S_CON_WINDCODE'].tolist()))

hs300_df = fd.get_factor_value('WIND_AIndexMembers',
                              S_INFO_WINDCODE='000300.SH')
hs300_list = list(map(lambda x: stockList.trans_windcode2int(x), hs300_df.query('CUR_SIGN == 1')['S_CON_WINDCODE'].tolist()))


def trans_str(tmp):
    if type(tmp) is str and not (str(tmp).endswith('SZ') or str(tmp).endswith('SH')):
        tmp = int(tmp)
    elif type(tmp) is str:
        tmp = stockList.trans_windcode2int(tmp)
    return tmp


block_data = pd.read_excel('../real_trans/大宗交易列表.xlsx', sheet_name='Sheet2', index_col=0)
block_data.index = block_data.index.map(lambda x: trans_str(x))

start_date = 20220315
end_date = 20220415
block_data = pd.read_pickle(data_path + 'block_data_95.pkl')
block_data = block_data.query(f'{start_date} < 交易日期 < {end_date}')

block_data2 = block_data.drop_duplicates(['股票代码'])
stk_list = block_data2['股票代码'].tolist()
stk_list_noSZ50 = list(set(stk_list).difference(set(sz50_list)))
stk_list_noSZ50HS300 = list(set(stk_list_noSZ50).difference(set(hs300_list)))

chuangxin_stk_list = list(set(block_data.index.tolist()))
len(list(set(stk_list).intersection(set(chuangxin_stk_list))))
len(list(set(stk_list_noSZ50).intersection(set(chuangxin_stk_list))))
len(list(set(stk_list_noSZ50HS300).intersection(set(chuangxin_stk_list))))

#%% 读取70%样本
filename1 = '新版本_14_(0.6, 1)_(0.7, 1)_(120, 120)_95_20220115_20220415_result.pkl'
check = pd.read_pickle(hedge_path + filename1)
stk_list = list()
for idx in range(len(check)):
    stk_id = check[idx]['stk_id']
    stk_list.append(stk_id)
stk_list = list(set(stk_list))