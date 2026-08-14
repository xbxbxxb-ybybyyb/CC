import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_sparkle_vol(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "sparkle_vol"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "一天内成交量出现激增的时刻,计算这些时刻及之后4分钟的波动率,统计全天的均值" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
       'name': 'xdb_tick1m_cs', # xdb_order1m, xdb_tick1m
       'lag': 3 # 回看日期，N为往前回看1~N天
    }]

    def sparkle_times(self,group):
        group['VolumeTrade_diff'] = group['VolumeTrade'].diff().fillna(0)
        volume_mean = group['VolumeTrade_diff'].mean()
        volume_std = group['VolumeTrade_diff'].std()
        
        group['flag'] = (group['VolumeTrade_diff']>=volume_mean+volume_std) & (group['MDTime']>94500000) & (group['MDTime']<144500000)
        group['pct_chg'] = group['LastPx'].pct_change()
        group['vol_5'] = group['pct_chg'].shift(-4).rolling(5).std()
        vol_mean = group[group['flag']==1]['vol_5'].mean()

        return vol_mean

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m_cs']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        data = data[data['MDDate']==data['MDDate'].max()]
        vol_mean = data.groupby('Ticker').apply(self.sparkle_times)


        res = vol_mean.to_frame(self.factor_name)
        dt = data.index[0][0]
        res = pd.concat({dt:res}, names=['dt'])

        
        # -------------------------------------------------------------------------------------------------------------------
        database['pre_T_N'] = res[[self.factor_name]]
        return database

    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res