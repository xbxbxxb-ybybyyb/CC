# h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_sss_chipdown_5_ls_20(BaseFactor):
    strategy_name = "neptune"
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    chip_period = int(factor_name.split('_')[-3])
    factor_type = factor_name.split('_')[-2]
    factor_period = int(factor_name.split('_')[-1])

    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "sss"  # 开发人员姓名
    factor_explain = "日频筹码因子" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    t_day_data = []
    t_1_factor_data = [{'name': 'MD',
                        'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
                        'lag': factor_period+chip_period+5,
                        'column': ['turn','vwap','close','adjfactor']}]
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        factor_name=self.factor_name
        chip_period = self.chip_period
        factor_type = self.factor_type
        factor_period = self.factor_period
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            md = database['MD']
            md['turn'] = md['turn'] / 100
            md['vwap'] = md['vwap'] * md['adjfactor']
            md['close'] = md['close'] * md['adjfactor']

            md['up_atr_sum'] = 0
            md['down_atr_sum'] = 0

            md['rc0'] = md['vwap'] / md['close'] - 1
            md['atr0'] = md['turn']
            md['up_atr_sum'] = md['up_atr_sum'] + md['atr0'] * (md['rc0'] > 0).astype(float)
            md['down_atr_sum'] = md['down_atr_sum'] + md['atr0'] * (md['rc0'] < 0).astype(float)
            for i in range(1, chip_period + 1):
                md['rc%s' % i] = md['vwap'].unstack().shift(i).stack() / md['close'] - 1
                md['atr%s' % i] = (md['atr%s' % (i - 1)].unstack().shift(1).stack()) * (1 - md['turn'])
                md['up_atr_sum'] = md['up_atr_sum'] + md['atr%s' % i] * (md['rc%s' % i] > 0).astype(float)
                md['down_atr_sum'] = md['down_atr_sum'] + md['atr%s' % i] * (md['rc%s' % i] < 0).astype(float)
            md['value'] = md['down_atr_sum']



            if factor_type == 'mean':
                value = md['value'].unstack().rolling(factor_period, min_periods=1).mean()
            elif factor_type == 'std':
                value = md['value'].unstack().rolling(factor_period, min_periods=1).std()
            elif factor_type == 'cv':
                value = md['value'].unstack().rolling(factor_period, min_periods=1).std() / md['value'].unstack().rolling(factor_period, min_periods=1).mean().round(8).replace(0, np.nan)
            elif factor_type == 'ls':
                long = md['value'].unstack().rolling(factor_period, min_periods=1).mean()
                short = md['value'].unstack().rolling(int(factor_period // 5), min_periods=1).mean()
                value = short - long
            elif factor_type == 'max':
                value = md['value'].unstack().rolling(factor_period, min_periods=1).max()
            elif factor_type == 'min':
                value = md['value'].unstack().rolling(factor_period, min_periods=1).min()
            elif factor_type == 'ud':
                max = md['value'].unstack().rolling(factor_period, min_periods=1).max()
                min = md['value'].unstack().rolling(factor_period, min_periods=1).min()
                value = max - min
            elif factor_type == 'mud':
                mean = md['value'].unstack().rolling(factor_period, min_periods=1).mean()
                max = md['value'].unstack().rolling(factor_period, min_periods=1).max()
                min = md['value'].unstack().rolling(factor_period, min_periods=1).min()
                value = (mean - min) / (max - min).round(8).replace(0, np.nan)
            elif factor_type == 'lud':
                last = md['value'].unstack()
                max = md['value'].unstack().rolling(factor_period, min_periods=1).max()
                min = md['value'].unstack().rolling(factor_period, min_periods=1).min()
                value = (last - min) / (max - min).round(8).replace(0, np.nan)
            df = pd.DataFrame(value.stack())
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
