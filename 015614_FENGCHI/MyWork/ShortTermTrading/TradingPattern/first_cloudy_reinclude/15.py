# coding: utf-8
# Author：fengchi863
# Date ：2020/12/16 13:33

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
from ShortTermTrading.ConceptApi.ConceptApi import *
from ShortTermTrading.interface.ActiveConceptApi import *

# 绘图
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# 多线程
from multiprocessing import Pool

###########

basic_values = get_basic_values('Active_Concept')
concept = Get_Concept_Code()
concept_dict = concept.to_dict()['S_INFO_NAME']
daily_hot_concept = basic_values.rename(columns=concept_dict)
concept_code_list = list(concept_dict.keys())
concept_list = daily_hot_concept.columns.tolist() # 中文所有概念板块列表

###########

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

##############

start_date = 20200101
end_date = 20201201
shift_start_date = get_pre_trade_date(start_date, offset=30)
date_list = get_date_range(shift_start_date, end_date)
stock_code_and_name = pd.read_excel('/data/user/fengchi/MyWork/BullClient/other_data/stock_code_and_name.xlsx', encoding='gb18030')
stock_code_and_name_dict = {}
for idx, curr in stock_code_and_name.iterrows():
    stock_code = curr['证券代码']
    stock_name = curr['证券简称']
    stock_code_and_name_dict[stock_code] = stock_name


def save_pickle(file, floder_path, file_name):
    if not os.path.exists(floder_path):
        os.makedirs(floder_path)
    file.to_pickle(floder_path + file_name)


def save_xlsx(file, floder_path, file_name):
    if not os.path.exists(floder_path):
        os.makedirs(floder_path)
    file.to_excel(floder_path + file_name)

def get_stock_concept_1day(stock, date):
    stock_concept = get_1stock_concept('Concept_StockList', stock, start_date=date, end_date=date)
    stock_concept_list = stock_concept.sum()[stock_concept.sum()>0].index.tolist()
    return stock_concept_list

###############个股日间条件###############

# 非ST
stk_ST_judge = clean_stock_list(no_pause=False, no_ST=True, least_live_days=0).loc[
               start_date:end_date]  # 非ST stk_ST_judge

monitor_window = 3
daily_pctchg_threshold = 3  # 得出来的是百分比

stk_daily_pct_chg = get_daily_1factor('pct_chg', date_list=date_list)
stk_pctchg_judge_d2 = stk_daily_pct_chg.shift(2) > daily_pctchg_threshold
stk_pctchg_judge_d3 = stk_daily_pct_chg.shift(3) > daily_pctchg_threshold
stk_pctchg_judge_d4 = stk_daily_pct_chg.shift(4) > daily_pctchg_threshold

stk_daily_open_badj = get_daily_1factor('open_badj', date_list=date_list)
stk_daily_close_badj = get_daily_1factor('close_badj', date_list=date_list)
stk_daily_open_close = stk_daily_close_badj / stk_daily_open_badj - 1
stk_pctchg_judge_d1 = stk_daily_open_close.shift(1) < 0

stk_pctchg_judge_d22 = stk_daily_open_close.shift(2) > 0
stk_pctchg_judge_d33 = stk_daily_open_close.shift(3) > 0
stk_pctchg_judge_d44 = stk_daily_open_close.shift(4) > 0

tmp_stk_pctchg_judge1 = stk_pctchg_judge_d2 & stk_pctchg_judge_d3 & stk_pctchg_judge_d4 & stk_pctchg_judge_d22 & \
                        stk_pctchg_judge_d33 & stk_pctchg_judge_d44
stk_pctchg_judge1 = stk_pctchg_judge_d1 & stk_pctchg_judge_d2 & stk_pctchg_judge_d3 & stk_pctchg_judge_d4 & stk_pctchg_judge_d22 & \
                    stk_pctchg_judge_d33 & stk_pctchg_judge_d44

