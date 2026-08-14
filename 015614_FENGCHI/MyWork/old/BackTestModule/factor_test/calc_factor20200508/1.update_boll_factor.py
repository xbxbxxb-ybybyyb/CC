# coding: utf-8
# Author：fengchi863
# Date ：2020/5/8 13:08

'''
新增了布林带类的一些因子，其中主要是根据boll带类的因子设计了
'''

from dataApi.getData import *
from dataApi.usefulTools import *
from dataApi.stockList import *

factor_output_path = '/data/group/800319/storeFactor/original_intrafactor/'

start_date = 20170103
end_date = 20191231
date_list = get_date_range(start_date, end_date)

stock_pool = clean_stock_list('COMMON')
stock_list = clean_stock_list(no_limit_down=True, no_limit_up=True).shift(1).reindex(date_list)
stock_list = (stock_list > 0.5) & (
            stock_pool.shift(1).reindex_like(stock_list) > 0.5) if stock_pool is not None else stock_list
stock_list = stock_list.reindex(columns=sorted(stock_list.sum()[stock_list.sum() > 0.5].index.tolist()))

# open = get_minute_1factor('open', start_date, end_date, code_list=stock_list.columns.tolist())
# high = get_minute_1factor('high', start_date, end_date, code_list=stock_list.columns.tolist())
# low = get_minute_1factor('low', start_date, end_date, code_list=stock_list.columns.tolist())
close = get_minute_1factor('close', start_date, end_date, code_list=stock_list.columns.tolist())
vol = get_minute_1factor('vol', start_date, end_date, code_list=stock_list.columns.tolist())
amt = get_minute_1factor('amt', start_date, end_date, code_list=stock_list.columns.tolist())
benchmarkindexclose = get_minute_1factor('close', start_date, end_date, code_list=['ZZ500'], type='bench')
benchmarkindexopen = get_minute_1factor('open', start_date, end_date, code_list=['ZZ500'], type='bench')

index, columns = close.index, close.columns
# open = frame2arr(open)
close = frame2arr(close)
# high = frame2arr(high)
# low = frame2arr(low)
vol = frame2arr(vol)
amt = frame2arr(amt)
benchmarkindexclose = frame2arr(benchmarkindexclose)
benchmarkindexopen = frame2arr(benchmarkindexopen)
vwap = np.where(np.isnan(amt / vol), close, amt / vol)
# ret = close / delay(close) - 1
# sequence = (np.arange(close.shape[0]).repeat(close.shape[1] * close.shape[2])).reshape(close.shape[0], close.shape[1], close.shape[2])
# dtm = ~(open <= delay(open, 5)) * np.fmax((high - open), (open - delay(open, 5)))
# dbm = ~(open >= delay(open, 5)) * np.fmax((open - low), (open - delay(open, 5)))

alpha = ((close / close[0]).transpose(2, 0, 1) - (benchmarkindexclose / benchmarkindexclose[0])[:, :, 0]).transpose(1, 2, 0)
# 相对于昨收
# alpha1 = np.pad(((close[:,1:,:] / close[-1,:-1,:]).transpose(2, 0, 1) - benchmarkindexclose[:, 1:, 0] / benchmarkindexclose[-1, :-1, 0]
#                  ).transpose(1, 2, 0), ((0,0),(1,0),(0,0)), mode='constant', constant_values=np.nan)
alphav = ((vwap / vwap[0]).transpose(2, 0, 1) - (benchmarkindexclose / benchmarkindexclose[0])[:, :, 0]).transpose(1, 2, 0)

# boll4_10 = (alpha - ts_mean(alpha, 10)) / ts_std(alpha, 10)
# boll4_10 = arr2frame(boll4_10, index, columns)
# boll4_10.to_hdf(factor_output_path + 'boll4_10.h5', 'boll4_10')
#
# boll4_30 = (alpha - ts_mean(alpha, 30)) / ts_std(alpha, 30)
# boll4_30 = arr2frame(boll4_30, index, columns)
# boll4_30.to_hdf(factor_output_path + 'boll4_30.h5', 'boll4_30')

# 改为运行字符串
append_factor_df = pd.read_excel('日内因子补充20200508.xlsx', sheet_name='因子补充', index_col=0)
factor_names = append_factor_df['因子名称'].tolist()[-2:]
factor_fomulas = append_factor_df['因子逻辑'].tolist()[-2:]
for idx in range(len(factor_names)):
    e = time.clock()
    factor_name = factor_names[idx]
    if factor_name in ['boll4_20', 'boll10_20', 'boll6_20']:
        continue
    factor_fomula = factor_fomulas[idx]
    factor = eval(factor_fomula.split('=')[1])
    factor = arr2frame(factor, index, columns)
    factor.to_hdf(factor_output_path + factor_name + '.h5', factor_name)
    print(factor_name, '已完成')
    print('运行时间：', time.clock()-e)

print('finished!')