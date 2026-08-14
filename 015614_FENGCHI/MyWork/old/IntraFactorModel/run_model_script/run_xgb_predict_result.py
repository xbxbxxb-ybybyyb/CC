# @Time : 2020/5/25 16:58
# @Author : fengchi863
# @File : run_predict_result.py

import os
from multiprocessing import Pool

import gc
import pandas as pd

from conf.path_config import junk_clf_path

gc.enable()

from conf.model_param_config import XGBModel, best_param_clf_xgboost_rise_down_zero
from dataApi.stockList import clean_stock_list

xgb = XGBModel(start_date=20170102, end_date=20191231,
               factor_path='/data/group/800319/junkData/IntraFactorModel/FactorByStock_from2017_whole_mkt/')
out_path = '/data/group/800319/junkData/IntraFactorModel/predictions/xgb_rise_down_zero_1min_20200709/'
if not os.path.exists(out_path):
    os.mkdir(out_path)


def wraper(stk):
    if os.path.exists(out_path + '%d.pkl' % stk):
        print(stk, 'exist')
        return 0
    try:
        compare, metric = xgb.training_methodology(stk, 'rise_down_zero_1min', best_param_clf_xgboost_rise_down_zero)
        pd.to_pickle([compare, metric], out_path + '%d.pkl' % stk)
    except:
        print('Wrong', stk)
        pd.to_pickle([], out_path + 'Wrong_%d.pkl' % stk)
    gc.collect()


def main():
    stock_pool = clean_stock_list('ALL', no_limit_down=True, no_limit_up=True).loc[20140102:20200529]
    isin = stock_pool.sum(axis=0)
    stk_list = isin[isin > 0].index.tolist()
    pool = Pool(16)
    # pool.map(wraper, stk_list[-1000:])
    pool.map(wraper, [2200])
    pool.close()
    pool.join()




def main_portfolio_stk():
    # 韩旭陶鑫股票池
    wgt_opt = pd.read_hdf(junk_clf_path + 'Portfolio.h5', 'Portfolio')
    isin = wgt_opt.sum(axis=0)
    stk_list = isin[isin > 0].index.tolist()
    pool = Pool(6)
    pool.map(wraper, stk_list[-500:])
    pool.close()
    pool.join()


"""
def main_wrong():
    file_list = os.listdir(out_path)
    file_list = list(filter(lambda x : 'Wrong' in x,file_list))
    file_list = list(map(lambda x: int(x.strip('.pkl').split('_')[-1]),file_list))
    pool = Pool(20)
    pool.map(wraper, file_list)
    pool.close()
    pool.join()


def wraper_wrong(stk):
    if os.path.exists(out_path + '%d.pkl' % stk):
        print(stk, 'exist')
        return 0
    # try:
    compare, metric = lr.training_methodology(stk, 'twap', best_param_clf_lr)
    pd.to_pickle([compare, metric], out_path + '%d.pkl' % stk)
    # except:
    #     print('Wrong', stk)
    #     pd.to_pickle([], out_path + 'Wrong_%d.pkl' % stk)
    gc.collect()
"""

if __name__ == "__main__":
    # compare, metric = lr.training_methodology(1, 'rise_down_zero_1min', best_param_clf_lr)
    compare, metric = xgb.training_methodology(600645, 'rise_down_zero_5min', best_param_clf_xgboost_rise_down_zero)
    pd.to_pickle([compare, metric], out_path + '%d.pkl' % 600645)
    # main_portfolio_stk()
    # main()
    # wraper_wrong(600614)
    # file_list = os.listdir(out_path)
    # file_list = list(filter(lambda x : 'Wrong' not in x,file_list))
    # len(file_list)
