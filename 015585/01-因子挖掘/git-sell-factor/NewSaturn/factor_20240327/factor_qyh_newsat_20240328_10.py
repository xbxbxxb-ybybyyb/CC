import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_newsat_20240328_10(BaseFactor):
    strategy_name = "saturn/sell"
    factor_name = "qyh_newsat_20240328_10"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "买1是否离最新价更近在时间上的集中度" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "买单强度-挂单价格激进度" # 逻辑类别
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
        tick_df['factor'] = np.sign(abs(tick_df['Sell1Price'] - tick_df['LastPx']) - abs(tick_df['Buy1Price'] - tick_df['LastPx']))
        # if zcz:
        #     tick_df['factor'] = tick_df['factor']/2
        if tick_df['factor'].empty:
            res =  np.nan
        else:
            if abs(tick_df['factor'].mean()) > 0.0001:
                res =  tick_df['factor'].std() / tick_df['factor'].mean()
            else:
                res =  np.nan
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
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            return pd.Series(factor_dict)