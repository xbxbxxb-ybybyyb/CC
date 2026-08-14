import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_hotspot_test_xbc(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "qyh_hotspot_test_xbc"
    fill_na_value = 0.2
    need_pre_calculate_T_N = False
    owner = "xbc"  # 开发人员姓名
    factor_explain = "" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-挂单价格激进度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTickab']
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
            transaction_df = database['TTickab']
            transaction_df = transaction_df[(transaction_df['NumTrades'] > 0)]  #
            transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的逐笔成交数据

            value = np.nan
            if transaction_df.shape[0] >= 5:
                dt, ticker = transaction_df.index[0]
                dt = dt.strftime('%Y%m%d')
                zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')

                interval = max(min(3000, int(transaction_df.shape[0] / 2)), 10)
                transaction_df['ValueTrade'] = transaction_df['TotalValueTrade'] - transaction_df['TotalValueTrade'].shift(interval).fillna(0)
                transaction_df['VolumeTrade'] = transaction_df['TotalVolumeTrade'] - transaction_df['TotalVolumeTrade'].shift(interval).fillna(0)
                transaction_df['v_wap'] = transaction_df['ValueTrade'] / transaction_df['VolumeTrade']
                transaction_df['pct'] = (transaction_df['WeightedAvgOfferPx'] + transaction_df['WeightedAvgBidPx'] - 2 * transaction_df['v_wap']) / (transaction_df['pre_close'])
                if zcz:
                    transaction_df['pct'] = transaction_df['pct'] / 2
                value = transaction_df['pct'][-100:].mean()


            factor_dict = {self.factor_name: value}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)