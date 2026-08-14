# T+h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_qyh_new_combo2(BaseFactor):
    # 以下为因子基本信息
    strategy_name = "jupiter/europa"
    factor_name = "qyh_new_combo2"
    fill_na_value = 1
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "T-3~T-1日使用MD数据对每日超过全市场平均成交量的部分求和，计算平均，再用T日成交量除以上述基准" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "放量角度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    # 以下均为数据准备信息
    t_day_data = ['TTransaction']
    xdb_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 20, #注意为正数
         'column': ['pct_chg', 'turn', 'pre_close', 'amt', 'vwap']
    }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        md_data = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上述name一致
        md_data['res'] = md_data['amt'].unstack().rolling(5, 1).mean().stack()
        md_data['res'] = md_data['res'] - md_data['res'].unstack().mean(axis=1)
        res = md_data['res'].unstack().iloc[[-1]].stack().to_frame(name = 'res') # 此处iloc[[-1]]保持只有1个交易日；stack是必须的，否则index不正确
        database["pre_T_N"] = res
        return database

    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            df_trans = database['TTransaction']
            dt, ticker = df_trans.index[0]
            md_data = database['pre_T_N']
            md_data = md_data['res'].unstack()
            res1 = md_data[ticker][0] if ticker in md_data.columns else np.nan
            res2 = database['TTransaction']['TradeMoney'].sum()
            factor_dict = {self.factor_name: res2/res1 if abs(res1) > 0 else np.nan}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
