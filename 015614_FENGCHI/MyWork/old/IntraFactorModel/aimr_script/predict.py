# coding: utf-8
# Author：fengchi863
# Date ：2020/6/1 17:03

import os
from multiprocessing import Pool

import gc
import pandas as pd
from xquant.compute.aimr import AIMR

from conf.model_param_config import *

model = model_choice['xgb'][0]()
out_path = '/data/group/800319/junkData/IntraFactorModel/predictions/xgb_model_20200529_tick_twap/'
if not os.path.exists(out_path):
    os.mkdir(out_path)


def wraper(stk):
    if os.path.exists(out_path + '%d.pkl' % stk):
        print(stk, 'exist')
        return 0
    try:
        compare, metric = model.training_methodology(stk, 'tick_twap', best_param_clf_xgboost)
        pd.to_pickle([compare, metric], out_path + '%d.pkl' % stk)
    except Exception as e:
        print(e)
        print('Wrong', stk)
        pd.to_pickle([], out_path + 'Wrong_%d.pkl' % stk)
    gc.collect()


def main(stock_list):
    pool = Pool(10)
    pool.map(wraper, stock_list)
    pool.close()
    pool.join()


def main_portfolio_stk(stock_list):
    pool = Pool(10)
    pool.map(wraper, stock_list)
    pool.close()
    pool.join()


if __name__ == "__main__":
    param = AIMR.getParam()
    param = int(param)

    # main_portfolio_stk
    wgt_opt = pd.read_hdf('/data/group/800319/junkClassification/wgt_opt.h5', 'wgt_opt')
    isin = wgt_opt.sum(axis=0)
    stock_list = isin[isin > 0].index.tolist()

    # main
    # stock_pool = clean_stock_list('COMMON', no_limit_down=True, no_limit_up=True).loc[20170103:20191231]
    # isin = stock_pool.sum(axis=0)
    # stock_pool = stock_pool[isin[isin > 0].index]
    # stock_list = stock_pool

    length = len(stock_list)
    part = int(length / 4)
    start = (param - 1) * part
    end = param * part
    if param == 4:
        end = length
    print(start, end)

    main_portfolio_stk(stock_list[start:end])
    main(stock_list[start:end])
