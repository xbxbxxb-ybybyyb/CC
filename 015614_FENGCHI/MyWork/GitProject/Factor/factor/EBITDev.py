import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


class EBITDev(BaseFactor):
    depend_data = ['FactorData.WIND_AShareIncome', 'FactorData.Basic_factor.mkt_cap_ard',
                   'FactorData.Basic_factor.is_valid_raw']
    reform_window = 250
    financial_lag = 365

    def calc_single(self, database):
        income = database.depend_data['FactorData.WIND_AShareIncome']
        mkt_cap = database.depend_data['FactorData.Basic_factor.mkt_cap_ard']
        valid = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        dt = int(mkt_cap.index[-1])
        stk_code = mkt_cap.columns
        mkt_cap = mkt_cap.values[-1]
        valid = valid.values[-1]
        income = income[(income['ACTUAL_ANN_DT'].values <= dt) & ((income['STATEMENT_TYPE'].values == 408001000) |
                                                                  (income['STATEMENT_TYPE'].values == 408004000) |
                                                                  (income['STATEMENT_TYPE'].values == 408005000))]
        income = income.sort_values('ACTUAL_ANN_DT').groupby(level=[0, 1]).last()
        ebit = income.EBIT.unstack().reindex(columns=stk_code).fillna(method='pad').values[-1]
        result = ebit / mkt_cap
        result[valid == 0] = np.nan
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = (temp_result - temp_result.rolling(250, 1).mean()) / temp_result.rolling(250, 1).std()
        return alpha
