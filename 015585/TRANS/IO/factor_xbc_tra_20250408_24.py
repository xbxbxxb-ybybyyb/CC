import decimal
import datetime as dt
import pandas as pd
import numpy as np
from scipy.stats import norm, skew, kurtosis
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_tra_20250408_24(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "xbc_tra_20250408_24"
    fill_na_value =  0.056
    need_pre_calculate_T_N = False
    owner = "xbc"  # 开发人员姓名
    factor_explain = "factor_xbc_20231019_9.py" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTransaction']
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
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
            transaction_df = database['TTransaction']
            # zcz
            index = transaction_df.iloc[0].name
            tradingday, code = index[0].strftime('%Y%m%d'), index[1]
            if ((tradingday >= '20200824') and (code[0] == '3'))|(code[:2]=='68'):
                is_zcz = True
            else:
                is_zcz = False



            nan_value = 0.056
            transaction_df = transaction_df[(transaction_df['TradePrice'] > 0) & (transaction_df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
            transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]  # 选择连续竞价阶段

            transaction_df['direction_flag'] = (transaction_df['TradeBuyNo'] > transaction_df['TradeSellNo']).replace({True: 1, False: 2})

            if transaction_df.shape[0] > 2:
                transaction_df = transaction_df.tail(100)
                # zcz
                date, ticker = transaction_df.index[0]
                date = date.strftime('%Y%m%d')
                zcz = ((ticker[0:2] == '30') & (date >= '20200824')) | (ticker[0:2] == '68')
                transaction_df['up_down_ratio'] = (transaction_df['TradePrice'] - transaction_df['pre_close'][0]) / transaction_df['pre_close'][0]
                if zcz:
                    transaction_df['up_down_ratio'] = transaction_df['up_down_ratio'] / 2

                up_down_ratio_diff = transaction_df['up_down_ratio'].values[1:] - transaction_df['up_down_ratio'].values[:-1]
                up_down_ratio_diff = up_down_ratio_diff[1:] - up_down_ratio_diff[:-1]
                value = np.sum(np.abs(up_down_ratio_diff))
            else:
                value = nan_value
            factor_dict = {self.factor_name: value}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

