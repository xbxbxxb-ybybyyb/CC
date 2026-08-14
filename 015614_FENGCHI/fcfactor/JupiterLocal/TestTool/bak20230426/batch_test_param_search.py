# coding: utf-8
# Author：fengchi863
# Date ：2023/3/22 10:40

from JupiterLocal.TestTool.test1_factor_demo import strongFactorTest
from JupiterLocal.TestTool.run_factor_demo import run_factor
import os
import pandas as pd
import importlib
from tqdm import tqdm
from sendInfo import send_file

factor_name_list = list(map(lambda x: x[7: -3], os.listdir('/data/user/015614/fcfactor/JupiterLocal/d20230322/')))
basic_file_path = '/data/group/800463/data/project1_public/factor_lib/Basic_zt_001.h5'
res_path = '/data/user/015614/factor/'

bt_columns = ['nan_num', 'value_diff_score', 'value_stability_score', 'mixed_diff_score',
              'mixed_stability_score', 'score', 'corr_tot', 'mic_tot', 'high_corr_factor', 'high_corr_factor_corr']
res_df = pd.DataFrame(columns=bt_columns)

# def func():
#     factor_df =

for factor_name in tqdm(factor_name_list):
    # 生成
    try:
        start_date, end_date = 20160101, 20181231

        # 生成factor_df
        factor_df = run_factor(func, factor_name, 'TTransaction', start_date, end_date, basic_file_path, res_path, interval_res=False)

        # 回测
        sft = strongFactorTest(start_date, end_date)
        res_dict = sft.factor_test(factor_df, result_path=res_path, factor_corr_test=True, generate_pdf=True)

        nan_num = res_dict['factor_information'].loc['Nan|Inf Count', 'Factor Info']
        value_diff_score= res_dict['check_score_res'].loc['score', 'value_diff_score']
        value_stability_score= res_dict['check_score_res'].loc['score', 'value_stability_score']
        mixed_diff_score = res_dict['check_score_res'].loc['score', 'mixed_diff_score']
        mixed_stability_score = res_dict['check_score_res'].loc['score', 'mixed_stability_score']
        score = res_dict['check_score_res'].loc['score', 'tot_score']
        corr_tot = res_dict['corr_sta'].loc['corr_tot', 'value']
        mic_tot = res_dict['corr_sta'].loc['mic_tot', 'value']

        high_corr_s = res_dict['factor_corr'].query('factor_corr >= 0.7')
        if len(high_corr_s) == 0:
            high_corr_s = res_dict['factor_corr'].iloc[:2]
        else:
            high_corr_s = res_dict['factor_corr'].iloc[:len(high_corr_s) + 2]

        high_corr_factor_list_str = '，'.join(high_corr_s.index.tolist())
        high_corr_factor_corr_list_str = '，'.join(high_corr_s['factor_corr'].map(lambda x: round(x ,4)).map(str).tolist())

        res_df.loc[factor_name] = [nan_num, value_diff_score, value_stability_score,
                                   mixed_diff_score, mixed_stability_score, score, corr_tot, mic_tot, high_corr_factor_list_str, high_corr_factor_corr_list_str]
        print(f'{factor_name}测试成功')
    except Exception as e:
        print(e)
        print('error_factor_list：', factor_name)

send_file(res_df)