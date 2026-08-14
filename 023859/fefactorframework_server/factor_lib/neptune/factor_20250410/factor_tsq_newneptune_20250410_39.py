import numpy as np
import pandas as pd
import bottleneck as bn
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_tsq_newneptune_20250410_39(BaseFactor):
    strategy_name = "neptune"
    factor_name = "tsq_newneptune_20250410_39"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "tsq"  # 开发人员姓名
    factor_explain = "股息率60日均值/标准差" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'RISK',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5',
         'lag': 100,  # 注意为正数
         'column': ['Beta', 'BookToPrice', 'DividendYield', 'EarningsQuality', 'EarningsVariability', 'EarningsYield', 'Growth', 'Industry','InvestmentQuality', \
                    'Leverage', 'Liquidity', 'LongTermReversal','MidCapitalization', 'Momentum', 'Profitability', 'ResidualVolatility','Size']
         }
    ]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['RISK'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['RISK']  # 和上面t-1_factor_data的name一致
            # -------------------------------------------------------------------------------------------------------------------
            df_ori['factor'] = df_ori['DividendYield'].unstack().rolling(60,1).mean().stack().apply(lambda x : round_(x,5)) / df_ori['DividendYield'].unstack().rolling(60,1).std().stack().apply(lambda x : round_(x,5)).replace(0,np.nan)
            df_ori['factor'] = df_ori['factor'].unstack().rank(axis=1, pct=True).stack()
            df_ori[self.factor_name] = df_ori['factor'].apply(lambda x : round_(x,5))
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = df_ori[[self.factor_name]] # 纯粹的T-1_Factor直接返回全市场全区间因子值
            return database

    def prepare_T_data(self, database):
        return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            df_ori = database['pre_T_N']
            return df_ori # 纯h5文件的T-1_Factor直接返回df
