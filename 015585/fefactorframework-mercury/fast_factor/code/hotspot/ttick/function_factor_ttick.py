import numpy as np
import pandas as pd
import decimal
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
# 因子属性函数
def f_pro_rcleanb(tick_df):#相对净委买金额,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])
    return tick_df['factor']
def f_pro_cleanb2ttran(tick_df):#净委买金额/该阶段总成交额,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['ValueTrade'].sum()+1)
    return tick_df['factor']
def f_pro_cleanb2tran(tick_df):#净委买金额/tick成交额,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    cleanb2tran = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['ValueTrade']+1)
    return cleanb2tran
def f_pro_b2tran(tick_df):#委买金额/tick成交额,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['factor'] = (tick_df['buy_amt'])/(tick_df['ValueTrade']+1)
    return tick_df['factor']
def f_pro_b2ttran(tick_df):#委买金额/该阶段总成交额,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    b2ttran = (tick_df['buy_amt'])/tick_df['ValueTrade'].sum()
    return b2ttran
def f_pro_b2transtd(tick_df):#委买金额/成交的std,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    b2transtd = (tick_df['buy_amt'])/tick_df['ValueTrade'].std()
    return b2transtd
def f_pro_s2tran(tick_df):#委卖金额/tick成交额,series（开盘后）
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['sell_amt'])/(tick_df['ValueTrade']+1)
    return tick_df['factor']
def f_pro_s2ttran(tick_df):#委卖金额/该阶段总成交额,series（开盘后）
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['sell_amt'])/tick_df['ValueTrade'].sum()
    return tick_df['factor']
def f_pro_s2transtd(tick_df):#委卖金额/成交的std,series（开盘后）
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['sell_amt'])/tick_df['ValueTrade'].std()
    return tick_df['factor']
def f_pro_amt(tick_df):#成交额，series（开盘后）
    return tick_df['ValueTrade']
