# 因子自动书写
import os

from run_factor_demo import run_factor
from project_2_factor_test_origin import pj2FactorTest
import pandas as pd
import numpy as np
# 因子属性函数
def f_pro_rcleanb(tick_df):#相对净委买金额,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    rcleanb = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])
    return rcleanb
def f_pro_cleanb2ttran(tick_df):#净委买金额/该阶段总成交额,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    cleanb2ttran = (tick_df['buy_amt'] - tick_df['sell_amt'])/tick_df['ValueTrade'].sum()
    return cleanb2ttran
def f_pro_cleanb2tran(tick_df):#净委买金额/tick成交额,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    cleanb2tran = (tick_df['buy_amt'] - tick_df['sell_amt'])/tick_df['ValueTrade']
    return cleanb2tran
def f_pro_b2tran(tick_df):#委买金额/tick成交额,series（开盘后）
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    b2tran = (tick_df['buy_amt'])/tick_df['ValueTrade']
    return b2tran
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
    s2tran = (tick_df['sell_amt'])/tick_df['ValueTrade']
    return s2tran
def f_pro_s2ttran(tick_df):#委卖金额/该阶段总成交额,series（开盘后）
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    s2ttran = (tick_df['sell_amt'])/tick_df['ValueTrade'].sum()
    return s2ttran
def f_pro_s2transtd(tick_df):#委卖金额/成交的std,series（开盘后）
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    s2transtd = (tick_df['sell_amt'])/tick_df['ValueTrade'].std()
    return s2transtd
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
    absp = abs(tick_df['LastPx'] - tick_df['LastPx'].shift(1))
    absp = absp / (tick_df['pre_close'].max())
    return absp
def f_pro_bp(tick_df):#挂买均价（开盘后），series
    return tick_df['WeightedAvgBidPx']/(tick_df['pre_close'].max())
def f_pro_sp(tick_df):#挂卖均价（开盘后），series
    return tick_df['WeightedAvgOfferPx']/(tick_df['pre_close'].max())
