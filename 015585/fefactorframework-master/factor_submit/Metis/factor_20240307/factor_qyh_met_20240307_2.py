# 45,-0.049
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_met_20240307_2(BaseFactor):
    strategy_name = "metis"
    factor_name = "qyh_met_20240307_2"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "T日逼近涨停价后，价格涨幅*成交量相对于前3天tick平均值的涨幅 的中位数" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "放量角度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTickab_MetisAll']
    xdb_data = [
        {
       'name': 'xdb_tick1s', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s, xdb_tickex
       'lag': 3 # 回看日期，N为往前回看1~N天
    }]
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        tick1s_df = database['xdb_tick1s']
        tick1s_df = filter_930(tick1s_df)
        res = tick1s_df['VolumeTrade'].mean() # 得到tick1s计算的平均成交量
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
        return database
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            tick_df = database['TTickab_MetisAll']
            tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
            database['TTickab_MetisAll'] = filter_930(tick_df)

            return database
    def calculate(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N'][self.factor_name].values[0]
            tick_df = database['TTickab_MetisAll']
            t_fzt = tick_df[tick_df['LastPx'] >= round_(tick_df['LastPx'].max()-0.02, 2)]['MDTime'].min()  # 首次逼近涨停时间
            tick_df = tick_df[tick_df['MDTime'] >= t_fzt]
            #
            res3 = ((tick_df['LastPx'] / tick_df['pre_close']) * (tick_df['VolumeTrade'])).median()
            factor_dict = {self.factor_name: res3 / res if round_(res,5) > 0 else np.nan}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

