# h5 + xdb + T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_new_combo_3(BaseFactor):
    strategy_name = "jupiter/europa"
    factor_name = "qyh_new_combo_3"
    fill_na_value = 1
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "T-3到T-1日基于全息盘口的每日lastpx中位数的均值,减去md数据5日close均值，除以T日lastpx均值" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "价格形态" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTickab']
    xdb_data = [
        {
       'name': 'xdb_tickfull', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 3 # 回看日期，N为往前回看1~N天
    }]
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 7, #注意为正数
         'column': ['close']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            # database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        tickfull_df = database['xdb_tickfull']
        tickfull_df = tickfull_df[tickfull_df['LastPx'] > 0]
        res = tickfull_df.groupby('MDDate')['LastPx'].median().mean() # 得到全息盘口计算的均价

        dt,ticker = tickfull_df.index[0]
        md_data = database['MD_CHINA_STOCK_DAILY_WIND']
        res2 = md_data['close'].unstack().rolling(5,1).mean().iloc[-1]
        res2 = res2[ticker] if ticker in res2.index else np.nan # 过去5日close均值，取该标的的值
        res2 = np.nan if abs(res2) <= 1e-8 else res2
        database['pre_T_N'] = pd.DataFrame({self.factor_name: [res-res2]})
        return database
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            database['TTickab'] = filter_930(database['TTickab'])
            return database
    def calculate(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N'][self.factor_name].values[0]
            res3 = database['TTickab']['LastPx'].mean()
            factor_dict = {self.factor_name: res / (res3+1e-2)}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

