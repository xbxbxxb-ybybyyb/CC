# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class TurnNeuRetCorrSharp(BaseFactor):
    """

    *因子名 : TurnNeuRetCorrSharp
    *因子功能描述 : 收益率与市值中性化的换手率的相关系数的十日夏普
                     
    *因子参数 : close_adj-调整收盘价，turn-换手率，is_valid_raw-是否合法
    *作者 : 肖倩
    *因子创建日期 : 2019.02.15
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """

    factor_type = "DAY"

    s_close_badj = 'FactorData.Basic_factor.close_badj'
    s_pct_chg = 'FactorData.Basic_factor.pct_chg'
    s_turn = 'FactorData.Basic_factor.turn'
    s_amt = 'FactorData.Basic_factor.amt'

    depend_data = [s_close_badj, s_turn, s_amt, s_pct_chg]

    n = 10
    lag = n + 5 - 1 
    reform_window = n

    def calc_single(self, database):
        ret = database.depend_data[self.s_pct_chg]
        turn = database.depend_data[self.s_turn]
        amt = database.depend_data[self.s_amt]
        neu_turn = pd.DataFrame(columns = ret.columns)
        for i in range(self.n + 1):
            neu_turn =  neu_turn.append(self.get_neu_turn(turn[i:i+5], amt[i:i+5])) # neu_trn has n rows
        turn_shift = neu_turn.shift(1)

        factor = Util.array_coef(ret.tail(self.n), turn_shift.tail(self.n))
        return factor

    def reform(self, temp_result):
        temp_result = temp_result.rolling(self.n, min_periods=1).mean() / temp_result.rolling(self.n).std()
        return  temp_result

    # def definition(self, close_adj, turn,amt, is_valid_raw,n = 10):
        
        
    #     ret = close_adj.pct_change(1)
    #     neu_turn = self.get_neu_turn(turn,amt,is_valid_raw)
    #     turn_shift = neu_turn.shift(1)
        
    #     factor = ret.rolling(window=n).corr(turn_shift)
    #     factor = factor.rolling(n,min_periods=1).mean()/factor.rolling(n).std()
    #     factor[is_valid_raw == 0] = np.nan
        
    #     return factor

    def get_neu_turn(self, turn, amt):
        turn_valid = turn.tail(5)
        turn_valid_1week = turn_valid.mean()
        # turn_valid_1month = turn_valid.rolling(window=20,min_periods=20).mean()
        amt_valid = amt.tail(5)
        free_cap_valid = (amt_valid.iloc[-1]/turn_valid.iloc[-1])
        # result = pd.DataFrame(np.nan, index = is_valid_raw.index, columns=is_valid_raw.columns)
        date = turn.index[-1]
        factor_today = turn_valid_1week.dropna()
        result = pd.Series(np.nan, index = turn.columns, name = date)
        if len(factor_today) > 100:
            valid_stocks_today = factor_today.index
            size_today = np.log(free_cap_valid).loc[valid_stocks_today]
            # univariate Linear Regression
            X = size_today.values
            Y = factor_today.values
            X_bar = np.nanmean(X)
            Y_bar = np.nanmean(X)
            X_central = X - X_bar
            Y_central = Y - Y_bar
            b1 = np.nansum(X_central * Y_central) / np.nansum(X_central ** 2)
            b0 = Y_bar - X_bar * b1
            Y_predict = b0 + X * b1
            # model = LinearRegression(fit_intercept = True)
            # model.fit(X= size_today.values.reshape([len(size_today),1]), y = factor_today.values)
            # Y_predict = model.predict(X= size_today.values.reshape([len(size_today),1]))
            result[valid_stocks_today] = Y - Y_predict

        return result

    # def get_neu_turn(self, turn, amt, is_valid_raw):
    #     turn_valid = turn[is_valid_raw==1]
    #     turn_valid_1week = turn_valid.rolling(window=5,min_periods=5).mean()
    #     turn_valid_1month = turn_valid.rolling(window=20,min_periods=20).mean()
    #     amt_valid = amt[is_valid_raw==1]
    #     free_cap_valid = amt_valid/turn_valid
    #     result = pd.DataFrame(np.nan, index = is_valid_raw.index, columns=is_valid_raw.columns)

    #     for date in is_valid_raw.index:
    #         factor_today = turn_valid_1week.loc[date].dropna()
    #         if len(factor_today) < 100:
    #             continue
    #         valid_stocks_today = factor_today.index
    #         size_today = np.log(free_cap_valid.loc[date, valid_stocks_today])

    #         model = LinearRegression(fit_intercept= True)
       
    #         model.fit(X= size_today.values.reshape([len(size_today),1]), y = factor_today.values)
    #         y_hat = model.predict(X=size_today.values.reshape([len(size_today),1]))
    #         e = factor_today.values-y_hat
    #         result.loc[date, valid_stocks_today] = e
    #     return result     
    
            