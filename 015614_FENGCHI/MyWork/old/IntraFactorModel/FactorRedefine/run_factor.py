# @Time : 2020/6/1 16:07
# @Author : Zhichen Lu
# @File : run_factor.py


from dataApi.getData import *
from dataApi.usefulTools import *


def get_stock_data(factor_list, start=20170103, end=20191231):
    factor_dict = {}
    bar_list = None
    for factor in factor_list:
        factor_dict[factor] = get_minute_1factor(factor, start, end)
        factor_dict[factor].index = [x[0] * 10000 + x[1] for x in factor_dict[factor].index]
        if bar_list == None:
            bar_list = factor_dict[factor].index.tolist()
            date_list = list(set([int(x / 10000) for x in factor_dict[factor].index]))
            time_list = [x % 10000 for x in factor_dict[factor].index[:242]]
            code_list = factor_dict[factor].columns.tolist()
        factor_dict[factor] = frame2arr(factor_dict[factor])
    return factor_dict, bar_list, code_list, time_list, date_list


def get_bencmark_data(factor_list, start=20170103, end=20191231):
    factor_dict = {}
    for factor in factor_list:
        factor_dict[factor] = get_minute_1factor(factor, start, end, code_list=['ZZ500'], type='bench')
        factor_dict[factor].index = [x[0] * 10000 + x[1] for x in factor_dict[factor].index]
        factor_dict[factor] = frame2arr(factor_dict[factor])
    return factor_dict


##################################提取数据
start_date = 20170101
end_date = 20170201
print(end_date)
mkt_data, bar_list, code_list, _, _ = get_stock_data(['open', 'close', 'high', 'low', 'vol', 'amt'], start=start_date, end=end_date)
benc_mkt = get_bencmark_data(['open', 'close'], start=start_date, end=end_date)
benchmarkindexclose, benchmarkindexopen = benc_mkt['close'], benc_mkt['open']
open, close, high, low, vol, amt = [mkt_data[x] for x in ['open', 'close', 'high', 'low', 'vol', 'amt']]

vwap = amt / vol
vwap[(vwap == np.inf) | (vwap == -np.inf)] = np.nan
dtm = np.zeros(close.shape)
# 上涨振幅
dtm = dtm + (~(open <= delay(open, 5))) * np.fmax((high - open), (open - delay(open, 5)))
dbm = np.zeros(close.shape)
# 下降振幅
dbm = dbm + (~(open >= delay(open, 5))) * np.fmax((open - low), (open - delay(open, 5)))
alpha = ((close / close[0]).swapaxes(0, 2) - (benchmarkindexclose / benchmarkindexclose[0]).swapaxes(0, 2)[0]).swapaxes(0, 2)
ret = close / close[0] - 1
sequence = np.array([np.ones(close.shape[1:]) * i for i in range(242)])
