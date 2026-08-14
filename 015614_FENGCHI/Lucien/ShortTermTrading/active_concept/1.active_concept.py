# coding: utf-8
# Author：fengchi863
# Date ：2023/9/7 20:38

"""
根据条件设定概念是否强势
"""
import pandas as pd
import numpy as np
from dataApi import tradeDate, getData, stockList
from tqdm import tqdm
from ShortTermTrading.active_concept.config import *

#%% 计算每天的Wind概念板块个股数量
start_date = 20160101
# start_date = 20221001
shift_start_date = tradeDate.get_pre_trade_date(start_date, 5)
end_date = 20221231

date_list = tradeDate.get_date_range(start_date, end_date)
shift_date_list = tradeDate.get_date_range(shift_start_date, end_date)

wind_members = pd.read_pickle('/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/最新2015至今全量Wind列表.pkl')
daily_wind_stk_num = pd.DataFrame(index=shift_date_list, columns=wind_members)
daily_index_open = getData.get_daily_1factor('open', code_list=['ZZ500'], date_list=shift_date_list, type='bench')
daily_index_close = getData.get_daily_1factor('close', code_list=['ZZ500'], date_list=shift_date_list, type='bench')
daily_index_pctchg = daily_index_open / daily_index_close.shift(1) - 1

# # 一部分为0成份股的原因是那个指数当天还没有上行情   耗时6min
for dat in tqdm(shift_date_list):
    today_wind_stk_df = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_Wind&SW/{dat}.pkl')
    wind_list = list(filter(lambda x: str(x).endswith('WI'), today_wind_stk_df.columns))
    today_wind_stk_df = today_wind_stk_df[wind_list]
    today_wind_stk_num = today_wind_stk_df.sum(axis=0)
    today_wind_stk_num = today_wind_stk_num.reindex(index=wind_members).fillna(0)
    daily_wind_stk_num.loc[dat] = today_wind_stk_num.values

# print(daily_wind_stk_num)

#%% 计算每天Wind概念的涨跌幅，拼成一张表 耗时1分半钟
daily_wind_concept_pct = pd.DataFrame(index=date_list, columns=wind_members)
for dat in tqdm(shift_date_list):
    today_wind_concept = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_wind_factor/{dat}.pkl')
    today_wind_concept = today_wind_concept.reindex(index=wind_members).fillna(0) # TODO: 这里其他概念填充0还是nan
    daily_wind_concept_pct.loc[dat] = today_wind_concept.values.reshape(-1)

