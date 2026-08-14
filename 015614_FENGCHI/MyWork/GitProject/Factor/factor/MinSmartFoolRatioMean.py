import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinSmartFoolRatioMean(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.free_float_shares', 'FactorData.Basic_factor.close']
    reform_window = 4

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close_min = database.depend_data['FactorData.Basic_factor.close_minute']
        amt_min = database.depend_data['FactorData.Basic_factor.amt_minute']
        ffs = database.depend_data['FactorData.Basic_factor.free_float_shares']
        close = database.depend_data['FactorData.Basic_factor.close']
        stk_code = close_min.columns.union(ffs.columns)
        close_min = close_min.reindex(columns=stk_code)
        amt_min = amt_min.reindex(columns=stk_code)
        ffs = ffs.reindex(columns=stk_code)
        close = close.reindex(columns=stk_code)
        ffc = ffs.values * 10000 * close.values
        turn = amt_min.values / ffc
        re = close_min.pct_change().values
        last_30_min_re = re[-30:]
        last_30_min_turn = turn[-30:]
        re_rank = pd.DataFrame(last_30_min_re).rank(pct=True).values
        smart_rate = np.nanmean(np.where(re_rank > 0.8, last_30_min_turn, np.nan), axis=0)
        fool_rate = np.nanmean(np.where(re_rank < 0.2, last_30_min_turn, np.nan), axis=0)
        fool_rate = np.where(fool_rate != 0, fool_rate, np.nan)
        ratio = smart_rate / fool_rate
        if (~np.isnan(ratio)).sum() == 0:
            ratio = np.zeros(len(ratio))
        ratio = pd.Series(ratio, index=stk_code)
        return ratio

    def reform(self, temp_result):
        alpha = -temp_result.rolling(5, 1).mean()
        return alpha
