import pandas as pd
import numpy as np
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_demo_md_xdb_tick1m_cs(BaseFactor):
    strategy_name = "neptune"
    factor_name = "demo_md_xdb_tick1m_cs"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = ""  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时
    t_day_data = []
    #
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80,  # 注意为正数
         'column': ['close', 'adjfactor']
         }]
    t_1_factor_data_types = ['MD']
    xdb_data = [
        {
       'name': 'xdb_tick1m_cs', # xdb_order1m, xdb_tick1m
       'lag': 3 # 回看日期，N为往前回看1~N天
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        data = database['xdb_tick1m_cs']
        # -------------------------------------------------------------------------------------------------------------------
        # 因子逻辑部分
        res_tick = data.groupby(['dt','Ticker'])['LastPx'].mean().to_frame(name='lastpxmean')

        md_data = database['MD_CHINA_STOCK_DAILY_WIND']
        res_md = md_data['close'].unstack().rolling(5, 1).mean().iloc[[-1]].stack().reset_index()
        res_md['dt'] = res_tick.index[0][0]  # 提供的MD只会有T日之前的全市场信息，而没有当日，无法直接merge，要取最后一行重设为T日的dt
        res_md = res_md.set_index(['dt', 'Ticker'])
        res_tick['md_close_5_mean'] = res_md
        res_tick[self.factor_name] = res_tick['lastpxmean'] / res_tick['md_close_5_mean']
        # -------------------------------------------------------------------------------------------------------------------
        database['pre_T_N'] = res_tick[[self.factor_name]]
        return database
    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res