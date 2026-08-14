# -*- coding: utf-8 -*-
# @Time    : 2019/12/24 13:36
# @Author  : wangweidi
import numpy as np
import pandas as pd
import datetime as dt

def hf_preprocessing(data_type, md_df):
    if data_type == 'TransactionAllDay':
        use_col = ['MDDate', 'MDTime', 'TradeIndex', 'TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice',
                   'TradeQty', 'TradeMoney', 'HTSCSecurityID']
        md_df = md_df[use_col]
        md_df['MDTime'], md_df['MDDate'] = md_df['MDTime'].astype(int), md_df['MDDate'].astype(int)
        return md_df

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
    elif time1 < 93000000:
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=4*60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)

# def cal_Basic_zt(mdp, stock, date, pre_close, close, tolerance_period=10):
#     all_md_df = mdp.get_data_by_date('Transaction', stock, date)
#     all_md_df = all_md_df.query('MDTime <= "150000000"')
#     all_md_df = all_md_df.sort_values(by='TradeIndex', ascending=True)
#     all_md_df = hf_preprocessing('TransactionAllDay', all_md_df)
#     ul_price = np.floor(pre_close * 100 * 1.2 + 0.5) / 100 if ((date>='20200824') and (stock[:2]=='30')) | (stock[:3]=='688') else np.floor(pre_close * 100 * 1.1 + 0.5) / 100
#     all_md_df = all_md_df[all_md_df['TradePrice'] > 0]
#     all_md_df['LastTradePrice'] = all_md_df['TradePrice'].shift(1)
#     all_md_df['to_zt'] = (all_md_df['LastTradePrice'] < ul_price) & (all_md_df['TradePrice'] == ul_price)
#     # 分别需要排除9:30和13:00涨停的样本，因为无法参与，因此这两个时刻的数据要删掉
#     md_df = all_md_df[(all_md_df['MDTime'] > 93000000) & (all_md_df['MDTime'] <= 145700000) & (all_md_df['MDTime'] != 130000000)]
#     if md_df['to_zt'].sum() > 0:
#         ZT_Time, is_zt = md_df[md_df['to_zt'] == True].MDTime.min(), True
#     else: # 未实际突破
#         ZT_Time, is_zt = np.nan, False
#
#     high_price = all_md_df[all_md_df['MDTime'] < ZT_Time]['TradePrice'].max()
#     high_price = pre_close if np.isnan(high_price) else high_price
#
#     df = pd.DataFrame([[ZT_Time, is_zt, high_price, ul_price,]], columns=['ZT_Time', 'is_zt', 'high_price', 'ul_price'])
#     df.index = pd.Index([(pd.Timestamp(date), stock)], name=['dt', 'Ticker'])
#     if np.isnan(ZT_Time):
#         pattern_df = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan]], columns=['label_pattern', 'label_firstUL_end_Time', 'label_lastUL_Time', 'label_lastUL_end_Time'])
#     else:
#         if (stock[-2:] == 'SH') and (date < '20180820'): # 老规则，强行变成尾盘集合竞价
#             all_md_df.loc[all_md_df['MDTime'] > 145700000, 'TradePrice'] = close
#         pattern_df = cal_pattern(all_md_df, ZT_Time, ul_price, close, tolerance_period)
#     pattern_df.index = df.index
#     df = df.join(pattern_df)
#     return df

# 20240722 使用少森的函数
def cal_Basic_zt(mdp, stock, date, pre_close, close, tolerance_period=10):
    all_md_df =  mdp.get_data_by_date('Transaction', stock, date).sort_values(by=['MDTime','TradeIndex'])
    all_md_df = hf_preprocessing('TransactionAllDay', all_md_df)
    ul_price = np.floor(pre_close * 100 * 1.2 + 0.5) / 100 if (((date>='20200824') and (stock[:2]=='30')) | (stock[:2]=='68')) else np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    all_md_df = all_md_df[all_md_df['TradePrice'] > 0]
    all_md_df['LastTradePrice'] = all_md_df['TradePrice'].shift(1)
    all_md_df['to_zt'] = (all_md_df['LastTradePrice']<ul_price) & (all_md_df['TradePrice']==ul_price)
    #分别需要排除9:30和13:00涨停的样本，应为无法参与，因此这两个时刻的数据要删掉
    md_df = all_md_df[(all_md_df['MDTime'] > 93000000) & (all_md_df['MDTime'] <= 145700000) & (all_md_df['MDTime'] != 130000000)]
    # all_md_df = all_md_df[(all_md_df['MDTime'] > 93000000) & (all_md_df['MDTime'] <= 145700000) & (all_md_df['MDTime'] != 130000000)]
    if md_df['to_zt'].sum() > 0:
        zt_index = list(md_df['to_zt']).index(True)
        zt_trade = md_df.iloc[zt_index]
        ZT_Time, is_zt = zt_trade['MDTime'], True
    else: #未实际突破
        ZT_Time, is_zt = np.nan, False

    high_price = all_md_df[all_md_df['MDTime']<ZT_Time]['TradePrice'].max()
    high_price = pre_close if np.isnan(high_price) else high_price
    if ZT_Time==ZT_Time:
        l3_time = max(fun_get_time(ZT_Time, -3 * 60), 93000000)
        max_rise_pct = (ul_price - all_md_df[(all_md_df['MDTime']>=l3_time) & (all_md_df['MDTime']<=ZT_Time)]['TradePrice'].min()) / pre_close
        #if ((date>='20200824') and (stock[:2]=='30')):
        if ((date >= '20200824') and (stock[:2] == '30')) | (stock[:2] == '68'):
            max_rise_pct = max_rise_pct / 2
    else:
        max_rise_pct = np.nan
    df = pd.DataFrame([[ZT_Time, is_zt, high_price, ul_price, max_rise_pct]],
                      columns=['ZT_Time', 'is_zt', 'high_price', 'ul_price', 'max_rise_pct'])
    df.index = pd.Index([(pd.Timestamp(date), stock)], name=['dt', 'Ticker'])
    if np.isnan(ZT_Time):
        pattern_df = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan]], columns=['label_pattern', 'label_firstUL_end_Time', 'label_lastUL_Time', 'label_lastUL_end_Time'])
    else:
        if (stock[-2:] == 'SH') and (date < '20180820'): # 老规则，强行变成尾盘集合竞价
            all_md_df.loc[all_md_df['MDTime'] > 145700000, 'TradePrice'] = close
        pattern_df = cal_pattern(all_md_df, ZT_Time, ul_price, close, tolerance_period)
    pattern_df.index = df.index
    df = df.join(pattern_df)
    return df

