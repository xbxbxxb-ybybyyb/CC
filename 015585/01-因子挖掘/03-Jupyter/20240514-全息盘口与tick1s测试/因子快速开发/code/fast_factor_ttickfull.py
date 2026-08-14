import os
from run_factor_demo_parallel_new import run_factor
from test_factor_demo import strongFactorTest
import pandas as pd
import numpy as np
# 因子属性函数
def f_pro_orderp2bp(tick_df):# 订单价格 - 买均对应的收益率
    tick_df = tick_df[tick_df['WeightedAvgBidPx'] > 0.5]
    tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['WeightedAvgBidPx']) / tick_df['pre_close']
    return tick_df['factor']
def f_pro_orderp2sp(tick_df):# 订单价格 - 卖均对应的收益率
    tick_df = tick_df[tick_df['WeightedAvgOfferPx'] > 0.5]
    tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['WeightedAvgOfferPx']) / tick_df['pre_close']
    return tick_df['factor']
def f_pro_orderp2lp(tick_df):# 订单价格 - 最新价格对应的收益率
    tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['LastPx']) / tick_df['pre_close']
    return tick_df['factor']
def f_pro_orderp2bp10(tick_df):# 订单价格是否高于卖10价格
    tick_df = tick_df[tick_df['Buy10Price'] > 0]
    tick_df['factor'] = np.sign(tick_df['OrderPrice'] - tick_df['Buy10Price'])
    return tick_df['factor']
def f_pro_ordervol2bvol(tick_df): # 订单量/挂买量
    tick_df['factor'] = (tick_df['OrderQty'] / tick_df['TotalBidQty'])
    return tick_df['factor']
def f_pro_ordervol2svol(tick_df): # 订单量/挂卖量
    tick_df['factor'] = (tick_df['OrderQty'] / tick_df['TotalOfferQty'])
    return tick_df['factor']