#%% 计算每天的活跃概念
daily_active_concept = pd.DataFrame(index=date_list, columns=wind_members)
for dat in tqdm(shift_date_list):
    today_wind_stk_df = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_Wind&SW/{dat}.pkl')
    wind_list = list(filter(lambda x: str(x).endswith('WI'), today_wind_stk_df.columns))
    today_wind_stk_df = today_wind_stk_df[wind_list]
    daily_pct = getData.get_daily_1factor('pct_chg', date_list=[dat], code_list=today_wind_stk_df.index.tolist())
    daily_limit_up = getData.get_daily_1factor('limit_up', date_list=[dat], code_list=today_wind_stk_df.index.tolist())

    # 涨跌幅
    daily_pct.columns = daily_pct.columns.map(lambda x: stockList.trans_int2windcode(x))
    daily_pct = daily_pct.reindex(columns=today_wind_stk_df.index)
    daily_pct_array = np.tile(daily_pct.values.reshape(-1, 1), len(wind_list))

    daily_limit_up.columns = daily_limit_up.columns.map(lambda x: stockList.trans_int2windcode(x))
    daily_limit_up = daily_limit_up.reindex(columns=today_wind_stk_df.index)
    daily_limit_up_array = np.tile(daily_limit_up.values.reshape(-1, 1), len(wind_list)) > 0.5

    today_wind_stk_df[today_wind_stk_df == 0] = np.nan

    daily_pct_array = daily_pct_array * today_wind_stk_df.values # 每个概念内 是否属于这个概念 涨跌幅
    daily_limit_up_array = (daily_limit_up_array * (today_wind_stk_df.values > 0.5))  # 每个概念内 是否属于这个概念 是否涨停
    # today_wind_stk_pct = pd.DataFrame(daily_pct_array, index=today_wind_stk_df.index, columns=today_wind_stk_df.columns)
    # today_wind_stk_limitup = pd.DataFrame(daily_pct_array, index=today_wind_stk_df.index, columns=today_wind_stk_df.columns)

    """依次划分"""
    today_index_pct = daily_index_pctchg.loc[dat].values[0]
    # 对于小板块，板块内至少有2只个股涨幅大于5%，且至少有1只个股涨停
    today_sml_concept_flag = (SML_CONCEPT_RANGE[0] <= daily_wind_stk_num.reindex(columns=wind_list).loc[dat].values) & (
                daily_wind_stk_num.reindex(columns=wind_list).loc[dat].values < SML_CONCEPT_RANGE[1])

    today_sml_active_concept_cond1 = daily_wind_concept_pct.reindex(columns=wind_list).loc[dat].values > SML_CONCEPT_PCT
    today_sml_active_concept_cond2 = (daily_wind_concept_pct.reindex(columns=wind_list).loc[dat].values - today_index_pct) > SML_CONCEPT_EXCESS_PCT
    today_sml_active_concept_cond3 = ((daily_pct_array > 0.05).sum(axis=0) >= 2) & (daily_limit_up_array.sum(axis=0) >= 1)

    today_sml_active_concept = today_sml_active_concept_cond1 * today_sml_active_concept_cond2 * today_sml_active_concept_cond3

    # 对于中板块，板块内前30%个股（按涨跌幅排名）涨幅大于5%，且至少有1只个股涨停
    today_mid_concept_flag = (MID_CONCEPT_RANGE[0] <= daily_wind_stk_num.reindex(columns=wind_list).loc[dat].values) & (
                daily_wind_stk_num.reindex(columns=wind_list).loc[dat].values < MID_CONCEPT_RANGE[1])

    today_mid_active_concept_cond1 = daily_wind_concept_pct.reindex(columns=wind_list).loc[dat].values > MID_CONCEPT_PCT
    today_mid_active_concept_cond2 = (daily_wind_concept_pct.reindex(columns=wind_list).loc[dat].values - today_index_pct) > MID_CONCEPT_EXCESS_PCT
    today_mid_active_concept_cond3 = ((daily_pct_array > 0.05).sum(axis=0) > (~np.isnan(daily_pct_array)).sum(axis=0) * 0.3) & (daily_limit_up_array.sum(axis=0) >= 1)
    today_mid_active_concept = today_mid_active_concept_cond1 * today_mid_active_concept_cond2 * today_mid_active_concept_cond3

    # 对于大板块，板块内前30%个股（按涨跌幅排名）涨幅大于4%，且至少有1只个股涨停
    today_big_concept_flag = (BIG_CONCEPT_RANGE[0] <= daily_wind_stk_num.reindex(columns=wind_list).loc[dat].values) & (
            daily_wind_stk_num.reindex(columns=wind_list).loc[dat].values < BIG_CONCEPT_RANGE[1])

    today_big_active_concept_cond1 = daily_wind_concept_pct.reindex(columns=wind_list).loc[dat].values > BIG_CONCEPT_PCT
    today_big_active_concept_cond2 = (daily_wind_concept_pct.reindex(columns=wind_list).loc[dat].values - today_index_pct) > BIG_CONCEPT_EXCESS_PCT
    today_big_active_concept_cond3 = ((daily_pct_array > 0.04).sum(axis=0) > (~np.isnan(daily_pct_array)).sum(axis=0) * 0.3) & (daily_limit_up_array.sum(axis=0) >= 1)
    today_big_active_concept = today_big_active_concept_cond1 * today_big_active_concept_cond2 * today_big_active_concept_cond3

    today_active_concept = today_sml_active_concept + today_mid_active_concept + today_big_active_concept
    today_active_concept = pd.Series(today_active_concept, index=wind_list).reindex(wind_members).fillna(False)
    daily_active_concept.loc[dat] = today_active_concept

daily_active_concept.to_pickle('/data/user/015614/TEST/active_concept_test/active_concept_fulldays.pkl')
daily_active_concept = daily_active_concept.loc[date_list]
daily_active_concept.to_pickle('/data/user/015614/TEST/active_concept_test/active_concept.pkl')