def f_pro_b12b(tick_df):#买1-买均（开盘后），series
    return (tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx'])/(tick_df['pre_close'].max())
def f_pro_s12s(tick_df):#卖1-卖均（开盘后），series
    return (tick_df['Sell1Price'] - tick_df['WeightedAvgOfferPx'])/(tick_df['pre_close'].max())
def f_pro_b12s1(tick_df):#买1-卖1（开盘后），series
    return (tick_df['Buy1Price'] - tick_df['Sell1Price'])/(tick_df['pre_close'].max())
def f_pro_b2s(tick_df):#买均-卖均（开盘后），series
    return (tick_df['WeightedAvgBidPx'] - tick_df['WeightedAvgOfferPx'])/(tick_df['pre_close'].max())
def f_pro_tran2b(tick_df):#成交-买均（开盘后），series
    return (tick_df['ValueTrade']/tick_df['VolumeTrade'] - tick_df['WeightedAvgBidPx'])/(tick_df['pre_close'].max())
def f_pro_vwap2p(tick_df):#vwap/最新价（开盘后）,series
    tick_df['vwap'] = tick_df['ValueTrade'].cumsum()/tick_df['VolumeTrade'].cumsum()
    return tick_df['vwap']/tick_df['LastPx']
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
    return tick_df['Buy2OrderQty']/tick_df['Buy1OrderQty'] - tick_df['Sell2OrderQty']/tick_df['Buy1OrderQty']
def f_pro_diffb12tran(tick_df):#买1数量的差分/该tick成交量(开盘后),series
    return (tick_df['Buy1OrderQty'] - tick_df['Buy1OrderQty'].shift(1)) / tick_df['VolumeTrade']
def f_pro_b1(tick_df):#买1量，series
    return tick_df['Buy1OrderQty']
def f_pro_pb1(tick_df):#买1价，series
    return tick_df['Buy1Price']/(tick_df['pre_close'].max())
def f_pro_b(tick_df):#挂买总额(开盘后），后续除以市值，series
    return tick_df['WeightedAvgBidPx'] * tick_df['TotalBidQty']*1000
def f_pro_ratiob1thans1(tick_df):#买1是否离最新价更近（开盘后），series
    return np.sign(abs(tick_df['Sell1Price'] - tick_df['LastPx']) - abs(tick_df['Buy1Price'] - tick_df['LastPx']))
def f_pro_amt2newamt(tick_df):#amt/amt.tail(1)(开盘后),series
    return tick_df['ValueTrade']/(tick_df['ValueTrade'].tail(1))
def f_pro_pv(tick_df):#涨幅*量,（开盘后）series
    return (tick_df['LastPx']/tick_df['pre_close'].max()-1) * tick_df['VolumeTrade']
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
# 时间筛选函数，返回时间点
def f_t_kind_930(tick_df):
    return 93000000
def get_f_t_filter(tick_df,type_t,t):
    if type_t == 'before':
        tick_df = tick_df[tick_df['MDTime'] < t]
    elif type_t == 'after':
        tick_df = tick_df[tick_df['MDTime'] >= t]
    if t != 93000000: # 一般不包括集合竞价
        tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    return tick_df
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
#
# 后续处理
# 标准化处理
def f_std_nostd(tick_df_ori,tick_df):
    return tick_df
def f_std_2length(tick_df_ori,length):
    return length / len(tick_df_ori)
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
# 参数设置
dic_property = {
                # 'rcleanb':f_pro_rcleanb,
                # 'cleanb2ttran':f_pro_cleanb2ttran,
                # 'cleanb2tran':f_pro_cleanb2tran,
                # 'b2tran':f_pro_b2tran,
                # 'b2ttran':f_pro_b2ttran,
                # 'b2transtd':f_pro_b2transtd,
                # 's2tran':f_pro_s2tran,
                # 's2ttran':f_pro_s2ttran,
                # 's2transtd':f_pro_s2transtd,
                # 'amt':f_pro_amt,
                # 'corrb2b1':f_pro_corrb2b1,
                # 'corrpv':f_pro_corrpv,
                # 'corrb12s1':f_pro_corrb12s1,
                # 'corrb2s':f_pro_corrb2s,
                # 'corrb2t':f_pro_corrb2t,
                # 'corrbp2bv':f_pro_corrbp2bv,
                # 'corrbp2t':f_pro_corrbp2t,
                # 'corrb2tp':f_pro_corrb2tp,
                # 'rlength':f_pro_rlength,
                # 'abspchange':f_pro_abspchange,
                # 'bp':f_pro_bp,
                # 'sp':f_pro_sp,
                # 'b12b':f_pro_b12b,
                # 's12s':f_pro_s12s,
                # 'b12s1':f_pro_b12s1,
                # 'b2s':f_pro_b2s,
                # 'tran2b':f_pro_tran2b,
                # 'vwap2p':f_pro_vwap2p,
                # 'tpmin':f_pro_tpmin,
                # 'tvwap2pmin':f_pro_tvwap2pmin,
                # 'ratiob':f_pro_ratiob,
                # 'ratiob2':f_pro_ratiob2,
                # 'diffb12tran':f_pro_diffb12tran,
                # 'b1':f_pro_b1,
                # 'pb1':f_pro_pb1,
                # 'b':f_pro_b,
                # 'ratiob1thans1':f_pro_ratiob1thans1,
                # 'amt2newamt':f_pro_amt2newamt,
                # 'pv':f_pro_pv,
                'pricev':f_pro_pricev,
                # 't':f_pro_t
               }
dic_time_kind = {
                 '930':f_t_kind_930,
                }
time_type = ['before','after']
dic_tick_kind1 = {'all':f_tick_kind1_all,
                   'amt25':f_tick_kind1_25,
                   'amt75':f_tick_kind1_75}# amt
dic_tick_kind2 = {'all':f_tick_kind2_all,
                   'up':f_tick_kind2_up,
                   'down':f_tick_kind2_down}# up&down
dic_tick_kind3 = {
                   '0':f_tick_kind3_all,
                   'p25':f_tick_kind3_25,
                   'p75':f_tick_kind3_75
                   }# 价格单
tick_type3 = ['bigger','smaller']
dic_len_type = {'all':f_len_all,
                'h500':f_len_h20,
                't500':f_len_t20,
                'half1':f_len_half1,
                'half2':f_len_half2
               }
dic_std = {'nostd':f_std_nostd,
           '2length':f_std_2length,
          }
dic_calc = {'nocalc':f_calc_nocalc,
            'max':f_calc_max,
#             'min':f_calc_min,
            'avg':f_calc_avg,
            # 'med':f_calc_med,
            'cv':f_calc_cv,
            'sum':f_calc_sum,
            'cct':f_calc_cct,
            'skew':f_calc_skew,
            'kurt':f_calc_kurt,
            'change':f_calc_change,
            'tail':f_calc_tail,
           }
dic_compare = [
               'nocompare',
               'compare_t',
               'compare_1',
               'compare_2',
               'compare_3',
               'compare_len_h2t',
               'compare_len_half12']
# 主体函数
def generate_factor(tick_df,
                    property_i,
                    time_kind_i,
                    time_type_i,
                    tick_kind1_i,
                    tick_kind2_i,
                    tick_kind3_i,
                    tick_type3_i,
                    len_type_i,
                    std_i,
                    calc_i):
    # 新增tick成交额、成交量列
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    # 筛选时间
    t = dic_time_kind[time_kind_i](tick_df)
    tick_df_t = get_f_t_filter(tick_df,time_type_i,t)
    # 筛选amt
    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
    # 筛选up&down
    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
    # 筛选tick价格
    p = dic_tick_kind3[tick_kind3_i](tick_df)
    if p > 0:
        tick_df_t_3 = get_f_p_filter(tick_df_t_2,tick_type3_i,p)
    else:
        tick_df_t_3 = tick_df_t_2.copy()
    # 筛选长度
    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_3)
    # 因子属性
    factor_origin = dic_property[property_i](tick_df_t_len)
    # 如果是amt,尝试标准化
    if (property_i == 'rlength'):
        factor_origin = dic_std[std_i](tick_df,factor_origin)
    # 计算最终结果
    if type(factor_origin) == pd.Series:
        factor = dic_calc[calc_i](factor_origin)
    else:
        factor = factor_origin
    return factor
