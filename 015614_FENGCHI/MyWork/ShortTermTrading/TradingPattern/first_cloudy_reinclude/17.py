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
from ShortTermTrading.dataApi import getData
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.stockList import clean_stock_list, trans_int2windcode
from multiprocessing import Pool
from ConceptApi import *
from ActiveConceptApi import *

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
end_date = 20201222
shift_start_date = get_pre_trade_date(start_date, offset=30)
date_list = get_date_range(shift_start_date, end_date)

run_date = 20201218
run_datetime = 202012180900

pattern_name = '热点首阴反包'
child_name = '分歧转一致叠加板块_V1'
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

stock_code_and_name = pd.read_excel('/data/user/fengchi/MyWork/BullClient/other_data/stock_code_and_name.xlsx',
                                    encoding='gb18030')
stock_code_and_name_dict = {}
for idx, curr in stock_code_and_name.iterrows():
    stock_code = curr['证券代码']
    stock_name = curr['证券简称']
    stock_code_and_name_dict[stock_code] = stock_name


def get_stock_concept_1day(stock, date):
    stock_concept = get_1stock_concept('Concept_StockList', stock, start_date=date, end_date=date)
    stock_concept_list = stock_concept.sum()[stock_concept.sum() > 0].index.tolist()
    return stock_concept_list


def save_pickle(file, floder_path, file_name):
    if not os.path.exists(floder_path):
        os.makedirs(floder_path)
    file.to_pickle(floder_path + file_name)


def save_xlsx(file, floder_path, file_name):
    if not os.path.exists(floder_path):
        os.makedirs(floder_path)
    file.to_excel(floder_path + file_name)

print('开始计算日间')
# 非ST
stk_ST_judge = clean_stock_list(no_pause=False, no_ST=True, least_live_days=0).loc[start_date:end_date] # 非ST stk_ST_judge
stk_list = stk_ST_judge.columns.tolist()

monitor_window = 3

stk_daily_pct_chg = get_daily_1factor('pct_chg', code_list=stk_list, date_list=date_list)
stk_pctchg_judge_d1 = ((stk_daily_pct_chg < 7) & (stk_daily_pct_chg > -7)).shift(1) # 控制分歧当日收盘涨跌幅在-5到5之间
continue_window = 3
stk_daily_updown = get_daily_1factor('limit_up', code_list=stk_list, date_list=date_list)
stk_daily_3day2limitup = stk_daily_updown.rolling(continue_window).sum()
stk_daily_continue_up = stk_daily_3day2limitup >= 2
stk_daily_continue_up_judge = stk_daily_continue_up.shift(2)

stk_pctchg_judge2 = stk_pctchg_judge_d1 & stk_daily_continue_up_judge  # 连续三天两板

stk_pctchg_judge = stk_pctchg_judge2 # 日间涨幅条件

#############

# 涨停标准
stk_list20 = list()
for stk_code in stk_list:
    if stk_code // 1000 == 300 or stk_code// 1000 == 688:
        stk_list20.append(stk_code)
stk_list10 = list(set(stk_list) - set(stk_list20))

daily_max_pct = pd.DataFrame(index=date_list, columns=stk_pctchg_judge.columns)
daily_max_pct.loc[shift_start_date:20200820, stk_list] = 0.098
daily_max_pct.loc[20200820:end_date, stk_list10] = 0.098
daily_max_pct.loc[20200820:end_date, stk_list20] = 0.198
#############

# 如果最高价达到过涨停价，那么成交量限制为昨天的0.8以上，否则昨天的1倍以上
stk_close = get_daily_1factor('close_badj', code_list=stk_list, date_list=date_list)
stk_pre_close = get_daily_1factor('pre_close_badj', code_list=stk_list, date_list=date_list)
stk_high = get_daily_1factor('high_badj', code_list=stk_list, date_list=date_list)
stk_high_pctchg = stk_high / stk_pre_close
stk_reach_limit_judge = stk_high_pctchg > daily_max_pct

