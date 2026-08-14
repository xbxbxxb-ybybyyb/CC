# coding: utf-8
# Author：fengchi863
# Date ：2023/11/24 10:04

import os
from Zeus.Europa.v4_0_61.strat_conf import *
from Zeus.Europa.v4_0_61.path_conf import *
from Zeus.Europa.v4_0_61.backtest.sim_backtest.SimBackTest import SimBackTest

if __name__ == '__main__':
    period = period
    date_dict = date_config[period]
    hyper_search_mode = 1
    test_start_date = date_dict['test_start_date']
    test_end_date = date_dict['test_end_date']
    fit_start_date = date_dict['fit_start_date']
    fit_end_date = date_dict['fit_end_date']
    hyper_root_path = f'/data/user/015614/Zeus/pred/Europa/{strategy_version}/'
    model_names = os.listdir(hyper_root_path)
    pred_fpath_list = list()
    fit_fpath_list = list()
    if hyper_search_mode > 0:
        for model_name in model_names:
            if not os.path.exists(hyper_root_path + model_name + f'/hyper/'):
                continue
            hyper_list = os.listdir(hyper_root_path + model_name + f'/hyper/')
            for search_time in hyper_list:
                pred_fpath_list.append(hyper_root_path + model_name + f'/hyper/{search_time}/{test_start_date}~{test_end_date}.csv')
                fit_fpath_list.append(hyper_root_path + model_name + f'/hyper/{search_time}/{fit_start_date}~{fit_end_date}.csv')
    else:
        for model_name in model_names:
            if not os.path.exists(hyper_root_path + model_name + '/'):
                continue
            pred_fpath_list.append(hyper_root_path + model_name + f'/{test_start_date}~{test_end_date}.csv')
            fit_fpath_list.append(hyper_root_path + model_name + f'/{fit_start_date}~{fit_end_date}.csv')

    sbt = SimBackTest(pred_fpath_list=pred_fpath_list,
                      fit_fpath_list=fit_fpath_list,
                      date_dict=date_config[period],
                      attend_ratio_range=(20, 50),
                      save_flag=True,
                      multi_attend=True)
    sbt.start_backtest(multi=True)