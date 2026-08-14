# coding: utf-8
# Author：fengchi863
# Date ：2023/8/10 14:51

"""
对比和FSV8、FSV10、FSV11的因子筛选结果
"""

from Zeus.Europa.v2_0_18.path_conf import *
import pandas as pd
import numpy as np
from tscv import GapWalkForward
from LucienUtil.FileUtil import FileUtil
from tqdm import tqdm
import time
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

factor_score = pd.read_excel(factor_score_fpath, index_col=0)

top_num = 240
PERIOD = 'period5'
fsv8 = pd.read_excel(eval(f'xgb_imptc_{PERIOD}_fpath'), index_col=0)
top50_fsv8 = fsv8.iloc[:top_num]
top50_fsv8_list = top50_fsv8['factor_name'].tolist()
fsv10 = pd.read_excel(eval(f'xgb_imptc_fsv10_{PERIOD}_fpath'), index_col=0)
top50_fsv10 = fsv10.iloc[:top_num]
top50_fsv10_list = top50_fsv10['factor_name'].tolist()
fsv11 = pd.read_excel(eval(f'xgb_imptc_fsv11_{PERIOD}_fpath'), index_col=0)
top50_fsv11 = fsv11.iloc[:top_num]
top50_fsv11_list = top50_fsv11['factor_name'].tolist()

rffs_weight = pd.read_pickle('/data/user/015614/Zeus/factor_select/Europa/v2_0_18/tmp_rf_cv_score_period5_test1_default.pkl')
top50_rffs_weight = rffs_weight.sort_values('mean', ascending=False).iloc[:top_num].index.tolist()

new_gain_factors = pd.read_pickle('/data/user/015614/Zeus/factor_select/Europa/v2_0_18/tmp_rf_cv_score_period5_test1.pkl')
new_gain_factors = new_gain_factors.sort_values('mean', ascending=False).iloc[:top_num].index.tolist()

res = pd.DataFrame(index=['fsv8', 'fsv10', 'fsv11', 'rffs_gain_list', 'rffs_weight_list'])
res['与new_factor_test交集数量'] = [len(set(top50_fsv8_list).intersection(set(new_gain_factors))),\
                                   len(set(top50_fsv10_list).intersection(set(new_gain_factors))),\
                                  len(set(top50_fsv11_list).intersection(set(new_gain_factors))),\
                                  len(new_gain_factors),
                                  len(set(top50_rffs_weight).intersection(set(new_gain_factors))),]
res['情绪因子个数'] = [top50_fsv8.query('factor_owner == "emotion" or factor_owner == "emotion_time"').shape[0],
                 top50_fsv10.query('factor_owner == "emotion" or factor_owner == "emotion_time"').shape[0],
                 top50_fsv11.query('factor_owner == "emotion" or factor_owner == "emotion_time"').shape[0],
                 factor_score.query(f'factor_name in {new_gain_factors}').query('factor_owner == "emotion" or factor_owner == "emotion_time"').shape[0],
                 factor_score.query(f'factor_name in {top50_rffs_weight}').query('factor_owner == "emotion" or factor_owner == "emotion_time"').shape[0]]
res.to_excel('/data/user/015614/junkData/20230817未成交强势股分析.xlsx')
from dataApi.sendInfo import send_file
send_file(res)

"""需要让sss补充的因子"""
factor_df = pd.read_factor('')