#### 成交量
stk_daily_amt = get_daily_1factor('amt', code_list=stk_list, date_list=date_list)
stk_daily_amt_pct_1d = stk_daily_amt.pct_change(1)
stk_daily_amt_pct_judge1 = stk_daily_amt_pct_1d > 0
stk_daily_amt_pct_judge2 = stk_daily_amt_pct_1d > -0.2

stk_daily_amt_judge = (stk_daily_amt_pct_judge2 & stk_reach_limit_judge) | (stk_daily_amt_pct_judge1 & (~stk_reach_limit_judge))
stk_daily_amt_judge = stk_daily_amt_judge.shift(1)

### 换手率
stk_daily_turn = get_daily_1factor('turn',  code_list=stk_list, date_list=date_list)
stk_daily_turn_rolling10 = stk_daily_turn.rolling(10).mean()
stl_daily_turn_judge = stk_daily_turn > stk_daily_turn_rolling10

stk_daily_judge = stk_pctchg_judge & stk_ST_judge & stk_daily_amt_judge & stl_daily_turn_judge #  总的日间条件

daily_stock_pool = stk_daily_judge.stack()[stk_daily_judge.stack()]
print('日间选出个股：', len(daily_stock_pool), '只')
save_xlsx(daily_stock_pool, stk_xlsx_path, '首阴反包%s_daily_stock_pool.xlsx' % child_name)

print('开始计算日内')
stk_minute_close = get_minute_1factor('close_badj', start_datetime=shift_start_date, end_datetime=end_date, code_list=stk_list)
stk_minute_amt = get_minute_1factor('amt', start_datetime=shift_start_date, end_datetime=end_date, code_list=stk_list)
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
stk_minute_close_nbadj = get_minute_1factor('close', code_list=stk_list, start_datetime=shift_start_date, end_datetime=end_date).loc[(shift_start_date, 925):(end_date, 1500), :]
vol = get_minute_1factor('vol', code_list=stk_list, start_datetime=shift_start_date, end_datetime=end_date)
amt = get_minute_1factor('amt', code_list=stk_list, start_datetime=shift_start_date, end_datetime=end_date)
vwap = amt.groupby('date').cumsum() / vol.groupby('date').cumsum()
stk_minute_vwap_judge = stk_minute_close_nbadj > vwap # 买入时股价高于当天vwap

# 条件四：个股日内涨速大于2%/2min
pctchg_speed_2m = stk_minute_close.pct_change(2)
pctchg_speed_2m_judge = pctchg_speed_2m > 0.015
stk_speed_amt_judge = stk_intraday_amt_judge & pctchg_speed_2m_judge
stk_speed_amt_judge = stk_speed_amt_judge.rolling(5).sum() >= 1

stk_minute_pctchg_buy_judge = stk_minute_pctchg_buy_judge[stk_list]
print(stk_minute_pctchg_buy_judge.shape, stk_intraday_amt_judge.shape, stk_minute_vwap_judge.shape, stk_speed_amt_judge.shape)
stk_minute_judge = stk_minute_pctchg_buy_judge  & stk_intraday_amt_judge & stk_minute_vwap_judge & stk_speed_amt_judge

print('日内日间整合')
# 日间日内整合，4m59s
print(stk_daily_judge.shape, stk_minute_judge.shape)
stk_daily_judge_copy = pd.DataFrame(np.array(stk_daily_judge.loc[stk_minute_close.index.get_level_values('date')]), \
                              index=stk_minute_close.index, columns=stk_daily_judge.columns)
stk_buy_point = stk_daily_judge_copy & stk_minute_judge # 总的触发信号
stk_buy_point = stk_buy_point.dropna(how='all', axis=0)

stk_buy_point = stk_buy_point.fillna(False)
stats_profit = (stk_buy_point * 1.0)[stk_buy_point]
stats_profit = stats_profit.groupby('date').cumsum() == 1
stats_profit_stack = stats_profit.stack()[stats_profit.stack()]
print('日间日内触发个数：', len(stats_profit_stack))

