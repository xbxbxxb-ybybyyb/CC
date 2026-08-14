import numpy as np
import pandas as pd
import decimal
import datetime as dt
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
def fun_get_time(time1,sec_delta):
    tmp_time = dt.datetime.strptime(str(time1)[:-3],'%H%M%S')
    tmp_time2 = tmp_time+dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
    if (int(tmp_time2_str)>113000000)&(time1<=113000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<130000000)&(time1>=130000000):
        adj_tmp_time2 = tmp_time2-dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<93000000)&(time1>=93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif (time1<93000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=4*60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)
# 因子属性函数
def f_pro_amt(trade_df):#
    trade_df['factor'] = trade_df['TradeAmt']
    return trade_df
def f_pro_amt2mv(trade_df):#
    trade_df['factor'] = trade_df['TradeAmt'] / trade_df['pre_close'] / trade_df['ff_shares']
    return trade_df
def f_pro_vol(trade_df):#
    trade_df['factor'] = trade_df['TradeQty']
    return trade_df
def f_pro_pct(trade_df):#
    trade_df['factor'] = trade_df['TradePrice'] / trade_df['pre_close'] - 1
    return trade_df
def f_pro_vwappct(trade_df):#
    trade_df['factor'] = trade_df['TradeAmt'].cumsum() / trade_df['TradeQty'].cumsum() / trade_df['pre_close'] - 1
    return trade_df
def f_pro_buypctdiff(trade_df):
    trade_df['max_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('max')
    trade_df['min_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('min')
    trade_df['factor'] = (trade_df['max_price'] - trade_df['min_price'])/trade_df['pre_close']
    return trade_df
def f_pro_amt2buypctdiff(trade_df):
    trade_df['max_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('max')
    trade_df['min_price'] = trade_df.groupby('TradeBuyNo')['TradePrice'].transform('min')
    trade_df['factor'] = trade_df['TradeAmt'] / ((trade_df['max_price'] + 1e-2 - trade_df['min_price'])/trade_df['pre_close'])
    return trade_df
# 时间筛选函数，返回时间点
def f_t_kind_930(trade_df):
    return 93000000
def f_t_kind_30s(trade_df):
    max_time = trade_df['MDTime'].max()
    res = fun_get_time(max_time,-30)
    return res
def f_t_kind_1m(trade_df):
    max_time = trade_df['MDTime'].max()
    res = fun_get_time(max_time,-60)
    return res
def f_t_kind_3m(trade_df):
    max_time = trade_df['MDTime'].max()
    res = fun_get_time(max_time,-180)
    return res
def get_f_t_filter(trade_df,t):
    trade_df = trade_df[trade_df['MDTime'] < 145700000]
    trade_df = trade_df[trade_df['MDTime'] >= t]
    return trade_df

# trade性质筛选
## bs
def f_bs_allbs(trade_df):
    return (trade_df)
def f_bs_buy(trade_df):
    trade_df = trade_df[trade_df['TradeBSFlag'] == 1]
    return trade_df
def f_bs_sell(trade_df):
    trade_df = trade_df[trade_df['TradeBSFlag'] == 2]
    return trade_df

## price
def f_price_allp(trade_df):
    return (trade_df)
def f_price_up9(trade_df):
    price9 = trade_df['pre_close'] * 1.09
    trade_df = trade_df[trade_df['TradePrice'] >= price9]
    return trade_df
def f_price_down9(trade_df):
    price9 = trade_df['pre_close'] * 1.09
    trade_df = trade_df[trade_df['TradePrice'] < price9]
    return trade_df
## 订单金额
def f_amt_allamt(trade_df):
    return trade_df
def f_amt_big(trade_df):
    groupby_buy = trade_df.groupby('TradeBuyNo')['TradeAmt'].sum()
    groupby_buy = groupby_buy[groupby_buy >= 200000]
    big_buy_list = list(groupby_buy.index)
    trade_df = trade_df[trade_df['TradeBuyNo'].isin(big_buy_list)]
    return trade_df
def f_amt_small(trade_df):
    groupby_buy = trade_df.groupby('TradeBuyNo')['TradeAmt'].sum()
    groupby_buy = groupby_buy[groupby_buy < 50000]
    small_buy_list = list(groupby_buy.index)
    trade_df = trade_df[trade_df['TradeBuyNo'].isin(small_buy_list)]
    return trade_df
# 长度
def f_len_all(trade_df):
    return trade_df
def f_len_t50(trade_df):
    if len(trade_df)>50:
        return trade_df.tail(50)
    else:
        return trade_df
def f_len_t100(trade_df):
    if len(trade_df)>100:
        return trade_df.tail(100)
    else:
        return trade_df
def f_len_t300(trade_df):
    if len(trade_df)>300:
        return trade_df.tail(300)
    else:
        return trade_df
# 模式1
def f_mode1_alldf(trade_df):
    return [trade_df]
def f_mode1_bsdf(trade_df):
    trade_df1 = trade_df[trade_df['TradeBSFlag'] == 1]
    trade_df2 = trade_df[trade_df['TradeBSFlag'] == 2]
    return [trade_df1, trade_df2]
def f_mode1_lendf1(trade_df):
    trade_df1 = trade_df.tail(100)
    trade_df2 = trade_df.iloc[:-100]
    return [trade_df1, trade_df2]
def f_mode1_lendf2(trade_df):
    trade_df1 = trade_df.tail(100)
    trade_df2 = trade_df.tail(1000)
    return [trade_df1, trade_df2]
def f_mode1_pricedf1(trade_df):
    trade_df1 = trade_df[trade_df['TradePrice'] / trade_df['pre_close'] >= 1.09]
    trade_df2 = trade_df[trade_df['TradePrice'] / trade_df['pre_close'] < 1.09]
    return [trade_df1, trade_df2]

# 模式2
def f_mode2_calc(trade_df_list):
    return trade_df_list
def f_mode2_calcbuybs(trade_df_list):
    if len(trade_df_list) != 1:
        print('error trade_df_list != 1，请检查循环中的continuep判断')
        raise TypeError
    else:
        trade_df = trade_df_list[0]
        trade_df = trade_df.groupby('TradeBuyNo')['factor','TradeMoney'].sum()
        trade_df1 = trade_df[trade_df['TradeMoney'] >= 200000]
        trade_df2 = trade_df[trade_df['TradeMoney'] < 50000]
    return [trade_df1, trade_df2]

def f_mode2_gbuy(trade_df_list):
    res = []
    for trade_df in trade_df_list:
        trade_df = trade_df.groupby('TradeBuyNo')['factor'].sum().to_frame(name = 'factor')
        res.append(trade_df)
    return res
def f_mode2_gsell(trade_df_list):
    res = []
    for trade_df in trade_df_list:
        trade_df = trade_df.groupby('TradeSellNo')['factor'].sum().to_frame(name = 'factor')
        res.append(trade_df)
    return res
# 计算函数
def f_calc_max(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.max()
def f_calc_min(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.min()
def f_calc_avg(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.mean()
def f_calc_med(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.median()
def f_calc_cv(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        if  abs(tick_series.mean()) > 0.0001:
            return tick_series.std() / tick_series.mean()
        else:
            return np.nan
def f_calc_sum(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.sum()
def f_calc_cct(tick_series):
    if abs(tick_series.sum()) > 0.001:
        return (tick_series**2).sum() / (tick_series.sum())**2
    else:
        return np.nan
def f_calc_skew(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.skew()
def f_calc_kurt(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.kurt()
def f_calc_change(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.head(1).mean() - tick_series.tail(1).mean()
def f_calc_tail(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.tail(1).mean()
def f_calc_m2m(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.max() / tick_series.mean() if (tick_series.min() >= 0 or tick_series.max() <= 0) else np.nan
def f_calc_std(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.std()
def f_calc_length(tick_series):
    return len(tick_series)