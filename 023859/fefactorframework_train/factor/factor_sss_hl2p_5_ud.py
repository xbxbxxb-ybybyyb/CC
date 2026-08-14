# h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_sss_hl2p_5_ud(BaseFactor):
    strategy_name = "neptune"
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    factor_period = int(factor_name.split('_')[-2])
    factor_type = factor_name.split('_')[-1]
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "sss"  # 开发人员姓名
    factor_explain = "日频K线比例因子" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = []
    t_1_factor_data = [{'name': 'MD',
                        'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
                        'lag': factor_period+5,
                        'column': ['amt','high','low','open','close','pre_close']}]
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        factor_name=self.factor_name
        factor_period = self.factor_period
        factor_type = self.factor_type
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            md = database['MD']
            md['ratio'] = (md['high'] - md['low']) * 100 / md['pre_close']
            md['ratio'] = md['ratio'].clip(lower=-10, upper=10)
            md.loc[md['amt'] == 0, 'ratio'] = np.nan

            if factor_type == 'mean':
                ratio = md['ratio'].unstack().rolling(factor_period, min_periods=1).mean()
            elif factor_type == 'std':
                ratio = md['ratio'].unstack().rolling(factor_period, min_periods=1).std()
            elif factor_type == 'cv':
                ratio = md['ratio'].unstack().rolling(factor_period, min_periods=1).std() / md[
                    'ratio'].unstack().rolling(factor_period, min_periods=1).mean().round(8).replace(0, np.nan)
            elif factor_type == 'ls':
                long = md['ratio'].unstack().rolling(factor_period, min_periods=1).mean()
                short = md['ratio'].unstack().rolling(int(factor_period // 5), min_periods=1).mean()
                ratio = short - long
            elif factor_type == 'max':
                ratio = md['ratio'].unstack().rolling(factor_period, min_periods=1).max()
            elif factor_type == 'min':
                ratio = md['ratio'].unstack().rolling(factor_period, min_periods=1).min()
            elif factor_type == 'ud':
                max = md['ratio'].unstack().rolling(factor_period, min_periods=1).max()
                min = md['ratio'].unstack().rolling(factor_period, min_periods=1).min()
                ratio = max - min
            elif factor_type == 'mud':
                mean = md['ratio'].unstack().rolling(factor_period, min_periods=1).mean()
                max = md['ratio'].unstack().rolling(factor_period, min_periods=1).max()
                min = md['ratio'].unstack().rolling(factor_period, min_periods=1).min()
                ratio = (mean - min) / (max - min).round(8).replace(0, np.nan)
            elif factor_type == 'lud':
                last = md['ratio'].unstack()
                max = md['ratio'].unstack().rolling(factor_period, min_periods=1).max()
                min = md['ratio'].unstack().rolling(factor_period, min_periods=1).min()
                ratio = (last - min) / (max - min).round(8).replace(0, np.nan)
            df = pd.DataFrame(ratio.stack())
            df.columns = [factor_name]
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