'''
时间上前后对比，只有时间 = before
买卖单前后对比，只有all
大小单同理
价格订单，p=0不行，其他可以，只有bigger
len订单，只有h500和half1可以
'''
def generate_factor_addcompare(tick_df,
                               property_i,
                               time_kind_i,
                               time_type_i,
                               tick_kind1_i,
                               tick_kind2_i,
                               tick_kind3_i,
                               tick_type3_i,
                               len_type_i,
                               std_i,
                               calc_i,
                               compare_i):
    if compare_i == 'nocompare':
        value = generate_factor(tick_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                tick_kind1_i,
                                tick_kind2_i,
                                tick_kind3_i,
                                tick_type3_i,
                                len_type_i,
                                std_i,
                                calc_i)
    elif (compare_i == 'compare_t') & (time_type_i == 'before'):
        value_1 = generate_factor(tick_df,
                                    property_i,
                                    time_kind_i,
                                    'before',
                                    tick_kind1_i,
                                    tick_kind2_i,
                                    tick_kind3_i,
                                    tick_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value_2 = generate_factor(tick_df,
                                    property_i,
                                    time_kind_i,
                                    'after',
                                    tick_kind1_i,
                                    tick_kind2_i,
                                    tick_kind3_i,
                                    tick_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value = value_1 - value_2
    elif (compare_i == 'compare_1') & (tick_kind1_i == 'all'):
        value_1 = generate_factor(tick_df,
                                    property_i,
                                    time_kind_i,
                                    time_type_i,
                                    'amt25',
                                    tick_kind2_i,
                                    tick_kind3_i,
                                    tick_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value_2 = generate_factor(tick_df,
                                    property_i,
                                    time_kind_i,
                                    time_type_i,
                                    'amt75',
                                    tick_kind2_i,
                                    tick_kind3_i,
                                    tick_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value = value_1 - value_2
    elif (compare_i == 'compare_2') & (tick_kind2_i == 'all'):
        value_1 = generate_factor(tick_df,
                                    property_i,
                                    time_kind_i,
                                    time_type_i,
                                    tick_kind1_i,
                                    'up',
                                    tick_kind3_i,
                                    tick_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value_2 = generate_factor(tick_df,
                                    property_i,
                                    time_kind_i,
                                    time_type_i,
                                    tick_kind1_i,
                                    'down',
                                    tick_kind3_i,
                                    tick_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value = value_1 - value_2
    elif (compare_i == 'compare_3') & (tick_kind3_i != '0') & (tick_type3_i == 'bigger'):
        value_1 = generate_factor(tick_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                tick_kind1_i,
                                tick_kind2_i,
                                tick_kind3_i,
                                'bigger',
                                len_type_i,
                                std_i,
                                calc_i)
        value_2 = generate_factor(tick_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                tick_kind1_i,
                                tick_kind2_i,
                                tick_kind3_i,
                                'smaller',
                                len_type_i,
                                std_i,
                                calc_i)
        value = value_1 - value_2
    elif (compare_i == 'compare_len_h2t') & (len_type_i == 'h500'):
        value_1 = generate_factor(tick_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                tick_kind1_i,
                                tick_kind2_i,
                                tick_kind3_i,
                                tick_type3_i,
                                'h500',
                                std_i,
                                calc_i)
        value_2 = generate_factor(tick_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                tick_kind1_i,
                                tick_kind2_i,
                                tick_kind3_i,
                                tick_type3_i,
                                't500',
                                std_i,
                                calc_i)
        value = value_1 - value_2
    elif (compare_i == 'compare_len_half12') & (len_type_i == 'half1'):
        value_1 = generate_factor(tick_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                tick_kind1_i,
                                tick_kind2_i,
                                tick_kind3_i,
                                tick_type3_i,
                                'half1',
                                std_i,
                                calc_i)
        value_2 = generate_factor(tick_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                tick_kind1_i,
                                tick_kind2_i,
                                tick_kind3_i,
                                tick_type3_i,
                                'half2',
                                std_i,
                                calc_i)
        value = value_1 - value_2
    else:
        raise ValueError('出现了不允许的compare因子')
    return value
# 高相关因子的字符串拼接
def get_str_corr_factor(df):
    str_ = ''
    for i in df.index:
        str_ += i
        str_ += ':'
        str_ += str(round(df.loc[i,'factor_corr'],2))
        str_ += ','
    return str_
# 因子测试结果写入df
def write_excel(result_df):
    result_df.loc[factor_name,'factor_name'] = factor_name
    result_df.loc[factor_name,'IC'] = factor_test.result_dic['corr_sta'].loc['corr_tot','value']
    result_df.loc[factor_name,'info'] = factor_test.result_dic['corr_sta'].loc['mic_tot','value']
    result_df.loc[factor_name,'score'] = factor_test.result_dic['check_score_res'].loc['score','tot_score']
    result_df.loc[factor_name,'corr_other'] = get_str_corr_factor(factor_test.result_dic['factor_corr_summary'])
    result_df.loc[factor_name,'repeat'] = factor_test.result_dic['other_sta']['same_rate'][0]
    result_df.loc[factor_name,'mean'] = factor_test.basic_df['factor'].mean()
    result_df.loc[factor_name,'med'] = factor_test.basic_df['factor'].median()
    result_df.loc[factor_name,'property'] = property_i
    result_df.loc[factor_name,'time_kind'] = time_kind_i
    result_df.loc[factor_name,'time_type'] = time_type_i
    result_df.loc[factor_name,'tick_bs'] = tick_kind1_i
    result_df.loc[factor_name,'tick_bigsmall'] = tick_kind2_i
    result_df.loc[factor_name,'tick_p'] = tick_kind3_i
    result_df.loc[factor_name,'tick_ptype'] = tick_type3_i
    result_df.loc[factor_name,'len_type'] = len_type_i
    result_df.loc[factor_name,'std'] = std_i
    result_df.loc[factor_name,'calc'] = calc_i
    result_df.loc[factor_name,'compare'] = compare_i
    return result_df
# 计算
result_df = pd.DataFrame(columns = ['factor_name','IC','info',
                                    'score','corr_other','repeat','mean','med',
                                    'property','time_kind','time_type',
                                    'tick_bs','tick_bigsmall','tick_p','tick_ptype',
                                    'len_type','std','calc',
                                    'compare'])
list_del = []
for  i in list(os.listdir('/data/user/015585/01-因子挖掘/04-Sell/因子快速开发/h5/Jupiter/20230509Tick/')):
    list_del.append(i[:-3])
list_series = ['rcleanb',
                'cleanb2ttran',
                'cleanb2tran',
                'b2tran',
                'b2ttran',
                'b2transtd',
                's2tran',
                's2ttran',
                's2transtd',
                'amt',
                'abspchange',
                'bp',
                'sp',
                'b12b',
                's12s',
                'b12s1',
                'b2s',
                'tran2b',
                'vwap2p',
                'ratiob',
                'ratiob2',
                'diffb12tran',
                'b1',
                'pb1',
                'b',
                'ratiob1thans1',
                'amt2newamt',
                'pv',
                't',
                ]
list_b930 = ['ratiob2',
            'b1',
            'pb1',
            't',]
# 注意这里使用快速拉升样本
filter_factor = pd.read_pickle('/data/group/800463/data/project1_public/factor_lib_v2/filter_quickrise.pkl')
sft = strongFactorTest(20160101, 20191231, filter_factor=filter_factor, filter_name='quickrise')
for time_kind_i in dic_time_kind:
    for time_type_i in time_type:
        for tick_kind1_i in dic_tick_kind1:
            for tick_kind2_i in dic_tick_kind2:
                for tick_kind3_i in dic_tick_kind3:
                    for tick_type3_i in tick_type3:
                        if (tick_kind3_i == '0') & (tick_type3_i == 'smaller'):
                            continue#剔除“小于全部价格”的因子
                        if (tick_kind3_i == 'p25') & (tick_type3_i == 'bigger'):
                            continue
                        if (tick_kind3_i == 'p75') & (tick_type3_i == 'smaller'):
                            continue
                        for len_type_i in dic_len_type:
                            if (time_type_i == 'before') & (len_type_i == 'h500'):
                                continue#剔除在xx时间前的最初500单，此类会重复
                            if (time_type_i == 'after') & (len_type_i == 't500'):
                                continue#剔除在xx时间后的最后500单，此类会重复
                            for property_i in dic_property:
                                if (len_type_i != 'all') & (property_i == 'rlength'):
                                    continue
                                if (time_type_i == 'before') & (time_kind_i == '930') & (property_i not in list_b930):
                                    continue
                                if (len_type_i == 'h500') & (property_i == 'avg'):
                                    continue
                                for std_i in dic_std:
                                    if (property_i != 'rlength') & (std_i != 'nostd'):
                                        continue#非标准化因子，不需要标准化
                                    for calc_i in dic_calc:
                                        if (property_i not in list_series) & (calc_i != 'nocalc'):
                                            continue#目前只有series可以使用calc
                                        if (property_i in list_series) & (calc_i == 'nocalc'):
                                            continue#series，必须calc
                                        for compare_i in dic_compare:
                                            if (compare_i != 'nocompare') & \
                                               ((compare_i != 'compare_t') | (time_type_i != 'before')) & \
                                               ((compare_i != 'compare_1') | (tick_kind1_i != 'all')) &\
                                               ((compare_i != 'compare_2') | (tick_kind2_i != 'all')) &\
                                               ((compare_i != 'compare_3') | (tick_kind3_i == '0') | (tick_type3_i != 'bigger')) &\
                                               ((compare_i != 'compare_len_h2t') | (len_type_i != 'h500')) &\
                                               ((compare_i != 'compare_len_half12') | (len_type_i != 'half1')):
                                                continue
                                            factor_name = time_kind_i + '_' + time_type_i + '_'\
                                                          + tick_kind1_i + '_' + tick_kind2_i + '_' + tick_kind3_i + '_' \
                                                          + tick_type3_i + '_' \
                                                          + len_type_i + '_' \
                                                          + property_i + '_' \
                                                          + std_i + '_' \
                                                          + calc_i + '_'\
                                                          + compare_i
                                            if factor_name in list_del:
                                                print(factor_name)
                                                continue
                                            def factor_func(tick_df, return_fillna_dic=False):
                                                if return_fillna_dic:
                                                    # 返回因子为nan时的填充值
                                                    return {factor_name: 0}
                                                value = generate_factor_addcompare(tick_df,
                                                                                   property_i,
                                                                                   time_kind_i,
                                                                                   time_type_i,
                                                                                   tick_kind1_i,
                                                                                   tick_kind2_i,
                                                                                   tick_kind3_i,
                                                                                   tick_type3_i,
                                                                                   len_type_i,
                                                                                   std_i,
                                                                                   calc_i,
                                                                                   compare_i)
                                                factor_dict = {factor_name: value}
                                                # ---------------------------------------------------------------------------------------------------------------
                                                return pd.Series(factor_dict)
                                            print(factor_name)

                                            basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_001.h5'
                                            factor_path = '/data/user/015585/01-因子挖掘/04-Sell/因子快速开发/h5/Jupiter/20230530Tick/'
                                            factor_df0 = run_factor(func = factor_func,
                                                                    factor_name = factor_name,
                                                                    factor_type = 'TTickab',
                                                                    start_date = 20160101,
                                                                    end_date = 20191231,
                                                                    basic_file_path = basic_file_path,
                                                                    result_path = factor_path,
                                                                    interval_res=False)

                                            start_date, end_date = 20160101, 20191231
                                            df = pd.read_hdf(factor_path + factor_name + '.h5')
                                            result_path = '/data/user/015585/01-因子挖掘/04-Sell/因子快速开发/回测报告/Jupiter/20230530Tickqr/'
                                            factor_test = strongFactorTest(20160101, 20191231, filter_factor=filter_factor, filter_name='quickrise')
                                            for col in df.columns:
                                                print(col)
                                                factor_test.factor_test(df[[col]], result_path, factor_corr_test=True)
                                                check_score = factor_test.result_dic['check_score_res']
                                                print('总分:',check_score.loc['score','tot_score'])
                                                print('CORR:',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])
                                                # print('高corr库中因子：')
                                                # print(factor_test.result_dic['factor_corr_summary'])
                                                # print('均值与中位数')
                                                # print(factor_test.basic_df['factor'].mean(),'',factor_test.basic_df['factor'].median())
                                                result_df = write_excel(result_df)
# # 保存excel
# import datetime
# time_now = str(datetime.datetime.now())
# str_property = '' #因子性质
# for i in dic_property.keys():
#     str_property += (i+'_')
# str_time = '' #筛选时间
# for i in dic_time_kind.keys():
#     str_time += (i+'_')
# result_df.to_excel('/data/user/015585/01-因子挖掘/04-Sell/因子快速开发/汇总excel/'
#                  + '快速开发因子_' + str_property + '_' + str_time + '_' + time_now + '.xlsx')