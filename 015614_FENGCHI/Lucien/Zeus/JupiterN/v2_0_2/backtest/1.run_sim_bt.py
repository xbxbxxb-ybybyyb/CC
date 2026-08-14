# coding: utf-8
# Author：fengchi863
# Date ：2023/11/24 10:04

import os
from Zeus.JupiterN.v2_0_2.config.strat_conf import *
from Zeus.JupiterN.v2_0_2.config.path_conf import *
import pandas as pd
from LucienUtil.FileUtil import FileUtil
from Zeus.JupiterN.v2_0_2.backtest.SimBackTest import SimBackTest

def calc_stats_df(stats_df, stats_df2, model_test_mingan, model_fit_mingan):
    stats_df['平均收益风险比'] = model_test_mingan['收益风险比'].mean()
    stats_df['平均收益夏普比率'] = model_test_mingan['收益夏普比率'].mean()
    stats_df['累计扣费总收益'] /= 1e8
    stats_df['最大回撤'] /= 1e8
    # stats_df = stats_df.map(lambda x: round(x, 2))
    stats_df['基础样本数量'] = int(stats_df['基础样本数量'])
    # stats_df['因子数量'] = len(inst.factor_list)

    stats_df2['平均收益风险比'] = model_fit_mingan['收益风险比'].mean()
    stats_df2['平均收益夏普比率'] = model_fit_mingan['收益夏普比率'].mean()
    stats_df2['累计扣费总收益'] /= 1e8
    stats_df2['最大回撤'] /= 1e8
    stats_df = stats_df.map(lambda x: round(x, 2))
    stats_df2['基础样本数量'] = int(stats_df2['基础样本数量'])

    print(stats_df[['收益风险比', '收益夏普比率', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '预测值与标签IC', '扣费后收益率胜率', '基础样本数量']].to_dict())
    stats_df = stats_df[['基础样本数量', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '样本参与率', '收益风险比', '夏普比率', '收益夏普比率', '预测值与标签IC']]
    stats_df2 = stats_df2[['基础样本数量', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '样本参与率', '收益风险比', '夏普比率', '收益夏普比率', '预测值与标签IC']]
    stats_df2 = stats_df2.rename(dict(zip(stats_df2.index.tolist(), [x + '_fit' for x in stats_df2.index])))

    stats_df = pd.concat([stats_df, stats_df2])
    output_dict = {'汇总结果': stats_df, 'test': model_test_mingan, 'fit': model_fit_mingan}
    return output_dict

if __name__ == '__main__':
    period = 'period2'
    date_dict = DATE_CONFIG[period]
    hyper_search_mode = 0
    test_start_date = date_dict['test_start_date']
    test_end_date = date_dict['test_end_date']
    fit_start_date = date_dict['fit_start_date']
    fit_end_date = date_dict['fit_end_date']
    config_list = ['config1', 'config2', 'config35', 'config46']
    for config in config_list:
        hyper_root_path = f'/data/user/015614/Zeus/pred/JupiterN/{STRATEGY_VERSION}/{config}/'
        model_names = os.listdir(hyper_root_path)
        # model_names = list(filter(lambda x: 'Cross' in x, model_names))
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

        import importlib
        module_name = f'Zeus.JupiterN.v2_0_2.config.path_conf'
        module = importlib.import_module(module_name)
        if config[-2:] in ['35', '46']:
            tmp_config = config[:-1]
            PT = getattr(module, tmp_config)
        else:
            PT = getattr(module, config)

        label = PT['label']
        data_fpath = PT['data_fpath']
        profit_data_fpath = PT['profit_data_fpath']
        sbt = SimBackTest(pred_fpath_list=pred_fpath_list,
                          fit_fpath_list=fit_fpath_list,
                          data_fpath=data_fpath,
                          profit_data_fpath=profit_data_fpath,
                          date_dict=DATE_CONFIG[period],
                          period=period,
                          attend_ratio_range=(20, 50),
                          save_flag=True,
                          multi_attend=True)
        sbt.start_backtest(multi=False)