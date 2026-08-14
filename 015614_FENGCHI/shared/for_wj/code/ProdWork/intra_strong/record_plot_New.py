# -*- coding: utf-8 -*-
"""
Created on Wed May 22 14:48:42 2019
用于买入标的的各个成交位置图
@author: 013600
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime as dt
import sys
from xquant.thirdpartydata.marketdata import MarketData

ma = MarketData()
from xquant.marketdata import MarketData

mdp = MarketData()
from LucienUtil import IO


IO_mother_dir = '/data/group/800080/warehouse_event'


# IO_mother_dir = '/data/group/800080/warehouse'

def get_up_limit_dic(codes, day):
    f_data = IO.read_data([day, day], columns=['pre_close', 'close']
                          , alt=IO_mother_dir + '/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    if (day >= '20200824') & (codes[0] == '3'):
        ZT_price = np.floor(f_data['pre_close'] * 100 * 1.2 + 0.5) / 100
    else:
        ZT_price = np.floor(f_data['pre_close'] * 100 * 1.1 + 0.5) / 100
    uplimit = (f_data['close'] == ZT_price)
    dic = dict()
    for i in codes:
        dic[i] = uplimit.loc[day, i]
    return dic


def inttime2str(time):
    time_str = str(int(time))
    if len(time_str) == 8:
        time_str = '0' + time_str
    return time_str[0:2] + ':' + time_str[2:4] + ':' + time_str[4:6]


def get_zt_time_dic(df, trade_date_h):
    df_need = df[(df['order_direction'] == 'SplitLastShot') |
                 (df['order_direction'] == 'JupiterFirstOrder') | (df['order_direction'] == 'MRiskSplitLastShotBuy') | (
                             df['order_direction'] == 'MRiskSplitShotBuy')]
    df_need['ZT_Time_dt'] = df_need['ZT_Time'].apply(
        lambda x: dt.datetime.strptime(trade_date_h + ' ' + inttime2str(x), '%Y-%m-%d %H:%M:%S'))
    res_dic = {list(df_need['Unnamed: 0'])[i]: list(df_need['ZT_Time_dt'])[i] for i in range(len(df_need))}
    return res_dic


def get_position_index(trade_df, require_time, require_y=False):
    time_list = list(trade_df['time'])
    if require_time in time_list:
        index_x = time_list.index(require_time)
        if require_y:
            return index_x, trade_df['price'].iloc[index_x]
        else:
            return index_x
    elif require_time < time_list[0]:
        if require_y:
            return 0, trade_df['price'].iloc[0]
        else:
            return 0
    else:
        for i in range(len(time_list) - 1):
            if time_list[i] < require_time < time_list[i + 1]:
                delta1 = (require_time - time_list[i]).seconds
                delta2 = (time_list[i + 1] - require_time).seconds
                index_x = i + (delta1 / (delta1 + delta2))
                if require_y:
                    p1, p2 = trade_df['price'].iloc[i], trade_df['price'].iloc[i + 1]
                    y = p1 + (p2 - p1) * (delta1 / (delta1 + delta2))
                    return index_x, y
                else:
                    return index_x


def plot_trade_data(fig, indicator, x_plot_number, trade_data, xticks_num, save_pic):
    # plt.figure(21, figsize = (15,15))
    # 当日价格走势图
    fig.add_subplot(2, x_plot_number, indicator)
    plt.title(str(trade_data['trade_date']) + '-' + trade_data['code'] + '--09:30:00~15:00:00')
    plt.plot(list(trade_data['price_df']['price']))
    x_ticks = trade_data['price_df']['time'].apply(lambda x: str(x)[~8:~6] + ':' + str(x)[~6:~4] + ':' + str(x)[~4:~2])
    use_index = [i * ((len(trade_data['price_df']) - 1) // xticks_num) for i in range(xticks_num + 1)]
    plt.xticks(use_index, tuple(x_ticks.iloc[use_index]), rotation=90)
    # 画区间线
    pic_start_index = get_position_index(trade_data['price_df'], trade_data['pic_interval'][0])
    pic_end_index = get_position_index(trade_data['price_df'], trade_data['pic_interval'][1])
    plt.plot([pic_start_index, pic_start_index],
             [min(trade_data['price_df']['price']), max(trade_data['price_df']['price'])])
    plt.plot([pic_end_index, pic_end_index],
             [min(trade_data['price_df']['price']), max(trade_data['price_df']['price'])])

    # 筛选局部价格数据
    trade_data['price_df'] = trade_data['price_df'][(trade_data['price_df']['time'] >= trade_data['pic_interval'][0]) \
                                                    & (trade_data['price_df']['time'] <= trade_data['pic_interval'][1])]
    # 局部价格走势图
    fig.add_subplot(2, x_plot_number, indicator + x_plot_number)
    plt.grid()
    plt.title(str(trade_data['trade_date']) + '-' + trade_data['code'] + '--%s~%s' % ( \
        min(trade_data['pic_interval']).strftime('%H:%M:%S'), \
        max(trade_data['pic_interval']).strftime('%H:%M:%S')))
    plt.plot(list(trade_data['price_df']['price']))
    x_ticks = trade_data['price_df']['time'].apply(lambda x: x.strftime("%H:%M:%S"))
    use_index = [i * ((len(trade_data['price_df']) - 1) // xticks_num) for i in range(xticks_num + 1)]
    print('use_index:,x_ticks.iloc[use_index]')
    print(len(use_index),len(x_ticks))
    if len(x_ticks)>0:
        plt.xticks(use_index, tuple(x_ticks.iloc[use_index]), rotation=90)

        # 突破点
        zt_time_x, zt_time_y = get_position_index(trade_data['price_df'], trade_data['zt_time'], require_y=True)
        plt.scatter(zt_time_x, zt_time_y, marker='+', color='y', label='break point', s=90)

        # 挂单点
        x_list, y_list = [], []
        for i in range(len(trade_data['trade_df']['place_order_time_list'])):
            place_x = get_position_index(trade_data['price_df'], trade_data['trade_df']['place_order_time_list'].iloc[i],
                                         require_y=False)
            place_y = trade_data['trade_df']['place_order_price'].iloc[i]
            x_list.append(place_x)
            y_list.append(place_y)
        plt.scatter(x_list, y_list, marker='s', color='b', label='place order point', s=30)

        # 成交点
        try:
            x_list, y_list = [], []
            for i in range(len(trade_data['trade_df']['filled_time_list'])):
                trade_x = get_position_index(trade_data['price_df'], trade_data['trade_df']['filled_time_list'].iloc[i],
                                             require_y=False)
                trade_y = trade_data['trade_df']['filled_ave_price'].iloc[i]
                x_list.append(trade_x)
                y_list.append(trade_y)
        except:
            print('no deal')

        plt.ylim(trade_data['price_limit'])
        plt.scatter(x_list, y_list, marker='o', color='r', label='filled point', s=20)
        plt.legend(loc='best')
    # if save_pic:
    #     plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/成交画图/%s-%s/%s.png"%(trade_data['envir'], trade_data['trade_date'], trade_data['code']))
    # plt.show()


envir = '生产环境'
from xquant.factordata import FactorData

s = FactorData()
if len(sys.argv) > 1:
    trade_date = sys.argv[1]
else:
    trade_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
    # date = '20230606'# # 若未在当个交易日晚上运行程序，需要在次日早上修改date
print('current date = %s' % trade_date)

#trade_date_h = '2022-09-30'
trade_date_h = trade_date[0:4] + '-' + trade_date[4:6] + '-' + trade_date[6:8]
# print('tradedate = %s'%trade_date)
MD_data_prod_dir = IO_mother_dir + '/prod/LOCAL_DATA/FLAG/%s/' % trade_date
import time

while (os.path.exists(MD_data_prod_dir + '%s_MD.success' % trade_date) == False):
    print('等待MD或RDF或RISK或5分钟数据中')
    time.sleep(60)

# if not os.path.exists('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/成交画图/%s-%s/'%(envir, trade_date)):
#     os.makedirs('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/成交画图/%s-%s/'%(envir, trade_date))
logFile = '/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_%s_%s.xlsx' % (trade_date, 'prod')
if os.path.exists(logFile):
    trade_record_df = pd.read_excel(logFile, sheet_name='每日订单')
    trade_record_df = trade_record_df[trade_record_df['actionSource'] == 'JupiterNew']
else:
    trade_record_df = pd.DataFrame()
# trade_record_df = pd.read_csv(open('A:\\wangwd\\data_file\\LOG\\交易记录\\tradeRecords-%d-%s.csv'%(trade_date, envir)))
# trade_record_df = trade_record_df[trade_record_df['orderFillQty']>0]
is_up_limit = get_up_limit_dic(list(trade_record_df['stockcode'].drop_duplicates()), trade_date)
ZT_Time_all = get_zt_time_dic(
    pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/每日突破/每日突破_%s_%s.xlsx' % (trade_date, 'prod'),sheet_name='每日突破New'), trade_date_h)
num_stocks_2_plot = len(set(trade_record_df[(trade_record_df['actionSource'] == 'JupiterNew') & (
            (trade_record_df['orderType'] == 'SplitLastShot') | (trade_record_df['orderType'] == 'MRiskSplitShot') |
            (trade_record_df['orderType'] == 'JupiterFirstOrder') | (
                        trade_record_df['orderType'] == 'MRiskSplitLastShotBuy') | (
                        trade_record_df['orderType'] == 'MRiskSplitShotBuy'))]['stockcode']))
x_plot_number = min(40, int(np.ceil(num_stocks_2_plot)))
fig = plt.figure(figsize=(12 * x_plot_number, 18))
# fig = plt.figure(figsize=(12*(x_plot_number-30), 18))
plt.rcParams['font.size'] = 15
indicator = 0
code_list = list(set(trade_record_df[(trade_record_df['actionSource'] == 'JupiterNew') & (
            (trade_record_df['orderType'] == 'SplitLastShot') | (trade_record_df['orderType'] == 'MRiskSplitShot') |
            (trade_record_df['orderType'] == 'JupiterFirstOrder') | (
                        trade_record_df['orderType'] == 'MRiskSplitLastShotBuy') | (
                        trade_record_df['orderType'] == 'MRiskSplitShotBuy'))]['stockcode']))[:40]
for code in code_list:
    indicator += 1
    print(code)
    df = trade_record_df[(trade_record_df['actionSource'] == 'JupiterNew') & ((trade_record_df['stockcode'] == code) & (
                (trade_record_df['orderType'] == 'SplitLastShot') | (trade_record_df['orderType'] == 'MRiskSplitShot') |
                (trade_record_df['orderType'] == 'JupiterFirstOrder') | (
                            trade_record_df['orderType'] == 'MRiskSplitLastShotBuy') | (
                            trade_record_df['orderType'] == 'MRiskSplitShotBuy')))].copy()
    trade_dict = dict()
    last_order_time = df[df['ordStatus'] == 'PENDING_NEW']['transactionTime'].max()
    trade_dict['place_order_time_list'] = [dt.datetime.strptime(last_order_time[:~8], '%Y-%m-%dT%H:%M:%S')]
    trade_dict['place_order_price'] = [df[df['ordStatus'] == 'PENDING_NEW'] \
                                           [df[df['ordStatus'] == 'PENDING_NEW']['transactionTime'] == last_order_time][
                                           'price'].max()]
    if 'FILLED' in df['ordStatus'].values:
        filled_order_time = df[df['ordStatus'] == 'FILLED']['transactionTime'].max()
        trade_dict['filled_time_list'] = [dt.datetime.strptime(filled_order_time[:~8], '%Y-%m-%dT%H:%M:%S')]
        trade_dict['filled_ave_price'] = [df[df['ordStatus'] == 'FILLED'] \
                                              [df[df['ordStatus'] == 'FILLED']['transactionTime'] == filled_order_time][
                                              'avgPx'].max()]
    elif 'PARTIALLY_FILLED' in df['ordStatus'].values:
        partially_filled_order_time = df[df['ordStatus'] == 'PARTIALLY_FILLED']['transactionTime'].max()
        trade_dict['filled_time_list'] = [dt.datetime.strptime(partially_filled_order_time[:~8], '%Y-%m-%dT%H:%M:%S')]
        trade_dict['filled_ave_price'] = [df[df['ordStatus'] == 'PARTIALLY_FILLED'] \
                                              [df[df['ordStatus'] == 'PARTIALLY_FILLED'][
                                                   'transactionTime'] == partially_filled_order_time]['avgPx'].max()]
    else:
        trade_dict['filled_time_list'] = pd.Timestamp(np.nan)
        trade_dict['filled_ave_price'] = np.nan

    trade_df = pd.DataFrame(trade_dict)
    trade_start_time = min(trade_df['place_order_time_list'].dropna())
    trade_end_time = max(trade_df['filled_time_list'].dropna()) if len(
        trade_df['filled_time_list'].dropna()) > 0 else trade_start_time
    pic_start_time = trade_start_time + dt.timedelta(minutes=-1)
    pic_end_time = trade_end_time + dt.timedelta(minutes=1)

    tick_data = mdp.get_data_by_date("Stock", code, trade_date, sort_by_receive_time=False)
    print(tick_data.shape)
    print(tick_data.columns.tolist())
    if len(tick_data) > 0:
        tick_data = tick_data[(tick_data['MDTime'].astype(int) >= 93000000)&(tick_data['MDTime'].astype(int) < 163000000)&(tick_data['LastPx']>0)]

        # tick_data = ma.getMDSecurityTickDataFrame(code, "%s093000"%(trade_date), "%s150000"%(trade_date), 0)

        price_df = pd.DataFrame()
        price_df['time'], price_df['price'] = tick_data['MDTime'], tick_data['LastPx']
        price_df['time'] = price_df['time'].apply(
            lambda x: dt.datetime.strptime(trade_date + str(x)[:~2], '%Y%m%d%H%M%S'))

        trade_data = {'trade_df': trade_df, 'price_df': price_df, 'zt_time': ZT_Time_all[code], 'code': code,
                      'envir': envir, \
                      'trade_date': trade_date, 'pic_interval': [pic_start_time, pic_end_time],
                      'price_limit': tick_data[tick_data['MaxPx'] != 0][['MinPx', 'MaxPx']].values[0]}
        plot_trade_data(fig, indicator, x_plot_number, trade_data, xticks_num=10, save_pic=True)
    else:
        print(code, trade_date, 'has no tickdata!!!!!!!!!!')

plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.1)
plt.savefig("/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/成交画图/%s_New_%s.png" % (trade_date, envir), dpi=80)
print('create jupiter png in %s!!!!!!!!!!' % "/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/成交画图/%s_New_%s.png" % (
trade_date, envir))


