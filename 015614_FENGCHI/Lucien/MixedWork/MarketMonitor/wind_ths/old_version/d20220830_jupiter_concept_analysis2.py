# coding: utf-8
# Author：fengchi863
# Date ：2022/8/30 19:37

"""
第二个版本修改：
双姐：申万二级行业不包含进来再算下，按照日度来算下每日涉及到的概念数量、zt数量>=5的概念数量。

算出来结果中有Wind概念的属于少部分，所以还是使用第一个版本
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
"""第一种方案
for idx in tqdm(range(len(deal_data))):
    deal = deal_data.iloc[idx]
    index = deal.name
    concept_pctchg = pd.DataFrame(index=all_wind_concept + sw_concept_list, columns=['pctchg'])
    # trade_dt, stk_code = deal['dt'], deal['Ticker']
    trade_dt, stk_code = pd.to_datetime('2022-08-15'), '600395.SH'
    try:
        for _wind_concept in all_wind_concept:
            _isin_this = pd.read_pickle('/data/user/015614/tmp概念分析/BlockData/each_block/' + _wind_concept + '.pkl')
            if (trade_dt, stk_code) in _isin_this.index.tolist():
                concept_pctchg.loc[_wind_concept, 'pctchg'] = wind_daily_data.query(f'TRADE_DT == "{trade_dt.strftime("%Y%m%d")}" & S_INFO_WINDCODE == @_wind_concept').iloc[0]['S_DQ_PCTCHANGE']
        for _sw_concept in sw_concept_list:
            _isin_this = pd.read_pickle('/data/user/015614/tmp概念分析/BlockData/each_block/' + _sw_concept + '.pkl')
            if (trade_dt, stk_code) in _isin_this.index.tolist():
                concept_pctchg.loc[_sw_concept, 'pctchg'] = sw_daily_data.query(f'TRADE_DT == "{trade_dt.strftime("%Y%m%d")}" & S_INFO_WINDCODE == @_sw_concept').iloc[0]['S_DQ_PCTCHANGE']
        concept_pctchg = concept_pctchg.dropna()
        concept_pctchg = concept_pctchg.sort_values(['pctchg'], ascending=False)
        deal_data.loc[index, '概念代码'] = concept_pctchg.index[0]
        deal_data.loc[index, '概念名称'] = sw_code_concept_dict[concept_pctchg.index[0]]
        deal_data.loc[index, '概念涨跌幅'] = concept_pctchg['pctchg'].values[0]
    except Exception as e:
        # traceback.print_exception(e)
        print(f'{trade_dt}, {stk_code}, 报错')
"""
# 第二种方案
concept_members = pd.read_pickle('/data/user/015614/tmp概念分析/BlockData/concept_members.pkl')
for idx in tqdm(range(len(deal_data))):
    deal = deal_data.iloc[idx]
    index = deal.name
    concept_pctchg = pd.DataFrame(index=all_wind_concept, columns=['pctchg'])
    trade_dt, stk_code = deal['dt'], deal['Ticker']
    try:
        all_concept_list = concept_members.loc[trade_dt, stk_code][concept_members.loc[trade_dt, stk_code] == True].index.tolist()
        wind_concept = list(filter(lambda x: 'WI' in x, all_concept_list))
        wind_concept = list(set(wind_concept_list) & set(wind_concept))
        if not wind_concept:
            continue
        concept_pctchg = pd.DataFrame(index=wind_concept, columns=['pctchg'])
        if wind_concept:
            concept_pctchg.loc[wind_concept, 'pctchg'] = wind_daily_data.query(f'TRADE_DT == "{trade_dt.strftime("%Y%m%d")}"').set_index(['S_INFO_WINDCODE']).loc[wind_concept, 'S_DQ_PCTCHANGE'].values
        concept_pctchg = concept_pctchg.sort_values(['pctchg'], ascending=False)
        deal_data.loc[index, '概念代码'] = concept_pctchg.index[0]
        deal_data.loc[index, '概念名称'] = sw_code_concept_dict[concept_pctchg.index[0]]
        deal_data.loc[index, '概念涨跌幅'] = concept_pctchg['pctchg'].values[0]
    except Exception as e:
        # traceback.print_exception(e)
        print(f'{trade_dt}, {stk_code}, 报错')
raw_col_list = deal_data.columns.tolist()
new_col_list = raw_col_list[:2] + raw_col_list[-3:] + raw_col_list[2:-3]
deal_data = deal_data[new_col_list]
from LucienUtil.FileUtil import FileUtil
FileUtil.save_df2xls(deal_data, '/data/user/015614/tmp概念分析/', '近两周Jupiter策略触发信号样本最大涨幅概念.xlsx')

# 测试为空的数量
pd.isnull(deal_data['概念名称']).sum() / deal_data.shape[0]

#%% 按日度计算每日涉及的概念数量
group_data = deal_data.groupby(['概念名称'])['概念名称'].count()

from dataApi.sendInfo import send_file
send_file('/data/user/015614/tmp概念分析/近两周Jupiter策略触发信号样本最大涨幅概念.xlsx')
print(1)
