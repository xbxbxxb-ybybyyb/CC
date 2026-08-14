from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
import sys

param1, param2 = "VALUE_DIFF_MED_TRADER", 60 # 配置超参数

def mean_(factor_series):
    return factor_series[~np.isnan(factor_series)].mean()

class factor_fc_n20250403_117(BaseFactor):
    owner = 'fc'
    strategy_name = "neptune"
    factor_name = sys._getframe().f_code.co_name[7:]
    fill_na_value = 1e8
    need_pre_calculate_T_N = True
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否（本因子需要调整，为简单起见未加入注册制部分）
    logic_type = "价格形态" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'AShareMoneyFlow', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5',
         'lag': 360,
         'column': [param1]
    }]
    t_1_factor_data_types = ['AShareMoneyFlow']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        else:
            df_ori = database['AShareMoneyFlow']
            res = df_ori[param1].unstack().rolling(param2, 1).apply(mean_).stack()

            database['pre_T_N'] = pd.DataFrame({self.factor_name: res})
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori  # 纯h5文件的T-1_Factor直接返回df
