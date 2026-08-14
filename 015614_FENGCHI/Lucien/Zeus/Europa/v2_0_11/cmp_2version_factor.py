# coding: utf-8
# Author：fengchi863
# Date ：2023/3/23 11:20

import pandas as pd
from LucienUtil.FileUtil import FileUtil
from Zeus.Europa.v2_0_11.path_conf import *

"""
三种可能影响：
1、新增加的剔除的低耗时因子（测试不出来，因为不知道哪些是由于低耗时加入的）
2、新加入的T-1日因子影响
3、新加入的emotion因子影响
4、新加入的所有因子影响
先把这三类因子列表都算出来，保存起来，然后对于新增加的剔除因子，进行补充，对于新加入的因子，进行减少
在一个模型上测试即可
"""

factor_score_df = pd.read_excel(factor_score_fpath)
new_factor = factor_score_df.query('factor_date > 20221116')    # 相对于20221116实盘版本
# time_cost_df = pd.read_excel('/data/group/800463/sunss/europa/20230317/europa策略低耗时列表.xlsx')

new_factor_list = new_factor['factor_name'].tolist()
new_factor_t1_list = new_factor.query('factor_type == "T-1_factor"')['factor_name'].tolist()
new_factor_emotion_list = new_factor.loc[new_factor['factor_owner'].map(lambda x: x.startswith('emotion'))]['factor_name'].tolist()

FileUtil.save_list2pkl(new_factor_list, factor_select_path, 'new_factor_list.pkl')
FileUtil.save_list2pkl(new_factor_t1_list, factor_select_path, 'new_factor_t1_list.pkl')
FileUtil.save_list2pkl(new_factor_emotion_list, factor_select_path, 'new_factor_emotion_list.pkl')
