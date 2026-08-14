import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *
# 财务+MD
class factor_tsq_newneptune_caiwu_test2(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_caiwu_test2"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80, #注意为正数
         'column': ['close','amt']
    }]  # T-N factor数据，格式如上
    finance_data = [
        {'name': 'AShareBalanceSheet', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareBalanceSheet/AShareBalanceSheet.h5',
         'lag': 600, #注意为正数，是按交易日而非报告期
         'column': ['ANN_DT', 'STATEMENT_TYPE', 'FIX_ASSETS', 'TOT_CUR_ASSETS','MONETARY_CAP']
    }]  # 财务数据，格式如上
    t_1_factor_data_types = ['MD','FINANCE'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_balancesheet = database['AShareBalanceSheet'] # 和上面t-1_factor_data的name一致
            df_balancesheet[self.factor_name] = df_balancesheet['FIX_ASSETS'].unstack().rolling(4,1).std().stack() + df_balancesheet['TOT_CUR_ASSETS'].unstack().rolling(4,1).sum().stack()
            df_balancesheet = extend_finance_table_to_daily(df_balancesheet,
                                                            database['finance_data_max_lag_start_date'], database['end_date'],
                                                            self.factor_name, self.fill_na_value) # 使用固定的转换函数转为日频因子，并且索引会被改为ANN_DT以避免未来信息

            md_data = database['MD_CHINA_STOCK_DAILY_WIND']
            md_data['factor'] = df_balancesheet[self.factor_name]
            md_data[self.factor_name] = (md_data['factor'] / md_data['amt'].replace(0,np.nan)).apply(lambda x : round_(x,4))
            # -------------------------------------------------------------------------------------------------------------------
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