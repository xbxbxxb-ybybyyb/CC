# 因子自动书写
from run_factor_demo import run_factor
from test_factor_demo import strongFactorTest
import pandas as pd
import numpy as np
# 因子属性函数
def f_pro_amt(order_df):
    order_df['OrderAmt'] = order_df['OrderPrice'] * order_df['OrderQty']
    return order_df['OrderAmt']
def f_pro_length(order_df):
    return len(order_df)
def f_pro_corr_pv(order_df):
    corr = pd.concat([order_df['OrderPrice'],order_df['OrderQty']],axis = 1).corr(method = 'spearman').iloc[0,1]
    return corr
def f_pro_price_v(order_df):
    if order_df['OrderQty'].sum() > 10:
        p = (order_df['OrderPrice'] * order_df['OrderQty']).sum() / order_df['OrderQty'].sum()
    else:
        p = np.nan
    pre_close = order_df['pre_close'].max()
    if pre_close > 0.1:
        pct = p / pre_close - 1
        dt, ticker = order_df.index[0]
        dt = dt.strftime('%Y%m%d')
        zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
        if zcz == 1:
            pct = pct / 2
        return pct
    else:
        return np.nan
def f_pro_t(order_df):
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
    order_df['MDTime_delta'] = order_df['MDTime'].apply(lambda x : inttime2deltamls(x))
    return order_df['MDTime_delta']
def f_pro_index(order_df):
    return order_df['OrderIndex']
# 时间筛选函数，返回时间点
def f_t_kind_930(order_df):
    return 93000000
def get_f_t_filter(order_df,type_t,t):
    if type_t == 'before':
        order_df = order_df[order_df['MDTime'] < t]
    elif type_t == 'after':
        order_df = order_df[order_df['MDTime'] >= t]
    if t != 93000000: # 一般不包括集合竞价
        order_df = order_df[order_df['MDTime'] >= 93000000]
    return order_df
# 订单性质筛选
# 买卖
def f_o_kind1_all(order_df):
    return (order_df)
def f_o_kind1_buy(order_df):
    return (order_df[order_df['OrderBSFlag'] == 1])
def f_o_kind1_sell(order_df):
    return (order_df[order_df['OrderBSFlag'] == 2])
# 大小
def f_o_kind2_all(order_df):
    return (order_df)
def f_o_kind2_big(order_df):
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    return order_df[order_df['OrderAmt'] > 200000]
def f_o_kind2_small(order_df):
    order_df['OrderAmt'] = order_df['OrderQty'] * order_df['OrderPrice']
    return order_df[order_df['OrderAmt'] < 50000]
# 价格
def f_o_kind3_all(order_df):
    return 0
def f_o_kind3_zt(order_df):
    pre_close = round(order_df['pre_close'].mean(),3)
    dt,ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    return p_zt
def f_o_kind3_9(order_df):
    pre_close = round(order_df['pre_close'].mean(),3)
    dt,ticker = order_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    if zcz:
        p = pre_close * (1 + 0.09 * 2)
    else:
        p = pre_close * 1.09
    return p
def get_f_p_filter(order_df,type_p,p):
    if p > 0:
        if type_p == 'bigger':
            order_df = order_df[order_df['OrderPrice'] >= p]
        elif type_p == 'smaller':
            order_df = order_df[order_df['OrderPrice'] < p]#不能取等号，否则涨停价会有问题
        else:
            print('按价格分组未在指定范围内')
    else:
        order_df = order_df
    return order_df
# 长度
def f_len_all(order_df):
    return order_df
def f_len_h500(order_df):
    if len(order_df)>500:
        return order_df.head(500)
    else:
        return order_df
def f_len_t500(order_df):
    if len(order_df)>500:
        return order_df.tail(500)
    else:
        return order_df
def f_len_half1(order_df):
    if len(order_df)>10:
        return order_df.head(int(len(order_df) / 2))
    else:
        return order_df
def f_len_half2(order_df):
    if len(order_df)>10:
        return order_df.tail(int(len(order_df) / 2))
    else:
        return order_df
#
# 后续处理
# 标准化处理，仅对成交量
def f_std_nostd(order_df,order_amt):
    return order_amt
def f_std_2mv(order_df,order_amt):
    mv = order_df['pre_close'].max() * order_df['ff_shares'].max()
    if mv > 10:
        return order_amt / mv
    else:
        return order_amt / np.nan
def f_std_2ttl(order_df,order_amt):
    order_df = order_df[order_df['MDTime'] >= 93000000]
    tran_ttl = (order_df['OrderQty'] * order_df['OrderPrice']).sum()
    if tran_ttl > 0:
        return order_amt / tran_ttl
    else:
        return order_amt / np.nan
