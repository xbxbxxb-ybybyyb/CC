import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg11(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg11, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                        lookback_bars=2000)

    def on_bar(self, data):
        # 收益率的均值与标准差之和
        close = data['close_zz500']
        ret = close.pct_change(5, fill_method=None)
        ret_mean = ts_mean(ret, 20)
        ret_std = ts_std(ret, 20)
        factor = ret_mean + 1 * ret_std
        # factor = factor.rolling(10, min_periods=5).mean()
        # factor = factor.sum(axis=1)

        factor = (factor * data['weight_zz500']).sum(axis=1)
        # factor = ((ret_long * data['weight_zz500']).sum(axis=1)) / weight_long.sum(axis=1) - (ret * data['weight_zz500']).sum(axis=1)
        #factor = factor.rolling(15, min_periods=2).mean()
        factor = factor.to_frame()   
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 1200)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        factor[factor<=-0.5] = 0
        #factor[factor>=0.5] = np.nan
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:15:32 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class LminLmean_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low_spot']
        super(LminLmean_ind_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        ctl_r = -data['low_spot'].rolling(50, min_periods =30).min()/data['low_spot'].rolling(30, min_periods =15).mean()
        factor = ctl_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=True):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class high_low_diff_a2p_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(high_low_diff_a2p_zsj, self).__init__(
            required_columns=['close_zz500', 'amount_zz500', 'high_zz500', 'low_zz500', 'open_zz500', 'weight_boolean_zz500'],
            lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        stk_amt = data['amount_zz500'][bool_mask]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        # factor_name = 'high_low_diff_a2p'
        roll_win = 30
        ma_win = 30
        ts_pct_win = 2400
        min_pct = 0.9
        min_periods = int(roll_win * min_pct)
        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = high_open_diff.rolling(roll_win, min_periods).sum() - \
                            open_low_diff.rolling(roll_win, min_periods).sum()
        high_low_diff_active_raw = high_low_diff_stk[active_mask].mean(axis=1)
        high_low_diff_inactive_raw = high_low_diff_stk[inactive_mask].mean(axis=1)
        high_low_diff_a2p_raw = high_low_diff_active_raw - high_low_diff_inactive_raw
        high_low_diff_a2p = calc_ma_helper(high_low_diff_a2p_raw, ma_win, ts_pct_win, min_pct)
        # ts_factor_quick(high_low_diff_a2p, price, factor_name, layers=5)

        factor = high_low_diff_a2p.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200 * 4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from utils_zsj import *



class csv_disp_sign_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(csv_disp_sign_zsj, self).__init__(factor_name = 'csv_disp_sign_zsj',
                                              required_columns = ['close_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 2400)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        factor_name = 'csv_disp_sign'
        csv_disp = stk_ret.std(axis=1)
        stk2idx_ret = stk_ret.mean(axis=1)
        csv_disp_sign_raw = csv_disp * np.sign(stk2idx_ret)
        csv_disp_sign_raw = csv_disp_sign_raw.rolling(130,min_periods=30).mean()
        csv_disp_sign = rolling_norm(csv_disp_sign_raw,242*5)
        factor = pd.DataFrame(csv_disp_sign,columns=[self.__class__.__name__])
        return factor



##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_icif(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_icif, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        factor = df['close'] - df['close_if']
        factor = factor - mean(factor, 240)
        factor = mean(factor, 20)
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 13:17:31 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class IFIC4_CC(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot_if']
        super(IFIC4_CC, self).__init__(required_columns=required_columns)
    

    def on_bar(self, data):

        temp = data['close_spot_if'].rolling(60, min_periods = 15).mean() - data['close_spot_if'].shift(20).rolling(40, min_periods = 7).mean()
        factor = temp.to_frame()

        factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator


def log(df):
    return np.log(df[df > 0])


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


class wsc1_future_kpz(FactorGenerator):
    def __init__(self):
        required_columns = ['close_if', 'recent_month_mask']
        lookback_bars = 2000
        super(wsc1_future_kpz, self).__init__(required_columns=required_columns,
                                              lookback_bars=lookback_bars)

    def on_bar(self, df):
        # 算子搜索
        mask = df['recent_month_mask']
        factor = log(df['close_if'])
        factor = rolling_norm(factor)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor < 0] = 0
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_delay(df1, d):
    # A_(i-d)
    output = df1.shift(periods=d)
    return output


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output
    

class wsc4_future_kpz(FactorGenerator):
    def __init__(self):
        super(wsc4_future_kpz, self).__init__(required_columns=['close_if', 'recent_month_mask'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        # dpo技术指标
        mask = data['recent_month_mask']
        close = data['close_if']
        N = 20
        dpo = close - ts_delay(ts_mean(close, N), int(N/2+1))
        factor = abs(dpo - dpo.rolling(60, min_periods=30).median()) # 把非线性因子变换成线性因子
        factor = factor.rolling(30, min_periods=15).mean()
        factor = ts_rank(factor, 600*2)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts50_future_nr_tr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix, 'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts50_future_nr_tr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        returns = df['close' + suffix].pct_change(fill_method=None)
        N = 20
        factor = ts_sum((returns>0),N)
        factor = ts_mean(factor, N)
        factor = ts_rank(factor, 5 * 242)

        factor = rolling_norm(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 60)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0] = 0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc15_cfg_vs(FactorGeneratorComplex):
    def __init__(self):
        super(wsc15_cfg_vs, self).__init__(required_columns=['close_zz500', 'stk_volatility_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']

        # vidya技术指标,vi可用来衡量股票过去一段时间的趋势，趋势越强vi值越大，此时vidya赋予当前的close更大的权重，捕捉趋势，反之同理。
        stk_close = data['close_zz500']
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        temp[abs(temp)<1e-8] = np.nan
        vi = abs(ts_delta(stk_close, n)) / temp
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 240)
        
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1800)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.3] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:12:50 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class VLSM_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'volume_zz500', 'weight_boolean_zz500']
        
        super(VLSM_CFG2_CC, self).__init__(required_columns=required_columns
                                  )

    

    def on_bar(self, data):
        stk_amount = (data['amount_zz500'])[data['weight_boolean_zz500']]
        bool_df = 2 * stk_amount.rank(axis=1, pct=True) - 1
        
        vwap = data['amount_zz500']/data['volume_zz500']
        price_diff_1 = vwap/vwap.shift(1)-1
        price_diff_30 = vwap/vwap.shift(30)-1
        copcor1_r = -(price_diff_1-price_diff_30)#.rolling(10, min_periods = 1).mean()       
        factor = (bool_df*copcor1_r[data['weight_boolean_zz500']]).mean(axis = 1).to_frame()
        factor = factor.rolling(10, min_periods = 1).mean()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]

        #factor[factor<=-0.5] = 0
        factor = ts_rank(factor)
        #factor = factor.rolling(3, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor[factor<=-0.5]=0
        return factor

##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from utils_zsj import *

