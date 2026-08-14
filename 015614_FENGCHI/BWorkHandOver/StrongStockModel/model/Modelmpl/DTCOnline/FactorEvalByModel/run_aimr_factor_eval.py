# @Time : 2021/12/30 14:14
# @Author : Zhichen Lu
# @File : run_aimr_factor_eval.py
import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from dataApi.tradeDate import get_date_range, get_recent_trade_date, get_pre_trade_date

from StrongStockModel.model.Modelmpl.DTCOnline.FactorEvalByModel import aimr_multitimes
import configparser
import os,time
import json
import itertools
import pandas as pd
import configparser
import datetime
conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])
params = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607, 'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100,
          'sampling_method': 'gradient_based', 'subsample': 0.8, 'tree_method': 'gpu_hist',
          'val_pred_path': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_val_pred/',
          'model_conf_path': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_model_conf/',
          'feature_path': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_factor_list/',
          'load local model': True}
TARGET_PATH = '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_EvalRes/'

i = 0
while True:

    now = datetime.datetime.now()
    HHMM = int(now.strftime('%H%M'))
    no_running_period = [(610, 930), (1555, 1915)]
    forbiden_period = False
    trading_day = get_recent_trade_date(int(now.strftime('%Y%m%d'))) == int(now.strftime('%Y%m%d'))
    if trading_day:
        for s, e in no_running_period:
            if HHMM > s and HHMM < e:
                forbiden_period = True

                delta_period = datetime.datetime(now.year,now.month,now.day, e//100, e%100) - datetime.datetime(now.year,now.month,now.day, HHMM//100, HHMM%100)
                print(f'---------------sleep until {datetime.datetime(now.year,now.month,now.day, e//100, e%100)} -------------------')
                time.sleep(delta_period.seconds+60)
                break

    aimr_para_list = []
    for p_idx in list(range(135))[24:]:
        tr_end = para_list[p_idx][1][1]
        if not os.path.exists(params['val_pred_path']+f'{tr_end}.pkl') or not os.path.exists(params['model_conf_path']+f'{tr_end}.json') or not os.path.exists(params['feature_path']+f'{tr_end}.pkl'):
            continue
        factor_list = pd.read_pickle(params['feature_path']+f'{tr_end}.pkl')
        factor_list = list(filter(lambda x : not os.path.exists(f'{TARGET_PATH}/{tr_end}/{x}.npy'),factor_list))
        temp_para = [(x,tr_end) for x in factor_list]
        aimr_para_list = aimr_para_list+temp_para

    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),f'{len(aimr_para_list)} mission are now waiting')

    if not aimr_para_list:
        time.sleep(60*30)

    task_num = 99
    if trading_day:
        if HHMM<1915:
            task_num =task_num// 2
    print('task_num',task_num)


    aimr_params = {
        "parallel_list": aimr_para_list[:task_num],
        "tag":"xquant",
        "cpu":1,
        "gpu":0,
        "memory":1024*15,
        "preferred_gpu":0
    }
    aimr_multitimes.runTasks('./FactorEvalByModel/XGBMonthlyAllFeatureEval.py',json.dumps(aimr_params))
    i+=1
    print(f'----------{i}----------')

