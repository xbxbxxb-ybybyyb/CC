from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





def irr_filter(input_signal, window):

    alpha = 2 / (window + 1)

    b0 = alpha - (alpha ** 2) / 4

    b1 = (alpha ** 2) / 2

    b2 = -(alpha - (3 * alpha ** 2) / 4)

    a1 = -2 * (1 - alpha)

    a2 = (1 - alpha) ** 2

    y = np.zeros_like(input_signal)

    for n in range(len(input_signal)):

        if n == 0:

            y[n] = b0 * input_signal[n]

        elif n == 1:

            y[n] = b0 * input_signal[n] + b1 * input_signal[n-1] - a1 * y[n-1]

        else:

            y[n] = (b0 * input_signal[n] + b1 * input_signal[n-1] + b2 * input_signal[n-2] - a1 * y[n-1] - a2 * y[n-2])

    return y



def nanforward_fill(arr):

    """

    使用前向填充（Forward Fill）填充数组中的 NaN 值。

    """

    arr = arr.astype(float).copy()  # 确保数组为浮点类型

    mask = np.isnan(arr)

    if not mask.any():

        return arr

    non_nan_idx = np.where(~mask)[0]

    non_nan_vals = arr[non_nan_idx]



    nan_idx = np.where(mask)[0]



    indices = np.searchsorted(non_nan_idx, nan_idx, side='right') - 1

    valid = indices >= 0  # 过滤无效索引（如开头的 NaN）

    arr[nan_idx[valid]] = non_nan_vals[indices[valid]]

    return arr

    

class fac_79_df(FutureFactor): 



    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(int(np.ceil(125/ self.bars_dict[self.ticker])) * freq) # different product should be different

        self.required_columns = ['last_n_20_volume', 'last_n_20_ret','volume']

        self.normalize_size = 2000

        self.normalize_type = 'ts_rank'



    def calculate(self, data):

        ba = data['last_n_20_volume']

        ret10 = data['last_n_20_ret']

        volume = data['volume']

        volume[abs(volume) < 1e-8] = np.nan

        fac_raw = nanforward_fill(ret10 * ba / volume)

        fac = irr_filter(fac_raw[-25*5:],25)[-1] + ema_1(fac_raw[-25*3:],25*3,1/26)

        return fac