# @Time : 2020/6/9 9:35
# @Author : Zhichen Lu
# @File : multi_processing_1min.py
# @Time : 2020/5/25 16:58
# @Author : Zhichen Lu
# @File : run_predict_result.py

import sys

sys.path.append('/data/user/015664/IntradayStrasts/intrafactormodel/')
sys.path.append('/data/user/015664/IntradayStrasts/BackTestModule/')
import os
from multiprocessing import Pool
import gc
import pandas as pd
from conf.model_param_config import *
from dataApi.stockList import clean_stock_list
from conf.feature_config import scale_list, non_scale_list

print(len(scale_list))
out_path = '/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_5min_2018all_mkt_origin_nodrop_factor_20200709/'
# fil_list = os.listdir(out_path)
# for file_name in fil_list:
#     os.remove(out_path+file_name)
if not os.path.exists(out_path):
    os.mkdir(out_path)


def wraper(stk):
    if os.path.exists(out_path + '%d.pkl' % stk):
        print(stk, 'exist')
        return 0
    try:
        lr = RollingLRModel(start_date=20170102, end_date=20191231, factor_path='/data/group/800319/junkData/IntraFactorModel/FactorByStock_from2017_whole_mkt/',
                            scare_list=scale_list, non_scare_list=non_scale_list)
        compare, metric = lr.training_methodology(stk, 'rise_down_zero_1min', best_param_clf_lr)
        pd.to_pickle([compare, metric], out_path + '%d.pkl' % stk)
    except:
        print('Wrong', stk)
        pd.to_pickle([], out_path + 'Wrong_%d.pkl' % stk)
    gc.collect()


#
# def wraper_mlp(stk):
#     if os.path.exists(out_path + '%d.pkl' % stk):
#         print(stk, 'exist')
#         return 0
#     try:
#         lr = MLPModel(start_date=20170102, end_date=20191231, factor_path= '/data/group/800319/junkData/IntraFactorModel/FactorByStock_from2017_whole_mkt/',
#                         scare_list=scale_list,non_scare_list=non_scale_list)
#         compare, metric = lr.training_methodology(stk, 'rise_down_zero_5min', best_param_clf_mlp)
#         pd.to_pickle([compare, metric], out_path + '%d.pkl' % stk)
#     except:
#         print('Wrong', stk)
#         pd.to_pickle([], out_path + 'Wrong_%d.pkl' % stk)
#     gc.collect()
#
# def wraper(stk):
#     if os.path.exists(out_path + '%d.pkl' % stk):
#         print(stk, 'exist')
#         return 0
#     try:
#         lr = MLPModel(start_date=20170102, end_date=20191231, factor_path= '/data/group/800319/junkData/IntraFactorModel/FactorByStock_from2017_whole_mkt/',
#                         scare_list=scale_list,non_scare_list=non_scale_list)
#         compare, metric = lr.training_methodology(stk, 'rise_down_zero_5min', best_param_clf_mlp)
#         pd.to_pickle([compare, metric], out_path + '%d.pkl' % stk)
#     except:
#         print('Wrong', stk)
#         pd.to_pickle([], out_path + 'Wrong_%d.pkl' % stk)
#     gc.collect()

def main(i):
    stock_pool = clean_stock_list('ALL', no_limit_down=True, no_limit_up=True).loc[20180102:20181231]
    isin = stock_pool.sum(axis=0)
    stk_list = isin[isin > 0].index.tolist()
    print(len(stk_list))
    pool = Pool(10)
    if i == 3:
        pool.map(wraper, stk_list[(i - 1) * len(stk_list) // 3:])
    else:
        pool.map(wraper, stk_list[(i - 1) * len(stk_list) // 3:i * len(stk_list) // 3])
    pool.close()
    pool.join()


# lr = RollingLRModel(start_date=20170102, end_date=20191231, factor_path='/data/group/800319/junkData/IntraFactorModel/FactorByStock_/')
# compare, metric = lr.training_methodology(603076, 'rise_down_zero_1min', best_param_clf_lr)
"""

def main_portfolio_stk():
    wgt_opt = pd.read_hdf('/data/group/800319/junkClassification/wgt_opt.h5', 'wgt_opt')
    isin = wgt_opt.sum(axis=0)
    stock_list = isin[isin>0].index.tolist()
    pool = Pool(20)
    pool.map(wraper, stock_list)
    pool.close()
    pool.join()

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
    # wraper(600614)
    #    param = AIMR.getParam()
    #    param = int(param)
    #    main(param)

    main(1)
    # param=1
#    main_portfolio_stk(param)
#     for i in range(1,4):
#         main(i)
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
