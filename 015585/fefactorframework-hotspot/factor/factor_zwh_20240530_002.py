# T+h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
# 逻辑：
import copy

def preprocess_T_1_zwh(data_df, process_cols=[]):
    # import pdb; pdb.set_trace()
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
    if 'amt' in data_df.columns:
        data_df['amt'] = np.log(1+1e-9+data_df['amt'])
    if 'volume' in data_df.columns:
        data_df['volume'] = np.log(1+1e-9+data_df['volume'])
    data_df['zcz'] = (((data_df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
            data_df.reset_index()['dt'] >= '2020-08-24'))
                 | (data_df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    zcz_df = data_df[data_df['zcz']]
    prices_ = [i for i in ['open', 'close', 'high', 'low', 'vwap'] if i in data_df.columns]
    for k in prices_:
        data_df[data_df['zcz']][k] = ((zcz_df[k] / zcz_df['pre_close'] - 1) / 2 + 1) * zcz_df['pre_close']
    return data_df

class factor_zwh_20240530_002(BaseFactor):
    owner = 'zwh'
    strategy_name = "hotspot"
    factor_name = "zwh_20240530_002"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    factor_explain = "涨幅换手比例" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否（本因子需要调整，为简单起见未加入注册制部分）
    logic_type = "涨幅换手比例" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    xdb_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',  # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 50,  # 注意为正数
         'column': ['pct_chg', 'turn', 'pre_close', 'amt', 'vwap', 'adjfactor']
         }]

    t_1_factor_data_types = ['MD']

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        EPS = 1e-9
        md_data_ = database['MD_CHINA_STOCK_DAILY_WIND']
        md_data = copy.deepcopy(md_data_)
        md_data = preprocess_T_1_zwh(md_data)
        md_data[md_data['pct_chg'] >= 0]['turn'] = 0.0
        res = md_data['pct_chg'] / (EPS + md_data['turn'])
        res = res.apply(lambda x: round_(x, 5))
        N = 20
        resmax = res.unstack().rolling(N // 2, 1).max().stack()
        resme = res.unstack().rolling(N, 1).std().stack().apply(lambda x: round_(x, 5))
        resmi = res.unstack().rolling(N // 2, 1).min().stack()
        res = (resmax + resmi) / (EPS + resme)
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
