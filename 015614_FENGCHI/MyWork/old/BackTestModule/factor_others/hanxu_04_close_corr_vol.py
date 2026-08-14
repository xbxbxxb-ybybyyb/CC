import psutil
import pandas as pd
import numpy as np
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_minute_1factor, get_daily_1factor

def _memory_used():

    info = psutil.virtual_memory()
    used = round((info.total - info.available) / 1024 ** 3, 2)
    return used

##1参数部分
#日期
start_date = 20170103
end_date = 20191231
#因子参数
roll_window = 30
#信号参数
buy_percent = 0.05
sell_percent = 0.1
ts_buy_band = 0.5
ts_sell_band = 2
#日间股票池参数
daily_corr_period = 20
daily_ret_period = 60
least_live_days = 120
least_recover_days = 5
daily_ret_low_band = 0.1
daily_ret_high_band = 0.8
pe_low_band = 0
pe_high_band = 300

##2日内因子部分
#提取数据
close = get_minute_1factor('close', get_pre_trade_date(start_date, daily_corr_period), end_date)
vol =  get_minute_1factor('vol', get_pre_trade_date(start_date, daily_corr_period), end_date)
#准备矩阵运算
index, columns = close.index[242 * daily_corr_period:].map(lambda x: x[0] * 10000 + x[1]), close.columns
close = close.values.reshape(close.shape[0] // 242, 242, close.shape[1]).transpose(2, 0, 1)
vol = vol.values.reshape(vol.shape[0] // 242, 242, vol.shape[1]).transpose(2, 0, 1)
#计算因子
x = close[..., 1: -4]
y = vol[..., 1: -4]
del close, vol

cx = np.cumsum(x, axis=-1)[..., 29:]
cy = np.cumsum(y, axis=-1)[..., 29:]
cxy = np.cumsum(x * y, axis=-1)[..., 29:]
cx2 = np.cumsum(x ** 2, axis=-1)[..., 29:]
cy2 = np.cumsum(y ** 2, axis=-1)[..., 29:]
n = np.arange(30, 238)
corr = (n * cxy - cx * cy) / np.sqrt((n * cx2 - cx ** 2) * (n * cy2 - cy ** 2))
corr[(corr == np.inf) | (corr == - np.inf)] = np.nan

#日内数据计算日间因子
daily_corr = pd.DataFrame(corr[:, :-1 ,-1].T, index=get_date_range(get_pre_trade_date(
    start_date, daily_corr_period), get_pre_trade_date(end_date)), columns=columns)
daily_corr = daily_corr.rolling(daily_corr_period).mean().iloc[daily_corr_period - 1:]

#继续计算因子
corr_fill = np.nanmedian(corr, axis=0)
corr -= corr_fill
corr[np.isnan(corr)] = 0
corr += corr_fill
score = corr[:, daily_corr_period:, :]
del x, y, cx, cy, cxy, cx2, cy2, n, corr
##3日内信号部分
#计算阈值
high_band = np.quantile(score, 1 - buy_percent, axis=0)
low_band = np.quantile(score, sell_percent, axis=0)

#计算信号
sign = np.zeros((score.shape[0], score.shape[1], 242))
sign[..., 30:-4][(score > high_band) & ((score.transpose(2, 1, 0) > ts_sell_band * daily_corr.values).transpose(2, 1, 0))] = -1
sign[..., 30:-4][(score < low_band) & ((score.transpose(2, 1, 0) < ts_buy_band * daily_corr.values).transpose(2, 1, 0))] = 1

close = get_minute_1factor('close', start_date, end_date).values.reshape(vol_refer.shape).swapaxes(0, 1)
open = get_minute_1factor('open', start_date, end_date).values.reshape(vol_refer.shape).swapaxes(0, 1)
vol_refer = vol_refer.swapaxes(0, 1)

close_bench = get_minute_1factor('close', start_date, end_date, code_list=['ZZ500'], type='bench').iloc[:, 0].values
close_bench = close_bench.reshape(close_bench.shape[0] // 242, 242).swapaxes(0, 1)
pre_close_bench = get_daily_1factor('close', get_date_range(
    get_pre_trade_date(start_date), get_pre_trade_date(end_date)), code_list=['ZZ500'], type='bench').iloc[:, 0].values
ret3 = close / pre_close - np.expand_dims(close_bench / pre_close_bench, axis=2).repeat(close.shape[2], axis=2)
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
sign = sign.transpose(2, 1, 0)
sign = (sign > 0.5) * daily_filter.values * 1 - (sign < -0.5) * 1
sign = pd.DataFrame(sign.transpose(1, 0, 2).reshape(sign.shape[0] * sign.shape[1], sign.shape[2]),
                    index=index, columns=columns)

##6测试部分
from dataApi.testFactor import FactorBackTest
from BackTestModule.QuickFactorEvaluationBackTest import FactorBackTest as FactorBackTest2

ft = FactorBackTest(start_date, end_date)
ft.evaluate(sign)
ft.result

ft2 = FactorBackTest(sign)
ft2.evaluation(23)
ft2.result_output('close_corr_vol', fileroot='/data/user/015836/')