import matplotlib
matplotlib.use('agg')
from multifactor.data.utils import *
import os
import numpy as np
import pandas as pd
import bottleneck as bk

import matplotlib.pyplot as plt

_,date,_ = check_update_date()
date = str(date)


file = 'CONCAT'

h5path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/'
starttime=int(date)
endtime=21220228
dataname = 'MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5'


def calc(file, cat, path):

        temp_td = pd.read_csv(path + file + '/_all_total_trade_detail.csv')
        df_day = pd.DataFrame()
        for item in temp_td.iterrows():
            temp_df = pd.DataFrame()
            num = item[0] + 1
            trades = item[1].copy()
            ot = pd.to_datetime(trades['open_time'])
            ct = pd.to_datetime(trades['close_time'])
            op = float(temp_y.loc[ot])
            cp = float(temp_y.loc[ct])
            buysell = trades['pos']

            op_location = list(temp_y.index).index(ot)
            cl_location = list(temp_y.index).index(ot)


            if buysell == 1:
                optimal = float(temp_y.iloc[op_location+2:op_location+21].max())
            else:
                optimal = float(temp_y.iloc[op_location+2:op_location+21].min())

            fixed_point_price = float(temp_y.iloc[op_location+20])
            temp_df['trades_no'] = [num]
            temp_df['pos'] = [int(buysell)]
            temp_df['open_time'] = [ot]
            temp_df['open_price'] = [op]
            temp_df['close_time'] = [ct]
            temp_df['close_price'] = [cp]
            temp_df['optimal_price_20m'] = [optimal]
            temp_df['20m_fixed_price'] = [fixed_point_price]
            temp_df['deal_profit'] = float(trades['profit_intradeal'])
            temp_df['holding_time'] = int(trades['holding_time'])
            df_day = pd.concat([df_day, temp_df])

        tk = df_day.set_index('trades_no')
        print(file, ot)
        return [file, tk]
    

def type_convertor(func):
    """
    与operators文件中的算子相配套，用于调整输出的数据格式，使之与输入的数据格式相一致
    """

    def wrapper(*args, **kwargs):
        data = args[0]
        if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
            raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
        output = func(*args, **kwargs)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(output, index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(output, index=data.index, name=data.name)
        return output

    return wrapper


@type_convertor
def ts_mean(data, d):
    # moving time-series mean for the past d periods
    if d == 1:
        output = data
    else:
        output = bk.move_mean(data, window=d, min_count=int(d / 2), axis=0)
    return output


def ts_delta(data, d):
    # A_i - A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = data - ts_delay(data, d)
    else:
        output = data.diff(periods=d)
    return output



def rsi(price_close, time_period=14):
    """
    rsi(relative strength index) calculates a ratio of the recent upward price movements to the absolute price movement.
    """
    close_up = ts_delta(price_close, 1)
    close_up[close_up < 0] = 0
    close_down = -ts_delta(price_close, 1)
    close_down[close_down < 0] = 0
    close_up_ma = ts_mean(close_up, time_period)
    close_down_ma = ts_mean(close_down, time_period)
    price_rsi = close_up_ma / (close_up_ma + close_down_ma)
    return price_rsi


def draw_daily_performance(date, price_raw_data, stats_raw_data, save_path):
    price_temp = price_raw_data.loc[f'{date}']
    stats_temp = stats_raw_data.loc[f'{date}']
    stats_temp_long = stats_temp[stats_temp['pos'] == 1]
    stats_temp_short = stats_temp[stats_temp['pos'] == -1]

    list_1 = []
    list_2 = []

    for i in stats_temp_long.itertuples():
        temp_list_1 = list()
        temp_list_1.append(price_temp.index.tolist().index(i.open_time))
        temp_list_1.append(price_temp.index.tolist().index(i.close_time))
        list_1.append(temp_list_1)
        temp_list_2 = list()
        temp_list_2.append(price_temp['vwap'].loc[i.open_time])
        temp_list_2.append(price_temp['vwap'].loc[i.close_time])
        list_2.append(temp_list_2)

    list_3 = []
    list_4 = []

    for i in stats_temp_short.itertuples():
        temp_list_3 = list()
        temp_list_3.append(price_temp.index.tolist().index(i.open_time))
        temp_list_3.append(price_temp.index.tolist().index(i.close_time))
        list_3.append(temp_list_3)
        temp_list_4 = list()
        temp_list_4.append(price_temp['vwap'].loc[i.open_time])
        temp_list_4.append(price_temp['vwap'].loc[i.close_time])
        list_4.append(temp_list_4)

    fig = plt.figure(figsize=(15, 8))
    ax = fig.add_subplot(1, 1, 1)
    f1 = ax.plot(price_temp['vwap'].values, color='saddlebrown', label='vwap')
    for i in zip(list_1, list_2):
        f3 = ax.plot(i[0], i[1], marker='o', markersize=8, linewidth=3, color='red', label='long')
    for i in zip(list_3, list_4):
        f4 = ax.plot(i[0], i[1], marker='o', markersize=8, linewidth=3, color='green', label='short')
    ax.set_xticks(np.arange(0, price_temp.shape[0], 30))
    ax.set_xticklabels(price_temp.index[::30], rotation=30)[-1]
    ax_right = ax.twinx()
    f2 = ax_right.stackplot(np.arange(price_temp.shape[0]), price_temp['rsi_20min'].values,
                            labels=['rsi_20min'], alpha=0.3)
    f = f1 + f2
    if len(list_1) > 0:
        f += f3
    if len(list_3) > 0:
        f += f4
    labels = [i.get_label() for i in f]
    ax.legend(f, labels, fontsize=12)
    fig.suptitle(f'{date}', fontsize=36)
    plt.savefig(os.path.join(save_path, f'{date}.png'))
    #plt.show()
    plt.close()

for cat in ['IC', 'IF']:

    path = '/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking/back_test/%s/%s/'%(date, cat.upper())
    origindata = IO.read_data([starttime, endtime], columns=['vwap'],
                              alt=os.path.join(h5path, dataname)).xs('%s.CFE'%cat.upper(), level=1)

    temp_y = origindata['vwap'].to_frame()
    hholder = calc(file, cat, path)   
    di = {}
    di[hholder[0]] = hholder[1]
    stats_raw_ic = di['CONCAT']

    price_raw_ic = temp_y


    stats_raw_ic.index = pd.to_datetime(stats_raw_ic['open_time'])
    price_raw_ic['rsi_20min'] = rsi(price_raw_ic['vwap'], 20) * 100

    draw_daily_performance(date, price_raw_ic[['vwap', 'rsi_20min']], stats_raw_ic, path)