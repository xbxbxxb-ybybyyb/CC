# @Time : 2021/7/8 10:28
# @Author : Zhichen Lu
# @File : ResIntegration.py

import pandas as pd
from R2D2.conf.path_conf import root_path
from R2D2.Env.FixEnv import StockEnv
from stable_baselines3 import A2C
from dataApi.tradeDate import get_date_range
import os
from tqdm import tqdm

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

all_pred_ret = []

for train_start, train_end, test_start, test_end in tqdm(period_info):
    model = A2C.load(f'{base_path}/model/test_model_{train_start}_{train_end}')
    stk_list = pd.read_pickle(f'{base_path}/stk_list/{train_start}_{train_end}.pkl')
    env = StockEnv(start=test_start, end=test_end, stk_list=stk_list)
    obs = env.reset()
    terminal = False

    index = []
    pred = []
    while not terminal:
        action = model.predict(obs)
        pred.append(action[0].tolist())
        sate, reward, terminal, _ = env.step(action[0])
        index.append(env.datetime[:2])
    pred_ret = pd.DataFrame(pred, index=pd.MultiIndex.from_tuples(index), columns=stk_list)
    pd.to_pickle(pred_ret, f'{base_path}pred_ret/{test_start}_{test_end}.pkl')
    all_pred_ret.append(pred_ret)

all_pred_ret = pd.concat(all_pred_ret)
pd.to_pickle(all_pred_ret, f'{base_path}all_pred_ret.pkl')
