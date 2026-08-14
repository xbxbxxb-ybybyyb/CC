import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_below_ice_vol(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "below_ice_vol"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "使用前一分钟累积挂单量估计成交量，实际成交量小于估计成交量的对应时刻的分钟收益率标准差" # 因子逻辑解释
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
    
    def order_ice(self,group):
        group['pct_chg'] = group['LastPx'].pct_change().replace([np.inf,-np.inf],np.nan)
        group['TotalQty'] = np.minimum(group['TotalBidQty'],group['TotalOfferQty']).shift(1)
        turn_rate = (group['VolumeTrade'] / group['TotalQty']).replace([np.inf,-np.inf],np.nan).mean()

        group = group.set_index('MDTime')
        group['TurnVolume'] = group['TotalQty'] * turn_rate
        group['flag'] = (group['VolumeTrade'] > group['TurnVolume']).astype(int)


        below_vol = group[group['flag']==0]['pct_chg'].std()
        
        return below_vol

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m_cs']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        data = data[data['MDDate']==data['MDDate'].max()]
        
        below_vol = data.groupby('Ticker').apply(self.order_ice)

        res = below_vol.to_frame(self.factor_name)
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