import psutil
import pandas as pd
import numpy as np
from scipy import stats
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_minute_1factor, get_daily_1factor

def _memory_used():

    info = psutil.virtual_memory()
    used = round((info.total - info.available) / 1024 ** 3, 2)
    return used

def _fill_nan(arr):

    arr_fill = np.nanmedian(arr, axis=0)
    arr -= arr_fill
    arr[np.isnan(arr)] = 0
    arr += arr_fill
    return arr
##1参数部分
#日期
start_date = 20170103
end_date = 20191231
#因子参数
roll_window = 30
#信号参数
buy_percent = 0.1
sell_percent = 0.1
ts_buy_band = 1
ts_sell_band = 1
#日间股票池参数
daily_vol_period = 20
daily_ret_period = 60
least_live_days = 120
least_recover_days = 5
daily_ret_low_band = 0.1
daily_ret_high_band = 0.8
pe_low_band = 0
pe_high_band = 300

##2日内因子部分
#提取数据
close = get_minute_1factor('close', get_pre_trade_date(start_date, daily_vol_period), end_date)
vol =  get_minute_1factor('vol', get_pre_trade_date(start_date, daily_vol_period), end_date)
free_share = get_daily_1factor('free_float_shares', get_date_range(get_pre_trade_date(
    start_date, daily_vol_period + 1), get_pre_trade_date(end_date)))