def f_pro_corrb2b1(tick_df):#挂买总量和买1的corr（开盘后）
    corr = pd.concat([tick_df['TotalBidQty'],tick_df['Buy1OrderQty']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_corrpv(tick_df):#成交额和价格相关性（开盘后）
    corr = pd.concat([tick_df['ValueTrade'],tick_df['LastPx']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_corrb12s1(tick_df):#挂买1和卖1的corr（开盘后）
    corr = pd.concat([tick_df['Sell1OrderQty'],tick_df['Buy1OrderQty']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_corrb2s(tick_df):#挂买1和卖1的corr（开盘后）
    corr = pd.concat([tick_df['TotalBidQty'],tick_df['TotalOfferQty']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_corrb2t(tick_df):#挂买和成交量的corr（开盘后）
    corr = pd.concat([tick_df['TotalBidQty'],tick_df['VolumeTrade']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_corrbp2bv(tick_df):#挂买均价和挂买量的corr（开盘后）
    corr = pd.concat([tick_df['WeightedAvgBidPx'],tick_df['TotalBidQty']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_corrbp2t(tick_df):#挂买均价和成交量的corr（开盘后）
    corr = pd.concat([tick_df['WeightedAvgBidPx'],tick_df['ValueTrade']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_corrb2tp(tick_df):#挂买价格和成交均价的corr（开盘后）
    corr = pd.concat([tick_df['WeightedAvgBidPx'],tick_df['ValueTrade']/
                      tick_df['VolumeTrade']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_rlength(tick_df):#长度（时间），只对“是否上涨”有效，后续要除以总长度
    return len(tick_df)
def f_pro_abspchange(tick_df):#abs(价格差分)/preclose,(开盘后)series
    tick_df['factor'] = abs(tick_df['LastPx'] - tick_df['LastPx'].shift(1))
    tick_df['factor'] = tick_df['factor'] / (tick_df['pre_close'])
    return tick_df['factor']
def f_pro_bp(tick_df):#挂买均价（开盘后），series
    return tick_df['WeightedAvgBidPx']/(tick_df['pre_close'])
def f_pro_sp(tick_df):#挂卖均价（开盘后），series
    return tick_df['WeightedAvgOfferPx']/(tick_df['pre_close'])
def f_pro_b12b(tick_df):#买1-买均（开盘后），series
    return (tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx'])/(tick_df['pre_close'])
def f_pro_b1delb(tick_df):#买1/买均（开盘后），series
    return (tick_df['Buy1Price'] / tick_df['WeightedAvgBidPx'])
def f_pro_s12s(tick_df):#卖1-卖均（开盘后），series
    return (tick_df['Sell1Price'] - tick_df['WeightedAvgOfferPx'])/(tick_df['pre_close'])
def f_pro_b12s1(tick_df):#买1-卖1（开盘后），series
    return (tick_df['Buy1Price'] - tick_df['Sell1Price'])/(tick_df['pre_close'])
def f_pro_b2s(tick_df):#买均-卖均（开盘后），series
    return (tick_df['WeightedAvgBidPx'] - tick_df['WeightedAvgOfferPx'])/(tick_df['pre_close'])
def f_pro_tran2b(tick_df):#成交-买均（开盘后），series
    return (tick_df['ValueTrade']/tick_df['VolumeTrade'] - tick_df['WeightedAvgBidPx'])/(tick_df['pre_close'])
def f_pro_vwap2p(tick_df):#vwap/最新价（开盘后）,series
    tick_df['vwap'] = tick_df['ValueTrade'].cumsum()/tick_df['VolumeTrade'].cumsum()
    return tick_df['vwap']/tick_df['LastPx']
def f_pro_syx1(tick_df):# 相对上影线：high - last / high - low，series
    tick_df['pcummax'] = tick_df['LastPx'].cummax()
    tick_df['pcummin'] = tick_df['LastPx'].cummin()
    tick_df['amp'] = tick_df['pcummax'] - tick_df['pcummin']
    tick_df['amp'] = tick_df['amp'].apply(lambda x: np.nan if abs(x)<0.0001 else x)
    tick_df['factor'] = (tick_df['pcummax'] - tick_df['LastPx'])\
                      / tick_df['amp']
    return tick_df['factor']
def f_pro_xyx1(tick_df):# 相对下影线：last - low / high - low，series
    tick_df['pcummax'] = tick_df['LastPx'].cummax()
    tick_df['pcummin'] = tick_df['LastPx'].cummin()
    tick_df['amp'] = tick_df['pcummax'] - tick_df['pcummin']
    tick_df['amp'] = tick_df['amp'].apply(lambda x: np.nan if abs(x)<0.0001 else x)
    tick_df['syx1'] = (tick_df['LastPx'] - tick_df['pcummin'])\
                      / tick_df['amp']
    return tick_df['syx1']
def f_pro_tpmin(tick_df):#价格首次最小值的时间（开盘后）
    tick_df = tick_df[tick_df['LastPx'] == tick_df['LastPx'].min()].head(1)
    return tick_df['MDTime'].mean()
def f_pro_tvwap2pmin(tick_df):#vwap/price最小值时间（开盘后）
    tick_df['vwap'] = tick_df['ValueTrade'].cumsum()/tick_df['VolumeTrade'].cumsum()
    tick_df = tick_df[(tick_df['vwap']/tick_df['LastPx']) == (tick_df['vwap']/tick_df['LastPx']).min()].head(1)
    return tick_df['MDTime'].mean()
def f_pro_ratiob(tick_df):#委买/总(开盘后),series
    return tick_df['TotalBidQty']/(tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
def f_pro_ratiob2(tick_df):#买2/买1 - 卖2/买1,series
    return tick_df['Buy2OrderQty']/(tick_df['Buy1OrderQty']+1) - tick_df['Sell2OrderQty']/(tick_df['Buy1OrderQty']+1)
def f_pro_diffb12tran(tick_df):#买1数量的差分/该tick成交量(开盘后),series
    return (tick_df['Buy1OrderQty'] - tick_df['Buy1OrderQty'].shift(1)) / (tick_df['VolumeTrade']+1)
def f_pro_b1(tick_df):#买1量，series
    return tick_df['Buy1OrderQty']
def f_pro_pb1(tick_df):#买1价，series
    return tick_df['Buy1Price']/(tick_df['pre_close'])
def f_pro_b(tick_df):#挂买总额(开盘后），后续除以市值，series
    return tick_df['WeightedAvgBidPx'] * tick_df['TotalBidQty']*1000
def f_pro_ratiob1thans1(tick_df):#买1是否离最新价更近（开盘后），series
    return np.sign(abs(tick_df['Sell1Price'] - tick_df['LastPx']) - abs(tick_df['Buy1Price'] - tick_df['LastPx']))
def f_pro_amt2newamt(tick_df):#amt/amt.tail(1)(开盘后),series
    return tick_df['ValueTrade']/(tick_df['ValueTrade'].tail(1))
def f_pro_bdiff(tick_df):#买均的一阶差分序列,series
    return (tick_df['WeightedAvgBidPx'] - tick_df['WeightedAvgBidPx'].shift(1))/tick_df['pre_close']
def f_pro_sdiff(tick_df):#卖均的一阶差分序列,series
    return (tick_df['WeightedAvgOfferPx'] - tick_df['WeightedAvgOfferPx'].shift(1))/tick_df['pre_close'].max()
def f_pro_pdiff(tick_df):#LastPx的一阶差分序列,series
    return (tick_df['LastPx'] - tick_df['LastPx'].shift(1))/tick_df['pre_close']
def f_pro_pv(tick_df):#涨幅*量,（开盘后）series
    return (tick_df['LastPx']/tick_df['pre_close']-1) * tick_df['VolumeTrade']
def f_pro_pa(tick_df):#涨幅*金额,（开盘后）series
    return (tick_df['LastPx']/tick_df['pre_close']-1) * tick_df['ValueTrade']
def f_pro_pricev(tick_df): #amt加权涨跌幅(开盘后）
    if tick_df['ValueTrade'].sum() > 10:
        p = tick_df['ValueTrade'].sum() / tick_df['VolumeTrade'].sum()
    else:
        p = np.nan
    pre_close = tick_df['pre_close'].max()
    if pre_close > 0.1:
        pct = p / pre_close - 1
        dt, ticker = tick_df.index[0]
        dt = dt.strftime('%Y%m%d')
        zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
        if zcz == 1:
            pct = pct / 2
        return pct
    else:
        return np.nan
def f_pro_t(tick_df):#时间，series
    def inttime2deltamls(itime):
        mls = int(str(int(itime))[-3:])
        s = int(str(int(itime))[-5:-3])
        m = int(str(int(itime))[-7:-5])
        h = int(str(int(itime))[:-7])
        time_mls = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + mls
        time_mls_930 = 9 * 3600 * 1000
        if int(itime) > 120000000:
            time_delta = time_mls - time_mls_930 - 5400000
        else:
            time_delta = time_mls - time_mls_930
        return time_delta
    tick_df['MDTime_delta'] = tick_df['MDTime'].apply(lambda x : inttime2deltamls(x))
    return tick_df['MDTime_delta']
def f_pro_hp(tick_df):
    return tick_df['HighPx'] / tick_df['pre_close']
def f_pro_lpcummax(tick_df):
    return tick_df['LastPx'].cummax() / tick_df['pre_close']
def f_pro_h2l(tick_df):
    return (tick_df['HighPx'] - tick_df['LowPx']) / tick_df['pre_close']
def f_pro_h2l2(tick_df):
    return (tick_df['LastPx'].cummax() - tick_df['LastPx'].cummin()) / tick_df['pre_close']
def f_pro_hlmid(tick_df):
    return 0.5*(tick_df['HighPx'] + tick_df['LowPx']) / tick_df['pre_close']
def f_pro_hlmid2lp(tick_df): # ((high + low) / 2) - lastpx
    return (0.5 * (tick_df['HighPx'] + tick_df['LowPx']) - tick_df['LastPx']) / tick_df['pre_close']
def f_pro_numtradesdiff(tick_df):
    return tick_df['NumTrades'] - tick_df['NumTrades'].shift(1).fillna(0)
def f_pro_bias5(tick_df): # 和过去15S均价的差异
    tick_df = tick_df[tick_df['LastPx']>0]
    tick_df['ma5'] = tick_df['LastPx'].rolling(5,1).mean()
    tick_df['factor'] = (tick_df['LastPx'] - tick_df['ma5'].shift(1))/tick_df['pre_close']
    return tick_df['factor']
def f_pro_pctturn(tick_df): # pct * turn
     return (tick_df['LastPx'] / tick_df['pre_close'] - 1) * tick_df['VolumeTrade'] / tick_df['ff_shares']

# 时间筛选函数，返回时间点
def f_t_kind_930(cancel_df):
    return 0
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
# tick性质筛选
# amt
def f_tick_kind1_all(tick_df):
    return (tick_df)
def f_tick_kind1_25(tick_df):#必须开盘以后
    limit = tick_df['ValueTrade'].quantile(0.25)
    tick_df = tick_df[tick_df['ValueTrade'] <= limit]
    return tick_df
def f_tick_kind1_75(tick_df):#必须开盘以后
    limit = tick_df['ValueTrade'].quantile(0.75)
    tick_df = tick_df[tick_df['ValueTrade'] >= limit]
    return tick_df
# 是否上涨
def f_tick_kind2_all(tick_df):
    return (tick_df)
def f_tick_kind2_up(tick_df):#必须开盘以后
    tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
    return tick_df
def f_tick_kind2_down(tick_df):#必须开盘以后
    tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]
    return tick_df
# 价格
def f_tick_kind3_all(tick_df):
    return 0
def f_tick_kind3_25(tick_df):
    return tick_df['LastPx'].quantile(0.25)
def f_tick_kind3_75(tick_df):
    return tick_df['LastPx'].quantile(0.75)
def get_f_p_filter(tick_df,type_p,p):
    if p > 0:
        if type_p == 'bigger':
            tick_df = tick_df[tick_df['LastPx'] > p]
        elif type_p == 'smaller':
            tick_df = tick_df[tick_df['LastPx'] < p]
        else:
            print('按价格分组未在指定范围内')
    else:
        tick_df = tick_df
    return tick_df
# 长度
def f_len_all(tick_df):
    return tick_df
def f_len_h20(tick_df):
    if len(tick_df)>20:
        return tick_df.head(20)
    else:
        return tick_df
def f_len_t20(tick_df):
    if len(tick_df)>20:
        return tick_df.tail(20)
    else:
        return tick_df
def f_len_half1(tick_df):
    if len(tick_df)>10:
        return tick_df.head(int(len(tick_df) / 2))
    else:
        return tick_df
def f_len_half2(tick_df):
    if len(tick_df)>10:
        return tick_df.tail(int(len(tick_df) / 2))
    else:
        return tick_df
# 标准化处理
def f_std_nostd(tick_df_ori,tick_df):
    return tick_df
def f_std_2length(tick_df_ori,length):
    return length / (len(tick_df_ori)+1)
# 计算序列值，仅针对因子属性得到序列的情况
def f_calc_nocalc(factor_origin):
    return factor_origin
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
        tick_series = tick_series + tick_series.min()
        return tick_series.max() / tick_series.mean() if tick_series.mean()>0 else np.nan
def f_calc_std(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.std()
