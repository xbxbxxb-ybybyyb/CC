import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_qyh_saturn_20250123_3(BaseFactor):
    strategy_name = "saturn/sell"
    factor_name = "qyh_saturn_20250123_3"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "前500个撤单的量价相关性" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "买单强度-挂单价格激进度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['T1mCancel']
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            return database

    def prepare_T_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            cancel_df = database['T1mCancel']
            pre_close = cancel_df['pre_close'].max()
            ff_shares = cancel_df['ff_shares'].max()
            dt, ticker = cancel_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            bj = ticker[-2:] == 'BJ'
            cancel_df = filter_930(cancel_df)
            cancel_df['MDTime_delta'] = cancel_df['MDTime'].apply(
                    lambda x: get_time_delta(x) - 1800000) # 距离930毫秒数
            database['T1mCancel'] = cancel_df
            database['zcz'] = zcz
            database['bj'] = bj
            database['pre_close'] = pre_close
            database['ff_shares'] = ff_shares
            return database

    def calculate(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            cancel_df = database['T1mCancel']
            ff_shares = database['ff_shares']
            cancel_df = cancel_df[cancel_df['OrderPrice'] > 0]
            zcz = database['zcz']
            bj = database['bj']
            pre_close = database['pre_close']
            #
            if zcz:
                p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
            elif bj:
                p_zt = np.floor(pre_close * 100 * 1.3 + 0.5) / 100
            else:
                p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
            cancel_df = cancel_df[cancel_df['OrderPrice'] < p_zt]
            cancel_df = cancel_df.head(500) if len(cancel_df) > 500 else cancel_df
            res = pd.concat([cancel_df['OrderPrice'], cancel_df['OrderQty']], axis=1).corr(method='spearman').iloc[0, 1]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
