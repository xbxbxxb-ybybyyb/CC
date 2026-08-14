# T+h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
import copy

# 逻辑：


def preprocess_T_1_zwh(data_df):
    if 'pct_chg' in data_df.columns:
        data_df.loc[data_df['pct_chg'] > 10, 'pct_chg'] = 10  # 截断
        data_df.loc[data_df['pct_chg'] < -10, 'pct_chg'] = -10  # 截断
    if 'open' in data_df.columns:
        data_df['open'] = data_df['open'] * data_df['adjfactor']
    if 'close' in data_df.columns:
        data_df['close'] = data_df['close'] * data_df['adjfactor']
    if 'pre_close' in data_df.columns:
        data_df['pre_close'] = data_df['pre_close'] * data_df['adjfactor']
    if 'high' in data_df.columns:
        data_df['high'] = data_df['high'] * data_df['adjfactor']
    if 'low' in data_df.columns:
        data_df['low'] = data_df['low'] * data_df['adjfactor']
    if 'vwap' in data_df.columns:
        data_df['vwap'] = data_df['vwap'] * data_df['adjfactor']
    if 'volume' in data_df.columns:
        data_df['volume'] = data_df['volume'] / data_df['adjfactor']

    data_df['zcz'] = (((data_df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
            data_df.reset_index()['dt'] >= '2020-08-24'))
                 | (data_df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    zcz_df = data_df[data_df['zcz']]
    prices_ = [i for i in ['open', 'close', 'high', 'low', 'vwap'] if i in data_df.columns]
    for k in prices_:
        data_df.loc[data_df['zcz']==1, k] = ((zcz_df[k] / zcz_df['pre_close'] - 1) / 2 + 1) * zcz_df['pre_close']

    return data_df



class factor_zwh_newNeptune_20250327_011(BaseFactor):
    owner = 'zwh'
    strategy_name = "hotspot"
    factor_name = "zwh_newNeptune_20250327_011"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "价格换手强度" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否（本因子需要调整，为简单起见未加入注册制部分）
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 100,  # 注意为正数
         'column': ['close', 'high', 'low', 'vwap', 'turn','open', 'amt', 'pre_close', 'adjfactor']
         }]
    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        EPS = 1e-9
        md_data_ = database['MD_CHINA_STOCK_DAILY_WIND']
        md_data = copy.deepcopy(md_data_)
        df = preprocess_T_1_zwh(md_data)
        high = df['high']
        low = df['low']

        high_pct = (high - low) / low - 1
        low_pct = (df['close'] - df['pre_close']) / df['pre_close'] - 1

        vv = (abs(high_pct) + abs(low_pct)) * (df['turn'])  # * df['pct_chg']

        # res = vv.unstack().rolling(14, min_periods=14).min().stack()  ## 30 0.735
        res = vv.unstack().rolling(5, min_periods=5).min().stack() /vv.unstack().rolling(5, min_periods=5).mean().stack() ##??


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
            # import pdb; pdb.set_trace()
            # ---------------------------------------------------------------------------------------------------------------
            return df_ori
