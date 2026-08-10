from future_factor import FutureFactor
import numpy as np


class MinuteLocalExtremaVolumeRatio(FutureFactor):
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 1
    data_dict = {}
    data_dict['Continuous_Data'] = {'IC': ['close', 'volume']}
    normalize_size = 60
    normalize_type = 'ts_rank'
    
    def get_local_extrema(self, price):
        threshold = 2 * np.nanstd(price[1:] / price[:-1] - 1)
        localhighs = []
        locallows = []
        prel = 0
        preh = 0
        lh = 0
        ll = 0
        for i in range(len(price)):
            if price[lh] >= price[prel] * (1 + threshold) and price[lh] >= price[i] * (1 + threshold):
                localhighs.append(lh)
                lh = i
                prel = i
            else:
                if price[i] < price[lh] / (1 + threshold) or price[i] > price[lh]:
                    lh = i
                if price[i] <= price[prel]:
                    prel = i
            if price[ll] <= price[preh] / (1 + threshold) and price[ll] <= price[i] / (1 + threshold):
                locallows.append(ll)
                ll = i
                preh = i
            else:
                if price[i] > price[ll] * (1 + threshold) or price[i] < price[ll]:
                    ll = i
                if price[i] >= price[preh]:
                    preh = i
        if price[lh] >= price[prel] * (1 + threshold):
            localhighs.append(lh)
        if price[ll] <= price[preh] / (1 + threshold):
            locallows.append(ll)
        return localhighs, locallows
        
    def calculate(self, data):
        lb = 60
        close = data['close_cont_IC'].values[-lb:]
        volume = data['volume_cont_IC'].values[-lb:]
        lh, ll = self.get_local_extrema(close)
        if (len(ll) >= 1) & (len(lh) >= 1):
            vol_ll = np.nanmean(volume[ll])
            vol_lh = np.nanmean(volume[lh])
            f = (vol_ll - vol_lh) / (vol_ll + vol_lh)
        else:
            f = 0
        if np.isnan(f) or np.isinf(f):
            f = 0
        return f
