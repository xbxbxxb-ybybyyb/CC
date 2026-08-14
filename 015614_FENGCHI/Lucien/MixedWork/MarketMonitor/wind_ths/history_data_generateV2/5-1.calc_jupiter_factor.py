# coding: utf-8
# Author：fengchi863
# Date ：2023/3/26 13:02

import sys
sys.path.append('/data/user/015614/Lucien')
import os
import pandas as pd
import numpy as np
from LucienUtil.SpeedUtil import SpeedUtil
from tqdm import tqdm
from dataApi import tradeDate, getData, stockList
import time
from xquant.factordata import FactorData

def calc_limit_max(pre_close):
    cyb = list(filter(lambda x: stockList.trans_int2windcode(x).startswith('3'), pre_close.columns.tolist()))
    not_cyb = list(filter(lambda x: stockList.trans_int2windcode(x).startswith('3') - 1, pre_close.columns.tolist()))
    if pre_close.index[0] >= 20200824:
        pre_close_cyb = pre_close[cyb]
        pre_close_not_cyb = pre_close[not_cyb]
        limit_max_cyb = (pre_close_cyb * 100 * 1.2 + 0.5).apply(np.floor) / 100
        limit_max_not_cyb = (pre_close_not_cyb * 100 * 1.1 + 0.5).apply(np.floor) / 100
        limit_max = pd.concat([limit_max_cyb, limit_max_not_cyb], axis=1)[pre_close.columns]
        return limit_max
    elif pre_close.index[-1] < 20200824:
        limit_max = (pre_close * 100 * 1.1 + 0.5).apply(np.floor) / 100
        return limit_max
    else:
        after_20200824 = pre_close.loc[20200824:]
        before_20200824 = pre_close.loc[:20200823]
        limit_max_before_20200824 = (before_20200824 * 100 * 1.1 + 0.5).apply(np.floor) / 100

        pre_close_cyb = after_20200824[cyb]
        pre_close_not_cyb = after_20200824[not_cyb]
        limit_max_cyb = (pre_close_cyb * 100 * 1.2 + 0.5).apply(np.floor) / 100
        limit_max_not_cyb = (pre_close_not_cyb * 100 * 1.1 + 0.5).apply(np.floor) / 100
        limit_max_after_20200824 = pd.concat([limit_max_cyb, limit_max_not_cyb], axis=1)[pre_close.columns]

        limit_max = pd.concat([limit_max_before_20200824, limit_max_after_20200824], axis=0)
    return limit_max

# TODO：
"""
设置下面的时间区间，生成特定时间的参数
两组日期参数，一组是2014版申万二级行业，一组是2021版申万二级行业
"""
# start_date = 20150101
# end_date = 20211212
start_date = 20211212
end_date = 20221027

date_list = tradeDate.get_date_range(start_date, end_date)
stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=1, least_normal_days=1, no_pause=True, start_date=start_date, end_date=end_date)
stk_list = stk_pool.iloc[-1].index.tolist()

# 概念触板数量indexes
pre_close = getData.get_daily_1factor('pre_close', date_list=date_list, code_list=stk_list)
limit_max = calc_limit_max(pre_close)
close = getData.get_daily_1factor('close', date_list=date_list, code_list=stk_list)
high = getData.get_daily_1factor('high', date_list=date_list, code_list=stk_list)
zt = pd.DataFrame((close == limit_max)) & stk_pool
daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=date_list, code_list=stk_list)
daily_max_pctchg = (high / pre_close - 1) * 100
czt = pd.DataFrame((high == limit_max)) & stk_pool
czt = czt & (daily_max_pctchg > 6)   # czt这里表示触发过涨停的个股

block_path = '/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/'

# 概念筛选indexes
stk_pool2 = stockList.clean_stock_list(no_ST=False, least_live_days=1, least_normal_days=0, no_pause=True, start_date=start_date, end_date=end_date)
stk_list2 = stk_pool2.iloc[-1].index.tolist()
pre_close2 = getData.get_daily_1factor('pre_close', date_list=date_list, code_list=stk_list2)
limit_max2 = calc_limit_max(pre_close2)
close2 = getData.get_daily_1factor('close', date_list=date_list, code_list=stk_list2)
high2 = getData.get_daily_1factor('high', date_list=date_list, code_list=stk_list2)
czt2 = pd.DataFrame((high2 == limit_max2)) & stk_pool2

czt2_df = czt2.stack()[czt2.stack()]
czt2_df.index.names = ['dt', 'stk_code']
czt2_df = czt2_df.reset_index()
czt2_df['dt'] = czt2_df['dt'].map(lambda x: pd.to_datetime(str(x)))
czt2_df['stk_code'] = czt2_df['stk_code'].map(lambda x: stockList.trans_int2windcode(x))
czt2_df = czt2_df.set_index(['dt', 'stk_code'])
basic_zt_indexes = czt2_df.index.tolist()
jupiter_df = pd.DataFrame(basic_zt_indexes, columns=['dt', 'stk_code'])
jupiter_df['trade_date'] = jupiter_df['dt'].map(lambda x: int(x.strftime('%Y%m%d')))
jupiter_df = jupiter_df.query('trade_date >= @start_date & trade_date <= @end_date')

