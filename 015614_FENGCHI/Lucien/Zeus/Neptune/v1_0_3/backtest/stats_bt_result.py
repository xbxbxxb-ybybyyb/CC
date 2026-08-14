# coding: utf-8
# Author：fengchi863
# Date ：2025/4/1 13:31

import os
import re
import json
import pandas as pd
from Zeus.Neptune.v1_0_3.scripts.hyper_param_space import hyper_xgb_reg_params_space
from Zeus.Neptune.v1_0_3.config.strat_conf import DATE_CONFIG, STRATEGY_NAME, STRATEGY_VERSION
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil

result_path = '/data/user/015614/Zeus/pred/Neptune/v1_0_3/'
# period = 'period7_fit'
period = 'period1'

watch_params = list(hyper_xgb_reg_params_space[0][idx][0] for idx in range(len(hyper_xgb_reg_params_space[0])))

def get_best_score_and_param():
    return

def get_all_result():
    res_df = pd.DataFrame()
    test_start_date = DATE_CONFIG[period]['test_start_date']
    test_end_date = DATE_CONFIG[period]['test_end_date']
    fit_start_date = DATE_CONFIG[period]['fit_start_date']
    fit_end_date = DATE_CONFIG[period]['fit_end_date']
    for dirpath, dirnames, filenames in os.walk(result_path):
        for filename in filenames:
            if 'bt_result' in filename and 'hyper' in dirpath and 'roll' not in dirpath and period in dirpath:
                bt_result_dict = pd.read_excel(dirpath + '/' + f'bt_result_{period}.xlsx', index_col=0, sheet_name=None)
                stats_df, model_test_mingan = bt_result_dict['汇总结果'].iloc[:, 0], bt_result_dict['test']
                stats_df['累计扣费总收益'] /= 1e8
                stats_df['最大回撤'] /= 1e8
                stats_df['平均收益风险比'] = model_test_mingan['收益风险比'].mean()
                stats_df['平均收益夏普比率'] = model_test_mingan['收益夏普比率'].mean()
                stats_df = stats_df.map(lambda x: round(x, 2))
                stats_df['基础样本数量'] = int(stats_df['基础样本数量'])

                with open(dirpath + '/' + f'train_result_{period}.json', 'r') as f_obj:
                    train_result = json.load(f_obj)
                train_result = pd.DataFrame(train_result).fillna('nan')

                stats_df['train_accuracy'] = train_result.loc[2, 1]
                stats_df['test_accuracy'] = train_result.loc[0, 1]

                with open(dirpath + '/' + 'param.json', 'r') as f_obj:
                    param = json.load(f_obj)

                tmp_res = pd.Series({**{k: v for k, v in param.items() if k in watch_params}, **stats_df.to_dict()})

                config_flag = f'config{re.findall(r"config(.*?)/", dirpath)[0]}'
                model_name = f'{re.findall(r"/(.*?)Xgb", dirpath)[0]}Xgb'.split('/')[-1]
                str_param = str(param)
                hyper_idx = dirpath.split('/')[-1]
                tmp_res['config_flag'] = config_flag
                tmp_res['model_name'] = model_name
                tmp_res['str_param'] = str_param
                tmp_res['hyper_idx'] = hyper_idx
                res_df = pd.concat([res_df, tmp_res], axis=1, sort=False)

    res_df = res_df.T.reset_index()
    group_df = res_df.groupby(['config_flag', 'model_name']).apply(lambda x: x.sort_values('test_accuracy', ascending=False))
    group_df = group_df.drop(['config_flag', 'model_name'], axis=1).reset_index(drop=True)

    # 保存按规则排序后的第一名的参数，并生成最好的相关性
    group_best_df = res_df.groupby(['config_flag', 'model_name']).apply(lambda x: x.sort_values('test_accuracy', ascending=False).head(1))
    group_best_df = group_best_df.drop(['config_flag', 'model_name'], axis=1).reset_index()
    pred_df = pd.DataFrame()
    for idx in range(len(group_best_df)):
        row = group_best_df.iloc[idx]
        hyper_idx = row['hyper_idx']
        str_param = row['str_param']
        config_flag = row['config_flag']
        model_name = row['model_name']

        # 将最佳参数保存到对应路径，供训练读取
        best_dir_path = os.path.join(result_path, config_flag, model_name, period, 'hyper/')
        best_params = {'best_hyper_idx': hyper_idx, 'best_param': str_param}
        with open(os.path.join(result_path, config_flag, model_name, period, 'hyper/') + f'best_params.json', 'w') as f:
            json.dump(best_params, f, ensure_ascii=False)

        tmp_pred_df = pd.read_csv(best_dir_path + hyper_idx + f'/{test_start_date}~{test_end_date}.csv')
        tmp_pred_df[f'{config_flag}_{model_name}'] = tmp_pred_df['pred_Reg']
        pred_df = pd.concat([pred_df, tmp_pred_df[f'{config_flag}_{model_name}']], axis=1)

    corr_df = pred_df.corr()

    res_dict = {
        '各参数表现': group_df,
        '最佳表现': group_best_df,
        '最佳之间的相关性': corr_df,
    }

    FileUtil.save_dict2xls(res_dict, '/data/user/015614/junkData/', f'hyper_{STRATEGY_NAME}_{STRATEGY_VERSION}_{period}.xlsx')
    send_file(f'/data/user/015614/junkData/hyper_{STRATEGY_NAME}_{STRATEGY_VERSION}_{period}.xlsx')


if __name__ == '__main__':
    get_all_result()