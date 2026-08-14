# coding: utf-8
# Author：fengchi863
# Date ：2022/9/6 14:27
import sys
sys.path.append('/data/user/015614/Lucien')
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

"""设置下面的时间区间，生成特定时间的参数"""
# start_date = 20150101
# end_date = 20211213
start_date = 20211213
end_date = 20220909

date_list = tradeDate.get_date_range(start_date, end_date)
stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=1, least_normal_days=1, no_pause=True, start_date=start_date, end_date=end_date)
stk_list = stk_pool.iloc[-1].index.tolist()

pre_close = getData.get_daily_1factor('pre_close', date_list=date_list, code_list=stk_list)
# limit_max = getData.get_daily_1factor('limit_max', date_list=date_list, code_list=stk_list)
limit_max = calc_limit_max(pre_close)
close = getData.get_daily_1factor('close', date_list=date_list, code_list=stk_list)
high = getData.get_daily_1factor('high', date_list=date_list, code_list=stk_list)
zt = pd.DataFrame((close == limit_max)) & stk_pool
daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=date_list, code_list=stk_list)
daily_max_pctchg = (high / pre_close - 1) * 100
czt = pd.DataFrame((high == limit_max)) & stk_pool
czt = czt & (daily_max_pctchg > 6)   # czt这里表示触发过涨停的个股

basic_zt_fname = '/data/group/800463/project/project1_prod/generalStrong_v3/Basic_zt/Basic_zt.h5'
block_path = '/data/user/015614/daily/basic/basic_wind_sw_history/BlockData/'

basic_zt_data = pd.read_hdf(basic_zt_fname)
basic_zt_indexes = basic_zt_data.index.tolist()
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

sw2_name = pd.read_excel('/data/user/015614/daily/basic/basic_wind_sw_history/BlockData/申万二级行业2021版.xlsx', index_col=0)
sw2_name_dict1 = sw2_name['简称'].to_dict()
sw2_name = pd.read_excel('/data/user/015614/daily/basic/basic_wind_sw_history/BlockData/申万二级行业2014版.xlsx', index_col=0)
sw2_name_dict2 = sw2_name['sw_name'].to_dict()

name_dict = dict(list(wind_name_dict.items()) + list(sw2_name_dict1.items()) + list(sw2_name_dict2.items()))

def calc_stk_index(trade_date):
    stk_list = jupiter_df.query(f'trade_date == {trade_date}')['stk_code'].tolist()
    deal_data = pd.DataFrame(index=stk_list)
    concept_factor_wind = pd.read_pickle(block_path + f'daily_wind_factor/{trade_date}.pkl')
    concept_factor_sw = pd.read_pickle(block_path + f'daily_sw_factor/{trade_date}.pkl')
    has_kline_concept = list(concept_factor_wind.index.tolist() + concept_factor_sw.index.tolist())
    for stk_code in stk_list:
        if stk_code == '000748.SZ':
            print(1)
        concept_df = pd.read_pickle(block_path + f'daily_Wind&SW/{trade_date}.pkl')
        concept_list = concept_df.loc[stk_code][concept_df.loc[stk_code] == 1].index.tolist()
        # 确保当天有行情，和行情序列取并集
        no_kline_concept_list = list(set(concept_list).difference(set(has_kline_concept)))
        if no_kline_concept_list:
            print(f'这些概念{trade_date}没有行情', no_kline_concept_list)
        concept_list = list(set(concept_list).difference(set(no_kline_concept_list)))
        wind_concept = list(filter(lambda x: 'WI' in x, concept_list))
        sw_concept = list(filter(lambda x: 'SI' in x, concept_list))
        if len(concept_list) == 0:
            print(f'该个股{trade_date}没有行业：{stk_code}')    # 观察基本都是由于新上市导致，比如第一天断一字板
            continue
        concept_pctchg = pd.DataFrame(index=wind_concept + sw_concept, columns=['pctchg', 'czt_num'])
        if wind_concept:
            concept_pctchg.loc[wind_concept, 'pctchg'] = concept_factor_wind.loc[wind_concept].values[:, 0]
            for a_wind_concept in wind_concept:
                concept_member_list = concept_df[a_wind_concept][concept_df[a_wind_concept] == 1].index.tolist()
                czt_num = czt.loc[trade_date, list(map(stockList.trans_windcode2int, concept_member_list))].sum()
                concept_pctchg.loc[a_wind_concept, 'czt_num'] = czt_num

        if sw_concept:
            concept_pctchg.loc[sw_concept, 'pctchg'] = concept_factor_sw.loc[sw_concept].values[:, 0]
            for a_sw_concept in sw_concept:
                concept_member_list = concept_df[a_sw_concept][concept_df[a_sw_concept] == 1].index.tolist()
                if len(concept_member_list) < 10:   # 只算大于10个成分股的个股
                    continue
                czt_num = czt.loc[trade_date, list(map(stockList.trans_windcode2int, concept_member_list))].sum()
                concept_pctchg.loc[a_sw_concept, 'czt_num'] = czt_num

        concept_pctchg = concept_pctchg.sort_values(['czt_num', 'pctchg'], ascending=False)
        deal_data.loc[stk_code, '概念代码'] = concept_pctchg.index[0]
        deal_data.loc[stk_code, '概念名称'] = name_dict[concept_pctchg.index[0]]
        deal_data.loc[stk_code, '概念涨跌幅'] = concept_pctchg['pctchg'].values[0]
        deal_data.loc[stk_code, '概念涨停数量'] = concept_pctchg['czt_num'].values[0]
    deal_data['dt'] = pd.to_datetime(str(trade_date))
    deal_data['Ticker'] = deal_data.index.tolist()
    deal_data = deal_data.set_index(['dt', 'Ticker'])
    deal_data.to_pickle(block_path + f'daily_max_pctchg_concept/{trade_date}.pkl')

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
    # calc_stk_index(20211215)
    print('耗时：', time.time() - t1)  # 共耗时804秒，没想到竟然只用13分钟