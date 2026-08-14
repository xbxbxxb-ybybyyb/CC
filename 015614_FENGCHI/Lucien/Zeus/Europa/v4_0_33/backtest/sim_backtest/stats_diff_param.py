# coding: utf-8
# Author：fengchi863
# Date ：2024/3/18 13:11

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

import pandas as pd
from Zeus.Europa.v4_0_33.strat_conf import strategy_version, strategy_name
from Zeus.Europa.v4_0_33.path_conf import *

if __name__ == '__main__':
    period = 'period7'
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
    model_res = pd.DataFrame(columns=['基础样本数量',
                                     '扣费后收益率胜率',
                                     '样本参与率',
                                     '实际参与次数',
                                     '累计扣费总收益',
                                     '最大回撤',
                                     '收益风险比',
                                     '夏普比率',
                                     '收益夏普比率',
                                     '预测值与标签IC',
                                     '预测值与标签RankIC',
                                     '平均收益风险比',
                                     '平均收益夏普比率'])
    for model_name in model_names:

        if not os.path.exists(hyper_root_path + model_name + f'/bt_result.xlsx'):
            continue

        bt_result_dict = pd.read_excel(hyper_root_path + model_name + f'/bt_result.xlsx', index_col=0, sheet_name=None)
        stats_df, model_test_mingan = bt_result_dict['汇总结果'].iloc[:,0], bt_result_dict['test']
        stats_df['累计扣费总收益'] /= 1e8
        stats_df['最大回撤'] /= 1e8
        stats_df['平均收益风险比'] = model_test_mingan['收益风险比'].mean()
        stats_df['平均收益夏普比率'] = model_test_mingan['收益夏普比率'].mean()
        stats_df = stats_df.map(lambda x: round(x, 2))
        stats_df['基础样本数量'] = int(stats_df['基础样本数量'])
        tmp_res = pd.Series(stats_df.to_dict())

        model_res.loc[model_name, :] = tmp_res.T
    output_dict['汇总结果'] = model_res

    from dataApi.sendInfo import send_file
    from LucienUtil.FileUtil import FileUtil
    FileUtil.save_dict2xls(output_dict, '/data/user/015614/junkData/', f'{strategy_version}_{strategy_name}.汇总结果.xlsx')
    send_file(f'/data/user/015614/junkData/{strategy_version}_{strategy_name}.汇总结果.xlsx')