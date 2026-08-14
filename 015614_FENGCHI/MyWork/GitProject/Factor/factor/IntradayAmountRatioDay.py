import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class IntradayAmountRatioDay(BaseFactor):
    # 因子名称：IntradayAmountRatio
    # 计算公式：盘中成交额（10:00~11:00以及13:30~14:30）的成交额 / 全天成交额，取15日Sharpe
    # 因子逻辑：开盘和尾盘存在较多噪声交易，盘中成交额相对开盘和尾盘成交额越大，股价越有可能上涨
    depend_data = ['FactorData.Basic_factor.amt_minute']
    reform_window = 15

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = amt.columns
        amt = amt.values
        # 盘中成交额（10:00~11:00以及13:30~14:30）的成交额 / 全天成交额
        res = (np.nansum(amt[30: 90], axis=0) + np.nansum(amt[150:210], axis=0)) / np.nansum(amt, axis=0)
        res = pd.Series(res, index=stk_code)
        return res

    def reform(self, temp_result):
        alpha = temp_result.rolling(15).mean() / temp_result.rolling(15).std()
        return alpha
