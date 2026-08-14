import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_newsat_20240509_4(BaseFactor):
    strategy_name = "saturn/sell"
    factor_name = "qyh_newsat_20240509_4"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "委买金额/成交的std的和在上涨/下跌时候的差异" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-总量强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = [
        {
       'name': 'xdb_tick1s', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s,xdb_tickex
       'lag': 1 # 回看日期，N为往前回看1~N天
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        tick_df = database['xdb_tick1s']
        dt, ticker = tick_df.index[0]
        dt = dt.strftime('%Y%m%d')
        zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
        tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
        tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
        tick_df = filter_930(tick_df)  # 选择连续竞价阶段的tick数据
        # tick_df = tick_df[tick_df['MDTime'] <= 143000000]
        tick_df = tick_df[tick_df['MDTime'] < 145700000]
        tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
        # tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
        # tick_df['factor'] = (tick_df['WeightedAvgBidPx'] - tick_df['WeightedAvgBidPx'].shift(1))/tick_df['pre_close']
        tick_df1 = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]
        tick_df1['factor'] = (tick_df1['buy_amt']) / tick_df1['ValueTrade'].std()
        tick_df2 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1)]
        tick_df2['factor'] = (tick_df2['buy_amt']) / tick_df2['ValueTrade'].std()
        # if zcz:
        res = tick_df1['factor'].sum() - tick_df2['factor'].sum()
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
            factor_dict = {self.factor_name: res1}
            return pd.Series(factor_dict)