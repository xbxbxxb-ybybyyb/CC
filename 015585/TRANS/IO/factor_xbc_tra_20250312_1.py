import decimal
import datetime as dt
import pandas as pd
import numpy as np
from scipy.stats import norm, skew, kurtosis
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_tra_20250312_1(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "xbc_tra_20250312_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "xbc"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
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
            up_ratios = [i/1000 for i in range(0,101,10)]
            if is_zcz:
                near_zt_prices = [np.floor(transaction_df['pre_close'][0] * 100 * (i*2+1) + 0.5+1e-8) / 100 for i in up_ratios]
            else:
                near_zt_prices = [np.floor(transaction_df['pre_close'][0] * 100 * (i+1) + 0.5+1e-8) / 100 for i in up_ratios]
            transaction_df = transaction_df.loc[transaction_df['TradeMoney']>0]
            transaction_df = transaction_df.loc[transaction_df['TradeBSFlag']>0]
            if transaction_df.shape[0]>0:
                transaction_df_nears = [transaction_df.loc[(transaction_df['TradePrice'] > near_zt_prices[i])&(transaction_df['TradePrice'] <= near_zt_prices[i+1])] for i in range(len(near_zt_prices)-1)]
                values = []
                for transaction_df_near1 in transaction_df_nears:
                    if transaction_df_near1.shape[0] > 0:
                        value1 = transaction_df_near1['TradeQty'].sum()
                        values.append(value1)
                values = np.array(values)
                value = np.max(values)/np.sum(values)
            else:
                value = np.nan

            factor_dict = {self.factor_name: value}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

