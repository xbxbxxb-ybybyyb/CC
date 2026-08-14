import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
def calculate_skewness(data):
    """
    计算数据的样本偏度（无偏估计）

    参数：
    data : list, numpy.ndarray, pandas.Series
        输入的一维数值型数据

    返回：
    float
        样本偏度系数，正数表示右偏，负数表示左偏
    """

    # 转换输入为NumPy数组
    data = np.asarray(data)
    n = data.size

    if n < 3:
        return 0.0

    mean = np.mean(data)
    m2 = np.mean((data - mean) ** 2)  # 二阶中心矩
    m3 = np.mean((data - mean) ** 3)  # 三阶中心矩

    if m2 == 0:
        return 0.0  # 方差为0时所有值相同，偏度定义为0

    # 无偏校正系数
    bias_correction = (n ** 2) / ((n - 1) * (n - 2))

    # 样本偏度计算
    skewness = bias_correction * (m3 / (m2 ** 1.5))

    return float(skewness)


class factor_wj_neptune_20250424_7(BaseFactor):
    strategy_name = "neptune"
    factor_name = "wj_neptune_20250424_7"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "wj"  # 开发人员姓名
    factor_explain = "早盘资金流入量+尾盘资金流入量，5日最大值" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'AShareMoneyFlow',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareMoneyFlow/AShareMoneyFlow.h5',#
         'lag': 80,  # 注意为正数
         'column': ['S_MFD_INFLOW_CLOSE','S_MFD_INFLOW_OPEN','S_MFD_INFLOW']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['AShareMoneyFlow']  # T-1的h5文件类型列表

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['AShareMoneyFlow']  # 和上面t-1_factor_data的name一致


            df_ori['long'] = (df_ori['S_MFD_INFLOW_CLOSE'] + df_ori['S_MFD_INFLOW_OPEN']).unstack().rolling(5,
                                                                                                            1).apply(
                lambda x: np.max(x)).stack()
            # df_ori['short'] = (df_ori['volume']).unstack().rolling(60, 3).apply(lambda x: (np.max(x)-np.median(x))/(np.std(x)+1e-3)).stack()
            df_ori[self.factor_name] = (df_ori['long']).apply(lambda x: round_(x, 5))  # 矩阵大小不同时，Python精度差异，导致计算值不同

            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_ori[[self.factor_name]]  # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori  # 纯h5文件的T-1_Factor直接返回df