from future_factor import FutureFactor
import numpy as np


class MinuteOpenInterestReturnCorrtimesReturn_IH(FutureFactor):
    '''
    Description: -mean(pct_chg(close_000905.SH, 1), 60) * corr(pct_chg(close_000905.SH, 1), OpenInterest, 720)
    Class: PV_Corr
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 3
    data_dict = {}
    data_dict['Continuous_Data'] = {'IH':['OpenInterest']}
    data_dict['Index_Id'] = {'000016.SH': ['close']}
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_000016.SH'].values[-237 * self.days_past - 1:]
        interest = data['OpenInterest_cont_IH'].values[-237 * self.days_past:]
        r = np.diff(close) / close[:-1]
        f = -np.nanmean(r[-60:]) * np.corrcoef(interest, r)[0, 1]
        return f
