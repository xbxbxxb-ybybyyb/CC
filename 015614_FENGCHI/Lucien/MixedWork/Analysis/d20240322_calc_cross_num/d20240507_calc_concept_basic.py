# coding: utf-8
# Author：fengchi863
# Date ：2024/5/6 8:52

from dataApi import tradeDate
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
import os

"""
/data/user/015614/daily/basic/basic_wind_sw_history3/BlockData/each_block/ 
此数据为成分股数据，以及这个wind概念的发布日期、K线日期等获取到的应该保有的wind概念，但没有进行剔除
root_path = '/data/user/015614/daily/basic/basic_wind_sw_history3/BlockData/daily_Wind&SW/'

此数据为未完整版本，因为写着写着发现原来计算的是对的
"""

root_path = '/data/user/015614/daily/basic/basic_wind_sw_history3/BlockData/daily_Wind&SW/'

start_date = 20191201
end_date = 20230531
date_list = tradeDate.get_date_range(start_date, end_date)

# 剔除的概念
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

res = pd.DataFrame(index=date_list, columns=['剔除概念数', '全市场概念数量', 'WIND概念数量', 'SW概念数量'])
concept_stk_num_list = list()
for dat in date_list:
    wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_LISTDATE=[f'<= {dat}'], S_INFO_WINDCODE="like'884%'")
    wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
    wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
    raw_concept_num = len(wind_concept)
    wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
    wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains(drop_concept_formatted)]
    filter_col = ['S_INFO_WINDCODE', 'S_INFO_CODE', 'S_INFO_NAME']
    wind_concept = wind_concept[filter_col]
    now_concept_num = len(wind_concept)
    format_drop_num = raw_concept_num - now_concept_num

    concept_df = pd.read_pickle(root_path + f'{dat}.pkl')
    daily_concept_list = concept_df.sum(axis=0).loc[concept_df.sum(axis=0) > 0].index.tolist()
    daily_concept_list = list(filter(lambda x: x.endswith('WI'), daily_concept_list))
    daily_concept_num = len(daily_concept_list)


    drop_num = raw_concept_num - daily_concept_num

    wind_concept_list = list(map(lambda x: x.endswith('WI'), daily_concept_list))
    wind_concept_num = sum(wind_concept_list)

    sw_concept_list = list(map(lambda x: x.endswith('SI'), daily_concept_list))
    sw_concept_num = sum(sw_concept_list)

    drop_concept_num = all_wind_concept_num - wind_concept_num

    # 统计概念成分股变化
    tmp = concept_df[daily_concept_list].sum(axis=0).replace(0, np.nan)
    concept_stk_num_list.append(pd.DataFrame(tmp, columns=[dat]))

    res.loc[dat, '剔除概念数'] = drop_concept_num
    res.loc[dat, '全市场概念数量'] = daily_concept_num
    res.loc[dat, 'WIND概念数量'] = wind_concept_num
    res.loc[dat, 'SW概念数量'] = sw_concept_num

daily_concept_cont = pd.concat(concept_stk_num_list, axis=1).T
diff_df = daily_concept_cont.diff().describe().T

output_dict = {
    '统计数据': res,
    '每日diff变化值': diff_df
}
from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(output_dict, '/data/user/015614/junkData/', '概念统计数据.xlsx')
