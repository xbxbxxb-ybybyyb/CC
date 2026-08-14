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
store_address = '/data/group/800319/storeFactor/intrafactor_pre_day_padding/'
if not os.path.exists(store_address):
    os.mkdir(store_address)
# result_address = '/data/group/800319/batchTest'
# corr_address = '/data/group/800319/storeFactor/corrcoef'
factor_list = []
f = open('/data/user/015664/IntradayStrasts/intrafactormodel/FactorRedefine/factor_definition_redefine.txt')
factor_list = [x.strip('\n') for x in f.readlines()]
f.close()
# 2起止日期
start_date = 20170103
end_date = 20191231
stk_pool = clean_stock_list('ALL').loc[start_date: end_date]
isin = stk_pool.sum()
stocks = isin[isin > 0].index.to_list()
print('loading data')
# 3导入数据
open = get_minute_1factor('open', start_date, end_date, code_list=stocks)
print(open.shape)
close = get_minute_1factor('close', start_date, end_date, code_list=stocks)
high = get_minute_1factor('high', start_date, end_date, code_list=stocks)
low = get_minute_1factor('low', start_date, end_date, code_list=stocks)
vol = get_minute_1factor('vol', start_date, end_date, code_list=stocks)
amt = get_minute_1factor('amt', start_date, end_date, code_list=stocks)
benchmarkindexclose = get_minute_1factor('close', start_date, end_date, code_list=['ZZ500'], type='bench')
benchmarkindexopen = get_minute_1factor('open', start_date, end_date, code_list=['ZZ500'], type='bench')
print('preparing data')
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

window = 75
open = np.concatenate((delay(open.swapaxes(0, 1), 1).swapaxes(0, 1)[-window:], open), axis=0)
close = np.concatenate((delay(close.swapaxes(0, 1), 1).swapaxes(0, 1)[-window:], close), axis=0)
high = np.concatenate((delay(high.swapaxes(0, 1), 1).swapaxes(0, 1)[-window:], high), axis=0)
low = np.concatenate((delay(low.swapaxes(0, 1), 1).swapaxes(0, 1)[-window:], low), axis=0)
vol = np.concatenate((delay(vol.swapaxes(0, 1), 1).swapaxes(0, 1)[-window:], vol), axis=0)
amt = np.concatenate((delay(amt.swapaxes(0, 1), 1).swapaxes(0, 1)[-window:], amt), axis=0)
benchmarkindexclose = np.concatenate((delay(benchmarkindexclose.swapaxes(0, 1), 1).swapaxes(0, 1)[-window:], benchmarkindexclose), axis=0)
benchmarkindexopen = np.concatenate((delay(benchmarkindexopen.swapaxes(0, 1), 1).swapaxes(0, 1)[-window:], benchmarkindexopen), axis=0)

vwap = np.where(np.isnan(amt / vol), close, amt / vol)
ret = close / delay(close) - 1
sequence = (np.arange(close.shape[0]).repeat(close.shape[1] * close.shape[2])).reshape(close.shape[0], close.shape[1], close.shape[2])
dtm = ~(open <= delay(open, 5)) * np.fmax((high - open), (open - delay(open, 5)))
dbm = ~(open >= delay(open, 5)) * np.fmax((open - low), (open - delay(open, 5)))

alpha = ((close / close[0]).transpose(2, 0, 1) - (benchmarkindexclose / benchmarkindexopen[0])[:, :, 0]).transpose(1, 2, 0)
alpha1 = np.pad(((close[:, 1:, :] / close[-1, :-1, :]).transpose(2, 0, 1) - benchmarkindexclose[:, 1:, 0] / benchmarkindexclose[-1, :-1, 0]
                 ).transpose(1, 2, 0), ((0, 0), (1, 0), (0, 0)), mode='constant', constant_values=np.nan)
pct = close / close[0] - 1
print('finish data prepare')

for line in tqdm(factor_list):
    content = line.split(sep='=', maxsplit=1)
    content[0] = content[0].strip()
    if os.path.exists(store_address + '/' + content[0] + '.h5'):
        print(content[0], 'exist')
        continue
    if content[0] not in ['factor116', 'alpha55']:
        continue
    # try:
    print(content[0])
    factor = eval(content[1])

    arr2frame(factor[-242:], index, columns).to_hdf(store_address + '/' + content[0].strip() + '.h5', content[0].strip(), format='t')
    del factor
    gc.collect()
    print(content[0], 'done')
    # except:
    #     print(line, content[0])
