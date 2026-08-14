# T+h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
# 逻辑：
class factor_qyh_newsat_20240201_2(BaseFactor):
    owner = 'qyh'
    strategy_name = "saturn/sell"
    factor_name = "qyh_newsat_20240201_2"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "T日s1vwap/过去5日均价的振幅" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否（本因子需要调整，为简单起见未加入注册制部分）
    logic_type = "价格形态" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ["T1mTickab"]
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 10, #注意为正数
         'column': ['close']
    }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            res = df_ori['close'].unstack().rolling(5,1).mean().iloc[[-1]].stack().to_frame(name='res')
            database["pre_T_N"] = res
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        else:
            tick_df = database['T1mTickab']
            dt, ticker = tick_df.index[0]
            tick_df = filter_930(tick_df)
            database['T1mTickab'] = tick_df
            database['dt'] = dt
            database['ticker'] = ticker
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['T1mTickab']
            dt = database['dt']
            ticker = database['ticker']
            tick_df['factor'] = tick_df['TotalValueTrade'] / (tick_df['TotalVolumeTrade']+1e-5) # T日均价
            md_data = database['pre_T_N'][['res']]
            res1 = md_data.query("Ticker == '{}'".format(ticker))['res'].values
            res1 = res1[0] if len(res1) > 0 else np.nan
            tick_df['factor'] = tick_df['factor'] / res1
            #
            res = tick_df['factor'].max() - tick_df['factor'].min()
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
