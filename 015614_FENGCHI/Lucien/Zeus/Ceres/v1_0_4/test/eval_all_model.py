# coding: utf-8
# Author：fengchi863
# Date ：2024/10/24 21:56

"""
根据所有模型的平均收益风险比进行打分、收益夏普比率进行打分、该区间的收益风险比进行打分
"""

import pandas as pd
import numpy as np

result_path = '/data/user/015614/junkData/'
period_list = ['period4', 'period5', 'period6', 'period7', 'period8']

res_dict = dict()

for period in period_list:
    tmp_res = pd.read_excel(result_path + f'v1_0_4_Ceres_{period}_汇总结果.xlsx')
    tmp_res['config'] = tmp_res['config'].fillna(method='ffill')
    tmp_res['model_name'] = tmp_res['config'] + '_' + tmp_res['model_name']
    tmp_res['平均收益风险比得分'] = tmp_res['平均收益风险比'].rank(pct=True)    # 得分越大越好
    tmp_res['收益风险比得分'] = tmp_res['收益风险比'].rank(pct=True)
    tmp_res['平均收益夏普比率得分'] = tmp_res['平均收益夏普比率'].rank(pct=True)
    tmp_res['收益夏普比率得分'] = tmp_res['收益夏普比率'].rank(pct=True)
    tmp_res['累计收益得分'] = tmp_res['累计扣费总收益'].rank(pct=True)

    res_dict[period] = tmp_res

# 汇总各个得分到一个表格里进行加权
indicator_dict = dict()
indicator_list = ['平均收益风险比得分', '收益风险比得分', '平均收益夏普比率得分', '收益夏普比率得分', '累计收益得分']
for indicator in indicator_list:
    tmp_res_list = list()
    for period in period_list:
        tmp_res = res_dict[period]
        tmp = tmp_res.set_index('model_name')[[indicator]]
        tmp.columns = [period]
        tmp_res_list.append(tmp)
    score_df = pd.concat(tmp_res_list, axis=1)
    score_df['各区间得分之和'] = score_df.sum(axis=1)
    indicator_dict[indicator] = score_df

tmp_list = list()
for indicator in indicator_list:
    tmp = indicator_dict[indicator]
    score_df = tmp[['各区间得分之和']]
    score_df.columns = [indicator]
    tmp_list.append(score_df)
check = pd.concat(tmp_list, axis=1)
check['得分之和'] = check.sum(axis=1)
indicator_dict['汇总'] = check


from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(indicator_dict, result_path, 'Ceres从第四区间开始得分.xlsx')
from dataApi.sendInfo import send_file
send_file(result_path + 'Ceres从第四区间开始得分.xlsx')
