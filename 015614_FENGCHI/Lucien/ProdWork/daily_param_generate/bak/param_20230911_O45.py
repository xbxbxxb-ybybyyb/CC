# -*- coding: utf-8 -*-
# @Time    : 2022/6/8 17:32
# @Author  : wangweidi
# -*- coding: utf-8 -*-
# @Time    : 2022/4/15 9:37
# @Author  : wangweidi
import os
import datetime as dt
import pandas as pd
import numpy as np
import random
import ProdWork.daily_param_generate.bak.pre_file_check as pre_check
import time
from xquant.xqutils.helper import link
from xquant.factordata import FactorData

s = FactorData()
pd.set_option('display.max_columns',40)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 500)

def get_random_time(num, start_time, end_time):
    time_list = []
    start_time, end_time = dt.datetime.strptime(start_time, '%H%M%S'), dt.datetime.strptime(end_time, '%H%M%S')
    interval_seconds = (end_time - start_time).seconds
    for second in range(interval_seconds):
        time_str = (start_time + dt.timedelta(seconds=second)).strftime('%H:%M:%S')
        time_list.append(time_str)

    res_list = time_list * ((num // len(time_list)) + 1)
    res_list = res_list[:num]
    return res_list


def param_str(ser, envir):
    res_str = ''
    for factor, value in zip(list(ser.index), list(ser)):
        if factor in ['saturn_Last_volatility_5']:
            s = '%.20f' % (value)
        elif factor in ['ul_price', 'pre_close']:
            s = '%.2f' % (value)
        elif (factor in ['saturn_yzhan_hf_af1_27']):
            s = '%.35f' % (value)
        else:
            s = '%.16f' % (value)
        while (len(s) > 1) and ((s[-1] == '0') or (s[-1] == '.')):
            last_str = s[-1]
            s = s[:-1]
            if last_str == '.':
                break
        if abs(round(value - float(s), 16)) > 0.001:
            print('factor value diff!!!!!! ', value, s)
        res_str += '%s:' % (factor) + s + ';'
    return res_str


def get_key_word(str_ser):
    res_dic = {}
    for index, factor_str in str_ser.iterrows():
        factor_list = factor_str['因子数据'].split(';')
        for factor in factor_list:
            if ('nan' in factor) or ('inf' in factor):
                res_dic[index] = factor
    return res_dic


def get_init_position(today, port_code, Oxx):
    if Oxx == 'O32':
        port_file = '/data/group/800463/position/综合信息查询_组合证券_537_%s.xls' % (today)
        df = pd.read_excel(port_file, dtype={'证券代码': str})
        if len(df) == 0:
            return {}
        df = df[(df['交易市场'] == '上交所A') | (df['交易市场'] == '深交所A')]
    elif Oxx == 'O45':
        port_file = '/data/group/800463/position/O45_组合证券_%s.xlsx' % (today)
        df = pd.read_excel(port_file, dtype={'证券代码': str})
        if len(df) == 0:
            return {}
        df = df[(df['交易市场'] == '上海') | (df['交易市场'] == '深圳')]

    df['证券代码'] = df['证券代码'].apply(lambda x: x + '.SH' if x[0] == '6' else x + '.SZ')
    if Oxx == 'O32':
        df = df[df['资产单元编号'] == int(port_code)]
    code_list = list(df['证券代码'])
    position_list = list(df['T日指令可用数量'])
    position_dic = {code_list[i]: position_list[i] for i in range(len(code_list))}
    return position_dic


def get_init_amt(today, port_code, Oxx):
    if Oxx == 'O32':
        port_file = '/data/group/800463/position/综合信息查询_组合证券_537_%s.xls' % (today)
        df = pd.read_excel(port_file, dtype={'证券代码': str})
        if len(df) == 0:
            return {}
        df = df[(df['交易市场'] == '上交所A') | (df['交易市场'] == '深交所A')]

    elif Oxx == 'O45':
        port_file = '/data/group/800463/position/O45_组合证券_%s.xlsx' % (today)
        df = pd.read_excel(port_file, dtype={'证券代码': str})
        if len(df) == 0:
            return {}
        df = df[(df['交易市场'] == '上海') | (df['交易市场'] == '深圳')]
        df['市值'] = df['持仓市值(元)']

    df['证券代码'] = df['证券代码'].apply(lambda x: x + '.SH' if x[0] == '6' else x + '.SZ')
    if Oxx == 'O32':
        df = df[df['资产单元编号'] == int(port_code)]
    return df.set_index('证券代码')['市值']


def get_jupiter_position(today):
    last_tradingday = s.tradingday(str(today), -2)[0]
    last_tradingday_str = last_tradingday[:4] + '-' + last_tradingday[4:6] + '-' + last_tradingday[6:]
    df = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/jupiter成交记录-%s.xlsx' % (last_tradingday),
                       sheet_name='累计买入明细')
    code_list = df[(df['发生日期'] == last_tradingday_str) & (df['成交数量'] > 0)]['证券代码'].to_list()
    return code_list

def get_ceres_position(today):
    last_tradingday = s.tradingday(str(today), -2)[0]
    # last_tradingday_str = last_tradingday[:4]+'-'+last_tradingday[4:6]+'-'+last_tradingday[6:]
    df = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/ceres成交记录-%s.xlsx'%(last_tradingday), sheet_name='累计卖出明细')
    code_list = df[df['是否全部卖出']!=1]['证券代码'].to_list()
    return code_list

def get_shares_data(stock_list, today):
    df = s.get_factor_value('WIND_AShareEODDerivativeIndicator',
                            factors=['TRADE_DT', 'S_INFO_WINDCODE', 'TOT_SHR_TODAY', 'FLOAT_A_SHR_TODAY'],
                            TRADE_DT=[today]).rename(columns={'S_INFO_WINDCODE': '股票代码',
                                                              'TOT_SHR_TODAY': '总股本',
                                                              'FLOAT_A_SHR_TODAY': '流通股本'}).set_index(['股票代码'])
    df = df.reindex(stock_list)
    df.index.names = ['code']
    if df.isnull().sum().sum() > 0:
        print('股本数据存在nan！！！！！！！！！！')
        print(df[df.isnull().sum(axis=1) > 0])
    return df[['总股本', '流通股本']]


def get_max_and_high_data(stock_list, today):
    df = s.get_factor_value('Basic_factor', stock_list, [today], ['high', 'mdc_maxpx']).rename(
        columns={'mdc_maxpx': 'maxpx'}).reset_index(level=0, drop=True)
    df = df.reindex(stock_list)
    df.index.names = ['code']
    if df.isnull().sum().sum() > 0:
        print('最高价涨停价 数据存在nan！！！！！！！！！！')
        print(df[df.isnull().sum(axis=1) > 0])
    return df[['high', 'maxpx']]


def get_pre_close(code_list, tradingday, use_self_preclose):
    pre_close = pd.read_pickle('/data/group/800463/param/pre_close/%s.pkl' % (tradingday)).reindex(code_list)
    if use_self_preclose:
        return pre_close['self_preclose'].to_list()
    else:
        return pre_close['unadjfactor_preclose'].to_list()


def cal_ul_price(df, key='前收盘价格'):
    df['code'] = list(df.index)
    df['ul_price'] = df.apply(lambda x: np.floor(x[key] * 100 * 1.1 + 0.5) / 100 if x['code'][:2] != '30' else np.floor(
        x[key] * 100 * 1.2 + 0.5) / 100, axis=1)
    return df['ul_price']


def get_trade_status(stock_list, today):
    df = s.get_factor_value('Basic_factor', stock_list, [today], ['mdc_trade_status']).rename(
        columns={'mdc_trade_status': 'trade_status'})
    df = df.reset_index().set_index('stock')
    if df.isnull().sum().sum() > 0:
        print('trade_status数据存在nan！！！！！！！！！！')
        print(df[df.isnull().sum(axis=1) > 0])
    df.index.names = ['code']
    return df['trade_status']


def get_sample_univ(today, white_list_list, black_list_list, grey_list_list):
    sample_df = pd.DataFrame()
    for white_list in white_list_list:
        tmp_sample_df = pd.read_excel(white_list)[['证券代码']].astype('str').rename(columns={'证券代码': '股票代码'})
        tmp_sample_df['股票代码'] = tmp_sample_df['股票代码'].apply(lambda x: x + '.SH' if x[0] == '6' else x + '.SZ')
        is_stock = tmp_sample_df['股票代码'].apply(lambda x: True if x[0] in ['0', '3', '6'] else False)
        tmp_sample_df = tmp_sample_df[is_stock]
        sample_df = sample_df.append(tmp_sample_df)
    sample_df = sample_df.drop_duplicates()
    sample_df = sample_df.sort_values(by='股票代码').reset_index(drop=True)

    all_black_list = []
    for black_list in black_list_list:
        black_df = pd.read_excel(black_list, dtype=str)
        if '出池时间' in black_df.columns:
            black_df = black_df[black_df['出池时间'].isnull()]
        if '证券代码' in black_df.columns:
            all_black_list = all_black_list + list(black_df['证券代码'])
        else:
            all_black_list = all_black_list + list(black_df['股票代码'])
    all_black_list = list(all_black_list)
    all_black_list = [x + '.SH' if x[0] == '6' else x + '.SZ' for x in all_black_list]

    print('股票池初始数量：%d' % (len(sample_df)))
    # after_st_filter = s.stock_filter(sample_df['股票代码'].to_list(), yesterday, 'STPT')['stock'].to_list()
    print('对于摘帽的股票，要测试确定是否会被筛选掉')
    # sample_df = sample_df[sample_df['股票代码'].apply(lambda x: x in after_st_filter)]
    # print('去除ST后数量：%d' % (len(sample_df)))
    sample_df = sample_df[sample_df['股票代码'].apply(lambda x: x not in all_black_list)]
    print('去除黑名单后数量：%d' % (len(sample_df)))
    sample_df = sample_df[sample_df['股票代码'].apply(lambda x: x[:2] != '68')]
    print('去除科创板后数量：%d' % (len(sample_df)))
    risk_df = s.get_factor_value('WIND_AShareST')
    risk_list = list(risk_df[risk_df['REMOVE_DT'].isnull() & (risk_df['S_TYPE_ST']!='R')]['S_INFO_WINDCODE'])
    sample_df = sample_df[sample_df['股票代码'].apply(lambda x: (x not in risk_list))]
    print('去除退市后数量：%d' % (len(sample_df)))
    strong_stock = get_init_position(today, '3701', 'O32')
    sample_df = sample_df[sample_df['股票代码'].apply(lambda x: x not in strong_stock)]
    print('去除次新强势持仓后数量：%d' % (len(sample_df)))
    ten_days_ago = int(s.tradingday(today, -11)[0])
    ipo_df = pd.read_hdf('/data/group/800080/warehouse/prod/DATABASE/WIND/AShareIPO/AShareIPO.h5')
    new_stock = list(ipo_df[ipo_df['S_IPO_LISTDATE'] >= ten_days_ago]['S_IPO_LISTDATE'].index.get_level_values(1))
    sample_df = sample_df[sample_df['股票代码'].apply(lambda x: x not in new_stock)]
    print('去除10日新股后数量：%d' % (len(sample_df)))

    all_grey_list = []
    for grey_list in grey_list_list:
        grey_df = pd.read_excel(grey_list, dtype=str)
        if '证券代码' in grey_df.columns:
            all_grey_list = all_grey_list + list(grey_df['证券代码'])
        else:
            all_grey_list = all_grey_list + list(grey_df['股票代码'])
    all_grey_list = [x + '.SH' if x[0] == '6' else x + '.SZ' for x in all_grey_list]
    print('灰名单股票:%s' % (all_grey_list))
    for stock in all_grey_list:
        if stock in list(sample_df['股票代码']):
            print('ERROR!!!!灰名单样本%s在样本中' % (stock))
        if stock not in all_black_list:
            print('ERROR!!!!灰名单样本%s不在黑名单中' % (stock))
    sample_df = sample_df.append(pd.DataFrame(all_grey_list, columns=['股票代码']))
    print('增加灰名单后数量：%d' % (len(sample_df)))
    return sample_df.reset_index(drop=True).sort_values(by='股票代码'), all_grey_list


def check_name(x):
    sheet = ['InitialBasicParam', '指数', 'T-1日涨停股票', 'T-1日非一字涨停的涨停股票', 'T-1日触板股票', 'T-1日形态3股票',
             'T-1日形态4股票', 'T-1日筛选后形态4股票', 'T-1日筛选后形态2股票', 'T-1日开盘非涨停收盘涨停股票', 'T-1日全部触板股票',
             '股票数据', '全部股票数据', 'saturn配置参数', 'saturn截面订阅列表', 'ceres配置参数', 'ceres截面订阅列表']

    x_sheet = list(x.keys())
    if (sheet != x_sheet):
        print('sheet_name 不相同！！！！！')
    else:
        print('sheet_name 相同')

    # stock_list = set(x['T-1日涨停股票']['股票代码']) | set(x['T-1日非一字涨停的涨停股票']['股票代码']) | set(x['T-1日触板股票']['股票代码']) |\
    #              set(x['T-1日形态3股票']['股票代码']) | set(x['T-1日形态4股票']['股票代码']) | set(x['T-1日筛选后形态4股票']['股票代码']) | \
    #              set(x['T-1日筛选后形态2股票']['股票代码'])| set(x['T-1日开盘非涨停收盘涨停股票']['股票代码']) | set(x['T-1日全部触板股票']['股票代码']) | set(x['saturn截面订阅列表']['股票代码']) | set(x['ceres截面订阅列表']['股票代码'])
    # data_stock_list = set(x['股票数据']['股票代码']) | {'600614.SH', '000662.SZ', '000835.SZ', '002711.SZ', '002071.SZ', '600701.SH'}
    #


def check(today, df, initPosition, factor_param):
    strong_stock = get_init_position(today, '3701', 'O32')

    print('--------------------------------------')
    print('期初持仓', initPosition)
    print('强势股次新股持仓', strong_stock)
    if factor_param.shape[1] != 335:
        print('factor shape!!!!!!!!!!!!', factor_param.shape)
    else:
        print('factor shape', factor_param.shape)
    print('--------------------------------------')
    # 统计空值
    null_sta = df.isnull().any()
    if sum(null_sta) > 0:
        print('存在空值！！！！！')
        print(null_sta[null_sta])
    else:
        print('OK 未检查到空值')

    # 交易所监控额度和股数的检查
    # if (sum(df['交易所监控的较大额度'] != 2800000) > 0) or (sum(df['交易所监控的较大股数'] != 280000) > 0):
    #     print('交易所监控数量不对' + '!' * 10)
    # else:
    #     print('OK 交易所监控数量符合要求')

    # 一个TICK内的最大挂单次数检查
    if (sum(df['一个TICK内的最大挂单次数'] != 1) > 0):
        print('一个TICK内的最大挂单次数不对' + '!' * 10)
    else:
        print('OK 一个TICK内的最大挂单次数符合要求')

    # 判断次新股强势股是否在样本中
    in_sample = set(df['股票代码']) & set(strong_stock.keys())
    if len(in_sample) == 0:
        print('OK 样本中没有次新股或者强势股')
    else:
        print('样本中存在次新股或者强势股%s' % (in_sample), '!' * 10)

    # 小单测试数量
    print('参与小单测试的个股数量=%d个' % (sum(df['小单测试'])))

    # 单笔订单的最大下单股数
    print('单笔订单的最大下单股数=%d股' % (max(df['单次下单最大股数'])))

    d = df[['股票代码', '前收盘价格',
            'NL1目标金额', 'NL2目标金额', 'NL3目标金额', 'NL4目标金额', 'NL5目标金额',
            'NewL1目标金额', 'NewL2目标金额', 'NewL3目标金额', 'NewL4目标金额', 'NewL5目标金额',
            'NL1目标金额_add', 'NL2目标金额_add', 'NL3目标金额_add', 'NL4目标金额_add', 'NL5目标金额_add']].copy()
    d['ul_price'] = np.floor(d['前收盘价格'] * 1.1 * 100 + 0.5) / 100
    d['exchange'] = d['股票代码'].apply(lambda x: x[:2])
    d.loc[d['exchange'] == '30', 'ul_price'] = np.floor(d['前收盘价格'] * 1.2 * 100 + 0.5) / 100
    print(d.groupby('exchange').max()[
              ['NL1目标金额', 'NL2目标金额', 'NL3目标金额', 'NL4目标金额', 'NL5目标金额',
               'NewL1目标金额', 'NewL2目标金额', 'NewL3目标金额', 'NewL4目标金额', 'NewL5目标金额',
               'NL1目标金额_add', 'NL2目标金额_add', 'NL3目标金额_add', 'NL4目标金额_add', 'NL5目标金额_add'
               ]])


def generate(today, envir):
    while True:
        flag, file_list = pre_check.pre_check(today)
        lm = link.LinkMessage()
        lm.sendMessage('all param file ready:%s;%s' % (flag, file_list))

        if flag:
            break
        else:
            time.sleep(60)

    use_self_preclose = True
    yesterday = s.tradingday(today, -2)[0]
    print(today, envir, '\n')
    file_path = '/data/group/800463/param/param/'
    file_name = '%sparam-%s-%s-O45.xlsx' % (file_path, today, envir)

    saturn_list = ['930', '931']
    ceres_list = ['930', '931']
    sell_list = ['930', '931']

    white_list_list = ['/data/group/800463/stock_list/white_list/%s.xls' % (today)]

    grey_list_list = ['/data/group/800463/stock_list/grey_list/grey_list_%s.xlsx' % (today)]

    black_list_list = ['/data/group/800463/stock_list/black_other_list/黑名单-20240415.xlsx',
                       '/data/group/800463/stock_list/black_other_list/手动调整黑名单.xlsx',
                       '/data/group/800463/stock_list/abnormal_notice_list/abnormal_notice_list_%s.xlsx' % (today),
                       '/data/group/800463/stock_list/pre_st_list/pre_st_list_%s.xlsx' % (yesterday),
                       '/data/group/800463/stock_list/after_dt_list/after_dt_list_%s.xlsx' % (yesterday),
                       '/data/group/800463/stock_list/defer_reply_list/defer_reply_list_%s.xlsx' % (yesterday),
                       '/data/group/800463/stock_list/share_comp_restrict_list/share_comp_restrict_list_%s.xlsx' % (today)
                       ]

    factor_param = pd.read_pickle(
        '/data/group/800463/param/factor_param/N_all_factor_zt_merge_v2212_%s.pkl' % (today)).reset_index('dt').drop('dt',
                                                                                                                  axis=1)
                                                                                                                
    factor_param_v8 = pd.read_pickle(
        '/data/group/800463/param/factor_param/N_all_factor_zt_merge_v2304_%s.pkl' % (today)).reset_index('dt').drop('dt',
                                                                                                                  axis=1)                                                                                                             
    eur_factor_param = pd.read_pickle(
        '/data/group/800463/param/factor_param/N_all_factor_zt_merge_v2304_%s.pkl' % (today)).reset_index('dt').drop('dt',
                                                                                                                  axis=1)                                                                                                                
    df, just_sell_list = get_sample_univ(today, white_list_list, black_list_list, grey_list_list)

    ceres_code_list = get_ceres_position(today)
    df['是否使用原有卖出逻辑'] = 0#df['股票代码'].apply(lambda x:1 if (x in ceres_code_list) else 0) #if envir == 'prod' else df['股票代码'].apply(lambda x: 0 if (int(x[-4]) % 2 == 0) else 1)
    df['订阅策略名称'] = 'AlphaRobotStrategy'
    df['订阅消息Key'] = df['股票代码']

    SH50_set = set(s.hset('INDEX', today, 'SZ50', 1)['stock'])

    p2_amt_dic = {'930': {'raw': 0, 'vote2': 0, 'vote3': 0, 'vote4': 0, 'vote5': 0, 'vote6': 0, 'vote7': 0},
                  '931': {'raw': 0, 'vote2': 0, 'vote3': 3e6, 'vote4': 3e6, 'vote5': 3e6, 'vote6': 3e6, 'vote7': 3e6}}

    p2_amt_dic_p = {'930': {'raw': 0, 'vote2': 0, 'vote3': 0, 'vote4': 0, 'vote5': 0, 'vote6': 0, 'vote7': 0},
                    '931': {'raw': 0, 'vote2': 0, 'vote3': 3e6, 'vote4': 3e6, 'vote5': 3e6, 'vote6': 3e6, 'vote7': 3e6}}

    print('Saturn策略规模', p2_amt_dic, p2_amt_dic_p)

    sp2_amt_dic = {'930': {'raw': 0, 'vote2': 0, 'vote3': 0, 'vote4': 0, 'vote5': 0, 'vote6': 0, 'vote7': 0},
                   '931': {'raw': 0, 'vote2': 0, 'vote3': 0, 'vote4': 0, 'vote5': 0, 'vote6': 0, 'vote7': 0}}

    sp2_amt_dic_p = {'930': {'raw': 0, 'vote2': 0, 'vote3': 0, 'vote4': 0, 'vote5': 0, 'vote6': 0, 'vote7': 0},
                     '931': {'raw': 0, 'vote2': 0, 'vote3': 0, 'vote4': 0, 'vote5': 0, 'vote6': 0, 'vote7': 0}}

    print('Ceres策略规模', sp2_amt_dic, sp2_amt_dic_p)

    # lower_limit_amt = 5e6
    # 用作Jupiter规模的下限
    NewL1 = {'amt': {'SH': 0, 'SZ': 0}, 'vol': {'SH': 0, 'SZ': 0}}  # 投票2
    NewL2 = {'amt': {'SH': 0, 'SZ': 0}, 'vol': {'SH': 0, 'SZ': 0}}  # 投票3
    NewL3 = {'amt': {'SH': 1900e4, 'SZ': 1900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}  # 投票4
    NewL4 = {'amt': {'SH': 1900e4, 'SZ': 1900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}  # 投票5
    NewL5 = {'amt': {'SH': 1900e4, 'SZ': 1900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}  # 投票6

    NL1 = {'amt': {'SH': 0, 'SZ': 0}, 'vol': {'SH': 30e5, 'SZ': 30e5}}
    NL2 = {'amt': {'SH': 900e4, 'SZ': 900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}
    NL3 = {'amt': {'SH': 900e4, 'SZ': 900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}
    NL4 = {'amt': {'SH': 900e4, 'SZ': 900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}
    NL5 = {'amt': {'SH': 900e4, 'SZ': 900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}

    NL1_add = {'amt': {'SH': 0, 'SZ': 0}, 'vol': {'SH': 30e5, 'SZ': 30e5}}
    NL2_add = {'amt': {'SH': 900e4, 'SZ': 900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}
    NL3_add = {'amt': {'SH': 900e4, 'SZ': 900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}
    NL4_add = {'amt': {'SH': 900e4, 'SZ': 900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}
    NL5_add = {'amt': {'SH': 900e4, 'SZ': 900e4}, 'vol': {'SH': 30e5, 'SZ': 30e5}}
   

    other_df = get_shares_data(list(df['股票代码']), today).rename(columns={'流通股本': '自由流通股本'})
    df = df.join(other_df['自由流通股本'], on='股票代码')

    # if envir == 'prod':
    #     df['重新下单等待时长（毫秒）'] = 10000  # df['股票代码'].apply(lambda x: 10000 if x[-2:]=='SZ' else 100)
    # else:
    df['mrisk重新下单等待时长(毫秒)'] = 1000
    df['对敲重新下单等待时长(毫秒)'] = 10

    df['前收盘价格'] = get_pre_close(list(df['股票代码']), today, use_self_preclose)
    df = df[(df['前收盘价格'] >= 2) | (df['股票代码'].isin(get_init_position(today, '54702', 'O45')))]
    print('删除2元以下股票后总数:%d' % (len(df)))
    ul_price_ser = cal_ul_price(df.set_index('股票代码')[['前收盘价格']])
    df['新时点触发价格'] = (ul_price_ser - 0.01).apply(lambda x: round(x, 2)).values

    df['参数目录'] = 'resources/JGStrategy/JupiterStrategy'
    df['JupiterNew模型目录'] = 'resources/JGStrategy/JupiterNewStrategy'
    df['允许买入开始时间'] = '09:30:00'
    df['允许卖出开始时间'] = '09:30:00'
    df['允许买入结束时间'] = '14:30:00'
    df['允许卖出结束时间'] = '14:55:00'
    df['取消订阅非必要行情时间'] = '23:30:00' if envir in ['uat', 'night'] else '15:00:00'

    cyb = df['股票代码'].apply(lambda x: x[:2] == '30')

    # df.loc[~cyb, '目标金额'] = df[['股票代码', '前收盘价格']].apply(lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * lastzt_2_vol['vol'][x['股票代码'][-2:]] + 1, lastzt_2_vol['amt'][x['股票代码'][-2:]]), axis=1)
    # df.loc[cyb, '目标金额'] = df[['股票代码', '前收盘价格']].apply(lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * lastzt_2_vol_300['vol'][x['股票代码'][-2:]] + 1, lastzt_2_vol_300['amt'][x['股票代码'][-2:]]), axis=1)


    df.loc[~cyb, 'NL1目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL1['vol'][x['股票代码'][-2:]] + 1,
                      NL1['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL1目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL1['vol'][x['股票代码'][-2:]] + 1,
                      NL1['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NL2目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL2['vol'][x['股票代码'][-2:]] + 1,
                      NL2['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL2目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL2['vol'][x['股票代码'][-2:]] + 1,
                      NL2['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NL3目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL3['vol'][x['股票代码'][-2:]] + 1,
                      NL3['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL3目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL3['vol'][x['股票代码'][-2:]] + 1,
                      NL3['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NL4目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL4['vol'][x['股票代码'][-2:]] + 1,
                      NL4['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL4目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL4['vol'][x['股票代码'][-2:]] + 1,
                      NL4['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NL5目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL5['vol'][x['股票代码'][-2:]] + 1,
                      NL5['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL5目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL5['vol'][x['股票代码'][-2:]] + 1,
                      NL5['amt'][x['股票代码'][-2:]]), axis=1)
    # -----------------------------------new-------------------------------
    df.loc[~cyb, 'NewL1目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NewL1['vol'][x['股票代码'][-2:]] + 1,
                      NewL1['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NewL1目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NewL1['vol'][x['股票代码'][-2:]] + 1,
                      NewL1['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NewL2目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NewL2['vol'][x['股票代码'][-2:]] + 1,
                      NewL2['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NewL2目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NewL2['vol'][x['股票代码'][-2:]] + 1,
                      NewL2['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NewL3目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NewL3['vol'][x['股票代码'][-2:]] + 1,
                      NewL3['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NewL3目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NewL3['vol'][x['股票代码'][-2:]] + 1,
                      NewL3['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NewL4目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NewL4['vol'][x['股票代码'][-2:]] + 1,
                      NewL4['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NewL4目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NewL4['vol'][x['股票代码'][-2:]] + 1,
                      NewL4['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NewL5目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NewL5['vol'][x['股票代码'][-2:]] + 1,
                      NewL5['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NewL5目标金额'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NewL5['vol'][x['股票代码'][-2:]] + 1,
                      NewL5['amt'][x['股票代码'][-2:]]), axis=1)
    # -----------------------------------n_add---------------------------
    df.loc[~cyb, 'NL1目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL1_add['vol'][x['股票代码'][-2:]] + 1,
                      NL1_add['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL1目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL1_add['vol'][x['股票代码'][-2:]] + 1,
                      NL1_add['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NL2目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL2_add['vol'][x['股票代码'][-2:]] + 1,
                      NL2_add['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL2目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL2_add['vol'][x['股票代码'][-2:]] + 1,
                      NL2_add['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NL3目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL3_add['vol'][x['股票代码'][-2:]] + 1,
                      NL3_add['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL3目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL3_add['vol'][x['股票代码'][-2:]] + 1,
                      NL3_add['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NL4目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL4_add['vol'][x['股票代码'][-2:]] + 1,
                      NL4_add['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL4目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL4_add['vol'][x['股票代码'][-2:]] + 1,
                      NL4_add['amt'][x['股票代码'][-2:]]), axis=1)

    df.loc[~cyb, 'NL5目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * NL5_add['vol'][x['股票代码'][-2:]] + 1,
                      NL5_add['amt'][x['股票代码'][-2:]]), axis=1)
    df.loc[cyb, 'NL5目标金额_add'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * NL5_add['vol'][x['股票代码'][-2:]] + 1,
                      NL5_add['amt'][x['股票代码'][-2:]]), axis=1)

    random.seed(0)
    random_rate_arr = np.array([random.uniform(0.96, 0.98) for i in range(len(df))])
    cols = ['NL1目标金额', 'NL2目标金额', 'NL3目标金额', 'NL4目标金额', 'NL5目标金额',
            'NewL1目标金额', 'NewL2目标金额', 'NewL3目标金额', 'NewL4目标金额', 'NewL5目标金额',
            'NL1目标金额_add', 'NL2目标金额_add', 'NL3目标金额_add', 'NL4目标金额_add', 'NL5目标金额_add']
    df[cols] = (df[cols].mul(random_rate_arr, axis=0)).astype(int)

    # 前5日成交额20%的约束
    df = df.join(factor_param['五日流动性限制额'], on='股票代码')
    df['当日触发前流动性限制系数'] = 0.25
    
    df['单笔订单所能打压的价格幅度'] = -0.01
    df['最高卖出对手盘下降档位'] = 2

    df['TICK交易量移动平均值的折减系数'] = 0.2
    df['开盘时刻挂单占比'] = 0.1

    ul_price_ser = cal_ul_price(df.set_index('股票代码')[['前收盘价格']])
    cover_vol = pd.DataFrame()
    cover_vol['涨停板封单覆盖量'] = ((15000000 / ul_price_ser).apply(lambda x: np.floor(x / 100) * 100))
    df = df.join(cover_vol, on='股票代码')

    if envir in ['uat', 'night']:
        # initPosition = {'000002.SZ': 100000, '300223.SZ': 500000, '600185.SH': 120000}
        initPosition = get_init_position(today, '54702', 'O45')
        initPosition = {key : min(vol, 1000000) for key, vol in initPosition.items()}
        init_amt_ser = get_init_amt(today, '54702', 'O45')
        all_postion = initPosition

        jupiter_position = {}  # get_jupiter_position(today)
    else:
        initPosition = get_init_position(today, '54702', 'O45')
        init_amt_ser = get_init_amt(today, '54702', 'O45')
        all_postion = {**initPosition, **get_init_position(today, '54702', 'O32')}
        jupiter_position = {}  # get_jupiter_position(today)

    just_sell_list = just_sell_list + list(init_amt_ser[init_amt_ser > 1300e4].index)
    print(len(initPosition))
    strong_dict = get_init_position(today, '3701', 'O32')

    if len(set(initPosition.keys()) & set(strong_dict.keys())) > 0:
        common_set = (set(initPosition.keys()) & set(strong_dict.keys()))
        print('强势股次新股与日内强势股存在共有的持仓%s，需要把这部分持仓一起给交易员卖出%s' % (common_set, '!' * 100))
        for key in common_set:
            initPosition.pop(key)

    df['期初可用仓位'] = df['股票代码'].apply(lambda x: 0 if x not in initPosition else initPosition[x])  # 实盘次日要改过来
    # 如果要把买入上限提升到160万股以上，需要把三个80万修改为95万
    cyb = df['股票代码'].apply(lambda x: x[:2] == '30')
    df.loc[~cyb, '单次下单最大股数'] = 950000
    df.loc[cyb, '单次下单最大股数'] = 300000
    df['交易所监控的较大额度'] = df['股票代码'].apply(lambda x: 900000 if x[-2:] == 'SH' else 2500000)
    df.loc[df['股票代码'].isin(SH50_set), '交易所监控的较大额度'] = 450000
    df['交易所监控的较大股数'] = df['股票代码'].apply(lambda x: 90000 if x[-2:] == 'SH' else 250000)
    df.loc[df['股票代码'].isin(SH50_set), '交易所监控的较大股数'] = 45000
    print(df[['交易所监控的较大额度', '交易所监控的较大股数']].iloc[0])
    df['交易所监控的巨大额度'] = 8000000
    df['交易所监控的巨大股数'] = 950000
    df['买入的巨大额度'] = 14000000
    df['买入的巨大股数'] = 3000000
    df['撤单监控的巨大额度'] = 8000000
    df['撤单监控的巨大股数'] = 950000

    df['交易所监控的较大额度(无拉抬)'] = 2500000
    df.loc[df['股票代码'].isin(SH50_set), '交易所监控的较大额度(无拉抬)'] = 1250000
    df['交易所监控的较大股数(无拉抬)'] = 250000
    df.loc[df['股票代码'].isin(SH50_set), '交易所监控的较大股数(无拉抬)'] = 125000
    df['买入成交量占比上边界(无拉抬)'] = 0.18
    df.loc[df['股票代码'].isin(SH50_set), '买入成交量占比上边界(无拉抬)'] = 0.125
    df['交易所监控的反向交易涨跌幅范围'] = df['股票代码'].apply(lambda x: 0.02 if x[-2:] == 'SH' else 0.035)

    df['一个TICK内的最大挂单次数'] = 1
    small_test = initPosition
    df['小单测试'] = 0  # sample_df['股票代码'].apply(lambda x: 1 if (x in small_test) or (x in ['000001.SZ', '600000.SH']) else 0)
    df['使用Quote累计成交量'] = df['股票代码'].apply(lambda x: 0 if x[0] == '3' else 1)
    df['动态切割交易所监控的数量'] = 3
    df['突破后涨停板挂单被防对敲后再次尝试次数'] = 30000

    df['是否进行下单'] = 1
    df['jupiter是否反向卖出'] = 0
    df['saturn和ceres是否反向买入'] = 0
    df['saturn和ceres是否反向卖出'] = 0
    df['saturn和ceres挂单后jupiter是否需要加仓'] = 0

    df['等待截面数据时间(秒)'] = 3
    df['距离第一次触发最大下单延时毫秒数'] = 3*60*1000#df['股票代码'].apply(lambda x: 10*1000 if x[-2:] == 'SH' else 5*1000)#300 * 1000 #if envir not in ['uat', 'night'] else 30000
    df['下单前Tick最大延时毫秒数'] = 10000000  # df['股票代码'].apply(lambda x: 1000 if x[-2:]=='SH' else 10000000) if envir not in ['night'] else int(864000000)
    df[
        '下单前Trade最大延时毫秒数'] = 10000000  # df['股票代码'].apply(lambda x: 500 if x[-2:]=='SH' else 10000000) if envir not in ['night'] else int(864000000)
    # df['接收积压行情最大系统耗时毫秒数'] = 20
    df['早盘延时tick截止时间点'] = '09:33:00'
    # df['短区间拉抬幅度lowPx使用截止时间点'] = '09:00:00'
    df['jupiter因子是否串行计算'] = 0  # if envir in ['prod', 'uat'] else 1
    df['模型预热次数'] = 5
    df['自营买单查询预热'] = 1  # df['股票代码'].apply(lambda x: (int(x[-5:-3]) % 3) == 0).astype(int)

    df['默认成交占比'] = 0.23
    df['默认成交占比上边界'] = 0.23

    df['最大涨跌幅度'] = df['股票代码'].apply(lambda x: 0.1 if x[:2] in ['00', '60'] else 0.2)

    # 拆单买入相关参数
    df['买入最大委托占比'] = 0.25
    df['买入下单版本'] = 1
    df['拆单笔数上限'] = df['股票代码'].apply(lambda x: 32 if x[:2] in ['30'] else 8)
    df['大单封涨停持续时间'] = 9 * 60
    df['大单封涨停间隔时间'] = 30

    # Jupiter下单相关参数
    df['JupiterN买入下单方式'] = 2  # df['股票代码'].apply(lambda x:0 if x[-2:]=='SH' else 2)
    df['JupiterNew买入下单方式'] = 2  # df['股票代码'].apply(lambda x:0 if x[-2:]=='SH' else 2) if envir == 'prod' else 2
    df['Jupiter策略启动组合'] = 2  # 0 JupiterNew;1 JupiterN;2 both


    df['mrisk拆单间隔毫秒数'] = 0#df['股票代码'].apply(lambda x: 2 if x[-2:] == 'SZ' else 3)
    df['mrisk下单模式'] = 1 #if envir in ['uat', 'night'] else 0

    # df['是否使用二次下单'] = df['股票代码'].apply(lambda x: 0 if x[-2:]=='SH' else 1)
    df = df.join(ul_price_ser, on='股票代码')
    df['Jupiter首次下单量下限'] = df['ul_price'].apply(lambda x: min(150000, 1500000 / x // 100 * 100))
    df['Jupiter首次下单市场占比'] = 0.15
    df['最近一笔查询是否使用委托'] = 0
    df['单次下单最大股数'] = df[['单次下单最大股数','ul_price']].apply(lambda x: min(x['单次下单最大股数'], (7800000 / x['ul_price']) // 100 * 100), axis=1)
    df = df.drop('ul_price', axis=1)


    ycbd_5_stocklist = pd.read_excel(r'/data/group/800463/stock_list/ycbd_list/ycbd_list_%s.xlsx'%today)
    ycbd_5_stocklist = ycbd_5_stocklist['stk_code'].values.tolist()
    df['单票持仓总规模上限'] = df[['股票代码']].apply(lambda x: 900e4 if x['股票代码'] in ycbd_5_stocklist else 2800e4, axis = 1)
    cyb_tmp = df['股票代码'].apply(lambda x: x[:2] == '30')
#    df.loc[~cyb_tmp, '单票持仓总规模上限'] = df[['股票代码', '前收盘价格','单票持仓总规模上限']].apply(
#        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * 380e4 + 1,
#                      x['单票持仓总规模上限']), axis=1)
#    df.loc[cyb_tmp, '单票持仓总规模上限'] = df[['股票代码', '前收盘价格','单票持仓总规模上限']].apply(
#        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * 380e4 + 1,
#                      x['单票持仓总规模上限']), axis=1)
    df.loc[~cyb_tmp, '单票持仓总规模上限'] = df[['股票代码', '前收盘价格','单票持仓总规模上限']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * 600e4 + 1,
                      x['单票持仓总规模上限']) if (x['股票代码'] not in ycbd_5_stocklist) else min(np.floor(x['前收盘价格'] * 100 * 1.1 + 0.5) / 100 * 190e4 + 1,
                      x['单票持仓总规模上限']), axis=1)
    df.loc[cyb_tmp, '单票持仓总规模上限'] = df[['股票代码', '前收盘价格','单票持仓总规模上限']].apply(
        lambda x: min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * 600e4 + 1,
                      x['单票持仓总规模上限']) if (x['股票代码'] not in ycbd_5_stocklist) else min(np.floor(x['前收盘价格'] * 100 * 1.2 + 0.5) / 100 * 190e4 + 1,
                      x['单票持仓总规模上限']), axis=1)

    df['最后一笔买单拉升幅度阈值'] = 0.025
    df['强制撤单时间点'] = '14:55:00'
    df['是否触发预热'] = 0
    df['单标的tick截取毫秒数'] = df['股票代码'].apply(lambda x: 1000 if x[-2:] == 'SH' else 2000)
    df['JupiterZ快速卖出信号阈值'] = 4
    df['是否验证模式'] = 0
    df.loc[df['期初可用仓位']>0,'是否验证模式'] = 0
    

    df['Jupiter拆单v2单笔下单金额上限'] = 2000000

    # 静态信息参数
    df['交易日期'] = today
    df['是否使用静态数据查询'] = 1 if envir == 'prod' else 0

    # Saturn 相关参数
    df['saturn和ceres单次最小买入金额'] = 10000
    df['单笔订单所能拉升的价格幅度'] = 0.01
    df['最高买入对手盘上升档位'] = 2
    df['买入成交量占比上边界'] = df['股票代码'].apply(lambda x: 0.18 if x[-2:] == 'SH' else 0.18)
    df.loc[df['股票代码'].isin(SH50_set), '买入成交量占比上边界'] = 0.125
    df['交易所监控的时间长度(秒)'] = 185
    # df['短区间拉抬幅度时间长度(秒)'] = 4

    df['时钟延迟毫秒'] = 100
    pct_dic = {'SH50': 0.009, 'other': 0.019}
    df['交易所监控的涨跌幅范围'] = df[['股票代码', '前收盘价格']].apply(
        lambda x: min(pct_dic['SH50'], 0.01 - 0.02 / x['前收盘价格']) if x['股票代码'] in SH50_set else min(pct_dic['other'],
                                                                                                   0.02 - 0.02 / x[
                                                                                                       '前收盘价格']),
        axis=1)
    # ---------------------------------------------saturn因子数据---------------------------------------------------------
    p2_param = pd.read_pickle('/data/group/800463/param/factor_param/saturn_param_v6_%s.pkl' % (today)).loc[pd.Timestamp(today)]
    p2_param['saturn_pre_close'] = get_pre_close(list(p2_param.index), today, use_self_preclose)
    p2_param['saturn_float_shares'] = other_df['自由流通股本']
    p2_param['saturn_pat_factor_p2'] = 0

    p2_factor_param_list = list(p2_param.index)
    df['saturn历史因子'] = df['股票代码'].apply(
        lambda x: param_str(p2_param.loc[x], envir) if x in p2_factor_param_list else '')

    # ---------------------------------------------ceres因子数据----------------------------------------------------------
    sp2_param = pd.read_pickle('/data/group/800463/param/factor_param/ceres_param_v3_%s.pkl' % (today)).loc[pd.Timestamp(today)]
    sp2_param['saturn_pre_close'] = get_pre_close(list(sp2_param.index), today, use_self_preclose)
    sp2_param['saturn_float_shares'] = other_df['自由流通股本']

    sp2_factor_param_list = []
    df['ceres历史因子'] = df['股票代码'].apply(
        lambda x: param_str(sp2_param.loc[x], envir) if x in sp2_factor_param_list else '')

    # ---------------------------------------------sell因子数据----------------------------------------------------------
    sell_param = pd.read_pickle('/data/group/800463/param/factor_param/sell_param_v1_%s.pkl' % (today)).loc[pd.Timestamp(today)]
    sell_param['saturn_pre_close'] = get_pre_close(list(sell_param.index), today, use_self_preclose)
    sell_param['saturn_float_shares'] = other_df['自由流通股本']

    sell_factor_param_list = list(sell_param.index)
    df['sell历史因子'] = df['股票代码'].apply(
        lambda x: param_str(sell_param.drop(['jpt_ZT_Time','jpt_high_price','jpt_ul_price','jpt_open_is_zt'], axis=1).loc[x], envir) if x in sell_factor_param_list else '')
        
    # -----------------------------------------------打印参数-------------------------------------------------------------
    df['自营接口异常是否打印客户端'] = 0 if envir == 'prod' else 1
    df['是否打印Trade信息'] = 0  # if envir == 'prod' else df['股票代码'].apply(lambda x:int(x[5])==3).astype(int)
    if envir == 'night':
        df['是否打印Trade信息'] = 0

    # --------------------------------------------Saturn参数sheet页-------------------------------------------------------
    saturn_df_list = []
    saturn_code_list = list(
        set(df[df['saturn历史因子'] != '']['股票代码']) & set(p2_param[p2_param['saturn_after_not_ul_len'] > 10].index))
    saturn_code_list = list(set(saturn_code_list) - set(just_sell_list))

    saturn_code_list.sort()
    model_dic = {'930': "",
                 '931': 'resources/JGStrategy/SaturnStrategy/SecondModel'}
    for saturn_time in saturn_list:  # , '931']:
        s_df = pd.DataFrame()
        s_df['股票代码'] = saturn_code_list
        s_df['saturn节点标识'] = saturn_time

        if saturn_time == '930':
            sh_sz = s_df['股票代码'].apply(lambda x: x[-2:])
            s_df.loc[sh_sz == 'SH', '计算和预测开始时间'] = get_random_time(len(s_df.loc[sh_sz == 'SH']), '092800', '092900')
            s_df.loc[sh_sz == 'SZ', '计算和预测开始时间'] = get_random_time(len(s_df.loc[sh_sz == 'SZ']), '092705', '092800')
            s_df['买入开始时间'] = '09:30'
            s_df['o2pre阈值'] = s_df['股票代码'].apply(lambda x: -100 if x[0] != '3' else -100)
        elif saturn_time == '931':
            s_df['计算和预测开始时间'] = '09:31:00'
            s_df['买入开始时间'] = '09:31'
        s_df['saturn策略样本筛选阈值'] = -0.3277283212327676
        
        s_df['区间目标金额'] = s_df['股票代码'].apply(
            lambda x: p2_amt_dic_p[saturn_time]['raw'] if x in jupiter_position else p2_amt_dic[saturn_time]['raw'])
        s_df['投票2目标金额'] = s_df['股票代码'].apply(
            lambda x: p2_amt_dic_p[saturn_time]['vote2'] if x in jupiter_position else p2_amt_dic[saturn_time]['vote2'])
        s_df['投票3目标金额'] = s_df['股票代码'].apply(
            lambda x: p2_amt_dic_p[saturn_time]['vote3'] if x in jupiter_position else p2_amt_dic[saturn_time]['vote3'])
        s_df['投票4目标金额'] = s_df['股票代码'].apply(
            lambda x: p2_amt_dic_p[saturn_time]['vote4'] if x in jupiter_position else p2_amt_dic[saturn_time]['vote4'])
        s_df['投票5目标金额'] = s_df['股票代码'].apply(
            lambda x: p2_amt_dic_p[saturn_time]['vote5'] if x in jupiter_position else p2_amt_dic[saturn_time]['vote5'])
        s_df['投票6目标金额'] = s_df['股票代码'].apply(
            lambda x: p2_amt_dic_p[saturn_time]['vote6'] if x in jupiter_position else p2_amt_dic[saturn_time]['vote6'])
        s_df['投票大于等于7目标金额'] = s_df['股票代码'].apply(
            lambda x: p2_amt_dic_p[saturn_time]['vote7'] if x in jupiter_position else p2_amt_dic[saturn_time]['vote7'])


        s_df['投票2目标金额add'] = 0
        s_df['投票3目标金额add'] = 0
        s_df['投票4目标金额add'] = 0
        s_df['投票5目标金额add'] = 0
        s_df['投票6目标金额add'] = 0
        s_df['投票大于等于7目标金额add'] = 0

        s_df['模型目录'] = model_dic[saturn_time]
        saturn_df_list.append(s_df)

    if len(saturn_df_list) > 0:
        saturn_df = pd.concat(saturn_df_list)[['股票代码', 'saturn节点标识', '计算和预测开始时间', '买入开始时间', 'o2pre阈值','saturn策略样本筛选阈值',
                                               '区间目标金额', '投票2目标金额', '投票3目标金额', '投票4目标金额', '投票5目标金额', '投票6目标金额',
                                               '投票大于等于7目标金额',
                                               '投票2目标金额add', '投票3目标金额add', '投票4目标金额add', '投票5目标金额add', '投票6目标金额add',
                                               '投票大于等于7目标金额add',
                                               '模型目录']]

        yz_tz_list = list(p2_param[p2_param['saturn_lzt_day_pattern'].apply(lambda x: x in [1, 2])].index)
        saturn_df = saturn_df[saturn_df['股票代码'].apply(lambda x: (x not in yz_tz_list))]
        print('一字板T字板不参与信号触发')

        saturn_df = saturn_df[saturn_df['股票代码'].apply(lambda x: (x not in all_postion) or (x in jupiter_position))]
        print('持仓非Jupiter样本不参与saturn信号触发！！')
    else:
        saturn_df = pd.DataFrame(columns=['股票代码', 'saturn节点标识', '计算和预测开始时间', '买入开始时间', 'o2pre阈值',
                                          '区间目标金额', '投票2目标金额', '投票3目标金额', '投票4目标金额', '投票5目标金额', '投票6目标金额',
                                          '投票大于等于7目标金额',
                                          '投票2目标金额add', '投票3目标金额add', '投票4目标金额add', '投票5目标金额add', '投票6目标金额add',
                                          '投票大于等于7目标金额add',
                                          '模型目录'])

    p2_param_filter=p2_param[(p2_param['saturn_after_not_ul_len']>10)&(p2_param['saturn_lzt_day_pattern'].isin([3,4]))]
    saturn_subscribe = p2_param_filter[['saturn_after_not_ul_len', 'saturn_lzt_day_pattern']].reset_index().rename(
        columns={'Ticker': '股票代码', 'saturn_after_not_ul_len': '上市一字涨停开板后交易日数量', 'saturn_lzt_day_pattern': '前一个交易日形态'})

    # -----------------------------------------------Ceres参数sheet页-----------------------------------------------------
    ceres_df_list = []
    ceres_code_list = list(
        set(df[df['ceres历史因子'] != '']['股票代码']) & set(sp2_param[sp2_param['after_not_ul_len'] > 10].index))
    raw_ceres_code_list = ceres_code_list.copy()
    ceres_code_list = list(set(ceres_code_list) - set(just_sell_list))

    ceres_code_list.sort()
    ceres_model_dic = {'930': '',
                       '931': 'resources/JGStrategy/CeresStrategy/SecondModel'}

    for ceres_time in ceres_list:  # , '931']:
        s_df = pd.DataFrame()
        s_df['股票代码'] = ceres_code_list
        s_df['ceres节点标识'] = ceres_time

        if ceres_time == '930':
            sh_sz = s_df['股票代码'].apply(lambda x: x[-2:])
            s_df.loc[sh_sz == 'SH', '计算和预测开始时间'] = get_random_time(len(s_df.loc[sh_sz == 'SH']), '092800', '092900')
            s_df.loc[sh_sz == 'SZ', '计算和预测开始时间'] = get_random_time(len(s_df.loc[sh_sz == 'SZ']), '092705', '092800')
            s_df['买入开始时间'] = '09:30'
            # s_df['o2pre阈值'] = s_df['股票代码'].apply(lambda x: 0.08 if x[0] != '3' else 0.16)
        elif ceres_time == '931':
            s_df['计算和预测开始时间'] = '09:31:00'
            s_df['买入开始时间'] = '09:31'

        s_df['区间目标金额'] = s_df['股票代码'].apply(
            lambda x: sp2_amt_dic_p[ceres_time]['raw'] if x in jupiter_position else sp2_amt_dic[ceres_time]['raw'])
        s_df['投票2目标金额'] = s_df['股票代码'].apply(
            lambda x: sp2_amt_dic_p[ceres_time]['vote2'] if x in jupiter_position else sp2_amt_dic[ceres_time]['vote2'])
        s_df['投票3目标金额'] = s_df['股票代码'].apply(
            lambda x: sp2_amt_dic_p[ceres_time]['vote3'] if x in jupiter_position else sp2_amt_dic[ceres_time]['vote3'])
        s_df['投票4目标金额'] = s_df['股票代码'].apply(
            lambda x: sp2_amt_dic_p[ceres_time]['vote4'] if x in jupiter_position else sp2_amt_dic[ceres_time]['vote4'])
        s_df['投票5目标金额'] = s_df['股票代码'].apply(
            lambda x: sp2_amt_dic_p[ceres_time]['vote5'] if x in jupiter_position else sp2_amt_dic[ceres_time]['vote5'])
        s_df['投票6目标金额'] = s_df['股票代码'].apply(
            lambda x: sp2_amt_dic_p[ceres_time]['vote6'] if x in jupiter_position else sp2_amt_dic[ceres_time]['vote6'])
        # s_df['投票大于等于7目标金额'] = s_df['股票代码'].apply(
        #     lambda x: sp2_amt_dic_p[ceres_time]['vote7'] if x in jupiter_position else sp2_amt_dic[ceres_time]['vote7'])


        s_df['模型目录'] = ceres_model_dic[ceres_time]
#        ceres_df_list.append(s_df)

    if len(ceres_df_list) > 0:
        ceres_df = pd.concat(ceres_df_list)[['股票代码', 'ceres节点标识', '计算和预测开始时间', '买入开始时间', '区间目标金额',
                                             '投票2目标金额', '投票3目标金额', '投票4目标金额', '投票5目标金额', '投票6目标金额',
                                             '模型目录']]

        # ceres_df = ceres_df[ceres_df['股票代码'].apply(lambda x: (x not in all_postion) or (x in jupiter_position))]
        ceres_df = ceres_df[ceres_df['股票代码'].apply(lambda x: (x not in all_postion))]
        print('非Jupiter持仓样本不参与ceres信号触发！！')
    else:
        ceres_df = pd.DataFrame(columns=['股票代码', 'ceres节点标识', '计算和预测开始时间', '买入开始时间', 'o2pre阈值',
                                         '区间目标金额', '投票2目标金额', '投票3目标金额', '投票4目标金额', '投票5目标金额', '投票6目标金额',
                                         '投票2目标金额add', '投票3目标金额add', '投票4目标金额add', '投票5目标金额add', '投票6目标金额add',
                                         '模型目录'])

    ceres_subscribe = sp2_param[['after_not_ul_len']].reset_index().rename(
        columns={'Ticker': '股票代码', 'after_not_ul_len': '上市一字涨停开板后交易日数量'})


    # --------------------------------------------Sell参数sheet页-------------------------------------------------------
    sell_select_condition = ((sell_param['jpt_ZT_Time'] == sell_param['jpt_ZT_Time'])
                  & (sell_param['jpt_ZT_Time'] >= 93000000)
                  & (sell_param['jpt_open_is_zt'] == 0)
                  & (sell_param['jpt_high_price'] < (sell_param['jpt_ul_price'])))
    sell_df_list = []
    sell_code_list = list(
        set(df[df['sell历史因子'] != '']['股票代码']) & set(sell_param[(sell_param['saturn_after_not_ul_len'] > 10) & sell_select_condition].index))

    sell_code_list.sort()
    model_dic = {'930': ["",""],
                 '931': ['resources/JGStrategy/SellStrategy/v1FirstModel','resources/JGStrategy/SellStrategy/v3FirstModel']}
    for sell_time in sell_list:
        s_df = pd.DataFrame()
        s_df['股票代码'] = sell_code_list
        s_df['sell节点标识'] = sell_time

        if sell_time == '930':
            sh_sz = s_df['股票代码'].apply(lambda x: x[-2:])
            s_df.loc[sh_sz == 'SH', '计算和预测开始时间'] = get_random_time(len(s_df.loc[sh_sz == 'SH']), '092800', '092900')
            s_df.loc[sh_sz == 'SZ', '计算和预测开始时间'] = get_random_time(len(s_df.loc[sh_sz == 'SZ']), '092705', '092800')
            s_df['v1阈值'] = 4
            s_df['v3阈值'] = 8
        elif sell_time == '931':
            s_df['计算和预测开始时间'] = '09:31:00'
            s_df['v1阈值'] = 4
            s_df['v3阈值'] = 8

        s_df['v1模型目录'] = model_dic[sell_time][0]
        s_df['v3模型目录'] = model_dic[sell_time][1]
        sell_df_list.append(s_df)

    if len(sell_df_list) > 0:
        sell_df = pd.concat(sell_df_list)[['股票代码', 'sell节点标识', '计算和预测开始时间', 'v1阈值', 'v3阈值','v1模型目录','v3模型目录']]
        yz_tz_list = list(sell_param[sell_param['saturn_lzt_day_pattern'].apply(lambda x: x in [1, 2])].index)
        sell_df = sell_df[sell_df['股票代码'].apply(lambda x: (x not in yz_tz_list))]
        print('一字板T字板不参与sell信号触发')
        
        sell_df = sell_df[sell_df['股票代码'].apply(lambda x: (x in all_postion))]
        print('只有持仓样本参与sell信号触发！！')


    else:
        sell_df = pd.DataFrame(columns=['股票代码', 'sell节点标识', '计算和预测开始时间', 'v1阈值', 'v3阈值','v1模型目录','v3模型目录'])

   
    sell_param_filter=sell_param[(sell_param['saturn_after_not_ul_len']>10)&(sell_param['saturn_lzt_day_pattern'].isin([3,4]))]
    sell_subscribe = sell_param_filter[['saturn_after_not_ul_len', 'saturn_lzt_day_pattern']].reset_index().rename(columns={'Ticker': '股票代码', 'saturn_after_not_ul_len': '上市一字涨停开板后交易日数量', 'saturn_lzt_day_pattern': '前一个交易日形态'})
    # -------------------------------------------------------------------------------------------------------------------
    # Jupiter因子参数
    for factor_param_tmp in [factor_param, factor_param_v8]:
        factor_param_tmp['pre_close'] = get_pre_close(list(factor_param_tmp.index), today, use_self_preclose)
        if ('EFS_factor' not in factor_param_tmp.columns) or ('hml_factor' not in factor_param_tmp.columns) or (
                'k3_factor' not in factor_param_tmp.columns):
            print('分场景指标缺失！！！！！！！！！！！！！！')
        factor_param_tmp['ul_price'] = cal_ul_price(factor_param_tmp[['pre_close']], key='pre_close')
        factor_param_tmp['float_shares'] = other_df['自由流通股本']
    factor_param_list = list(factor_param.index)
    if 'hml_factor' not in eur_factor_param.columns:
            print('europa分场景指标缺失！！！！！！！！！！！！！！')
    eur_factor_param['pre_close'] = get_pre_close(list(eur_factor_param.index), today, use_self_preclose)
    eur_factor_param['ul_price'] = cal_ul_price(eur_factor_param[['pre_close']], key='pre_close')
    eur_factor_param_list = list(eur_factor_param.index)


    df['因子数据'] = df['股票代码'].apply(lambda x: param_str(factor_param.loc[x], envir) if x in factor_param_list else np.nan)
    df['europa历史因子'] = df['股票代码'].apply(lambda x: param_str(eur_factor_param.loc[x], envir) if x in eur_factor_param_list else np.nan)
    df['前一日是否收盘涨停'] = df['股票代码'].apply(lambda x: factor_param['last_is_zt'].loc[x])
    df.loc[df['前一日是否收盘涨停']>0, '因子数据'] = df.loc[df['前一日是否收盘涨停']>0].apply(lambda x: param_str(factor_param_v8.loc[x['股票代码']], envir) if x['股票代码'] in list(factor_param_v8.index) else np.nan, axis = 1)


    df.loc[df['前一日是否收盘涨停']>0, 'Jupiter策略启动组合'] = 1
    df.loc[df['股票代码'].isin(yz_tz_list), 'JupiterZ快速卖出信号阈值'] = 14

    df['是否需要买入'] = df[['股票代码', '前一日是否收盘涨停']].apply(
        lambda x: 0 if ((x['股票代码'][:2] in ['30']) and (x['前一日是否收盘涨停'])) else 1, axis=1)

    if envir in ['uat', 'night']:
#        df.loc[df['前一日是否收盘涨停']==1, '期初可用仓位'] = 1000000
        df['期初可用仓位'] = 0
        # print('ceres样本调整持仓!!!!!!!!!!!!!')

    # 调整只需要卖出不需要买入的个股
    for single_code in set(just_sell_list):
        print(single_code, '只卖出不进行买入！！！！！！！！')
        df.loc[df['股票代码'] == single_code, '是否需要买入'] = 0
        df.loc[df['股票代码'] == single_code, cols] = 0
    # 调整前日涨停的样本
    df.loc[(df['前一日是否收盘涨停']>0) & (df['股票代码'].apply(lambda x:x[0]!='3')), '是否需要买入'] = 1

    has_nan = df['因子数据'].apply(lambda x: ':nan' in x)
    has_inf = df['因子数据'].apply(lambda x: ':inf' in x)
    if (has_nan.sum() > 0) or (has_inf.sum() > 0):
        print('因子中有nan样本个数:%d;因子中有inf样本个数:%d!!!!!!!!!!!!!!!!!!!' % (has_nan.sum(), has_inf.sum()))
        print(get_key_word(df[has_nan | has_inf][['股票代码', '因子数据']].set_index('股票代码')))
        df = df[(has_nan == False) & (has_inf == False)]
        print('删除因子为nan行之后股票总数：', len(df))

    ten_ul_break_set = list(factor_param[factor_param['after_not_ul_len'] <= 10].index)
    in_10_ul_break_set = df['股票代码'].apply(lambda x: x in ten_ul_break_set)
    df = df[~in_10_ul_break_set]
    print('删除新股开板10日日后股票总数：', len(df))

    fifteen_after_ipo_set = list(factor_param[factor_param['list_len'] <= 15].index)
    fifteen_after_ipo_set = [code for code in fifteen_after_ipo_set if code[:2] == '30']
    in_15_ipo_set = df['股票代码'].apply(lambda x: x in fifteen_after_ipo_set)
    df = df[~in_15_ipo_set]
    print('删除创业板上市15日后股票总数：', len(df))

    df['自由流通股本'] = df['自由流通股本']
    df = df[df.isnull().sum(axis=1) == 0]
    print('删除nan行之后股票总数：', len(df))

    except_set = (set(initPosition.keys()) - set(df['股票代码']))
    if len(except_set) != 0:
        print('有持仓股票没有在实例中!!!!!!!', except_set)

    saturn_df = saturn_df[saturn_df['股票代码'].isin(df['股票代码'].to_list())]
    ceres_df = ceres_df[ceres_df['股票代码'].isin(df['股票代码'].to_list())]
    sell_df = sell_df[sell_df['股票代码'].isin(df['股票代码'].to_list())]

#    code_list = saturn_df['股票代码'].to_list() + ceres_df['股票代码'].to_list()
    code_list = sorted(list(set(saturn_df['股票代码'].to_list() + ceres_df['股票代码'].to_list())))
    print('saturn codes: ', len(code_list), code_list)
    df.loc[df['股票代码'].isin(code_list), '是否验证模式'] = 0
    # df.loc[df['股票代码'].isin(code_list), '是否使用mrisk拉抬打压风控'] = 1
    # df.loc[df['是否使用mrisk拉抬打压风控']==1, '重新下单等待时长（毫秒）'] = 10000

    check(today, df, initPosition, factor_param)

    prepare_dic = pd.read_pickle('/data/group/800463/param/factor_param/prepare_dic_v2212_%s.pkl' % (today))
    for col in ['sel_lastday_o2ul因子前N日之和', 'sel_lastday_o2ul因子数据长度', 'last_ul_open_excess_pct_sum因子前N日之和',
                'last_ul_open_excess_pct_sum因子数据长度', 'pat3_o2ul_mean5因子样本o2ul前4日之和', 'pat3_o2ul_mean5因子样本前4日个数',
                'lastday_pat4com因子前N日之和', 'lastday_pat4com因子数据长度', '形态4 T-3日~T-2日o2ul之和', '形态2 T-3日~T-2日o2ul之和',
                'T-3日~T-1日形态2样本总数量', 'T-3日~T-1日形态4样本总数量']:
        df[col] = prepare_dic[col]
    index = pd.DataFrame(['000300.SH', '000852.SH', '399101.SZ'], columns=['股票代码'])

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    excel_writer = pd.ExcelWriter(file_name)
    df = df.join(prepare_dic['Saturn策略历史数据'].fillna(0), on='股票代码')
    # print('此处的Saturn策略因子暂时fillna！！！！！！！此时nan数量', df[['过去60日开盘成交额均值', '前日半小时换手分位数', '前日非集合竞价成交额']].isnull().sum().sum())
    if envir == 'night':
        x = get_max_and_high_data(df['股票代码'].to_list(), today)
        df = df.join(x, on='股票代码')
        df = df[(df['high'] >= df['maxpx'].apply(lambda x: round(x - 0.01, 2))) | (df['saturn历史因子'] != '') | (
                    df['ceres历史因子'] != '')].drop(['maxpx', 'high'], axis=1)
        # df = df[(df['saturn历史因子'] != '')].drop(['maxpx', 'high'], axis=1)
        # df = df[(df['saturn历史因子'] != '') | (df['ceres历史因子'] != '')].drop(['maxpx', 'high'], axis=1)
    df.to_excel(excel_writer, sheet_name='InitialBasicParam', index=None)
    index.to_excel(excel_writer, sheet_name='指数', index=None)
    prepare_dic['T-1日涨停股票'].to_excel(excel_writer, sheet_name='T-1日涨停股票', index=None)
    prepare_dic['T-1日非一字涨停的涨停股票'].to_excel(excel_writer, sheet_name='T-1日非一字涨停的涨停股票', index=None)
    prepare_dic['T-1日触板股票'].to_excel(excel_writer, sheet_name='T-1日触板股票', index=None)
    prepare_dic['T-1日形态3股票'].to_excel(excel_writer, sheet_name='T-1日形态3股票', index=None)
    prepare_dic['T-1日形态4股票'].to_excel(excel_writer, sheet_name='T-1日形态4股票', index=None)
    prepare_dic['T-1日筛选后形态4股票'].to_excel(excel_writer, sheet_name='T-1日筛选后形态4股票', index=None)
    prepare_dic['T-1日筛选后形态2股票'].to_excel(excel_writer, sheet_name='T-1日筛选后形态2股票', index=None)
    prepare_dic['T-1日开盘非涨停收盘涨停股票'].to_excel(excel_writer, sheet_name='T-1日开盘非涨停收盘涨停股票', index=None)
    prepare_dic['T-1日全部触板股票'].to_excel(excel_writer, sheet_name='T-1日全部触板股票', index=None)

    stock_list = df['股票代码'].to_list()
    prepare_dic['全部股票数据'] = prepare_dic['全部股票数据'][prepare_dic['全部股票数据']['股票代码'].apply(lambda x: x in stock_list)]

    if use_self_preclose:
        stock_inf = prepare_dic['股票数据']
        stock_inf['self_昨收价'] = get_pre_close(list(stock_inf['股票代码']), today, use_self_preclose)
        stock_inf.loc[stock_inf['股票代码'].apply(lambda x: x in ['000300.SH', '000852.SH', '399101.SZ']), 'self_昨收价'] = \
            stock_inf['昨收价']
        stock_inf['self_昨日最高价'] = (stock_inf['self_昨收价'] / stock_inf['昨收价'] * stock_inf['昨日最高价']).apply(
            lambda x: np.floor(x * 100 + 0.5) / 100)
        a = stock_inf[['股票代码', 'self_昨收价', 'self_昨日最高价','昨日流通股份']].rename(columns={'self_昨收价': '昨收价', 'self_昨日最高价': '昨日最高价'})
        a.to_excel(excel_writer, sheet_name='股票数据', index=None)

        stock_inf = prepare_dic['全部股票数据']
        stock_inf['self_昨收价'] = get_pre_close(list(stock_inf['股票代码']), today, use_self_preclose)
        stock_inf['self_昨日最高价'] = (stock_inf['self_昨收价'] / stock_inf['昨收价'] * stock_inf['昨日最高价']).apply(
            lambda x: np.floor(x * 100 + 0.5) / 100)
        a = stock_inf[['股票代码', 'self_昨收价', 'self_昨日最高价']].rename(columns={'self_昨收价': '昨收价', 'self_昨日最高价': '昨日最高价'})
        a.to_excel(excel_writer, sheet_name='全部股票数据', index=None)
    else:
        prepare_dic['股票数据'].to_excel(excel_writer, sheet_name='股票数据', index=None)
        prepare_dic['全部股票数据'].to_excel(excel_writer, sheet_name='全部股票数据', index=None)

    print('！！！！！！！！saturn与sell重合票：', set(saturn_df['股票代码']).intersection(set(sell_df['股票代码'])))
    print('理应启动的sell-实际启动的sell：', set(df[(df['期初可用仓位']>0) & (df['前一日是否收盘涨停']==1)]['股票代码'])-set(sell_df['股票代码']))
    print('实际启动的sell-理应启动的sell：', set(sell_df['股票代码']) - set(df[(df['期初可用仓位']>0) & (df['前一日是否收盘涨停']==1)]['股票代码']))
    saturn_df.to_excel(excel_writer, sheet_name='saturn配置参数', index=None)
    saturn_subscribe.fillna(-1).to_excel(excel_writer, sheet_name='saturn截面订阅列表', index=None)
    ceres_df.to_excel(excel_writer, sheet_name='ceres配置参数', index=None)
    ceres_subscribe.fillna(-1).to_excel(excel_writer, sheet_name='ceres截面订阅列表', index=None)
    sell_df.to_excel(excel_writer, sheet_name='sell配置参数', index=None)
    sell_subscribe.fillna(-1).to_excel(excel_writer, sheet_name='sell截面订阅列表', index=None)
    excel_writer.save()
    x = pd.read_excel(file_name, sheet_name=None)
    check_name(x)
    df[['股票代码','saturn历史因子']].to_pickle(file_name.replace('.xlsx','_saturn.pkl'))



if __name__ == '__main__':
    today = dt.datetime.now().strftime('%Y%m%d')
    envir = 'prod'
    generate(today, envir)