print('叠加板块')
import h5py
read_path='/data/group/800319/fengchi/interface/active_concept_data/active_concept_data.h5'
f = h5py.File(read_path)
active_concept_list2020 = list(f.keys())

def get_need_stk_list(s:pd.Series):
    pct10_num = len(s) * 0.2
    if pct10_num <= 3:
        return s.index.tolist()
    elif 3 < pct10_num <= 7:
        return s.sort_values(ascending=False)[:int(pct10_num)].index.tolist()
    elif pct10_num > 7:
        return s.sort_values(ascending=False)[:7].index.tolist()
    else:
        return list()


# 多进程的方式
def wrapper(concept):
    trigger_concat = []
    concept_stk = get_concept_values('Concept_StockList', concept, start_date=shift_start_date, end_date=end_date)
    concept_stk_copy = pd.DataFrame(np.array(concept_stk.loc[stats_profit.index.get_level_values('date')]), \
                                    index=stats_profit.index, columns=concept_stk.columns)
    stk_list = list(set(stk_buy_point).intersection(set(concept_stk_copy.columns.tolist())))
    trigger_stk_1concept = stats_profit[stk_list] & concept_stk_copy[stk_list]

    # 判断这个概念能否在那一分钟触发
    trigger_stk_1concept_judge = trigger_stk_1concept.sum(axis=1) >= 1
    trigger_stk_1concept_judge = trigger_stk_1concept_judge[trigger_stk_1concept_judge]
    trigger_stk_1concept_judge = trigger_stk_1concept_judge.reset_index()

    for idx in range(len(trigger_stk_1concept_judge)):
        date, time = trigger_stk_1concept_judge.iloc[idx]['date'], trigger_stk_1concept_judge.iloc[idx]['time']
        concept_stk = get_active_stock_1concept(concept, date, date).loc[date]
        concept_stk_list = concept_stk[concept_stk].index.tolist()
        if concept_stk_list == 0:
            continue
        else:
            tmp_minute_close_badj = getData.get_minute_1factor('close_badj', code_list=concept_stk_list,
                                                               start_datetime=date, end_datetime=date)
            tmp_daily_pre_close_badj = getData.get_daily_1day(['pre_close_badj'], code_list=concept_stk_list, date=date)
            tmp_stk_pctchg = tmp_minute_close_badj.loc[date, time] / tmp_daily_pre_close_badj['pre_close_badj'] - 1
            need_stk_list = get_need_stk_list(tmp_stk_pctchg)
            if len(need_stk_list) == 0:
                continue
            if tmp_minute_close_badj.pct_change(2).loc[date, time][need_stk_list].mean() > 0.01:
                print(tmp_minute_close_badj.pct_change(2).loc[date, time][need_stk_list].mean())
                tmp_s = trigger_stk_1concept.loc[date, time]
                trigger_stk_list = tmp_s[tmp_s].index.tolist()
                for trigger_stk in trigger_stk_list:
                    trigger_concat.append((date, time, concept, trigger_stk))
    return trigger_concat


pbar = tqdm(total=len(active_concept_list2020))


def update(*param):
    pbar.update()
    if pbar.last_print_n == len(active_concept_list2020):
        pbar.close()


pool = Pool(32)
pool_dict = dict()
for concept in active_concept_list2020:
    pool_dict[concept] = pool.apply_async(wrapper, (concept,), callback=update)
pool.close()
pool.join()

print('板块叠加完成')
records = []
for concept in pool_dict:
    try:
        records += pool_dict[concept].get()
    except:
        print(concept, 'wrong')
        records += wrapper(concept)

# 去重
record_set = set()
final_record = []
for record in records:
    date, time, stk_code = record[0], record[1], record[3]
    if (date, time ,stk_code) not in record_set:
        record_set.add((date, time, stk_code))
        final_record.append(record)
    else:
        continue

print('最终触发数量：', len(final_record))
stk_buy_point2 = pd.DataFrame(final_record,columns=['date', 'time', 'concept', 'stk_code']).sort_values(['date', 'time']).reset_index(drop=True)
save_pickle(stk_buy_point2, output_dir, child_name+'.pkl')