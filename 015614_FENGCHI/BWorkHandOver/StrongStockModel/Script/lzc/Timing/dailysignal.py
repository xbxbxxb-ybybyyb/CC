# @Time : 2021/3/18 10:55
# @Author : Zhichen Lu
# @File : dailysignal.py

import pandas as pd
from dataApi.getData import get_daily_1factor
import numpy as np
from xquant.factordata import FactorData
s = FactorData()

alpha = pd.read_pickle('/data/group/800319/信号存储/daily_stock_score_v3_20210127.pkl')

vwap = get_daily_1factor('vwap').loc[alpha.index]
close = get_daily_1factor('close').loc[alpha.index]
close_badj = get_daily_1factor('close_badj').loc[alpha.index]
vwap_adj = vwap*close_badj/close

date_list = alpha.index.tolist()

pct = vwap_adj.pct_change()

label = pd.DataFrame({'prediction':alpha.stack(),'actual':pct.shift(-2).stack()}).dropna()
label['adj_prediction'] = np.nan
for i in range(5,len(date_list)-1):
    temp = label.loc[date_list[i-5:i]]
    mean,std = temp.mean() ,temp.std()
    label.loc[[date_list[i]],'adj_prediction'] = ((label.loc[[date_list[i]],'prediction'] - mean['prediction'])/std['prediction'])*std['actual'] + mean['actual']
    print(date_list[i])

adj_prediction = label.reset_index().pivot_table(index='level_0',columns='level_1',values='adj_prediction')
actual = label.reset_index().pivot_table(index='level_0',columns='level_1',values='actual')



wind_a = s.get_factor_value('WIND_AIndexWindIndustriesEOD',S_INFO_WINDCODE=['881001.WI'])[['TRADE_DT','S_DQ_CLOSE']].set_index('TRADE_DT')
wind_a = wind_a.sort_index()
wind_a.index = wind_a.index.astype(int)
free_float_shares = s.get_factor_value('Basic_factor',factor_names=['free_float_shares'],mddate=alpha.index.astype(str).tolist())
free_float_shares = free_float_shares.reset_index().pivot_table(index='mddate',columns='stock',values='free_float_shares')
free_float_shares.columns = [int(x[:-3]) for x in free_float_shares.columns]
free_float_shares.index =free_float_shares.index.astype(int)

free_float_cap = free_float_shares*close

weight = (free_float_cap.T/free_float_cap.sum(axis=1)).T


judge = (weight*adj_prediction).sum(axis=1)<0



adj_prediction_pct = adj_prediction.shift(2)#.mean(axis=1)

wind_a_future_profit = wind_a[wind_a.columns[0]].pct_change().shift(-2).loc[adj_prediction_pct.index]

predict_down = wind_a_future_profit[judge]
(predict_down<0).sum()/predict_down.shape[0]


pct_change = close_badj.pct_change()
twap_index_profit = (weight.shift(2)*pct).sum(axis=1)
adj_prediction_index_profit = (weight.shift(2)*adj_prediction_pct).sum(axis=1)
index_profit = (weight.shift(1)*pct_change).sum(axis=1)

compare = pd.DataFrame({'actual':wind_a[wind_a.columns[0]].pct_change(),'calc':index_profit,'twap_index':twap_index_profit,'adj_predict':adj_prediction_index_profit}).loc[index_profit.index]
compare.loc[compare.index[0],:] = 0





compare = pd.DataFrame({'wind_a':wind_a.pct_change()['S_DQ_CLOSE'],'all_mean':close.pct_change().mean(axis=1)})
