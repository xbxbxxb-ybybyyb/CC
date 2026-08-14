import pandas as pd 
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_skew_ret(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "skew_ret"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "计算每日市场收益偏度为正时股票的对数偏离度的总和" # 因子逻辑解释
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

    def skew_ret(self,df):
        data = df.copy()
        data['pct_chg'] = data.groupby('code', group_keys=False)['LastPx'].diff() / data['LastPx']
        
        grouped_mdtime = data.groupby('MDTime')['pct_chg']
        # 计算上涨/下跌平均 pct_chg（一次分组，两次聚合）
        up_base = grouped_mdtime.apply(lambda x: x[x > 0].mean())  # 上涨时段均值
        down_base = grouped_mdtime.apply(lambda x: x[x < 0].mean())  # 下跌时段均值
        
        data['up_base'] = data['MDTime'].map(up_base)
        data['down_base'] = data['MDTime'].map(down_base)
        
        data['bias'] = np.where(
            data['pct_chg'] > 0,  # 上涨时：pct_chg - up_base
            data['pct_chg'] - data['up_base'],
            np.where(
                data['pct_chg'] < 0,  # 下跌时：pct_chg - down_base
                data['pct_chg'] - data['down_base'],
                0  # 平盘时：0
            )
        )
        
        skew = data.groupby('MDTime')['bias'].skew()
        data['skew'] = data['MDTime'].map(skew)
        
        filtered = data[(data['skew'] > 0)]
        if len(filtered > 0):
            daily_result = filtered.assign(log_bias=np.sign(filtered['bias'])*np.log(1+abs(filtered['bias']))).groupby('code', group_keys=False)['log_bias'].sum()
        else:
            daily_result = pd.Series(np.nan,index=data.index)
        return daily_result
    

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        data.index.names = ['date', 'code']
        daily_result = data.groupby('MDDate',group_keys=True).apply(self.skew_ret)
        res = daily_result.groupby('code',group_keys=False).mean()
        res = res.groupby('date',group_keys=False).apply(lambda x:(x-x.mean())/x.std())

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