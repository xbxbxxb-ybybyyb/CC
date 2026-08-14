import decimal
import datetime as dt
import pandas as pd
import numpy as np
from scipy.stats import norm, skew, kurtosis
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_tra_20250408_10(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "xbc_tra_20250408_10"
    fill_na_value = 0.04
    need_pre_calculate_T_N = False
    owner = "xbc"  # 开发人员姓名
    factor_explain = "factor_xbc_up_down_ratio_diff_mean.py" # 因子逻辑解释
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


            nan_value = 0.04

            transaction_df = transaction_df[
                (transaction_df['TradePrice'] > 0) & (transaction_df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据


            if transaction_df.shape[0] > 130:
                # zcz
                index = transaction_df.iloc[0].name
                tradingday, code = index[0].strftime('%Y%m%d'), index[1]
                if ((tradingday >= '20200824') and (code[0] == '3'))|(code[:2] == '68'):
                    is_zcz = True
                else:
                    is_zcz = False
                transaction_df['up_down_ratio'] = (transaction_df['TradePrice'] - transaction_df['pre_close'][0]) / transaction_df['pre_close'][0]
                if is_zcz:
                    transaction_df['up_down_ratio'] = transaction_df['up_down_ratio']/2

                near_num = min(500,transaction_df.shape[0])
                transaction_df_near = transaction_df.iloc[-near_num:,:]
                transaction_df_far = transaction_df.iloc[:-near_num, :]
                value = transaction_df_near['up_down_ratio'].mean()-transaction_df_far['up_down_ratio'].mean()
            else:
                value = nan_value




            factor_dict = {self.factor_name: value}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

