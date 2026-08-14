import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_vol_vol_prem(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "vol_vol_prem"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "日内滚动波动率的波动率较高时的流动性溢价水平" # 因子逻辑解释
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


    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m_cs']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        data = data[data['MDDate']==data['MDDate'].max()]
        data['ValueTrade'] = data.groupby('Ticker', group_keys=False)['TotalValueTrade'].diff().fillna(0)
        data['pct_chg'] = data.groupby('Ticker')['LastPx'].pct_change()
        data['vol'] = data.groupby('Ticker')['pct_chg'].transform(lambda x: x.rolling(5).std())
        data['vol_vol'] = data.groupby('Ticker')['vol'].transform(lambda x: x.rolling(5).std())

        vol_vol_mean = data['vol_vol'].groupby('Ticker').mean()
        data['vol_vol_mean'] = data.index.get_level_values(1).map(vol_vol_mean)
        vol_vol_volume = data[data['vol_vol']>=data['vol_vol_mean']].groupby('Ticker')['VolumeTrade'].mean() / data.groupby('Ticker')['VolumeTrade'].mean()
        vol_vol_value = data[data['vol_vol']>=data['vol_vol_mean']].groupby('Ticker')['ValueTrade'].mean() / data.groupby('Ticker')['ValueTrade'].mean()

        prem = vol_vol_value - vol_vol_volume
        res = prem.to_frame(self.factor_name)
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