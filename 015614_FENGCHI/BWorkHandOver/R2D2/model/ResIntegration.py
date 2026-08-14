# @Time : 2021/7/8 10:28
# @Author : Zhichen Lu
# @File : ResIntegration.py

import pandas as pd
from R2D2.conf.path_conf import root_path
from R2D2.Env.FixEnv import StockEnv
from stable_baselines3 import A2C
from dataApi.tradeDate import get_date_range
import os

base_path = f'{root_path}/TainingRes/A2CTest_train80_test20/'

file_list = os.listdir(base_path)


def split_date_period(date_list, train_period, test_period):
    train_start = date_list[0:-test_period - train_period:test_period]
    train_end = [date_list[date_list.index(x) + train_period - 1] for x in train_start]
    predict_start = [date_list[date_list.index(x) + train_period] for x in train_start]
    predict_end = [date_list[date_list.index(x) + test_period - 1] for x in predict_start]

    period_info = list(zip(train_start, train_end, predict_start, predict_end))
    if period_info[-1][-1] != date_list[-1]:
        last_period = tuple([date_list[date_list.index(x) + test_period] for x in period_info[-1][:-1]]) + (date_list[-1],)
        period_info.append(last_period)
    return period_info


start, end = 20170101, 20201231
train_date_list = get_date_range(start, end)
period_info = split_date_period(train_date_list, 80, 20)

account = pd.Series()
for train_start, train_end, test_start, test_end in period_info:
    # obs = None
    accout_value, account_index, cash_series, daily_holding = pd.read_pickle(f'{base_path}pred_res/pred_{test_start}.pkl')
    temp_account = pd.Series(accout_value, index=account_index)
    temp_account = temp_account / temp_account.tolist()[0]
    if len(account) > 0:
        temp_account = temp_account * account.tolist()[-1]
    account = pd.concat([account, temp_account])
