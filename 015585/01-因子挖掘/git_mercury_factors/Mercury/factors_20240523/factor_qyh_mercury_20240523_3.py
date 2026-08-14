import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_mercury_20240523_3(BaseFactor):
    strategy_name = "mercury"
    factor_name = "qyh_mercury_20240523_3"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "919之前,买1量的偏度" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "放量角度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTickab919']
    xdb_data = []
    def pre_calculate_T_N_data(self, database):
        return database
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            dt, ticker = database['TTickab919'].index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            database['zcz'] = zcz
            return database
    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['TTickab919']
            tick_df['factor'] = tick_df['Buy1Price']/(tick_df['pre_close'])
            zcz = database['zcz']
            if zcz:
                tick_df['factor'] = (tick_df['factor']-1)/2+1
            res = tick_df['factor'].tail(1).mean()
            factor_dict = {self.factor_name: res}
            return pd.Series(factor_dict)