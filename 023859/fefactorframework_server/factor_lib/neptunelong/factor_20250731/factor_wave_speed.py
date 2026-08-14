import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_wave_speed(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "wave_speed"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "根据交易量得到当日的潮汐，计算潮起到潮落收益率变化的平均速度" # 因子逻辑解释
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

    def group_wave_stat(self,group):
        group_tmp = group[group['LastPx'] > 0]
        if len(group_tmp) < 13:
            return np.nan
        group_tmp['n_volume'] = group_tmp['VolumeTrade'].shift(-4).rolling(9).sum()
        group_tmp = group_tmp.dropna(subset=['n_volume', 'LastPx'])
        if len(group_tmp) < 3:
            return np.nan
        n_volume = group_tmp['n_volume'].values
        closes = group_tmp['LastPx'].values
        top = np.argmax(n_volume)
        if top in (0, len(n_volume)-1):
            return np.nan
        m = np.argmin(n_volume[:top])
        n_sub = np.argmin(n_volume[top:])
        n = top + n_sub
        if n <= m or np.isclose(closes[m], 0):
            return np.nan
        return (closes[n] - closes[m]) / (closes[m]) / (n - m)
    

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m_cs']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        daily_result = data[['VolumeTrade','LastPx','MDDate']].groupby(['Ticker','MDDate'], group_keys=False).apply(self.group_wave_stat)
        res = daily_result.groupby('Ticker',group_keys=False).mean()
        res = res.to_frame(name=self.factor_name)
        res = pd.concat({data.index[0][0]: res}, names=['dt'])
        # res = res.groupby('dt',group_keys=False).apply(lambda x:(x-x.mean())/x.std())
        # res = res.to_frame(name=self.factor_name)
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