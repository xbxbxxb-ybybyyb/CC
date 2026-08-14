# coding: utf-8
# Author：fengchi863
# Date ：2022/9/5 20:43

"""
保存Wind数据大小
"""

import sys
sys.path.append('/data/user/015614/Lucien/')
from xquant.factordata import FactorData
from tqdm import tqdm
import pandas as pd
from LucienUtil.FileUtil import FileUtil
from dataApi import tradeDate

block_path = '/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/'
fd = FactorData()
# start_date = 20150101
# end_date = 20221027 # TODO：每次重跑这里要改
start_date = 20221028
end_date = 20230906
date_list = tradeDate.get_date_range(start_date, end_date)

wind_concept_list = FileUtil.read_list(block_path, '最新2015至今全量Wind列表.pkl')
sw2_concept_list = FileUtil.read_list('/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/', '最新2015至今全量申万二级行业列表.pkl')
sw20211_list = pd.read_excel('/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/申万一级行业2021版.xlsx', index_col=0).index.tolist()
sw20141_list = pd.read_excel('/data/user/015614/daily/basic/basic_wind_sw_history2/BlockData/申万一级行业2014版.xlsx', index_col=0).index.tolist()
sw1_all_list = list(set(sw20211_list + sw20141_list))
sw12_concept_list = sw2_concept_list + sw1_all_list
# %% 获取Wind概念涨跌幅（2015-2022 1.5h）
for date in tqdm(date_list):
    wind_daily_data = fd.get_factor_value('WIND_AIndexWindIndustriesEOD',
                                          TRADE_DT=[date],
                                          S_INFO_WINDCODE=wind_concept_list)[['TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_PCTCHANGE']]
    wind_daily_data = wind_daily_data.set_index('S_INFO_WINDCODE')[['S_DQ_PCTCHANGE']]
    wind_daily_data.columns = ['pctchg']
    FileUtil.save_df2pkl(wind_daily_data, block_path + 'daily_wind_factor/', f'{date}.pkl')

#%% 获取申万二级行业涨跌幅（2015-2022 10min）
# for date in tqdm(date_list):
#     sw_daily_data = fd.get_factor_value('WIND_ASWSIndexEOD',
#                                         TRADE_DT=[date],
#                                         factors=['TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_CLOSE', 'S_DQ_PRECLOSE'],
#                                         S_INFO_WINDCODE=sw12_concept_list)
#     sw_daily_data['S_DQ_PCTCHANGE'] = (sw_daily_data['S_DQ_CLOSE'] / sw_daily_data['S_DQ_PRECLOSE'] - 1) * 100
#     sw_daily_data = sw_daily_data.set_index('S_INFO_WINDCODE', drop=True)[['S_DQ_PCTCHANGE']]
#     sw_daily_data.columns = ['pctchg']
#     FileUtil.save_df2pkl(sw_daily_data, block_path + 'daily_sw_factor/', f'{date}.pkl')