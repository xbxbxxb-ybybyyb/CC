# coding: utf-8
# Author：fengchi863
# Date ：2021/5/25 13:29

from LimitUpPredStrategy.backtest.strategy_backtest.StrategyTest import StrategyTest
from LimitUpPredStrategy.conf.path_conf import pred_output_path, bt_output_path
from LimitUpPredStrategy.Util.DataUtil import DataUtil
import pandas as pd
import os

kind_ensembles = 'voting'

model_pred_list = ['linear_reg/linear_reg_trainPeriod60_predictPeriod10_factorNum4_pctThreshold0.03_signal_r2s3.pkl',
                   'linear_reg/linear_reg_trainPeriod60_predictPeriod10_factorNum4_pctThreshold0.02_signal_r2s3.pkl']

model_pred_list = [pred_output_path + pred_path for pred_path in model_pred_list]

model_ensembles_num = len(model_pred_list)
pred_sum = 0
for model_pred_path in model_pred_list:
    pred_sum += DataUtil.read_pickle(model_pred_path).loc[:,'prediction'].astype(int)

pred_sum[pred_sum['prediction'] > (model_ensembles_num / 2)] = True