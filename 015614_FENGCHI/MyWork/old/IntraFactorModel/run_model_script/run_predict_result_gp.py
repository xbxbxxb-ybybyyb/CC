# @Time : 2020/5/25 16:58
# @Author : Zhichen Lu
# @File : run_predict_result.py

import os
from multiprocessing import Pool

import gc
import pandas as pd

from conf.model_param_config import *
from dataApi.stockList import clean_stock_list

lr = RollingLRModel(factor_path='/data/group/800319/junkData/IntraFactorModel/gp_FactorByStock/')
out_path = '/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_gp_factor_20200604/'
if not os.path.exists(out_path):
    os.mkdir(out_path)


def wraper(stk):
    if os.path.exists(out_path + '%d.pkl' % stk):
        print(stk, 'exist')
        return 0
    try:
        compare, metric = lr.training_methodology(stk, 'rise_down_zero_5min', best_param_clf_lr)
        pd.to_pickle([compare, metric], out_path + '%d.pkl' % stk)
    except:
        print('Wrong', stk)
        pd.to_pickle([], out_path + 'Wrong_%d.pkl' % stk)
    gc.collect()


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
    stock_list = isin[isin > 0].index.tolist()

    pool = Pool(20)
    pool.map(wraper, stock_list[:len(stock_list) // 2])
    pool.close()
    pool.join()


def main_wrong():
    file_list = os.listdir(out_path)
    file_list = list(filter(lambda x: 'Wrong' in x, file_list))
    file_list = list(map(lambda x: int(x.strip('.pkl').split('_')[-1]), file_list))
    pool = Pool(10)
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


if __name__ == "__main__":
    main_portfolio_stk()
    # main()
    # wraper_wrong(600614)
    # file_list = os.listdir(out_path)
    # file_list = list(filter(lambda x : 'Wrong' not in x,file_list))
    # len(file_list)

"""
from dataset_generation import FactorDataSet
from dataApi.getData import get_minute_1factor,get_daily_1factor
from dataApi.tradeDate import get_date_range
from dataApi.usefulTools import *
fds = FactorDataSet()
def wraper(stk):
    try:
        label = fds.get_label_twap(stk)
        print(stk,'done')
        return label
    except:
        print(stk,'wrong')
signal = pd.read_pickle('/data/group/800319/junkClassification/predict_signal_lr_20200527_revised.pkl')
signal.columns = [int(x) for x in signal.columns.tolist()]
close = get_minute_1factor('close',start_datetime=201701030925,end_datetime=201912311500,code_list=[int(x) for x in signal.columns.tolist()])
daily_twap = get_daily_1factor('twap',date_list=get_date_range(20170103,20191231),code_list=signal.columns.tolist())
close_arr = frame2arr(close)
twap_profit = daily_twap.values/close_arr - 1
signal_arr = frame2arr(signal)
real_lable = (twap_profit>0)*1. - 1.*(twap_profit<0)
label_df = arr2frame(real_lable,index=close.index.tolist(),columns=close.columns.tolist())
label_df = label_df.loc[signal.index]
judge = (label_df==signal).sum()
acc = judge/signal.count()

label_arr = frame2arr(label_df)
morning_part = 60
morning_judge = np.equal(arr2frame(signal_arr[:morning_part],columns=signal.columns,index=list(range(morning_part*611))),
                         arr2frame(label_arr[:morning_part],columns=signal.columns,index=list(range(morning_part*611))))
morning_signal = arr2frame(signal_arr[:morning_part],columns=signal.columns,index=list(range(morning_part*611)))
morning_label = arr2frame(label_arr[:morning_part],columns=signal.columns,index=list(range(morning_part*611)))
acc_morning = morning_judge.sum()/morning_signal.count()
"""
