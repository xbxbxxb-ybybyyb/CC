# coding: utf-8
# Author：fengchi863
# Date ：2023/11/24 13:04

import os
import json
import pandas as pd
from Zeus.Europa.v4_0_14.strat_conf import strategy_version
from Zeus.Europa.v4_0_14.path_conf import *

xgb_watch_params = ['eta', 'num_boost_round', 'max_depth', 'objective', 'seed']
lgb_watch_params = ['learning_rate', 'n_estimators', 'max_depth', 'seed']

if __name__ == '__main__':
    period = 'period6'
    date_dict = date_config[period]
    test_start_date = date_dict['test_start_date']
    test_end_date = date_dict['test_end_date']
    fit_start_date = date_dict['fit_start_date']
    fit_end_date = date_dict['fit_end_date']
    hyper_root_path = f'/data/user/015614/Zeus/pred/Europa/{strategy_version}/'
    model_names = os.listdir(hyper_root_path)
    pred_fpath_list = list()
    fit_fpath_list = list()
    output_dict = {}
    for model_name in model_names:
        model_param_list = []

        if not os.path.exists(hyper_root_path + model_name + f'/hyper/'):
            continue

        hyper_list = os.listdir(hyper_root_path + model_name + f'/hyper/')
        for search_time in hyper_list:
            if not os.path.exists(hyper_root_path + model_name + f'/hyper/{search_time}/bt_result.xlsx'):
                continue

            with open(hyper_root_path + model_name + f'/hyper/{search_time}/param.json', 'r') as f_obj:
                param = json.load(f_obj)
            if 'Xgb' in model_name:
                watch_params = xgb_watch_params
            if 'Lgb' in model_name:
                watch_params = lgb_watch_params

            bt_result_dict = pd.read_excel(hyper_root_path + model_name + f'/hyper/{search_time}/bt_result.xlsx', index_col=0, sheet_name=None)
            stats_df, model_test_mingan = bt_result_dict['汇总结果'].iloc[:,0], bt_result_dict['test']
            stats_df['累计扣费总收益'] /= 1e8
            stats_df['最大回撤'] /= 1e8
            stats_df['平均收益风险比'] = model_test_mingan['收益风险比'].mean()
            stats_df['平均收益夏普比率'] = model_test_mingan['收益夏普比率'].mean()
            stats_df = stats_df.map(lambda x: round(x, 2))
            stats_df['基础样本数量'] = int(stats_df['基础样本数量'])
            tmp_res = pd.Series({**{k:v for k, v in param.items() if k in watch_params}, **stats_df.to_dict()})
            model_param_list.append(tmp_res)

        model_param_res = pd.DataFrame(model_param_list).sort_values(watch_params)
        output_dict[model_name] = model_param_res
        if 'seed' in watch_params:
            watch_params.remove('seed')
        groupby_param_res = model_param_res.groupby(watch_params).agg({'累计扣费总收益': 'mean',
                                                                       '最大回撤': 'mean',
                                                                       '收益风险比': 'mean',
                                                                       '收益夏普比率': 'mean',
                                                                       '平均收益风险比': 'mean',
                                                                       '平均收益夏普比率': 'mean'}).sort_values(watch_params).reset_index()

        output_dict[f'stats_{model_name}'] = groupby_param_res

    from dataApi.sendInfo import send_file
    from LucienUtil.FileUtil import FileUtil
    FileUtil.save_dict2xls(output_dict, '/data/user/015614/junkData/', 'bt_res.xlsx')
    send_file('/data/user/015614/junkData/bt_res.xlsx')

    output_dict2 = dict()
    xgb_res_list = list()
    lgb_res_list = list()
    for stats_sheet in output_dict.keys():
        if 'Xgb' in stats_sheet and 'stats' in stats_sheet:
            res = output_dict[stats_sheet]
            res['model_name'] = stats_sheet.replace('stats_', '')
            xgb_res_list.append(res)
        if 'Lgb' in stats_sheet and 'stats' in stats_sheet:
            res = output_dict[stats_sheet]
            res['model_name'] = stats_sheet.replace('stats_', '')
            lgb_res_list.append(res)
    output_dict2['Xgb'] = pd.concat(xgb_res_list, axis=0).sort_values(xgb_watch_params).reset_index()
    output_dict2['Lgb'] = pd.concat(lgb_res_list, axis=0).sort_values(lgb_watch_params).reset_index()
    FileUtil.save_dict2xls(output_dict2, '/data/user/015614/junkData/', 'bt_res2.xlsx')
    send_file('/data/user/015614/junkData/bt_res2.xlsx')





