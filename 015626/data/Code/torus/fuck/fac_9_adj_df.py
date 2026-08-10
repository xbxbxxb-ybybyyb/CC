from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np

def irr_filter2(data, coef, bbb):
    window = bbb 
    sig1_list = data[-window * 6 :]
    return irr_filter(sig1_list[-int(window * coef):],  int(window * coef))[-1]

class fac_9_adj_df(FutureFactor):


    def __init__(self, ticker, freq):

        
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(2 * freq)
        self.required_columns = ['close', 'volume', 'BidAskSpreadMean', 'open', 'low', 'dt']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 1800
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.sig1_list = []
        self.rtn_list = []
        
    def calculate(self, data):
        hclose = data['close'][-31:]
        coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(data['BidAskSpreadMean'][-30:]))
        if coef_temp > 10:
            coef =0.1
        elif (coef_temp > 6) and (coef_temp <= 10):
            coef = 0.3
        elif (coef_temp > 4) and (coef_temp <= 6):
            coef = 1
        elif (coef_temp > 3) and (coef_temp <= 4):
            coef = 2
        elif (coef_temp <= 3):
            coef = 5
        else:
            coef = 6
            
        aaa = 120
        bbb = 2
        ccc = 6
        # np.datetime64(pd.to_datetime('201703061459'))
        
        twap = (data['open'][-350:] + data['close'][-350:]) / 2
        rtn = (twap[int(coef * 45)-1:] - twap[:-int(coef * 45)+1])
        if len(rtn) > 1:
            self.rtn_list.append(rtn[-1])
        else:
            self.rtn_list.append(np.nan)

        #if data['dt'][-1] == np.datetime64(pd.to_datetime('201703060900')):
        #print(self.rtn_list[-aaa:])
        #print(nanstd_np(self.rtn_list[-aaa:], ddof = 1))
        vol1 = nanstd_np(self.rtn_list[-aaa:], ddof = 1)

        ret = data['close'][-1] - nanmin_np(data['low'][-int(coef * aaa) - 1 :-1])
        sig = ret / r(vol1)
        self.sig1_list.append(sig)

        return irr_filter4(np.array(self.sig1_list), coef, bbb)

    def pre_calculate(self, data):
        for i in range(121, -1, -1):
            if i == 0:
                hclose = data['close'][(-31 - i) : ]
                ba = data['BidAskSpreadMean'][(-30 - i):]
                dopen = data['open'][(-350 - i): ]
                dclose = data['close'][(-350 - i): ]
                dlow = data['low'][(-350 - i): ]
            else:
                hclose = data['close'][(-31 - i) : -i]
                ba = data['BidAskSpreadMean'][(-30 - i) : -i]
                dopen = data['open'][(-350 - i) : -i]
                dclose = data['close'][(-350 - i) : -i ]
                dlow = data['low'][(-350 - i) : -i ]
            
            aaa = 120


            if len(hclose) > 0:
                coef_temp = nanstd_np(hclose[1:] - hclose[:-1], ddof = 1) / r(nanmean_np(ba))

                if coef_temp > 10:
                    coef =0.1
                elif (coef_temp > 6) and (coef_temp <= 10):
                    coef = 0.3
                elif (coef_temp > 4) and (coef_temp <= 6):
                    coef = 1
                elif (coef_temp > 3) and (coef_temp <= 4):
                    coef = 2
                elif (coef_temp <= 3):
                    coef = 5
                else:
                    coef = 6
                
                twap = (dopen[-350:] + dclose[-350:]) / 2

                rtn = (twap[int(coef * 45)-1:] - twap[:-int(coef * 45)+1])
                if len(rtn) > 1:
                    self.rtn_list.append(rtn[-1])
                else:
                    self.rtn_list.append(np.nan)
        
                vol1 = nanstd_np(self.rtn_list[-aaa:], ddof = 1)
                
                ret = hclose[-1] - nanmin_np(dlow[-int(coef * aaa) - 1 :-1])
                sig = ret / r(vol1)
                #print(twap[int(coef * 45)-1:][-1], twap[:-int(coef * 45)+1][-1])
                if len(rtn) > 0:
                    self.rtn_list.append(rtn[-1])
                else:
                    self.rtn_list.append(np.nan)
                self.sig1_list.append(sig)
            else:
                self.rtn_list.append(np.nan)
                self.sig1_list.append(np.nan)

        