import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_newsat_20240411_16(BaseFactor):
    strategy_name = "saturn/sell"
    factor_name = "qyh_newsat_20240411_16"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "价格差分在活跃/不活跃时的最小值差异" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "卖单强度-挂单价格激进度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = [
        {
       'name': 'xdb_tickex', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s,xdb_tickex
       'lag': 1 # 回看日期，N为往前回看1~N天
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        tick_df = database['xdb_tickex']
        dt, ticker = tick_df.index[0]
        dt = dt.strftime('%Y%m%d')
        zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
        tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
        tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
        tick_df = filter_930(tick_df)  # 选择连续竞价阶段的tick数据
        # tick_df = tick_df[tick_df['MDTime'] >= 143000000]
        tick_df = tick_df[tick_df['MDTime'] < 145700000]
        tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
        tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
        tick_df1['factor'] = (tick_df1['LastPx'] - tick_df1['LastPx'].shift(1))/tick_df1['pre_close']
        tick_df2['factor'] = (tick_df2['LastPx'] - tick_df2['LastPx'].shift(1))/tick_df2['pre_close']
        if zcz:
            tick_df1['factor'] = (tick_df1['factor']) / 2
            tick_df2['factor'] = (tick_df2['factor']) / 2

        res = tick_df1['factor'].min() - tick_df2['factor'].min()
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
        return database
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            return database
    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res1 = database['pre_T_N'][self.factor_name].values[0]
            # tick_df = database['T1mTickab']
            # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
            # tick_df = filter_930(tick_df)  # 选择连续竞价阶段的tick数据
            # res = tick_df['ValueTrade'].mean()
            factor_dict = {self.factor_name: res1}
            return pd.Series(factor_dict)