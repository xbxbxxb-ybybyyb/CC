from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
class NetProfitSurprise(BaseFactor):
    """
    * 因子名 : NetProfitSurprise
    * 因子功能描述 : 净利润增长惊喜度。用过去三年考虑季节影响的净利润预测当前季度，查看达预期的程度，若超出很多则很好
    * 作者 : 刘正
    * 因子创建日期 : 2019.01.24
    * 因子修改日期 : 2020.01.14
    * 修改人 : 游加平
    """
    factor_type = "DAY"
    depend_data = ["FactorData.WIND_AShareIncome", 'FactorData.Basic_factor.turn']
    financial_lag = 1400
    lag = 0

    def calc_single(self, database):
        time_s = time.time()
        WIND_AShareIncome = database.depend_data['FactorData.WIND_AShareIncome']
        turn = database.depend_data['FactorData.Basic_factor.turn']
        
        data = WIND_AShareIncome[['ANN_DT', 'STATEMENT_TYPE', 'NET_PROFIT_EXCL_MIN_INT_INC']]
        data = data[data['STATEMENT_TYPE']==408001000]
        ann_dt = data['ANN_DT'].unstack().reindex(columns=turn.columns)
        net_profit = data['NET_PROFIT_EXCL_MIN_INT_INC'].unstack().reindex(columns=turn.columns)

        net_profit_ttm = self.trans_ttm(net_profit)
        net_profit_surprise  = self.perform_surprise(net_profit_ttm)
        trading_day_list = turn.index.tolist()
        performace_surprise_3y = self.get_daily_df_from_quarter_field(ann_dt, net_profit_surprise, trading_day_list)
        ans = performace_surprise_3y.iloc[-1]
        return ans
    
    def perform_surprise(self, df_quarter_raw):
        def pred_ni(x):
            T = len(x)-5
            c = (x[4 :T+4].sum() - x[:T].sum()) / T
            return x[T]+c

        def cal_sig(x):
            T = len(x)-5
            c = (x[4 :T+4].sum() - x[:T].sum()) / T
            # c = 0
            # for i in range(T):
            #     c = c+x[i+4]-x[i]
            # c = c/T

            sig = np.sum((x[4:T+4] - x[:T] - c) ** 2)
            # for i in range(T):
            #     sig += np.square(x[i+4]-x[i]-c)
            return np.sqrt(sig)/(T-1)

        predict = df_quarter_raw.rolling(13).apply(pred_ni)
        sigma = df_quarter_raw.rolling(13).apply(cal_sig)
        factor_df = (df_quarter_raw - predict) / sigma
        return factor_df

    def trans_ttm(self, df_quarter):
        df_values = df_quarter.values
        diff_list = []
        for j in range(df_values.shape[0]):
            if j % 4 !=0:
                diff = df_values[j] - df_values[j-1]
            else:
                diff = df_values[j]
            diff_list.append(diff)
        diff_array = np.stack(diff_list, axis=0)
        diff_df = pd.DataFrame(diff_array, index=df_quarter.index, columns=df_quarter.columns)
        return diff_df

    def get_daily_df_from_quarter_field(self, stm_issuingdate, df_quarter, trading_date_list):
        stm_issuingdate = stm_issuingdate.astype(float).values
        daily_array = np.nan * np.ones((len(trading_date_list), len(df_quarter.columns)))
        for idx, date in enumerate(trading_date_list):
            daily_array[idx] = pd.DataFrame(np.where(stm_issuingdate <= int(date), df_quarter, np.nan)).fillna(
                method='ffill').iloc[-1].values
        return pd.DataFrame(daily_array, index=trading_date_list, columns=df_quarter.columns)