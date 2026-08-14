import decimal
import datetime as dt
import pandas as pd
import numpy as np
from scipy.stats import norm, skew, kurtosis
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_tra_20250408_12(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "xbc_tra_20250408_12"
    fill_na_value =  -74
    need_pre_calculate_T_N = False
    owner = "xbc"  # 开发人员姓名
    factor_explain = "factor_xbc_exchange_ratio_diff.py" # 因子逻辑解释
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


            nan_value = -74
            transaction_df = transaction_df[(transaction_df['TradePrice'] > 0) & (transaction_df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
            #transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据
            transaction_df['exchange_ratio'] = transaction_df['TradeQty'] / transaction_df['ff_shares']
            # zcz
            index = transaction_df.iloc[0].name
            tradingday, code = index[0].strftime('%Y%m%d'), index[1]
            if ((tradingday >= '20200824') and (code[0] == '3'))|(code[:2] == '68'):
                is_zcz = True
            else:
                is_zcz = False

            up_ratios = [i/1000 for i in range(60,100,1)]
            if is_zcz:
                near_zt_prices = [np.floor(transaction_df['pre_close'][0] * 100 * (i*2+1) + 0.5) / 100 for i in up_ratios]
            else:
                near_zt_prices = [np.floor(transaction_df['pre_close'][0] * 100 * (i+1) + 0.5) / 100 for i in up_ratios]
            transaction_df_nears = [transaction_df.loc[transaction_df['TradePrice'] > i] for i in near_zt_prices]
            values = []
            for transaction_df_near1 in transaction_df_nears:
                if transaction_df_near1.shape[0] > 0:
                    value1 = transaction_df_near1['exchange_ratio'].sum()
                else:
                    value1 = 0
                if value1 > 0:
                    values.append(value1)
            values = np.array(values)
            values = values[1:] - values[:-1]
            value = np.sum(values)




            factor_dict = {self.factor_name: value}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

