# coding: utf-8
# Author：fengchi863
# Date ：2023/11/24 13:04

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

import json
import os
import pandas as pd
from Zeus.Europa.v4_0_84.config.strat_conf import *
from Zeus.Europa.v4_0_84.config.path_conf import *
from Zeus.Europa.v4_0_84.scripts.hyper_param_space import xgb_fixed_params, lgb_fixed_params

# 防止query的时候触发关键字，lambda需要特殊处理
xgb_watch_params = ['eta', 'num_boost_round', 'max_depth', 'colsample_bytree', 'alpha', 'lambda', 'subsample', 'seed']
lgb_watch_params = ['learning_rate', 'n_estimators', 'max_depth', 'colsample_bytree', 'reg_alpha', 'reg_lambda', 'min_child_weight', 'subsample', 'seed']

if __name__ == '__main__':
    period = PERIOD
    date_dict = [period]
    test_start_date = DATE_CONFIG['test_start_date']
    test_end_date = DATE_CONFIG['test_end_date']
    fit_start_date = DATE_CONFIG['fit_start_date']
    fit_end_date = DATE_CONFIG['fit_end_date']
    hyper_root_path = f'/data/user/015614/Zeus/pred/Europa/{STRATEGY_VERSION}/'
    model_names = os.listdir(hyper_root_path)
    pred_fpath_list = list()
    fit_fpath_list = list()
    output_dict = {}
    for model_name in model_names:
        if 'Xgb' in model_name:
            watch_params = xgb_watch_params
        if 'Lgb' in model_name:
            watch_params = lgb_watch_params

        model_param_list = []

        if not os.path.exists(hyper_root_path + model_name + f'/hyper/'):
            continue

        hyper_list = os.listdir(hyper_root_path + model_name + f'/hyper/')
        for search_time in hyper_list:
            if not os.path.exists(hyper_root_path + model_name + f'/hyper/{search_time}/bt_result.xlsx'):
                continue

            with open(hyper_root_path + model_name + f'/hyper/{search_time}/param.json', 'r') as f_obj:
                param = json.load(f_obj)

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
    # send_file('/data/user/015614/junkData/bt_res.xlsx')

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
    if len(xgb_res_list) > 0:
        xgb_group_res = pd.concat(xgb_res_list, axis=0).sort_values(xgb_watch_params).reset_index()
        xgb_group_res = xgb_group_res.rename({'lambda': 'lambdaa'}, axis=1)
        output_dict2['Xgb'] = xgb_group_res
    if len(lgb_res_list) > 0:
        lgb_group_res = pd.concat(lgb_res_list, axis=0).sort_values(lgb_watch_params).reset_index()
        lgb_group_res = lgb_group_res.replace({'lambda': 'lambdaa'})
        output_dict2['Lgb'] = lgb_group_res

    xgb_fixed_params = {('lambdaa' if k == 'lambda' else k): v for k, v in xgb_fixed_params.items()}
    lgb_fixed_params = {('lambdaa' if k == 'lambda' else k): v for k, v in lgb_fixed_params.items()}
    xgb_model_name_list = output_dict2['Xgb']['model_name'].unique().tolist()
    # lgb_model_name_list = output_dict2['Lgb']['model_name'].unique()

    for _, model_name in enumerate(xgb_model_name_list):
        # 更换部分关键字
        if 'Xgb' in model_name:
            watch_params = xgb_watch_params
        if 'Lgb' in model_name:
            watch_params = lgb_watch_params
        if 'lambda' in watch_params:
            watch_params = [x if x != 'lambda' else 'lambdaa' for x in watch_params]

        row_num = len(watch_params)  # ['累计扣费总收益', '最大回撤', '收益风险比', '平均收益风险比', '收益夏普比率', '平均收益夏普比率']
        col_num = 6
        fig, axes = plt.subplots(nrows=row_num, ncols=col_num, figsize=(col_num * 20, row_num * 10))

        model_bt_res = output_dict2['Xgb'].query(f'model_name == "{model_name}"')
        for idx1, watch_param in enumerate(watch_params):
            xgb_fixed_params_copy = xgb_fixed_params.copy()
            xgb_fixed_params_copy.pop(watch_param)
            expr_list = list()
            for k, v in xgb_fixed_params_copy.items():
                if k in watch_params:
                    expr_list += [f'{k}=={v}' if type(v) != str else f'"{k}"=="{v}"']
            query_expr = '&'.join(expr_list)
            tmp_model_bt_res = model_bt_res.query(query_expr)
            for idx2, bt_indi in enumerate(['累计扣费总收益', '最大回撤', '收益风险比', '平均收益风险比', '收益夏普比率', '平均收益夏普比率']):
                ax = axes[idx1, idx2]
                tmp_model_bt_res[[watch_param, bt_indi]].set_index(watch_param).plot(ax=ax)
        plt.savefig(f'/data/user/015614/junkData/hyper_compare_{model_name}.png', bbox_inches='tight', pad_inches=0.1)

    # for _, model_name in enumerate(lgb_model_name_list):
    #     # 更换部分关键字
    #     if 'Xgb' in model_name:
    #         watch_params = xgb_watch_params
    #     if 'Lgb' in model_name:
    #         watch_params = lgb_watch_params
    #     if 'lambda' in watch_params:
    #         watch_params = [x if x != 'lambda' else 'lambdaa' for x in watch_params]
    #
    #     row_num = len(watch_params)  # ['累计扣费总收益', '最大回撤', '收益风险比', '平均收益风险比', '收益夏普比率', '平均收益夏普比率']
    #     col_num = 6
    #     fig, axes = plt.subplots(nrows=row_num, ncols=col_num, figsize=(col_num * 20, row_num * 10))
    #
    #     model_bt_res = output_dict2['Lgb'].query(f'model_name == "{model_name}"')
    #     for idx1, watch_param in enumerate(watch_params):
    #         lgb_fixed_params_copy = lgb_fixed_params.copy()
    #         lgb_fixed_params_copy.pop(watch_param)
    #         expr_list = list()
    #         for k, v in lgb_fixed_params_copy.items():
    #             if k in watch_params:
    #                 expr_list += [f'{k}=={v}' if type(v) != str else f'"{k}"=="{v}"']
    #         query_expr = '&'.join(expr_list)
    #         tmp_model_bt_res = model_bt_res.query(query_expr)
    #         for idx2, bt_indi in enumerate(['累计扣费总收益', '最大回撤', '收益风险比', '平均收益风险比', '收益夏普比率', '平均收益夏普比率']):
    #             ax = axes[idx1, idx2]
    #             tmp_model_bt_res[[watch_param, bt_indi]].set_index(watch_param).plot(ax=ax)
    #     plt.savefig(f'/data/user/015614/junkData/hyper_compare_{model_name}.png', bbox_inches='tight', pad_inches=0.1)

    FileUtil.save_dict2xls(output_dict2, '/data/user/015614/junkData/', 'bt_res2.xlsx')
    send_file('/data/user/015614/junkData/bt_res2.xlsx')





