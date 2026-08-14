import decimal
import datetime as dt
import pandas as pd
import numpy as np
from scipy.stats import norm, skew, kurtosis
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_tra_20250408_3(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "xbc_tra_20250408_3"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "xbc"  # 开发人员姓名
    factor_explain = "factor_xbc_dir_mean_change.py" # 因子逻辑解释
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


            nan_value =  0.
            transaction_df = transaction_df[
                (transaction_df['TradePrice'] > 0) & (transaction_df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
            transaction_df['direction_flag'] = (transaction_df['TradeBuyNo'] > transaction_df['TradeSellNo']).replace({True: 1, False: 2})
            if transaction_df.shape[0]>100:
                near_num=100
                transaction_df_near = transaction_df.iloc[-near_num:, :]
                transaction_df_near['direction_flag_index'] = [i for i in range(transaction_df_near.shape[0])]
                transaction_df_near1 = transaction_df_near.loc[transaction_df_near['direction_flag']==1]
                transaction_df_near2 = transaction_df_near.loc[transaction_df_near['direction_flag']==2]
                value = (transaction_df_near1['direction_flag_index'].mean()-transaction_df_near2.shape[0]/2)/transaction_df_near.shape[0]

                transaction_df_far = transaction_df.iloc[:-near_num, :]
                if transaction_df_far.shape[0]<100:
                    value_far=-0.06
                else:
                    transaction_df_far['direction_flag_index'] = [i for i in range(transaction_df_far.shape[0])]
                    transaction_df_far1 = transaction_df_far.loc[transaction_df_far['direction_flag'] == 1]
                    transaction_df_far2 = transaction_df_far.loc[transaction_df_far['direction_flag'] == 2]
                    value_far = (transaction_df_far1['direction_flag_index'].mean() - transaction_df_far2.shape[0]/2) / transaction_df_far.shape[0]
                value = abs(value-value_far)
            else:
                value = nan_value




            factor_dict = {self.factor_name: value}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

