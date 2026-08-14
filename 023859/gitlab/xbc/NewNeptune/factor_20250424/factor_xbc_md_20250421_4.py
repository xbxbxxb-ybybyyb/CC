# h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_md_20250421_4(BaseFactor):
    strategy_name = "neptune"
    factor_name = "xbc_md_20250421_4"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "xbc"  # 开发人员姓名
    factor_explain = "WeightedAvgBidPx的滚动最小值" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'ordersheet5_new', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800463/data/generalStrong/ordersheet5_new/WeightedAvgBidPx.h5',
         'lag': 50, #注意为正数
         'column': []
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['ordersheet5_new'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            md = database['ordersheet5_new'] # 和上面t-1_factor_data的name一致
            md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                    md.reset_index()['dt'] >= '2020-08-24'))
                         | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
            factor_name = self.factor_name
            md_data = md

            factor_df = pd.DataFrame()
            columns = list(md_data.columns)
            md_data1 = pd.DataFrame(index=md_data.index)
            for i in range(md_data.shape[1] - 1):
                md_data1[i] = md_data[columns[i + 1]] - md_data[columns[i]]
            md_data['stat'] = (md_data[columns[-1]] - md_data[columns[0]]) / (md_data1.abs().sum(axis=1))

            md_data[factor_name] = md_data['stat'].unstack().rolling(4, min_periods=1).min().stack()#.round(4)
            # -------------------------------------------------------------------------------------------------------------------
            md_data[factor_name] = md_data[factor_name].apply(lambda x: round_(x, 4))
            database['pre_T_N'] = md_data[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
