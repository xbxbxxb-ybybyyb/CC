# coding: utf-8
# Author：fengchi863
# Date ：2022/9/7 10:45
"""
概念的增量更新代码
"""
import sys
sys.path.append('/data/user/015614/Lucien')

import warnings
import os
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from LucienUtil.FileUtil import FileUtil
from LucienUtil import IO
from tqdm import tqdm
import time
import datetime as dt
from dataApi.sendInfo import send_message
from dataApi import stockList, getData

warnings.filterwarnings("ignore")
fd = FactorData()

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

# 初始化参数
path = '/data/user/015614/daily/basic/basic_wind_sw_history/'
path_block = path + 'BlockData/'
if len(sys.argv) > 1:
    today_date = sys.argv[1]
    print(f'当前计算{today_date}...')
else:
    today_date = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
    # today_date = '20220926' # 测试

t1 = time.time()

#%% 1、读取Wind概念当天的成分股数据
print(f'1、读取Wind概念当天的成分股数据...{time.time() - t1}')
member0 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='<20200101', F_INFO_WINDCODE="like'884%'")  # 进出记录需要取全部时间区间，数量超过上限分为两部分。
member1 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='>=20200101', F_INFO_WINDCODE="like'884%'")
wind_member = pd.concat([member0, member1], ignore_index=True)
wind_member = wind_member.query('CUR_SIGN==1')  # 如果未调出，为缺失值，替换为极大值
wind_member = wind_member[['F_INFO_WINDCODE', 'S_CON_WINDCODE']].astype(str)
wind_member.columns = ['block', 'Ticker']
wind_member = wind_member[wind_member['Ticker'].str.endswith(('.SZ', '.SH'))]
wind_member = wind_member[wind_member['Ticker'].str.startswith(('0', '3', '6'))]

# 获取交易日期列表
date_df = pd.DataFrame()
date_df['dt'] = fd.tradingday(today_date, today_date)
date_df['dt'] = pd.to_datetime(date_df['dt'])

#%% 2、读取申万二级行业当天的成分股数据
print(f'2、读取申万二级行业当天的成分股数据...{time.time() - t1}')
# 申万行业指数代码和wind指数代码对应表
IndexContrastSector = fd.get_factor_value('WIND_IndexContrastSector')
IndexContrastSector = IndexContrastSector[IndexContrastSector['S_INFO_INDEXCODE'].str.endswith('.SI')]
IndexContrastSector = IndexContrastSector[IndexContrastSector['S_INFO_INDUSTRYCODE'].str.startswith('760')]
IndexContrastSector = IndexContrastSector[['S_INFO_INDUSTRYCODE', 'S_INFO_INDEXCODE']]
IndexContrastSector.set_index('S_INFO_INDUSTRYCODE', inplace=True)

# 读取行业指数成分股进出记录，15:30更新，这个时候调用是空的！！！
AShareSWIndustriesClass = fd.get_factor_value('WIND_AShareSWNIndustriesClass')
AShareSWIndustriesClass = AShareSWIndustriesClass.query('CUR_SIGN=="1"')
AShareSWIndustriesClass = AShareSWIndustriesClass[['S_INFO_WINDCODE', 'SW_IND_CODE']]
AShareSWIndustriesClass.columns = ['S_INFO_WINDCODE', 'industry']

AShareSWIndustriesClass['industry'] = AShareSWIndustriesClass['industry'].apply(lambda x: x[:6].ljust(16, '0'))
AShareSWIndustriesClass['industry'] = AShareSWIndustriesClass['industry'].apply(lambda x: IndexContrastSector.loc[x, 'S_INFO_INDEXCODE'] if x in IndexContrastSector.index else np.nan)