class ret_active2inactive_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(ret_active2inactive_zsj, self).__init__(factor_name = 'ret_active2inactive_zsj',
                                              required_columns = ['close_zz500','amount_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 2400)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']
        stk_amt = data['amount_zz500'][bool_mask]
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        ma_win = 180
        ts_pct_win = 1200
        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0
        ret_active_raw = stk_ret[active_mask].mean(axis=1)
        ret_inactive_raw = stk_ret[inactive_mask].mean(axis=1)
        ret_active2inactive_raw = ret_active_raw - ret_inactive_raw
        ret_active2inactive = calc_ma_helper(ret_active2inactive_raw, ma_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(ret_active2inactive,columns=[self.__class__.__name__])
        return factor



##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
# from help_functions_wsc import replace_zero


    
class wsc_hf17(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf17, self).__init__(required_columns=['Bid1AmtMean_500', 'Buy1NumOrdersMean_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 买一挂单金额除以买一挂单数量，表征平均一单的挂单金额，还是大小单逻辑
        factor_raw = hf_data['Bid1AmtMean_500'].sum(axis=1) / hf_data['Buy1NumOrdersMean_500'].sum(axis=1)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *


class wyc_if_2hour_return(FactorGenerator):
    def __init__(self):
        required_columns=['close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_if_2hour_return, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']

        cif = df['close_if']
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif / cif.shift(1) - 1
        factor = mean(ifreturn, 200)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor[factor<0]=0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc13_cfg_ar(FactorGeneratorComplex):
    def __init__(self):
        super(wsc13_cfg_ar, self).__init__(required_columns=['weight_zz500', 'volume_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_zz500']
        weight_true = data['weight_boolean_zz500']
        amount_mask = stk_amount[weight_true]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 东方金工20191029，用区间内的vwap和vwap均值之间的偏差度量买卖压力
        stk_volume = data['volume_zz500']
        stk_vwap = stk_amount / stk_volume
        vwap_ma = ts_mean(stk_vwap, 45)
        amount_ma = ts_mean(stk_amount, 45)
        volume_ma = ts_mean(stk_volume, 45)
        volume_ma[abs(volume_ma)<1e-8] = np.nan
        temp = amount_ma / volume_ma
        temp[abs(temp)<1e-8] = np.nan
        apb = vwap_ma / temp
        factor_init = -np.log(apb)

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 2000)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_future_nr_cr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'high' + suffix,'low' + suffix,'close' + suffix,'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts6_future_nr_cr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        N = 45
        a = (df['high' + suffix] - df['low' + suffix])
        a[abs(a) < 1e-8] = np.nan
        factor = df['volume' + suffix] * ((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / a
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/N)
        factor = ts_rank(factor, 1200)
        factor = ts_mean(factor, 15)

        factor = rolling_norm(factor, 5 * 242)

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 20)
        factor = ts_mean(factor, 100)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 13:23:21 2021

@author: appadmin
"""
#GA_ind_CC_nr_w_a

import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class GA_ind_nr_w_a_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_zz500','amount_zz500', 'close_zz500', 'open_zz500', 'weight_zz500', 'low_zz500', 'high_zz500']

        super(GA_ind_nr_w_a_CFG_CC, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, data):
        df_s = (data['amount_zz500'].rolling(120, min_periods = 15).sum())[data['weight_boolean_zz500']]
        stk_weight = data['weight_zz500']

        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)


        bool_df = stk_weight*temp1

        a = data['high_zz500'].rolling(120, min_periods = 60).max()-data['open_zz500'].shift(120)
        b = data['close_zz500'] - data['low_zz500'].rolling(120, min_periods = 60).min()
        c = (data['high_zz500'].rolling(120, min_periods = 60).max()-data['low_zz500'].rolling(120, min_periods = 60).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        vwtc_r = rolling_norm(vwtc_r, 242)
        factor = (vwtc_r*bool_df).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:31:06 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class ClMaxClMin_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'recent_month_mask']
 
        super(ClMaxClMin_CC, self).__init__(
                                  required_columns=required_columns)

    
    def on_bar(self, data):

        m_vwap_ind_r = (data['close']).rolling(45, min_periods = 30).max()/data['close'].rolling(45, min_periods = 30).min()
        factor = m_vwap_ind_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts414_vr_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','stk_volatility_zz500']
        lookback_bars=2000
        super(wyc_ts414_vr_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = pd.DataFrame(np.where(df['close' + suffix] > delay(df['close' + suffix], 2), std(df['close' + suffix], 50), 0),
                              index=df['close' + suffix].index, columns=df['close' + suffix].columns)

        factor = ts_mean(factor, 30)

        factor = factor * (2 * df['stk_volatility_zz500'].rank(axis=1, pct=True) - 1)
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 60)
        factor = ts_mean(factor, 10)

        factor.columns = [columnname]
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        factor[factor > 0] = 0

        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts38_spot(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts38_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        temp1 = df['close_spot'].copy()
        temp1[df['close_spot'] > delay(df['close_spot'], 1)] = std(df['close_spot'],20)
        temp1[df['close_spot'] <= delay(df['close_spot'], 1)] = 0
        a = ts_truncated_ema(temp1, 5 * 242, 1/100)

        temp1[df['close_spot'] > delay(df['close_spot'], 1)] = 0
        temp1[df['close_spot'] <= delay(df['close_spot'], 1)] = std(df['close_spot'], 20)
        b = ts_truncated_ema(temp1, 5 * 242, 1/100)

        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = ts_rank_positive(factor, 30)
        factor = mean(factor, 100)

        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc9_cfg_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc9_cfg_vr, self).__init__(required_columns=['close_zz500', 'open_zz500', 'volume_zz500', 'stk_volatility_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 假设持仓30分钟，min_30_earning表示那一分钟这笔持仓的盈亏
        stk_close = data['close_zz500']
        stk_open = data['open_zz500']
        stk_volume = data['volume_zz500']
        min_30_earning = (stk_close - stk_open.shift(30)) * stk_volume
        factor_init = min_30_earning

        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_if_2hour_return_ws_cfg(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'weight' + suffix]
        lookback_bars=2000
        super(wyc_if_2hour_return_ws_cfg, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        cif = df['close' + suffix]
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif / cif.shift(1) - 1
        factor = ts_mean(ifreturn, 200)

        factor = factor * df['weight' + suffix]
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 40)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        return factor
##########
from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            if isinstance(sig, pd.DataFrame):
                sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, pd.Series):
                sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
                sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                    index=sig.index, name=sig.name)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            return 2 * signal - 1    
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            return signal

class tr1_zf(FactorGenerator):
    def __init__(self):
        required_columns = ['high_spot','low_spot','close_spot']
        super(tr1_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        hh = data['high_spot'].rolling(242,min_periods=30).max()
        ll = data['low_spot'].rolling(242,min_periods=30).min()
        sig = 2*data['close_spot']/(hh+ll)
        sig = rolling_norm(sig,242)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)



        
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 13:13:40 2020

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class BS_Main_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_500', 'weight_500', 'BuyUniqueOrderNum_500', 'BuyTradeNum_500', 'SellUniqueOrderNum_500', 'SellTradeNum_500']
        super(BS_Main_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
        df_s = data['amount_500'].rolling(10, min_periods = 5).sum()
        df_s = df_s[data['weight_500']>0]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)

        factor = (data['BuyUniqueOrderNum_500'] / data['BuyTradeNum_500']) - (data['SellUniqueOrderNum_500'] / data['SellTradeNum_500'])
        factor = (factor[bool_df]).mean(axis = 1)
        factor = factor.rolling(6, min_periods = 3).mean()
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]

        return -factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_sma(df1, alpha):
    # 移动平均 Y_0 = A_0, Y_i = alpha*A_i + (1-alpha)*Y_(i-1)
    output = df1.ewm(alpha=alpha, adjust=False).mean()
    return output


def ts_max(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_max(df1, window=d, min_count=int(d/2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_max(df1, window=d, min_count=int(d/2), axis=0),
                      index=df1.index, name=df1.name)
    return output


def ts_min(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_min(df1, window=d, min_count=int(d/2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_min(df1, window=d, min_count=int(d/2), axis=0),
                      index=df1.index, name=df1.name)
    return output


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d/2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_mean(df1, window=d, min_count=int(d/2), axis=0),
                      index=df1.index, name=df1.name)
    return output


class wsc8_future(FactorGenerator):
    def __init__(self):
        super(wsc8_future, self).__init__(required_columns=['close', 'high', 'low', 'recent_month_mask'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        mask = data['recent_month_mask']
        close = data['close']
        high = data['high']
        low = data['low']
        n = 30
        m = 75
        n3 = 210
        low_n = ts_min(low, n)
        high_n = ts_max(high, n)
        a = high_n - low_n
        a[abs(a)<1e-8] = np.nan
        b = (close- low_n) / (high_n - low_n)
        b_low = ts_min(b, m)
        b_high = ts_max(b, m)
        c = b_high - b_low
        c[abs(c)<1e-8] = np.nan
        d = (b - b_low) / c
        e = ts_sma(d, 2/3)
        factor = ts_sma(e, 2/3)
        factor = ts_mean(factor, n3)
        factor = ts_rank(factor, 1200)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        #factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts40_future(FactorGenerator):
    def __init__(self):

        required_columns=['close','vwap', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts40_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        high = df['vwap']
        close = delay(df['close'], 20)
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        aa = high.rolling(20, min_periods=10).cov(close) / (s * f)


        factor = ((((ts_sum(df['close'], 20) / 20) - df['close'])) + aa)
        factor = ts_rank_positive(factor, 20)
        factor = mean(factor, 100)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc7_cfg_ar(FactorGeneratorComplex):
    def __init__(self):
        super(wsc7_cfg_ar, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'high_zz500', 'low_zz500', 'weight_boolean_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        weight_true = data['weight_boolean_zz500']
        amount_mask = data['amount_zz500'][weight_true]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # KDJD技术指标，先用stochastics指标衡量收盘价位于最近n分钟的最低价和最高价之间的位置，在以此为基础，计算该指标位于最近m分钟的最大值和最小值之间的位置，作为factor_init。
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        n = 20
        m = 60
        low_n = ts_min(stk_low, n)
        high_n = ts_max(stk_high, n)
        a = high_n - low_n
        a[abs(a)<1e-8] = np.nan
        stochastics = (stk_close- low_n) / a
        stochastics_low = ts_min(stochastics, m)
        stochastics_high = ts_max(stochastics, m)
        c = stochastics_high - stochastics_low
        c[abs(c)<1e-8] = np.nan
        stochastics_double = (stochastics - stochastics_low) / c
        factor_init = stochastics_double

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 30)
        factor = ts_rank(factor_mean, 1800)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 14:40:35 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class Absvc_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'volume', 'recent_month_mask']
        super(Absvc_CC, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        temp1 = data['close'].diff()
        temp2 = np.abs(data['volume'] * temp1)
        hdl_ind_r = temp2.rolling(20, min_periods = 10).mean()
        factor = (hdl_ind_r[data['recent_month_mask']]).mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_if_2hour_return_nr_as_cfg(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_if_2hour_return_nr_as_cfg, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        cif = df['close' + suffix]
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif / cif.shift(1) - 1
        factor = ts_mean(ifreturn, 200)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 40)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 15:07:08 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class LCCorr_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot']

        super(LCCorr_ind_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):
        high = data['low_spot']
        close = data['close_spot']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_chgpcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        factor = t_chgpcor2.to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from joblib import Parallel, delayed


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    # 这是后面算子计算的辅助函数
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table

    
def get_top_mean(df1, d):
    output = pd.Series(np.nan, index=df1.index)
    a = rolling_window(df1, d)
    b = np.sort(a)
    c = np.nanmean(b[:,-5:], axis=1)
    flag = np.sum(np.isnan(a), axis=1) 
    flag = np.where(flag <= d - int(d / 2), 1, np.nan)
    output.iloc[d - 1:] = c * flag
    return output


def multi_processing(df, func, n_jobs, **kwargs):
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T


class stk2idx_maxret_diff_chg_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_maxret_diff_chg_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                          lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']
        stk_ret = stk_close / stk_close.shift(1) - 1

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        ret_win = 60
        stk_max_ret = multi_processing(df=stk_ret, func=get_top_mean, n_jobs=20, d=ret_win)

        # common code for maxret_diff
        ret_win_short = 5
        stk_ret_duration = stk_close/stk_close.shift(ret_win_short) - 1 
        stk_maxret_diff = stk_max_ret - (stk_ret_duration/ret_win_short)
        stk_maxret_diff[~np.isfinite(stk_maxret_diff)] = np.nan
        stk_maxret_diff = stk_maxret_diff[bool_mask]
        stk2idx_maxret_diff_raw = stk_maxret_diff.mean(axis=1)

        # factor logic
        short_win = 10
        long_win = 30
        ts_pct_win = 1200
        min_pct = 0.9
        stk2idx_maxret_diff_chg = calc_change_helper(stk2idx_maxret_diff_raw,short_win,long_win,ts_pct_win)        
        # ts_factor_quick(stk2idx_maxret_diff_chg,price,factor_name,layers=5)

        factor = stk2idx_maxret_diff_chg.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc11_cfg_search_wr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc11_cfg_search_wr, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                                  lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_zz500']
        stk_weight_rank = 2 * stk_weight.rank(axis=1, pct=True) - 1

        # 算子搜索
        stk_close = data['close_zz500']
        stk_close_delta = ts_delta(stk_close, 15)
        factor_init = ts_max(stk_close_delta, 20)

        factor_raw = (factor_init * stk_weight_rank).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
# from help_functions_wsc import replace_zero


    
class wsc_hf19(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf19, self).__init__(required_columns=['PxStd_500', 'VolStd_500', 'amount_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 股票1分钟内价格波动和成交量波动的相关性，这个因子的逻辑暂时还想不清楚，只得到结论是价格和交易量不同时高波动时看涨
        # 引入amount时因为原因子表现不够强
        # rolling15分钟是因为原因子在持仓时间变长后迅速失效
        amount_500 = hf_data['amount_500']
        data1 = ts_mean(hf_data['PxStd_500'], 15).corrwith(ts_mean(hf_data['VolStd_500'], 15), axis=1)
        factor_raw = data1 * ts_mean(amount_500.sum(axis=1), 15)
        factor_mean = -ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from utils_zsj import *


def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

class u2d_vol_ratio_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(u2d_vol_ratio_zsj, self).__init__(factor_name = 'u2d_vol_ratio_zsj',
                                              required_columns = ['close_zz500','volume_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_volume = data['volume_zz500']
        factor_name = 'u2d_vol_ratio'
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        up_mask = stk_ret > 0
        down_mask = stk_ret < 0

        up_vol = stk_volume[up_mask].sum(axis=1)
        down_vol = stk_volume[down_mask].sum(axis=1)
        down_vol[abs(down_vol)<1e-8] = np.nan
        u2d_vol_ratio_raw = up_vol / down_vol
        u2d_vol_ratio_raw = u2d_vol_ratio_raw.rolling(90,min_periods=30).mean()
        u2d_vol_ratio = rolling_normalize(u2d_vol_ratio_raw,window=242*3)
        ##### format factor #####
        factor = pd.DataFrame(u2d_vol_ratio,columns=[self.__class__.__name__])
        return factor



##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc2_spot(FactorGenerator):
    def __init__(self):
        super(wsc2_spot, self).__init__(required_columns=['close_spot'],
                                         lookback_bars=2000)

    def on_bar(self, data):
        # 计算长周期和短周期两条均线，作差表示这两条均线包围的面积
        # abs(factor - factor.rolling(600, min_periods=300).median())是因为在这之前的因子分组表现两头好中间差
        close = data['close_spot']
        close_ma_long = close.rolling(85, min_periods=30).mean()
        close_ma_short = close.rolling(10, min_periods=5).mean()
        factor = close_ma_short - close_ma_long

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 380)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        factor[factor<0] = 0
        # factor[factor>=0.5] = np.nan
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts5_future(FactorGenerator):
    def __init__(self):
        required_columns=['volume','high','close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts5_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        N = 45
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close'], N) / N), N) / delay(df['close'], N))<=0.05,(-1 * (df['close'] - ts_min(df['close'], N))),(-1 * delta(df['close'], 3))),index=df['close'].index,columns=df['close'].columns)
        factor = mean(ts_rank_positive(-1*factor, 1200),15)

        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.75] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 18:08:58 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class ZHZH_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot']

        super(ZHZH_ind_CC, self).__init__(
                                  required_columns=required_columns)

    
    def on_bar(self, data):

        temp = (data['high_spot']>=(data['high_spot'].rolling(15, min_periods = 5).max())).astype(int).rolling(60, min_periods = 5).mean()
        factor = ts_rank(temp.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 01:04:16 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

# 多头因子
class hhll_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns =['high_zz500', 'low_zz500', 'amount_zz500', 'weight_boolean_zz500']
        
        super(hhll_CFG_CC, self).__init__(
                                  required_columns=required_columns)

    
 
    
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        d1 = data['high_zz500']>data['high_zz500'].shift(1)
        d2 = data['low_zz500']>data['low_zz500'].shift(1)
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4

        vwtc_r = d_f.rolling(25, min_periods =15).mean()
        factor = (vwtc_r[stk_amount]).mean(axis = 1)
        #factor.index = data.index
        
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]
        return factor
##########
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import multi_processing_joblib
from operators_wsc import *


class wsc_cfg9(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg9, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'high_zz500', 'low_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # er技术指标。用来衡量市场的多空力量对比。
        # 在多头市场，人们会更贪婪地在接近高价的地方买入，BullPower越高则当前多头力量越强；而在空头市场，人们可能因为恐惧而在接近低价的地方卖出，BearPower越低则当前空头力量越强。
        # 当两者都大于0时，反映当前多头力量占据主导地位；两者都小于0则反映空头力量占据主导地位。
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_weight = data['weight_zz500']
        N = 30
        bull_power = stk_high - multi_processing_joblib(stk_close, ts_truncated_ema, n_jobs=-1, d=60, alpha=(N-1)/(N+1))
        bear_power = stk_low - multi_processing_joblib(stk_close, ts_truncated_ema, n_jobs=-1, d=60, alpha=(N-1)/(N+1))
        factor_init = bull_power + bear_power
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor = -ts_mean(factor_raw, 65)

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 300*4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        #factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc12_cfg_vs(FactorGeneratorComplex):
    def __init__(self):
        super(wsc12_cfg_vs, self).__init__(required_columns=['close_zz500', 'high_zz500', 'low_zz500', 'open_zz500', 'stk_volatility_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']

        # 东方金工20200421，通过股价在回滚区间内的位置衡量股票日内买卖压力
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        stk_price = (stk_high + stk_low + stk_open + stk_close) / 4
        n = 30
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        temp = high_n - low_n
        temp[abs(temp)<1e-8] = np.nan
        arpp = (rpp - low_n) / temp
        factor_init = -arpp
        
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 35)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        factor[factor>0] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 10:38:48 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class VLSM_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'weight_zz500', 'open_zz500', 'high_zz500', 'low_zz500', 'weight_boolean_zz500']
        
        super(VLSM_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    

    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        temp1 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['open_zz500'], data['close_zz500']))
        temp2 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['close_zz500'], data['open_zz500']))
        temp1.index = data['open_zz500'].index
        temp2.index = data['open_zz500'].index
        temp1.columns = data['open_zz500'].columns
        temp2.columns = data['open_zz500'].columns
        b = (data['high_zz500'] - temp1).rolling(40, min_periods = 15).mean()
        b[abs(b)<1e-8] = np.nan
        t_pcor = (data['high_zz500']-temp1)/b
        a = (data['high_zz500'].rolling(40, min_periods = 15).max()-data['low_zz500'].rolling(40, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (data['close_zz500']-data['low_zz500'].rolling(40, min_periods = 15).min())/a
        t_pcorr = (t_pcor2 - t_pcor).rolling(40, min_periods = 20).mean()
        factor = (t_pcorr[bool_df]).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<=-0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg3(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg3, self).__init__(required_columns=['close_zz500', 'close_spot', 'weight_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股数量
        index_return = data['close_spot'].pct_change(periods=60, fill_method=None)
        stock_return = data['close_zz500'].pct_change(periods=60, fill_method=None)
        excess_return = (stock_return.subtract(index_return, axis=0))  # .skew(axis=1)
        excess_return_weight = data['weight_zz500'][excess_return < 0].sum(axis=1)
        excess_return_weight = excess_return_weight.rolling(10, min_periods=5).mean()

        factor = excess_return_weight.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 1200)
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_ti19_spot(FactorGenerator):
    def __init__(self):
        super(wsc_ti19_spot, self).__init__(required_columns=['close_spot'],
                                            lookback_bars=2000)

    def on_bar(self, data_dict):
        # 由VIDYA指标改造而来
        # VIDYA指标也属于均线的一种，但是在权重中加入了ER指标
        # 当前趋势较强时，ER指标值较大，VIDYA会赋予当前价格更大的权重，使其紧随价格变动，减少其滞后性
        # 当前趋势较弱时（如震荡市），VIDYA会赋予当前价格较小的权重，增加其滞后性，使其更加平滑，避免产生更多的交易信号
        # 因子值为close-VIDYA，化简后为(1-vi)(close_t-close_(t-1))，属于动量指标
        index_close = data_dict['close_spot']
        n = 10
        temp = ts_sum(abs(ts_delta(index_close, 1)), n)
        temp[abs(temp)<1e-8] = np.nan
        vi = abs(ts_delta(index_close, n)) / temp
        vidya = vi * index_close + (1-vi) * ts_delay(index_close, 1)
        factor_raw = index_close - vidya
        factor_mean = ts_mean(factor_raw, 180)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 08:55:09 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HDL_CC(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'recent_month_mask']
        super(HDL_CC, self).__init__(required_columns=required_columns)
        
    
    def on_bar(self, data):

        hdl_r = (data['high'].rolling(25, min_periods = 10).max())/(data['low'].rolling(25, min_periods = 10).min())
        factor = ((hdl_r.rolling(10, min_periods = 2).mean())[data['recent_month_mask']]).mean(axis =1).to_frame()
        factor.columns = [self.__class__.__name__]
        factors = ts_rank(factor)
        factors[factors<=-0.5] = 0
        return factors
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_future_ws(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'close' + suffix,'weight' + suffix]
        lookback_bars=2000
        super(wyc_ts44_future_ws, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        temp1 = df['volume' + suffix].copy(deep = True)
        con2 = df['close' + suffix] < delay(df['close' + suffix],1)
        temp1[con2] = -1 * df['volume' + suffix]
        factor = ts_sum(temp1, 20)
        factor = ts_mean(factor, 20)

        factor = factor * df['weight' + suffix]
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts108_future(FactorGenerator):
    def __init__(self):
        required_columns=['close_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts108_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        key = 'close_if'
        factor = pd.DataFrame(np.where(df[key] - delay(df[key], 1) < 0, abs(df[key] - delay(df[key], 1)), 0),
                              index=df[key].index, columns=df[key].columns)
        factor = ts_sum(factor, 12)
        factor = ts_rank(factor, 20)
        factor = mean(factor, 80)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()
        factor.columns = [columnname]

        factor[factor <= -0.5] = 0
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts1_spot_ar(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix, 'close' + suffix,'amount' + suffix, 'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts1_spot_ar, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        close = df['close' + suffix]
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = high / high.shift(60) - 1
        h_c = close / high - 1
        a = ts_mean(h_c, 60)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, 10)
        factor = ts_mean(factor, 10) * -1

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        ar = (2 * a.rank(axis=1, pct=True) - 1)
        factor = factor * ar
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 200)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0.5] = 0


        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 14:23:45 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class VwLs_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'volume_zz500', 'weight_boolean_zz500']
        
        super(VwLs_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    

    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        #bool_df = 2 * stk_weight.rank(axis=1, pct=True) - 1
        vwap = data['amount_zz500']/data['volume_zz500']
        price_diff_1 = vwap/vwap.shift(1)-1
        price_diff_30 = vwap/vwap.shift(90)-1
        copcor1_r = -(price_diff_1-price_diff_30).rolling(5, min_periods = 1).mean()       
        factor = (bool_df*copcor1_r).mean(axis = 1).to_frame()
        #factor = factor.rolling(10, min_periods = 1).mean()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]

        #factor[factor<=-0.5] = 0
        factor = ts_rank(factor)
        #factor = factor.rolling(3, min_periods = 2).mean()
        factor[factor<=-0.5]=0
        return factor



##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_ti4_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti4_cfg, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data_dict):
        # Arms技术指标，用来显示成交额是否跟随价格上涨或者价格下跌
        weight_mask = data_dict['weight_boolean_zz500']
        stk_close = data_dict['close_zz500']
        stk_amount = data_dict['amount_zz500']
        price_diff = ts_delta(stk_close, 1)
        up_num = ((price_diff[weight_mask]) >= 0).sum(axis=1)
        down_num = ((price_diff[weight_mask]) < 0).sum(axis=1)
        up_amount = stk_amount[price_diff>=0][weight_mask].sum(axis=1)
        down_amount = stk_amount[price_diff<0][weight_mask].sum(axis=1)
        factor_raw = (up_num / down_num) / (up_amount / down_amount)
        factor_mean = -ts_mean(factor_raw, 35)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_hf9(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf9, self).__init__(required_columns=['Bid1AmtMean_500', 'Ask1AmtMean_500', 'close_500', 'weight_500'],
                                      lookback_bars=2000)

    def on_bar(self, hf_data):
        # factor logic：过去20分钟的收益率和买一挂单额＞卖一挂单额是两个动量指标，将它们叠加
        close_500 = hf_data['close_500']
        weight_500 = hf_data['weight_500']
        stk_ret = ts_pct_change(close_500, 20)
        stk_ret = stk_ret.replace([-np.inf, np.inf], np.nan)
        flag1 = hf_data['Bid1AmtMean_500'] >= hf_data['Ask1AmtMean_500']
        flag2 = stk_ret >= 0
        factor_raw = (ts_sum(flag1*flag2, 10)*weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 9)
        factor = ts_rank(factor_mean, 500)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_sma(df1, alpha):
    # 移动平均 Y_0 = A_0, Y_i = alpha*A_i + (1-alpha)*Y_(i-1)
    output = df1.ewm(alpha=alpha, adjust=False).mean()
    return output
    

class wsc5_spot(FactorGenerator):
    def __init__(self):
        super(wsc5_spot, self).__init__(required_columns=['close_spot', 'high_spot', 'low_spot'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        # factor logic
        close = data['close_spot']
        high = data['high_spot']
        low = data['low_spot']
        N = 30
        bull_power = high - ts_sma(close, alpha=(N-1)/(N+1))
        bear_power = low - ts_sma(close, alpha=(N-1)/(N+1))
        factor = bull_power + bear_power
        # factor = rolling_norm(a, 240) + rolling_norm(b, 240)
        #factor = abs(dpo - dpo.rolling(60, min_periods=30).median())#.rolling(10).mean()
        factor = -factor.rolling(180, min_periods=60).mean()
        # factor = abs(factor - factor.rolling(500, min_periods=250).median())
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 900)
        factor[factor <= -0.5] = 0
        #factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:53:33 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *



class CFG23_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']

        super(CFG23_CC, self).__init__(required_columns=required_columns
                                  )
    

    def on_bar(self, data):
        index_close = data['close_spot']
        stk_close = data['close_zz500']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        x = np.array(range(len(data['close_zz500'])))
        holder = {}
        for item in data['close_zz500'].columns:
            close_spot = data['close_zz500'][item].values
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 60))
        temp1 = pd.DataFrame(holder)
        temp1.index = data['close_zz500'].index
        temp1.columns = data['close_zz500'].columns
        temp = (temp1[bool_df]).mean(axis = 1)
        factor = rolling_norm(temp.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<=0] = 0
        factor[factor>1] = np.nan
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 10:22:33 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class CFG1_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'weight_zz500', 'weight_boolean_zz500']

        super(CFG1_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        df_s = df['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[df['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        hclose = df['close_zz500']
        weight = df['weight_zz500']
        hret = (hclose/hclose.shift(1)-1)
        temp_weighted = hret*weight*bool_df
        a = (temp_weighted[df['weight_boolean_zz500']].mean(axis = 1))
        a = a.to_frame()
        a.index.name = 'dt'
        a1 = a.rolling(35, min_periods = 15).mean()
        a2 = rolling_norm(a1, method = 'ts_rank')
        #a2.iloc[:, 0] = a2.iloc[:, 0].rolling(3, min_periods = 2).mean()
        a2.columns = [columnname]
        #a2[a2<=-0.5] = np.nan
        #a2 = ts_rank(a2)
        return a2

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:08:06 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class HL123_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'high_zz500', 'amount_zz500', 'weight_boolean_zz500']

        super(HL123_CFG2_CC, self).__init__(required_columns=required_columns)
    

    def normalization(self, signal, holding_window = 1200, ep_range = 3): 
        # Get rid of extreme values using 
        signal_mean = signal.rolling(holding_window,min_periods=int(holding_window/2)).mean() 
        signal_std = signal.rolling(holding_window,min_periods=int(holding_window/2)).std() 
        upper_bound = signal_mean + ep_range*signal_std
        lower_bound = signal_mean - ep_range*signal_std
        signal[signal>upper_bound] = upper_bound
        signal[signal<lower_bound] = lower_bound
        # Rolling Normalize
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        # In Case the input signal is not a DataFrame
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        # In case max_s = min_s
        signal[signal>1] = np.nan
        signal[signal<-1] = np.nan
        return aa

    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_zz500']
        hhigh = df['high_zz500']
        df_s = df['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[df['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12).rolling(15, min_periods = 2).mean()
        i2 = ts_rank((i2[bool_df]).mean(axis = 1).to_frame())
        #i2 = rolling_norm(i2)
        #i2[i2>1] = np.nan
        i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2
##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts102_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot_if', 'volume_spot_if']
        lookback_bars=2000
        super(wyc_ts102_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        factor = ts_mean(ts_mean((sign(delta(df['volume_spot_if'], 5)) * (-1 * delta(df['close_spot_if'], 5))), 2), 10)

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 18:26:51 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class L123_CC(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'recent_month_mask']

        super(L123_CC, self).__init__(required_columns=required_columns)

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(30, min_periods = 2).mean()
        i2 = (i2[df['recent_month_mask']]).mean(axis = 1)
        i2 = ts_rank(i2.to_frame())

        i2[i2<=0] = 0
        i2.columns = [columnname]    
        return i2
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from utils_zsj import *

class ret_a2p_sharpe_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(ret_a2p_sharpe_zsj, self).__init__(factor_name = 'ret_a2p_sharpe_zsj',
                                              required_columns = ['close_zz500','amount_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 3000)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][bool_mask]
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        ma_win = 30
        ts_pct_win = 2400
        roll_win = 10
        min_win = int(roll_win * 0.5)
        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0
        ret_active_raw = stk_ret[active_mask].mean(axis=1)
        ret_inactive_raw = stk_ret[inactive_mask].mean(axis=1)
        
        a = ret_active_raw.rolling(roll_win,min_win).std()
        a[abs(a)<1e-8] = np.nan
        b = ret_inactive_raw.rolling(roll_win, min_win).std()
        b[abs(b) < 1e-8] = np.nan
        ret_active_sharpe_raw = ret_active_raw.rolling(roll_win, min_win).mean() / a
        ret_inactive_sharpe_raw = ret_inactive_raw.rolling(roll_win, min_win).mean() / b
        ret_a2p_sharpe_raw = ret_active_sharpe_raw - ret_inactive_sharpe_raw
        ret_a2p_sharpe = calc_ma_helper(ret_a2p_sharpe_raw, ma_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(ret_a2p_sharpe,columns=[self.__class__.__name__])
        return factor



##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:33:38 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class LminLmean_IFIC_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low_if', 'recent_month_mask']
        super(LminLmean_IFIC_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        ctl_r = -data['low_if'].rolling(60, min_periods =15).min()/data['low_if'].rolling(30, min_periods =10).mean()
        factor = (ctl_r[data['recent_month_mask']]).mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 242*3)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:09:56 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class HLTM_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'high_spot', 'low_spot']

        super(HLTM_ind_CC, self).__init__(
                                  required_columns=required_columns)
    def on_bar(self, data):

        temp1 = data['high_spot'].rolling(15, min_periods = 7).max()-data['close_spot']
        temp2 = data['close_spot']-data['low_spot'].rolling(15, min_periods = 7).min()
        temp = pd.Series(np.where(temp1>temp2, temp1, temp2))
        temp.index = temp1.index
        vwtc_r = (temp).rolling(30, min_periods = 15).mean()      
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242*4)
        factor = ts_rank(factor)
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts414_cr_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','stk_index_corr_zz500']
        lookback_bars=2000
        super(wyc_ts414_cr_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = pd.DataFrame(np.where(df['close' + suffix] > delay(df['close' + suffix], 2), std(df['close' + suffix], 50), 0),
                      index=df['close' + suffix].index, columns=df['close' + suffix].columns)

        factor = ts_mean(factor, 30)
        factor = factor*(2 * df['stk_index_corr_zz500'].rank(axis = 1, pct=True) - 1)
        factor = factor.sum(axis=1).to_frame()

        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 5 * 242)    

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:00:17 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class SmaxSmean_CC(FactorGenerator):
    def __init__(self):
        required_columns =['share', 'recent_month_mask']
        super(SmaxSmean_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        pd1_r = data['share'].rolling(30, min_periods = 5).mean() - data['share'].rolling(120, min_periods = 75).mean()
        factor = (pd1_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<=-0.5] = 0
        return factor



##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 17:46:55 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

# demo
class GA_ind_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'low_spot_if', 'open_spot_if', 'high_spot_if']

        super(GA_ind_IFIC_CC, self).__init__(
                                  required_columns=required_columns)
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        n = 120
        a = data['high_spot_if'].rolling(n, min_periods = int(n/2)).max()-data['open_spot_if'].shift(n)
        b = data['close_spot_if'] - data['low_spot_if'].rolling(n, min_periods = int(n/2)).min()
        c = (data['high_spot_if'].rolling(n, min_periods = int(n/2)).max()-data['low_spot_if'].rolling(n, min_periods = int(n/2)).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a*b)/c
        factor = vwtc_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<=-0.5] = 0
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_bigon_cfghf(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['BuyUniqueOrderNum_500','BuyTradeNum_500']
        lookback_bars=2000
        super(wyc_bigon_cfghf, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        btn = df['BuyTradeNum_500'].copy()
        btn[abs(btn) < 1e-8] = np.nan
        factor = 1 - df['BuyUniqueOrderNum_500'] / btn

        factor = factor.sum(axis=1).to_frame()
        factor = ts_mean(factor, 14)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *


class wsc_hf1(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf1, self).__init__(required_columns=['BuyTradeNum_500', 'BuyUniqueOrderNum_500', 'weight_500'],
                                      lookback_bars=2000)

    def on_bar(self, data):
        # 主买独立成交订单数/主买成交订单数，比值越小，说明一笔单子拆分的越细，也就是说拆分前的单子（即独立订单数）金额越大，而大单的涌入一般会出现领涨现象
        temp = data['BuyTradeNum_500'].copy()
        temp[abs(temp)<1e-8] = np.nan
        factor_raw = (data['BuyUniqueOrderNum_500'] / temp * data['weight_500']).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        factor = -ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 19:16:39 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class ClMaxClMin_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_if', 'recent_month_mask']
 
        super(ClMaxClMin_IFIC_CC, self).__init__(
                                  required_columns=required_columns)

    
    def on_bar(self, data):

        m_vwap_ind_r = (data['close_if']).rolling(30, min_periods = 15).max()/data['close_if'].rolling(30, min_periods = 15).min()
        factor = m_vwap_ind_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242*3, method = 'ts_rank')

        
        return factor



##########
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from help_functions_wsc import *



class wsc_mean_plus_std(FactorGenerator):
    def __init__(self):
        super(wsc_mean_plus_std, self).__init__(required_columns=['close_spot'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        # 过去5分钟收益率的(均值+标准差*2)
        a = data['close_spot'].pct_change(5)
        b = a.rolling(30, min_periods=15).mean()
        c = a.rolling(30, min_periods=15).std()
        factor = b + 2 * c
        factor = factor.rolling(10).mean()
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600)
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:28:04 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class SYXWR_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot', 'open_spot', 'high_spot']

        super(SYXWR_ind_CC, self).__init__(
                                  required_columns=required_columns)

    


    def on_bar(self, data):

        temp1 = pd.Series(np.where(data['open_spot']>data['close_spot'], data['open_spot'], data['close_spot']))
        temp2 = pd.Series(np.where(data['open_spot']>data['close_spot'], data['close_spot'], data['open_spot']))
        temp1.index = data['open_spot'].index
        temp2.index = data['open_spot'].index
        b = (data['high_spot'] - temp1).rolling(30, min_periods = 15).mean()
        b[abs(b)<1e-8] = np.nan
        t_pcor = (data['high_spot']-temp1)/b
        a = (data['high_spot'].rolling(30, min_periods = 15).max()-data['low_spot'].rolling(30, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (data['close_spot']-data['low_spot'].rolling(30, min_periods = 15).min())/a
        t_pcorr = (t_pcor2 - t_pcor).rolling(90, min_periods = 20).mean()
        factor = t_pcorr.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor


##########
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:47:24 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *



class CFG23_2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'weight_boolean_zz500']

        super(CFG23_2_CC, self).__init__(required_columns=required_columns
                                  )    
            
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        x = np.array(range(len(data['amount_zz500'])))
        holder = {}
        for item in data['close_zz500'].columns:
            close_spot = data['close_zz500'][item].values
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 45))
        temp1 = pd.DataFrame(holder)
        temp1.index = data['close_zz500'].index
        temp = (temp1[bool_df]).mean(axis = 1)
        factor = rolling_norm(temp.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<=-0.5] = 0
        factor[factor>1] = np.nan
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 14:21:01 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class LCCorr_ind_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'low_spot_if']

        super(LCCorr_ind_IFIC_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):
        high = data['low_spot_if']
        close = data['close_spot_if']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_chgpcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        factor = t_chgpcor2.to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor


##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts208_future(FactorGenerator):
    def __init__(self):
        required_columns=['close_ih', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts208_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        key = 'close_ih'
        factor = pd.DataFrame(np.where(df[key] - delay(df[key], 1) < 0, abs(df[key] - delay(df[key], 1)), 0),
                              index=df[key].index, columns=df[key].columns)
        factor = ts_sum(factor, 12)
        factor = ts_rank(factor, 20)
        factor = ts_mean(factor, 100)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()
        factor.columns = [columnname]

        factor[factor <= -0.5] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:55:42 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

def normalization(signal, holding_window = 1200): 
    max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
    min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
    a = (signal - min_s)/(max_s-min_s)
    a = 2*a-1
    aa = pd.DataFrame(a)
    aa.index = signal.index
    aa.columns = signal.columns
    return aa

class VwRetSk_CC(FactorGenerator):
    def __init__(self):
        
        required_columns =['vwap', 'recent_month_mask']

        super(VwRetSk_CC, self).__init__(
                                  required_columns=required_columns
                                  )
    def on_bar(self, data):

        vsk_r = -data['vwap'].diff().rolling(30, min_periods = 15).skew()       
        factor = (vsk_r[data['recent_month_mask']]).mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = normalization(factor)
        factor[factor<=-0.5] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 13:49:19 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *



class CFG7_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_zz500', 'close_zz500', 'open_zz500', 'weight_boolean_zz500']

        super(CFG7_CC, self).__init__(required_columns=required_columns
                                  )
    

    def on_bar(self, df):
        columnname = self.__class__.__name__
        to = df['turnover_zz500']
        hclose = df['close_zz500']
        
        hopen = df['open_zz500']
        ret = hclose/hopen -1
        hret = hclose/hclose.shift(1) -1
        cc1 = ((to[hclose<hopen]/abs(ret[hclose<hopen])))
        ccc1 = cc1.rolling(60, min_periods = 7).mean()
        ccc1 = ccc1[df['weight_boolean_zz500']]
        hret = hret[df['weight_boolean_zz500']]
        cc2 = to_ts(ccc1, hret)
        ccc2 = cc2.rolling(60, min_periods = 15).mean()
        cc3 = rolling_norm(ccc2.to_frame(), method = 'ts_rank')
        #cc3 = cc3.rolling(3, min_periods = 2).mean()
        cc3[cc3<=-1] = np.nan
        cc3[cc3>1] = np.nan
        cc3.columns = [columnname]
        return cc3

##########
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg7(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg7, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # 长短期收益率之差
        stk_close = data['close_zz500']
        stk_ret_short = stk_close.pct_change(15, fill_method=None)
        stk_ret_long = stk_close.pct_change(120, fill_method=None) 
        a = stk_ret_long - stk_ret_short
        a[a<0] = 0
        #a[a>0] = 1
        factor = (a * data['weight_zz500']).sum(axis=1)
        #factor = factor.rolling(5, min_periods=2).mean()

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 500)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:07:05 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HHLS_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot']

        super(HHLS_ind_CC, self).__init__(required_columns=required_columns)

    
    def on_bar(self, data):

        temp = data['high_spot'].rolling(50, min_periods = 15).max() - data['high_spot'].shift(50).rolling(50, min_periods = 7).max()
        factor = temp.to_frame()
        factor = rolling_norm(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts14_future_cr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix, 'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts14_future_cr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        suffix = '_zz500'
        key = 'close' + suffix
        factor = pd.DataFrame(np.where(df[key] > delay(df[key], 2), std(df[key], 50), 0),
                              index=df[key].index, columns=df[key].columns)
        factor = ts_mean(factor, 30)

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_delay(df1, d):
    # A_(i-d)
    output = df1.shift(periods=d)
    return output


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output
    

class wsc4_future(FactorGenerator):
    def __init__(self):
        super(wsc4_future, self).__init__(required_columns=['close', 'recent_month_mask'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        # dpo技术指标
        mask = data['recent_month_mask']
        close = data['close']
        N = 20
        dpo = close - ts_delay(ts_mean(close, N), int(N/2+1))
        factor = abs(dpo - dpo.rolling(60, min_periods=30).median())#.rolling(10).mean()
        factor = factor.rolling(45, min_periods=30).mean()
        factor = ts_rank(factor, 600*2)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts47_future(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts47_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        con1 = df['close'] > delay(df['close'], 1)
        factor = con1.rolling(100).sum()
        factor = mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()


        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 18:29:27 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class L123_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns=['low_spot']

        super(L123_ind_CC, self).__init__(required_columns=required_columns)

        
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_spot']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(25, min_periods = 2).mean()
        i2 = ts_rank(i2.to_frame())

        i2.columns = [columnname]    
        return i2
##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts32_future(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts32_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        mask = df['recent_month_mask']
        temp = df['close'].copy()
        N = 20
        UP = temp.copy(deep = True)
        UP[df['close'] > delay(df['close'], 1)] = std(df['close'], N)
        UP[df['close'] <= delay(df['close'], 1)] = 0
        factor = sma(UP, N, 1)
        factor = ts_rank_positive(factor, 50)
        factor = mean(factor, 50)

        def rolling_normalize(df, x):
            def normalize(dd):
                a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
                b = (a - 0.5) * 2
                return b

            return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 13:29:53 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

# demo
class updown_cfg2_CC(FactorGeneratorComplex):
    def __init__(self):

        required_columns =['close_zz500', 'amount_zz500', 'weight_boolean_zz500']

        super(updown_cfg2_CC, self).__init__(
                                  required_columns=required_columns)
        
            


    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        hclose = (data['close_zz500']/data['close_zz500'].shift(1)-1)
        #upclose = ((hclose>0) * stk_amount).sum(axis = 1)
        #downclose = ((hclose<0) * stk_amount).sum(axis = 1)

        upclose = stk_amount[hclose>0].sum(axis=1)
        downclose = stk_amount[hclose<0].sum(axis=1)

        vwtc_r = ((upclose-downclose)/ (upclose+downclose)).rolling(90, min_periods = 45).mean()
        vwtc_r[abs(vwtc_r)>10000] = np.nan
        factor = vwtc_r.to_frame()
        
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts15_future_nr_as(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts15_future_nr_as, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'

        high = df['high' + suffix]
        high = multi_processing_joblib(df=high, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/11)
        a = ts_rank(high, 80)
        factor = ts_mean(a, 50)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 09:28:50 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class SYXWR_ar_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'weight_boolean_zz500', 'close_zz500', 'open_zz500', 'high_zz500', 'low_zz500']
        super(SYXWR_ar_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):

        stk_amount = (data['amount_zz500'])[data['weight_boolean_zz500']]
        stk_amount_rank = 2 * stk_amount.rank(axis=1, pct=True) - 1
        
        temp1 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['open_zz500'], data['close_zz500']))
        temp2 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['close_zz500'], data['open_zz500']))
        temp1.index = data['open_zz500'].index
        temp2.index = data['open_zz500'].index
        temp1.columns = data['open_zz500'].columns
        temp2.columns = data['open_zz500'].columns
        b = (data['high_zz500'] - temp1).rolling(30, min_periods = 15).mean()
        b[abs(b)<1e-8] = np.nan
        t_pcor = (data['high_zz500']-temp1)/b
        a = (data['high_zz500'].rolling(30, min_periods = 15).max()-data['low_zz500'].rolling(30, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (data['close_zz500']-data['low_zz500'].rolling(30, min_periods = 15).min())/a
        t_pcorr = (t_pcor2 - t_pcor)
        factor = (t_pcorr*stk_amount_rank).sum(axis = 1).to_frame()
        factor = factor.rolling(40, min_periods = 20).mean()
        factor = ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            if isinstance(sig, pd.DataFrame):
                sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, pd.Series):
                sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
                sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                    index=sig.index, name=sig.name)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            return 2 * signal - 1    
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            return signal

def ts_rank(df1, d = 1200):
    # moving time-series rank for the past d periods
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output

class tr1_cfg_zf_cr(FactorGeneratorComplex):
    def __init__(self):
        required_columns = ['close_zz500','high_zz500','low_zz500','stk_index_corr_zz500']
        super(tr1_cfg_zf_cr, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        hh = data['high_zz500'].rolling(242,min_periods=30).max()
        ll = data['low_zz500'].rolling(242,min_periods=30).min()
        fac = 2*data['close_zz500']/(hh+ll)
        facorg = rolling_norm(fac,242)
        cr = (data['stk_index_corr_zz500'].rank(axis=1,pct=True))*2-1
        fac = (facorg*cr).sum(axis=1).rolling(5,min_periods=5).mean()
        sig = ts_rank(fac,242*5)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
##########
from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk
from scipy.stats import rankdata

def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

def mean(A,d):
    output = A.rolling(d,min_periods=int(round(d/2))).mean()
    output.iloc[:d-1] = np.nan
    return output

def ts_rank(df, d=10):
    def rolling_rank(x):
        return rankdata(x)[-1]
    return df.rolling(d,min_periods=min(d//2,10)).apply(rolling_rank,raw=True)

def ts_max(A,d):
    output = A.rolling(d,min_periods=int(round(d/2))).max()
    output.iloc[:d-1] = np.nan
    return output
    
def ts_min(A,d):
    output = A.rolling(d,min_periods=int(round(d/2))).min()
    output.iloc[:d-1] = np.nan
    return output

class ts24_futures_zf(FactorGenerator):
    def __init__(self):
        required_columns = ['close','high','low', 'recent_month_mask']
        super(ts24_futures_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        mask = data['recent_month_mask']
        N = 20
        wmadf = mean(data['close'], N)
        longc = ts_max(data['high'], N) - wmadf
        shortc = ts_min(data['low'], N) - wmadf
        factor =  (longc - shortc) / data['close']
        factor = ts_rank(factor, 80)
        factor = mean(factor, 40)
        factor = rolling_normalize(factor,242*5)
        factor[factor<-0.8]=0
        factor = factor[mask].sum(axis=1)
        factor.name = self.__class__.__name__
        return pd.DataFrame(factor)
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 18:22:57 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
import numpy as np
from factor_generator import FactorGenerator
from operators_cc import *

class ZHZH_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'recent_month_mask']

        super(ZHZH_CC, self).__init__(
                                  required_columns=required_columns)

    
    
    def on_bar(self, data):

        temp = (data['high']>=(data['high'].rolling(10, min_periods = 5).max())).astype(int).rolling(90, min_periods = 5).mean()
        temp = temp[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor = ts_rank(temp)
        factor[factor<=-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts49_future(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts49_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        con1 = ((delta((ts_sum(df['close'], 100) / 100), 100) / delay(df['close'], 100)) <= 0.05)
        temp1 = df['close'].copy(deep = True)
        temp1[con1] = (df['close'] - ts_min(df['close'], 200))
        temp1[~con1] = delta(df['close'], 10)
        factor = temp1
        factor = ts_rank_positive(factor, 50)
        factor = mean(factor, 50)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()


        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 14:58:22 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class Crossing_Turns_CC(FactorGenerator):
    def __init__(self):

        required_columns =['open', 'low', 'close', 'high', 'vwap', 'recent_month_mask']

        super(Crossing_Turns_CC, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):

        temp = np.abs(pd.DataFrame(np.where(data['open']-data['close'] == 0, 0.1, data['open']-data['close'])))
        temp.index = data['open'].index
        temp.columns = data['open'].columns
        temp = (temp[data['recent_month_mask']]).mean(axis = 1)
        temp0 = ((data['high'] - data['low'])[data['recent_month_mask']]).mean(axis = 1)
        temp1 = temp0/temp
        a = (data['vwap']/data['vwap'].shift(1)-1).rolling(30, min_periods = 15).sum()
        a = (a[data['recent_month_mask']]).mean(axis = 1)
        vwtc_r = (temp1*(a)).rolling(25, min_periods = 5).mean()
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<=-0.5]=0
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
# from help_functions_wsc import replace_zero


    
class wsc_hf15(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf15, self).__init__(required_columns=['PxVolCorr_500', 'weight_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 股价价量相关性
        weight_500 = hf_data['weight_500']
        factor_raw = (hf_data['PxVolCorr_500']*weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1800)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc8_cfg_ar(FactorGeneratorComplex):
    def __init__(self):
        super(wsc8_cfg_ar, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'high_zz500', 'low_zz500', 'weight_boolean_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        weight_true = data['weight_boolean_zz500']
        amount_mask = data['amount_zz500'][weight_true]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # ddi技术指标，先以high+low作为合成价格，然后以它向上or向下作为flag，作用到一个刻画标的向上or向下波动的指标上（abs(ts_delta(high, 1))， abs(ts_delta(low, 1))），即high和low的路径
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        n = 30
        hl = stk_high + stk_low
        high_abs = abs(ts_delta(stk_high, 1))
        low_abs = abs(ts_delta(stk_low, 1))
        dmz = np.maximum(high_abs, low_abs)
        dmz[ts_delta(hl, 1)<=0] = 0
        dmf = np.maximum(high_abs, low_abs)
        dmf[ts_delta(hl, 1)>=0] = 0
        a = ts_sum(dmz, n) + ts_sum(dmf, n)
        a[abs(a)<1e-8] = np.nan
        ddi = (ts_sum(dmz, n) - ts_sum(dmf, n)) / a
        factor_init = ddi

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""

class vwap_ma_zsj(FactorGenerator):
    def __init__(self):
        super(vwap_ma_zsj, self).__init__(factor_name = 'vwap_ma_zsj',
                                          required_columns = ['close','high','low','volume', 'recent_month_mask'],
                                          lookback_bars = 1300)

    def on_bar(self, data):
        ##### def data #####
        mask = data['recent_month_mask']
        close = data['close']
        high = data['high']
        low = data['low']
        volume = data['volume']

        ##### calc factor #####
        def calc_vwap_sig(close, high, low, volume, roll_win):
            typical = (high + low + close) / 3
            mf = volume * typical
            volume_sum = SUM(volume, roll_win)
            volume_sum[abs(volume_sum)<1e-8] = np.nan
            mf_sum = SUM(mf, roll_win)
            vwap_val = mf_sum / volume_sum
            vwap_diff = close - vwap_val
            return vwap_diff

        """vwap_ma"""
        factor_name = 'vwap_ma'
        roll_win = 15
        ma_win = 60
        ts_pct_win = 1200
        score_raw = calc_vwap_sig(close, high, low, volume, roll_win)
        vwap_ma = calc_ma_helper(score_raw, ma_win, ts_pct_win)
        vwap_ma = vwap_ma[mask].sum(axis=1)

        ##### format factor #####
        vwap_ma.name = self.__class__.__name__
        factor = pd.DataFrame(vwap_ma)
        factor[factor<0]=0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:18:41 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class CloseVoltoMean_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'recent_month_mask']

        super(CloseVoltoMean_ind_CC, self).__init__(
                                  required_columns=required_columns)

    
    def on_bar(self, data):

        prstd3_r = data['close_spot'].rolling(40, min_periods =5).std()/data['close_spot'].rolling(40, min_periods =15).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')
        factor[factor<-0.2]=0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_ti1_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti1_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data_dict):
        # abi技术指标，值越大表示市场越活跃，活动和变化频繁，反之意味着市场缺乏变化
        # 是不是意味着市场越活跃的时候未来上涨的概率就越大，但是如果跌的股票远大于涨的股票，为什么未来还会上涨呢？
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        stk_ret = ts_delta(stk_close, 1)
        stk_ret[stk_ret>=0] = 1
        stk_ret[stk_ret<0] = -1
        factor_raw = abs((stk_ret*stk_weight).sum(axis=1))
        factor_mean = ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp8_future(FactorGenerator):
    def __init__(self):
        super(wsc_gp8_future, self).__init__(required_columns=['amount', 'recent_month_mask'],
                                             lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170701-20190228，验证时间段：20190301-20190630
        # 因子逻辑：由因子逻辑的Word文档可知，ts_reg_beta也是动量的一种表现方式，另一方面，由gp6可知，交易额的成交额应该是个正向因子，那逻辑就是一个正向因子叠加动量。
        future_amount = data_dict['amount']
        future_mask = data_dict['recent_month_mask']
        amount_std = ts_std(future_amount, 68)
        factor_raw = multi_processing_joblib(df=amount_std, func=ts_reg_beta, n_jobs=-1, d=37)[future_mask].sum(axis=1)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 17:09:17 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HcorrC_ind_IFIC_CC(FactorGenerator):
    def __init__(self):
        
        required_columns =['close_spot_if', 'high_spot_if']
        
        super(HcorrC_ind_IFIC_CC, self).__init__(
                                  required_columns=required_columns)


    
    def on_bar(self, data):

        high = data['high_spot_if']
        close = data['close_spot_if']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        t_pcor2[abs(t_pcor2) > 1e8] = 0
        factor = t_pcor2.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 2420)
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc14_cfg_search_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc14_cfg_search_cr, self).__init__(required_columns=['stk_index_corr_zz500', 'open_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # 算子搜索
        stk_open = data['open_zz500']
        a = ts_pct_change(stk_open, 20)
        factor_init = ts_median(a, 30)

        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=0] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc10_cfg_vs(FactorGeneratorComplex):
    def __init__(self):
        super(wsc10_cfg_vs, self).__init__(required_columns=['close_zz500', 'stk_volatility_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']

        # 计算长短期收益率之差
        stk_close = data['close_zz500']
        stk_ret_short = stk_close.pct_change(10, fill_method=None)
        stk_ret_long = stk_close.pct_change(130, fill_method=None) 
        a = stk_ret_long - stk_ret_short
        a[a<0] = 0
        factor_init = a
        
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 16:41:39 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class LminC_CFG3_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']
        super(LminC_CFG3_CC, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        cs2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        lltc_ind_r = -data['low_zz500'].rolling(180, min_periods = 90).min()/(data['close_zz500'])
        factor = (lltc_ind_r[cs2]).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        #factor[factor>1] = np.nan
        #factor[factor<-0.5] = np.nan
        #factor[factor == np.nan] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 11:00:43 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *


class CloseVoltoMean_cr_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500', 'close_spot']
        super(CloseVoltoMean_cr_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
    
        '''corr_sum'''
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]

        '''corr_rank'''
        mask = 2 * stk_index_corr.rank(axis=1, pct=True) - 1
        
        prstd3_r = data['close_zz500'].rolling(40, min_periods =5).std()/data['close_zz500'].rolling(40, min_periods =15).mean()
        factor = (prstd3_r*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(20, min_periods = 10).mean()
        factor = rolling_norm(factor, 720, method = 'ts_rank')
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:55:29 2020

@author: appadmin
"""

import pandas as pd
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class hhll_ind_CC_nr_ct_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'close_spot', 'weight_boolean_zz500', 'turnover_zz500', 'high_zz500', 'low_zz500']
        super(hhll_ind_CC_nr_ct_CFG_CC, self).__init__(required_columns=required_columns
                                  )


    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        turnover = (data['turnover_zz500'].rolling(60, min_periods = 15).mean())[data['weight_boolean_zz500']]
        temp1 = (data['high_zz500']>data['high_zz500'].shift(1)).astype(int)
        temp2 = (data['low_zz500']>data['low_zz500'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        factor = temp
        factor = rolling_norm(factor)
        #factor[abs(factor)>1] = np.nan
        tempp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        tempp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        mask = tempp2 * tempp4
        factor1 = (factor * mask).sum(axis = 1).to_frame()
        factor1 = factor1.rolling(30, min_periods = 15).mean()
        factor1 = ts_rank(factor1)
        factor1.columns = [self.__class__.__name__]
        return factor1
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from utils_zsj import *


class trade_strength_a2p_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(trade_strength_a2p_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][bool_mask]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        # factor_name = 'trade_strength_a2p'
        roll_win = 30
        ma_win = 30
        ts_pct_win = 4800
        min_pct = 0.9
        min_periods = int(min_pct * roll_win)
        abs_dis = np.abs(stk_close - stk_close.shift(1))
        stk_tot_dis = abs_dis.rolling(roll_win, min_periods).sum()
        stk_tot_dis[abs(stk_tot_dis)<1e-8] = np.nan
        stk_final_dis = stk_close - stk_close.shift(roll_win)
        stk_trade_strength = stk_final_dis / stk_tot_dis
        ts_active_raw = stk_trade_strength[active_mask].mean(axis=1)
        ts_inactive_raw = stk_trade_strength[inactive_mask].mean(axis=1)
        ts_a2p_raw = ts_active_raw - ts_inactive_raw
        trade_strength_a2p = calc_ma_helper(ts_a2p_raw, ma_win, ts_pct_win, min_pct)
        # ts_factor_quick(trade_strength_a2p, price, factor_name, layers=5)

        factor = trade_strength_a2p.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200 * 4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_ti2_spot(FactorGenerator):
    def __init__(self):
        super(wsc_ti2_spot, self).__init__(required_columns=['high_spot', 'low_spot', 'close_spot', 'amount_spot'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # adl技术指标, 用分钟内价格变化对amount进行调整，调整系数: [-1, 1]，close越接近high调整系数越大，越接近low越低
        # 原指标还要对amount_adj累加，在现有框架下，为了保证每个时间点因子值可比，用ts_sum代替累加
        # 个人理解是amount是个动量指标，(2 * index_close - index_high - index_low) / (index_high - index_low)也是个动量指标，相当于两个动量指标共同作用得到的结果
        index_high = data_dict['high_spot']
        index_low = data_dict['low_spot']
        index_close = data_dict['close_spot']
        index_amount = data_dict['amount_spot']
        x = index_high - index_low
        x[abs(x)<1e-8] = np.nan
        amount_adj = (2 * index_close - index_high - index_low) / x * index_amount
        amount_adj = ts_sum(amount_adj, 60)
        factor = ts_rank(amount_adj, 950)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts6_spot_nr_ts(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts6_spot_nr_ts, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        close = df['close' + suffix]
        gain_close_30 = ts_gain(close, 30)
        factor = ts_levelchange(gain_close_30, 20)
        factor = ts_mean(factor, 110)

        factor = rolling_norm(factor, 5 * 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        factor = factor * t
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 20)
        factor = ts_mean(factor, 200)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0.2] = 0

        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts34_future_ts_50_100(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'high' + suffix,'low' + suffix,'volume' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts34_future_ts_50_100, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        chl = df['high' + suffix]-df['low' + suffix]
        chl[abs(chl) < 1e-6] = np.nan
        factor = ((df['close' + suffix]-df['low' + suffix])-(df['high' + suffix]-df['close' + suffix]))/chl*df['volume' + suffix]
        factor = ts_mean(factor, 150)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        factor = factor * t
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 100)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk2idx_ret_range_corr_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_ret_range_corr_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'high_zz500', 'low_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']

        # factor logic
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        ma_win = 60
        ts_pct_win = 1200
        min_pct = 0.9
        stk_ret_range = stk_high/stk_low - 1
        stk_ret = stk_close/stk_close.shift(1) - 1
        ret_range_corr_raw = stk_ret[bool_mask].corrwith(stk_ret_range[bool_mask],axis=1)
        stk2idx_ret_range_corr = calc_ma_helper(ret_range_corr_raw,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_ret_range_corr.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc4_cfg_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc4_cfg_cr, self).__init__(required_columns=['close_zz500', 'close_spot', 'stk_index_corr_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # dpo技术指标，比较当前close与前一段时间的close均线
        stk_close = data['close_zz500']
        N = 20
        dpo = stk_close - ts_delay(ts_mean(stk_close, N), int(N/2+1))
        factor_init = dpo
        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.9] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts414_ws_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','weight_zz500']
        lookback_bars=2000
        super(wyc_ts414_ws_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = pd.DataFrame(np.where(df['close' + suffix] > delay(df['close' + suffix], 2), std(df['close' + suffix], 30), 0),
                              index=df['close' + suffix].index, columns=df['close' + suffix].columns)

        factor = factor * df['weight_zz500']
        factor = factor.sum(axis=1).to_frame()

        # factor = ts_rank(factor, 60)
        factor = ts_mean(factor, 30)

        factor.columns = [columnname]
        factor[columnname] = ts_rank_bk(factor, 5 * 242)

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 13:29:44 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class DJC_cv_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500', 'close_spot']
        super(DJC_cv_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    

    
    def on_bar(self, data):
        stk_close = data['close_zz500']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_zz500']]
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        
        tempp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        tempp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp5 = data['close_zz500'].rolling(5, min_periods = 2).mean()
        temp10 = data['close_zz500'].rolling(10, min_periods = 5).mean()
        temp20 = data['close_zz500'].rolling(20, min_periods = 10).mean()
        temp60 = data['close_zz500'].rolling(60, min_periods = 30).mean()
        temp120 = data['close_zz500'].rolling(120, min_periods = 60).mean()
        temp5_diff = (temp5.diff()>0).astype(int)
        temp10_diff = (temp10.diff()>0).astype(int)
        temp20_diff = (temp20.diff()>0).astype(int)
        temp60_diff = (temp60.diff()>0).astype(int)
        temp120_diff = (temp120.diff()>0).astype(int)
        temp = (temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff).rolling(20, min_periods = 15).mean()
        mask = tempp2 * tempp3
        factor = (temp*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts419_vs_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','high_zz500','low_zz500','volume_zz500','stk_volatility_zz500']
        lookback_bars=2000
        super(wyc_ts419_vs_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = ts_sum(((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / (
                    df['high' + suffix] - df['low' + suffix]) * df['volume' + suffix], 10)
        finaldf = ts_mean(factor, 30)

        factor = finaldf * df['stk_volatility_zz500']
        factor = factor.sum(axis=1).to_frame()
        factor = ts_rank(factor, 400)
        factor = ts_mean(factor, 5)

        factor.columns = [columnname]
        factor[columnname] = rolling_normalize(factor, 5 * 242)

        return factor
##########
from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk

def ts_rank(df1, d = 1200):
    # moving time-series rank for the past d periods
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output

class sr1_zf(FactorGenerator):
    def __init__(self):
        required_columns = ['close_spot','low_spot']
        super(sr1_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        rtn = data['close_spot']/data['close_spot'].shift(1)-1
        vol = rtn.rolling(60,min_periods=30).std()
        vol[abs(vol)<1e-8] = np.nan
        ret = data['close_spot']/(data['low_spot'].shift(1).rolling(60,min_periods=30).min())-1
        sig = ret/vol
        sig = ts_rank(sig, 242*2)
        sig = sig.rolling(5,min_periods=2).mean()
        sig[sig<=-0.5]=0
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc11_cfg_search_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc11_cfg_search_cr, self).__init__(required_columns=['close_zz500', 'stk_index_corr_zz500'],
                                                  lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # 算子搜索
        stk_close = data['close_zz500']
        stk_close_delta = ts_delta(stk_close, 15)
        factor_init = ts_max(stk_close_delta, 15)

        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1800)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts26_future_tr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix , 'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts26_future_tr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        N = 6
        N1 = 4
        N2 = 8
        MTM = df['close' + suffix] - delay(df['close' + suffix], 1);
        MTMMA = sma(MTM, N, 1);
        DIF = ts_mean(delay(MTMMA, 1), N1) - ts_mean(delay(MTMMA, 1), N2)
        factor = sma(DIF, 100, 1)
        factor = ts_rank_bk(factor, 242 * 2)
        factor = ts_mean(factor, 242)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 20)
        factor = ts_mean(factor, 80)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0] = 0

        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk2idx_amt_ret_corr_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_amt_ret_corr_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']
        
        # factor logic
        stk_amt_change = (stk_amt - stk_amt.shift(1))[bool_mask]
        stk_ret = (stk_close/stk_close.shift(1) - 1)[bool_mask]
        amt_ret_corr_raw = stk_amt_change.corrwith(stk_ret,axis=1)
        ma_win = 30
        ts_pct_win = 1200
        min_pct = 0.9
        stk2idx_amt_ret_corr = calc_ma_helper(amt_ret_corr_raw,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_amt_ret_corr.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc3_cfg_ar(FactorGeneratorComplex):
    def __init__(self):
        super(wsc3_cfg_ar, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'close_spot', 'weight_boolean_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        weight_true = data['weight_boolean_zz500']
        amount_mask = data['amount_zz500'][weight_true]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 比较股票和指数涨幅大小，大则置1，小则置0
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        index_return = index_close.pct_change(3, fill_method=None)
        stk_return = stk_close.pct_change(3, fill_method=None)
        return_difference = stk_return.sub(index_return, axis=0)
        return_difference[return_difference > 0] = 1
        return_difference[return_difference <= 0] = 0
        temp = ts_sum(return_difference, 90)
        temp[abs(temp)<1e-8] = np.nan
        factor_init = ts_sum(return_difference, 15) / temp
        factor_init = factor_init.replace([-np.inf, np.inf], np.nan)

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc17_cfg_ret_as(FactorGeneratorComplex):
    def __init__(self):
        super(wsc17_cfg_ret_as, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                               lookback_bars=2000)

    def on_bar(self, data):
        # 长江金工高频因子八，偏度因子
        # 计算close的偏度，偏度＞0时，大于价格均值的价格比小于价格均值的价格少，个股成交集中在价格相对较低的水平，反之亦然，因此认为偏度越小的股票未来价格更可能上升。
        # 取当分钟rolling_skew前50%的股票，计算它们的过去一分钟return，作为因子值，再套相应的mask，因为每期选出的票都不一样，所以为了时序上可比，要做一定的归一化处理。
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amount = data['amount_zz500']
        stk_ret = ts_pct_change(stk_close, 1)[bool_mask]
        stk_skew = ts_skew(stk_close, 30)[bool_mask]
        skew_long = stk_skew.gt(stk_skew.quantile(0.5, axis=1), axis=0)
        factor_init = stk_ret[skew_long]

        factor_raw = (factor_init * stk_amount).sum(axis=1) / (stk_amount * skew_long).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = rolling_norm(factor_mean, 1200)

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_future(FactorGenerator):
    def __init__(self):

        required_columns=['volume','close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts44_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        mask = df['recent_month_mask']
        temp1 = df['volume'].copy(deep = True)
        con1 = df['close']>delay(df['close'],1)
        con2 = df['close']<delay(df['close'],1)
        temp1[con2] = -1 * df['volume']
        factor = ts_sum(temp1,20)
        factor = mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()


        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<0]=0
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from help_functions_wsc import *



class wsc11_future(FactorGenerator):
    def __init__(self):
        super(wsc11_future, self).__init__(required_columns=['close', 'high', 'low', 'open', 'recent_month_mask'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # 根据asi指标改造而来
        # asi指标由si累加而来，但这样会导致每个时刻累加的起点不同，因此用si过去一段时间的移动平均代替，解决起点不同的问题
        mask = data['recent_month_mask']
        close = data['close']
        high = data['high']
        low = data['low']
        open = data['open']
        n = 20
        a = abs(high-ts_delay(close, 1))
        b = abs(low-ts_delay(close, 1))
        c = abs(high-ts_delay(low, 1))
        d = abs(ts_delay(close, 1)-ts_delay(open, 1))
        k = np.maximum(a, b)
        m = ts_max(high-low, n)
        r1 = a + 0.5*b + 0.25*d
        r2 = b + 0.5*a + 0.25*d
        r3 = c + 0.25*d
        r4 = r2.copy(deep=True)
        r4[(a>=b)&(a>=c)] = r1
        r = r4.copy(deep=True)
        r[(c>=a)&(c>=b)] = r3
        si = 50 * (ts_delta(close, 1) + ts_delay(close, 1) - ts_delay(open, 1) + 0.5*(close - open)) / r * k / m

        #asi = si.cumsum()
        #M = 20
        #asima = ts_mean(asi, M)
        #factor = ts_delta(asima, 1)
        factor = si
        factor = ts_mean(factor, 90)
        factor = ts_rank(factor, 600*2)
        factor = factor[mask].sum(axis=1)
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        #factor[factor >= 0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_delay(df1, d):
    # A_(i-d)
    output = df1.shift(periods=d)
    return output


def ts_mean(df1, d):
    # moving time-series average for the past d periods
    output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=int(d / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class wsc4_spot(FactorGenerator):
    def __init__(self):
        super(wsc4_spot, self).__init__(required_columns=['close_spot'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        close = data['close_spot']
        N = 20
        dpo = close - ts_delay(ts_mean(close.to_frame(), N), int(N/2+1)).iloc[:,0]
        # factor = rolling_norm(a, 240) + rolling_norm(b, 240)
        factor = abs(dpo - dpo.rolling(60, min_periods=30).median())#.rolling(10).mean()
        factor = factor.rolling(30, min_periods=15).mean()
        # factor = abs(factor - factor.rolling(500, min_periods=250).median())
        # print(factor)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600*2)
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 10:33:02 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class HmaxC_ind_nr_al_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'weight_boolean_zz500', 'weight_zz500', 'turnover_zz500', 'high_zz500', 'close_zz500']

        super(HmaxC_ind_nr_al_CC, self).__init__(required_columns=required_columns
                                  )
        
        
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(60, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        turnover = (data['turnover_zz500'].rolling(60, min_periods = 15).mean())[data['weight_boolean_zz500']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        bool_df = temp1&temp4
        
        hmhm_r = -data['high_zz500'].rolling(120, min_periods = 90).max()/data['close_zz500']
        hmhm_r = rolling_norm(hmhm_r, 242)
        factor = hmhm_r[bool_df].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        #factor = factor.between_time('13:00', '14:49').groupby(pd.TimeGrouper('D')).mean().dropna(how = 'all')
        factor = rolling_norm(factor, 242)
        #factor[factor<0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 01:16:25 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

# 多头因子
class hhll_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns =['high_zz500', 'low_zz500', 'close_zz500','close_spot', 'weight_boolean_zz500']
        
        super(hhll_CFG2_CC, self).__init__(
                                  required_columns=required_columns)

    
 

    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        d1 = data['high_zz500']>data['high_zz500'].shift(1)
        d2 = data['low_zz500']>data['low_zz500'].shift(1)
        d_f = (d1.astype(int)+d2.astype(int))
        d_f[d_f == 2] = 4

        vwtc_r = d_f.rolling(40, min_periods =15).mean()
        factor = (vwtc_r[bool_df]).mean(axis = 1)
        #factor.index = data.index
        
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc11_cfg_search_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc11_cfg_search_vr, self).__init__(required_columns=['close_zz500', 'stk_volatility_zz500'],
                                                  lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 算子搜索
        stk_close = data['close_zz500']
        stk_close_delta = ts_delta(stk_close, 15)
        factor_init = ts_max(stk_close_delta, 20)

        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        factor[factor>=0.5] = 0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts419_cs_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','high_zz500','low_zz500','volume_zz500','stk_index_corr_zz500']
        lookback_bars=2000
        super(wyc_ts419_cs_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = ts_sum(((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / (
                    df['high' + suffix] - df['low' + suffix]) * df['volume' + suffix], 10)
        finaldf = ts_mean(factor, 30)

        factor = finaldf * df['stk_index_corr_zz500']
        factor = factor.sum(axis=1).to_frame()
        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 5 * 242)

        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


class wsc_search1_long(FactorGenerator):
    def __init__(self):
        super(wsc_search1_long, self).__init__(required_columns=['close_spot'],
                                               lookback_bars=2000)

    def on_bar(self, data):
        # 算子搜索
        data_need = data['close_spot'].to_frame()
        factor = reg_beta(data_need, 45)
        factor = rolling_norm(factor, 600)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:12:24 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class VwapLSVol_CC(FactorGenerator):
    def __init__(self):

        required_columns =['vwap', 'recent_month_mask']

        super(VwapLSVol_CC, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        prstd_r = -data['vwap'].rolling(1200, min_periods = 600).std()/data['vwap'].rolling(45, min_periods = 15).std()
        factor = (prstd_r[data['recent_month_mask']]).mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc18_cfg_wr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc18_cfg_wr, self).__init__(required_columns=['close_zz500', 'high_zz500', 'low_zz500', 'open_zz500', 'weight_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_zz500']
        stk_weight_rank = 2 * stk_weight.rank(axis=1, pct=True) - 1

        # 根据asi指标改造而来
        # asi指标由si累加而来，但这样会导致每个时刻累加的起点不同，因此用si过去一段时间的移动平均代替，解决起点不同的问题
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        n = 45
        a = abs(stk_high-ts_delay(stk_close, 1))
        b = abs(stk_low-ts_delay(stk_close, 1))
        c = abs(stk_high-ts_delay(stk_low, 1))
        d = abs(ts_delay(stk_close, 1)-ts_delay(stk_open, 1))
        k = np.maximum(a, b)
        m = ts_max(stk_high-stk_low, n)
        r1 = a + 0.5*b + 0.25*d
        r2 = b + 0.5*a + 0.25*d
        r3 = c + 0.25*d
        r4 = r2.copy(deep=True)
        r4[(a>=b)&(a>=c)] = r1
        r = r4.copy(deep=True)
        r[(c>=a)&(c>=b)] = r3
        r[abs(r)<1e-8] = np.nan
        m[abs(m)<1e-8] = np.nan
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open)) / r * k / m
        factor_init = si

        factor_raw = (factor_init * stk_weight_rank).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 70)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        factor[factor>=0.5] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:19:00 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

# 多头因子
class cd_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['close_spot']
        
        super(cd_ind_CC, self).__init__(
                                  required_columns=required_columns)
        
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    


    def on_bar(self, data):

        temp = data['close_spot'].rolling(60, min_periods = 2).mean().diff()
        factor = temp.to_frame()
        factor.columns =  [self.__class__.__name__]
        factor = self.normalization(factor, 4800)
        factor[factor<0] = 0
        factor[factor>1] = 0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc7_cfg_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc7_cfg_cr, self).__init__(required_columns=['close_zz500', 'stk_index_corr_zz500', 'high_zz500', 'low_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # KDJD技术指标，先用stochastics指标衡量收盘价位于最近n分钟的最低价和最高价之间的位置，在以此为基础，计算该指标位于最近m分钟的最大值和最小值之间的位置，作为factor_init。
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        n = 20
        m = 60
        low_n = ts_min(stk_low, n)
        high_n = ts_max(stk_high, n)
        a = high_n - low_n
        a[abs(a)<1e-8] = np.nan
        stochastics = (stk_close- low_n) / a
        stochastics_low = ts_min(stochastics, m)
        stochastics_high = ts_max(stochastics, m)
        c = stochastics_high - stochastics_low
        c[abs(c)<1e-8] = np.nan
        stochastics_double = (stochastics - stochastics_low) / c
        factor_init = stochastics_double

        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 30)
        factor = ts_rank(factor_mean, 1800)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.8] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 19:50:40 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class L123_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'weight_boolean_zz500']

        super(L123_CFG_CC, self).__init__(required_columns=required_columns
                                  )
 
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_zz500']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(30, min_periods = 2).mean()
        i2 = (i2[df['weight_boolean_zz500']]).mean(axis = 1)
        i2 = ts_rank(i2.to_frame())
        #i2 = rolling_norm(i2)
        i2[i2>1] = np.nan
        #i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:50:31 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HLLSVol_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low', 'recent_month_mask']
 
        super(HLLSVol_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        a = (data['high']/data['low']).rolling(240, min_periods =10).std()
        a[a<1e-10] = np.nan
        ocre3_r = (data['high']/data['low']).rolling(40, min_periods =10).std()/a
        factor = ocre3_r[data['recent_month_mask']].mean(axis = 1).to_frame()
 
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<0]=0
        return factor
    

##########
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
import bottleneck as bk

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            if isinstance(sig, pd.DataFrame):
                sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, pd.Series):
                sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
                sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                    index=sig.index, name=sig.name)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            return 2 * signal - 1    
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            return signal

def ts_rank(df1, d = 1200):
    # moving time-series rank for the past d periods
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output

class ss1_cfg_zf(FactorGeneratorComplex):
    def __init__(self):
        required_columns = ['close_zz500','high_zz500','weight_boolean_zz500','amount_zz500']
        super(ss1_cfg_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        rtn = data['close_zz500']/data['close_zz500'].shift(1)-1
        vol = rtn.rolling(60,min_periods=30).std()
        ret = data['close_zz500']/(data['high_zz500'].shift(1).rolling(60,min_periods=30).max())-1
        facorg = ret/vol
        facorg = rolling_norm(facorg,242*5)
        ar = (data['amount_zz500'][data['weight_boolean_zz500']].rank(axis=1,pct=True))*2-1
        fac = (facorg*ar).sum(axis=1).rolling(5,min_periods=2).mean()
        sig = ts_rank(fac,242*5)
        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_ti9_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti9_cfg, self).__init__(required_columns=['close_zz500', 'open_zz500', 'low_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data_dict):
        # 蜡烛图：实体（带方向）/下影线
        stk_open = data_dict['open_zz500']
        stk_low = data_dict['low_zz500']
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        x = stk_close - stk_open
        y = stk_open.copy()
        y[x<0] = stk_close
        z = y - stk_low
        z[abs(z)<1e-8] = np.nan
        u = x/z
        factor_raw = (u * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 13:46:14 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class MALS_CC(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'recent_month_mask']

        super(MALS_CC, self).__init__(required_columns=required_columns)

    
    def on_bar(self, data):

        temp = data['close'].rolling(60, min_periods = 15).mean() - data['close'].shift(20).rolling(40, min_periods = 7).mean()
        temp = (temp[data['recent_month_mask']]).mean(axis = 1)
        factor = temp.rolling(3, min_periods = 1).mean().to_frame()
       
        factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 2420)
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from utils_zsj import *




class stk2idx_amt_rank_a2p_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_amt_rank_a2p_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][bool_mask]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        rank_win = 30
        stk_amt_rank_short = calc_ts_pct(stk_amt,rank_win)
        score_raw = stk_amt_rank_short
        mask1 = active_mask#up_mask_duration#up_mask#
        mask2 = inactive_mask#down_mask_duration#down_mask#inactive_mask
        active_raw = score_raw[mask1].mean(axis=1)
        inactive_raw = score_raw[mask2].mean(axis=1)
        score = active_raw - inactive_raw

        ma_win = 20
        ts_pct_win = 2400
        min_pct = 0.9
        stk2idx_amt_rank_a2p = calc_ma_helper(-1*score,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_amt_rank_a2p.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 20:47:18 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class L123_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'amount_zz500', 'close_spot', 'weight_boolean_zz500']

        super(L123_CFG2_CC, self).__init__(required_columns=required_columns
                                  )
    

    

    
    def on_bar(self, data):
        df_s = (data['amount_zz500'].rolling(120, min_periods = 15).sum())
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        #stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr[stk_amount]
        columnname = self.__class__.__name__
        hlow = data['low_zz500']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12).rolling(25, min_periods = 2).mean()
        i2 = (i2*bool_df).mean(axis = 1)
        i2 = ts_rank(i2.to_frame())
        #i2 = rolling_norm(i2)
        #i2[i2>1] = np.nan
        #i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 14:32:32 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class HDLD_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'amount_zz500',  'open_zz500', 'weight_boolean_zz500']

        super(HDLD_CFG_CC, self).__init__(required_columns=required_columns
                                  )
    

    
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        temp1 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['open_zz500'], data['close_zz500']))
        temp2 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['close_zz500'], data['open_zz500']))
        temp1.index = data['open_zz500'].index
        temp2.index = data['open_zz500'].index
        temp1.columns = data['open_zz500'].columns
        temp2.columns = data['open_zz500'].columns
        t_pcorr = ((temp1 - temp1.shift(1))+(temp2 - temp2.shift(1))).rolling(60, min_periods = 45).mean()
        
        factor = (t_pcorr[bool_df]).mean(axis = 1)
        #factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor.to_frame())
        #factor = ts_rank(factor)
        #factor[factor<-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_future_nr_as(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts44_future_nr_as, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        temp1 = df['volume' + suffix].copy(deep = True)
        con2 = df['close' + suffix]<delay(df['close' + suffix],1)
        temp1[con2] = -1 * df['volume' + suffix]
        factor = ts_sum(temp1,20)
        factor = ts_mean(factor, 20)

        factor = rolling_normalize(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 300)
        factor = ts_mean(factor, 5)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        return factor

##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from utils_zsj import *

class stk2indx_skew_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2indx_skew_zsj, self).__init__(factor_name = 'stk2indx_skew_zsj',
                                              required_columns = ['close_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 2400)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_ret = stk_close / stk_close.shift(1) - 1
        factor_name = 'stk2indx_skew_zsj'
        ma_win = 20
        ts_pct_win = 1200
        stk2indx_skew_raw = stk_ret[bool_mask].skew(axis=1).rolling(5,min_periods=2).mean()
        stk2indx_skew = calc_ma_helper(stk2indx_skew_raw, ma_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(stk2indx_skew,columns=[self.__class__.__name__])
        return factor



##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts14_future(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts14_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        factor = pd.DataFrame(np.where(df['close'] > delay(df['close'], 2), std(df['close'], 50), 0),
                              index=df['close'].index, columns=df['close'].columns)
        factor = mean(factor, 30)
        factor = factor.fillna(method='ffill')
        factor= ts_rank(factor, 3 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()
                
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 16:48:06 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class CLP_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'position', 'recent_month_mask']

        super(CLP_CC, self).__init__(
                                  required_columns=required_columns)
    def on_bar(self, data):

        temp1 = (pd.DataFrame(np.where(data['close']>0, 1, np.where(data['close']<0, -1, 0))))
        temp1.index = data['close'].index
        temp1.columns = data['close'].columns
        temp1 = (temp1[data['recent_month_mask']]).mean(axis = 1)
        temp3 = ((data['position'].diff())[data['recent_month_mask']]).mean(axis = 1)
        temp3.index = data['position'].index
        temp2 = np.abs(temp3 * (temp1))
        hdl_ind_r = temp2.rolling(30, min_periods = 15).mean()
        factor = hdl_ind_r.to_frame()
        factor.columns = [self.__class__.__name__]
        
        factor = rolling_norm(factor)
        factor[factor<-0.3]=0
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts25_future(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts25_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        factor =  mean(df['close'], 20) / df['close']
        factor = ts_rank_positive(factor, 20)
        factor = mean(factor, 60)

        def rolling_normalize(df, x):
            def normalize(dd):
                a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
                b = (a - 0.5) * 2
                return b

            return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()
        
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_hf3(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf3, self).__init__(required_columns=['Ask1AmtMean_500'],
                                      lookback_bars=2000)

    def on_bar(self, data):
        # factor logic: 见每一行后面的注释
        a = data['Ask1AmtMean_500'].sum(axis=1) # 当下分钟成分股的卖一价总挂单额
        factor_raw = ts_rank(a, 30) # 表示当下挂单额在过去30分钟的排序
        factor_mean = ts_mean(factor_raw, 45)
        factor = -ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 17:37:12 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class LSC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low', 'close', 'recent_month_mask']

        super(LSC_CC, self).__init__(
                                  required_columns=required_columns)

    def normalization(self, signal, holding_window = 1200, ep_range = 3): 
        # Get rid of extreme values using 
        signal_mean = signal.rolling(holding_window,min_periods=int(holding_window/2)).mean() 
        signal_std = signal.rolling(holding_window,min_periods=int(holding_window/2)).std() 
        upper_bound = signal_mean + ep_range*signal_std
        lower_bound = signal_mean - ep_range*signal_std
        signal[signal>upper_bound] = upper_bound
        signal[signal<lower_bound] = lower_bound
        # Rolling Normalize
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        # In Case the input signal is not a DataFrame
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        # In case max_s = min_s
        signal[signal>1] = np.nan
        signal[signal<-1] = np.nan
        return aa
    
    
    def on_bar(self, data):

        hh = (data['high'].rolling(30, min_periods = 10).max() - data['close'])/(data['high'].rolling(30, min_periods = 10).max() - data['low'].rolling(30, min_periods = 10).min()) 
        ll = (data['close'] - data['low'].rolling(30, min_periods = 10).min())/(data['high'].rolling(30, min_periods = 10).max() - data['low'].rolling(30, min_periods = 10).min())
        vwtc_r = ll.rolling(20, min_periods = 15).mean()-hh.rolling(20, min_periods = 15).mean()
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        hh[abs(hh)>10000] = np.nan
        ll[abs(ll)>10000] = np.nan
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242*4)
        factor[factor<=-0.5] = np.nan
        factor = factor.rolling(3, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor[factor<0] = 0
        return factor



##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc19_cfg_as(FactorGeneratorComplex):
    def __init__(self):
        super(wsc19_cfg_as, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_zz500']
        bool_mask = data['weight_boolean_zz500']
        amount_mask = stk_amount[bool_mask]

        # arron_os指标区间为[-100, 100]，100表示股价创新高，-100表示创新低，指标值越大，表示股价最近位置越高
        close = data['close_zz500']
        n = 30
        arron_up = ts_argmax(close, n) / n * 100  # 过去n分钟最高价出现时间与当前时间的距离占时间段长度的比例
        arron_down = ts_argmin(close, n) / n * 100  # 过去n分钟最低价出现时间与当前时间的距离占时间段长度的比例
        arron_os = arron_up - arron_down
        factor_init = arron_os


        factor_raw = (factor_init * amount_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 18)
        factor = ts_rank(factor_mean, 1000)
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.64] = 0
        #factor[factor>=0.5] = np.nan
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 13:30:33 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class HL123_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'high_zz500', 'weight_boolean_zz500']

        super(HL123_CFG_CC, self).__init__(required_columns=required_columns)
    

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_zz500']
        hhigh = df['high_zz500']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12).rolling(5, min_periods = 2).mean()
        i2 = ts_rank(i2[df['weight_boolean_zz500']].mean(axis = 1).to_frame())
        #i2 = rolling_norm(i2)
        #i2[i2>1] = np.nan
        i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


class wsc3_future(FactorGenerator):
    def __init__(self):
        super(wsc3_future, self).__init__(required_columns=['close', 'recent_month_mask'],
                                                lookback_bars=2000)

    def on_bar(self, data):
        mask = data['recent_month_mask']
        a = data['close'].pct_change(5, fill_method=None)
        b = a.rolling(45, min_periods=15).mean()
        c = a.rolling(45, min_periods=15).std()
        factor = b + 2 * c
        factor = factor.rolling(10).mean()
        factor = ts_rank(factor, 600)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 10:02:33 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

    
    
def to_ts(df, ret, LS = True, Lag = False):
    if LS == True:
        if Lag == False:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
        else:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)
    else:
        if Lag == False:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
        else:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)


class CFG16_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'weight_boolean_zz500']
        lookback_bars=2000
        super(CFG16_CC, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)


    def on_bar(self, df):
        columnname = self.__class__.__name__

        hlow = df['low_zz500']
        hclose = df['close_zz500']
        hret = hclose/hclose.shift(1)-1
        i1 = -hlow.rolling(60, min_periods =15).min()/hlow.rolling(30, min_periods =10).mean()
        hret = hret[df['weight_boolean_zz500']]
        i1 = i1[df['weight_boolean_zz500']]
        i2 = to_ts(i1, hret)
        i2 = rolling_norm(i2.rolling(30, min_periods = 15).mean().to_frame(), method = 'ts_rank')
        i2 = i2.rolling(5, min_periods = 2).mean() 
        i2 = rolling_norm(i2, method = 'ts_rank')
        i2[i2>1] = np.nan
        i2[i2<=-0.5] = 0
        i2.columns = [columnname]    
        return i2
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 18:01:27 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class BS_7_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['buy_superorder_money_500', 'buy_bigorder_money_500', 'weight_500', 'amount_500']
        super(BS_7_CC, self).__init__(required_columns=required_columns)
        
    def on_bar(self, data):
        factor = (data['buy_superorder_money_500']+data['buy_bigorder_money_500'])/data['amount_500']
        factor = factor.replace([np.inf, -np.inf], np.nan)
        factor = factor.rolling(15, min_periods = 2).mean()
        df_s = data['amount_500'].rolling(60, min_periods = 5).sum()
        df_s = df_s[data['weight_500']>0]                                                                         
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.9, axis = 1)), axis=0)
        factor = (factor[bool_df]).mean(axis = 1)
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 13:53:15 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

def to_ts(df, ret, LS = True, Lag = False):
    if LS == True:
        if Lag == False:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
        else:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)
    else:
        if Lag == False:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
        else:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)

class CFG8_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['volume_zz500', 'close_zz500', 'float_shares_zz500', 'weight_boolean_zz500']

        super(CFG8_CC, self).__init__(required_columns=required_columns
                                  )
    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hvolume = df['volume_zz500']
        hclose = df['close_zz500']
        hfs = df['float_shares_zz500']
        hret = hclose/hclose.shift(1) - 1
        d1 = hvolume/hclose/hfs
        d1 = d1[df['weight_boolean_zz500']]
        hret = hret[df['weight_boolean_zz500']]
        d1 = to_ts(d1, hret)
        dd1 = d1.rolling(30, min_periods = 15).mean()
        dd2 = rolling_norm(dd1.to_frame())
        dd2.columns = [columnname]
        dd2[dd2<=-0.5] = 0
        dd2[dd2>1] = np.nan
        
        return dd2
##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_icc_ifv_corr(FactorGenerator):
    def __init__(self):
        required_columns=['close','volume_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_icc_ifv_corr, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        high = df['volume_if']
        close = df['close']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = high.rolling(60, min_periods=30).cov(close) / (s * f)
        factor = -1 * factor
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')

        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=False):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk2idx_ret_jump_a2p_chg_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_ret_jump_a2p_chg_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][bool_mask]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        short_win = 5
        long_win = 30
        stk_ret_short = stk_close/stk_close.shift(short_win) - 1
        stk_ret_long = stk_close/stk_close.shift(long_win) - 1
        stk_ret_jump = stk_ret_short - stk_ret_long

        score_raw = stk_ret_jump
        mask1 = active_mask#up_mask_duration#up_mask#
        mask2 = inactive_mask#down_mask_duration#down_mask#
        active_raw = score_raw[mask1].mean(axis=1)
        inactive_raw = score_raw[mask2].mean(axis=1)
        stk2idx_ret_jump_a2p_raw = active_raw - inactive_raw

        short_win = 10
        long_win = 90
        ts_pct_win = 2400
        min_pct = 0.9
        stk2idx_ret_jump_a2p_chg = calc_change_helper(-1*stk2idx_ret_jump_a2p_raw,short_win,long_win,ts_pct_win)        


        factor = stk2idx_ret_jump_a2p_chg.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc12_cfg_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc12_cfg_vr, self).__init__(required_columns=['close_zz500', 'open_zz500', 'stk_volatility_zz500', 'high_zz500', 'low_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 东方金工20200421，通过股价在回滚区间内的位置衡量股票日内买卖压力
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        stk_price = (stk_high + stk_low + stk_open + stk_close) / 4
        n = 30
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        temp = high_n - low_n
        temp[abs(temp)<1e-8] = np.nan
        arpp = (rpp - low_n) / temp
        factor_init = arpp

        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 15:55:47 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class CloseVoltoMean_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'recent_month_mask']

        super(CloseVoltoMean_IFIC_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):

        prstd3_r = data['close_spot_if'].rolling(30, min_periods =10).std()/data['close_spot_if'].rolling(30, min_periods =15).mean()
        prstd3_r = prstd3_r.rolling(10, min_periods = 2).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 13:06:42 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

# demo
class updown_cfg4_CC(FactorGeneratorComplex):
    def __init__(self):

        required_columns =['close_zz500', 'volume_zz500', 'weight_boolean_zz500']

        super(updown_cfg4_CC, self).__init__(
                                  required_columns=required_columns, lookback_bars=2000)
        


    def on_bar(self, data):
        hc = (data['close_zz500']/data['close_zz500'].shift(1)-1)[data['weight_boolean_zz500']]
        hcv = (data['volume_zz500']/data['volume_zz500'].shift(1)-1)[data['weight_boolean_zz500']]
        upclose = (hc>0).sum(axis = 1)
        downclose = (hc<0).sum(axis = 1)
        upvolume = (hcv > 0).sum(axis = 1)
        downvolume = (hcv < 0).sum(axis = 1)
        aa = (upclose/downclose)
        aa[abs(aa)>100000] = np.nan
        bb = (upvolume/downvolume)
        bb[abs(bb)>100000] = np.nan
        vwtc_r = (aa/bb)
        vwtc_r[abs(vwtc_r)>100000] = np.nan
        vwtc_r = vwtc_r.rolling(35, min_periods = 15).mean()
        factor = vwtc_r.to_frame()
        factor.index = hc.index
        
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor


##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk



class wyc_ts14_future_nr_cr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix, 'stk_index_corr' + suffix]
        lookback_bars=2000
        super(wyc_ts14_future_nr_cr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        suffix = '_zz500'
        key = 'close' + suffix
        factor = pd.DataFrame(np.where(df[key] > delay(df[key], 2), std(df[key], 50), 0),
                              index=df[key].index, columns=df[key].columns)
        factor = ts_mean(factor, 30)

        factor = rolling_normalize(factor, 5 * 242)

        cr = (2 * df['stk_index_corr' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * cr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc1_cfg_wr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc1_cfg_wr, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_zz500']
        stk_weight_rank = 2 * stk_weight.rank(axis=1, pct=True) - 1

        # 计算长短两条均线包围的面积
        stk_close = data['close_zz500']
        close_ma_long = ts_mean(stk_close, 90)
        close_ma_short = ts_mean(stk_close, 15)
        factor_init = close_ma_short - close_ma_long
        factor_raw = (factor_init * stk_weight_rank).sum(axis=1)
        factor_mean = factor_raw
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk


class wyc_ts34_future_ts_200_5(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'high' + suffix,'low' + suffix,'volume' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts34_future_ts_200_5, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        factor = ((df['close' + suffix]-df['low' + suffix])-(df['high' + suffix]-df['close' + suffix]))/(df['high' + suffix]-df['low' + suffix])*df['volume' + suffix]
        factor = ts_mean(factor, 150)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        factor = factor * t
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 200)
        factor = ts_mean(factor, 5)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < -0.9] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 17:32:21 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HcorrC_IFIC_CC(FactorGenerator):
    def __init__(self):
        required_columns =['high_if', 'close_if', 'recent_month_mask']

        super(HcorrC_IFIC_CC, self).__init__(
                                  required_columns=required_columns)
        

    def on_bar(self, data):

        high = data['high_if']
        close = data['close_if']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        t_pcor2[abs(t_pcor2) > 1e8] = 0
        factor = t_pcor2[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""

class amihund_measure_zsj(FactorGenerator):
    def __init__(self):
        super(amihund_measure_zsj, self).__init__(factor_name = 'amihund_measure_zsj',
                                                required_columns = [ 'close','amount', 'recent_month_mask'],
                                                lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        mask = data['recent_month_mask']
        close = data['close']
        amount = data['amount']
        minute_ret = close / close.shift(1) - 1

        ##### calc factor #####
        ret_pos = minute_ret > 0
        amount = amount.replace({0: np.nan})
        amihund_measure_raw = minute_ret / amount

        min_pct = 0.9
        amihund_win = 90
        ts_pct_win = 1200
        amihund_measure_raw_ma = amihund_measure_raw.rolling(amihund_win, int(amihund_win * min_pct)).mean()
        amihund_measure = calc_ts_pct(amihund_measure_raw_ma, ts_pct_win)
        amihund_measure = amihund_measure[mask].sum(axis=1)
        amihund_measure.name = self.__class__.__name__
        ##### format factor #####
        factor = pd.DataFrame(amihund_measure)
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 09:59:40 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *


class GA_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['open_zz500', 'close_zz500', 'amount_zz500',  'high_zz500', 'low_zz500', 'weight_boolean_zz500']

        super(GA_CFG_CC, self).__init__(required_columns=required_columns
                                  )
    

    
    def on_bar(self, data):

        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        
        a = data['high_zz500'].rolling(120, min_periods = 60).max()-data['open_zz500'].shift(120)
        b = data['close_zz500'] - data['low_zz500'].rolling(120, min_periods = 60).min()
        c = (data['high_zz500'].rolling(120, min_periods = 60).max()-data['low_zz500'].rolling(120, min_periods = 60).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        factor = (vwtc_r[bool_df]).mean(axis = 1)
        #factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor.to_frame())
        #factor = ts_rank(factor)
        #factor[factor<-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 17:09:20 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from operators_cc import *

# 多头因子
class td_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low', 'high', 'recent_month_mask']
        
        super(td_CC, self).__init__(
                                  required_columns=required_columns)

    


    def on_bar(self, data):
        temp = data['low'].rolling(10, min_periods = 5).min()-data['low'].rolling(60, min_periods = 5).min()+data['high'].rolling(10, min_periods = 5).max()-data['high'].rolling(60, min_periods = 5).max()
        factor = (temp[data['recent_month_mask']]).mean(axis= 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor)
        factor[factor<=-0.5] = 0
        factor[factor>1] = 0
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc16_cfg_search_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc16_cfg_search_vr, self).__init__(required_columns=['close_zz500', 'stk_volatility_zz500'],
                                                  lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 算子搜索
        stk_close = data['close_zz500']
        factor_init = ts_reg_beta(stk_close, 15)

        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1800)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc1_cfg_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc1_cfg_vr, self).__init__(required_columns=['close_zz500', 'stk_volatility_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1
            
        # 计算长短两条均线包围的面积
        stk_close = data['close_zz500']
        close_ma_long = ts_mean(stk_close, 75)
        close_ma_short = ts_mean(stk_close, 10)
        factor_init = close_ma_short - close_ma_long

        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        factor = ts_rank(factor_mean, 900)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 09:45:52 2020

@author: appadmin
"""

import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class CFG21_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'weight_zz500', 'weight_boolean_zz500']

        super(CFG21_CC, self).__init__(required_columns=required_columns
                                  )

            
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_zz500']
        hweight = df['weight_zz500']
        #weight = df['weight_zz500'].xs('weight_zz500', axis=1, drop_level=True)
        
        a = -hlow.rolling(60, min_periods =15).min()/hlow.rolling(15, min_periods =5).mean()
        htemp = ((a[df['weight_boolean_zz500']])*hweight).mean(axis = 1)

        htemp = ts_rank(htemp.to_frame())

        htemp.columns = [columnname]

        return htemp

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:18:46 2020

@author: appadmin
"""

import pandas as pd
import numpy as np

from factor_generator import FactorGenerator
from operators_cc import *

class CDO_CC(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'open', 'recent_month_mask']
        super(CDO_CC, self).__init__(required_columns=required_columns)
                                 

    
    def on_bar(self, data):

        cdo_r = data['close'].rolling(120, min_periods = 60).mean()/data['open'].rolling(120, min_periods = 60).mean()
        factor = (cdo_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')
        #factor = factor.rolling(3,min_periods=1).mean()
        factor[factor<=-0.5]=0
        return factor


##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_future_ts(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'high' + suffix,'low' + suffix,'close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts6_future_ts, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        N = 45
        a = (df['high' + suffix] - df['low' + suffix])
        a[abs(a) < 1e-8] = np.nan
        factor = df['volume'+ suffix] * ((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / a
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/N)

        factor = ts_rank(factor, 1200)
        factor = ts_mean(factor, 15)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        factor = factor * t
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 200)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_sma(df1, alpha):
    # 移动平均 Y_0 = A_0, Y_i = alpha*A_i + (1-alpha)*Y_(i-1)
    output = df1.ewm(alpha=alpha, adjust=False).mean()
    return output


def ts_max(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_max(df1, window=d, min_count=int(d/2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_max(df1, window=d, min_count=int(d/2), axis=0),
                      index=df1.index, name=df1.name)
    return output

def ts_min(df1, d):
    # moving time-series average for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_min(df1, window=d, min_count=int(d/2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_min(df1, window=d, min_count=int(d/2), axis=0),
                      index=df1.index, name=df1.name)
    return output

    
class wsc7_spot(FactorGenerator):
    def __init__(self):
        super(wsc7_spot, self).__init__(required_columns=['amount_spot'],
                                        lookback_bars=2000)

    def on_bar(self, df):
        factor = df['amount_spot'].to_frame()
        factor = ts_max(factor, 20)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor,1150)
        # factor[factor>=0.75] = np.nan
        factor[factor<=-0.5] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 10:16:52 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class CFG19_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'weight_zz500', 'weight_boolean_zz500']

        super(CFG19_CC, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def to_ts(self, df, ret, weight, LS = True, Lag = False):
        ret = ret*weight
        #df = df.fillna(0)
        #print((df!=0).astype(int).sum(axis = 1))
        if LS == True:
            if Lag == False:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
            else:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)
        else:
            if Lag == False:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
            else:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        hweight = df['weight_zz500']
        hlow = df['low_zz500']
        hclose = df['close_zz500']
        hret = hclose/hclose.shift(1)-1
        #weight = df['weight_zz500'].xs('weight_zz500', axis=1, drop_level=True)
        htemp = (hlow<=(hlow.rolling(15, min_periods = 2).min())).astype(int).rolling(90, min_periods = 5).mean()
        htemp = self.to_ts(htemp, hret, hweight)
        htemp = self.normalization(htemp.to_frame().rolling(120, min_periods = 15).mean(), 242*3)
        #a2 = pd.DataFrame(a2)
        htemp.index = hlow.index
        htemp.columns = [columnname]
        htemp[htemp<=-0.5] = 0
        return htemp

##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""
class volume_level_zsj(FactorGenerator):
    def __init__(self):
        super(volume_level_zsj, self).__init__(factor_name = 'volume_level_zsj',
                                                required_columns = ['volume', 'recent_month_mask'],
                                                lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        mask = data['recent_month_mask']
        volume = data['volume']

        ##### calc factor #####
        ma_win = 60
        ts_pct_win = 1200
        volume_ma_raw = volume.rolling(ma_win).mean()
        volume_level = calc_ts_pct(volume_ma_raw, ts_pct_win)
        volume_level = volume_level[mask].sum(axis=1)

        ##### format factor #####
        volume_level.name = self.__class__.__name__
        factor = pd.DataFrame(volume_level)
        return factor

##########
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg5(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg5, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_zz500', 'weight_boolean_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # 选取每个截面上过去3分钟收益率最高的前10%的股票，然后求它们的加权交易额（权重为weight）
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']
        stk_ret = stk_close.pct_change(3, fill_method=None)[bool_mask]
        stk_ret_long = stk_ret.gt(stk_ret.quantile(0.9, axis=1), axis=0)
        factor = stk_amt[stk_ret_long]#.rolling(30, min_periods=20).mean()
        # factor = stk_ret.rolling(30*2, min_periods=15).cov(stk_amt)
        factor = (factor * data['weight_zz500']).sum(axis=1)
        #factor = factor.rolling(5, min_periods=1).mean()
        factor = factor.rolling(20, min_periods=7).mean()

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 200*6)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc2_cfg_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc2_cfg_vr, self).__init__(required_columns=['close_zz500', 'stk_volatility_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1
            
        # as follows
        stk_close = data['close_zz500']
        a = stk_close.pct_change(3, fill_method=None)
        b = ts_mean(a, 30)
        c = ts_std(a, 30)
        factor_init = 4 * b + c
        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 16)
        factor = ts_rank(factor_mean, 1800)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


def ts_max(df1, d):
    # time-series max over the past d1 periods ,whose min_periods is d2
    output = pd.DataFrame(bk.move_max(df1, window=d, min_count=int(d/2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


def rolling_norm(sig, window=240, method='max_min'):
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            # sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_min) / (sig_max - sig_min)
            return 2 * signal - 1
        elif method == 'max_min_mean':
            sig_max = sig.rolling(window, min_periods=int(window / 2)).max()
            sig_min = sig.rolling(window, min_periods=int(window / 2)).min()
            sig_mean = sig.rolling(window, min_periods=int(window / 2)).mean()
            signal = (sig - sig_mean) / (sig_max - sig_min)
            return signal


class wsc_tsmax_amount(FactorGenerator):
    def __init__(self):
        required_columns = ['amount', 'recent_month_mask']
        lookback_bars = 2000
        super(wsc_tsmax_amount, self).__init__(required_columns=required_columns,
                                               lookback_bars=lookback_bars)

    def on_bar(self, df):
        # 算子搜索
        mask = df['recent_month_mask']
        factor = df['amount']
        factor = ts_max(factor, 45)
        factor = rolling_norm(factor, 120)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor>=0.75] = np.nan
        # factor[(factor<=-0.6)&(factor>=-0.5)] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc18_cfg_as(FactorGeneratorComplex):
    def __init__(self):
        super(wsc18_cfg_as, self).__init__(required_columns=['close_zz500', 'high_zz500', 'low_zz500', 'open_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_zz500']
        bool_mask = data['weight_boolean_zz500']
        amount_mask = stk_amount[bool_mask]


        # 根据asi指标改造而来
        # asi指标由si累加而来，但这样会导致每个时刻累加的起点不同，因此用si过去一段时间的移动平均代替，解决起点不同的问题
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        n = 20
        a = abs(stk_high-ts_delay(stk_close, 1))
        b = abs(stk_low-ts_delay(stk_close, 1))
        c = abs(stk_high-ts_delay(stk_low, 1))
        d = abs(ts_delay(stk_close, 1)-ts_delay(stk_open, 1))
        k = np.maximum(a, b)
        m = ts_max(stk_high-stk_low, n)
        r1 = a + 0.5*b + 0.25*d
        r2 = b + 0.5*a + 0.25*d
        r3 = c + 0.25*d
        r4 = r2.copy(deep=True)
        r4[(a>=b)&(a>=c)] = r1
        r = r4.copy(deep=True)
        r[(c>=a)&(c>=b)] = r3
        r[abs(r)<1e-8] = np.nan
        m[abs(m)<1e-8] = np.nan
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open)) / r * k / m
        factor_init = si

        factor_raw = (factor_init * amount_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = ts_rank(factor_mean, 1200)
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.7] = 0
        #factor[factor>=0.5] = np.nan
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from utils_zsj import *


class high_low_diff_stk2idx_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(high_low_diff_stk2idx_zsj, self).__init__(
            required_columns=['close_zz500', 'amount_zz500', 'high_zz500', 'low_zz500', 'open_zz500', 'weight_boolean_zz500'],
            lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        stk_amt = data['amount_zz500']

        # factor logic
        # factor_name = 'high_low_diff_stk2idx'
        roll_win = 30
        ma_win = 30
        ts_pct_win = 2400
        min_pct = 0.9
        min_periods = int(0.5 * roll_win)
        high_open_diff = stk_high - stk_open
        open_low_diff = stk_open - stk_low
        high_low_diff_stk = high_open_diff.rolling(roll_win, min_periods).sum() - open_low_diff.rolling(roll_win,
                                                                                                        min_periods).sum()
        high_low_diff_stk2idx_raw = high_low_diff_stk[bool_mask].mean(axis=1)
        high_low_diff_stk2idx = calc_ma_helper(high_low_diff_stk2idx_raw, ma_win, ts_pct_win, min_pct)
        # ts_factor_quick(high_low_diff_stk2idx, price, factor_name, layers=5)

        factor = high_low_diff_stk2idx.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200 * 4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 18:18:43 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *


class CFG18_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_zz500', 'close_zz500', 'weight_zz500', 'weight_boolean_zz500']

        super(CFG18_CC, self).__init__(required_columns=required_columns
                                  )


    def on_bar(self, df):
        columnname = self.__class__.__name__
        hhigh = df['high_zz500']
        hclose = df['close_zz500']
        hweight = df['weight_zz500']
        hret = hclose/hclose.shift(1)-1
        #weight = df['weight_zz500'].xs('weight_zz500', axis=1, drop_level=True)
        htemp = (hhigh>=(hhigh.rolling(45, min_periods = 5).max())).astype(int).rolling(90, min_periods = 5).mean()
        htemp = ((hret*hweight)[df['weight_boolean_zz500']]).mean(axis = 1)
        htemp = rolling_norm(htemp.to_frame().rolling(45, min_periods = 15).mean(), method = 'ts_rank')
        #a2 = pd.DataFrame(a2)
        htemp.index = hhigh.index
        htemp.columns = [columnname]
        htemp[htemp<=-0.5] = 0
        return htemp
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts53_future(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'volume', 'position', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts53_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        N = 10
        turnover = df['volume'] / df['position']
        returns = df['close'].pct_change(fill_method=None)
        s = turnover.rolling(N, min_periods=N//2).std()
        f = returns.rolling(N, min_periods=N//2).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = -1 * turnover.rolling(N, min_periods=N//2).cov(returns) / (s * f)

        # factor = -1 * correlation(turnover,returns,N).replace([np.inf,-np.inf],np.nan)
        factor = ts_rank_positive(factor, 15)
        factor = mean(factor, 100)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.5] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *


class wyc_ihcv_corr(FactorGenerator):
    def __init__(self):
        required_columns=['close_ih','volume_ih', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ihcv_corr, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        # factor = correlation(df.close_ih, df.volume_ih, 30)
        mask = df['recent_month_mask']
        high = df['volume_ih']
        close = df['close_ih']
        s = high.rolling(30, min_periods=15).std()
        f = close.rolling(30, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = high.rolling(30, min_periods=15).cov(close) / (s * f)
        factor = -1 * mean(factor, 10)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 3 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]

        factor[factor<-0.5]=0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts38_future(FactorGenerator):
    def __init__(self):

        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts38_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        temp1 = df['close'].copy()
        temp1[df['close'] > delay(df['close'], 1)] = std(df['close'],20)
        temp1[df['close'] <= delay(df['close'], 1)] = 0
        a = sma(temp1, 100, 1)
        temp1[df['close'] > delay(df['close'], 1)] = 0
        temp1[df['close'] <= delay(df['close'], 1)] = std(df['close'], 20)
        b = sma(temp1, 100, 1)
        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = ts_rank_positive(factor, 30)
        factor = mean(factor, 100)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()


        columnname = self.__class__.__name__
        factor.columns = [columnname]

        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc18_cfg_ar(FactorGeneratorComplex):
    def __init__(self):
        super(wsc18_cfg_ar, self).__init__(required_columns=['close_zz500', 'high_zz500', 'low_zz500', 'open_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_zz500']
        weight_true = data['weight_boolean_zz500']
        amount_mask = stk_amount[weight_true]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 根据asi指标改造而来
        # asi指标由si累加而来，但这样会导致每个时刻累加的起点不同，因此用si过去一段时间的移动平均代替，解决起点不同的问题
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        n = 45
        a = abs(stk_high-ts_delay(stk_close, 1))
        b = abs(stk_low-ts_delay(stk_close, 1))
        c = abs(stk_high-ts_delay(stk_low, 1))
        d = abs(ts_delay(stk_close, 1)-ts_delay(stk_open, 1))
        k = np.maximum(a, b)
        m = ts_max(stk_high-stk_low, n)
        r1 = a + 0.5*b + 0.25*d
        r2 = b + 0.5*a + 0.25*d
        r3 = c + 0.25*d
        r4 = r2.copy(deep=True)
        r4[(a>=b)&(a>=c)] = r1
        r = r4.copy(deep=True)
        r[(c>=a)&(c>=b)] = r3
        r[abs(r)<1e-8] = np.nan
        m[abs(m)<1e-8] = np.nan
        si = 50 * (ts_delta(stk_close, 1) + ts_delay(stk_close, 1) - ts_delay(stk_open, 1) + 0.5*(stk_close - stk_open)) / r * k / m
        factor_init = si

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 50)
        factor = ts_rank(factor_mean, 650)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 16:06:54 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

# 多头因子
class lma_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low', 'close', 'recent_month_mask']
        
        super(lma_CC, self).__init__(
                                  required_columns=required_columns)

    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa

    def on_bar(self, data):

        vwtc_r = (data['low']-data['close'].rolling(120, min_periods = 30).mean())
        factor = (vwtc_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 2420)
        factor[factor<0] = 0
        factor[factor>1] = 0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts419_ar_cfg(FactorGeneratorComplex):
    def __init__(self):

        required_columns=['close_zz500','high_zz500','low_zz500','volume_zz500','amount_zz500']
        lookback_bars=2000
        super(wyc_ts419_ar_cfg, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        factor = ts_sum(((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / (
                    df['high' + suffix] - df['low' + suffix]) * df['volume' + suffix], 10)
        finaldf = ts_mean(factor, 30)

        factor = finaldf * (2 * df['amount_zz500'].rank(axis=1, pct=True) - 1)

        factor = factor.sum(axis=1).to_frame()
        factor = ts_mean(factor, 20)

        factor.columns = [columnname]
        factor[columnname] = rolling_norm(factor, 5 * 242)

        factor[factor < -0.5] = 0

        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_future_s(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'close' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts44_future_s, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        temp1 = df['volume' + suffix].copy(deep = True)
        con2 = df['close' + suffix]<delay(df['close' + suffix],1)
        temp1[con2] = -1 * df['volume' + suffix]
        factor = ts_sum(temp1,20)
        factor = ts_mean(factor, 20)

        factor = factor[df['weight_boolean' + suffix]]
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]
        factor[factor < 0] = 0

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 16:25:14 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from operators_cc import *

class Rev_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'recent_month_mask']

        super(Rev_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):
        vwtc_r = data['close']/data['close'].shift(180)-1
        vwtc_r = (vwtc_r[data['recent_month_mask']]).mean(axis = 1)
        factor = vwtc_r.rolling(3, min_periods = 2).mean().to_frame()
        factor = rolling_norm(factor, 2420)
        factor[factor<-0.5] = 0
        factor[factor>1] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 14:04:46 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

# demo
class hhll_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot', 'low_spot']

        super( hhll_ind_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):

        temp = np.where((data['high_spot']>data['high_spot'].shift(1)) & (data['low_spot']>data['low_spot'].shift(1)), 4, np.where((data['high_spot']<data['high_spot'].shift(1)) & (data['low_spot']<data['low_spot'].shift(1)), 0, 1))
        temp = pd.Series(temp)
        temp.index = data['high_spot'].index
        vwtc_r = temp.rolling(45, min_periods =30).mean()
        factor = vwtc_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 2420)
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:10:58 2020

@author: appadmin
"""

import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class L123_CC_nr_ae_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_zz500', 'low_zz500', 'turnover_zz500', 'amount_zz500']
        super(L123_CC_nr_ae_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, df):
        df_s = (df['amount_zz500'].rolling(120, min_periods = 15).sum())[df['weight_boolean_zz500']]
        ret_30 = (df['turnover_zz500']/df['turnover_zz500'].shift(30)-1)[df['weight_boolean_zz500']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)

        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)
        mask = temp1*temp5
        hlow = df['low_zz500']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        ii2 = rolling_norm(i2)
        factor = (ii2*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(40, min_periods = 20).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *


class wyc_if_2hour_return_as_150_20_cfg(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_if_2hour_return_as_150_20_cfg, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'
        ifreturn = df['close' + suffix] / df['close' + suffix].shift(1) - 1
        factor = ts_mean(ifreturn, 200)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 150)
        factor = ts_mean(factor, 20)
        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]


        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts13_future_nr_as_300_10(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts13_future_nr_as_300_10, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        factor = ts_max(delta(rolling_norm(ts_max(high,121),3*242),15),19)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

    
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_hf11(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf11, self).__init__(required_columns=['close_500', 'SellTradeMoney_500'],
                                      lookback_bars=3000)

    def on_bar(self, hf_data):
        # factor logic
        close_500 = hf_data['close_500']
        close_500[abs(close_500) < 1e-8] = np.nan
        stk_ret = ts_pct_change(close_500, 20)
        x = hf_data['SellTradeMoney_500'].rank(axis=1, pct=True) * 2 - 1
        stk_ret = ts_pct_change(close_500, 1).replace([-np.inf, np.inf], np.nan)
        factor_raw = (x*stk_ret).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 36)
        factor = ts_rank(factor_mean, 900)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=True):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class volatility_a2p_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(volatility_a2p_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                 lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][bool_mask]
        stk_ret = stk_close / stk_close.shift(1) - 1

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        # factor_name = 'volatility_a2p'
        ma_win = 20
        ts_pct_win = 2400
        min_pct = 0.92

        roll_win = 15
        min_periods = int(roll_win * 0.5)
        stk_vol = stk_ret.rolling(roll_win, min_periods).std()
        vol_active_raw = stk_vol[active_mask].mean(axis=1)
        vol_inactive_raw = stk_vol[inactive_mask].mean(axis=1)
        volatility_a2p_raw = vol_active_raw - vol_inactive_raw
        volatility_a2p = calc_ma_helper(volatility_a2p_raw, ma_win, ts_pct_win, min_pct)
        # factor = ts_factor_quick(volatility_a2p,price,factor_name,layers=5)

        factor = volatility_a2p.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200 * 4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 13:49:04 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *


class RolTrendLS_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'close_spot', 'high_zz500', 'amount_zz500', 'weight_boolean_zz500']

        super(RolTrendLS_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
        df_s = (data['amount_zz500'].rolling(120, min_periods = 15).sum())
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr*stk_amount
        a = (data['high_zz500'].rolling(120, min_periods = 15).max() - data['low_zz500'].rolling(120, min_periods = 15).min())
        a[abs(a)<1e-8] = np.nan
        ll = (data['close_zz500'] - data['low_zz500'].rolling(120, min_periods = 15).min()) / a
        a2 = ll.rolling(10, min_periods = 5).mean()
        a3 = a2.rolling(10, min_periods = 5).mean()
        vwtc_r = 3*a3-2*a2
        factor = (vwtc_r[bool_df]).mean(axis = 1).to_frame()
        factor = factor.rolling(5, min_periods = 1).mean()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc20_cfg_vs(FactorGeneratorComplex):
    def __init__(self):
        super(wsc20_cfg_vs, self).__init__(required_columns=['close_zz500', 'close_spot', 'stk_volatility_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']

        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股平均波动率打分
        index_return = data['close_spot'].pct_change(periods=45, fill_method=None)
        stock_return = data['close_zz500'].pct_change(periods=45, fill_method=None)
        excess_return = (stock_return.subtract(index_return, axis=0))
        excess_return_weight = volatility_mask[excess_return < 0].sum(axis=1)
        excess_return_weight = ts_mean(excess_return_weight, 15)
        factor = ts_rank(excess_return_weight, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        factor[factor>0] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:19 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

# demo
class CLSH_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'share', 'recent_month_mask']

        super(CLSH_CC, self).__init__(
                                  required_columns=required_columns)

    def on_bar(self, data):

        temp1 = pd.DataFrame(np.where(data['close'].diff()>0, 1, np.where(data['close'].diff()<0, -1, 0)))
        temp1.index = data['close'].index
        temp1.columns = data['close'].columns
        temp1 = (temp1[data['recent_month_mask']]).mean(axis = 1)
        temp2 = np.abs(((data['share'])[data['recent_month_mask']]).mean(axis = 1) * temp1)
        hdl_ind_r = temp2.rolling(30, min_periods = 15).mean()
        factor = hdl_ind_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242*4)
        factor = factor.rolling(5, min_periods = 4).mean()
        factor = ts_rank(factor, 242*3)

        return factor
##########
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from help_functions_wsc import *



class wsc_return_comparison(FactorGenerator):
    def __init__(self):
        super(wsc_return_comparison, self).__init__(required_columns=['close_spot', 'close_spot_if'],
                                                    lookback_bars=2000)

    def on_bar(self, data):
        # 比较hs300指数和zz500指数过去三分钟收益率大小
        a = data['close_spot'].pct_change(3)
        b = data['close_spot_if'].pct_change(3)
        c = a - b
        c[c > 0] = 1
        c[c <= 0] = 0
        temp = c.rolling(180, min_periods=90).sum()
        temp[abs(temp)<1e-8] = np.nan
        factor = c.rolling(30, min_periods=15).sum() / temp
        factor = factor.rolling(10).mean()
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 600 * 2)
        # factor[factor <= -0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *


class wyc_ifcv_corr2(FactorGenerator):
    def __init__(self):
        required_columns=['close_if','volume_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ifcv_corr2, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        # factor = correlation(df.close_if, df.volume_if, 30)
        mask = df['recent_month_mask']
        high = df['volume_if']
        close = df['close_if']
        s = high.rolling(30, min_periods=15).std()
        f = close.rolling(30, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = high.rolling(30, min_periods=15).cov(close) / (s * f)
        factor = -1 * mean(factor, 10)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 3 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]

        factor[factor<-0.5]=0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 16:53:24 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from operators_cc import *

# 多头因子
class vc_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['volume_spot', 'close_spot']

        super(vc_ind_CC, self).__init__(
                                  required_columns=required_columns)

    def on_bar(self, data):
        t_prcd0 = data['volume_spot'].diff().rolling(15, min_periods=7).mean()*(data['close_spot']-data['close_spot'].shift(15))
        factor = t_prcd0.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = -rolling_norm(factor)
        factor[factor>1] = 0
        factor[factor<-1] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:14:51 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class OCtHL_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot', 'low_spot', 'close_spot', 'open_spot']

        super(OCtHL_ind_CC, self).__init__(
                                  required_columns=required_columns)

    def on_bar(self, data):
        temp1 = data['open_spot'] - data['close_spot']
        temp2 = data['high_spot'] - data['low_spot']
        temp2[abs(temp2)<1e-8] = np.nan
        t_pcor2 = -temp1/temp2
        t_pcor2[abs(t_pcor2) > 1e8] = 0
        t_pcor2 = t_pcor2.rolling(30, min_periods = 15).mean().rolling(5, min_periods = 2).mean()
        factor = t_pcor2.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
    
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 09:05:01 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class CrossingTurns_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_zz500', 'close_zz500', 'low_zz500', 'open_zz500', 'close_spot', 'weight_boolean_zz500', 'amount_zz500']

        super(CrossingTurns_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    
    def on_bar(self, data):
        df_s = (data['amount_zz500'].rolling(120, min_periods = 15).sum())
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr*stk_amount
        temp = np.abs(data['close_zz500']-data['open_zz500'])
        temp[temp==0] = 0.01
        #temp.index = hclose.index
        temp0 = (data['high_zz500'] - data['low_zz500'])
        temp1 = temp0/temp
        a = (data['close_zz500']/data['close_zz500'].shift(1)-1).rolling(30, min_periods = 15).sum()
        vwtc_r = (temp1*(a)).rolling(15, min_periods = 2).mean()
        factor = (vwtc_r[bool_df]).mean(axis = 1)
        factor.index = data['close_zz500'].index
        factor = ts_rank(factor.to_frame())
        factor[factor<=-0.5] = np.nan
        #factor = (factor - 0.25)*4/3
        factor.columns = [self.__class__.__name__]
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_hf2(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf2, self).__init__(required_columns=['BuyTradeNum_500', 'BuyUniqueOrderNum_500', 'weight_500'],
                                      lookback_bars=2000)

    def on_bar(self, data):
        # 主买独立成交订单数/主买成交订单数，比值越小，说明一笔单子拆分的越细，也就是说拆分前的单子（即独立订单数）金额越大，而大单的涌入一般会出现领涨现象
        buow = (data['BuyUniqueOrderNum_500']*data['weight_500']).sum(axis=1)
        buow[abs(buow) < 1e-8] = np.nan
        factor_raw = (data['BuyTradeNum_500']*data['weight_500']).sum(axis=1) / buow
        factor_mean = ts_mean(factor_raw, 25)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = 0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from help_functions_wsc import multi_processing_joblib
from operators_wsc import *


class wsc5_future(FactorGenerator):
    def __init__(self):
        super(wsc5_future, self).__init__(required_columns=['close', 'high', 'low', 'recent_month_mask'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # er技术指标。用来衡量市场的多空力量对比。
        # 在多头市场，人们会更贪婪地在接近高价的地方买入，BullPower越高则当前多头力量越强；而在空头市场，人们可能因为恐惧而在接近低价的地方卖出，BearPower越低则当前空头力量越强。
        # 当两者都大于0时，反映当前多头力量占据主导地位；两者都小于0则反映空头力量占据主导地位。
        mask = data['recent_month_mask']
        close = data['close']
        high = data['high']
        low = data['low']
        N = 45
        bull_power = high - multi_processing_joblib(close, ts_truncated_ema, n_jobs=-1, d=60, alpha=(N-1)/(N+1))
        bear_power = low - multi_processing_joblib(close, ts_truncated_ema, n_jobs=-1, d=60, alpha=(N-1)/(N+1))
        factor_raw = bull_power + bear_power
        factor_mean = -ts_mean(factor_raw, 180)
        factor = ts_rank(factor_mean, 900)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.5] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from utils_zsj import *

class csv_disp_chg_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(csv_disp_chg_zsj, self).__init__(factor_name = 'csv_disp_chg_zsj',
                                              required_columns = ['close_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 2400)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        factor_name = 'csv_disp_chg_zsj'
        ma_win = 60
        short_win = 20
        long_win = 240
        ts_pct_win = 1200
        csv_disp = stk_ret.std(axis=1)
        stk2idx_ret = stk_ret.mean(axis=1)
        csv_disp_sign_raw = csv_disp * np.sign(stk2idx_ret)
        csv_disp_sign = calc_ma_helper(csv_disp_sign_raw, ma_win, ts_pct_win)
        csv_disp_chg = calc_change_helper(csv_disp_sign, short_win, long_win, ts_pct_win)
        ##### format factor #####
        factor = pd.DataFrame(csv_disp_chg,columns=[self.__class__.__name__])
        return factor



##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_future_vr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'close' + suffix,'stk_volatility' + suffix]
        lookback_bars=2000
        super(wyc_ts44_future_vr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        temp1 = df['volume' + suffix].copy(deep = True)
        con2 = df['close' + suffix]<delay(df['close' + suffix],1)
        temp1[con2] = -1 * df['volume' + suffix]
        factor = ts_sum(temp1,20)
        factor = ts_mean(factor, 20)

        vr = (2 * df['stk_volatility' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * vr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 100)
        factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 17:58:03 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *
# 多头因子
class cmh_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns =['high_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']
        
        super(cmh_CFG_CC, self).__init__(
                                  required_columns=required_columns)

    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        vwtc_r = (data['high_zz500']-data['close_zz500'].rolling(60, min_periods = 30).mean())
        factor = (vwtc_r[bool_df]).mean(axis = 1).to_frame()
        #factor.index = data.index

        
        factor = ts_rank(factor, 1000)
        factor = factor.rolling(2, min_periods = 1).mean()
        factor = ts_rank(factor)

        factor[factor<=-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts225_future(FactorGenerator):
    def __init__(self):

        required_columns=['close_ih', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts225_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        columnname = self.__class__.__name__
        cih = df['close_ih']
        cih[abs(cih) < 1e-8] = np.nan
        factor = mean(cih, 20) / cih
        factor = ts_rank(factor, 20)
        factor = ts_mean(factor, 60)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()        
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 15:00:22 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class CFG12_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'low_zz500', 'weight_zz500', 'weight_boolean_zz500']
        lookback_bars=2000
        super(CFG12_CC, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)
    
    
    def on_bar(self, df):
        columnname = self.__class__.__name__

        hclose = df['close_zz500']
        hlow = df['low_zz500']
        weight = df['weight_zz500']
        g = hlow.rolling(120, min_periods = 90).min()/hclose
        g1 = ((g*weight)[df['weight_boolean_zz500']]).mean(axis = 1)
        gg1 = (-g1)
        gg2 = rolling_norm(gg1.to_frame(), method = 'ts_rank')
        #gg2[gg2<=-0.5] = np.nan
        gg2[gg2>1] = np.nan
        gg2.columns = [columnname]    
        return gg2

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts37_future(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts37_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        factor = -1 * sma(((df['close']-mean(df['close'],20))/mean(df['close'],20) - delay((df['close'] - mean(df['close'],20))/mean(df['close'],20),6)),12,1)

        factor = ts_rank_positive(factor, 40)
        factor = mean(factor, 50)

        def rolling_normalize(df, x):
            def normalize(dd):
                a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
                b = (a - 0.5) * 2
                return b

            return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from utils_zsj import *


class stk2idx_ret_ch_corr_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_ret_ch_corr_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'high_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']

        # factor logic
        stk_high = data['high_zz500']
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_high[abs(stk_high) < 1e-8] = np.nan
        stk_ret_close = stk_close/stk_close.shift(1) - 1
        stk_ret_high = stk_high/stk_high.shift(1) - 1
        ret_close_high_corr_raw = stk_ret_close[bool_mask].corrwith(stk_ret_high[bool_mask],axis=1)
        ma_win = 30
        ts_pct_win = 1200
        min_pct = 0.9
        stk2idx_ret_ch_corr = calc_ma_helper(ret_close_high_corr_raw,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_ret_ch_corr.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 14:46:50 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HcorrC_ind_CC(FactorGenerator):
    def __init__(self):
        
        required_columns =['close_spot', 'high_spot']
        
        super(HcorrC_ind_CC, self).__init__(
                                  required_columns=required_columns)


    
    def on_bar(self, data):


        high = data['high_spot']
        close = data['close_spot']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        t_pcor2[abs(t_pcor2) > 1e8] = 0
        factor = t_pcor2.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 2420)
        return factor

##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from utils_zsj import *

class vol_diff_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(vol_diff_zsj, self).__init__(factor_name = 'vol_diff_zsj',
                                              required_columns = ['close_zz500','volume_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 2400)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_volume = data['volume_zz500']
        factor_name = 'vol_diff'
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        up_mask = stk_ret > 0
        down_mask = stk_ret < 0
        up_vol = stk_volume[up_mask].sum(axis=1)
        down_vol = stk_volume[down_mask].sum(axis=1)
        vol_diff_raw = up_vol - down_vol
        vol_diff_raw = vol_diff_raw.rolling(60,min_periods=15).mean()
        vol_diff = rolling_norm(vol_diff_raw,window=242*5)
        vol_diff[vol_diff<=-0.85] = 0
        ##### format factor #####
        factor = pd.DataFrame(vol_diff,columns=[self.__class__.__name__])
        return factor



##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc12_cfg_cs(FactorGeneratorComplex):
    def __init__(self):
        super(wsc12_cfg_cs, self).__init__(required_columns=['close_zz500', 'stk_index_corr_zz500', 'high_zz500', 'low_zz500', 'open_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']

        # 东方金工20200421，通过股价在回滚区间内的位置衡量股票日内买卖压力
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        stk_price = (stk_high + stk_low + stk_open + stk_close) / 4
        n = 30
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        temp = high_n - low_n
        temp[abs(temp)<1e-8] = np.nan
        arpp = (rpp - low_n) / temp
        factor_init = -arpp

        factor_raw = (factor_init * corr_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 3)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        #factor[factor<=-0.8] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 13:11:08 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


# demo
class updown_cfg4_2_CC(FactorGeneratorComplex):
    def __init__(self):

        required_columns =['close_zz500', 'volume_zz500', 'amount_zz500', 'weight_boolean_zz500']

        super(updown_cfg4_2_CC, self).__init__(
                                  required_columns=required_columns, lookback_bars=2000)
        


    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        hc = ((data['close_zz500']/data['close_zz500'].shift(1)-1))[stk_amount]
        hcv = ((data['volume_zz500']/data['volume_zz500'].shift(1)-1))[stk_amount]
        upclose = (hc>0).sum(axis = 1)
        downclose = (hc<0).sum(axis = 1)
        upvolume = (hcv > 0).sum(axis = 1)
        downvolume = (hcv < 0).sum(axis = 1)
        aa = (upclose/downclose)
        aa[abs(aa)>100000] = np.nan
        bb = (upvolume/downvolume)
        bb[abs(bb)>100000] = np.nan
        vwtc_r = (aa/bb)
        vwtc_r[abs(vwtc_r)>100000] = np.nan
        vwtc_r = vwtc_r.rolling(35, min_periods = 15).mean()
        factor = vwtc_r.to_frame()
        factor.index = hc.index
        
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 17:01:00 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class CFG26_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']

        super(CFG26_CC, self).__init__(required_columns=required_columns
                                  )
    

            
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        #stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr[stk_amount]
        hmhm_r = data['close_zz500'].rolling(60, min_periods = 15).mean() - data['close_zz500'].shift(20).rolling(40, min_periods = 7).mean()
        factor = (hmhm_r*bool_df).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        #factor = factor.rolling(3, min_periods =2).mean()
        factor = ts_rank(factor, 242*3)
        factor[factor<-0.5]=0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:19:05 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class RolTrendLS_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot', 'high_spot']

        super(RolTrendLS_ind_CC, self).__init__(
                                  required_columns=required_columns)
        


    def on_bar(self, data):
        a = (data['high_spot'].rolling(60, min_periods = 15).max() - data['low_spot'].rolling(60, min_periods = 15).min())
        a[abs(a)<1e-8] = np.nan
        ll = (data['close_spot'] - data['low_spot'].rolling(60, min_periods = 15).min()) / a
        a2 = ll.rolling(10, min_periods = 5).mean()
        a3 = a2.rolling(10, min_periods = 5).mean()
        vwtc_r = 3*a3-2*a2
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts37_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts37_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__


        cmcs = mean(df['close_spot'],25)
        cmcs[abs(cmcs) < 1e-6] = np.nan
        factor = (df['close_spot']-mean(df['close_spot'],25))/cmcs - delay((df['close_spot'] - mean(df['close_spot'],25))/cmcs,6)
        factor = -1 * ts_truncated_ema(factor, 100, 5/12)

        factor = ts_rank_positive(factor, 25)
        factor = mean(factor, 50)

        factor = factor.to_frame()
        factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        
        return factor
##########
from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp4_future(FactorGenerator):
    def __init__(self):
        super(wsc_gp4_future, self).__init__(required_columns=['amount', 'recent_month_mask'],
                                         lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170701-20190228，验证时间段：20190301-20190630
        # 因子逻辑：过去30分钟amount的最大值的线性外推，amount越大收益越高，逻辑合理。
        future_amount = data_dict['amount']
        future_mask = data_dict['recent_month_mask']
        amount_max = ts_max(future_amount, 39)
        factor_raw = multi_processing_joblib(df=amount_max, func=ts_pred, n_jobs=-1, d=64)[future_mask].sum(axis=1)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:44:58 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *



class CFG20_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'high_zz500', 'weight_zz500', 'weight_boolean_zz500']

        super(CFG20_CC, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_zz500']
        hhigh = df['high_zz500']
        hclose = df['close_zz500']
        hweight = df['weight_zz500']
        #hret = hclose/hclose.shift(1)-1
        #weight = df['weight_zz500'].xs('weight_zz500', axis=1, drop_level=True)
        r = (hhigh.rolling(90, min_periods = 10).max() - hlow.rolling(90, min_periods = 10).min())
        r[abs(r)<1e-8] = np.nan
 
        hh = (hhigh.rolling(90, min_periods = 10).max() - hclose)/r 

        ll = (hclose - hlow.rolling(90, min_periods = 10).min())/r
       

        vwtc_r = ll.rolling(20, min_periods = 5).mean()

        vw = hh.rolling(20, min_periods = 5).mean()
        
        a = vwtc_r-vw
        htemp = ((a[df['weight_boolean_zz500']])*hweight).mean(axis = 1)

        htemp = rolling_norm(htemp.to_frame(), 242*3)
        htemp[np.abs(htemp)>1] = 0
        htemp = htemp.rolling(3, min_periods = 2).mean()
        htemp = rolling_norm(htemp)
        
        #a2 = pd.DataFrame(a2)
        #htemp.index = hlow.index
        htemp.columns = [columnname]
        htemp[np.abs(htemp)>1] = 0
        htemp[htemp<=0] = 0
        return htemp
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 17:16:54 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class LminLmean_CC(FactorGenerator):
    def __init__(self):
        required_columns =['low', 'recent_month_mask']
        super(LminLmean_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        ctl_r = -data['low'].rolling(60, min_periods =15).min()/data['low'].rolling(30, min_periods =10).mean()
        factor = ctl_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<=-0.5] = 0
        return factor



##########
from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp6_future(FactorGenerator):
    def __init__(self):
        super(wsc_gp6_future, self).__init__(required_columns=['volume', 'recent_month_mask'],
                                             lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170701-20190228，验证时间段：20190301-20190630
        # 因子逻辑：成交量的波动率，如果逻辑成立的话就是成交量波动越大，未来收益越高
        future_volume = data_dict['volume']
        future_mask = data_dict['recent_month_mask']
        factor_raw = ts_std(future_volume, 22)[future_mask].sum(axis=1)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts41_future(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts41_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        factor = wma(((df['close'] - delay(df['close'],3))/delay(df['close'],3)*100+(df['close'] - delay(df['close'],6))/delay(df['close'],6)*100),12)
        factor = ts_rank_positive(-1 * factor, 20)
        factor = mean(factor, 20)
        factor = factor.fillna(method='ffill')
        factor = rolling_normalize(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *

class wyc_ts2_future(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'volume', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ts2_future, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        mask = df['recent_month_mask']
        factor = mean(mean((sign(delta(df['volume'], 5)) * (-1 * delta(df['close'], 5))),2),10)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 10:56:58 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class HDLD_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_zz500', 'low_zz500','close_zz500', 'open_zz500', 'close_spot', 'weight_boolean_zz500']

        super(HDLD_CFG2_CC, self).__init__(required_columns=required_columns
                                  )
    

    

    
    def on_bar(self, data):
        
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        temp = np.abs(data['close_zz500']-data['open_zz500'])
        temp[temp==0] = 0.01
        temp.index = data['high_zz500'].index
        temp0 = (data['high_zz500'] - data['low_zz500'])
        temp1 = temp0/temp
        a = (data['close_zz500']/data['close_zz500'].shift(1)-1).rolling(30, min_periods = 15).sum()
        vwtc_r = (temp1*(a))#.rolling(20, min_periods = 2).mean()
        factor = (vwtc_r[bool_df]).mean(axis = 1)
        factor.index = data['close_zz500'].index
        factor = factor.to_frame()
        factor = factor.rolling(10, min_periods = 5).mean()
        #print(b.iloc[:, 0].corr(b1.iloc[:, 0]))
        factor2 = ts_rank(factor, 242*3)
        factor2 = factor2.rolling(3, min_periods = 1).mean()
        factor2 = ts_rank(factor2)
        factor2[factor2<=-0.5] = np.nan
        factor2.columns = [self.__class__.__name__]
        return factor2

##########
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_cfg4(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg4, self).__init__(required_columns=['close_zz500', 'open_zz500', 'weight_zz500', 'high_zz500', 'low_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # b/a衡量了这一分钟的股价波动
        a = data['high_zz500'] - data['low_zz500']
        a[a<1e-5] = np.nan
        b = (data['close_zz500']-data['open_zz500'])
        b[b<0] = np.nan
        c = ts_sum(b/a, 60)
        factor = (c * data['weight_zz500']).sum(axis=1)
        factor_mean = ts_mean(factor, 5)
        factor = ts_rank(factor_mean, 200*6)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:12:29 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class OCtHL_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low', 'close', 'open', 'recent_month_mask']

        super(OCtHL_CC, self).__init__(
                                  required_columns=required_columns)


    def on_bar(self, data):
        temp1 = data['open'] - data['close']
        temp2 = data['high'] - data['low']
        temp2[abs(temp2)<1e-8] = np.nan
        t_pcor2 = -temp1/temp2
        t_pcor2[abs(t_pcor2) > 1e8] = 0
        t_pcor2 = t_pcor2.rolling(30, min_periods = 15).mean().rolling(5, min_periods = 2).mean()
        
        factor = (t_pcor2[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=True):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk_l2c_a2p_chg_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk_l2c_a2p_chg_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                  lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][bool_mask]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        # factor_name = 'stk_l2c_a2p_chg'
        ma_win = 30
        short_win = 20
        long_win = 90
        ts_pct_win = 2400
        min_pct = 0.9
        stk_low2close_raw = stk_close.rolling(60, 30).min() / stk_close
        stk_l2c_active_raw = stk_low2close_raw[active_mask].mean(axis=1)
        stk_l2c_inactive_raw = stk_low2close_raw[inactive_mask].mean(axis=1)
        stk_l2c_a2p_raw = -1 * (stk_l2c_active_raw - stk_l2c_inactive_raw)
        stk_l2c_a2p_chg = calc_change_helper(stk_l2c_a2p_raw, short_win, long_win, ts_pct_win)
        # ts_factor_quick(stk_l2c_a2p_chg, price, factor_name, layers=5)

        factor = stk_l2c_a2p_chg.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200 * 4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc5_cfg_ws(FactorGeneratorComplex):
    def __init__(self):
        super(wsc5_cfg_ws, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_zz500']

        # tii技术指标，首先计算dev=clos-close_ma，再分别对dev中正负部分各自ts_sum得到devpos和devneg(取负保证该值＞0)，最后计算devpos/(devpos+devneg)
        # 该值越大，表示过去一段上涨的越多，属于动量
        stk_close = data['close_zz500']
        n = 20
        m = int(n/2) + 1
        close_ma = ts_mean(stk_close, n)
        dev = stk_close - close_ma
        devpos = dev.copy(deep=True)
        devneg = -dev.copy(deep=True)
        devpos[devpos<0] = 0
        devneg[devneg<0] = 0
        sumpos = ts_sum(devpos, m)
        sumneg = ts_sum(devneg, m)
        temp = sumpos + sumneg
        temp[abs(temp)<1e-8] = np.nan
        tii = sumpos / temp
        factor_init = tii

        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 90)
        factor = rolling_norm(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 14:04:15 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *



class CFG9_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500']

        super(CFG9_CC, self).__init__(required_columns=required_columns
                                  )


    
    def on_bar(self, df):
        columnname = self.__class__.__name__

        hclose = df['close_zz500']
        hret = hclose/hclose.shift(1) - 1
        
        e = hclose.rolling(30, min_periods = 20).max()/hclose.rolling(30, min_periods = 20).min()
        e = e[df['weight_boolean_zz500']]
        hret = hret[df['weight_boolean_zz500']]
        e1 = to_ts(e, hret)
        ee1 = e1.rolling(30, min_periods = 15).mean()
        e2 = rolling_norm(ee1.to_frame())
        e2[e2<=0] = 0
        e2[e2>1] = np.nan
        e2.columns = [columnname]
        #e2.iloc[:, 0] = e2.iloc[:, 0].rolling(3, min_periods = 2).mean()
        return e2

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc20_cfg_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc20_cfg_vr, self).__init__(required_columns=['close_zz500', 'close_spot', 'stk_volatility_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股平均波动率打分
        index_return = data['close_spot'].pct_change(periods=45, fill_method=None)
        stock_return = data['close_zz500'].pct_change(periods=45, fill_method=None)
        excess_return = (stock_return.subtract(index_return, axis=0))
        excess_return_weight = volatility_rank_mask[excess_return < 0].sum(axis=1)
        excess_return_weight = -ts_mean(excess_return_weight, 15)
        factor = ts_rank(excess_return_weight, 2400)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:25:52 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class PositiontoVolume_CC(FactorGenerator):
    def __init__(self):
        required_columns =['position', 'volume', 'recent_month_mask']
        super(PositiontoVolume_CC, self).__init__(
                                  required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):

        a = (data['volume'].rolling(40, min_periods =30).std())
        a[abs(a) < 1e-8] = np.nan
        pd1_r = -data['position']/ a
        factor = (pd1_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_ti10_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti10_cfg, self).__init__(required_columns=['close_zz500', 'open_zz500', 'high_zz500', 'weight_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # 蜡烛图：实体（带方向）/上影线
        stk_open = data_dict['open_zz500']
        stk_high = data_dict['high_zz500']
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        x = stk_close - stk_open
        y = stk_open.copy()
        y[x>0] = stk_close
        z = stk_high - y
        z[abs(z)<1e-8] = np.nan
        u = x / z
        factor_raw = (u * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 600)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc15_cfg_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc15_cfg_cr, self).__init__(required_columns=['close_zz500', 'stk_index_corr_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # vidya技术指标,vi可用来衡量股票过去一段时间的趋势，趋势越强vi值越大，此时vidya赋予当前的close更大的权重，捕捉趋势，反之同理。
        stk_close = data['close_zz500']
        n = 10
        temp = ts_sum(abs(ts_delta(stk_close, 1)), n)
        temp[abs(temp)<1e-8] = np.nan
        vi = abs(ts_delta(stk_close, n)) / temp
        vidya = vi * stk_close + (1-vi) * ts_delay(stk_close, 1)
        factor_init = rolling_norm(vidya, 240)

        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 2)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.3] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 00:38:19 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class LMLS_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'close_spot', 'weight_boolean_zz500']

        super(LMLS_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        
        '''corr_rank'''
        stk_index_corr_rank = 2 * stk_index_corr.rank(axis=1, pct=True) - 1
        temp = data['low_zz500'].rolling(50, min_periods = 15).mean() - data['low_zz500'].shift(20).rolling(30, min_periods = 7).mean()
        factor = (temp*stk_index_corr_rank).mean(axis = 1).to_frame()
        factor.index = data['low_zz500'].index
        #factor = np.abs(factor)
        factor.columns = [self.__class__.__name__]
        #factor = rolling_norm(factor)
        factor = factor#.rolling(3, min_periods = 2).mean()
        factor = ts_rank(factor)
        #factor[factor<-0.5] = np.nan
        #factor.columns = [self.__class__.__name__]
        
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:51:35 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class ZHZH_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'high_zz500', 'weight_boolean_zz500']
        
        super(ZHZH_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        temp = (data['high_zz500']>=(data['high_zz500'].rolling(30, min_periods = 5).max())).astype(int).rolling(40, min_periods = 5).mean()
        temp = (temp[bool_df]).mean(axis = 1)
        factor = ts_rank(temp.to_frame())
        #factor = ts_rank(factor)
        #factor[factor<=-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts1_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot', 'close_spot']
        lookback_bars=2000
        super(xdy_ts1_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        close = df['close_spot']
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = high / high.shift(60) - 1
        h_c = close / high - 1
        a = mean(h_c, 60)
        a[abs(a) < 1e-8] = np.nan
        factor = ts_sum(gain_high_60 / a, 10)
        factor = mean(factor, 10) * -1
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        factor.loc[factor[columnname] <= -0.5] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""
class dpo_std_zsj(FactorGenerator):
    def __init__(self):
        super(dpo_std_zsj, self).__init__(factor_name = 'dpo_std_zsj',
                                         required_columns = ['close', 'recent_month_mask'],
                                         lookback_bars = 1500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        mask = data['recent_month_mask']

        ##### calc factor #####

        def calc_dpo_sig(close, roll_win):
            dpo = close - REF(MA(close, roll_win), int(roll_win / 2 + 1))
            return dpo

        dpo_win = 45
        ma_win = 30
        ts_pct_win = 1200
        dpo_raw = calc_dpo_sig(close, dpo_win)
        dpo_std_raw = dpo_raw.rolling(ma_win, 1).std()
        dpo_std = calc_ts_pct(dpo_std_raw, ts_pct_win)
        dpo_std = dpo_std[mask].sum(axis=1)

        ##### format factor #####
        dpo_std.name = self.__class__.__name__
        factor = pd.DataFrame(dpo_std)
        factor[factor<=-0.5] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:18:15 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class ClMaxClMin_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot']
 
        super(ClMaxClMin_ind_CC, self).__init__(
                                  required_columns=required_columns)
    
    def on_bar(self, data):

        m_vwap_ind_r = (data['close_spot']).rolling(60, min_periods = 30).max()/data['close_spot'].rolling(60, min_periods = 30).min()
        factor = m_vwap_ind_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')
        return factor


##########
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg10(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg10, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'close_spot', 'weight_boolean_zz500'],
                                        lookback_bars=2000)

    def on_bar(self, data):
        # 计算截面上过去15分钟涨幅最大的前10%的股票加权平均涨幅（权重为weight）
        bool_mask = data['weight_boolean_zz500']
        close = data['close_zz500']
        ret = close.pct_change(15, fill_method=None)[bool_mask]
        # ret_mean = ret.mean(axis=1)
        # ret_std = ret.std(axis=1)
        ret_flag = ret.gt(ret.quantile(0.9, axis=1), axis=0)
        ret_long = ret[ret_flag]
        weight_long = data['weight_zz500'][ret_flag]
        # factor = factor.rolling(10, min_periods=5).mean()
        # factor = factor.sum(axis=1)

        factor = ((ret_long * data['weight_zz500']).sum(axis=1)) / weight_long.sum(axis=1) - data['close_spot'].pct_change(15, fill_method=None)
        # factor = ((ret_long * data['weight_zz500']).sum(axis=1)) / weight_long.sum(axis=1) - (ret * data['weight_zz500']).sum(axis=1)
        factor = factor.rolling(15, min_periods=2).mean()
        factor = factor.to_frame()   
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 300*4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        #factor[factor<=-0.5] = np.nan
        factor[factor>0] = 0
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts14_spot(FactorGenerator):
    def __init__(self):
        required_columns=['close_spot']
        lookback_bars=2000
        super(wyc_ts14_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, df):
        factor = pd.DataFrame(np.where(df['close_spot'] > delay(df['close_spot'], 1), std(df['close_spot'], 50), 0),
                              index=df['close_spot'].to_frame().index, columns=df['close_spot'].to_frame().columns)
        factor = ts_rank_positive(factor, 120)
        factor = mean(factor, 20)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = self.ts_rank(factor, 5 * 242)
        factor.iloc[:, 0] =  factor.iloc[:, 0].rolling(3, min_periods = 2).mean()
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from utils_zsj import *


class stk2idx_amt_chg_u2d_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_amt_chg_u2d_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                     lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        up_mask = stk_ret > 0
        down_mask = stk_ret < 0

        # factor logic
        stk_amt_chg = stk_amt - stk_amt.shift(1)
        score_raw = stk_amt_chg
        mask1 = up_mask
        mask2 = down_mask
        active_raw = score_raw[mask1].mean(axis=1)
        inactive_raw = score_raw[mask2].mean(axis=1)
        score = active_raw - inactive_raw

        ma_win = 60
        ts_pct_win = 1200
        min_pct = 0.9
        stk2idx_amt_chg_u2d = calc_ma_helper(score,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_amt_chg_u2d.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc3_cfg_vr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc3_cfg_vr, self).__init__(required_columns=['close_zz500', 'close_spot', 'stk_volatility_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']
        volatility_rank_mask = 2 * volatility_mask.rank(axis=1, pct=True) - 1

        # 比较股票和指数涨幅大小，大则置1，小则置0
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        index_return = index_close.pct_change(3, fill_method=None)
        stk_return = stk_close.pct_change(3, fill_method=None)
        return_difference = stk_return.sub(index_return, axis=0)
        return_difference[return_difference > 0] = 1
        return_difference[return_difference <= 0] = 0
        temp = ts_sum(return_difference, 90)
        temp[abs(temp)<1e-8] = np.nan
        factor_init = ts_sum(return_difference, 15) / temp
        factor_init = factor_init.replace([-np.inf, np.inf], np.nan)
        factor_raw = (factor_init * volatility_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 16:49:29 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from operators_cc import *

class Rev_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot']

        super(Rev_ind_CC, self).__init__(
                                  required_columns=required_columns)
    
    def on_bar(self, data):
        vwtc_r = data['close_spot']/data['close_spot'].shift(120)-1
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 4800)
        factor[factor<-1] = np.nan
        factor[factor>1] = np.nan
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *

def rolling_norm(df,x):
    def normalize(dd):
        a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
        b = (a-0.5)*2
        return b
    return df.rolling(x, min_periods=int(x/2)).apply(normalize)

class wyc_ifcv_corr(FactorGenerator):
    def __init__(self):
        required_columns=['close_if','volume_if', 'recent_month_mask']
        lookback_bars=2000
        super(wyc_ifcv_corr, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        # factor = correlation(df.close_if, df.volume_if, 30)
        mask = df['recent_month_mask']
        high = df['volume_if']
        close = df['close_if']
        s = high.rolling(30, min_periods=15).std()
        f = close.rolling(30, min_periods=15).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        factor = high.rolling(30, min_periods=15).cov(close) / (s * f)
        factor = -1 * mean(factor, 30)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()
        
        factor.columns = [columnname]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 13:20:46 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class LSC_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'close_spot', 'amount_zz500', 'high_zz500', 'weight_boolean_zz500']

        super(LSC_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
        df_s = (data['amount_zz500'].rolling(120, min_periods = 15).sum())
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None).shift(1)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        #stk_index_corr = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.90, axis = 1)), axis=0)
        bool_df = stk_index_corr*stk_amount
        hh = (data['high_zz500'].rolling(30, min_periods = 10).max() - data['close_zz500'])/(data['high_zz500'].rolling(30, min_periods = 10).max() - data['low_zz500'].rolling(30, min_periods = 10).min()) 
        ll = (data['close_zz500'] - data['low_zz500'].rolling(30, min_periods = 10).min())/(data['high_zz500'].rolling(30, min_periods = 10).max() - data['low_zz500'].rolling(30, min_periods = 10).min())
        hh[abs(hh)>100000] = np.nan
        ll[abs(ll)>100000] = np.nan
        vwtc_r = ll.rolling(15, min_periods = 5).mean()-hh.rolling(15, min_periods = 5).mean()
        factor = (vwtc_r[data['weight_boolean_zz500']]*bool_df).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = factor.rolling(3, min_periods = 1).mean()
        factor = ts_rank(factor)

        #factor[factor<=-0.5] = np.nan
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_1_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_1_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'amount_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # 长江金工高频因子2：结构化反转因子
        # 因子主体由三部分组成：对数收益率，成交量倒数和收益波动率
        # 对数收益率代表动量，成交量倒数的逻辑是当多空力量悬殊时，股价会以很小的成交量迅速到达一个合理价位（这部分内容见研报），收益波动率的逻辑是只有当市场成交活跃时，趋势才强
        # 但是在成分股上，关于成交量的结论和指数上反过来了，也就是成交量越大时趋势越强
        # 发现把volume换成amount，效果更好
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        stk_amount = data_dict['amount_zz500']
        ret = ts_pct_change(stk_close, 1)
        log_ret = log(ret+1)
        ret_std = ts_std(ret, 15)
        log_ret_weight = log_ret * stk_amount * ret_std
        factor_raw = (ts_sum(log_ret_weight, 30)*stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""

class ma_displaced_std_zsj(FactorGenerator):
    def __init__(self):
        super(ma_displaced_std_zsj, self).__init__(factor_name = 'ma_displaced_std_zsj',
                                                           required_columns = ['close', 'recent_month_mask'],
                                                           lookback_bars = 1500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        mask = data['recent_month_mask']
        ##### calc factor #####

        def calc_ma_displaced(close, short_win=10, long_win=20):
            ma_close = MA(close, long_win)
            ma_displaced = REF(ma_close, short_win)
            ma_diff = close - ma_displaced
            return ma_diff

        factor_name = 'ma_displaced_std'
        short_win = 10
        long_win = 90
        std_win = 40
        ts_pct_win = 242*5
        score_raw = calc_ma_displaced(close, short_win, long_win)
        ma_displaced_std = calc_std_helper(score_raw, std_win, ts_pct_win)
        ma_displaced_std = ma_displaced_std[mask].sum(axis=1)

        ##### format factor #####
        ma_displaced_std.name = self.__class__.__name__
        factor = pd.DataFrame(ma_displaced_std) 
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts13_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot']
        lookback_bars=2000
        super(xdy_ts13_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        factor = ts_max(delta(rolling_norm(ts_max(high,121),3*242),15),19)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        factor.loc[factor[columnname] <= 0] = 0

        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts4_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot']
        lookback_bars=2000
        super(xdy_ts4_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        factor = ts_position(high, 30)
        factor = -1 * factor.rolling(100, min_periods=20).skew()
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        factor.loc[factor[columnname] <= -0.5] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 16:17:24 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HLTM_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['vwap_if', 'high_if', 'low_if', 'recent_month_mask']

        super(HLTM_IFIC_CC, self).__init__(
                                  required_columns=required_columns)


    
    def on_bar(self, data):

        temp1 = data['high_if'].rolling(15, min_periods = 7).max()-data['vwap_if']
        temp2 = data['vwap_if']-data['low_if'].rolling(15, min_periods = 7).min()
        temp = pd.DataFrame(np.where(temp1>temp2, temp1, temp2))
        temp.index = temp1.index
        temp.columns = temp1.columns
        vwtc_r = temp.rolling(40, min_periods = 15).mean() 
        factor = (vwtc_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 18:52:13 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class fvs2_ind_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'close_if', 'recent_month_mask']

        super(fvs2_ind_IFIC_CC, self).__init__(
                                  required_columns=required_columns)
    

    def on_bar(self, data):

        close_spot = data['close_spot_if']
        close = data['close_if']
        vwtc_r = close.rolling(40, min_periods=15).corr(close_spot)
        vwtc_r  = vwtc_r.replace([-np.inf, np.inf], np.nan)
        vwtc_r = vwtc_r[data['recent_month_mask']]
        factor = (vwtc_r*(np.sign(-(close.sub(close_spot,axis=0))))[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor = np.abs(factor)
        factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor


##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *
from help_functions_wsc import replace_zero


    
class wsc_hf18(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf18, self).__init__(required_columns=['Bid1AmtMean_500', 'Buy1NumOrdersMean_500', 'weight_500'],
                                       lookback_bars=3000)

    def on_bar(self, hf_data):
        # 买一挂单金额除以买一挂单数量，表征平均一单的挂单金额，还是大小单逻辑
        weight_500 = hf_data['weight_500']
        temp = hf_data['Buy1NumOrdersMean_500'].copy()
        temp = replace_zero(temp)
        factor_raw = (hf_data['Bid1AmtMean_500'] / temp * weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wsc import *



class wsc_ti8(FactorGenerator):
    def __init__(self):
        super(wsc_ti8, self).__init__(required_columns=['high', 'low', 'close', 'open', 'recent_month_mask'],
                                      lookback_bars=2000)

    def on_bar(self, data_dict):
        # 大阳线技术指标，当开盘价接近最低价，收盘价显著高于开盘价且接近最高价时出现该图形。指标范围: [0,1]，且指标越高未来上涨概率越大，因此若close<open，则将指标值置为0.
        future_high = data_dict['high']
        future_low = data_dict['low']
        future_close = data_dict['close']
        future_open = data_dict['open']
        future_mask = data_dict['recent_month_mask']
        x = future_high - future_low
        x[abs(x)<1e-8] = np.nan
        ratio1 = (future_close-future_open) / x
        ratio1[(future_close-future_open)<0] = 0
        factor_mean = ts_mean(ratio1, 120)
        factor = ts_rank(factor_mean, 1200)
        factor = factor[future_mask].sum(axis=1)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts13_future(FactorGenerator):
    def __init__(self):
        required_columns=['high', 'recent_month_mask']
        lookback_bars=2000
        super(xdy_ts13_future, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        mask = df['recent_month_mask']
        high = df['high']
        factor = ts_max(delta(rolling_norm(ts_max(high,121),3*242),15),19)
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor = factor[mask].sum(axis=1)
        factor = factor.to_frame()

        factor.columns = [columnname]
        factor.loc[factor[columnname] <= 0] = 0

        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts6_future_ar(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'high' + suffix,'low' + suffix,'close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts6_future_ar, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        suffix = '_zz500'

        N = 45
        a = (df['high' + suffix] - df['low' + suffix])
        a[abs(a) < 1e-8] = np.nan
        factor = df['volume'+suffix] * ((df['close' + suffix] - df['low' + suffix]) - (df['high' + suffix] - df['close' + suffix])) / a
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/N)
        factor = ts_rank(factor, 1200)
        factor = ts_mean(factor, 15)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        ar = (2 * a.rank(axis=1, pct=True) - 1)
        factor = factor * ar
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 100)
        factor = ts_mean(factor, 20)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor
##########
from factor_generator import FactorGenerator
import pandas as pd
import numpy as np
import bottleneck as bk
from scipy.stats import rankdata

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            if isinstance(sig, pd.DataFrame):
                sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, pd.Series):
                sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
                sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                    index=sig.index, name=sig.name)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            return 2 * signal - 1    
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            return signal

def mean(A,d):
    output = A.rolling(d,min_periods=int(round(d/2))).mean()
    output.iloc[:d-1] = np.nan
    return output

def ts_rank_positive(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                           index=df1.index, name=df1.name)
    return (output+1)/2

def delay(A,n):
    return A.shift(periods=n)

class ts29_futures_zf(FactorGenerator):
    def __init__(self):
        required_columns = ['close','volume', 'recent_month_mask']
        super(ts29_futures_zf, self).__init__(required_columns=required_columns)

    def on_bar(self, data):
        mask = data['recent_month_mask']
        N = 10
        n2 = 20
        n3 = 200
        factor = -1 * (data['close'] - delay(data['close'], N)) / delay(data['close'],N) * data['volume']
        factor = ts_rank_positive(factor, n2)
        factor = mean(factor, n3)
        factor = rolling_norm(factor,242*5)
        factor = factor[mask].sum(axis=1)
        factor.name = self.__class__.__name__
        return pd.DataFrame(factor)
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 14:03:04 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class LminC_ind_CC_vr_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500', 'low_zz500', 'close_spot']
        super(LminC_ind_CC_vr_CFG_CC, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, data):
        '''volatility_sum'''
        stk_close = data['close_zz500']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = self.ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_zz500']]

        '''volatility_rank'''
        mask = 2 * stk_volatility.rank(axis=1, pct=True) - 1
        lltc_ind_r = -data['low_zz500'].rolling(180, min_periods = 90).min()/(data['close_zz500'])
        factor = (lltc_ind_r*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(5, min_periods = 2).mean()
        factor = self.ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts13_future_nr_as_50_10(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['high' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts13_future_nr_as_50_10, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        high = df['high' + suffix]
        factor = ts_max(delta(rolling_norm(ts_max(high,121),3*242),15),19)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 50)
        factor = ts_mean(factor, 10)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0
    
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 13:34:01 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class HcorrC_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_zz500', 'close_zz500', 'high_zz500', 'weight_boolean_zz500']

        super(HcorrC_CFG_CC, self).__init__(required_columns=required_columns
                                  )
    

    

    def on_bar(self, data):

        high = data['high_zz500']
        close = data['close_zz500']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-7] = np.nan
        f[abs(f) < 1e-7] = np.nan
        t_pcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        t_pcor2[~np.isfinite(t_pcor2)] = 0
        factor = (t_pcor2[data['weight_boolean_zz500']]*data['weight_zz500']).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor
##########
from factor_generator import FactorGenerator
from operators_wyc import *
import numpy as np

class xdy_ts2_spot(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot', 'low_spot']
        lookback_bars=2000
        super(xdy_ts2_spot, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        columnname = self.__class__.__name__

        high = df['high_spot']
        low = df['low_spot']
        high[abs(high) < 1e-8] = np.nan
        gain_high_20 = high / high.shift(20) - 1
        factor = (low * gain_high_20).to_frame()
        factor = ts_truncated_ema(factor, 100, 1/26).to_frame()

        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = rolling_norm(factor, 5 * 242)
        factor[factor <= -0.3] = 0

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 15:31:03 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class HHLS_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'high_zz500', 'weight_boolean_zz500']

        super(HHLS_CFG_CC, self).__init__(required_columns=required_columns
                                  )
    

    
            
    def on_bar(self, data): 
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        hdl_r = data['high_zz500'].rolling(40, min_periods = 15).max() - data['high_zz500'].shift(40).rolling(40, min_periods = 7).max()
        factor = hdl_r.rolling(10, min_periods = 2).mean()
        factor = (factor[bool_df]).mean(axis = 1)  
        factors = ts_rank(factor.to_frame())
        factors.columns = [self.__class__.__name__]
        #factors[factors<=-0.5] = np.nan
        return factors

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 10:45:34 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


# demo
class PositiontoVolume2_IFIC_CC(FactorGenerator):
    def __init__(self):
        
        required_columns =['volume_if', 'position_if', 'recent_month_mask']
        super(PositiontoVolume2_IFIC_CC, self).__init__(
                                  required_columns=required_columns)



    def on_bar(self, data):
        a = data['position_if']
        a[abs(a) < 1e-8] = np.nan
        temp = data['volume_if']/a
        hdl_ind_r = temp.rolling(20, min_periods = 15).mean()
        factor = (hdl_ind_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc5_cfg_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc5_cfg_cr, self).__init__(required_columns=['close_zz500', 'close_spot', 'stk_index_corr_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1,pct=True) - 1
        # tii技术指标，首先计算dev=clos-close_ma，再分别对dev中正负部分各自ts_sum得到devpos和devneg(取负保证该值＞0)，最后计算devpos/(devpos+devneg)
        # 该值越大，表示过去一段上涨的越多，属于动量
        stk_close = data['close_zz500']
        n = 20
        m = int(n/2) + 1
        close_ma = ts_mean(stk_close, n)
        dev = stk_close - close_ma
        devpos = dev.copy(deep=True)
        devneg = -dev.copy(deep=True)
        devpos[devpos<0] = 0
        devneg[devneg<0] = 0
        sumpos = ts_sum(devpos, m)
        sumneg = ts_sum(devneg, m)
        temp = sumpos + sumneg
        temp[abs(temp)<1e-8] = np.nan
        tii = sumpos / temp
        factor_init = tii

        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.8] = 0
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_spot(FactorGenerator):
    def __init__(self):

        required_columns=['volume_spot','close_spot']
        lookback_bars=2000
        super(wyc_ts44_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        
        temp1 = df['volume_spot'].copy(deep = True)
        con1 = df['close_spot']>delay(df['close_spot'],1)
        con2 = df['close_spot']<delay(df['close_spot'],1)
        temp1[con2] = -1 * df['volume_spot']
        factor = ts_sum(temp1,20)
        factor = mean(factor, 20)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_norm(factor, 5 * 242)
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts6_spot_tr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'turnover' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts6_spot_tr, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        close = df['close' + suffix]
        gain_close_30 = ts_gain(close, 30)
        factor = ts_levelchange(gain_close_30, 20)
        factor = ts_mean(factor, 110)

        t = df['turnover' + suffix][df['weight_boolean' + suffix]]
        tr = (2 * t.rank(axis=1, pct=True) - 1)
        factor = factor * tr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 200)
        factor = ts_mean(factor, 5)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0.2] = 0

        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc2_cfg_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc2_cfg_cr, self).__init__(required_columns=['close_zz500', 'stk_index_corr_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # as follows
        stk_close = data['close_zz500']
        a = stk_close.pct_change(3, fill_method=None)
        b = ts_mean(a, 30)
        c = ts_std(a, 30)
        factor_init = b + 0.5 * c
        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts6_spot(FactorGenerator):
    def __init__(self):
        required_columns=['volume_spot','high_spot','low_spot','close_spot']
        lookback_bars=2000
        super(wyc_ts6_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):

        
        N = 50
        a = (df['high_spot'] - df['low_spot'])
        a[abs(a) < 1e-8] = np.nan
        factor = sma(df['volume_spot'] * ((df['close_spot'] - df['low_spot']) - (df['high_spot'] - df['close_spot'])) / a, N, 1)
        factor = ts_rank_positive(factor, 100)
        factor = mean(factor, 160)

        factor = factor.to_frame()

        def rolling_normalize(df, x):
            def normalize(dd):
                a = (dd[-1] - dd.min()) / (dd.max() - dd.min())
                b = (a - 0.5) * 2
                return b

            return df.rolling(x, min_periods=int(x / 2)).apply(normalize)

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = rolling_normalize(factor, 5 * 242)
        return factor

##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc9_cfg_wr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc9_cfg_wr, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'open_zz500', 'volume_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_weight = data['weight_zz500']
        stk_weight_rank = 2 * stk_weight.rank(axis=1, pct=True) - 1

        # 假设持仓30分钟，min_30_earning表示那一分钟这笔持仓的盈亏
        stk_close = data['close_zz500']
        stk_open = data['open_zz500']
        stk_volume = data['volume_zz500']
        min_30_earning = (stk_close - stk_open.shift(30)) * stk_volume
        factor_init = min_30_earning

        factor_raw = (factor_init * stk_weight_rank).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.9] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import numpy as np

class xdy_ts6_spot_ar(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(xdy_ts6_spot_ar, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        close = df['close' + suffix]
        gain_close_30 = ts_gain(close, 30)
        factor = ts_levelchange(gain_close_30, 20)
        factor = ts_mean(factor, 110)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        ar = (2 * a.rank(axis=1, pct=True) - 1)
        factor = factor * ar
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 20)
        factor = ts_mean(factor, 15)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 10:40:21 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class OCtHL_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'open_zz500', 'high_zz500', 'amount_zz500', 'weight_boolean_zz500']

        super(OCtHL_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        stk_amount = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        temp1 = data['open_zz500'] - data['close_zz500']
        temp2 = data['high_zz500'] - data['low_zz500']
        t_pcor2 = -temp1/temp2
        t_pcor2[abs(t_pcor2)>10000] = np.nan
        t_pcor2 = t_pcor2.rolling(45, min_periods = 15).mean()#.rolling(5, min_periods = 2).mean()
        factor = (t_pcor2*stk_amount).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 1000)
        return factor
##########
from factor_generator import FactorGenerator
from operators_wsc import *
from help_functions_wsc import multi_processing_joblib



class wsc_gp10_future(FactorGenerator):
    def __init__(self):
        super(wsc_gp10_future, self).__init__(required_columns=['amount', 'close', 'recent_month_mask'],
                                             lookback_bars=2000)

    def on_bar(self, data_dict):
        # gp搜索因子，搜索时间段：20170701-20190228，验证时间段：20190301-20190630
        # 因子逻辑：成交额的波动率*过去一段时间价量背离的最大值，两者都是正向因子，逻辑合理。
        future_amount = data_dict['amount']
        future_close = data_dict['close']
        future_mask = data_dict['recent_month_mask']
        factor_raw = mul2(ts_std(future_amount, 44), ts_argmax(ts_cov(future_amount, neg(future_close), 14), 97))[future_mask].sum(axis=1)
        factor = ts_rank(factor_raw, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 17:53:22 2020

@author: appadmin
"""
from operators_cc import *
import numpy as np
from factor_generator_complex import FactorGeneratorComplex

class BS4_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['Bid1AmtMean_500', 'BuyNumOrdersSumMean_500', 'weight_500']

        super(BS4_CC, self).__init__(required_columns=required_columns)
        
    def on_bar(self, data):
        # ts_max(div(VolumeMean, position), 60).
        columnname = self.__class__.__name__
        temp1 = (data['Bid1AmtMean_500']/data['BuyNumOrdersSumMean_500']).rolling(10, min_periods = 5).mean()
        temp1[abs(temp1)>10000] = np.nan
        temp = (temp1*data['weight_500']).mean(axis = 1).to_frame()
        a2 = rolling_norm(temp, method = 'ts_rank')
        #a2.iloc[:, 0] = a2.iloc[:, 0].rolling(3, min_periods = 2).mean()
        a2.columns = [columnname]

        return a2

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
import bottleneck as bk

class wyc_ts5_future_nr_as(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'high' + suffix,'close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts5_future_nr_as, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        N = 45
        factor = pd.DataFrame(np.where((delta((ts_sum(df['close' + suffix], N) / N), N) / delay(df['close' + suffix], N))<=0.05,(-1 * (df['close' + suffix] - ts_min(df['close' + suffix], N))),(-1 * delta(df['close' + suffix], 3))),index=df['close' + suffix].index,columns=df['close' + suffix].columns)
        factor = ts_mean(ts_rank(-1*factor, 1200),15)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        factor = factor * a
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 300)
        factor = ts_mean(factor, 15)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]


        return factor
##########
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""
class retvol_zsj(FactorGenerator):
    def __init__(self):
        super(retvol_zsj, self).__init__(factor_name = 'retvol_zsj',
                                                required_columns = ['close', 'recent_month_mask'],
                                                lookback_bars = 400)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        mask = data['recent_month_mask']
        minute_ret = close/close.shift(1) - 1

        ##### calc factor #####
        """retvol"""
        vol_win = 60
        ts_pct_win = 240
        retvol_raw = minute_ret.rolling(vol_win, 1).std()
        retvol = calc_ts_pct(retvol_raw, ts_pct_win)
        retvol = retvol[mask].sum(axis=1)

        ##### format factor #####
        retvol.name = self.__class__.__name__
        factor = pd.DataFrame(retvol)
        return factor


##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=True):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk2idx_c2l_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_c2l_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'low_zz500', 'weight_boolean_zz500'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_low = data['low_zz500']
        stk_amt = data['amount_zz500']

        # factor logic
        # factor_name = 'stk2idx_c2l'
        ma_win = 30
        ts_pct_win = 2400
        roll_win_fac = 20
        min_periods = 10
        min_pct = 0.9
        stk_c2l_raw = (stk_close / stk_low - 1).rolling(roll_win_fac, min_periods).mean()
        stk2idx_c2l_raw = stk_c2l_raw[bool_mask].mean(axis=1)
        stk2idx_c2l = calc_ma_helper(stk2idx_c2l_raw, ma_win, ts_pct_win, min_pct)
        # ts_factor_quick(stk2idx_c2l,price,factor_name,layers=5)

        factor = stk2idx_c2l.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200 * 4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 13:28:00 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HL123_CC(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'recent_month_mask']

        super(HL123_CC, self).__init__(required_columns=required_columns)

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low']
        hhigh = df['high']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = ((i11-i12).rolling(20, min_periods = 2).mean())[df['recent_month_mask']]
        i2 = ts_rank(i2.mean(axis = 1).to_frame())
        i2[i2<=0] = 0
        i2.columns = [columnname]    
        return i2
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 16:48:02 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HmaxC_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'high_spot']

        super(HmaxC_ind_CC, self).__init__(
                                  required_columns=required_columns)
        

    def on_bar(self, data):

        hmhm_r = -data['high_spot'].rolling(120, min_periods = 90).max()/data['close_spot']
        hmhm_r[abs(hmhm_r)>100000] = np.nan
        factor = hmhm_r.to_frame()
  
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 1000)
        factor[factor<0]=0
        return factor
##########
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc2_cfg_vs(FactorGeneratorComplex):
    def __init__(self):
        super(wsc2_cfg_vs, self).__init__(required_columns=['close_zz500', 'stk_volatility_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']

        # as follows
        stk_close = data['close_zz500']
        a = stk_close.pct_change(3, fill_method=None)
        b = ts_mean(a, 30)
        c = ts_std(a, 30)
        factor_init = b
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc20_cfg_cr(FactorGeneratorComplex):
    def __init__(self):
        super(wsc20_cfg_cr, self).__init__(required_columns=['close_zz500', 'close_spot', 'stk_index_corr_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_zz500']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股平均波动率打分
        index_return = data['close_spot'].pct_change(periods=45, fill_method=None)
        stock_return = data['close_zz500'].pct_change(periods=45, fill_method=None)
        excess_return = stock_return.subtract(index_return, axis=0)
        excess_return_weight = corr_rank_mask[excess_return < 0].sum(axis=1)
        excess_return_weight = -ts_mean(excess_return_weight, 25)
        factor = ts_rank(excess_return_weight, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor<0] = 0
        #factor[factor>=0.5] = 0
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 10:55:03 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class L123_CC_nr_vs_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_boolean_zz500', 'low_zz500']
        super(L123_CC_nr_vs_CFG_CC, self).__init__(required_columns=required_columns
                                  )


    
    def on_bar(self, df):

        hlow = df['low_zz500']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        ii2 = rolling_norm(i2)
        stk_close = df['close_zz500']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        mask = stk_volatility[df['weight_boolean_zz500']]
        factor = (ii2*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(40, min_periods = 20).mean()
        factor = ts_rank(factor, 720)
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:33:08 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class VLSM_CC(FactorGenerator):
    def __init__(self):
        required_columns=['volume', 'recent_month_mask']
        super(VLSM_CC, self).__init__(
                                  required_columns=required_columns,
                                  )
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):

        a = data['volume'].rolling(90, min_periods = 45).mean()
        a[abs(a) < 1e-8] = np.nan
        vwap_t_r = data['volume'].rolling(60, min_periods = 25).mean()/a
        factor = (vwap_t_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factors = self.normalization(factor)
        return factors


##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np
from functools import partial
from utils_zsj import *


class stk2idx_ret_rank_short_a2p_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk2idx_ret_rank_short_a2p_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                                             lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][data['weight_boolean_zz500']]
 

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        rank_win = 30
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_ret = stk_close/stk_close.shift(1) - 1
        stk_ret_rank_short = calc_ts_pct(stk_ret,rank_win)

        score_raw = stk_ret_rank_short
        mask1 = active_mask#up_mask_duration#up_mask#
        mask2 = inactive_mask#down_mask_duration#down_mask#inactive_mask
        active_raw = score_raw[mask1].mean(axis=1)
        inactive_raw = score_raw[mask2].mean(axis=1)
        score = active_raw - inactive_raw

        ma_win = 25
        ts_pct_win = 2800
        min_pct = 0.9
        stk2idx_ret_rank_short_a2p = calc_ma_helper(score,ma_win,ts_pct_win,min_pct)

        factor = stk2idx_ret_rank_short_a2p.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np


class wyc_ts7_future_nr_vr(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'

        required_columns=['close' + suffix,'stk_volatility' + suffix]
        lookback_bars=2000
        super(wyc_ts7_future_nr_vr, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        N = 15
        factor = (sma(sma(sma(log(df['close' + suffix]), N, 2), N, 2), N, 2) - delay(
            sma(sma(sma(log(df['close' + suffix]), N, 2), N, 2), N, 2), 1)) / delay(
            sma(sma(sma(log(df['close' + suffix]), N, 2), N, 2), N, 2), 1)
        factor = ts_mean(factor, 10)

        factor = rolling_normalize(factor, 5 * 242)

        vr = (2 * df['stk_volatility' + suffix].rank(axis=1, pct=True) - 1)
        factor = factor * vr
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank_bk(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor > 0] = 0

        return factor
##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts44_future_nr_ar(FactorGeneratorComplex):
    def __init__(self):
        suffix = '_zz500'
        required_columns=['volume' + suffix,'close' + suffix,'amount' + suffix,'weight_boolean' + suffix]
        lookback_bars=2000
        super(wyc_ts44_future_nr_ar, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

    def on_bar(self, df):
        suffix = '_zz500'
        columnname = self.__class__.__name__

        temp1 = df['volume' + suffix].copy(deep = True)
        con2 = df['close' + suffix]<delay(df['close' + suffix],1)
        temp1[con2] = -1 * df['volume' + suffix]
        factor = ts_sum(temp1,20)
        factor = ts_mean(factor, 20)

        factor = rolling_norm(factor, 5 * 242)

        a = df['amount' + suffix][df['weight_boolean' + suffix]]
        ar = (2 * a.rank(axis=1, pct=True) - 1)
        factor = factor * ar
        factor = factor.sum(axis=1).to_frame()

        factor = ts_rank(factor, 20)
        factor = ts_mean(factor, 200)
        factor = ts_rank(factor, 5 * 242)
        factor.columns = [columnname]

        factor[factor < 0] = 0

        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 09:08:07 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator
import numpy as np

class DJX_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['close_spot']

        super(DJX_ind_CC, self).__init__(
                                  required_columns=required_columns)
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):

        temp5 = data['close_spot'].rolling(5, min_periods = 2).mean()
        temp10 = data['close_spot'].rolling(10, min_periods = 5).mean()
        temp20 = data['close_spot'].rolling(20, min_periods = 10).mean()
        temp60 = data['close_spot'].rolling(60, min_periods = 30).mean()
        temp120 = data['close_spot'].rolling(120, min_periods = 60).mean()
        temp5_diff = (temp5.diff()>0).astype(int)
        temp10_diff = (temp10.diff()>0).astype(int)
        temp20_diff = (temp20.diff()>0).astype(int)
        temp60_diff = (temp60.diff()>0).astype(int)
        temp120_diff = (temp120.diff()>0).astype(int)
        temp = (temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff).rolling(15, min_periods = 5).mean()
        factor = self.ts_rank(temp.to_frame())
        factor[factor<-0.5] = 0
        factor.columns = [self.__class__.__name__]
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 17:26:31 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class cmh_ae_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_zz500','amount_zz500', 'turnover_zz500', 'high_zz500', 'close_zz500']

        super(cmh_ae_CFG_CC, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, data):
        df_s = (data['amount_zz500'].rolling(120, min_periods = 15).sum())[data['weight_boolean_zz500']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        ret_30 = (data['turnover_zz500']/data['turnover_zz500'].shift(30)-1)[data['weight_boolean_zz500']]
        ret_30 = ret_30.replace([-np.inf, np.inf], np.nan)
        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)

        bool_df = temp1&temp5

        vwtc_r = data['high_zz500']-(data['close_zz500'].rolling(120, min_periods = 30).mean())
        vwtc_r = rolling_norm(vwtc_r)
        factor = (vwtc_r*bool_df).mean(axis = 1).to_frame().rolling(10, min_periods = 5).mean()
        factor = ts_rank(factor, 242)
        factor.columns = [self.__class__.__name__]
        return factor
##########
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import pandas as pd
import numpy as np


def place_back_format(dat_mat, dat_orig):
    if isinstance(dat_orig, pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat, index=dat_orig.index, columns=dat_orig.columns)
    elif isinstance(dat_orig, pd.Series):
        dat_fmt = pd.Series(dat_mat, index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt


def calc_ts_pct(ts_dat, roll_win=20, min_pct=1, force_range=True):
    min_win = int(min_pct * roll_win)
    ts_dat_pct_np = bk.move_rank(ts_dat, window=roll_win, min_count=min_win, axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1) / 2
    ts_dat_pct = place_back_format(ts_dat_pct_np, ts_dat)
    return ts_dat_pct


def calc_change_helper(score_raw, short_win, long_win, ts_pct_win, sign=1, min_pct=0.9):
    score_change_raw = sign * (
            score_raw.rolling(short_win, int(min_pct * short_win)).mean() - score_raw.rolling(long_win, int(
        min_pct * long_win)).mean())
    score_change = calc_ts_pct(score_change_raw, ts_pct_win, min_pct=min_pct)
    return score_change


def calc_std_helper(score_raw, std_win, ts_pct_win, min_pct=0.9):
    score_std_raw = score_raw.rolling(std_win, int(min_pct * std_win)).std()
    score_std = calc_ts_pct(score_std_raw, ts_pct_win)
    return score_std


def calc_ma_helper(score_raw, ma_win, ts_pct_win, min_pct=0.9):
    score_ma_raw = score_raw.rolling(ma_win, int(min_pct * ma_win)).mean()
    score_ma = calc_ts_pct(score_ma_raw, ts_pct_win, min_pct=min_pct)
    return score_ma


def ts_rank(df1, window=240):
    # 时序rolling秩
    output = pd.DataFrame(bk.move_rank(df1, window=window, min_count=int(window / 2), axis=0),
                          index=df1.index, columns=df1.columns)
    return output


class stk_l2c_a2p_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(stk_l2c_a2p_zsj, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                              lookback_bars=2000)

    def on_bar(self, data):
        ## prep data
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500'][bool_mask]

        cut_line = stk_amt.median(axis=1)
        active_mask = stk_amt.subtract(cut_line, axis=0) >= 0
        inactive_mask = stk_amt.subtract(cut_line, axis=0) < 0

        # factor logic
        # factor_name = 'stk_l2c_a2p'
        ma_win = 30
        ts_pct_win = 2400
        min_pct = 0.9
        stk_low2close_raw = stk_close.rolling(60, 30).min() / stk_close
        stk_l2c_active_raw = stk_low2close_raw[active_mask].mean(axis=1)
        stk_l2c_inactive_raw = stk_low2close_raw[inactive_mask].mean(axis=1)
        stk_l2c_a2p_raw = stk_l2c_active_raw - stk_l2c_inactive_raw
        stk_l2c_a2p = calc_ma_helper(-1 * stk_l2c_a2p_raw, ma_win, ts_pct_win, min_pct)
        # ts_factor_quick(stk_l2c_a2p,price,factor_name,layers=5)

        factor = stk_l2c_a2p.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor[columnname] = ts_rank(factor, 200 * 4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

##########
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 12:20:34 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class CDO_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['open_spot', 'close_spot']

        super(CDO_ind_CC, self).__init__(
                                  required_columns=required_columns)

    
    def on_bar(self, data):

        odc_ind_r = data['close_spot'].rolling(150, min_periods = 60).mean()-data['open_spot'].rolling(150, min_periods = 60).mean()
        factor = odc_ind_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')
        factor[factor<=-0.5] = 0
        return factor

##########
from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_ti7_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti7_cfg, self).__init__(required_columns=['close_zz500', 'open_zz500', 'high_zz500', 'low_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data_dict):
        # 大阴线技术指标，当开盘价接近最高价，收盘价显著低于开盘价且接近最低价时出现该图形，指标范围：[0, 1)，且指标值越小未来下跌概率越大，因此若close>open，则将指标值置为1.
        stk_open = data_dict['open_zz500']
        stk_high = data_dict['high_zz500']
        stk_low = data_dict['low_zz500']
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        x = stk_high - stk_low
        x[abs(x)<1e-8] = np.nan
        ratio1 = (stk_high-stk_low-abs(stk_open-stk_close)) / x
        ratio1[(stk_open-stk_close)<0] = 1
        factor_raw = (ratio1*stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor
##########
