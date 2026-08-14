# coding: utf-8
# Author：fengchi863
# Date ：2022/8/24 10:06

"""
wind概念：

同花顺概念：['融资融券','标普','深股通','半年报预增','沪股通','MSCI','新股与次新股','央企', '次新股', '创投', '参股']
常规概念有361个、新兴概念有79个，其他概念有645个。
"""

import pandas as pd
from xquant.factordata import FactorData
from LucienUtil.FileUtil import FileUtil
from dataApi.tradeDate import get_trade_date_interval
junk_path = '/data/user/015614/tmp概念分析/'
fd = FactorData()
ths_concept_rank_history_path = '/data/user/015614/daily/同花顺数据/同花顺概念排名/history/'
ths_concept_rank_history_fpath = ths_concept_rank_history_path + '同花顺概念排名20220817.json'

#%% 同花顺概念 数量
ths_fpath = '/data/user/015614/daily/同花顺数据/概念板块同花顺/概念板块同花顺20221125.json'
ths_data = pd.read_json(ths_fpath, typ='dict')

concept_type1 = pd.read_excel(junk_path + '常规概念.xlsx')
concept_type2 = pd.read_excel(junk_path + '新兴概念列表.xlsx')
concept_type3 = pd.read_excel(junk_path + '其他概念列表.xlsx')

print(f'原始同花顺概念数量：{len(concept_type1) + len(concept_type2) + len(concept_type3)}')
print(f'常规、新兴、其他概念分别有{len(concept_type1)},{len(concept_type2)},{len(concept_type3)}个')

del_concept = ['融资融券','标普','深股通','半年报预增','沪股通','MSCI','新股与次新股','央企', '次新股', '创投', '参股']
concept_type11 = concept_type1[~concept_type1['概念名称'].str.contains('|'.join(del_concept))]
concept_type22 = concept_type2[~concept_type2['概念名称'].str.contains('|'.join(del_concept))]
concept_type33 = concept_type3[~concept_type3['概念名称'].str.contains('|'.join(del_concept))]

print(f'剔除后同花顺概念数量：{len(concept_type11) + len(concept_type22) + len(concept_type33)}')
print(f'剔除后常规、新兴、其他概念分别有{len(concept_type11)},{len(concept_type22)},{len(concept_type33)}个')

#%% 万得概念 数量
wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
wind_concept = wind_concept[~wind_concept['CHANGE_HISTORY'].astype(str).str.contains('停用')]
print(f'Wind剔除前概念数量：{len(wind_concept)}')
wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
print(f'Wind剔除后概念数量：{len(wind_concept)}')

#%% 对比WIND概念和同花顺同一概念的创建日期
check = wind_concept[wind_concept['S_INFO_NAME'].str.contains('|'.join(concept_type11['概念名称'].tolist()))]
check = check[['S_INFO_NAME','S_INFO_LISTDATE']]
filter_concept = ['碳中和', '工业4.0', '磷化工', '机器视觉', '钠离子电池', '区块链', '培育钻石', '稀土永磁', '智能穿戴',
                  '充电桩', '大飞机', '专精特新企业', '军民融合']
check1 = check[check['S_INFO_NAME'].str.contains('|'.join(filter_concept))]
check1['THS_LIST_DATE'] = [20141127, 20190725, 20210715, 20170324, 20220704, 20170803, 20211018, 20210303, 20140519, 20210818, 20100729, 20130606, 20130722]
check1['DATA_DIFF'] = check1.apply(lambda x: get_trade_date_interval(x['THS_LIST_DATE'], int(x['S_INFO_LISTDATE'])) + 1, axis=1)
check1.columns = ['概念名称', 'Wind发布日期', '同花顺发布日期', 'Wind比同花顺早(交易日)']
check1 = check1.reset_index(drop=True)
# FileUtil.save_df2xls(check, junk_path, 'Wind与同花顺概念对比.xlsx')

check2 = check[check['S_INFO_LISTDATE'] > '20200101']   # 共32个
filter_concept = ['华为鲲鹏', '冬奥会', 'MCU芯片', '辅助生殖', '华为汽车', '上海自贸区', '储能', '第三代半导体', '动物疫苗', '钙钒矿电池']
check2 = check2[check['S_INFO_NAME'].str.contains('|'.join(filter_concept))]
check2['THS_LIST_DATE'] = [20220318, 20211216, 20210621, 20201023, 20210419, 20130813, 20210423, 20200907, 20190527]
check2['DATA_DIFF'] = check2.apply(lambda x: get_trade_date_interval(x['THS_LIST_DATE'], int(x['S_INFO_LISTDATE'])) + 1, axis=1)
check2.columns = ['概念名称', 'Wind发布日期', '同花顺发布日期', 'Wind比同花顺早(交易日)']
check2 = check2.reset_index(drop=True)
# FileUtil.save_df2xls(check2, junk_path, 'Wind与同花顺概念对比2.xlsx')