import pandas as pd
from xfactor.BaseFactor import BaseFactor


class GPMarTTMStandardGrowth(BaseFactor):
    # 因子名称：GPMarTTMStandardGrowth
    # 计算公式：毛利率TTM值的稳健增长（即zscore）
    # 因子逻辑：毛利率稳健增长越高的股票，股价越有可能上涨
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
        oper_rev = income['OPER_REV'].unstack().reindex(columns=stk_code)
        oper_rev_ttm = oper_rev.rolling(4).sum()
        oper_cost = income['LESS_OPER_COST'].unstack().reindex(columns=stk_code)
        oper_cost_ttm = oper_cost.rolling(4).sum()
        gpmar_ttm = (oper_rev_ttm - oper_cost_ttm) / oper_rev_ttm
        zscore = (gpmar_ttm.values - gpmar_ttm.rolling(4).mean().values) / gpmar_ttm.rolling(4).std().values
        result = pd.DataFrame(zscore[-3:], columns=stk_code).fillna(method='ffill').iloc[-1]
        return result
