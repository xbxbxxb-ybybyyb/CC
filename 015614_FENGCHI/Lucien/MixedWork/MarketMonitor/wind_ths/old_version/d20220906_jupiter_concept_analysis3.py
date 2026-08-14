# coding: utf-8
# Author：fengchi863
# Date ：2022/8/25 19:05
"""
第三个版本修改：
双姐：首先概念/行业内涨停数量 更改为触发过的涨停数量，只用管上过板即可，不用管其他筛选条件
另外是修改最大涨跌幅，板块内涨停数量最大的行业
"""

import os
from datetime import datetime as dt

import numpy as np
import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData

today_date = dt.today().strftime('%Y-%m-%d')
fd = FactorData()

#%% 选择Wind概念，做一些基础筛选
wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
wind_concept = wind_concept[~wind_concept['CHANGE_HISTORY'].astype(str).str.contains('停用')]
wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
filter_col = ['S_INFO_WINDCODE', 'S_INFO_CODE', 'S_INFO_NAME']
wind_concept = wind_concept[filter_col]
wind_concept_list = wind_concept['S_INFO_WINDCODE'].tolist()
code_concept_dict = wind_concept[['S_INFO_WINDCODE', 'S_INFO_NAME']].set_index('S_INFO_WINDCODE').to_dict()['S_INFO_NAME']

#%% 根据成分股数量筛选和剔除
member0 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='<20200101', F_INFO_WINDCODE="like'884%'")  # 进出记录需要取全部时间区间，数量超过上限分为两部分。
member1 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='>=20200101', F_INFO_WINDCODE="like'884%'")
wind_member = pd.concat([member0, member1], ignore_index=True)
wind_member = wind_member.query('CUR_SIGN==1')
member_group = wind_member.groupby('F_INFO_WINDCODE')['S_CON_WINDCODE'].count()
member_group = pd.DataFrame(member_group[wind_concept_list])
member_group = member_group[member_group['S_CON_WINDCODE'] < 100]
member_group['概念名称'] = member_group.index.map(lambda x: code_concept_dict[x])

# 剔除的概念
drop_concept_list = ['双创100',
                     '中小创蓝筹',
                     '扭亏',
                     '券商重仓',
                     '白马股',
                     '护城河',
                     '地方国企',
                     '国家队',
                     '最小市值',
                     '证金',
                     '高盈利成长股',
                     '限售解禁',
                     '即将解禁',
                     'QFII重仓',
                     '国家大基金',
                     '高送转预期',
                     'A50',
                     '沪伦通',
                     '增持',
                     '债转股',
                     '高瓴资本',
                     'QFII重仓(最新)',
                     '摘帽',
                     '保底增持',
                     '中概股回归',
                     '机构大额卖出',
                     '机构大额买入',
                     '信托重仓']
member_group = member_group[~member_group['概念名称'].str.contains('|'.join(drop_concept_list))]
wind_concept_list = member_group.index.tolist()