def f_pro_orderamt2bamt(tick_df):# 订单金额/挂买金额
    tick_df['factor'] = (tick_df['OrderQty'] * tick_df['OrderPrice']) / (tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx'])
    return tick_df['factor']
def f_pro_orderamt2samt(tick_df):# 订单金额/挂卖金额
    tick_df['factor'] = (tick_df['OrderQty'] * tick_df['OrderPrice']) / (tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx'])
    return tick_df['factor']
def f_pro_orderamt2bsamt(tick_df):# 订单金额/(挂卖金额+挂买总额)
    tick_df['factor'] = (tick_df['OrderQty'] * tick_df['OrderPrice']) / (tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
                                                                         + tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx'])
    return tick_df['factor']
def f_pro_orderamt2trade(tick_df):# 订单金额/阶段总成交
    tick_df['factor'] = (tick_df['OrderQty'] * tick_df['OrderPrice']) / tick_df['ValueTrade'].sum()
    return tick_df['factor']
def f_pro_orderp2tradep(tick_df):# 成交均价和挂单价格的差
    tick_df = tick_df[tick_df['ValueTrade'] > 1]
    tick_df['factor'] = (tick_df['OrderPrice'] - tick_df['ValueTrade'] / tick_df['VolumeTrade']) / tick_df['pre_close']
    return tick_df['factor']
# 时间筛选函数，返回时间点
def f_t_kind_930(tick_df):
    return 93000000
def f_t_kind_not15(tick_df):
    t_max = tick_df['MDTime'].max()
    if t_max <= 93100000:
        return 93000000
    elif (t_max <= 93500000)&(len(tick_df)>13):
        return tick_df['MDTime'].tail(13).min()
    elif (t_max <= 100000000)&(len(tick_df)>80):
        return tick_df['MDTime'].tail(80).min()
    else:
        return tick_df['MDTime'].tail(300).min()
def f_t_kind_not10(tick_df):# 只取-20min到-10min，这里返回-10min
    t_max = tick_df['MDTime'].max()
    if t_max <= 93100000:
        return 93000000
    elif (t_max <= 93500000)&(len(tick_df)>13):
        return tick_df['MDTime'].tail(13).min()
    elif (t_max <= 100000000)&(len(tick_df)>80):
        return tick_df['MDTime'].tail(80).min()
    else:
        return tick_df['MDTime'].tail(200).min()
def f_t_kind_not20(tick_df):# 不存放于dic中，这里返回-20min
    t_max = tick_df['MDTime'].max()
    if t_max <= 93100000:
        return 93000000
    elif (t_max <= 93500000)&(len(tick_df)>33):
        return tick_df['MDTime'].tail(33).min()
    elif (t_max <= 100000000)&(len(tick_df)>180):
        return tick_df['MDTime'].tail(180).min()
    else:
        return tick_df['MDTime'].tail(400).min()
def get_f_t_filter(tick_df,type_t,t):
    if type_t == 'before':
        tick_df = tick_df[tick_df['MDTime'] < t]
    elif type_t == 'after':
        tick_df = tick_df[tick_df['MDTime'] >= t]
    elif type_t == 'beside':#仅用于-20到-10，此时t=not10的时间
        tick_df1 = tick_df[tick_df['MDTime'] <= t]
        t_20 = f_t_kind_not20(tick_df)
        tick_df = tick_df1[tick_df1['MDTime'] >= t_20]
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
# 订单类别
def f_tick_kind4_all(tick_df):
    return tick_df
def f_tick_kind4_b1(tick_df):
    return tick_df[tick_df['OrderType'] == 'b1']
def f_tick_kind4_b2(tick_df):
    return tick_df[tick_df['OrderType'] == 'b2']
def f_tick_kind4_o1(tick_df):
    return tick_df[tick_df['OrderType'] == 'o1']
def f_tick_kind4_o2(tick_df):
    return tick_df[tick_df['OrderType'] == 'o2']
def f_tick_kind4_cb(tick_df):
    return tick_df[tick_df['OrderType'] == 'cb']
def f_tick_kind4_co(tick_df):
    return tick_df[tick_df['OrderType'] == 'co']
# 订单金额
def f_tick_kind5_all(tick_df):
    return tick_df
def f_tick_kind5_big(tick_df):
    return tick_df[(tick_df['OrderQty']*tick_df['OrderPrice'])>=200000]
def f_tick_kind5_mid(tick_df):
    return tick_df[((tick_df['OrderQty']*tick_df['OrderPrice'])<200000) & ((tick_df['OrderQty']*tick_df['OrderPrice'])>=50000)]
def f_tick_kind5_small(tick_df):
    return tick_df[(tick_df['OrderQty']*tick_df['OrderPrice'])<50000]
# 订单价格:1、高于卖10；2、低于买10；3、9%以上；4、高于市价*1.01；5、低于市价*0.99
def f_tick_kind6_all(tick_df):
    return tick_df
def f_tick_kind6_upsell10(tick_df):
    tick_df = tick_df[tick_df['Sell10Price'] > 0]
    tick_df = tick_df[tick_df['OrderPrice'] >= tick_df['Sell10Price']]
    return tick_df
def f_tick_kind6_downbuy10(tick_df):
    tick_df = tick_df[tick_df['Buy10Price'] > 0]
    tick_df = tick_df[tick_df['OrderPrice'] <= tick_df['Buy10Price']]
    return tick_df
def f_tick_kind6_up9(tick_df):
    # tick_df = tick_df[tick_df['Buy10Price'] > 0]
    tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['pre_close'] * 1.09)]
    return tick_df
def f_tick_kind6_up101(tick_df):
    # tick_df = tick_df[tick_df['Buy10Price'] > 0]
    tick_df = tick_df[tick_df['OrderPrice'] >= (tick_df['LastPx'] * 1.01)]
    return tick_df
def f_tick_kind6_down99(tick_df):
    # tick_df = tick_df[tick_df['Buy10Price'] > 0]
    tick_df = tick_df[tick_df['OrderPrice'] <= (tick_df['LastPx'] * 0.99)]
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
    if len(tick_df)>60:
        return tick_df.tail(60)
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
        if  abs(tick_series.mean()) > 0.000001:
            return tick_series.std() / tick_series.mean()
        else:
            return np.nan
def f_calc_sum(tick_series):
    if tick_series.empty:
        return np.nan
    else:
        return tick_series.sum()
def f_calc_cct(tick_series):
    if abs(tick_series.sum()) > 0.000001:
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
# 参数设置
dic_property = {
'orderp2bp':f_pro_orderp2bp,
'orderp2sp':f_pro_orderp2sp,
'orderp2lp':f_pro_orderp2lp,
'orderp2bp10':f_pro_orderp2bp10,
'ordervol2bvol':f_pro_ordervol2bvol,
'ordervol2svol':f_pro_ordervol2svol,
'orderamt2bamt':f_pro_orderamt2bamt,
'orderamt2samt':f_pro_orderamt2samt,
'orderamt2bsamt':f_pro_orderamt2bsamt,
'orderamt2trade':f_pro_orderamt2trade,
'orderp2tradep':f_pro_orderp2tradep
               }
dic_time_kind = {
                 '930':f_t_kind_930,
                 # 'not15':f_t_kind_not15,
                 # 'not10':f_t_kind_not10,
                }
# time_type = ['after','before','beside']
time_type = ['after']
dic_tick_kind1 = {'all':f_tick_kind1_all,
                   # 'amt25':f_tick_kind1_25,
                   # 'amt75':f_tick_kind1_75
                  }# amt
dic_tick_kind2 = {'all':f_tick_kind2_all,
                   # 'up':f_tick_kind2_up,
                   # 'down':f_tick_kind2_down
                  }# up&down
dic_tick_kind3 = {
                   '0':f_tick_kind3_all,
                   # 'p25':f_tick_kind3_25,
                   # 'p75':f_tick_kind3_75
                   }# 市场价格
tick_type3 = ['bigger','smaller']
dic_tick_kind4 = {
    'all':f_tick_kind4_all,
    'b1':f_tick_kind4_b1,
    'b2':f_tick_kind4_b2,
    'o1':f_tick_kind4_o1,
    'o2':f_tick_kind4_o2,
    'cb':f_tick_kind4_cb,
    'co':f_tick_kind4_co
}
dic_tick_kind5 = {
    'all':f_tick_kind5_all,
    'big':f_tick_kind5_big,
    'mid':f_tick_kind5_mid,
    'small':f_tick_kind5_small,
}
dic_tick_kind6 = {
    'all': f_tick_kind6_all,
    'upsell10': f_tick_kind6_upsell10,
    'downbuy10': f_tick_kind6_downbuy10,
    'up9': f_tick_kind6_up9,
    'up101':f_tick_kind6_up101,
    'down99':f_tick_kind6_down99,
}
dic_len_type = {
                'all':f_len_all,
                # 'h500':f_len_h20,
                # 't500':f_len_t20,
                # 'half1':f_len_half1,
                # 'half2':f_len_half2
               }
dic_std = {'nostd':f_std_nostd,
           '2length':f_std_2length,
          }
dic_calc = {'nocalc':f_calc_nocalc,
            'max':f_calc_max,
            'min':f_calc_min,
            'avg':f_calc_avg,
            'med':f_calc_med,
            'cv':f_calc_cv,
            'sum':f_calc_sum,
            'cct':f_calc_cct,
            'skew':f_calc_skew,
            'kurt':f_calc_kurt,
            'change':f_calc_change,
            'tail':f_calc_tail,
            'm2m':f_calc_m2m,
            'std':f_calc_std,
           }
dic_compare = [
               'nocompare',
               # 'compare_t',
               # 'compare_1',
               # 'compare_2',
               # 'compare_3',
               # 'compare_len_h2t',
               # 'compare_len_half12'
                ]
# 主体函数
def generate_factor(tick_df,
                    property_i,
                    time_kind_i,
                    time_type_i,
                    tick_kind1_i,
                    tick_kind2_i,
                    tick_kind3_i,
                    tick_type3_i,
                    tick_kind4_i,
                    tick_kind5_i,
                    tick_kind6_i,
                    len_type_i,
                    std_i,
                    calc_i):
    # 新增tick成交额、成交量列
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    # 筛选时间
    t = dic_time_kind[time_kind_i](tick_df)
    tick_df_t = get_f_t_filter(tick_df,time_type_i,t)
    # 筛选amt
    tick_df_t_1 = dic_tick_kind1[tick_kind1_i](tick_df_t)
    # 筛选up&down
    tick_df_t_2 = dic_tick_kind2[tick_kind2_i](tick_df_t_1)
    # 筛选tick价格
    p = dic_tick_kind3[tick_kind3_i](tick_df_t)
    if p > 0:
        tick_df_t_3 = get_f_p_filter(tick_df_t_2,tick_type3_i,p)
    else:
        tick_df_t_3 = tick_df_t_2.copy()
    # 筛选订单类型
    tick_df_t_4 = dic_tick_kind4[tick_kind4_i](tick_df_t_3)
    tick_df_t_5 = dic_tick_kind5[tick_kind5_i](tick_df_t_4)
    tick_df_t_6 = dic_tick_kind6[tick_kind6_i](tick_df_t_5)
    # 筛选长度
    tick_df_t_len = dic_len_type[len_type_i](tick_df_t_6)
    # 因子属性
    factor_origin = dic_property[property_i](tick_df_t_len)
    # rlength,尝试标准化
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
                               tick_kind4_i,
                               tick_kind5_i,
                               tick_kind6_i,
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
                                tick_kind4_i,
                                tick_kind5_i,
                                tick_kind6_i,
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
                                    tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
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
                                  tick_kind4_i,
                                  tick_kind5_i,
                                  tick_kind6_i,
                                'half2',
                                std_i,
                                calc_i)
        value = value_1 - value_2
    else:
        raise ValueError('出现了不允许的compare因子')
    return value
