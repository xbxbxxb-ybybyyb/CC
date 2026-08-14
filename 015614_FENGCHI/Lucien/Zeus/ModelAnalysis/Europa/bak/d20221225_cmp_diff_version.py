# coding: utf-8
# Author：fengchi863
# Date ：2022/12/25 15:10

"""
将原来的区间的回测结果拼成新的结果
"""

import pandas as pd
PERIOD = 'period1'
SUB_VERSION = 'v1'  # v1 v2 v3

for model_name in ['LgbRegModel', 'XgbRegModel', 'LrRegModel']:
    root_path = f'/data/user/015614/Zeus/pred/Europa/v1_0_30/{model_name}/'
    pred_type = 'test'   # test fit
    from Zeus.Europa.v1_0_30.path_conf import date_config
    date_dict = date_config[f'{PERIOD}_{pred_type}']
    out_begin, out_end = date_dict['test_start_date'], date_dict['test_end_date']
    test_fpath = root_path + f'{out_begin}~{out_end}_{model_name}_{SUB_VERSION}.csv'

    pred_type = 'fit'   # test fit
    date_dict = date_config[f'{PERIOD}_{pred_type}']
    out_begin, out_end = date_dict['test_start_date'], date_dict['test_end_date']
    fit_fpath = root_path + f'{out_begin}~{out_end}_{model_name}_{SUB_VERSION}.csv'

    test_data = pd.read_csv(test_fpath, index_col=0)
    fit_data = pd.read_csv(fit_fpath, index_col=0)
    all_data = pd.concat([test_data, fit_data.query(f'datelist >= {out_begin} & datelist <= {out_end}')], axis=0).drop_duplicates()
    all_data.sort_index()

    from Zeus.Europa.v1_0_31.path_conf import date_config
    from LucienUtil.FileUtil import FileUtil
    pred_type = 'test'   # test fit
    date_dict = date_config[f'{PERIOD}_{pred_type}']
    out_begin, out_end = date_dict['test_start_date'], date_dict['test_end_date']
    new_test_data = all_data.query(f'datelist >= {out_begin} & datelist <= {out_end}')
    FileUtil.save_df2csv(new_test_data, root_path, f'{out_begin}~{out_end}_{model_name}_{SUB_VERSION}_v1031.csv')

    pred_type = 'fit'   # test fit
    date_dict = date_config[f'{PERIOD}_{pred_type}']
    out_begin, out_end = date_dict['test_start_date'], date_dict['test_end_date']
    new_fit_data = all_data.query(f'datelist >= {out_begin} & datelist <= {out_end}')
    FileUtil.save_df2csv(new_fit_data, root_path, f'{out_begin}~{out_end}_{model_name}_{SUB_VERSION}_v1031.csv')
    
"""开始对比"""
import pandas as pd
from tqdm import tqdm
from dataApi.sendInfo import send_file

#%% 第一块
# root_path = '/data/user/015614/shared/backtest_result/20221215回测结果_Europa_fac_20221116三个区间测试有无因子筛选的差别2/'
root_path = '/data/user/015614/junkData/回测结果/'
period1_test = '20191001~20200331_Europa_fac_20221116_FSV8_all_pct_graded_lowCost_period1_all_merge_test_模型评价_20221225.xlsx'
period1_fit = '20200401~20201231_Europa_fac_20221116_FSV8_all_pct_graded_lowCost_period1_all_merge_fit_模型评价_20221225.xlsx'
period2_test = '20200401~20200930_Europa_fac_20221116_FSV8_all_pct_graded_lowCost_period2_all_merge_test_模型评价_20221225.xlsx'
period2_fit = '20201001~20210630_Europa_fac_20221116_FSV8_all_pct_graded_lowCost_period2_all_merge_fit_模型评价_20221225.xlsx'
period3_test = '20201001~20210331_Europa_fac_20221116_FSV8_all_pct_graded_lowCost_period3_all_merge_test_模型评价_20221225.xlsx'
period3_fit = '20210401~20211231_Europa_fac_20221116_FSV8_all_pct_graded_lowCost_period3_all_merge_fit_模型评价_20221225.xlsx'
bt_res_fpath_list = [period1_test, period1_fit, period2_test, period2_fit, period3_test, period3_fit]
bt_res_name_list = ['period1_test', 'period1_fit', 'period2_test', 'period2_fit', 'period3_test', 'period3_fit']
filtered_model_list = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel', 'oldLgbV8FcModel', 'oldXgbV8FcModel', 'oldLrRSFcModel']

res_df = pd.DataFrame(index=pd.MultiIndex.from_product([bt_res_name_list, filtered_model_list]))
for bt_res_name in tqdm(bt_res_name_list):
    bt = pd.read_excel(root_path + eval(bt_res_name), index_col=0, sheet_name='模型结果')
    for filtered_model in filtered_model_list:
        res_df.loc[(bt_res_name, filtered_model), '基础样本数量'] = bt.loc['基础样本数量', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '组合标签胜率'] = bt.loc['组合标签胜率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '扣费后收益率胜率'] = bt.loc['扣费后收益率胜率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '样本参与率'] = bt.loc['样本参与率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '实际参与次数'] = bt.loc['实际参与次数', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '累计扣费总收益'] = bt.loc['累计扣费总收益', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '最大回撤'] = bt.loc['最大回撤', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益风险比'] = bt.loc['收益风险比', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '夏普比率'] = bt.loc['夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益夏普比率'] = bt.loc['收益夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签IC'] = bt.loc['预测值与标签IC', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签RankIC'] = bt.loc['预测值与标签RankIC', filtered_model]

check = pd.concat([res_df.T], axis=1).T
send_file(check)