#准备矩阵运算
index, columns = close.index[242 * daily_vol_period:].map(lambda x: x[0] * 10000 + x[1]), close.columns
close = close.values.reshape(close.shape[0] // 242, 242, close.shape[1]).transpose(2, 0, 1)
vol = vol.values.reshape(vol.shape[0] // 242, 242, vol.shape[1]).transpose(1, 0, 2)
free_share = free_share.reindex(columns=columns).values
#计算因子
dp = close[..., 1:-3] - close[..., :-4]
std = np.apply_along_axis(np.convolve, -1, close[..., :-3] ** 2, np.ones(roll_window), 'valid')
std -= np.apply_along_axis(np.convolve, -1, close[..., :-3], np.ones(roll_window), 'valid') ** 2 / roll_window
std /= roll_window - 1
std **= 0.5
dp = dp.transpose(2, 1, 0)
std = std.transpose(2, 1, 0)
dp[roll_window - 2:] /= std
dp[: roll_window - 2] /= std[0]
buy_ratio = stats.t.cdf(dp, df=0.25)
buy_ratio *= 2
buy_ratio -= 1
buy_ratio *= vol[1:-3]
buy_vol = np.nancumsum(buy_ratio, axis=0)
del dp, std, buy_ratio

vol = np.nancumsum(vol[1:-3], axis=0)
buy_vol2vol = buy_vol / vol
buy_vol2share = buy_vol / free_share
abs_buy_vol2share = np.abs(buy_vol2share)
del vol, buy_vol
#日内数据计算日间因子
daily_buy_vol2vol = pd.DataFrame(buy_vol2vol[-1], index=get_date_range(get_pre_trade_date(
    start_date, daily_vol_period), end_date), columns=columns).apply(
    lambda x: x.dropna().rolling(daily_vol_period).mean().reindex(x.index)).iloc[daily_vol_period-1:-1].ffill()

daily_buy_vol2share = pd.DataFrame(buy_vol2share[-1], index=get_date_range(get_pre_trade_date(
    start_date, daily_vol_period), end_date), columns=columns).apply(
    lambda x: x.dropna().rolling(daily_vol_period).mean().reindex(x.index)).iloc[daily_vol_period-1:-1].ffill()

daily_abs_buy_vol2share = pd.DataFrame(abs_buy_vol2share[-1], index=get_date_range(get_pre_trade_date(
    start_date, daily_vol_period), end_date), columns=columns).apply(
    lambda x: x.dropna().rolling(daily_vol_period).mean().reindex(x.index)).iloc[daily_vol_period-1:-1].ffill()

#继续计算因子
buy_vol2vol = _fill_nan(buy_vol2vol.transpose(2, 1, 0))[:, daily_vol_period:, roll_window:]
buy_vol2share = _fill_nan(buy_vol2share.transpose(2, 1, 0))[:, daily_vol_period:, roll_window:]
abs_buy_vol2share = _fill_nan(abs_buy_vol2share.transpose(2, 1, 0))[:, daily_vol_period:, roll_window:]

##3日内信号部分
#计算阈值
low_band_buy_vol2vol = np.quantile(buy_vol2vol, buy_percent, axis=0)
high_band_buy_vol2vol = np.quantile(buy_vol2vol, 1 - sell_percent, axis=0)
low_band_buy_vol2share = np.quantile(buy_vol2share, buy_percent, axis=0)
high_band_buy_vol2share = np.quantile(buy_vol2share, 1 - sell_percent, axis=0)
low_band_abs_buy_vol2share = np.quantile(abs_buy_vol2share, buy_percent, axis=0)
high_band_abs_buy_vol2share = np.quantile(abs_buy_vol2share, 1 - sell_percent, axis=0)

#计算信号
sign_buy_vol2vol = np.zeros((buy_vol2vol.shape[0], buy_vol2vol.shape[1], 242))
sign_buy_vol2vol[..., roll_window+1:-3][(buy_vol2vol > high_band_buy_vol2vol) & (
    (buy_vol2vol.transpose(2, 1, 0) > ts_sell_band * daily_buy_vol2vol.values).transpose(2, 1, 0))] = -1
sign_buy_vol2vol[..., roll_window+1:-3][(buy_vol2vol < low_band_buy_vol2vol) & (
    (buy_vol2vol.transpose(2, 1, 0) < ts_buy_band * daily_buy_vol2vol.values).transpose(2, 1, 0))] = 1

sign_buy_vol2share = np.zeros((buy_vol2share.shape[0], buy_vol2share.shape[1], 242))
sign_buy_vol2share[..., roll_window+1:-3][(buy_vol2share > high_band_buy_vol2share) & (
    ((buy_vol2share / np.arange(roll_window + 1, 239) * 239).transpose(2, 1, 0) > ts_sell_band *
     daily_buy_vol2share.values).transpose(2, 1, 0))] = -1
sign_buy_vol2share[..., roll_window+1:-3][(buy_vol2share < low_band_buy_vol2share) & (
    ((buy_vol2share / np.arange(roll_window + 1, 239) * 239).transpose(2, 1, 0) < ts_buy_band *
     daily_buy_vol2share.values).transpose(2, 1, 0))] = 1

sign_abs_buy_vol2share = np.zeros((abs_buy_vol2share.shape[0], abs_buy_vol2share.shape[1], 242))
sign_abs_buy_vol2share[..., roll_window+1:-3][(abs_buy_vol2share > high_band_abs_buy_vol2share) & (
    ((abs_buy_vol2share / np.arange(roll_window + 1, 239) * 239).transpose(2, 1, 0) > ts_sell_band *
     daily_abs_buy_vol2share.values).transpose(2, 1, 0))] = -1
sign_abs_buy_vol2share[..., roll_window+1:-3][(abs_buy_vol2share < low_band_abs_buy_vol2share) & (
    ((abs_buy_vol2share / np.arange(roll_window + 1, 239) * 239).transpose(2, 1, 0) < ts_buy_band *
     daily_abs_buy_vol2share.values).transpose(2, 1, 0))] = 1

##4日间股票池部分
#清洗股票池
daily_cleaned_stock_list = clean_stock_list(least_live_days=least_live_days, least_recover_days=least_recover_days).\
    reindex(index=get_date_range(get_pre_trade_date(start_date), get_pre_trade_date(end_date)), columns=columns)

#收益分位数
daily_adj_close = get_daily_1factor(
    factor='close_badj',
    date_list=get_date_range(get_pre_trade_date(start_date, daily_ret_period), get_pre_trade_date(end_date)),
    code_list=columns.to_list(),
)
daily_ret = daily_adj_close.pct_change(daily_ret_period).iloc[daily_ret_period-1:].fillna(0)
daily_ret_rank = daily_ret.rank(pct=True, axis=1)

#市盈率范围
daily_pe = get_daily_1factor(
    factor='pe_ttm',
    date_list=get_date_range(get_pre_trade_date(start_date), get_pre_trade_date(end_date)),
    code_list=columns.to_list(),
)

#计算日间股票池
daily_filter = (
        True
        & (daily_ret_rank > daily_ret_low_band)
        & (daily_ret_rank < daily_ret_high_band)
        & (daily_pe > pe_low_band)
        & (daily_pe < pe_high_band)
        & daily_cleaned_stock_list
)
del daily_adj_close, daily_ret, daily_ret_rank, daily_pe, daily_cleaned_stock_list

##5综合信号部分
sign_buy_vol2vol = sign_buy_vol2vol.transpose(2, 1, 0)
sign_buy_vol2vol = (sign_buy_vol2vol > 0.5) * daily_filter.values * 1 - (sign_buy_vol2vol < -0.5) * 1
sign_buy_vol2vol = pd.DataFrame(sign_buy_vol2vol.transpose(1, 0, 2).reshape(
    sign_buy_vol2vol.shape[0] * sign_buy_vol2vol.shape[1], sign_buy_vol2vol.shape[2]), index=index, columns=columns)

sign_buy_vol2share = sign_buy_vol2share.transpose(2, 1, 0)
sign_buy_vol2share = (sign_buy_vol2share > 0.5) * daily_filter.values * 1 - (sign_buy_vol2share < -0.5) * 1
sign_buy_vol2share = pd.DataFrame(sign_buy_vol2share.transpose(1, 0, 2).reshape(
    sign_buy_vol2share.shape[0] * sign_buy_vol2share.shape[1], sign_buy_vol2share.shape[2]), index=index, columns=columns)

sign_abs_buy_vol2share = sign_abs_buy_vol2share.transpose(2, 1, 0)
sign_abs_buy_vol2share = (sign_abs_buy_vol2share > 0.5) * daily_filter.values * 1 - (sign_abs_buy_vol2share < -0.5) * 1
sign_abs_buy_vol2share = pd.DataFrame(sign_abs_buy_vol2share.transpose(1, 0, 2).reshape(
    sign_abs_buy_vol2share.shape[0] * sign_abs_buy_vol2share.shape[1], sign_abs_buy_vol2share.shape[2]),
    index=index, columns=columns)

##6测试部分
from dataApi.testFactor import FactorBackTest
from BackTestModule.QuickFactorEvaluationBackTest import FactorBackTest as FactorBackTest2

ft2 = FactorBackTest2(sign_abs_buy_vol2share)
ft2.evaluation(23)
ft2.result_output('bvc_abs_buy_vol2share', fileroot='/data/user/015836/')

ft2 = FactorBackTest2(sign_buy_vol2share)
ft2.evaluation(23)
ft2.result_output('bvc_buy_vol2share', fileroot='/data/user/015836/')

ft = FactorBackTest(start_date, end_date)
ft.evaluate(sign_buy_vol2vol)
ft.result



def whether_you2_or_me2(ind_list):

    return {x: x.replace('Ⅱ', '')  for x in ind_list}