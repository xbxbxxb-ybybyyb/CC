# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import xgboost as xgb
import os, gc, time, datetime
from StrongStockModel.conf.path_config import root_path
from tqdm import tqdm
from multiprocessing import Process
from dataApi.tradeDate import get_date_range,get_pre_trade_date
from dataApi.FixFactorRollPrepare import FixFactorRollPrepare
import random
import configparser
conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

def get_rolling_index(start, end, period=10, period_predict=10):
    date_list = get_date_range(start, end)
    rolling_train_test_idx_list = []
    if len(date_list) == period:
        return [(0, (date_list[0], date_list[-1], date_list[-1], date_list[-1]))]
    else:
        length = (len(date_list) - period) // period_predict + 1
    for idx in range(length):
        train_start_idx = idx * period_predict
        train_end_idx = idx * period_predict + period - 1
        if idx == (len(date_list) - period) // period_predict:
            if (len(date_list) - period) % period_predict == 0:
                test_end_idx, test_start_idx = len(date_list) - 1, len(date_list) - 1
            else:
                test_start_idx = idx * period_predict + period
                test_end_idx = len(date_list) - 1
        else:
            test_start_idx = idx * period_predict + period
            test_end_idx = test_start_idx + period_predict - 1
        train_start_date, train_end_date, test_start_date, test_end_date = [date_list[i] for i in
                                                                            [train_start_idx, train_end_idx,
                                                                             test_start_idx, test_end_idx]]
        rolling_train_test_idx_list.append(
            (idx, (train_start_date, train_end_date, test_start_date, test_end_date)))
    return rolling_train_test_idx_list

train_date_list = get_date_range(20160101,20170101)
test_date_list = get_date_range(20170101,20170630)

num = 50

if os.path.exists(f'/data/user/015664/AFuckingTrigger/NonLinearEval/factor_split{num}.pkl'):
    factor_split = pd.read_pickle(f'/data/user/015664/AFuckingTrigger/NonLinearEval/factor_split{num}.pkl')
else:
    factor_split = []
    while len(using_factor_list)>num:
        factor_split.append(random.sample(using_factor_list,num))
        using_factor_list = list(set(using_factor_list)-set(factor_split[-1]))
    pd.to_pickle(factor_split,f'/data/user/015664/AFuckingTrigger/NonLinearEval/factor_split{num}.pkl')


using_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')
factor_list = list(map(lambda x : x.replace('.npy',''),os.listdir('/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')))
using_factor_list = sorted(list(set(using_factor_list).intersection(set(factor_list))))


def fit_model(sub_factor_list):
    dp = FixFactorRollPrepare(start_date=train_date_list[0], end_date=test_date_list[-1], freq=7, model_time_len=1,
                              factor_list=sub_factor_list, load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/')
    X_train, y_train, nolimit, idx_date, idx_time, idx_code = dp.load_data(start_date=train_date_list[0], end_date=train_date_list[-1], return_idx=True)
    X_train, y_train, idx_date, idx_time, idx_code = dp.feature_engineering(X_train, y_train, nolimit, idx_date, idx_time, idx_code)
    clf = xgb.XGBRegressor(tree_method='gpu_hist')

