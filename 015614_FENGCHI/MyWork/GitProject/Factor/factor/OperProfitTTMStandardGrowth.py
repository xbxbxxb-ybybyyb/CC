import pandas as pd
from xfactor.BaseFactor import BaseFactor


class OperProfitTTMStandardGrowth(BaseFactor):
    # 因子名称：OperProfitTTMStandardGrowth
    # 计算公式：营业利润TTM值的稳健增长（即zscore）
    # 因子逻辑：营业利润稳健增长越高的股票，股价越有可能上涨
    depend_data = ['FactorData.WIND_AShareIncome', 'FactorData.Basic_factor.adjfactor']
    financial_lag = 365 * 3

    def calc_single(self, database):
        income = database.depend_data['FactorData.WIND_AShareIncome']
        adj = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = adj.columns
        dt = int(adj.index[-1])
        # 提取利润表，只需要单季度合并报表和单季度调整合并报表
        income = income[(income['ACTUAL_ANN_DT'].values <= dt) & ((income['STATEMENT_TYPE'].values == 408002000) |
                                                                  (income['STATEMENT_TYPE'].values == 408003000))]
        income = income.sort_values('ACTUAL_ANN_DT').groupby(level=[0, 1]).last()
        oper_profit = income.OPER_PROFIT.unstack().reindex(columns=stk_code)  # 提取营业利润科目
        oper_profit_ttm = oper_profit.rolling(4).sum()  # 计算ttm值
        zscore = (oper_profit_ttm.values - oper_profit_ttm.rolling(4).mean().values
                  ) / oper_profit_ttm.rolling(4).std().values  # 计算zscore
        result = pd.DataFrame(zscore[-3:], columns=stk_code).fillna(method='pad').iloc[-1]
        return result