#%% 申万二级概念名称
AIndexDescription = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
AIndexDescription['S_INFO_NAME'] = AIndexDescription['S_INFO_NAME'].str.replace('指数', '')
AIndexDescription = AIndexDescription[AIndexDescription['CHANGE_HISTORY'].astype(str).str.contains('概念')]
AIndexDescription = AIndexDescription[~AIndexDescription['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
AIndexDescription = AIndexDescription[~AIndexDescription['CHANGE_HISTORY'].astype(str).str.contains('停用')]

# 读取行业板块名称
IndexContrastSector = fd.get_factor_value('WIND_IndexContrastSector')
IndexContrastSector = IndexContrastSector[IndexContrastSector['S_INFO_INDEXCODE'].str.endswith('.SI')]
IndexContrastSector = IndexContrastSector[IndexContrastSector['S_INFO_INDUSTRYCODE'].str.startswith('760')]

# 合并
AIndexDescription = AIndexDescription[['S_INFO_WINDCODE', 'S_INFO_NAME']]
AIndexDescription.columns = ['block_code', 'block_name']
IndexContrastSector = IndexContrastSector[['S_INFO_INDEXCODE', 'S_INFO_INDUSTRYNAME']]
IndexContrastSector.columns = ['block_code', 'block_name']
block_name = pd.concat(([AIndexDescription, IndexContrastSector]), axis=0, ignore_index=True)
sw_code_concept_dict = block_name[['block_code', 'block_name']].set_index('block_code').to_dict()['block_name']

#%% 获取Wind概念涨跌幅
wind_daily_data = fd.get_factor_value('WIND_AIndexWindIndustriesEOD',
                                      TRADE_DT=['>=20220815', '<=20220826'],
                                      S_INFO_WINDCODE=wind_concept_list)[['TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_PCTCHANGE']]


#%% 获取申万二级行业涨跌幅
sw_daily_data = fd.get_factor_value('WIND_ASWSIndexEOD',
                                    TRADE_DT=['>=20220815', '<=20220826'],
                                    factors=['TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_CLOSE', 'S_DQ_PRECLOSE'],
                                    S_INFO_WINDCODE="like'8%.SI'")
sw_daily_data['S_DQ_PCTCHANGE'] = (sw_daily_data['S_DQ_CLOSE'] / sw_daily_data['S_DQ_PRECLOSE'] - 1) * 100


deal_fpath = f'/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发标签汇总_2022-08-26.xlsx'
deal_data = pd.read_excel(deal_fpath)
deal_data = deal_data[deal_data['dt'] >= pd.to_datetime('2022-08-15')]
deal_data = deal_data.reset_index(drop=True)
deal_data['概念代码'] = np.nan
deal_data['概念名称'] = np.nan
deal_data['概念涨跌幅'] = np.nan

all_wind_concept = list(filter(lambda x: 'WI' in x, os.listdir('/data/user/015614/tmp概念分析/BlockData/each_block/')))
all_wind_concept = list(set(map(lambda x: x[:-4], all_wind_concept)) & set(wind_concept_list))
sw_concept_list = list(filter(lambda x: 'SI' in x, os.listdir('/data/user/015614/tmp概念分析/BlockData/each_block/')))
sw_concept_list = list(map(lambda x: x[:-4], sw_concept_list))

#%% 统计涨停数量
start_date, end_date = 20220815, 20220825
from dataApi import tradeDate, stockList, getData
date_list = tradeDate.get_date_range(start_date, end_date)
stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=30, least_normal_days=1, no_pause=True, least_recover_days=0, start_date=start_date, end_date=end_date)
stk_list = stk_pool.iloc[-1].index.tolist()
limit_max = getData.get_daily_1factor('limit_max', date_list=date_list, code_list=stk_list)
close = getData.get_daily_1factor('close', date_list=date_list, code_list=stk_list)
high = getData.get_daily_1factor('high', date_list=date_list, code_list=stk_list)
pre_close = getData.get_daily_1factor('pre_close', date_list=date_list, code_list=stk_list)
zt = pd.DataFrame((close == limit_max)) & stk_pool
daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=date_list, code_list=stk_list)
daily_max_pctchg = (high / pre_close - 1) * 100
czt = pd.DataFrame((high == limit_max)) & stk_pool
czt = czt & (daily_max_pctchg > 6)   # czt这里表示触发过涨停的个股

concept_members = pd.read_pickle('/data/user/015614/tmp概念分析/BlockData/concept_members.pkl')
for idx in tqdm(range(len(deal_data))):
    deal = deal_data.iloc[idx]
    index = deal.name
    trade_dt, stk_code = deal['dt'], deal['Ticker']
    # trade_dt, stk_code = pd.to_datetime('2022-08-23'), '002306.SZ'
    try:
        all_concept_list = concept_members.loc[trade_dt, stk_code][concept_members.loc[trade_dt, stk_code] == True].index.tolist()
        wind_concept = list(filter(lambda x: 'WI' in x, all_concept_list))
        sw_concept = list(filter(lambda x: 'SI' in x, all_concept_list))
        wind_concept = list(set(wind_concept_list) & set(wind_concept))
        concept_pctchg = pd.DataFrame(index=wind_concept + sw_concept, columns=['pctchg', 'czt_num'])
        if wind_concept:
            concept_pctchg.loc[wind_concept, 'pctchg'] = wind_daily_data.query(f'TRADE_DT == "{trade_dt.strftime("%Y%m%d")}"').set_index(['S_INFO_WINDCODE']).loc[wind_concept, 'S_DQ_PCTCHANGE'].values
            for a_wind_concept in wind_concept:
                concept_member_list = concept_members.loc[(trade_dt, slice(None)), a_wind_concept][concept_members.loc[(trade_dt, slice(None)), a_wind_concept] == 1].index.get_level_values(1).tolist()
                czt_num = czt.loc[int(trade_dt.strftime('%Y%m%d')), list(map(stockList.trans_windcode2int, concept_member_list))].sum()
                concept_pctchg.loc[a_wind_concept, 'czt_num'] = czt_num
        if sw_concept:
            try:
                concept_pctchg.loc[sw_concept, 'pctchg'] = sw_daily_data.query(f'TRADE_DT == "{trade_dt.strftime("%Y%m%d")}"').set_index(['S_INFO_WINDCODE']).loc[sw_concept, 'S_DQ_PCTCHANGE'].values
                for a_sw_concept in sw_concept:
                    concept_member_list = concept_members.loc[(trade_dt, slice(None)), a_sw_concept][concept_members.loc[(trade_dt, slice(None)), a_sw_concept] == 1].index.get_level_values(1).tolist()
                    czt_num = czt.loc[int(trade_dt.strftime('%Y%m%d')), list(map(stockList.trans_windcode2int, concept_member_list))].sum()
                    concept_pctchg.loc[a_sw_concept, 'czt_num'] = czt_num
            except:
                print(f'{trade_dt}, {stk_code}, 没有{sw_concept}')
                pass    # 存在600777.SH 的 801961.SI 没有这个指数了
        concept_pctchg = concept_pctchg.sort_values(['czt_num', 'pctchg'], ascending=False)
        deal_data.loc[index, '概念代码'] = concept_pctchg.index[0]
        deal_data.loc[index, '概念名称'] = sw_code_concept_dict[concept_pctchg.index[0]]
        deal_data.loc[index, '概念涨停数量'] = concept_pctchg['czt_num'].values[0]
        deal_data.loc[index, '概念涨跌幅'] = concept_pctchg['pctchg'].values[0]
    except Exception as e:
        # traceback.print_exception(e)
        print(f'{trade_dt}, {stk_code}, 报错')
