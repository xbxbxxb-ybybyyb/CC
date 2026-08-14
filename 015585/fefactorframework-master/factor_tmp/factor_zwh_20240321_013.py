# T+h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
# 逻辑：
def preprocess_TTick_zwh(data_df,price_names = ['HighPx', 'LowPx','LastPx',  'WeightedAvgBidPx', 'WeightedAvgOfferPx',
                   'Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price', 'Buy6Price', 'Buy7Price',
                   'Buy8Price', 'Buy9Price', 'Buy10Price', 'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price',
                   'Sell5Price', 'Sell6Price', 'Sell7Price', 'Sell8Price', 'Sell9Price', 'Sell10Price']):
    dt, ticker = data_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = data_df['pre_close'].values[0]
    if zcz:
        data_df[price_names] = ((data_df[price_names] / pre_close - 1) / 2 + 1) * pre_close
    return data_df
class factor_zwh_20240321_013(BaseFactor):
    owner = 'zwh'
    strategy_name = "saturn/sell"
    factor_name = "zwh_20240321_013"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "价格分布比例刻画" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否（本因子需要调整，为简单起见未加入注册制部分）
    logic_type = "价格形态" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 20,  # 注意为正数
         'column': ['pct_chg', 'turn', 'pre_close', 'amt', 'vwap']
         }]
    t_1_factor_data_types = ['MD']
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        EPS = 1e-9
        md_data = database['MD_CHINA_STOCK_DAILY_WIND']
        res =  md_data['pct_chg']/(EPS+md_data['turn'])
        res = res.unstack().rolling(5, 1).mean().stack()
        md_data[self.factor_name] = res.apply(lambda x: round_(x, 5))
        database['pre_T_N'] = md_data[[self.factor_name]]
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
            # ---------------------------------------------------------------------------------------------------------------
            return df_ori