# 计算序列值，仅针对因子属性得到序列的情况
def f_calc_nocalc(factor_origin):
    return factor_origin
def f_calc_max(order_series):
    if order_series.empty:
        return np.nan
    else:
        return order_series.max()
def f_calc_min(order_series):
    if order_series.empty:
        return np.nan
    else:
        return order_series.min()
def f_calc_avg(order_series):
    if order_series.empty:
        return np.nan
    else:
        return order_series.mean()
def f_calc_med(order_series):
    if order_series.empty:
        return np.nan
    else:
        return order_series.median()
def f_calc_cv(order_series):
    if order_series.empty:
        return np.nan
    else:
        if  abs(order_series.mean()) > 0.0001:
            return order_series.std() / order_series.mean()
        else:
            return np.nan
def f_calc_sum(order_series):
    return order_series.sum()
def f_calc_cct(order_series):
    if abs(order_series.sum()) > 0.001:
        return (order_series**2).sum() / (order_series.sum())**2
    else:
        return np.nan
def f_calc_skew(order_series):
    return order_series.skew()
def f_calc_kurt(order_series):
    return order_series.kurt()
# 参数设置
dic_property = {
                'amt':f_pro_amt,
                # 'length':f_pro_length,
                # 'corr_pv':f_pro_corr_pv,
                # 'price_v':f_pro_price_v,
                # 't':f_pro_t,
                # 'index':f_pro_index
               }# 按挂单量的涨跌幅
dic_time_kind = {
                 '930':f_t_kind_930,
                }
time_type = ['before','after']
time_type = ['after']
dic_order_kind1 = {'all':f_o_kind1_all,
                   'buy':f_o_kind1_buy,
                   'sell':f_o_kind1_sell}# 买卖单
dic_order_kind2 = {'all':f_o_kind2_all,
                   'big':f_o_kind2_big,
                   'small':f_o_kind2_small}# 大小单
dic_order_kind3 = {
                   '0':f_o_kind3_all,
                   'zt':f_o_kind3_zt,
                   '9':f_o_kind3_9
                   }# 价格单
order_type3 = ['bigger','smaller']
dic_len_type = {'all':f_len_all,
                'h500':f_len_h500,
                't500':f_len_t500,
                'half1':f_len_half1,
                'half2':f_len_half2
               }
dic_std = {'nostd':f_std_nostd,
           '2mv':f_std_2mv,
           '2ttl':f_std_2ttl
          }