#############
continue_window = 2
stk_daily_updown = get_daily_1factor('limit_up', date_list=date_list)
stk_daily_continue_up = stk_daily_updown.rolling(continue_window).sum()
stk_daily_continue_up = stk_daily_continue_up == 2
stk_daily_continue_up = stk_daily_continue_up.shift(2)

stk_pctchg_judge2 = stk_daily_continue_up & stk_pctchg_judge_d1  # 连续两日涨停并且首阴

stk_pctchg_judge = stk_pctchg_judge1 | stk_pctchg_judge2  # 日间涨幅条件
##############
# stk_daily_amt = get_daily_1factor('amt', date_list=date_list)
# stk_daily_amt_judge = (stk_daily_amt.shift(1) / stk_daily_amt.shift(2).rolling(5).mean()) > 0.8 # 首阴成交量条件

stk_minute_amt = get_minute_1factor('amt', start_datetime=shift_start_date, end_datetime=end_date)
stk_minute_close = get_minute_1factor('close_badj', start_datetime=shift_start_date, end_datetime=end_date)
threshold = 0.4

# 记录首阴当天的开盘价以及首阴当天的状态
# stk_daily_open_badj stk_daily_close_badj
# 检测当天相对于前一天的收盘价是高开还是低开
stk_close = get_daily_1factor('close_badj', date_list=date_list)
stk_minute_close = get_minute_1factor('close_badj', start_datetime=shift_start_date, end_datetime=end_date).loc[(shift_start_date, 930):(end_date, 1500), :]
stk_minute_close.index.name = 'date', 'time'

stk_list = stk_minute_close.columns.intersection(stk_daily_open_badj.columns)

stk_daily_pre_close_badj = get_daily_1factor('pre_close_badj', date_list=date_list)
stk_daily_pre_close_badj = stk_daily_pre_close_badj[stk_list]
stk_daily_open_badj = stk_daily_open_badj[stk_list]
# 高开还是低开 True or False
stk_daily_high_open_judge = (stk_daily_open_badj > stk_daily_pre_close_badj).shift(1) # 是否高开
stk_daily_low_open_judge = (stk_daily_open_badj < stk_daily_pre_close_badj).shift(1) # 是否低开
stk_daily_ping_open_judge = (stk_daily_open_badj == stk_daily_pre_close_badj).shift(1) # 是否平开

stk_daily_judge = stk_pctchg_judge & stk_ST_judge & stk_daily_high_open_judge #  总的日间条件

################
daily_stock_pool = stk_daily_judge.stack()[stk_daily_judge.stack()]
print('日间选出个股：', len(daily_stock_pool), '只')
save_xlsx(daily_stock_pool, stk_xlsx_path, '首阴反包%s_daily_stock_pool.xlsx' % child_name)

#############个股日内条件################

# 条件一：买入时涨跌幅大于0
stk_minute_yes_close = pd.DataFrame(np.array(stk_close.shift(1).loc[stk_minute_close.index.get_level_values('date')]), \
                              index=stk_minute_close.index, columns=stk_close.columns)
stk_minute_pctchg = stk_minute_close / stk_minute_yes_close - 1
stk_minute_pctchg_buy_judge = stk_minute_pctchg > 0  # 买入时涨跌幅大于0 stk_minute_pctchg_buy_judge

# 条件二：买入时量比没有下降
stk_amt_rolling10 = stk_minute_amt.groupby('date').rolling(10).mean()
stk_amt_rolling_2m_mean = stk_minute_amt.groupby('date').rolling(2).mean()
stk_intraday_amt_judge = (stk_amt_rolling_2m_mean / stk_amt_rolling10 >= 0.8)
stk_intraday_amt_judge = stk_intraday_amt_judge.droplevel(0) # 买入时量比没有下降 stk_intraday_amt_judge