#%% 3、对申万二级行业和概念进行剔除
print(f'3、对申万二级行业和概念进行剔除...{time.time() - t1}')
# 剔除的概念
drop_concept_list = [# 100成分股以上
                     '小市值','融资融券','纳入富时罗素','标普道琼斯中国','成交主力','股票质押','纳入MSCI','专精特新','可转债',
                     '行业龙头','微盘股','专精特新企业','员工持股','基金重仓','破净','私募重仓','机构调研','基金重仓(季调)',
                     '减持','近期减持','小盘成长','大盘股','三新','5G应用','借壳上市','长三角','核心资产','珠三角','举牌',
                     '一线龙头','股权转让','可转债预案','华为平台','高送转','科技龙头','股权激励','资源股','业绩爆雷','养老金',
                     '浦东新区','消费电子产业','肺炎主题','双循环','文化传媒主题','央企','5G','节能环保','碳中和','新基建',
                     '外贸','深圳','合资企业','军民融合','国产化创新','社保重仓','分拆上市',
                     # 100成分股以下，不是概念的概念
                     '双创100','中小创蓝筹','扭亏','券商重仓','白马股','护城河','地方国企','国家队','最小市值','证金',
                     '高盈利成长股','限售解禁','即将解禁','QFII重仓','国家大基金','高送转预期','A50','沪伦通','增持',
                     '债转股','高瓴资本','QFII重仓(最新)','摘帽','保底增持','中概股回归','机构大额卖出','机构大额买入',
                     '信托重仓']
drop_concept_formatted = '|'.join(drop_concept_list)

fd = FactorData()
wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains(drop_concept_formatted)]
filter_col = ['S_INFO_WINDCODE', 'S_INFO_CODE', 'S_INFO_NAME']
wind_concept = wind_concept[filter_col]
wind_concept_list = wind_concept['S_INFO_WINDCODE'].tolist()
FileUtil.save_list2pkl(wind_concept_list, '/data/user/015614/daily/basic/basic_wind_sw_history/BlockData/', '最新2015至今全量Wind列表.pkl')
sw2_concept_list = list(AShareSWIndustriesClass['industry'].unique())

if os.path.exists(path_block + 'daily_Wind&SW/' + f'{today_date}.pkl'):
    res = pd.read_pickle(path_block + 'daily_Wind&SW/' + f'{today_date}.pkl')
    print(f'4、{today_date}已有拼接表，直接读取...{time.time() - t1}')
else:
    #%% 4、开始对所有概念和行业进行拼接，拼接到一张表上
    print(f'4、开始对所有概念和行业进行拼接，拼接到一张表上...{time.time() - t1}')
    concept_list = wind_concept_list + sw2_concept_list
    has_appear_stk_list = list(map(lambda x: stockList.trans_int2windcode(x), stockList.get_all_stock_ever_appear(today_date)))

    value_list = list()
    for concept in tqdm(concept_list):
        if 'WI' in concept:
            tmp_member = wind_member.query(f'block == "{concept}"')['Ticker'].tolist()
        else:   # 'SI'
            tmp_member = AShareSWIndustriesClass.query(f'industry == "{concept}"')['S_INFO_WINDCODE'].tolist()
        data = pd.DataFrame(1, index=tmp_member, columns=[concept])
        data2 = data.reindex(index=has_appear_stk_list, fill_value=0)
        value_list.append(data2.values)
    value_res = np.concatenate(value_list, axis=1)
    res = pd.DataFrame(value_res, index=has_appear_stk_list, columns=concept_list)
    res.to_pickle(path_block + 'daily_Wind&SW/' + f'{today_date}.pkl')
concept_df = res.copy()

#%% 5、计算当日czt个股
print(f'5、计算当日czt个股...{time.time() - t1}')
stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=1, least_normal_days=1, no_pause=True, least_recover_days=0, start_date=int(today_date), end_date=int(today_date))
stk_list = stk_pool.iloc[-1].index.tolist()

pre_close = getData.get_daily_1factor('pre_close', date_list=[today_date], code_list=stk_list)
limit_max = calc_limit_max(pre_close)
close = getData.get_daily_1factor('close', date_list=[today_date], code_list=stk_list)
high = getData.get_daily_1factor('high', date_list=[today_date], code_list=stk_list)
low = getData.get_daily_1factor('low', date_list=[today_date], code_list=stk_list)
zt = pd.DataFrame((close == limit_max)) & stk_pool
daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=[today_date], code_list=stk_list)
daily_max_pctchg = (high / pre_close - 1) * 100
czt = pd.DataFrame((high == limit_max)) & stk_pool
czt = czt & (daily_max_pctchg > 6)   # czt这里表示触发过涨停的个股

