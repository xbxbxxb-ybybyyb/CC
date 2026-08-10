from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np



def cross_hub_num_array(data_array, d):

    # 过去一段时间曲线穿越中枢的次数

    data_centralized = data_array - move_mean_bk(data_array,window = d,min_count = int(d/2))

    flag = (data_centralized[1:] * data_centralized[:-1]) < 0

    output = np.sum(flag[-d:])

    return output

    

class fac_57_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['close_secmain', 'low_secmain']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 1500

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 2

        self.tmplist = []

        

    def calculate(self, data):        

        close = data['close_secmain'][-400:]        

        low = data['low_secmain'][-400:]

        rtn = close[1:] - close[:-1]

        vol1 = nanstd_np(rtn[-90:], ddof = 1)

        vol2 = nanstd_np(rtn[-360:], ddof = 1)

        co = cross_hub_num_array(close[-70:],30) + 1

        ret1 = close[-1] - nanmin_np(low[:-1][-90:])

        ret2 = close[-1] - nanmin_np(low[:-1][-360:])

        if abs(vol1) < 1e-8:

            vol1 = np.nan

        if abs(vol2) < 1e-8:

            vol2 = np.nan

        temp = ret1 / vol1 / np.sqrt(co) + 2 * ret2 / vol2 / np.sqrt(co)

        self.tmplist.append(temp)

        

        factor = ema_1(self.tmplist[-30:], 30, 1/11)

        return factor



    def pre_calculate(self, data):

        for i in range(30, -1, -1):

            if i == 0:

                close = data['close_secmain'][-400:]        

                low = data['low_secmain'][-400:]

            else:

                close = data['close_secmain'][-(400+i):-i]        

                low = data['low_secmain'][-(400+i):-i]

            
            if len(close) > 1:
                rtn = close[1:] - close[:-1]

                vol1 = nanstd_np(rtn[-90:], ddof = 1)

                vol2 = nanstd_np(rtn[-360:], ddof = 1)

                co = cross_hub_num_array(close[-70:],30) + 1

                ret1 = close[-1] - nanmin_np(low[:-1][-90:])

                ret2 = close[-1] - nanmin_np(low[:-1][-360:])

                if abs(vol1) < 1e-8:

                    vol1 = np.nan

                if abs(vol2) < 1e-8:

                    vol2 = np.nan

                temp = ret1 / vol1 / np.sqrt(co) + 2 * ret2 / vol2 / np.sqrt(co)

                self.tmplist.append(temp)
            else:
                self.tmplist.append(np.nan)
