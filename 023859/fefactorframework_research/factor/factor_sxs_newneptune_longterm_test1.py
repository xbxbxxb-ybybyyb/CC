# Word中的Factor01
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_alpha_composite_stable_reversal(BaseFactor):
    strategy_name = "neptune"
    factor_name = "alpha_composite_stable_reversal"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = ""  # 开发人员姓名
    factor_explain = ""
    zcz_adjusted = "否"  # 是否针对注册制调整：是/否
    logic_type = ""  # 逻辑类别
    low_cost = ""  # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 30,  # window_088=20, window_097=10, lag设置为30
         'column': ['close', 'volume']
         }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database.get("skip", False):
            return database
        else:
            df_md = database['MD_CHINA_STOCK_DAILY_WIND']
            # --- 参数定义 ---
            window_088 = 20
            window_097 = 10
            w_reversal = 0.5
            w_stability = 0.5

            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            # --- 1. 计算基础因子 ---
            close = df_md['close'].unstack()
            volume = df_md['volume'].unstack()

            factor_reversal = -1 * (close.pct_change(periods=window_088) * 100)
            factor_stability = -1 * (volume.rolling(window=window_097).std())

            # --- 2. 因子标准化 (截面排序) ---
            rank_reversal = factor_reversal.rank(axis=1, pct=True)
            rank_stability = factor_stability.rank(axis=1, pct=True)

            # --- 3. 加权组合 ---
            composite_alpha = (w_reversal * rank_reversal) + (w_stability * rank_stability)

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
