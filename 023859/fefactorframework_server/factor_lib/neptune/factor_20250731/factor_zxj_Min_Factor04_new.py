import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Min_Factor04_new(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Min_Factor04_new"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj" 
    factor_explain = "开盘前半小时净委买变化率波动率-Lv5"
    zcz_adjusted = "否" 
    logic_type = "" 
    low_cost = ""
    t_day_data = []
    
    xdb_data = [
        {
            'name': 'xdb_tick1m_cs', 
            'lag': 1 
        }
    ]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
            
        data = database['xdb_tick1m_cs'].copy()  
        
        df_30min = data[(data['MDTime'] >= 93000000) & (data['MDTime'] < 100000000)].copy()

        buy_cols = [f'Buy{i}OrderQty' for i in range(1, 6)]
        sell_cols = [f'Sell{i}OrderQty' for i in range(1, 6)]
        
        df_30min = df_30min.reset_index()
        df_30min = df_30min.sort_values(by=['Ticker', 'MDTime'])

        buy_diffs = df_30min.groupby('Ticker')[buy_cols].diff()
        sell_diffs = df_30min.groupby('Ticker')[sell_cols].diff()

        net_buy_change = buy_diffs.sum(axis=1) - sell_diffs.sum(axis=1)
        
        rate = net_buy_change.div(df_30min['ff_shares'])
        
        rate.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        df_30min['rate_L5'] = rate
        
        final_factor = df_30min.groupby('Ticker')['rate_L5'].std()
        
        res_df = final_factor.to_frame(name=self.factor_name)

        current_date = pd.to_datetime(data.index[0][0])
        res_df['dt'] = current_date
        res_df.reset_index(inplace=True)
        res_df.set_index(['dt', 'Ticker'], inplace=True)    
        
        database['pre_T_N'] = res_df[[self.factor_name]]
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