# 条件三：买入时股价高于当天vwap
stk_minute_close_nbadj = get_minute_1factor('close', start_datetime=shift_start_date, end_datetime=end_date).loc[(shift_start_date, 925):(end_date, 1500), :]
vol = get_minute_1factor('vol', start_datetime=shift_start_date, end_datetime=end_date)
amt = get_minute_1factor('amt', start_datetime=shift_start_date, end_datetime=end_date)
vwap = amt.groupby('date').cumsum() / vol.groupby('date').cumsum()
stk_minute_vwap_judge = stk_minute_close_nbadj > vwap # 买入时股价高于当天vwap

# 条件四：个股日内涨速大于2%/2min
pctchg_speed_2m = stk_minute_close.pct_change(2)
pctchg_speed_2m_judge = pctchg_speed_2m > 0.015
stk_speed_amt_judge = stk_intraday_amt_judge & pctchg_speed_2m_judge
stk_speed_amt_judge = stk_speed_amt_judge.rolling(5).sum() >= 1

stk_minute_pctchg_buy_judge = stk_minute_pctchg_buy_judge[stk_list]
stk_minute_judge = stk_minute_pctchg_buy_judge  & stk_intraday_amt_judge & stk_minute_vwap_judge & stk_speed_amt_judge

# 日间日内整合
stk_daily_judge_copy = pd.DataFrame(np.array(stk_daily_judge.loc[stk_minute_close.index.get_level_values('date')]), \
                              index=stk_minute_close.index, columns=stk_daily_judge.columns)
stk_buy_point = stk_daily_judge_copy & stk_minute_judge # 总的触发信号

stats_profit = (stk_buy_point * 1.0)[stk_buy_point]
stats_profit = stats_profit.groupby('date').cumsum() == 1
stats_profit_stack = stats_profit.stack()[stats_profit.stack()]

# trigger_stock_pool = stk_buy_point.stack()[stk_buy_point.stack()]
# trigger_stock_pool.index.names = ['date', 'time', 'stk_code']

##################开始叠加板块################


concept_pctchg_stk_name = os.listdir(root_path + 'my_factor/concept_pctchg_stk/')
res = pd.read_pickle(root_path + 'my_factor/concept_pctchg_stk/' + concept_pctchg_stk_name[0])
for concept_df in tqdm(concept_pctchg_stk_name[1:]):
    print(concept_df)
    tmp = pd.read_pickle(root_path + 'my_factor/concept_pctchg_stk/' + concept_df)
    res = res | tmp

stk_list2 = set(stk_buy_point.columns).intersection(res.columns)
res = res[stk_list2]
stk_buy_point = stk_buy_point[stk_list2]
stk_buy_point2 = stk_buy_point & res

trigger_stock_pool2 = stk_buy_point2.stack()[stk_buy_point2.stack()]

# 统计收益
stats_profit = (stk_buy_point2 * 1.0)[stk_buy_point2]
stats_profit = stats_profit.groupby('date').cumsum() == 1
stats_profit_stack = stats_profit.stack()[stats_profit.stack()]

obj = pd.DataFrame(stats_profit_stack)
obj.index.names = 'date', 'time', 'stk_code'
obj = obj.reset_index()

obj['buy_price'] = obj.apply(lambda x: stk_minute_close.loc[(x['date'], x['time']), x['stk_code']], axis=1)
obj['sell_price'] = obj.apply(lambda x: stk_minute_close.loc[(x['date'], 1500), x['stk_code']], axis=1)
obj['profit'] = obj['sell_price'] / obj['buy_price'] - 1
obj['盈亏'] = obj['profit'].apply(lambda x: 1 if x > 0 else 0)
print('平均盈亏:', obj['profit'].mean())
print('胜率:', obj['盈亏'].sum()/len(obj))
print('盈亏比:', obj[obj['profit']>0]['profit'].sum() / obj[obj['profit']<0]['profit'].sum())

save_xlsx(obj, stk_xlsx_path, '首阴反包%s_minute_stock_pool.xlsx' % child_name)