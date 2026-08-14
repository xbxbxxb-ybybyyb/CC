# coding: utf-8
# Author：fengchi863
# Date ：2024/5/6 8:52

from dataApi import tradeDate
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
import time
import os

root_path = '/data/user/015614/daily/basic/basic_wind_sw_history3/BlockData/daily_Wind&SW/'

start_date = 20191201
end_date = 20230531
date_list = tradeDate.get_date_range(start_date, end_date)

# 统计原始概念数量
fd = FactorData()
wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
wind_concept_list = wind_concept['S_INFO_WINDCODE'].tolist()

# 统计缺失K线的数量
# t1 = time.time()
# ccpt_daily_data1 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + str(start_date), '<=' + "20161231"], S_INFO_WINDCODE="like'884%'")
# ccpt_daily_data2 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20170101", '<=' + "20171231"], S_INFO_WINDCODE="like'884%'")
# ccpt_daily_data22 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20180101", '<=' + "20181231"], S_INFO_WINDCODE="like'884%'")
# ccpt_daily_data3 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20190101", '<=' + "20191231"], S_INFO_WINDCODE="like'884%'")
# ccpt_daily_data4 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20200101", '<=' + "20201231"], S_INFO_WINDCODE="like'884%'")
# ccpt_daily_data5 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20210101", '<=' + "20211231"], S_INFO_WINDCODE="like'884%'")
# ccpt_daily_data6 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20220101", '<=' + "20221231"], S_INFO_WINDCODE="like'884%'")
# ccpt_daily_data7 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20230101", '<=' + str(end_date)], S_INFO_WINDCODE="like'884%'")
# ccpt_daily_data = pd.concat([ccpt_daily_data1, ccpt_daily_data2, ccpt_daily_data22, ccpt_daily_data3, ccpt_daily_data4, ccpt_daily_data5, ccpt_daily_data6, ccpt_daily_data7], axis=0)
# ccpt_daily_data = ccpt_daily_data[(ccpt_daily_data['S_DQ_HIGH'] - ccpt_daily_data['S_DQ_LOW']) > 0][['TRADE_DT', 'S_INFO_WINDCODE']]
# ccpt_daily_data.columns = ['dt', 'block']
# ccpt_daily_data['dt'] = pd.to_datetime(ccpt_daily_data['dt'])
# AIndexDescription = ccpt_daily_data.sort_values(['block', 'dt']).groupby('block')[['dt']].first()
# AIndexDescription.columns = ['list_dt']
# AIndexDescription['delist_dt'] = ccpt_daily_data.sort_values(['block', 'dt']).groupby('block')[['dt']].last()
# print('总耗时', time.time() - t1)  # 20150101-20220902 查询耗时377秒=8min

res = pd.DataFrame(index=date_list, columns=['剔除概念数', '全市场概念数量', 'WIND概念数量', 'SW概念数量'])
last_date_drop = list()
concept_stk_num_list = list()
drop_df = pd.DataFrame(index=date_list, columns=['当日所有剔除概念数量', '当日新增剔除概念数量', '当日所有剔除概念', '当日新增剔除概念'])
for dat in date_list:
    concept_df = pd.read_pickle(root_path + f'{dat}.pkl')
    daily_concept_list = concept_df.sum(axis=0).loc[concept_df.sum(axis=0) > 0].index.tolist()
    daily_concept_num = len(daily_concept_list)

    all_wind_concept_list = wind_concept[(wind_concept['S_INFO_LISTDATE'] <= str(dat))]['S_INFO_WINDCODE'].tolist()
    all_wind_concept_num = (wind_concept['S_INFO_LISTDATE'] <= str(dat)).sum()

    wind_concept_list = list(filter(lambda x: x.endswith('WI'), daily_concept_list))
    wind_concept_num = len(wind_concept_list)

    sw_concept_list = list(map(lambda x: x.endswith('SI'), daily_concept_list))
    sw_concept_num = sum(sw_concept_list)

    drop_concept_num = all_wind_concept_num - wind_concept_num

    # 把drop的写入表格
    drop_concept_list = list(set(all_wind_concept_list).difference(set(wind_concept_list)))
    today_drop = wind_concept.query(f'S_INFO_WINDCODE in {drop_concept_list}')['S_INFO_NAME'].tolist()
    today_new_drop = list(set(today_drop).difference(set(last_date_drop)))
    drop_df.loc[dat, '当日新增剔除概念'] = ','.join(sorted(today_new_drop))
    last_date_drop = today_drop
    drop_df.loc[dat, '当日所有剔除概念'] = ','.join(today_drop)
    drop_df.loc[dat, '当日所有剔除概念数量'] = len(today_drop)
    drop_df.loc[dat, '当日新增剔除概念数量'] = len(today_new_drop)

    # 统计概念成分股变化
    tmp = concept_df[daily_concept_list].sum(axis=0).replace(0, np.nan)
    concept_stk_num_list.append(pd.DataFrame(tmp, columns=[dat]))

    res.loc[dat, '剔除概念数'] = drop_concept_num
    res.loc[dat, '全市场概念数量'] = daily_concept_num
    res.loc[dat, 'WIND概念数量'] = wind_concept_num
    res.loc[dat, 'SW概念数量'] = sw_concept_num

daily_concept_cont = pd.concat(concept_stk_num_list, axis=1).T
check = daily_concept_cont.diff()
diff_df = daily_concept_cont.diff().describe().T

# 观察650个概念和686个概念的差异
len(daily_concept_list)
total_concept_list = daily_concept_cont.columns.tolist()
set(total_concept_list).difference(set(daily_concept_list))

output_dict = {
    '统计数据': res,
    '每日diff变化值': diff_df,
    '每日增量剔除概念': drop_df
}
from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(output_dict, '/data/user/015614/junkData/', '概念统计数据.xlsx')

# test
fpath = '/data/user/015614/daily/basic/basic_wind_sw_history3/BlockData/each_block/8841297.WI.pkl'
check = pd.read_pickle(fpath)