# coding: utf-8
# Author：fengchi863
# Date ：2023/7/17 19:26

from Zeus.Europa.v4_0_73.path_conf import *
from dataApi.sendInfo import send_file
from LucienUtil.FileUtil import FileUtil
import pandas as pd
import numpy as np
import math

PERIOD = 'period1'
pred_type = 'test'
pred_fpath = '/data/user/015614/Zeus/pred/Europa/v4_0_73/rffs_XgbRegModel/hyper/1/20191001~20200331_rffs_XgbRegModel_v1.csv'

PERIOD_list = ['period1', 'period1', 'period2', 'period2', 'period3', 'period3']
pred_type_list = ['test', 'fit', 'test', 'fit', 'test', 'fit']
period_list = [(PERIOD_list[i] + '_' + pred_type_list[i]) for i in range(len(PERIOD_list))]

model_list = ['fsv8_pct1_XgbRegModel', 'fsv10_pct1_XgbRegModel', 'fsv11_pct1_XgbRegModel', 'fsrs_pct1_XgbRegModel',
    'fsv8_pct1_LgbRegModel', 'fsv10_pct1_LgbRegModel', 'fsv11_pct1_LgbRegModel', 'fsrs_pct1_LgbRegModel',
    'fsv8_pct_XgbRegModel', 'fsv10_pct_XgbRegModel', 'fsv11_pct_XgbRegModel', 'fsrs_pct_XgbRegModel',
    'fsv8_pct_LgbRegModel', 'fsv10_pct_LgbRegModel', 'fsv11_pct_LgbRegModel', 'fsrs_pct_LgbRegModel',]

mean_df = pd.DataFrame(index=pd.MultiIndex.from_product([period_list, model_list]))
for model in model_list:
    print(model)
    # res_dict = pd.read_excel(f'/data/user/015614/junkData/{model}_addBuy.xlsx', sheet_name=None, index_col=0)
    res_dict = pd.read_excel(f'/data/user/015614/junkData/{model}.xlsx', sheet_name=None, index_col=0)
    for period in res_dict.keys():
        period_res = res_dict[period]
        mean_df.loc[(period, model), '平均累计收益'] = period_res['累计收益'].mean()
        mean_df.loc[(period, model), '平均收益率'] = period_res['平均收益率'].mean()
        mean_df.loc[(period, model), '平均最大回撤'] = period_res['最大回撤'].mean()
        mean_df.loc[(period, model), '平均收益风险比'] = period_res['收益风险比'].mean()
        mean_df.loc[(period, model), '平均夏普比率'] = period_res['夏普比率'].mean()
        mean_df.loc[(period, model), '平均收益夏普比率'] = period_res['收益夏普比率'].mean()

send_file(mean_df)



