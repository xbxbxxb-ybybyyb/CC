# coding: utf-8
# Author：fengchi863
# Date ：2023/3/22 17:44

import pandas as pd
from xquant.factordata import FactorData
from dataApi.sendInfo import send_file
from dataApi.stockList import get_stock_list, trans_int2windcode

drop_concept_list = [# 100成分股以上
                     '小市值','融资融券','纳入富时罗素','标普道琼斯中国','成交主力','股票质押','纳入MSCI','专精特新','可转债',
                     '行业龙头','微盘股','专精特新企业','员工持股','基金重仓','破净','私募重仓','机构调研','基金重仓(季调)',
                     '减持','近期减持','小盘成长','大盘股','三新','5G应用','借壳上市','长三角','核心资产','珠三角','举牌',
                     '一线龙头','股权转让','可转债预案','华为平台','高送转','科技龙头','股权激励','资源股','业绩爆雷','养老金',
                     '浦东新区','消费电子产业','肺炎主题','双循环','文化传媒主题','央企','5G','节能环保','碳中和','新基建',
                     '外贸','深圳','合资企业','军民融合','国产化创新','社保重仓','分拆上市',
                     # 100成分股以下
                     '双创100','中小创蓝筹','扭亏','券商重仓','白马股','护城河','地方国企','国家队','最小市值','证金',
                     '高盈利成长股','限售解禁','即将解禁','QFII重仓','国家大基金','高送转预期','A50','沪伦通','增持',
                     '债转股','高瓴资本','QFII重仓(最新)','摘帽','保底增持','中概股回归','机构大额卖出','机构大额买入',
                     '信托重仓']
drop_concept_formatted = '|'.join(drop_concept_list)

fd = FactorData()
wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
wind_concept_copy = wind_concept.copy()
wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]

search_date = [20160630, 20161230, 20170630, 20171229, 20180629, 20181228, 20190628,
20191231, 20200630, 20201231, 20210630, 20211231, 20220630, 20221230, 20230322]
search_date = search_date[4:]

basic_file_path = '/data/group/800463/project/project1_prod/left_v2212/Basic_zt_test/Basic_zt_001.h5'
label_file_path = '/data/group/800463/project/project1_prod/left_v2212/Label_zt_test/Label_zt_001.h5'
all_df = pd.read_hdf(basic_file_path)
all_df['T_o2pre'] = pd.read_hdf(label_file_path)['T_o2pre']
filter_df = all_df[(all_df['ZT_Time'] <= 143000000) &
                   (all_df['open_is_zt'] == 0) &
                   (all_df['T_o2pre'] >= -0.05) &
                   (all_df['after_not_ul_len'] > 10) &
                   (all_df['pre_close'] >= 2) &
                   (all_df['high_price'] < (all_df['trigger_price'])) &
                   (all_df['last_is_zt'] == 0)]

def get_europa_stk_list(date):
    return filter_df.loc[pd.to_datetime(str(date))].index.tolist()


wind_concept_df = pd.DataFrame(index=search_date, columns=['total_concept_num', 'delete_concept_num', 'remain_concept_num'])
cover_df = pd.DataFrame(index=search_date, columns=['>=1覆盖率', '>=3覆盖率', '>=5覆盖率'])
europa_cover_df = pd.DataFrame(index=search_date, columns=['>=1覆盖率', '>=3覆盖率', '>=5覆盖率'])
for dat in search_date:
    check = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_Wind&SW/{dat}.pkl')
    # check = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/daily_Wind&SW/20220630.pkl')
    total_concept_num = len(wind_concept_copy.query(f'S_INFO_LISTDATE <= "{dat}"')['S_INFO_NAME'].unique())
    check_ = check.sum(axis=0)[check.sum(axis=0) < 100]  # 剔除小于100的
    check_ = check_.loc[check_.index.map(lambda x: x.endswith('WI'))]
    less_than100_concept_list = check_.index.tolist()
    wind_concept = wind_concept_copy.query(f'S_INFO_LISTDATE <= "{dat}"')
    wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains(drop_concept_formatted)]
    wind_concept = wind_concept.query(f'S_INFO_WINDCODE in {less_than100_concept_list}')
    remain_concept_num = wind_concept.shape[0]
    delete_concept_num = total_concept_num - remain_concept_num
    wind_concept_df.loc[dat, :] = [total_concept_num, delete_concept_num, remain_concept_num]

    check2 = check[wind_concept['S_INFO_WINDCODE'].tolist()]
    stk_list = get_stock_list(dat)
    europa_stk_list = get_europa_stk_list(dat)
    stk_code_list = list(map(lambda x: trans_int2windcode(x), stk_list))
    check_all = check2.loc[stk_code_list].sum(axis=1)
    check_europa = check2.loc[europa_stk_list].sum(axis=1)
    stk_num = len(stk_code_list)
    europa_stk_num = len(europa_stk_list)
    cover_rate1 = (check_all >= 1).sum() / stk_num
    cover_rate3 = (check_all >= 3).sum() / stk_num
    cover_rate5 = (check_all >= 5).sum() / stk_num
    europa_cover_rate1 = (check_europa >= 1).sum() / europa_stk_num
    europa_cover_rate3 = (check_europa >= 3).sum() / europa_stk_num
    europa_cover_rate5 = (check_europa >= 5).sum() / europa_stk_num
    cover_df.loc[dat, :] = [cover_rate1, cover_rate3, cover_rate5]
    europa_cover_df.loc[dat, :] = [europa_cover_rate1, europa_cover_rate3, europa_cover_rate5]

send_file(wind_concept_df)
send_file(cover_df)
send_file(europa_cover_df)