import pandas as pd
from xfactor.BaseFactor import BaseFactor


class OperRevTTMStandardGrowth(BaseFactor):
    # 因子名称：OperRevTTMStandardGrowth
    # 计算公式：营业收入TTM值的稳健增长（即zscore）
    # 因子逻辑：营业收入稳健增长越高的股票，股价越有可能上涨
    depend_data = ['FactorData.Basic_factor.adjfactor', 'FactorData.WIND_AShareIncome']
    financial_lag = 3 * 365

    def calc_single(self, database):
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        income = database.depend_data['FactorData.WIND_AShareIncome']
        stk_code = adj.columns
        dt = int(adj.index[-1])
        income = income[(income['ACTUAL_ANN_DT'].values <= dt) & ((income['STATEMENT_TYPE'].values == 408002000) |
                                                                  (income['STATEMENT_TYPE'].values == 408003000))]
        income = income.sort_values('ACTUAL_ANN_DT').groupby(level=[0, 1]).last()
        rev = income['OPER_REV'].unstack().reindex(columns=stk_code)
        rev_ttm = rev.rolling(4).sum()
        zscore = (rev_ttm.values - rev_ttm.rolling(4).mean().values) / rev_ttm.rolling(4).std().values
        result = pd.DataFrame(zscore[-3:], columns=stk_code).fillna(method='ffill').iloc[-1]
        return result
