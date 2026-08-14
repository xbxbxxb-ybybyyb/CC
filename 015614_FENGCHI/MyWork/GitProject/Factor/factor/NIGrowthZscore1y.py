import pandas as pd
from xfactor.BaseFactor import BaseFactor


class NIGrowthZscore1y(BaseFactor):
    depend_data = ['FactorData.WIND_AShareIncome', 'FactorData.Basic_factor.adjfactor']
    financial_lag = 365 * 3

    def calc_single(self, database):
        income = database.depend_data['FactorData.WIND_AShareIncome']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = adj.columns
        dt = int(adj.index[-1])
        income = income[(income['ACTUAL_ANN_DT'].values <= dt) & ((income['STATEMENT_TYPE'].values == 408002000) |
                                                                  (income['STATEMENT_TYPE'].values == 408003000))]
        income = income.sort_values('ACTUAL_ANN_DT').groupby(level=[0, 1]).last()
        ni = income.NET_PROFIT_EXCL_MIN_INT_INC.unstack().reindex(columns=stk_code)
        ni_ttm_g = ni.rolling(4).sum()
        ni_ttm_g = pd.DataFrame(ni_ttm_g.values / ni_ttm_g.shift(1).values - 1, index=ni_ttm_g.index,
                                columns=ni_ttm_g.columns)
        zscore = (ni_ttm_g.values - ni_ttm_g.rolling(4).mean().values) / ni_ttm_g.rolling(4).std().values
        result = pd.DataFrame(zscore[-3:], columns=stk_code).fillna(method='pad').iloc[-1]
        return result
