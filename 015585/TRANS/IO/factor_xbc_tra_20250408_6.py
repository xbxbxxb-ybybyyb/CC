import decimal
import datetime as dt
import pandas as pd
import numpy as np
from scipy.stats import norm, skew, kurtosis
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_tra_20250408_6(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "xbc_tra_20250408_6"
    fill_na_value = 0.15
    need_pre_calculate_T_N = False
    owner = "xbc"  # 开发人员姓名
    factor_explain = "factor_xbc_pre_zt_length.py" # 因子逻辑解释
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


            nan_value = 0.15
            transaction_df = transaction_df[
                (transaction_df['TradePrice'] > 0) & (transaction_df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
            transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据

            if transaction_df.shape[0] > 0:
                #zcz
                index = transaction_df.iloc[0].name
                tradingday, code = index[0].strftime('%Y%m%d'),index[1]
                if (tradingday>='20200824') and (code[0]=='3'):
                    is_zcz = True
                else:
                    is_zcz = False

                if is_zcz:
                    near_zt_price1 = np.floor(transaction_df['pre_close'][0]  * 100 * 1.18 + 0.5) / 100
                    near_zt_price2 = np.floor(transaction_df['pre_close'][0]  * 100 * 1.16 + 0.5) / 100
                    near_zt_price3 = np.floor(transaction_df['pre_close'][0]  * 100 * 1.14 + 0.5) / 100
                else:
                    near_zt_price1 = np.floor(transaction_df['pre_close'][0] * 100 * 1.09 + 0.5) / 100
                    near_zt_price2 = np.floor(transaction_df['pre_close'][0] * 100 * 1.08 + 0.5) / 100
                    near_zt_price3 = np.floor(transaction_df['pre_close'][0] * 100 * 1.07 + 0.5) / 100

                transaction_df_near1 = transaction_df.loc[transaction_df['TradePrice']>near_zt_price1]
                transaction_df_near2 = transaction_df.loc[transaction_df['TradePrice']>near_zt_price2]
                transaction_df_near3 = transaction_df.loc[transaction_df['TradePrice']>near_zt_price3]

                value = (transaction_df_near1.shape[0]+transaction_df_near2.shape[0]+transaction_df_near3.shape[0])/transaction_df.shape[0]
            else:
                value = nan_value

            if value >10000:
                value = 10000




            factor_dict = {self.factor_name: value}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

