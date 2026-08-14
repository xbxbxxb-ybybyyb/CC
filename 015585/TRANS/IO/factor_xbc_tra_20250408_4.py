import decimal
import datetime as dt
import pandas as pd
import numpy as np
from scipy.stats import norm, skew, kurtosis
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_xbc_tra_20250408_4(BaseFactor):
    strategy_name = "hotspot"
    factor_name = "xbc_tra_20250408_4"
    fill_na_value = -0.2
    need_pre_calculate_T_N = False
    owner = "xbc"  # 开发人员姓名
    factor_explain = "factor_xbc_dir_ratio_change.py" # 因子逻辑解释
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


            nan_value = -0.2
            transaction_df = transaction_df[
                (transaction_df['TradePrice'] > 0) & (transaction_df['TradeMoney'] > 0)]  # 去除深圳撤单的逐笔成交数据
            def fun_get_time(time1, sec_delta):
                # 计算给定时间戳time1在sec_delta秒后的时间戳
                tmp_time = dt.datetime.strptime(str(time1)[:-3], '%H%M%S')
                tmp_time2 = tmp_time + dt.timedelta(seconds=sec_delta)
                tmp_time2_str = tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
                if (int(tmp_time2_str) > 113000000) & (time1 <= 113000000):
                    adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=1.5 * 3600)
                    adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
                    return int(adj_tmp_time2_str)
                elif (int(tmp_time2_str) < 130000000) & (time1 >= 130000000):
                    adj_tmp_time2 = tmp_time2 - dt.timedelta(seconds=1.5 * 3600)
                    adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
                    return int(adj_tmp_time2_str)
                elif (int(tmp_time2_str) < 93000000) & (time1 >= 93000000):
                    adj_tmp_time2_str = '92500000'
                    return int(adj_tmp_time2_str)
                elif (time1 < 93000000):
                    adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=4 * 60)
                    adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
                    return int(adj_tmp_time2_str)
                else:
                    return int(tmp_time2_str)
            if transaction_df.shape[0]>0:
                final_time = int(transaction_df.iloc[-1,0])
                bar_time = fun_get_time(final_time,-30)
                transaction_df['direction_flag'] = (transaction_df['TradeBuyNo'] > transaction_df['TradeSellNo']).replace({True: 1, False: 2})
                transaction_df_near = transaction_df.loc[transaction_df['MDTime']>bar_time]
                now_ratio = np.sum(transaction_df_near['direction_flag'] > 1) / transaction_df_near.shape[0]
                transaction_df_far = transaction_df.loc[transaction_df['MDTime']<=bar_time]
                if transaction_df_far.shape[0]<100:
                    past_ratio=0.425
                else:
                    past_ratio = np.sum(transaction_df_far['direction_flag'] > 1) / transaction_df_far.shape[0]
                value = now_ratio - past_ratio
            else:
                value = nan_value




            factor_dict = {self.factor_name: value}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

