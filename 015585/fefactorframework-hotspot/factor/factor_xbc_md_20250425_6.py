# h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_md_20250425_6(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "xbc_md_20250425_6"
    fill_na_value = 1.19
    need_pre_calculate_T_N = True
    owner = "xbc"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 300, #注意为正数
         'column': ['pct_chg', 'turn', 'pre_close', 'amt', 'vwap', 'open', 'low', 'high', 'close', 'adjfactor']
         }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            md = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                    md.reset_index()['dt'] >= '2020-08-24'))
                         | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
            factor_name = self.factor_name
            md_data = md
            # base
            md.loc[md['zcz']==True,'zt_price'] = np.floor(md['pre_close']*100*1.2+0.5+1e-8)/100
            md.loc[md['zcz']==False,'zt_price'] = np.floor(md['pre_close']*100*1.1+0.5+1e-8)/100
            md.loc[md['zcz'] == True, 'dt_price'] = np.floor(md['pre_close'] * 100 * 0.8 + 0.5 + 1e-8) / 100
            md.loc[md['zcz'] == False, 'dt_price'] = np.floor(md['pre_close'] * 100 * 0.9 + 0.5 + 1e-8) / 100
            md['close_is_zt'] = (md['close']-md['zt_price']).abs()<0.001
            md['high_is_zt'] = (md['high']-md['zt_price']).abs()<0.001
            md['high_ratio'] = md['high']/md['pre_close']
            md['close_ratio'] = md['close']/md['pre_close']
            md['low_ratio'] = md['low']/md['pre_close']
            md['open_ratio'] = md['open']/md['pre_close']
            md['adjfactor'] = md['adjfactor'].apply(lambda x: round_(x, 4))
            md['pre_close_adj'] = md['pre_close']*md['adjfactor']
            md['open_adj'] = md['open']*md['adjfactor']
            md['close_adj'] = md['close']*md['adjfactor']
            md['mid_open_close_adj'] = (md['open']+md['close'])/2*md['adjfactor']
            md['high_adj'] = md['high']*md['adjfactor']
            md['low_adj'] = md['low']*md['adjfactor']
            md['open_close_high_adj'] = md[['open','close']].max(axis=1)*md['adjfactor']
            md['pre_open_close_high_adj'] = np.nan
            md['pre_open_close_high_adj'] = md.groupby('Ticker')['open_close_high_adj'].shift(1)
            md['pre_low_adj'] = md.groupby('Ticker')['low_adj'].shift(1)
            md['open_close_high_ratio'] = md['open_close_high_adj']/md['pre_open_close_high_adj']
            md['close2open'] = md['close']-md['open']
            for i in range(1,10+1):
                md['close_ratio'+str(i)] = np.nan
                md['close_ratio'+str(i)] = md.groupby('Ticker')['close_ratio'].shift(i)

            high_days = 60
            md['before_n_close_high_adj'] = 0
            for i in range(1,1+high_days):
                md['before_high_adj_tmp'] = 0
                md['before_high_adj_tmp'] = md.groupby('Ticker')['close_adj'].shift(i)
                md['before_n_close_high_adj'] = md[['before_high_adj_tmp','before_n_close_high_adj']].max(axis=1)

            factor_df = pd.DataFrame()
            factor_df[factor_name] = md['before_n_close_high_adj']/md['close_adj']
            # -------------------------------------------------------------------------------------------------------------------
            md_data[factor_name] = factor_df[factor_name].apply(lambda x: round_(x, 4))
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
