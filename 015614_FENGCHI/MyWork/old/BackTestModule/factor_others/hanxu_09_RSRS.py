import psutil
import pandas as pd
import numpy as np
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_minute_1factor, get_daily_1factor


def _calc_percentile(arr, back):

    _arr = arr[back-1:]
    pos = 0
    neg = 0
    for i in range(back-1):
        pos += _arr <= arr[i:-(back-1-i)]
        neg += _arr > arr[i:-(back-1-i)]
    tile = (pos + 1) / (pos + neg + 1)
    tile[(tile == np.inf) | (tile == -np.inf)] = np.nan
    return tile

def _memory_used():

    info = psutil.virtual_memory()
    used = round((info.total - info.available) / 1024 ** 3, 2)
    return used

##1参数部分
#日期
start_date = 20170103
end_date = 20191231
#因子参数
reg_window = 30
percentile_days = 5
#信号参数
target_buy_num = 150
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
pre_get_days = reg_window // 237 + 1
drop_minutes = pre_get_days * 237 - reg_window + 1
high = get_minute_1factor('high_badj', get_pre_trade_date(start_date, refer_buy_days + refer_sell_days + pre_get_days +
                                                          percentile_days), end_date)

low = get_minute_1factor('low_badj', get_pre_trade_date(start_date, refer_buy_days + refer_sell_days + pre_get_days +
                                                        percentile_days), end_date)

#准备矩阵运算
index, columns = high.index[242 * (refer_buy_days + refer_sell_days + pre_get_days + percentile_days):].map(
    lambda x: x[0] * 10000 + x[1]), high.columns
high = high.values.reshape(high.shape[0] // 242, 242, high.shape[1]).transpose(1, 0, 2)[1:-4].transpose(1, 0, 2).reshape(
    high.shape[0] // 242 * 237, high.shape[1])[drop_minutes:]
low = low.values.reshape(low.shape[0] // 242, 242, low.shape[1]).transpose(1, 0, 2)[1:-4].transpose(1, 0, 2).reshape(
    low.shape[0] // 242 * 237, low.shape[1])[drop_minutes:]

#计算因子
cx = np.apply_along_axis(np.convolve, 0, low, np.ones(reg_window), 'valid')
cy = np.apply_along_axis(np.convolve, 0, high, np.ones(reg_window), 'valid')
cxy = np.apply_along_axis(np.convolve, 0, low * high, np.ones(reg_window), 'valid')
cx2 = np.apply_along_axis(np.convolve, 0, low ** 2, np.ones(reg_window), 'valid')
rsrs = (reg_window * cxy - cx * cy) / (reg_window * cx2 - cx ** 2)
del cx, cy, cxy, cx2, high, low
rsrs = _calc_percentile(rsrs[1:], percentile_days * 237)
#rsrs = rsrs[percentile_days * 237:]
rsrs = - rsrs.reshape(rsrs.shape[0] // 237, 237, rsrs.shape[1]).transpose(1, 0, 2)

buy = np.empty((242, rsrs.shape[1], rsrs.shape[2]))
buy[1:-4] = rsrs
buy[0] = np.nan
buy[-4:] = np.nan
sell = buy.copy()

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
ft2.result_output('hanxu_RSRS', fileroot='/data/group/800319/factorScripts/')


from dataApi.testFactor import FactorBackTest
ft = FactorBackTest(start_date, end_date)
ft.evaluate(sign)
ft.result