dic_calc = {'nocalc':f_calc_nocalc,
            'max':f_calc_max,
#             'min':f_calc_min,
            'avg':f_calc_avg,
            'med':f_calc_med,
            'cv':f_calc_cv,
            'sum':f_calc_sum,
            'cct':f_calc_cct,
            'skew':f_calc_skew,
            'kurt':f_calc_kurt
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
def generate_factor(order_df,
                    property_i,
                    time_kind_i,
                    time_type_i,
                    order_kind1_i,
                    order_kind2_i,
                    order_kind3_i,
                    order_type3_i,
                    len_type_i,
                    std_i,
                    calc_i):
    # 筛选时间
    t = dic_time_kind[time_kind_i](order_df)
    order_df_t = get_f_t_filter(order_df,time_type_i,t)
    # 筛选买卖单
    order_df_t_1 = dic_order_kind1[order_kind1_i](order_df_t)
    # 筛选大小单
    order_df_t_2 = dic_order_kind2[order_kind2_i](order_df_t_1)
    # 筛选挂单价格
    p = dic_order_kind3[order_kind3_i](order_df)
    if p > 0:
        order_df_t_3 = get_f_p_filter(order_df_t_2,order_type3_i,p)
    else:
        order_df_t_3 = order_df_t_2.copy()
    # 筛选长度
    order_df_t_len = dic_len_type[len_type_i](order_df_t_3)
    # 因子属性
    factor_origin = dic_property[property_i](order_df_t_len)
    # 如果是amt,尝试标准化
    if (property_i == 'amt'):
        factor_origin = dic_std[std_i](order_df,factor_origin)
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
def generate_factor_addcompare(order_df,
                               property_i,
                               time_kind_i,
                               time_type_i,
                               order_kind1_i,
                               order_kind2_i,
                               order_kind3_i,
                               order_type3_i,
                               len_type_i,
                               std_i,
                               calc_i,
                               compare_i):
    if compare_i == 'nocompare':
        value = generate_factor(order_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                order_kind1_i,
                                order_kind2_i,
                                order_kind3_i,
                                order_type3_i,
                                len_type_i,
                                std_i,
                                calc_i)
    elif (compare_i == 'compare_t') & (time_type_i == 'before'):
        value_1 = generate_factor(order_df,
                                    property_i,
                                    time_kind_i,
                                    'before',
                                    order_kind1_i,
                                    order_kind2_i,
                                    order_kind3_i,
                                    order_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value_2 = generate_factor(order_df,
                                    property_i,
                                    time_kind_i,
                                    'after',
                                    order_kind1_i,
                                    order_kind2_i,
                                    order_kind3_i,
                                    order_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value = value_1 / value_2 if abs(value_2) >= 0.00001 else np.nan
    elif (compare_i == 'compare_1') & (order_kind1_i == 'all'):
        value_1 = generate_factor(order_df,
                                    property_i,
                                    time_kind_i,
                                    time_type_i,
                                    'buy',
                                    order_kind2_i,
                                    order_kind3_i,
                                    order_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value_2 = generate_factor(order_df,
                                    property_i,
                                    time_kind_i,
                                    time_type_i,
                                    'sell',
                                    order_kind2_i,
                                    order_kind3_i,
                                    order_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value = value_1 / value_2 if abs(value_2) >= 0.00001 else np.nan
    elif (compare_i == 'compare_2') & (order_kind2_i == 'all'):
        value_1 = generate_factor(order_df,
                                    property_i,
                                    time_kind_i,
                                    time_type_i,
                                    order_kind1_i,
                                    'big',
                                    order_kind3_i,
                                    order_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value_2 = generate_factor(order_df,
                                    property_i,
                                    time_kind_i,
                                    time_type_i,
                                    order_kind1_i,
                                    'small',
                                    order_kind3_i,
                                    order_type3_i,
                                    len_type_i,
                                    std_i,
                                    calc_i)
        value = value_1 / value_2 if abs(value_2) >= 0.00001 else np.nan
    elif (compare_i == 'compare_3') & (order_kind3_i != '0') & (order_type3_i == 'bigger'):
        value_1 = generate_factor(order_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                order_kind1_i,
                                order_kind2_i,
                                order_kind3_i,
                                'bigger',
                                len_type_i,
                                std_i,
                                calc_i)
        value_2 = generate_factor(order_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                order_kind1_i,
                                order_kind2_i,
                                order_kind3_i,
                                'smaller',
                                len_type_i,
                                std_i,
                                calc_i)
        value = value_1 / value_2 if abs(value_2) >= 0.00001 else np.nan
    elif (compare_i == 'compare_len_h2t') & (len_type_i == 'h500'):
        value_1 = generate_factor(order_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                order_kind1_i,
                                order_kind2_i,
                                order_kind3_i,
                                order_type3_i,
                                'h500',
                                std_i,
                                calc_i)
        value_2 = generate_factor(order_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                order_kind1_i,
                                order_kind2_i,
                                order_kind3_i,
                                order_type3_i,
                                't500',
                                std_i,
                                calc_i)
        value = value_1 / value_2 if abs(value_2) >= 0.00001 else np.nan
    elif (compare_i == 'compare_len_half12') & (len_type_i == 'half1'):
        value_1 = generate_factor(order_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                order_kind1_i,
                                order_kind2_i,
                                order_kind3_i,
                                order_type3_i,
                                'half1',
                                std_i,
                                calc_i)
        value_2 = generate_factor(order_df,
                                property_i,
                                time_kind_i,
                                time_type_i,
                                order_kind1_i,
                                order_kind2_i,
                                order_kind3_i,
                                order_type3_i,
                                'half2',
                                std_i,
                                calc_i)
        value = value_1 / value_2 if abs(value_2) >= 0.00001 else np.nan
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
    result_df.loc[factor_name,'order_bs'] = order_kind1_i
    result_df.loc[factor_name,'order_bigsmall'] = order_kind2_i
    result_df.loc[factor_name,'order_p'] = order_kind3_i
    result_df.loc[factor_name,'order_ptype'] = order_type3_i
    result_df.loc[factor_name,'len_type'] = len_type_i
    result_df.loc[factor_name,'std'] = std_i
    result_df.loc[factor_name,'calc'] = calc_i
    result_df.loc[factor_name,'compare'] = compare_i
    return result_df
# 计算
result_df = pd.DataFrame(columns = ['factor_name','IC','info',
                                    'score','corr_other','repeat','mean','med',
                                    'property','time_kind','time_type',
                                    'order_bs','order_bigsmall','order_p','order_ptype',
                                    'len_type','std','calc',
                                    'compare'])
import os
a = list(os.listdir('/data/user/015585/01-因子挖掘/04-Sell/因子快速开发/h5/Jupiter/'))
b = []
for i in a:
    b.append(i[8:-3])
list_del = b
# list_del = list(pd.read_csv('/data/user/015585/01-因子挖掘/04-Sell/因子快速开发/汇总excel/' + '快速开发因子_第一次测试' + '.csv')['factor_name'])
for time_kind_i in dic_time_kind:
    for time_type_i in time_type:
        for order_kind1_i in dic_order_kind1:
            for order_kind2_i in dic_order_kind2:
                for order_kind3_i in dic_order_kind3:
                    for order_type3_i in order_type3:
                        if (order_kind3_i == '0') & (order_type3_i == 'smaller'):
                            continue#剔除“小于全部价格”的因子
                        for len_type_i in dic_len_type:
                            if (time_type_i == 'before') & (len_type_i == 'h500'):
                                continue#剔除在xx时间前的最初500单，此类会重复
                            if (time_type_i == 'after') & (len_type_i == 't500'):
                                continue#剔除在xx时间后的最后500单，此类会重复
                            for property_i in dic_property:
                                if (len_type_i != 'all') & (property_i == 'length'):
                                    continue
                                for std_i in dic_std:
                                    if (property_i != 'amt') & (std_i != 'nostd'):
                                        continue#非金额类因子，不需要除以成交量、市值
                                    for calc_i in dic_calc:
                                        if (property_i not in ['amt','t','index']) & (calc_i != 'nocalc'):
                                            continue#目前只有金额/T/INDEX类因子为series可以使用calc
                                        if (property_i in ['amt','t','index']) & (calc_i == 'nocalc'):
                                            continue#金额/T/INDEX类因子为series，必须calc
                                        for compare_i in dic_compare:
                                            if (compare_i != 'nocompare') & \
                                               ((compare_i != 'compare_t') | (time_type_i != 'before')) & \
                                               ((compare_i != 'compare_1') | (order_kind1_i != 'all')) &\
                                               ((compare_i != 'compare_2') | (order_kind2_i != 'all')) &\
                                               ((compare_i != 'compare_3') | (order_kind3_i == '0') | (order_type3_i != 'bigger')) &\
                                               ((compare_i != 'compare_len_h2t') | (len_type_i != 'h500')) &\
                                               ((compare_i != 'compare_len_half12') | (len_type_i != 'half1')):
                                                continue
                                            factor_name = time_kind_i + '_' + time_type_i + '_'\
                                                          + order_kind1_i + '_' + order_kind2_i + '_' + order_kind3_i + '_' \
                                                          + order_type3_i + '_' \
                                                          + len_type_i + '_' \
                                                          + property_i + '_' \
                                                          + std_i + '_' \
                                                          + calc_i + '_'\
                                                          + compare_i
                                            if factor_name in list_del:
                                                print(factor_name)
                                                continue
                                            def factor_func(order_df, return_fillna_dic=False):
                                                if return_fillna_dic:
                                                    # 返回因子为nan时的填充值
                                                    return {factor_name: 0}
                                                value = generate_factor_addcompare(order_df,
                                                                                   property_i,
                                                                                   time_kind_i,
                                                                                   time_type_i,
                                                                                   order_kind1_i,
                                                                                   order_kind2_i,
                                                                                   order_kind3_i,
                                                                                   order_type3_i,
                                                                                   len_type_i,
                                                                                   std_i,
                                                                                   calc_i,
                                                                                   compare_i)
                                                factor_dict = {factor_name: value}
                                                # ---------------------------------------------------------------------------------------------------------------
                                                return pd.Series(factor_dict)
                                            print(factor_name)

                                            basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_001.h5'
                                            factor_path = '/data/user/015585/01-因子挖掘/04-Sell/因子快速开发/h5/Jupiter/20230427/'
                                            factor_df0 = run_factor(func = factor_func,
                                                                    factor_name = factor_name,
                                                                    factor_type = 'TOrder',
                                                                    start_date = 20160101,
                                                                    end_date = 20191231,
                                                                    basic_file_path = basic_file_path,
                                                                    result_path = factor_path,
                                                                    interval_res=False)

                                            start_date, end_date = 20160101, 20191231
                                            df = pd.read_hdf(factor_path + factor_name + '.h5')
                                            result_path = '/data/user/015585/01-因子挖掘/04-Sell/因子快速开发/回测报告/Jupiter/20230427/'
                                            factor_test = factor_test = strongFactorTest(start_date, end_date)
                                            for col in df.columns:
                                                print(col)
                                                factor_test.factor_test(df[[col]], result_path, factor_corr_test=True)
                                                check_score = factor_test.result_dic['check_score_res']
                                                print('总分:',check_score.loc['score','tot_score'])
                                                print('CORR：')
                                                print(factor_test.result_dic['corr_sta'])
                                                print('高corr库中因子：')
                                                print(factor_test.result_dic['factor_corr_summary'])
                                                print('均值与中位数')
                                                print(factor_test.basic_df['factor'].mean(),'',factor_test.basic_df['factor'].median())
                                                result_df = write_excel(result_df)
# 保存excel
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