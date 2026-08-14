# @Time : 2020/6/3 14:14
# @Author : Zhichen Lu
# @File : data_pre_loading.py


import os

import gc
from tqdm import tqdm

from dataApi.getData import get_minute_1factor
from dataApi.stockList import clean_stock_list
from dataApi.usefulTools import *

# 1文件路径
store_address = '/data/group/800319/storeFactor/gp_intrafactor_from2017/'
if not os.path.exists(store_address):
    os.mkdir(store_address)
# result_address = '/data/group/800319/batchTest'
# corr_address = '/data/group/800319/storeFactor/corrcoef'

# 2起止日期
start_date = 20170103
end_date = 20191231
stk_pool = clean_stock_list('ALL').loc[start_date: end_date]
isin = stk_pool.sum()
stocks = isin[isin > 0].index.to_list()

# 3导入数据
open = get_minute_1factor('open', start_date, end_date, code_list=stocks)
close = get_minute_1factor('close', start_date, end_date, code_list=stocks)
high = get_minute_1factor('high', start_date, end_date, code_list=stocks)
low = get_minute_1factor('low', start_date, end_date, code_list=stocks)
vol = get_minute_1factor('vol', start_date, end_date, code_list=stocks)
amt = get_minute_1factor('amt', start_date, end_date, code_list=stocks)
benchmarkindexclose = get_minute_1factor('close', start_date, end_date, code_list=['ZZ500'], type='bench')
benchmarkindexopen = get_minute_1factor('open', start_date, end_date, code_list=['ZZ500'], type='bench')

# 4准备运算
index, columns = close.index, close.columns
open = frame2arr(open)
close = frame2arr(close)
high = frame2arr(high)
low = frame2arr(low)
vol = frame2arr(vol)
amt = frame2arr(amt)
benchmarkindexclose = frame2arr(benchmarkindexclose)
benchmarkindexopen = frame2arr(benchmarkindexopen)

vwap = np.where(np.isnan(amt / vol), close, amt / vol)
ret = close / delay(close) - 1
sequence = (np.arange(close.shape[0]).repeat(close.shape[1] * close.shape[2])).reshape(close.shape[0], close.shape[1], close.shape[2])
dtm = ~(open <= delay(open, 5)) * np.fmax((high - open), (open - delay(open, 5)))
dbm = ~(open >= delay(open, 5)) * np.fmax((open - low), (open - delay(open, 5)))

alpha = ((close / close[0]).transpose(2, 0, 1) - (benchmarkindexclose / benchmarkindexopen[0])[:, :, 0]).transpose(1, 2, 0)
alpha1 = np.pad(((close[:, 1:, :] / close[-1, :-1, :]).transpose(2, 0, 1) - benchmarkindexclose[:, 1:, 0] / benchmarkindexclose[-1, :-1, 0]
                 ).transpose(1, 2, 0), ((0, 0), (1, 0), (0, 0)), mode='constant', constant_values=np.nan)
pct = close / close[0] - 1

factor_list = []
for i in [2, 4, 6, 8, 10, 20, 30]:
    factor_list.append('pct_%d = close/delay(close,%d)' % (i, i))
factor_list.append('pct = pct')
for i in [2, 4, 6, 8, 10, 20, 30]:
    factor_list.append('alpha_%d = ((close/delay(close,%d)).transpose(2,0,1)/(benchmarkindexclose/delay(benchmarkindexclose,%d))[:,:,0]).transpose(1,2,0)' % (i, i, i))
factor_list.append('alpha = alpha')
for i in [3, 7, 15, 25]:
    factor_list.append('drawback_i = pct - ts_max(pct,i)'.replace('i', str(i)))
for i in [3, 7, 15, 25]:
    factor_list.append('drawback_alpha_i = alpha - ts_max(alpha,i)'.replace('i', str(i)))
for i in [3, 7, 15, 25]:
    factor_list.append('uprise_alpha_i = alpha - ts_min(alpha,%d)' % i)
for i in [3, 7, 15, 25]:
    factor_list.append('percentile_%d = (alpha - ts_min(alpha,%d))/( ts_max(alpha,%d) - ts_min(alpha,%d))' % (i, i, i, i))
for i in [3, 7, 15, 25]:
    factor_list.append('bias_i = pct-ts_mean(pct,i)'.replace('i', str(i)))
for i in [5, 10, 15, 20]:
    for j in [5, 10, 15, 20]:
        factor_list.append('singul_biasi_min_%d_%d = alpha + ts_min(ts_mean(alpha,%d),%d)' % (i, j, i, j))
for i in [5, 10, 15, 20]:
    for j in [5, 10, 15, 20]:
        factor_list.append('singul_biasi_max_%d_%d = alpha + ts_max(ts_mean(alpha,%d),%d)' % (i, j, i, j))
for i in [3, 5]:
    for j in [10, 20, 30]:
        factor_list.append('amtRatio_%d_%d = ts_mean(amt,%d)/ts_mean(amt,%d)' % (i, j, i, j))

for line in tqdm(factor_list):
    content = line.split(sep='=', maxsplit=1)
    if os.path.exists(store_address + '/' + content[0] + '.h5'):
        print(content[0], 'exist')
        continue
    try:
        factor = eval(content[1])
        arr2frame(factor, index, columns).to_hdf(store_address + '/' + content[0] + '.h5', content[0], format='t')
        del factor
        gc.collect()
    except:
        print(line, content[0])