#%% 6、计算wind和申万二级的行情
print(f'6、计算wind和申万二级的行情...{time.time() - t1}')
wind_daily_data = fd.get_factor_value('WIND_AIndexWindIndustriesEOD',
                                          TRADE_DT=[int(today_date)],
                                          S_INFO_WINDCODE=wind_concept_list)[['TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_PCTCHANGE']]
wind_daily_data = wind_daily_data.set_index('S_INFO_WINDCODE')[['S_DQ_PCTCHANGE']]
wind_daily_data.columns = ['pctchg']

sw_daily_data = fd.get_factor_value('WIND_ASWSIndexEOD',
                                        TRADE_DT=[int(today_date)],
                                        factors=['TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_CLOSE', 'S_DQ_PRECLOSE'],
                                        S_INFO_WINDCODE=sw2_concept_list)
sw_daily_data['S_DQ_PCTCHANGE'] = (sw_daily_data['S_DQ_CLOSE'] / sw_daily_data['S_DQ_PRECLOSE'] - 1) * 100
sw_daily_data = sw_daily_data.set_index('S_INFO_WINDCODE', drop=True)[['S_DQ_PCTCHANGE']]
sw_daily_data.columns = ['pctchg']

#%% 7、获取所有Wind和申万二级行业的名称
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

#%% 8、根据Basic_zt计算当日的因子
print(f'7、根据Basic_zt计算{today_date}的概念因子...{time.time() - t1}')

# 每个交易日22:08分左右更新
# basic_zt_fname = '/data/group/800463/project/project1_prod/generalStrong_v3/Basic_zt/Basic_zt.h5'
# try:
#     basic_zt_data = pd.read_hdf(basic_zt_fname)
#     assert basic_zt_data.index[-1][0] >= pd.to_datetime(str(today_date))    # 确保当天已经更新数据
# except:
#     time.sleep(60)
# basic_zt_indexes = basic_zt_data.index.tolist()

#%% 改为手动计算，不然Basic_zt生成时间太晚了，由于涨停价的计算方式问题，肯定已经不判断ST股涨停了
basic_zt = (high == limit_max) & (low < limit_max)
basic_zt = basic_zt[list(filter(lambda x: x // 1000 != 688, basic_zt.columns.tolist()))]
zt_list = list(map(stockList.trans_int2windcode, basic_zt.iloc[-1][basic_zt.iloc[-1]].index.tolist()))
basic_zt_indexes = pd.MultiIndex.from_product([[pd.to_datetime(str(today_date))], zt_list]).tolist()

jupiter_df = pd.DataFrame(basic_zt_indexes, columns=['dt', 'stk_code'])
jupiter_df['trade_date'] = jupiter_df['dt'].map(lambda x: x.strftime('%Y%m%d'))
jupiter_df = jupiter_df.query('trade_date >= @today_date & trade_date <= @today_date')

concept_factor_wind = wind_daily_data
concept_factor_sw = sw_daily_data
def calc_stk_index(trade_date):
    stk_list = jupiter_df.query(f'trade_date == "{trade_date}"')['stk_code'].tolist()
    deal_data = pd.DataFrame(index=stk_list)
    has_kline_concept = list(concept_factor_wind.index.tolist() + concept_factor_sw.index.tolist())
    for stk_code in stk_list:
        if stk_code == '002084.SZ':
            print(1)
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
    # 核验当日存储的文件
    if deal_data.shape[0] == 0:
        print(f'储存有错！！！DataFrame为空！！！')
        send_message(f'{today_date}储存有错！！！DataFrame为空！！！')
    FileUtil.save_df2pkl(deal_data, path_block + 'daily_max_pctchg_concept/jupiter/', f'{trade_date}.pkl')
    check = pd.read_hdf('/data/group/800463/fengc/daily/concept/jupiter_concept.h5')
    if check.index.get_level_values(0)[-1] != pd.to_datetime(str(today_date)):
        IO.pd_hdf5_writer(deal_data, '/data/group/800463/fengc/daily/concept/jupiter_concept.h5', dataset='concept', append=True)

calc_stk_index(int(today_date))
# calc_stk_index(20220930)
print(f'{today_date}所属概念计算已完成...{time.time() - t1}')
send_message(f'{today_date} jupiter日频概念数据已更新...')