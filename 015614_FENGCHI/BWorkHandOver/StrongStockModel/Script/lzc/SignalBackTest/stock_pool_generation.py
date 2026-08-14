# @Time : 2021/1/27 9:53
# @Author : Zhichen Lu
# @File : stock_pool_generation.py

import pandas as pd
from dataApi.getData import get_daily_1factor
from dataApi.tradeDate import get_date_range
import numpy as np
from tqdm import tqdm

pred_ret = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl')
date_list = pred_ret.index.tolist()

twap = get_daily_1factor('twap',get_date_range(20160101,20201231),code_list=pred_ret.columns.tolist())
close = get_daily_1factor('close',get_date_range(20160101,20201231),code_list=pred_ret.columns.tolist())
close_badj = get_daily_1factor('close_badj',get_date_range(20160101,20201231),code_list=pred_ret.columns.tolist())
twap_adj = twap*close_badj/close

pct_change = twap_adj.pct_change().shift(-2).loc[date_list]

def get_stat(pct_threshold):
    label = pd.DataFrame({'actual_label':pct_change.stack(),'prediction':pred_ret.stack()})
    label = label.dropna()
    label['threshold'] = np.nan
    label['signal'] = np.nan



    for idx in range(10,len(date_list),10):
        print(idx,date_list[idx-10:idx],date_list[idx:idx+10])
        val_set = label.loc[date_list[idx-10:idx]]
        tantile = (val_set['actual_label']<pct_threshold).sum()/val_set.shape[0]
        percentile = val_set['prediction'].quantile(tantile)
        label.loc[date_list[idx:idx+10],'threshold'] = percentile

    label['signal'] = label['prediction']>label['threshold']

    stock_pool = label.reset_index().pivot_table(index='level_0',columns='level_1',values='signal').fillna(False)
    check_num = stock_pool.sum(axis=1)

    stat = pd.DataFrame({'year':[x//10000 for x in check_num.index],'num':check_num})
    stat = stat.groupby('year').mean()
    return stat

res = {}
for pct_threshold in range(10,15):
    res[pct_threshold] = get_stat(pct_threshold*0.001)

check = pd.Panel(res).loc[:,:,'num']