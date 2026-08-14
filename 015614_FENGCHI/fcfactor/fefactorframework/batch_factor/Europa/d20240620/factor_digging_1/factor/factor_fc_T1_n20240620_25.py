# coding: utf-8
# Author：fengchi863
# Date ：2024/3/8 10:26

import numpy as np
import pandas as pd
import sys
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

param1, param2, param3 = 250, 130, 60 # 配置超参数

class factor_fc_T1_n20240620_25(BaseFactor):
    owner = 'fc'
    strategy_name = "europa"
    factor_name = sys._getframe().f_code.co_name[7:]
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = ""
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = "是"

    t_day_data = ['TTickab']
    xdb_data = [
       #  {
       # 'name': 'xdb_tickex', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s, xdb_tickex
       # 'lag': 1}
    ]
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 10,  # 注意为正数
         'column': ['vwap']}
    ]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database

        md_data = database['MD_CHINA_STOCK_DAILY_WIND']  # 和上面t-1_factor_data的name一致
        database['pre_T_N'] = pd.DataFrame({self.factor_name: md_data['vwap']})
        return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        else:
            # database['TTickab'] = filter_930(database['TTickab'])
            # database['TTickab'] = filter_930(database['TTickab'])
            return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            tick_df = database['TTickab']

            dt, Ticker = tick_df.index[0]
            zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
            zt_time = tick_df['MDTime'].max()
            pre_close = tick_df['pre_close'].iloc[0]

            tick_df = tick_df[(tick_df['NumTrades'] > 0)]
            tick_df = tick_df[tick_df['MDTime'] >= 93000000]

            time_itvl = param1
            tick_df['HighPx'] = tick_df['LastPx'].rolling(time_itvl, min_periods=1).max()
            tick_df['LowPx'] = tick_df['LastPx'].rolling(time_itvl, min_periods=1).min()
            tick_df['h2l'] = tick_df['HighPx'] / tick_df['LowPx']

            if len(tick_df) > 0:
                res = np.percentile(tick_df["h2l"][-param2:], param3) - np.percentile(tick_df["h2l"][-param2:], 100-param3)
            else:
                res = None
            # print(res)
            factor_dict = {self.factor_name: res}
            return pd.Series(factor_dict)  # 纯h5文件的T-1_Factor直接返回df
