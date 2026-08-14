import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_cs_test2(BaseFactor):
    strategy_name = "saturn"
    factor_name = "qyh_cs_test2"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时

    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80, #注意为正数
         'column': ['close']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    xdb_data = [{
        'name':'xdb_tickex_cs',
        'lag':2
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['xdb_tickex_cs']  # 和上面t-1_factor_data的name一致
            md_data = database['MD_CHINA_STOCK_DAILY_WIND']
            res = df_ori.groupby(['dt','Ticker']).apply(lambda x : x['LastPx'].mean()).to_frame(name=self.factor_name)
            res2 = md_data['close'].unstack().rolling(5,1).mean().iloc[[-1]] # 最新的一天，注意是xdb数据索引的前一天
            res2.index = [res.index[0][0]] # 日期后移一天，便于对齐
            res['md_result'] = res2.stack()
            database['pre_T_N'] = (res[self.factor_name] + res['md_result']).to_frame(name = self.factor_name) #
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            return res