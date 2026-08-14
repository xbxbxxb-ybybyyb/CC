import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_emo_20250909_1(BaseFactor):
    strategy_name = "europa"
    factor_name = "emo_20250909_1"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "前日收盘涨停标的数量" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = []
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND',
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 80, #注意为正数
         'column': ['adjfactor','pct_chg','turn','high', 'low', 'open', 'vwap', 'close','pre_close']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                    df_ori.reset_index()['dt'] >= '2020-08-24'))
                             | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
            df_ori['bj'] = (df_ori.reset_index()['Ticker'].apply(lambda x: x[-2:] == 'BJ')).values
            # for col in ['high', 'low', 'open', 'vwap', 'close']:
            #     if col in df_ori.columns:
            #         df_ori.loc[df_ori['zcz'] == 1, col] = ((df_ori.loc[df_ori['zcz'] == 1, col] - 1) / 2 + 1) * \
            #                                               df_ori.loc[df_ori['zcz'] == 1, 'pre_close']
            #         df_ori.loc[df_ori['bj'] == 1, col] = ((df_ori.loc[df_ori['bj'] == 1, col] - 1) / 3 + 1) * \
            #                                               df_ori.loc[df_ori['bj'] == 1, 'pre_close']
            # for col in ['high', 'low', 'open', 'vwap', 'close', 'pre_close']:
            #     df_ori[col] = df_ori[col] * df_ori['adjfactor']
            # -------------------------------------------------------------------------------------------------------------------
            def cal_ul_price(pre_close_dataframe, ratio=0.1):
                pre_close_dataframe = pre_close_dataframe.reset_index()
                after_824 = pre_close_dataframe['dt'] >= pd.Timestamp('20200824')
                cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '30')
                kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '68')
                pre_close_dataframe['ul_price'] = np.floor(
                    pre_close_dataframe['pre_close'] * 100 * (1 + ratio) + 0.5) / 100
                pre_close_dataframe.loc[(after_824 & cyb) | kcb, 'ul_price'] = np.floor(
                    pre_close_dataframe['pre_close'] * 100 * (1 + 2 * ratio) + 0.5) / 100
                return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']
            df_ori['ul_price'] = cal_ul_price(df_ori, ratio=0.1)
            df_ori['is_zt'] = df_ori['close'] == df_ori['ul_price']
            zt_num = df_ori.groupby('dt')['is_zt'].count()
            df_ori['zt_num'] = df_ori.index.get_level_values('dt').map(zt_num)
            df_ori[self.factor_name] = df_ori['zt_num']
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
