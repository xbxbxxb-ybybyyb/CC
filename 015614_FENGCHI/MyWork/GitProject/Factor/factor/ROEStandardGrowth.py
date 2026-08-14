# import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


class ROEStandardGrowth(BaseFactor):
    # 因子名称：ROEStandardGrowth
    # 计算公式：ROE的稳健增长（即zscore）
    # 因子逻辑：ROE稳健增长越高的股票，股价越有可能上涨
    depend_data = ['FactorData.Basic_factor.adjfactor', 'FactorData.WIND_AShareIncome',
                   'FactorData.WIND_AShareBalanceSheet']
    financial_lag = 3 * 365

    def calc_single(self, database):
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        income = database.depend_data['FactorData.WIND_AShareIncome']
        balance = database.depend_data['FactorData.WIND_AShareBalanceSheet']
        stk_code = adj.columns
        dt = int(adj.index[-1])
        income = income[(income['ACTUAL_ANN_DT'].values <= dt) & ((income['STATEMENT_TYPE'].values == 408002000) |
                                                                  (income['STATEMENT_TYPE'].values == 408003000))]
        income = income.sort_values('ACTUAL_ANN_DT').groupby(level=[0, 1]).last()
        profit = income['NET_PROFIT_EXCL_MIN_INT_INC'].unstack().reindex(columns=stk_code)
        balance = balance[(balance['ACTUAL_ANN_DT'].values <= dt) & ((balance['STATEMENT_TYPE'].values <= 408005000) |
                                                                     (balance['STATEMENT_TYPE'].values == 408050000))]
        balance = balance.sort_values('ACTUAL_ANN_DT').groupby(level=[0, 1]).last()
        equity = balance['TOT_SHRHLDR_EQY_EXCL_MIN_INT'].unstack().reindex(columns=stk_code)
        roe = profit / equity.rolling(2).mean()
        zscore = (roe.values - roe.shift(1).rolling(4).mean().values) / roe.shift(1).rolling(4).std().values
        result = pd.DataFrame(zscore[-3:], columns=stk_code).fillna(method='ffill').iloc[-1]
        return result
