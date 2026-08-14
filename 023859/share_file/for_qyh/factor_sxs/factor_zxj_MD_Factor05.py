import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

# Word中的Factor05

class factor_zxj_MD_Factor05(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_MD_Factor05"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "通过风险度量加权股票的超额收益。"
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 25,
         'column': ['high', 'low', 'close','pre_close', 'pct_chg']
    }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database
        else:
            df_md = database['MD_CHINA_STOCK_DAILY_WIND']
            # --- 参数定义 ---
            d = 10
            m = 15
            risk_indicator = 'tr' # 可选 'tr' 或 'turnover'

            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            # --- 1. 准备数据 ---
            high = df_md['high'].unstack()
            low = df_md['low'].unstack()
            close = df_md['close'].unstack()
            pct_chg = (df_md['pct_chg'] / 100).unstack()
            prev_close = df_md['pre_close'].unstack()

            # --- 2. 计算风险指标 R_t ---
            if risk_indicator == 'tr':
                #prev_close = close.shift(1)
                term1 = high - low
                term2 = abs(high - prev_close)
                term3 = abs(low - prev_close)
                numerator = np.maximum(term1, np.maximum(term2, term3))
                denominator = prev_close
                r_pivot = numerator / denominator.replace(0, np.nan)
            
            elif risk_indicator == 'turnover':
                 r_pivot = df_md['turn'].unstack()
            else:
                raise ValueError(f"Unsupported risk_indicator: '{risk_indicator}'")

            # --- 3. 计算风险调整因子 Risk_t ---
            r_rolling_mean = r_pivot.rolling(window=d, min_periods=d).mean()
            risk_df = r_rolling_mean - r_pivot
            
            # --- 4. 计算超额收益 ---
            market_return = pct_chg.mean(axis=1)
            excess_return_df = pct_chg.subtract(market_return, axis='index')

            # --- 5. 计算最终因子 ---
            product_df = risk_df * excess_return_df
            half_life = m / 2
            composite_alpha = product_df.ewm(halflife=half_life, min_periods=m, adjust=False).mean()

            # --- 结果转换 ---
            factor_series = composite_alpha.stack()
            df_result = factor_series.to_frame(name=self.factor_name)
            # -------------------------------------------------------------------------------------------------------------------

            database['pre_T_N'] = df_result
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database.get("skip", False):
            return pd.Series({self.factor_name: np.nan})
        else:
            return database['pre_T_N']
