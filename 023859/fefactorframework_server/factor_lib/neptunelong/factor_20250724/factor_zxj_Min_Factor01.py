# 引入必要的库
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * 

class factor_zxj_Min_Factor01(BaseFactor):
    strategy_name = "neptunelong"
    factor_name = "zxj_Min_Factor01"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  
    factor_explain = " -zscore(order_book_depth) - zscore(avg_bid_ask_spread)" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    t_day_data = []
    #
    xdb_data = [
        {
        'name': 'xdb_tick1m', # 数据源名称
        'lag': 1, # 回看日期
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database

        
        df_minute = database['xdb_tick1m'].copy()

        mid_price = (df_minute['Sell1Price'] + df_minute['Buy1Price']) / 2
        df_minute['relative_spread'] = (df_minute['Sell1Price'] - df_minute['Buy1Price']) / mid_price
      
        df_minute['relative_spread'].replace([np.inf, -np.inf], np.nan, inplace=True)
        daily_spread = df_minute.groupby(['dt', 'Ticker'])['relative_spread'].mean()
        daily_spread.name = 'avg_bid_ask_spread'


        df_minute['total_depth_l1'] = df_minute['Buy1OrderQty'] + df_minute['Sell1OrderQty']
        daily_depth = df_minute.groupby(['dt', 'Ticker'])['total_depth_l1'].mean()
        daily_depth.name = 'order_book_depth'


        tech_result = pd.concat([daily_spread, daily_depth], axis=1)

        def f_calc_std(factor_series):
            return np.std(factor_series[~np.isnan(factor_series)], ddof=1)


        grouped_by_dt = tech_result.groupby(level='dt')

        mean_depth = grouped_by_dt['order_book_depth'].transform('mean')
        std_depth = grouped_by_dt['order_book_depth'].transform(f_calc_std)
        z_depth = (tech_result['order_book_depth'] - mean_depth) / std_depth

        mean_spread = grouped_by_dt['avg_bid_ask_spread'].transform('mean')
        std_spread = grouped_by_dt['avg_bid_ask_spread'].transform(f_calc_std)
        z_spread = (tech_result['avg_bid_ask_spread'] - mean_spread) / std_spread

        liquidity_quality = -z_depth - z_spread

        res = liquidity_quality.to_frame(name=self.factor_name)
        # -------------------------------------------------------------------------------------------------------------------

        database['pre_T_N'] = res
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