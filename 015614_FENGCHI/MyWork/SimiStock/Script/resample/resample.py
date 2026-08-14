# coding: utf-8
# Author：fengchi863
# Date ：2022/4/20 13:08

from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from SimiStock.dataApi import stockList, tradeDate
import os

fd = FactorData()
sz50_df = fd.get_factor_value('WIND_AIndexMembers',
                              S_INFO_WINDCODE='000016.SH')
sz50_df = sz50_df[['S_CON_WINDCODE', 'S_CON_INDATE', 'S_CON_OUTDATE']]

sz50_df = sz50_df.rename({'S_CON_WINDCODE': '股票代码',
                          'S_CON_INDATE': '生效日',
                          'S_CON_OUTDATE': '剔除日'}, axis=1)

sz50_df = sz50_df.drop(2)
sz50_df['股票代码'] = sz50_df['股票代码'].map(stockList.trans_windcode2int)
sz50_df = sz50_df.sort_values(['生效日'])

sz50_df['value'] = 1
sz50_entry = sz50_df.pivot('生效日', '股票代码', 'value')
sz50_remove = sz50_df[['剔除日', '股票代码', 'value']].dropna().pivot('剔除日', '股票代码', 'value')
sz50 = sz50_entry.sub(sz50_remove, fill_value=0).replace(0, np.nan).ffill() > 0.5
sz50.index = sz50.index.map(int)
a = sz50.reindex(tradeDate.get_date_range(20131216)).ffill()

sz50_list = list(map(lambda x: stockList.trans_windcode2int(x), sz50_df.query('CUR_SIGN == 1')['S_CON_WINDCODE'].tolist()))

filename1 = '新版本_14_(0.6, 1)_(0.8, 1)_(120, 120)_95_20220315_20220415_result.pkl'
check = pd.read_pickle(hedge_path + filename1)
ret_list = list()
for idx in range(len(check)):
    stk_id = check[idx]['stk_id']
    trade_date = check[idx]['date']
    if stk_id in sz50_list:
        print(stk_id, 'in')
    else:
        ret_list.append(check[idx])
util.save_list2pkl(ret_list, hedge_path, os.path.splitext(filename1)[0] + '_noSZ50.pkl')
print(1)
