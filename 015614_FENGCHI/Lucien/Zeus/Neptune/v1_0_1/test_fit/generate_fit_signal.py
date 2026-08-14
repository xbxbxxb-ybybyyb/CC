# coding: utf-8
# Author：fengchi863
# Date ：2024/11/13 11:25

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil

period_list = ['period4_fit', 'period5_fit', 'period6_fit', 'period7_fit']
indicator1_list = ['平均收益风险比', '平均收益夏普比率', '累计扣费总收益', '收益风险比', '夏普比率', '收益夏普比率']
indicator2_list = ['累计扣费总收益', '平均收益风险比', '平均收益夏普比率']
best_indicator = ['累计扣费总收益']

res1 = pd.DataFrame(index=period_list)
res2 = pd.DataFrame(index=period_list)

test_fit_res = pd.read_excel(f'/data/user/015614/junkData/hyper_Neptune_v1_0_1_{period_list[0]}.xlsx', sheet_name='最佳表现')
model_list = (test_fit_res['config_flag'] + '_' + test_fit_res['model_name']).tolist()
res3 = pd.DataFrame(index=model_list, columns=period_list)

for indicator1 in indicator1_list:
    for indicator2 in indicator2_list:
        for period in period_list:
            test_fit_res = pd.read_excel(f'/data/user/015614/junkData/hyper_Neptune_v1_0_1_{period}.xlsx', sheet_name='最佳表现')
            res1.loc[period, f'{indicator1}_vs_{indicator2}_fit'] = np.corrcoef(test_fit_res[indicator1], test_fit_res[f'{indicator2}_fit'])[0, 1]
            res2.loc[period, f'{indicator1}_vs_{indicator2}_fit'] = spearmanr(test_fit_res[indicator1], test_fit_res[f'{indicator2}_fit'])[0]
            test_fit_res['index'] = test_fit_res['config_flag'] + '_' + test_fit_res['model_name']
            test_fit_res = test_fit_res.set_index('index')
            res3.loc[model_list, period] = test_fit_res[best_indicator].reindex(model_list).rank().values[:, 0]  # 排名第一得分最高
res1 = res1.T
res2 = res2.T
res = {'相关性': res1,
       '秩相关性': res2,
       '各区间模型排名': res3}
FileUtil.save_dict2xls(res, '/data/user/015614/junkData/', '模型相关性测试_临时.xlsx')
send_file('/data/user/015614/junkData/模型相关性测试_临时.xlsx')