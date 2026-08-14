# coding: utf-8
# Author：fengchi863
# Date ：2024/3/8 10:26

import numpy as np
import pandas as pd
import sys
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

param1, param2, param3, param4 = "Buy3Price", "NumTrades", 15, 0.01 # 配置超参数

class factor_fc_ttickab_n20240801_521(BaseFactor):
    owner = 'fc'
    strategy_name = "europa"
    factor_name = sys._getframe().f_code.co_name[7:]
    fill_na_value = 0
    need_pre_calculate_T_N = False
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

    ]
    t_1_factor_data_types = []

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
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
            tick_df = database['TTickab']

            dt, Ticker = tick_df.index[0]
            zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
            zt_time = tick_df['MDTime'].max()
            pre_close = tick_df['pre_close'].iloc[0]

            target_col = param1
            calc_col = param2
            target_count = param3
            target_pctchg = param4

            # tick_df = tick_df[(tick_df['NumTrades'] > 0)]
            tick_df = tick_df[tick_df['MDTime'] >= 92500000]
            if len(tick_df) == 0:
                factor_dict = {self.factor_name: 1}
                return pd.Series(factor_dict)  # 纯h5文件的T-1_Factor直接返回df
            tick_df['new_time'] = tick_df.MDTime.apply(lambda x: x // 10000)
            tick_df_new = tick_df.groupby('new_time')[[target_col]].mean()

            # 计算拐点
            turn_point_list = list()
            turn_time_list = list()
            turn_num, last_point, last_turn_px, last_turn_time = 0, 0, 0, 0
            last_idx = tick_df_new.index[0]
            is_first_turn = True

            for idx, row in tick_df_new[[target_col]][::-1].iterrows():
                if is_first_turn:
                    last_point = row[target_col]
                    last_turn_px = row[target_col]
                    last_turn_time = idx
                    turn_point_list.append(last_turn_px)
                    turn_time_list.append(last_turn_time)
                    is_first_turn = False
                else:
                    if row[target_col] < last_turn_px or last_turn_px == 0: # 寻找拐点
                        last_turn_px = row[target_col]
                        last_turn_time = idx
                        turn_num = 0
                        if idx == last_idx: # 遍历完成
                            turn_point_list.append(last_turn_px)
                            turn_time_list.append(last_turn_time)
                    else:   # 向上的拐点
                        if turn_num >= target_count and (last_point - last_turn_px) / pre_close > target_pctchg:
                            turn_point_list.append(last_turn_px)
                            turn_time_list.append(last_turn_time)
                            break
                        else:
                            turn_num += 1

            col = calc_col
            tick_df[col + '_new'] = tick_df[col].diff().diff().fillna(0)

            last_turn_time = turn_time_list[-1]
            part_tick_df = tick_df.query(f'new_time >= {last_turn_time}')

            # 计算因子值
            res = np.divide(part_tick_df[col + '_new'].std(), tick_df[col + '_new'].std())
            # print(res)
            factor_dict = {self.factor_name: res}
            return pd.Series(factor_dict)  # 纯h5文件的T-1_Factor直接返回df
