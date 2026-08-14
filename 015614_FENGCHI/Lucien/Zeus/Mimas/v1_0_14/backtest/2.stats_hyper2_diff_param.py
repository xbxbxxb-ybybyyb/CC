# coding: utf-8
# Author：fengchi863
# Date ：2023/11/24 13:04

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

import json
import pandas as pd
import os
from Zeus.Mimas.v1_0_14.config.strat_conf import *
from Zeus.Mimas.v1_0_14.config.path_conf import *
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil

# 防止query的时候触发关键字，lambda需要特殊处理
xgb_watch_params = ['num_boost_round', 'seed']
lgb_watch_params = ['n_estimators', 'seed']

if __name__ == '__main__':
    period = 'period3'
    date_dict = DATE_CONFIG[period]
    test_start_date = date_dict['test_start_date']
    test_end_date = date_dict['test_end_date']
    fit_start_date = date_dict['fit_start_date']
    fit_end_date = date_dict['fit_end_date']
    hyper_root_path = f'/data/user/015614/Zeus/pred/Mimas/{STRATEGY_VERSION}/'
    config_names = os.listdir(hyper_root_path)
    pred_fpath_list = list()
    fit_fpath_list = list()
    all_res_df = pd.DataFrame()
    for config in config_names:
        res_df = pd.DataFrame()
        model_names = os.listdir(hyper_root_path + f'{config}/')
        for model_name in model_names:
            if 'Xgb' in model_name:
                watch_params = xgb_watch_params
            if 'Lgb' in model_name:
                watch_params = lgb_watch_params

            model_param_list = []

            if not os.path.exists(hyper_root_path + f'{config}/' + model_name + f'/hyper/'):
                continue

            hyper_list = os.listdir(hyper_root_path + f'{config}/' + model_name + f'/hyper/')
            for search_time in hyper_list:
                if not os.path.exists(hyper_root_path + f'{config}/' + model_name + f'/hyper/{search_time}/bt_result_{period}.xlsx'):
                    continue

                with open(hyper_root_path + f'{config}/' + model_name + f'/hyper/{search_time}/param.json', 'r') as f_obj:
                    param = json.load(f_obj)

                bt_result_dict = pd.read_excel(hyper_root_path + f'{config}/' + model_name + f'/hyper/{search_time}/bt_result_{period}.xlsx', index_col=0, sheet_name=None)
                try:
                    train_result = pd.read_json(hyper_root_path + f'{config}/' + model_name + f'/hyper/{search_time}/train_result_{period}.json')
                except:
                    print(1)
                stats_df, model_test_mingan = bt_result_dict['汇总结果'].iloc[:,0], bt_result_dict['test']
                stats_df['累计扣费总收益'] /= 1e8
                stats_df['最大回撤'] /= 1e8
                stats_df['平均收益风险比'] = model_test_mingan['收益风险比'].mean()
                stats_df['平均收益夏普比率'] = model_test_mingan['收益夏普比率'].mean()
                stats_df = stats_df.map(lambda x: round(x, 2))
                stats_df['基础样本数量'] = int(stats_df['基础样本数量'])
                stats_df['train_accuracy'] = train_result.loc[2, 1]
                stats_df['test_accuracy'] = train_result.loc[0, 1]
                tmp_res = pd.Series({**{k:v for k, v in param.items() if k in watch_params}, **stats_df.to_dict()})
                model_param_list.append(tmp_res)

            model_param_res = pd.DataFrame(model_param_list).sort_values(watch_params)

            _watch_params = watch_params.copy()
            if 'seed' in watch_params:
                _watch_params.remove('seed')

            best_seed_list = model_param_res.sort_values('平均收益夏普比率', ascending=False).groupby(_watch_params)['seed'].agg('first').tolist()
            groupby_param_res = model_param_res.groupby(_watch_params).agg({'累计扣费总收益': 'mean',
                                                                           '最大回撤': 'mean',
                                                                           '收益风险比': 'mean',
                                                                           '收益夏普比率': 'mean',
                                                                           '平均收益风险比': 'mean',
                                                                           '平均收益夏普比率': 'mean',
                                                                           'train_accuracy': 'mean',
                                                                           'test_accuracy': 'mean'}).sort_values(_watch_params).reset_index()
            groupby_param_res['model_name'] = model_name
            groupby_param_res['best_seed'] = best_seed_list
            groupby_param_res = groupby_param_res.rename({'n_estimators': 'num_boost_round'}, axis=1)
            groupby_param_res['config'] = config
            groupby_param_res['test_acc'] = (groupby_param_res['test_accuracy'] - 0.4) * 100
            res_df = pd.concat([res_df, groupby_param_res], axis=0)
        all_res_df = pd.concat([all_res_df, res_df], axis=0)

    all_res_df = all_res_df.reset_index(drop=True)
    FileUtil.save_df2xls(all_res_df, '/data/user/015614/junkData/', f'hyper2_res_{STRATEGY_VERSION}_{period}.xlsx')
    send_file(f'/data/user/015614/junkData/hyper2_res_{STRATEGY_VERSION}_{period}.xlsx')