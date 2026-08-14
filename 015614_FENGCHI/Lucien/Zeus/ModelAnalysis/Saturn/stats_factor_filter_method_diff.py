# coding: utf-8
# Author：fengchi863
# Date ：2022/9/20 20:50

import pandas as pd
from LucienUtil.FileUtil import FileUtil
from Zeus.Saturn.v3_0_15.path_conf import factor_path
from dataApi.sendInfo import send_file
from Zeus.Saturn.v3_0_17.path_conf import filter_factor_fpath # method5

filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)
emotion_factor_list = filter_factor.query('factor_owner == "emotion"')['factor_name'].tolist()

strategy_name = 'SaturnS1'
version = 'v3_0_15'
model_name = 'lgb_reg_model'

factor_list0 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_10/', 'factor_list.pkl')
factor_list1 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_13/', 'factor_list.pkl')
factor_list2 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_14/', 'factor_list.pkl')
factor_list3 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_15/', 'factor_list.pkl')
factor_list4 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_16/', 'factor_list.pkl')
factor_list5 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_17/', 'factor_list.pkl')

col_list = ['method0', 'method1', 'method2', 'method3', 'method4', 'method5']
res_df = pd.DataFrame(index=col_list, columns=col_list)
for idx1, met1 in enumerate(col_list):
    for idx2, met2 in enumerate(col_list):
        common_list = list(set(eval(f'factor_list{idx1}')).intersection(set(eval(f'factor_list{idx2}'))))
        res_df.loc[met1, met2] = len(common_list)

emotion_num = pd.DataFrame(index=col_list, columns=['emotion_num'])
for idx1, met1 in enumerate(col_list):
    emotion_num.loc[met1, 'emotion_num'] = len(set(eval(f'factor_list{idx1}')).intersection(emotion_factor_list))

res_df = res_df / 271
send_file(res_df)

