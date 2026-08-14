# coding: utf-8
# Author：fengchi863
# Date ：2024/3/18 13:11

"""
正常回测，hyper=0的版本
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

import pandas as pd
import os
from Zeus.P4.v1_0_6.config.strat_conf import *
from Zeus.P4.v1_0_6.config.path_conf import *
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil

if __name__ == '__main__':
    period = 'period1'
    date_dict = DATE_CONFIG[period]
    test_start_date = date_dict['test_start_date']
    test_end_date = date_dict['test_end_date']
    fit_start_date = date_dict['fit_start_date']
    fit_end_date = date_dict['fit_end_date']
    hyper_root_path = f'/data/user/015614/Zeus/pred/P4/{STRATEGY_VERSION}/'
    # config_list = list(sorted(os.listdir(hyper_root_path)))
    config_list = [f'config{x}' for x in range(1, 5)]
    # config_list = ['config2', 'config5']
    # config_list = ['config1', 'config2', 'config3', 'config5', 'config7', 'config8', 'config9']
    output_dict = {}
    model_res = pd.DataFrame()
    signal_df = pd.DataFrame()
    for config in config_list:
        model_names = list(sorted(os.listdir(hyper_root_path + f'/{config}/')))
        for model_name in model_names:

                if not os.path.exists(hyper_root_path + config + '/' + model_name + f'/bt_result_{period}.xlsx'):
                    continue
                signal = pd.read_csv(pred_out_path + f'{STRATEGY_NAME}/{STRATEGY_VERSION}/{config}/{model_name}/{test_start_date}~{test_end_date}.csv')
                signal = signal[['pred_Reg']].rename({'pred_Reg': f'{config}-{model_name}'}, axis=1)
                signal_df = pd.concat([signal_df, signal], axis=1)

                bt_result_dict = pd.read_excel(hyper_root_path + config + '/' + model_name + f'/bt_result_{period}.xlsx', index_col=0, sheet_name=None)
                stats_df = bt_result_dict['汇总结果'].iloc[:,0]
                tmp_res = pd.Series(stats_df.to_dict())
                tmp_res['model_name'] = model_name
                tmp_res['config'] = config

                model_res = model_res.append(tmp_res.T, ignore_index=True)

    signal_corr = signal_df.corr()
    model_res = model_res[tmp_res.index.tolist()]
    output_dict['汇总结果'] = model_res.set_index(['config', 'model_name'])
    output_dict['相关性'] = signal_corr
    FileUtil.save_dict2xls(output_dict, '/data/user/015614/junkData/', f'{STRATEGY_VERSION}_{STRATEGY_NAME}_{period}_汇总结果.xlsx')
    send_file(f'/data/user/015614/junkData/{STRATEGY_VERSION}_{STRATEGY_NAME}_{period}_汇总结果.xlsx')