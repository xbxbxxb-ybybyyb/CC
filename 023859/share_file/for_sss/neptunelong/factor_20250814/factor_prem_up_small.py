import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_prem_up_small(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "prem_up_small"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "在缩量上涨时的流动性溢价（买入意愿强度）" # 因子逻辑解释
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
        data['ValueTrade'] = data.groupby(['Ticker','MDDate'], group_keys=False)['TotalValueTrade'].diff().fillna(0)
        data['volume_near'] = data['VolumeTrade'].groupby('Ticker').transform(lambda x: x.shift(-2).rolling(5).sum())
        data['pctchg_5'] = data['LastPx'].groupby('Ticker').pct_change(5)
        data['volume_flag'] = (data['volume_near'] > data['volume_near'].groupby('Ticker').shift(1)).astype(int)
        
        vol_up_large = (data[(data['volume_flag']>0)&(data['pctchg_5']>0)]['VolumeTrade'].groupby('Ticker').mean()) / data['VolumeTrade'].groupby('Ticker').mean()
        value_up_large = (data[(data['volume_flag']>0)&(data['pctchg_5']>0)]['ValueTrade'].groupby('Ticker').mean()) / data['ValueTrade'].groupby('Ticker').mean()
        prem_up_large = value_up_large - vol_up_large

        
        res = prem_up_large.to_frame(self.factor_name)
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