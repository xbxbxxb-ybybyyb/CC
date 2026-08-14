# coding: utf-8
# Author：fengchi863
# Date ：2020/5/29 15:06

import random

from dataApi.getData import *
from dataApi.stockList import *
from dataApi.usefulTools import *

start_date = 20170103
end_date = 20191231
date_list = get_date_range(start_date, end_date)
stock_pool = clean_stock_list('COMMON').loc[start_date:end_date]
isin = stock_pool.sum(axis=0)
stock_list = isin[isin>0].index.tolist()

close = get_minute_1factor('close', code_list=stock_list, start_datetime=201701030925, end_datetime=201912311500)
close_arr = frame2arr(close)
pct = close_arr / delay(close_arr, 1) - 1
stk_std = np.nanstd(pct, axis=0)

volatility = pd.DataFrame(stk_std, index=stock_pool.index, columns=stock_list)
volatility = volatility.loc[:20181231].replace(0, np.nan)
vol_mean = volatility.mean()

stock_list = list(map(lambda x : str(x).zfill(6)+'.SZ' if x<400000 else str(x)+'.SH',stock_list))

price = get_daily_1factor('close', date_list, stock_list)
mkt_cap = get_daily_1factor('a_mkt_cap', date_list, stock_list)
turnover = get_daily_1factor('turn', date_list, stock_list)
price_mean = price.mean()
mkt_cap_mean = mkt_cap.mean()
turnover_mean = turnover.mean()

sample = pd.DataFrame({'price': price_mean, 'mkt_cap': mkt_cap_mean, 'turnover': turnover_mean, 'std_mean': vol_mean})
sample = sample.rank(axis=0, pct=True)
sample_label = (sample > 0.2) * 1 + (sample > 0.4) * 1 + (sample > 0.6) * 1 + (sample > 0.8) * 1

selected = []
for col in sample_label.columns:
    print(col)
    for i in range(5):
        index_list = sample_label[sample_label[col] == i].index.tolist()
        selected = selected + random.sample(index_list, 2)

pd.to_pickle(selected, '/data/group/800319/junkData/IntraFactorModel/best_model_hyper_params/para_optimization_pool.pkl')
