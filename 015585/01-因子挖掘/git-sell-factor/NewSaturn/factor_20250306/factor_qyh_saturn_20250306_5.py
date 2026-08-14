import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_saturn_20250306_5(BaseFactor):
    strategy_name = "saturn/sell"
    factor_name = "qyh_saturn_20250306_5"
    fill_na_value = 0.002
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "小于9%的前500撤单的时间峰度" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-时间强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    xdb_data = [
        {
       'name': 'xdb_cancel', # xdb_order, xdb_trade, xdb_tickfull, xdb_tick1s
       'lag': 1 # 回看日期，N为往前回看1~N天
    }]
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            cancel_df = database['xdb_cancel']
            pre_close = cancel_df['pre_close'].max()
            ff_shares = cancel_df['ff_shares'].max()
            dt, ticker = cancel_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            bj = ticker[-2:] == 'BJ'
            cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                    lambda x: get_time_delta(x) - 1800000) # 距离930毫秒数
            cancel_df = filter_930(cancel_df)
            #
            if zcz:
                p = round_(pre_close * (1 + 0.09 * 2), 3)
            elif bj:
                p = round_(pre_close * (1 + 0.09 * 3), 3)
            else:
                p = round_(pre_close * 1.09, 3)
            cancel_df = cancel_df[cancel_df['OrderPrice'] < p]
            cancel_df = cancel_df.head(500) if len(cancel_df) > 500 else cancel_df
            cancel_df['factor'] = cancel_df['MDTime_delta']
            res = cancel_df['factor'].kurt()
            #
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [res]})
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
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
