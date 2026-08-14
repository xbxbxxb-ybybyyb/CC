# coding: utf-8
# Author：fengchi863
# Date ：2024/6/6 9:47

import pandas as pd
from Zeus.Europa.v4_0_61.path_conf import *
from Zeus.Europa.v4_0_60.submit_model.infer import *
from Zeus.Europa.v4_0_61.backtest.sim_backtest.SimBackTest import SimBackTest


PERIOD = 'period7'
root_dir = f'/data/user/015614/shared/for_wj/strategy_model/Europa/fac_20240531/区间{PERIOD[-1]}/'
model_name_list = os.listdir(root_dir)

stats_df_list = list()
for model_name in model_name_list:
    print(model_name)
    data_fpath = data_all_fpath
    model_dir = root_dir + model_name + '/'
    datapro_file = model_dir + 'Model_factorScaler.json'
    factor_list_file = model_dir + 'Model_factorName.json'
    threshold_file = model_dir + 'Model_config.json'
    # model_file = model_dir + 'model_seed0.pkl'
    model_file = model_dir + 'model_seed0.pkl'
    begin_date = date_config[PERIOD]["fit_start_date"]
    end_date = date_config[PERIOD]["fit_end_date"]
    data_df = pd.read_pickle(data_fpath)
    result, scaled_df = infer(data_df, factor_list_file, model_file, begin_date, end_date, threshold_file, datapro_file=datapro_file)

    # 转换格式
    result['prediction'] = result['prediction'].astype(bool)
    result['stockID'] = result.index.get_level_values(1).tolist()
    result['datelist'] = result.index.get_level_values(0).map(lambda x: x.strftime("%Y%m%d"))
    result['Indexs'] = result[['stockID', 'datelist']].apply(lambda x: x['stockID'] + ' ' + x['datelist'], axis=1)
    result = result.set_index('Indexs', drop=True)
    result.to_csv(model_dir + f'{date_config[PERIOD]["fit_start_date"]}~{date_config[PERIOD]["fit_end_date"]}_.csv')

    # 开始回测
    sbt = SimBackTest(pred_fpath_list=[model_dir + f'{date_config[PERIOD]["test_start_date"]}~{date_config[PERIOD]["test_end_date"]}_.csv'],
                      fit_fpath_list=[model_dir + f'{date_config[PERIOD]["fit_start_date"]}~{date_config[PERIOD]["fit_end_date"]}_.csv'],
                      date_dict=date_config[PERIOD],
                      attend_ratio_range=(20, 50),
                      save_flag=True,
                      multi_attend=True)
    stats_df, model_test_mingan, model_fit_mingan = sbt.start_backtest(multi=False)
    stats_df['累计扣费总收益'] /= 1e8
    stats_df['最大回撤'] /= 1e8
    stats_df['平均收益风险比'] = model_test_mingan['收益风险比'].mean()
    stats_df['平均收益夏普比率'] = model_test_mingan['收益夏普比率'].mean()
    stats_df['fit平均累计收益'] = model_fit_mingan['累计盈利'].mean()
    stats_df['fit平均收益风险比'] = model_fit_mingan['收益风险比'].mean()
    stats_df['fit平均收益夏普比率'] = model_fit_mingan['收益夏普比率'].mean()
    stats_df = stats_df.map(lambda x: round(x, 2))
    stats_df['基础样本数量'] = int(stats_df['基础样本数量'])
    print(stats_df[['收益风险比', '收益夏普比率', '平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '最大回撤', '预测值与标签RankIC', '基础样本数量', '扣费后收益率胜率']].to_dict())
    stats_df_list.append(stats_df)
stats_df = pd.concat(stats_df_list, axis=1)
stats_df.columns = model_name_list
print(stats_df)