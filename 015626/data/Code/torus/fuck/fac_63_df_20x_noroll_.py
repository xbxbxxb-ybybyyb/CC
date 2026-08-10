from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





def nanforward_fill(arr):

    """

    使用前向填充（Forward Fill）填充数组中的 NaN 值。

    """

    arr = arr.astype(float).copy()  # 确保数组为浮点类型

    mask = np.isnan(arr)

    if not mask.any():

        return arr  # 如果没有 NaN，直接返回原数组



    # 获取非 NaN 值的索引和值

    non_nan_idx = np.where(~mask)[0]

    non_nan_vals = arr[non_nan_idx]



    # 获取 NaN 值的索引

    nan_idx = np.where(mask)[0]



    # 使用 searchsorted 找到每个 NaN 对应的最近非 NaN 索引

    indices = np.searchsorted(non_nan_idx, nan_idx, side='right') - 1

    valid = indices >= 0  # 过滤无效索引（如开头的 NaN）



    # 填充 NaN 值

    arr[nan_idx[valid]] = non_nan_vals[indices[valid]]

    return arr



class fac_63_df_20x_noroll_(FutureFactor): 

    def __init__(self, ticker, freq):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 9

        self.required_columns = ['close_secmain']        

        self.normalize_size = int(20 * self.bars_dict[ticker] / freq)

        self.normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__



    def calculate(self, data):

        cls = data['close_secmain'][-2060:]

        cmax = move_max_bk(cls,window = 2000, min_count = 1000)

        cmin = move_min_bk(cls,window = 2000, min_count = 1000)

        dem = cmax - cmin

        dem[abs(dem) < 1e-8] = np.nan 

        price_level = nanforward_fill((cls - cmin) / (cmax - cmin) * 2 - 1)

        price_level = price_level[-60:]

        

        price_std = nanforward_fill(move_std_bk(cls, window = 1800, min_count = 2, ddof = 1))

        price_std = price_std[-60:]

        price_std[abs(price_std) < 1e-8] = np.nan

        factor_array = price_level / price_std        

        weight = 1/21 * np.array([(1 - 1/21) ** i for i in range(60)])[::-1]

        factor = nansum_np(factor_array * weight) / nansum_np(weight) # truncate_ema_1        

        return factor