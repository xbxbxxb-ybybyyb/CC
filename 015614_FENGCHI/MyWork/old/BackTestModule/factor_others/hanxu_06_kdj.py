import psutil
import pandas as pd
import numpy as np
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_minute_1factor, get_daily_1factor

def _rolling_windows(a, window):
    """Creates rolling-window 'blocks' of length `window` from `a`.
    Note that the orientation of rows/columns follows that of pandas.
    Example
    -------
    import numpy as np
    onedim = np.arange(20)
    twodim = onedim.reshape((5,4))
    print(twodim)
    [[ 0  1  2  3]
     [ 4  5  6  7]
     [ 8  9 10 11]
     [12 13 14 15]
     [16 17 18 19]]
    print(rwindows(onedim, 3)[:5])
    [[0 1 2]
     [1 2 3]
     [2 3 4]
     [3 4 5]
     [4 5 6]]
    print(rwindows(twodim, 3)[:5])
    [[[ 0  1  2  3]
      [ 4  5  6  7]
      [ 8  9 10 11]]
     [[ 4  5  6  7]
      [ 8  9 10 11]
      [12 13 14 15]]
     [[ 8  9 10 11]
      [12 13 14 15]
      [16 17 18 19]]]
    """

    if window > a.shape[0]:
        raise ValueError(
            "Specified `window` length of {0} exceeds length of"
            " `a`, {1}.".format(window, a.shape[0])
        )
    if isinstance(a, (pd.Series, pd.DataFrame)):
        a = a.values
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    shape = (a.shape[0] - window + 1, window) + a.shape[1:]
    strides = (a.strides[0],) + a.strides
    windows = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    if windows.ndim == 1:
        windows = np.atleast_2d(windows)
    return windows

def _memory_used():

    info = psutil.virtual_memory()
    used = round((info.total - info.available) / 1024 ** 3, 2)
    return used

##1参数部分
#日期
start_date = 20170103
end_date = 20191231
#因子参数
kdj_window = 60
kdj_ewm = 3
pre_heat = 10
J_low_band = 5
J_high_band = 95
#信号参数
target_buy_num = 200
target_unsold_num = 10
refer_buy_days = 10
refer_sell_days = 10
#日间股票池参数
daily_ret_period = 60
daily_amt_period = 20
daily_report_period = 240
least_live_days = 120
least_recover_days = 5
daily_ret_low_band = 0.05
daily_ret_high_band = 0.95
pe_low_band = 0
pe_high_band = 300
price_low_band = 3
amt_low_band = 1e4
week_report_low_band = 0

##2日内因子部分
#提取数据
pre_get_days = (kdj_window + pre_heat) // 242 + 1
drop_minutes = pre_get_days * 242 - kdj_window - pre_heat + 1
close = get_minute_1factor('close_badj',
                           get_pre_trade_date(start_date, pre_get_days + refer_buy_days + refer_sell_days), end_date)
high = get_minute_1factor('high_badj',
                          get_pre_trade_date(start_date, pre_get_days + refer_buy_days + refer_sell_days), end_date)
low = get_minute_1factor('low_badj',
                         get_pre_trade_date(start_date, pre_get_days + refer_buy_days + refer_sell_days), end_date)

#准备矩阵运算
high = high.rolling(kdj_window, min_periods=2).max().iloc[kdj_window + drop_minutes - 1:]
low = low.rolling(kdj_window, min_periods=2).min().iloc[kdj_window + drop_minutes - 1:]
close = close.iloc[kdj_window + drop_minutes - 1:]
rsv = (close - low) / (high - low) * 100
rsv = rsv.replace([np.inf, -np.inf], 50)
del high, low, close
K = rsv.ewm(com=kdj_ewm - 1, min_periods=2, adjust=False).mean()
D = K.ewm(com=kdj_ewm - 1, min_periods=2, adjust=False).mean()
J = 3 * K - 2 * D
K = K.iloc[pre_heat:]
D = D.iloc[pre_heat:]
J = J.iloc[pre_heat:]

MJ = J.copy()
MJ[MJ < J_low_band] = J_low_band
MJ[MJ > J_high_band] = J_high_band
buy = MJ * (J - D).abs()
sell = - (J - D).abs() / MJ

index, columns = buy.index[(refer_buy_days + refer_sell_days) * 242:].map(
    lambda x: x[0] * 10000 + x[1]), buy.columns