# 计算
list_del = []
for i in os.listdir('/dfs/user/015585/01_factor_develop_store/fast_factor/europa/h5/20240522tickfull/'):
    list_del.append(i.replace('.h5',''))
list_series = ['orderp2bp',
'orderp2sp',
'orderp2lp',
'orderp2bp10',
'ordervol2bvol',
'ordervol2svol',
'orderamt2bamt',
'orderamt2samt',
'orderamt2bsamt',
'orderamt2trade',
'orderp2tradep',
                ]
list_b930 = ['ratiob2',
            'b1',
            'pb1',
            't',]
sft = strongFactorTest(20170101, 20191231, filter_factor=None, cal_mi=None)
for time_kind_i in dic_time_kind:
    for time_type_i in time_type:
        if (time_kind_i == '930') & (time_type_i == 'before'):
            continue
        if (time_kind_i == 'not10') & (time_type_i != 'beside'):
            continue
        if (time_kind_i != 'not10') & (time_type_i == 'beside'):
            continue
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
                        for tick_kind4_i in dic_tick_kind4:
                            for tick_kind5_i in dic_tick_kind5:
                                for tick_kind6_i in dic_tick_kind6:
                                    if tick_kind6_i == 'all' and tick_kind5_i =='all':
                                        continue
                                    for len_type_i in dic_len_type:
                                        if (time_type_i == 'before') & (len_type_i == 'h500'):
                                            continue#剔除在xx时间前的最初500单，此类会重复
                                        # if (time_type_i == 'after') & (len_type_i == 't500'):
                                        #     continue#剔除在xx时间后的最后500单，此类会重复
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
                                                                      + tick_kind4_i + '_' \
                                                                      + tick_kind5_i + '_' \
                                                                      + tick_kind6_i + '_' \
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
                                                                                               tick_kind4_i,
                                                                                               tick_kind5_i,
                                                                                               tick_kind6_i,
                                                                                               len_type_i,
                                                                                               std_i,
                                                                                               calc_i,
                                                                                               compare_i)
                                                            factor_dict = {factor_name: value}
                                                            # ---------------------------------------------------------------------------------------------------------------
                                                            return pd.Series(factor_dict)
                                                        print(factor_name)

                                                        basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
                                                        factor_path = '/dfs/user/015585/01_factor_develop_store/fast_factor/europa/h5/20240606tickfull/'
                                                        factor_df0 = run_factor(func = factor_func,
                                                                                factor_name = factor_name,
                                                                                factor_type = 'TTickfull',
                                                                                start_date = 20170101,
                                                                                end_date = 20191231,
                                                                                basic_file_path = basic_file_path,
                                                                                result_path = factor_path,
                                                                                interval_res=False)
                                                        start_date, end_date = 20170101, 20191231
                                                        df = pd.read_hdf(factor_path + factor_name + '.h5')
                                                        result_path = '/dfs/user/015585/01_factor_develop_store/fast_factor/europa/factor_report/20240606tickfull/'
                                                        factor_test = strongFactorTest(20170101, 20191231,cal_mi=None)
                                                        for col in df.columns:
                                                            print(col)
                                                            factor_test.factor_test(df[[col]], result_path, factor_corr_test=True, generate_pdf=False)
                                                            check_score = factor_test.result_dic['check_score_res']
                                                            print('总分:',check_score.loc['score','tot_score'])
                                                            print('CORR:',factor_test.result_dic['corr_sta'].loc['corr_tot','value'])