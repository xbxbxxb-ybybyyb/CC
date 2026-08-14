import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_volume_time_smooth(BaseFactor):
    strategy_name = "neptune"
    factor_name = "volume_time_smooth"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "用等交易量划分交易时段，4个时段时长的标准差" # 因子逻辑解释
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

    def vol_time_stat(self,group):
        total_volume = group['TotalVolumeTrade'].values
        if np.all(total_volume == 0):
            md_time = group['MDTime'].values
            time_quantiles = np.percentile(md_time, [0, 25, 50, 75, 100])
            group['volume_time'] = pd.cut(
                md_time, 
                bins=time_quantiles, 
                labels=range(4),
                duplicates='drop'
            )
        else:
            quantile_list = [total_volume[-1] * (i / 4) for i in range(5)]
            group['volume_time'] = pd.cut(
                total_volume, 
                bins=quantile_list, 
                labels=range(4),
                duplicates='drop'
            )
        
        
        vol_count_std = group.groupby('volume_time')['pct_chg'].count().std()
        
        return vol_count_std


    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m_cs']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        data = data[data['MDDate']==data['MDDate'].max()]
        
        vol_count_std = data.groupby('Ticker').apply(self.vol_time_stat)

        res = vol_count_std.to_frame(self.factor_name)
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