# 获取Wind名字
fd = FactorData()
wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
wind_name_dict = wind_concept[['S_INFO_WINDCODE', 'S_INFO_NAME']].set_index('S_INFO_WINDCODE').to_dict()['S_INFO_NAME']

sw2_name = pd.read_excel('/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/申万二级行业2014版.xlsx', index_col=0)
sw2_name_dict1 = sw2_name['sw_name'].to_dict()
sw2_name = pd.read_excel('/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/申万二级行业2021版.xlsx', index_col=0)
sw2_name_dict2 = sw2_name['简称'].to_dict()

if end_date == 20211212:
    name_dict = dict(list(wind_name_dict.items()) + list(sw2_name_dict2.items()) + list(sw2_name_dict1.items()))
else:
    name_dict = dict(list(wind_name_dict.items()) + list(sw2_name_dict1.items()) + list(sw2_name_dict2.items()))

def calc_stk_index(trade_date):
    # TODO：一定要让trade_date放在最后，因为后面取最后一天的变量是这一天
    trade_date_list = [tradeDate.get_pre_trade_date(trade_date, 2), tradeDate.get_pre_trade_date(trade_date), trade_date]
    # 对刚刚更换SW2时进行对比
    if trade_date in [20150105, 20211213]:
        trade_date_list = [trade_date]
    if trade_date in [20150106, 20211214]:
        trade_date_list = [tradeDate.get_pre_trade_date(trade_date), trade_date]
    stk_list = jupiter_df.query(f'trade_date in {trade_date_list}')['stk_code'].unique().tolist()
    cur_stk_list = jupiter_df.query(f'trade_date == {trade_date}')['stk_code'].unique().tolist()

    has_kline_concept = list()
    stk_concept_list_dict = dict()
    for trade_date in trade_date_list:
        concept_factor_wind = pd.read_pickle(block_path + f'daily_wind_factor/{trade_date}.pkl')
        concept_factor_sw = pd.read_pickle(block_path + f'daily_sw_factor/{trade_date}.pkl')
        has_kline_concept.extend(list(concept_factor_wind.index.tolist() + concept_factor_sw.index.tolist()))
        concept_df = pd.read_pickle(block_path + f'daily_Wind&SW/{trade_date}.pkl')
        for stk_code in stk_list:
            concept_list = concept_df.loc[stk_code][concept_df.loc[stk_code] == 1].index.tolist()
            no_kline_concept_list = list(set(concept_list).difference(set(has_kline_concept)))
            concept_list = list(set(concept_list).difference(set(no_kline_concept_list)))
            if stk_code not in stk_concept_list_dict.keys():
                stk_concept_list_dict[stk_code] = concept_list
            else:
                tmp_list = stk_concept_list_dict[stk_code]
                tmp_list.extend(concept_list)
                stk_concept_list_dict[stk_code] = list(set(tmp_list))

    concept_count = pd.Series()
    for stk_code in stk_concept_list_dict.keys():
        concept_list = stk_concept_list_dict[stk_code]
        for concept in concept_list:
            if concept in concept_count.index:
                concept_count[concept] += 1
            else:
                concept_count[concept] = 1
    concept_count = concept_count.sort_values(ascending=False)
    concept_count_df = pd.DataFrame(concept_count, columns=['count'])
    concept_count_df['concept_pctchg'] = concept_count.index.map(lambda x: concept_factor_wind.loc[x, 'pctchg'] if x.endswith('WI') else concept_factor_sw.loc[x, 'pctchg']).values

    stk_concept_dict = dict()
    for concept in concept_count.index.tolist():
        for stk_code in stk_list:
            if stk_code not in stk_concept_dict.keys() and concept in stk_concept_list_dict[stk_code]:
                stk_concept_dict[stk_code] = concept

    deal_data = pd.DataFrame(pd.Series(stk_concept_dict), columns=['概念代码'])
    deal_data['概念名称'] = deal_data['概念代码'].map(lambda x: name_dict[x])
    deal_data = deal_data.loc[cur_stk_list]
    deal_data['dt'] = pd.to_datetime(str(trade_date))
    deal_data['Ticker'] = deal_data.index.tolist()
    deal_data = deal_data.set_index(['dt', 'Ticker'])
    deal_data = deal_data.sort_index()

    os.makedirs(block_path + f'daily_min_concept_num_concept/jupiter/', exist_ok=True)
    deal_data.to_pickle(block_path + f'daily_min_concept_num_concept/jupiter/{trade_date}.pkl')

def parallel_calc_stk_index(date_list):
    pbar = tqdm(range(len(date_list)))
    for idx in pbar:
        trade_dt = date_list[idx]
        pbar.set_description('并行生成中|%s' % trade_dt)
        calc_stk_index(trade_dt)

if __name__ == '__main__':
    t1 = time.time()
    SpeedUtil.multiprocess(20, parallel_calc_stk_index, date_list)
    # SpeedUtil.multiprocess(1, parallel_calc_stk_index, [20160712])  # DEBUG
    # calc_stk_index(20150106)
    # calc_stk_index(20211214)
    print('耗时：', time.time() - t1)  # 共耗时804秒，没想到竟然只用13分钟