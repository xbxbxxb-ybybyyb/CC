# @Time : 2020/5/26 16:59
# @Author : Zhichen Lu
# @File : run_mlp.py
import os
from multiprocessing import Pool

import gc
import pandas as pd

from conf.model_param_config import *
from dataApi.stockList import clean_stock_list

print(1)
mlp = MLPModel()
out_path = '/data/group/800319/junkData/IntraFactorModel/predictions/mlp_model_rise_down_zero_20200601/'
if not os.path.exists(out_path):
    os.mkdir(out_path)
print(2)
def wraper(stk):
    params = {'activation': 'relu', 'alpha': 9.756090506594905e-05, 'hidden_layer_sizes': (16, 32, 8),
              'learning_rate': 'adaptive', 'learning_rate_init': 0.0703114914234283, 'momentum': 0.1669382592981298, 'solver': 'sgd'}
    if os.path.exists(out_path + '%d.pkl' % stk):
        print(stk, 'exist')
        return 0
    try:
        compare, metric = mlp.training_methodology(stk, 'rise_down_zero', params)
        pd.to_pickle([compare, metric], out_path + '%d.pkl' % stk)
    except:
        print('Wrong', stk)
        pd.to_pickle([], out_path + 'Wrong_%d.pkl' % stk)
    gc.collect()


# def wraper_wrong(stk):
#     params = {'activation': 'tanh', 'alpha': 0.0029127028632977155, 'hidden_layer_sizes': (8, 8),
#               'learning_rate': 'adaptive', 'learning_rate_init': 0.02128564148920172, 'momentum': 0.13689656067198971, 'solver': 'sgd'}
#
#     if os.path.exists(out_path + '%d.pkl' % stk):
#         print(stk, 'exist')
#         return 0
#     compare, metric = mlp.training_methodology(stk, 'twap', params)
#     pd.to_pickle([compare, metric], out_path + '%d.pkl' % stk)
#     gc.collect()


def main():
    stock_pool = clean_stock_list('COMMON', no_limit_down=True, no_limit_up=True).loc[20170103:20191231]
    isin = stock_pool.sum(axis=0)
    stock_pool = stock_pool[isin[isin > 0].index]
    pool = Pool(20)
    pool.map(wraper, stock_pool.columns.tolist())
    pool.close()
    pool.join()

def main_portfolio_stk():
    wgt_opt = pd.read_hdf('/data/group/800319/junkClassification/wgt_opt.h5', 'wgt_opt')
    isin = wgt_opt.sum(axis=0)
    stock_list = isin[isin>0].index.tolist()
    pool = Pool(20)
    pool.map(wraper, stock_list)
    pool.close()
    pool.join()


# main_portfolio_stk()
main()
