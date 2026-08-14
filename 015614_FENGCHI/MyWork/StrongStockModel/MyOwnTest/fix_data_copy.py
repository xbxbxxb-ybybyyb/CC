# coding: utf-8
# Author：fengchi863
# Date ：2020/7/29 11:34

from StrongStockModel.conf.path_config import fix_factor_path, \
    root_path, intraday_factor_by_date_path
from StrongStockModel.dataApi.getData import get_date_range
from StrongStockModel.dataApi.stockList import clean_stock_list
from StrongStockModel.dataApi.tradeDate import trade_minutes
from StrongStockModel.System.LoadFactor.factor_utils import *
import pandas as pd, numpy as np, os
from StrongStockModel.conf.path_config import root_path

def frame2arr(df, minutes=242):
    return df.values.reshape(df.shape[0] // minutes, minutes, df.shape[1]).transpose(1, 0, 2)

fix_factor_list = fetch_factor_list()
fix1000 = []
fix1030 = []
fix1100 = []
fix1300 = []
fix1330 = []
fix1400 = []
fix1430 = []

count_dict = {'930':  0,
              '1000': 0,
              '1030': 0,
              '1100': 0,
              '1130': 0,
              '1300': 0,
              '1330': 0,
              '1330': 0,
              '1400': 0,
              '1430': 0}

for factor in fix_factor_list:
    if '1000' in factor:
        count_dict['1000'] += 1
        fix1000.append(factor)
    elif '1030' in factor:
        count_dict['1030'] += 1
        fix1030.append(factor)
    elif '1100' in factor:
        count_dict['1100'] += 1
        fix1100.append(factor)
    elif '1300' in factor:
        count_dict['1300'] += 1
        fix1300.append(factor)
    elif '1330' in factor:
        count_dict['1330'] += 1
        fix1330.append(factor)
    elif '1400' in factor:
        count_dict['1400'] += 1
        fix1400.append(factor)
    elif '1430' in factor:
        count_dict['1430'] += 1
        fix1430.append(factor)
    else:
        pass

fix1000 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1000))
fix1030 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1030))
fix1100 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1100))
fix1300 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1300))
fix1330 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1330))
fix1400 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1400))
fix1430 = list(map(lambda x: '_'.join(x.split('_')[1:]),fix1430))

fix_factor_list = list(set(fix1000).intersection(set(fix1030)).intersection(set(fix1100)).intersection(set(fix1300)).
     intersection(set(fix1330)).intersection(set(fix1400)).intersection(set(fix1430)))
fix_factor_list = sorted(fix_factor_list)

start_date = 20140101
end_date = 20161231
date_list = get_date_range(start_date, end_date)
factor_list = fetch_factor_list()

out_path = root_path + 'factor/fix_factor/'

stk_dict = pd.read_pickle(root_path + 'factor/stk_dict/stk_dict.pkl')
stk_list = list(stk_dict.keys())
stk_list.sort()

fix_trade_minutes = [1000, 1030, 1100, 1300, 1330, 1400, 1430]

def wrapper(date):
    if os.path.exists(out_path + '%d.npy' % date):
        return
    print(date)
    file_name = os.listdir('%s/mddate=%s' % (fix_factor_path, date))[0]
    df = pd.read_parquet('%s/mddate=%s/%s' % (fix_factor_path, date, file_name), columns=['stock'] + factor_list)
    df.set_index('stock', inplace=True)
    df.index = df.index.map(trans_windcode2int)
    df = df.loc[stk_list, :]
    factor = pd.DataFrame(index=pd.MultiIndex.from_product([fix_trade_minutes, stk_list]), columns=fix_factor_list)
    for fix_factor in fix_factor_list:
        # print(fix_factor)
        factor.loc[(1000, slice(None)), fix_factor] = df.loc[stk_list, 'Fix1000_' + fix_factor].values
        factor.loc[(1030, slice(None)), fix_factor] = df.loc[stk_list, 'Fix1030_' + fix_factor].values
        factor.loc[(1100, slice(None)), fix_factor] = df.loc[stk_list, 'Fix1100_' + fix_factor].values
        factor.loc[(1300, slice(None)), fix_factor] = df.loc[stk_list, 'Fix1300_' + fix_factor].values
        factor.loc[(1330, slice(None)), fix_factor] = df.loc[stk_list, 'Fix1330_' + fix_factor].values
        factor.loc[(1400, slice(None)), fix_factor] = df.loc[stk_list, 'Fix1400_' + fix_factor].values
        factor.loc[(1430, slice(None)), fix_factor] = df.loc[stk_list, 'Fix1430_' + fix_factor].values
    factor = frame2arr(factor, 7)
    print(factor.shape)
    np.save(out_path + '%d.npy' % date, factor)

from multiprocessing import Pool
pool = Pool(3)
pool.map_async(wrapper, date_list)
pool.close()
pool.join()
