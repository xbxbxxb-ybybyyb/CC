import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

# Word中的Factor03

class factor_zxj_MD_Factor03(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_MD_Factor03"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"  # 开发人员姓名
    factor_explain = "成交量、换手率与corr(vwap/high, high)的加权组合"
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80, # 最大的window是15, lag设置为25
         'column': ['vwap', 'high', 'volume', 'close', 'adjfactor', 'turn']
    }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database
        else:
            df_md = database['MD_CHINA_STOCK_DAILY_WIND']
            df_md = df_md[(df_md['volume']>0)&(df_md['vwap']>0)&(df_md['high']>0)]
            # --- 参数定义 ---
            corr_window = 15

            def f_calc_std(factor_series):
                return np.std(factor_series[~np.isnan(factor_series)], ddof=1)
            

            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            # --- 1. 准备数据 ---
            # vwap = df_md['vwap'].unstack()
            # high = df_md['high'].unstack()
            # volume = df_md['volume'].unstack()
            # close = df_md['close'].unstack()
            # adjfactor = df_md['adjfactor'].unstack()
            # turn = df_md['turn'].unstack()

            # --- 2. 计算基础因子 ---
            
            # term1_alpha1 = vwap / high.replace(0, np.nan)
            rank_alpha1 = (df_md['vwap'].unstack().rolling(window=10, min_periods=3).corr(df_md['high'].unstack()))

            # alpha3_factor = -volume.rolling(window=5).apply(f_calc_std)

            # adj_close = close * adjfactor
            # ctc_factor = adj_close.rolling(window=corr_window, min_periods=3).corr(turn).clip(lower=-1,upper=1)

            # --- 3. 因子标准化与组合 ---
            # rank_alpha1 = alpha1_factor.rank(axis=1, pct=True)
            # rank_alpha3 = alpha3_factor.rank(axis=1, pct=True)
            # rank_ctc = ctc_factor.rank(axis=1, pct=True)

            composite_alpha = rank_alpha1 #+ rank_alpha3 - rank_ctc

            # --- 结果转换 ---
            factor_series = composite_alpha.stack().clip(lower=-1,upper=1)
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