raw_col_list = deal_data.columns.tolist()
new_col_list = raw_col_list[:2] + raw_col_list[-4:] + raw_col_list[2:6]
deal_data = deal_data[new_col_list]
from LucienUtil.FileUtil import FileUtil
FileUtil.save_df2xls(deal_data, '/data/user/015614/tmp概念分析/', '近两周Jupiter策略触发信号样本最大涨停数量概念.xlsx')
from dataApi.sendInfo import send_file
send_file('/data/user/015614/tmp概念分析/近两周Jupiter策略触发信号样本最大涨停数量概念.xlsx')

group_data = deal_data.groupby(['dt', '概念代码', '概念名称'])['概念代码'].count()
group_data = pd.DataFrame(group_data)
# group_data['成分股数量'] = group_data.index.get_level_values(1).map(lambda x: (concept_members.loc[(dt, slice(None)), x] == 1).sum()).values
for dt, concept, concept_name in tqdm(group_data.index):
    # dt, concept = pd.to_datetime('2022-08-15'), '801072.SI'   # 调试
    concept_member_list = concept_members.loc[(dt, slice(None)), concept][concept_members.loc[(dt, slice(None)), concept] == 1].index.get_level_values(1).tolist()
    group_data.loc[(dt, concept, concept_name), '成分股数量'] = len(concept_member_list)
    czt_num = czt.loc[int(dt.strftime('%Y%m%d')), list(map(stockList.trans_windcode2int, concept_member_list))].sum()
    group_data.loc[(dt, concept, concept_name), '涨停数量'] = czt_num

    concept_zt_s = czt.loc[int(dt.strftime('%Y%m%d')), list(map(stockList.trans_windcode2int, concept_member_list))]
    concept_zt_list = concept_zt_s[concept_zt_s==1].index.tolist()
    triggered_stk_list = deal_data.query(f'dt == "{dt.strftime("%Y-%m-%d")}"')['Ticker'].tolist()
    triggered_stk_list = list(map(stockList.trans_windcode2int, triggered_stk_list))
    triggered_concept_zt_stk_list = list(set(concept_zt_list) & set(triggered_stk_list))
    group_data.loc[(dt, concept, concept_name), '触发过的涨停数量'] = len(triggered_concept_zt_stk_list)


group_data.columns = ['当日该概念/行业触发的个股个数', '成分股数量', '概念/行业内涨停数量', '触发个股涨停数量']
group_data = group_data.reset_index()
FileUtil.save_df2xls(group_data, '/data/user/015614/tmp概念分析/', '近两周Jupiter策略涉及的概念.xlsx')
from dataApi.sendInfo import send_file
send_file('/data/user/015614/tmp概念分析/近两周Jupiter策略涉及的概念.xlsx')

daily_concept_num = group_data.groupby('dt')['概念代码'].count()
daily_concept_num = pd.DataFrame(daily_concept_num)
daily_concept_num.columns = ['当日涉及概念及行业数量']
FileUtil.save_df2xls(daily_concept_num, '/data/user/015614/tmp概念分析/', '近两周Jupiter策略每日涉及概念数量.xlsx')
from dataApi.sendInfo import send_file
send_file('/data/user/015614/tmp概念分析/近两周Jupiter策略每日涉及概念数量.xlsx')

_group_data = group_data[group_data['概念/行业内涨停数量'] >= 5]
daily_concept_num_more5 = _group_data.groupby('dt')['概念代码'].count()
daily_concept_num_more5 = pd.DataFrame(daily_concept_num_more5)
daily_concept_num_more5.columns = ['当日涉及概念中涨停数量大于5的概念数量']
send_file(daily_concept_num_more5)