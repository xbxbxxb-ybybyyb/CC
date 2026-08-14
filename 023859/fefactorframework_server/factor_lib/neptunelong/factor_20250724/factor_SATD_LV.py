import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_SATD_LV(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "SATD_LV"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "每日成交量最大的10\%分钟的标准化单均金额" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
       'name': 'xdb_tick1m', # xdb_order1m, xdb_tick1m
       'lag': 3 # 回看日期，N为往前回看1~N天
    }]

    def volume_ATD_stat(self,group):
        values = group.values
        values = values[(values[:,0]>0)&(values[:,1]>0)]
        ATD = values[:,0].sum() / values[:,1].sum()
        q90 = np.nanpercentile(values[:,2],90)
        SATD_LV = values[values[:,2]>=q90][:,0].sum() / values[values[:,2]>=q90][:,1].sum() / ATD

        return np.array([SATD_LV])
    

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        data.index.names = ['date', 'code']
        data['ValueTrade'] = data.groupby(['code','MDDate'], group_keys=False)['TotalVolumeTrade'].diff().fillna(0)
        daily_result = data[['ValueTrade','NumTrades','VolumeTrade','MDDate']].groupby(['code','MDDate'], group_keys=False).apply(self.volume_ATD_stat)
        daily_result = pd.DataFrame(daily_result.to_list(),index=daily_result.index,columns=['SATD_LV'])

        res = daily_result.groupby('code',group_keys=False).mean()
        res = res.groupby('date',group_keys=False).apply(lambda x: (x-x.mean())/x.std())

        # -------------------------------------------------------------------------------------------------------------------
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
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
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)