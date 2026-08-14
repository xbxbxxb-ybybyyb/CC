# coding: utf-8
# Author：fengchi863
# Date ：2020/3/27 15:16

from dataApi.indName import *
from dataApi.getData import *
import numpy as np, pandas as pd

ind = get_daily_1factor('SW1').iloc[-1]
code_ind_dict = ind.to_dict()
sw1_dict = dict()
for sw1_code in set(ind.values):
    tmp_list = ind[ind == sw1_code].index.to_list() # 这里注意要加上外面的一层
    sw1_dict.update({sw1_code.astype(int): tmp_list})

# 处理行业相关
ind = get_daily_1factor('SW1').iloc[-1]
code_ind_dict = ind.to_dict()

def get_sw1_industry_name(stk_code: int)->str:
    sw1_code = int(code_ind_dict[stk_code])
    sw1_name = sw_level1[sw1_code]
    return sw1_name