def fun_common_time_interval(time1, time2):
    time3 = float(np.floor(time1 / 10000000) * 3600 +
                  np.floor(np.mod(time1, 10000000) / 100000) * 60 +
                  np.mod(time1, 100000) / 1000)
    time4 = float(np.floor(time2 / 10000000) * 3600 +
                  np.floor(np.mod(time2, 10000000) / 100000) * 60 +
                  np.mod(time2, 100000) / 1000)
    if (time1 <= 113000000) & (time2 >= 130000000):
        seconds = (time4 - time3) - 1.5 * 3600
    elif (time1 < 93000000) & (time2 >= 93000000):
        seconds = (time4 - time3) - 4*60
    else:
        seconds = time4 - time3
    return round(seconds, 3) / 60

def cal_pattern(md_df, ZT_Time, ul_price, close_price, tolerance_period):
    md_df = md_df.sort_values(by='TradeIndex', ascending=True)
    if abs(close_price - ul_price) > 0.0001: # 未收盘涨停
        label_pattern = 2
    else:
        last_not_zt_time = md_df[(md_df['TradePrice'] != ul_price)].iloc[-1]['MDTime']
        try:
            last_zt_start_time = md_df[(md_df['MDTime'] >= last_not_zt_time) & (md_df['TradePrice'] == ul_price)]['MDTime'].iloc[0]
        except:
            print(md_df.HTSCSecurityID.tolist()[0], ZT_Time, last_zt_start_time, last_not_zt_time)

        not_zt_len = fun_common_time_interval(ZT_Time, last_zt_start_time)
        # print('突破到最后一次涨停间隔时间：%s分钟' % str(not_zt_len))
        if not_zt_len > tolerance_period:
            label_pattern = 3
        else:
            label_pattern = 4
    # 首次涨停结束的时间
    ZT_index = md_df[(md_df['MDTime'] >= ZT_Time) & (md_df['TradePrice'] == ul_price)]['TradeIndex'].iloc[0]
    # print(ZT_Time,md_df[md_df['TradeIndex']==ZT_index][['MDTime','TradePrice', 'TradeIndex']].values)
    after_zt_md_df = md_df[md_df['TradeIndex'] >= ZT_index].copy()
    after_zt_not_zt_md_df = after_zt_md_df[(after_zt_md_df['TradePrice'] < ul_price)]
    if len(after_zt_not_zt_md_df) == 0:
        firstUL_end_Time = 150000000
        lastUL_Time = ZT_Time
        lastUL_end_Time = 150000000
    else:
        first_not_UL_end_Time = after_zt_not_zt_md_df.iloc[0]['MDTime'] # 第一次涨停开板时间
        firstUL_end_Time = after_zt_md_df[(after_zt_md_df['MDTime'] <= first_not_UL_end_Time) & (after_zt_md_df['TradePrice'] == ul_price)].iloc[-1]['MDTime']
        lastUL_end_Time = after_zt_md_df[after_zt_md_df['TradePrice'] == ul_price].iloc[-1]['MDTime']
        lastUL_end_Time_index = after_zt_md_df[after_zt_md_df['TradePrice'] == ul_price].iloc[-1]['TradeIndex']
        if (after_zt_md_df['MDTime'] > lastUL_end_Time).sum() == 0: # 最后一次涨停直至收盘
            lastUL_end_Time = 150000000
            lastUL_end_Time_index = np.inf

        if lastUL_end_Time == firstUL_end_Time: # 第一次涨停就是最后一次涨停
            lastUL_Time = ZT_Time
        else:
            last_no_zt_before_last_zt_index = after_zt_md_df[(after_zt_md_df['TradeIndex'] < lastUL_end_Time_index) &
                                                             (after_zt_md_df['TradePrice'] < ul_price)].iloc[-1]['TradeIndex'] # 最后一次涨停前非涨停的时间
            lastUL_Time = after_zt_md_df[(after_zt_md_df['TradeIndex'] >= last_no_zt_before_last_zt_index) &
                                         (after_zt_md_df['TradePrice']==ul_price)].iloc[0]['MDTime'] # 最后一次涨停开始时间

    df = pd.DataFrame([[label_pattern, firstUL_end_Time, lastUL_Time, lastUL_end_Time]],
                      columns=['label_pattern', 'label_firstUL_end_Time', 'label_lastUL_Time', 'label_lastUL_end_Time'])
    return df