#计算因子
buy = buy.values.reshape(buy.shape[0] // 242, 242, buy.shape[1]).transpose(1, 0, 2)
sell = sell.values.reshape(sell.shape[0] // 242, 242, sell.shape[1]).transpose(1, 0, 2)

##3日间股票池部分
#清洗股票池
daily_cleaned_stock_list = clean_stock_list(
    stock_list='COMMON',
    least_live_days=least_live_days,
    least_recover_days=least_recover_days,
    no_limit_down=True,
    no_limit_up=True,
).reindex(index=get_date_range(get_pre_trade_date(start_date, 1 + refer_buy_days + refer_sell_days),
                               get_pre_trade_date(end_date)), columns=columns)

#收益分位数
daily_adj_close = get_daily_1factor(
    factor='close_badj',
    date_list=get_date_range(get_pre_trade_date(start_date, refer_buy_days + refer_sell_days
                                                + daily_ret_period + 1), get_pre_trade_date(end_date)),
)
daily_ret = daily_adj_close.pct_change(daily_ret_period).iloc[daily_ret_period:].fillna(0)
daily_ret_rank = daily_ret.rank(pct=True, axis=1).reindex(columns=columns)

#市盈率范围
daily_pe = get_daily_1factor(
    factor='pe_ttm',
    date_list=get_date_range(get_pre_trade_date(start_date, 1 + refer_buy_days + refer_sell_days),
                             get_pre_trade_date(end_date)),
    code_list=columns.to_list(),
)

#股价不能低于
daily_price = get_daily_1factor(
    factor='close',
    date_list=get_date_range(get_pre_trade_date(start_date, 1 + refer_buy_days + refer_sell_days),
                             get_pre_trade_date(end_date)),
    code_list=columns.to_list(),
)

#过去20个交易日成交额中位数
daily_amt = get_daily_1factor(
    factor='amt',
    date_list=get_date_range(get_pre_trade_date(start_date, daily_amt_period + refer_buy_days + refer_sell_days),
                             get_pre_trade_date(end_date)),
    code_list=columns.to_list(),
)
daily_amt = daily_amt.rolling(daily_amt_period).median().iloc[daily_amt_period-1:]

#研报数量
daily_report_num = get_daily_1factor(
    factor='report_number7',
    date_list=get_date_range(get_pre_trade_date(start_date, daily_report_period + refer_buy_days + refer_sell_days),
                             get_pre_trade_date(end_date)),
    code_list=columns.to_list(),
)
daily_report_num = daily_report_num.rolling(daily_report_period).mean().iloc[daily_report_period-1:]

#计算日间股票池
daily_filter = (
        True
        & (daily_ret_rank > daily_ret_low_band)
        & (daily_ret_rank < daily_ret_high_band)
        & (daily_pe > pe_low_band)
        & (daily_pe < pe_high_band)
        & (daily_price > price_low_band)
        & (daily_amt > amt_low_band)
        & (daily_report_num > week_report_low_band)
        & (daily_cleaned_stock_list > 0)
)
del daily_cleaned_stock_list, daily_adj_close, daily_ret, daily_ret_rank, daily_pe, daily_price, daily_amt, daily_report_num

##4信号部分
sign_buy = buy.copy()
sign_buy[:, ~daily_filter.values] = np.nan
refer_buy_value = np.sort(np.nanmin(sign_buy[1:-4, :-1], axis=0), axis=1)[:, target_buy_num - 1]
refer_buy_value = pd.Series(refer_buy_value).rolling(refer_buy_days, min_periods=2).mean().values[refer_buy_days - 1:]
sign_buy = (sign_buy.transpose(0, 2, 1)[..., refer_buy_days:] <= refer_buy_value) * 1
sign_buy = sign_buy.transpose(1, 0, 2)
sign_buy[:, 1:-4, :][:, (sign_buy[:, 1:-4, :].cumsum(axis=1) > 0.5).sum(axis=0) > target_buy_num] = 0

sign_sell = sell[:, refer_buy_days + 1:].copy().transpose(0, 2, 1)
sign_sell[:, sign_buy[:, 1:-4, :-1].sum(axis=1) < 0.5] = np.nan
refer_sell_value = np.sort(np.nanmax(sign_sell[1:-4, :, :-1], axis=0), axis=0)[target_unsold_num - 1]
refer_sell_value = pd.Series(refer_sell_value).rolling(refer_sell_days, min_periods=2).mean().values[refer_sell_days - 1:]
sign_sell = (sign_sell[..., refer_sell_days:] >= refer_sell_value) * (-1)

sign_buy = (sign_buy[..., refer_sell_days:].transpose(2, 1, 0) > 0.5) * 1
sign_sell = (sign_sell.transpose(2, 0, 1) < -0.5) * 1
sign_buy[1:] -= sign_sell
sign = pd.DataFrame(sign_buy.reshape(sign_buy.shape[0] * sign_buy.shape[1], sign_buy.shape[2]),
                    index=index, columns=columns)
del sign_buy, sign_sell

##5测试部分
from BackTestModule.QuickFactorEvaluationBackTest import FactorBackTest as FactorBackTest

ft2 = FactorBackTest(sign)
ft2.evaluation(23)
ft2.result_output('hanxu_kdj_J_mul_abs_dj', fileroot='/data/group/800319/factorScripts/')