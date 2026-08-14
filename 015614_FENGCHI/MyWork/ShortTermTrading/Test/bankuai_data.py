# coding: utf-8
# Author：fengchi863
# Date ：2020/12/7 15:09

import os
import sys
sys.path.append('/data/group/800319')
sys.path.append('/data/user/fengchi/MyWork')
sys.path.append("/data/group/800319/Daily_ConCept/")
sys.path.append('/data/user/fengchi/MyWork/ShortTermTrading')
import numpy as np
import pandas as pd
from tqdm import tqdm
import time
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.stockList import clean_stock_list, trans_int2windcode
from multiprocessing import Pool
from ConceptApi import *

# 绘图
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# 多线程
from multiprocessing import Pool

basic_values = get_basic_values('Active_Concept')
concept = Get_Concept_Code()
concept_dict = concept.to_dict()['S_INFO_NAME']
daily_hot_concept = basic_values.rename(columns=concept_dict)
concept_code_list = list(concept_dict.keys())
concept_list = daily_hot_concept.columns.tolist() # 中文所有概念板块列表

start_date = 20200101
end_date = 20201201

run_date = 20201204
run_datetime = 202012041500

pattern_name = '热点首阴反包'
child_name = '高开低走非涨停买入'
holding_day = 1

root_path = '/data/group/800319/fengchi/pattern_test/'

tmp_data_path = root_path + 'temp_data/'

pickle_path = root_path + '/%s/%s/个股_%d_%d/' % (pattern_name, run_date, start_date, end_date)

stk_df_path = root_path + '%s/%s/外部股票池_%d_%d/stk_df.pkl' % (pattern_name, run_date, start_date, end_date)

# 储存股票池excel
stk_xlsx_path = root_path + '/%s/%s/筛选出的股票_%d_%d/' % (pattern_name, run_date, start_date, end_date)

# 储存结果
output_dir = root_path + '%s/%s/结果_%d_%d_%d/' % (pattern_name, run_date, start_date, end_date, run_datetime)

output_path = output_dir + '回测结果_%d_%d_%d_%d.xlsx' % (holding_day, start_date, end_date, run_datetime)

log_path = output_dir + '回测日志_%d_%d_%d_%d.log' % (holding_day, start_date, end_date, run_datetime)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

start_date = 20200101
end_date = 20201201
shift_start_date = get_pre_trade_date(start_date, offset=30)
date_list = get_date_range(shift_start_date, end_date)

concept_minute_pctchg = pd.read_pickle('/data/group/800319/fengchi/pattern_test/temp_data/minute_concept_pctchg2020.pkl') # 需要先保存
concept_minute_pctchg2 = concept_minute_pctchg - concept_minute_pctchg.shift(2)
concept_minute_pctchg2_judge = (concept_minute_pctchg2 > 0.008).fillna(False)

def calc_pctchg_stk(concept):
    print(concept)
    concept_df = get_concept_values('Concept_StockList', concept=concept, start_date=shift_start_date, end_date=end_date)
    concept_df_copy = pd.DataFrame(np.array(concept_df.shift(1).fillna(False).loc[stk_minute_close.index.get_level_values('date')]), \
                              index=stk_minute_close.index, columns=concept_df.columns)
    concept_df_copy = concept_df_copy * 1.0
    calc1 = concept_minute_pctchg2_judge[concept]
    calc1 = calc1 * 1.0
    concept_res = (concept_df_copy.T * calc1).T
    concept_res = concept_res == 1.0
    concept_res.to_pickle(root_path + 'my_factor/concept_pctchg_stk/%s.pkl' % concept.split('.')[0])


pool = Pool(70)
pool.map(calc_pctchg_stk, concept_code_list)