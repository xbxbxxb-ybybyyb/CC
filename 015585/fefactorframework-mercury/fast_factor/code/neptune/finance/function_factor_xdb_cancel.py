import numpy as np
import pandas as pd
import decimal

def get_time_delta(itime):
    mls = int(str(int(itime))[-3:])
    s = int(str(int(itime))[-5:-3])
    m = int(str(int(itime))[-7:-5])
    h = int(str(int(itime))[:-7])
    time_mls = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + mls
    time_mls_900 = 9 * 3600 * 1000
    if int(itime) > 120000000:
        time_delta = time_mls - time_mls_900 - 5400000
    else:
        time_delta = time_mls - time_mls_900
    return time_delta
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
# 因子属性函数
def f_pro_amt(cancel_df):
    cancel_df['OrderAmt'] = cancel_df['OrderPrice'] * cancel_df['OrderQty']
    return cancel_df['OrderAmt']
def f_pro_length(cancel_df):
    return len(cancel_df)
def f_pro_corr_pv(cancel_df):
    corr = pd.concat([cancel_df['OrderPrice'],cancel_df['OrderQty']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_price_v(cancel_df):
    pre_close = cancel_df['pre_close'].max()
    if cancel_df['OrderQty'].sum() > 10:
        p = (cancel_df['OrderPrice'] * cancel_df['OrderQty']).sum() / cancel_df['OrderQty'].sum()
    else:
        p = np.nan
    return p / pre_close - 1
def f_pro_t(cancel_df):
    return cancel_df['MDTime_delta']
def f_pro_index(cancel_df):
    return cancel_df['OrderIndex']
def f_pro_buynumratio(cancel_df):# 买单数量占比,非Series
    return len(cancel_df[cancel_df['OrderBSFlag']==1]) / (len(cancel_df)+1)
def f_pro_buyamtratio(cancel_df):# 买单金额占比,非Series
    cancel_df['OrderAmt'] = cancel_df['OrderPrice'] * cancel_df['OrderQty']
    return cancel_df[cancel_df['OrderBSFlag']==1]['OrderAmt'].sum() / (cancel_df['OrderAmt'].sum()+1)
def f_pro_bigratio(cancel_df):# 大单金额占比
    cancel_df['OrderAmt'] = cancel_df['OrderPrice'] * cancel_df['OrderQty']
    return cancel_df[cancel_df['OrderAmt'] >= 200000]['OrderAmt'].sum() / (cancel_df['OrderAmt'].sum() + 1)
def f_pro_price(cancel_df):#挂单价格
    cancel_df['factor'] = cancel_df['OrderPrice']/cancel_df['pre_close']
    return cancel_df['factor']
def f_pro_price1(cancel_df):#挂单价格/到目前为止的挂单vwap均价
    cancel_df['OrderAmt'] = cancel_df['OrderPrice'] * cancel_df['OrderQty']
    cancel_df['OrderAmtsum'] = cancel_df['OrderAmt'].cumsum()
    cancel_df['OrderQtysum'] = cancel_df['OrderQty'].cumsum()
    cancel_df['vwap'] = cancel_df['OrderAmtsum'] / cancel_df['OrderQtysum']
    cancel_df['factor'] = cancel_df['OrderPrice']/cancel_df['vwap']
    return cancel_df['factor']
# 时间筛选函数，返回时间点
def f_t_kind_930(cancel_df):
    return 0
def f_t_kind_1000(tick_df):
    return 30*60*1000
def f_t_kind_1430(tick_df):
    return 7*30*60*1000
def f_t_kind_tfzt(tick_df):
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['LastPx'] >= tick_df['LastPx'].max()]
    x = tick_df['MDTime'].min()
    return get_time_delta(x) - 1800000
def f_t_kind_tlzt(tick_df):
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[(tick_df['LastPx'] == tick_df['LastPx'].max())
                      & (tick_df['LastPx'] > tick_df['LastPx'].shift(1))]
    x = tick_df['MDTime'].max()
    return get_time_delta(x) - 1800000
def f_t_kind_tail30(cancel_df):
    t_max = cancel_df['MDTime_delta'].max()
    t = t_max - 30*1000
    return t
def f_t_kind_tail60(cancel_df):
    t_max = cancel_df['MDTime_delta'].max()
    t = t_max - 60*1000
    return t
def get_f_t_filter(cancel_df,type_t,t):
    if type_t == 'before':
        cancel_df = cancel_df[cancel_df['MDTime_delta'] < t]
    elif type_t == 'after':
        cancel_df = cancel_df[cancel_df['MDTime_delta'] >= t]
    if t != 0: # 一般不包括集合竞价
        cancel_df = cancel_df[cancel_df['MDTime_delta'] >= 0]
    return cancel_df
# 订单性质筛选
# 买卖
def f_cancel_kind1_all(cancel_df):
    return cancel_df
def f_cancel_kind1_buy(cancel_df):
    return (cancel_df[cancel_df['OrderBSFlag'] == 1])
def f_cancel_kind1_sell(cancel_df):
    return (cancel_df[cancel_df['OrderBSFlag'] == 2])
# 大小
def f_cancel_kind2_all(cancel_df):
    return cancel_df
def f_cancel_kind2_big(cancel_df):
    cancel_df['OrderAmt'] = cancel_df['OrderQty'] * cancel_df['OrderPrice']
    return cancel_df[cancel_df['OrderAmt'] > 200000]
def f_cancel_kind2_small(cancel_df):
    cancel_df['OrderAmt'] = cancel_df['OrderQty'] * cancel_df['OrderPrice']
    return cancel_df[cancel_df['OrderAmt'] < 50000]
# 价格
def f_cancel_kind3_all(cancel_df):
    return 0
def f_cancel_kind3_zt(cancel_df):
    pre_close = round(cancel_df['pre_close'].mean(),3)
    p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    return p_zt
def f_cancel_kind3_9(cancel_df):
    pre_close = round(cancel_df['pre_close'].mean(), 3)
    p = pre_close * 1.09
    return p
def f_cancel_kind3_95(cancel_df):
    pre_close = round(cancel_df['pre_close'].mean(),3)
    p = pre_close * 1.095
    return p
def f_cancel_kind3_98(cancel_df):
    pre_close = round(cancel_df['pre_close'].mean(),3)
    p = pre_close * 1.098
    return p
def get_f_p_filter(cancel_df,type_p,p):
    if p > 0:
        if type_p == 'bigger':
            cancel_df = cancel_df[cancel_df['OrderPrice'] >= p]
        elif type_p == 'smaller':
            cancel_df = cancel_df[cancel_df['OrderPrice'] < p]#不能取等号，否则涨停价会有问题
        else:
            print('按价格分组未在指定范围内')
    else:
        cancel_df = cancel_df
    return cancel_df
# 长度
def f_len_all(cancel_df):
    return cancel_df
def f_len_h500(cancel_df):
    if len(cancel_df)>500:
        return cancel_df.head(500)
    else:
        return cancel_df
def f_len_t500(cancel_df):
    if len(cancel_df)>500:
        return cancel_df.tail(500)
    else:
        return cancel_df
def f_len_t100(cancel_df):
    if len(cancel_df)>100:
        return cancel_df.tail(100)
    else:
        return cancel_df
def f_len_half1(cancel_df):
    if len(cancel_df)>10:
        return cancel_df.head(int(len(cancel_df) / 2))
    else:
        return cancel_df
def f_len_half2(cancel_df):
    if len(cancel_df)>10:
        return cancel_df.tail(int(len(cancel_df) / 2))
    else:
        return cancel_df
def f_len_t1min(cancel_df):
    return cancel_df[cancel_df['MDTime_delta'] >= (cancel_df['MDTime_delta'].max() - 60*1000)]
# 标准化处理，仅对成交量
def f_std_nostd(cancel_df,cancel_amt):
    return cancel_amt
def f_std_2mv(cancel_df,cancel_amt):
    mv = cancel_df['pre_close'].max() * cancel_df['ff_shares'].max()
    if mv > 10:
        return cancel_amt / mv
    else:
        return np.nan
def f_std_2ttl(cancel_df,cancel_amt):
    cancel_df = cancel_df[cancel_df['MDTime'] >= 93000000]
    tran_ttl = (cancel_df['OrderQty'] * cancel_df['OrderPrice']).sum()
    if tran_ttl > 0:
        return cancel_amt / tran_ttl
    else:
        return np.nan
# 标准化处理,计算序列值，仅针对因子属性得到序列的情况
def f_calc_nocalc(factor_origin):
    return factor_origin
def f_calc_max(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.max()
def f_calc_min(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.min()
def f_calc_avg(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.mean()
def f_calc_med(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.median()
def f_calc_cv(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        if  abs(cancel_series.mean()) > 0.0001:
            return cancel_series.std() / cancel_series.mean()
        else:
            return np.nan
def f_calc_sum(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.sum()
def f_calc_cct(cancel_series):
    if abs(cancel_series.sum()) > 0.001:
        return (cancel_series**2).sum() / (cancel_series.sum())**2
    else:
        return np.nan
def f_calc_skew(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.skew()
def f_calc_kurt(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.kurt()
def f_calc_change(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.head(1).mean() - cancel_series.tail(1).mean()
def f_calc_tail(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.tail(1).mean()
def f_calc_m2m(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        cancel_series = cancel_series + cancel_series.min()
        return cancel_series.max() / cancel_series.mean() if cancel_series.mean()>0 else np.nan
def f_calc_std(cancel_series):
    if cancel_series.empty:
        return np.nan
    else:
        return cancel_series.std()