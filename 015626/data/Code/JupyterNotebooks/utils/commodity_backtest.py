import os
import datetime
import numpy as np
import pandas as pd
import bottleneck as bk
import matplotlib.pyplot as plt
import matplotlib.ticker as mtk
from multiprocessing import Pool


def ts_rank(data, d):
    if d == 1:
        output = data
    else:
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0), index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0), index=data.index, name=data.name)
        elif isinstance(data, np.ndarray):
            output = bk.move_rank(data, window=d, min_count=int(d / 2), axis=0)
        else:
            output = None
    return output


def print_error(error):
    print('Error: {}'.format(error))
    return None


# ****************************************************************************************************


def back_test(ticker, signal, filter_series=None, start_date=None, end_date=None, in_th=0.5, ot_th=0.5, in_end=2, session1=True, session2=True, overnight=True, freq='1min', num_processes=10):
    if isinstance(signal, pd.DataFrame):
        signal = signal[signal.columns[0]]
    assert isinstance(signal, pd.Series)

    if freq == '1min':
        ref_path = '/data/user/016700/Data/Factors/TEMP/commodities/minute_backtest_reference_1min.pkl'
    elif freq == '3min':
        ref_path = '/data/user/016700/Data/Factors/TEMP/commodities/minute_backtest_reference_3min.pkl'
    elif freq == '5min':
        ref_path = '/data/user/016700/Data/Factors/TEMP/commodities/minute_backtest_reference_5min.pkl'
    else:
        raise RuntimeError(f'freq = {freq}')
    ref_dict = pd.read_pickle(ref_path)
    assert ticker in ref_dict, f'{ticker} not in {ref_path}'
    ref = ref_dict[ticker]
    assert isinstance(ref, pd.DataFrame)

    ss1_idx = (ref.index.hour > 6) & (ref.index.hour < 18)
    ss2_idx = (ref.index.hour < 6) | (ref.index.hour > 18)
    if session1 and session2:
        pass
    elif session1:
        ref = ref[ss1_idx]
    elif session2:
        ref = ref[ss2_idx]
    else:
        raise RuntimeError('session1 and session2')
    ref = ref.sort_index()

    if start_date is not None:
        ref = ref.loc[start_date:]
    if end_date is not None:
        ref = ref.loc[:end_date]
    start_date = max(ref.index[0], signal.index[0]).strftime('%Y%m%d')
    end_date = min(ref.index[-1], signal.index[-1]).strftime('%Y%m%d')
    ref = ref.loc[f'{start_date} 06:00':f'{end_date} 18:00']

    signal = signal.reindex(ref.index)
    signal = signal.fillna(0)

    if filter_series is None:
        filter_series = pd.Series(np.ones_like(signal), index=signal.index)
    if isinstance(filter_series, pd.DataFrame):
        filter_series = filter_series[filter_series.columns[0]]
    assert isinstance(filter_series, pd.Series)
    filter_series = filter_series.astype('int')
    filter_series = filter_series.reindex(signal.index)
    filter_series = filter_series.ffill(axis=0)

    # **************************************************

    idx = ref.index.to_series()
    idx_diff = idx.diff().dt.total_seconds() / 60
    idx_diff = idx_diff.fillna(0)
    bar_time = int(idx_diff.value_counts().sort_values(ascending=False).index[0])

    if overnight:
        contract = ref['contract']
        group_id = (contract != contract.shift()).astype('int').cumsum()
    else:
        group_id = (idx_diff > 240).cumsum() + 1

    # **************************************************

    price = ref['twap']
    price_diff = price.diff()
    price_diff[idx_diff > 240] = 0  # set overnight return to zero
    prev_corr = {}
    next_corr = {}
    for t in [1, 5, 10, 20, 30, 45, 60, 90, 120, 180, 240, 360, 480]:
        prev_ret = price_diff.rolling(t).sum() / price.shift(t)
        next_ret = prev_ret.shift(-1 - t)
        prev_ret = prev_ret.where(filter_series > 0, np.nan)
        next_ret = next_ret.where(filter_series > 0, np.nan)
        prev_corr[t] = signal.corr(prev_ret)
        next_corr[t] = signal.corr(next_ret)
    prev_corr = pd.Series(prev_corr)
    next_corr = pd.Series(next_corr)

    # **************************************************

    date_last_px = price.between_time(start_time='06:00', end_time='18:00')
    date_last_px = date_last_px.groupby(date_last_px.index.date).last()
    date_last_px.index = pd.to_datetime(date_last_px.index)
    date_list = date_last_px.index.strftime('%Y%m%d').to_list()

    pool = Pool(processes=num_processes)
    id_list = group_id.drop_duplicates().sort_values().to_list()
    outputs = [pool.apply_async(get_total_trade, args=(price[group_id == k], signal[group_id == k], filter_series[group_id == k], in_th, ot_th, in_end), error_callback=print_error) for k in id_list]
    pool.close()
    pool.join()
    outputs = [x.get() for x in outputs]
    total_trade = pd.concat(outputs, axis=0).sort_values(by='in_time')

    in_date_list = []
    ot_date_list = []
    trade_dates = set(date_list)
    for i in range(len(total_trade)):
        row = total_trade.iloc[i]
        in_time = row['in_time']
        in_date = in_time.strftime('%Y%m%d')
        if (in_date not in trade_dates) or (in_time.time() > datetime.time(18, 0)):
            for d in range(1, 10):
                in_date = (in_time + pd.Timedelta(days=d)).strftime('%Y%m%d')
                if in_date in trade_dates:
                    break
        in_date_list.append(in_date)
        ot_time = row['ot_time']
        ot_date = ot_time.strftime('%Y%m%d')
        if (ot_date not in trade_dates) or (ot_time.time() > datetime.time(18, 0)):
            for d in range(1, 10):
                ot_date = (ot_time + pd.Timedelta(days=d)).strftime('%Y%m%d')
                if ot_date in trade_dates:
                    break
        ot_date_list.append(ot_date)
        assert int(in_date) <= int(ot_date)
    total_trade['in_date'] = in_date_list
    total_trade['ot_date'] = ot_date_list

    total_trade['change'] = total_trade['ot_price'] - total_trade['in_price']
    assert np.all(total_trade['change'] == total_trade['itd_change'] + total_trade['ovn_change'])
    assert np.all(total_trade['itd_change'] == total_trade['ss1_change'] + total_trade['ss2_change'])
    total_trade['in_spread'] = ref['spread'].loc[total_trade['in_time']].to_list()
    total_trade['ot_spread'] = ref['spread'].loc[total_trade['ot_time']].to_list()
    total_trade['in_fee'] = ref['fee_one_sided'].loc[total_trade['in_time']].to_list()
    total_trade['ot_fee'] = ref['fee_one_sided'].loc[total_trade['ot_time']].to_list()
    total_trade['itd_return'] = total_trade['itd_change'] * total_trade['pos'] / total_trade['in_price']
    total_trade['ovn_return'] = total_trade['ovn_change'] * total_trade['pos'] / total_trade['in_price']
    total_trade['ss1_return'] = total_trade['ss1_change'] * total_trade['pos'] / total_trade['in_price']
    total_trade['ss2_return'] = total_trade['ss2_change'] * total_trade['pos'] / total_trade['in_price']
    total_trade['return'] = total_trade['change'] * total_trade['pos'] / total_trade['in_price']
    total_trade['net_return'] = (total_trade['change'] * total_trade['pos'] - total_trade['in_spread'] / 2 - total_trade['ot_spread'] / 2) / total_trade['in_price'] - total_trade['in_fee'] - total_trade['ot_fee']
    total_trade['hold_time'] = total_trade['hold_bars'] * bar_time
    total_trade['ticker'] = ticker
    total_trade = total_trade[['ticker', 'pos', 'in_time', 'ot_time', 'in_price', 'ot_price', 'in_spread', 'ot_spread', 'in_fee', 'ot_fee', 'in_date', 'ot_date',
                               'hold_bars', 'hold_time', 'change', 'return', 'net_return', 'itd_return', 'ovn_return', 'ss1_return', 'ss2_return']]

    result = get_result(prev_corr, next_corr, total_trade, date_list, date_last_px)
    return result


def get_total_trade(price, signal, filter_series, in_th, ot_th, in_end):
    pos = 0
    dt_in = None
    dt_ot = None
    px_in = None
    px_ot = None
    hold_bars = 0
    itd_change = 0
    ovn_change = 0
    ss1_change = 0
    ss2_change = 0
    trade_list = []
    n = len(price)
    for i in range(n):
        if pos == 0:
            dt_in = None
            dt_ot = None
            px_in = None
            px_ot = None
            hold_bars = 0
            itd_change = 0
            ovn_change = 0
            ss1_change = 0
            ss2_change = 0
            if (i < n - in_end) and (signal.iloc[i] > in_th) and (filter_series.iloc[i] > 0):
                dt_in = price.index[i + 1]
                px_in = price.iloc[i + 1]
                pos = 1
                continue
            if (i < n - in_end) and (signal.iloc[i] < -1 * in_th) and (filter_series.iloc[i] > 0):
                dt_in = price.index[i + 1]
                px_in = price.iloc[i + 1]
                pos = -1
                continue
        if pos > 0:
            hold_bars += 1
            price_diff = price.iloc[i + 1] - price.iloc[i]
            time_diff = price.index[i + 1] - price.index[i]
            time_diff = time_diff.total_seconds() / 60
            if time_diff < 240:
                itd_change += price_diff
                hour = price.index[i].hour
                if (hour > 6) and (hour < 18):
                    ss1_change += price_diff
                else:
                    ss2_change += price_diff
            else:
                ovn_change += price_diff
            if (signal.iloc[i] < ot_th) or (i == n - 2):
                dt_ot = price.index[i + 1]
                px_ot = price.iloc[i + 1]
                trade_list.append([pos, dt_in, dt_ot, px_in, px_ot, hold_bars, itd_change, ovn_change, ss1_change, ss2_change])
                pos = 0
                continue
        if pos < 0:
            hold_bars += 1
            price_diff = price.iloc[i + 1] - price.iloc[i]
            time_diff = price.index[i + 1] - price.index[i]
            time_diff = time_diff.total_seconds() / 60
            if time_diff < 240:
                itd_change += price_diff
                hour = price.index[i].hour
                if (hour > 6) and (hour < 18):
                    ss1_change += price_diff
                else:
                    ss2_change += price_diff
            else:
                ovn_change += price_diff
            if (signal.iloc[i] > -1 * ot_th) or (i == n - 2):
                dt_ot = price.index[i + 1]
                px_ot = price.iloc[i + 1]
                trade_list.append([pos, dt_in, dt_ot, px_in, px_ot, hold_bars, itd_change, ovn_change, ss1_change, ss2_change])
                pos = 0
                continue
    total_trade = pd.DataFrame(trade_list, columns=['pos', 'in_time', 'ot_time', 'in_price', 'ot_price', 'hold_bars', 'itd_change', 'ovn_change', 'ss1_change', 'ss2_change'])
    return total_trade


def get_result(prev_corr, next_corr, total_trade, date_list, date_last_px=None):
    if date_last_px is None:
        raw_ret = get_daily_ret(total_trade, date_list, ret_col='return')
    else:
        raw_ret = get_daily_ret_raw(total_trade, date_list, date_last_px)
    raw_cum_ret = raw_ret.cumsum()
    raw_stats = get_stats(total_trade, raw_ret, ret_col='return')

    select_trade = total_trade[total_trade['pos'] > 0]
    if date_last_px is None:
        raw_ret_l = get_daily_ret(select_trade, date_list, ret_col='return')
    else:
        raw_ret_l = get_daily_ret_raw(select_trade, date_list, date_last_px)
    raw_cum_ret_l = raw_ret_l.cumsum()
    raw_stats_l = get_stats(select_trade, raw_ret_l, ret_col='return')

    select_trade = total_trade[total_trade['pos'] < 0]
    if date_last_px is None:
        raw_ret_s = get_daily_ret(select_trade, date_list, ret_col='return')
    else:
        raw_ret_s = get_daily_ret_raw(select_trade, date_list, date_last_px)
    raw_cum_ret_s = raw_ret_s.cumsum()
    raw_stats_s = get_stats(select_trade, raw_ret_s, ret_col='return')

    if date_last_px is None:
        net_ret = get_daily_ret(total_trade, date_list, ret_col='net_return')
    else:
        net_ret = get_daily_ret_net(total_trade, date_list, date_last_px)
    net_cum_ret = net_ret.cumsum()
    net_stats = get_stats(total_trade, net_ret, ret_col='net_return')

    select_trade = total_trade[total_trade['pos'] > 0]
    if date_last_px is None:
        net_ret_l = get_daily_ret(select_trade, date_list, ret_col='net_return')
    else:
        net_ret_l = get_daily_ret_net(select_trade, date_list, date_last_px)
    net_cum_ret_l = net_ret_l.cumsum()
    net_stats_l = get_stats(select_trade, net_ret_l, ret_col='net_return')

    select_trade = total_trade[total_trade['pos'] < 0]
    if date_last_px is None:
        net_ret_s = get_daily_ret(select_trade, date_list, ret_col='net_return')
    else:
        net_ret_s = get_daily_ret_net(select_trade, date_list, date_last_px)
    net_cum_ret_s = net_ret_s.cumsum()
    net_stats_s = get_stats(select_trade, net_ret_s, ret_col='net_return')

    itd_ret = get_daily_ret(total_trade, date_list, ret_col='itd_return')
    itd_cum_ret = itd_ret.cumsum()

    ovn_ret = get_daily_ret(total_trade, date_list, ret_col='ovn_return')
    ovn_cum_ret = ovn_ret.cumsum()

    ss1_ret = get_daily_ret(total_trade, date_list, ret_col='ss1_return')
    ss1_cum_ret = ss1_ret.cumsum()

    ss2_ret = get_daily_ret(total_trade, date_list, ret_col='ss2_return')
    ss2_cum_ret = ss2_ret.cumsum()

    result = {
        'total_trade': total_trade,
        'date_list': date_list,
        'raw_stats': raw_stats,
        'raw_stats_l': raw_stats_l,
        'raw_stats_s': raw_stats_s,
        'raw_cum_ret': raw_cum_ret,
        'raw_cum_ret_l': raw_cum_ret_l,
        'raw_cum_ret_s': raw_cum_ret_s,
        'net_stats': net_stats,
        'net_stats_l': net_stats_l,
        'net_stats_s': net_stats_s,
        'net_cum_ret': net_cum_ret,
        'net_cum_ret_l': net_cum_ret_l,
        'net_cum_ret_s': net_cum_ret_s,
        'itd_cum_ret': itd_cum_ret,
        'ovn_cum_ret': ovn_cum_ret,
        'ss1_cum_ret': ss1_cum_ret,
        'ss2_cum_ret': ss2_cum_ret,
        'prev_corr': prev_corr,
        'next_corr': next_corr,
    }
    return result


def get_daily_ret(total_trade, date_list, ret_col):
    total_trade = total_trade.copy()
    trade_ret = total_trade[ret_col]
    trade_ret.index = total_trade['ot_date']
    daily_ret = trade_ret.groupby(trade_ret.index).sum()
    daily_ret = daily_ret.reindex(date_list, fill_value=0)
    daily_ret.index = pd.to_datetime(daily_ret.index)
    return daily_ret


def get_daily_ret_raw(total_trade, date_list, date_last_px):
    total_trade = total_trade.copy()
    date_prev_px = date_last_px.shift()
    daily_ret = []
    for date in date_list:
        df = total_trade[(total_trade['in_date'] == date) & (total_trade['ot_date'] == date)]
        if len(df) > 0:
            ret1 = (df['ot_price'] - df['in_price']) * df['pos'] / df['in_price']
            ret1 = ret1.sum()
        else:
            ret1 = 0
        df = total_trade[(total_trade['in_date'] == date) & (total_trade['ot_date'] > date)]
        if len(df) > 0:
            ret2 = (date_last_px[date] - df['in_price']) * df['pos'] / df['in_price']
            ret2 = ret2.sum()
        else:
            ret2 = 0
        df = total_trade[(total_trade['in_date'] < date) & (total_trade['ot_date'] == date)]
        if len(df) > 0:
            ret3 = (df['ot_price'] - date_prev_px[date]) * df['pos'] / df['in_price']
            ret3 = ret3.sum()
        else:
            ret3 = 0
        df = total_trade[(total_trade['in_date'] < date) & (total_trade['ot_date'] > date)]
        if len(df) > 0:
            ret4 = (date_last_px[date] - date_prev_px[date]) * df['pos'] / df['in_price']
            ret4 = ret4.sum()
        else:
            ret4 = 0
        daily_ret.append(ret1 + ret2 + ret3 + ret4)
    daily_ret = pd.Series(daily_ret, index=date_list)
    daily_ret.index = pd.to_datetime(daily_ret.index)
    return daily_ret


def get_daily_ret_net(total_trade, date_list, date_last_px):
    total_trade = total_trade.copy()
    date_prev_px = date_last_px.shift()
    daily_ret = []
    for date in date_list:
        df = total_trade[(total_trade['in_date'] == date) & (total_trade['ot_date'] == date)]
        if len(df) > 0:
            ret1 = ((df['ot_price'] - df['in_price']) * df['pos'] - df['in_spread'] / 2 - df['ot_spread'] / 2) / df['in_price'] - df['in_fee'] - df['ot_fee']
            ret1 = ret1.sum()
        else:
            ret1 = 0
        df = total_trade[(total_trade['in_date'] == date) & (total_trade['ot_date'] > date)]
        if len(df) > 0:
            ret2 = ((date_last_px[date] - df['in_price']) * df['pos'] - df['in_spread'] / 2) / df['in_price'] - df['in_fee']
            ret2 = ret2.sum()
        else:
            ret2 = 0
        df = total_trade[(total_trade['in_date'] < date) & (total_trade['ot_date'] == date)]
        if len(df) > 0:
            ret3 = ((df['ot_price'] - date_prev_px[date]) * df['pos'] - df['ot_spread'] / 2) / df['in_price'] - df['ot_fee']
            ret3 = ret3.sum()
        else:
            ret3 = 0
        df = total_trade[(total_trade['in_date'] < date) & (total_trade['ot_date'] > date)]
        if len(df) > 0:
            ret4 = (date_last_px[date] - date_prev_px[date]) * df['pos'] / df['in_price']
            ret4 = ret4.sum()
        else:
            ret4 = 0
        daily_ret.append(ret1 + ret2 + ret3 + ret4)
    daily_ret = pd.Series(daily_ret, index=date_list)
    daily_ret.index = pd.to_datetime(daily_ret.index)
    return daily_ret


def get_stats(total_trade, daily_ret, ret_col='return'):
    total_trade = total_trade.copy()
    num_tickers = len(total_trade['ticker'].drop_duplicates())
    num_tickers = 1
    if len(total_trade) > 0 and (total_trade[ret_col].abs().sum() > 0):
        trade_ret = total_trade[ret_col]
        trade_ret.index = total_trade['ot_time']

        cum_ret = daily_ret.cumsum()
        mdd = cum_ret - cum_ret.expanding().max()
        mdd_val = mdd.min()
        mdd_val = mdd_val / num_tickers
        mdd_end = mdd.idxmin()
        mdd_str = mdd[mdd == 0].loc[:mdd_end].index[-1]

        annual_return = cum_ret.iloc[-1] * (pd.Timedelta('365 days 00:00:00') / (cum_ret.index[-1] - cum_ret.index[0]))
        annual_return = annual_return / num_tickers
        sharpe_ratio = daily_ret.mean() / daily_ret.std() * np.sqrt(252)
        win_ratio = trade_ret.where(trade_ret > 0, np.nan).count() / trade_ret.count()
        profit_loss = -1 * trade_ret.where(trade_ret > 0, np.nan).mean() / trade_ret.where(trade_ret < 0, np.nan).mean()
        ret_per_trade = trade_ret.mean()
        avg_hold_bars = total_trade['hold_bars'].mean()
        avg_hold_time = total_trade['hold_time'].mean()
        trade_per_day = trade_ret.count() / daily_ret.count()
        trade_per_day = trade_per_day / num_tickers

        stats = {
            'annual_return': f'{annual_return:.2%}',
            'sharpe_ratio': f'{sharpe_ratio:.2f}',
            'win_ratio': f'{win_ratio:.2%}',
            'profit_loss': f'{profit_loss:.2f}',
            'ret_per_trade': f'{ret_per_trade:.4%}',
            'avg_hold_bars': f'{avg_hold_bars:.2f}',
            'avg_hold_time': f'{avg_hold_time:.2f}',
            'trade_per_day': f'{trade_per_day:.2f}',
            'mdd': f'{mdd_val:.2%}',
            'mdd_start': mdd_str.strftime('%Y-%m-%d'),
            'mdd_end': mdd_end.strftime('%Y-%m-%d'),
        }
    else:
        stats = {
            'annual_return': '-',
            'sharpe_ratio': '-',
            'win_ratio': '-',
            'profit_loss': '-',
            'ret_per_trade': '-',
            'avg_hold_bars': '-',
            'avg_hold_time': '-',
            'trade_per_day': '-',
            'mdd': '-',
            'mdd_start': '-',
            'mdd_end': '-',
        }
    return stats


def draw_plot(result, title, show_plot, save_plot, save_path):
    raw_stats = result['raw_stats']
    raw_stats_l = result['raw_stats_l']
    raw_stats_s = result['raw_stats_s']
    raw_cum_ret = result['raw_cum_ret']
    raw_cum_ret_l = result['raw_cum_ret_l']
    raw_cum_ret_s = result['raw_cum_ret_s']
    net_stats = result['net_stats']
    net_stats_l = result['net_stats_l']
    net_stats_s = result['net_stats_s']
    net_cum_ret = result['net_cum_ret']
    net_cum_ret_l = result['net_cum_ret_l']
    net_cum_ret_s = result['net_cum_ret_s']
    itd_cum_ret = result['itd_cum_ret']
    ovn_cum_ret = result['ovn_cum_ret']
    ss1_cum_ret = result['ss1_cum_ret']
    ss2_cum_ret = result['ss2_cum_ret']
    prev_corr = result['prev_corr']
    next_corr = result['next_corr']

    plt.rcParams['font.sans-serif'] = ['DejaVu Sans Mono']
    head_size = 16
    text_size = 12
    line_width = 1.5
    title_size = 12
    label_size = 12

    fig = plt.figure(figsize=(20, 16))

    ax = fig.add_subplot(4, 2, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    d1 = raw_cum_ret.index[0].strftime('%Y%m%d')
    d2 = raw_cum_ret.index[-1].strftime('%Y%m%d')
    ax.text(0.0, 0.9, f'{title}  ({d1} ~ {d2})', fontsize=head_size)

    ax.text(0.2, 0.8, 'Total', fontsize=text_size)
    ax.text(0.4, 0.8, 'Long', fontsize=text_size)
    ax.text(0.6, 0.8, 'Short', fontsize=text_size)
    keys = list(raw_stats.keys())
    for i, key in enumerate(keys):
        ax.text(0.0, 0.8 - (i + 1) * 0.07, f'{key}', fontsize=text_size)
    for i, key in enumerate(keys):
        ax.text(0.2, 0.8 - (i + 1) * 0.07, f'{raw_stats[key]}', fontsize=text_size)
    for i, key in enumerate(keys):
        ax.text(0.4, 0.8 - (i + 1) * 0.07, f'{raw_stats_l[key]}', fontsize=text_size)
    for i, key in enumerate(keys):
        ax.text(0.6, 0.8 - (i + 1) * 0.07, f'{raw_stats_s[key]}', fontsize=text_size)

    ax = fig.add_subplot(4, 2, 2)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # for i, idx in enumerate(next_corr.index[0:5]):
    for i, idx in enumerate([1, 10, 30, 60, 120]):
        ax.text(i * 0.2, 0.9, f'IC-{idx}:{next_corr.loc[idx]:.4f}', fontsize=text_size)

    ax.text(0.2, 0.8, 'Total', fontsize=text_size)
    ax.text(0.4, 0.8, 'Long', fontsize=text_size)
    ax.text(0.6, 0.8, 'Short', fontsize=text_size)
    keys = list(net_stats.keys())
    for i, key in enumerate(keys):
        ax.text(0.0, 0.8 - (i + 1) * 0.07, f'{key}', fontsize=text_size)
    for i, key in enumerate(keys):
        ax.text(0.2, 0.8 - (i + 1) * 0.07, f'{net_stats[key]}', fontsize=text_size)
    for i, key in enumerate(keys):
        ax.text(0.4, 0.8 - (i + 1) * 0.07, f'{net_stats_l[key]}', fontsize=text_size)
    for i, key in enumerate(keys):
        ax.text(0.6, 0.8 - (i + 1) * 0.07, f'{net_stats_s[key]}', fontsize=text_size)

    ax = fig.add_subplot(4, 2, 3)
    ax.plot(raw_cum_ret, color='royalblue', linewidth=line_width)
    ax.set_title('Cumulative Return', fontsize=title_size)
    ax.tick_params(labelsize=label_size)
    ax.grid()

    ax = fig.add_subplot(4, 2, 4)
    ax.plot(net_cum_ret, color='royalblue', linewidth=line_width)
    ax.set_title('Cumulative Return', fontsize=title_size)
    ax.tick_params(labelsize=label_size)
    ax.grid()

    ax = fig.add_subplot(4, 2, 5)
    ax.plot(raw_cum_ret_l, color='red', linewidth=line_width)
    ax.plot(raw_cum_ret_s, color='green', linewidth=line_width)
    ax.set_title('Long/Short Return', fontsize=title_size)
    ax.tick_params(labelsize=label_size)
    ax.grid()

    ax = fig.add_subplot(4, 2, 6)
    ax.plot(net_cum_ret_l, color='red', linewidth=line_width)
    ax.plot(net_cum_ret_s, color='green', linewidth=line_width)
    ax.set_title('Long/Short Return', fontsize=title_size)
    ax.tick_params(labelsize=label_size)
    ax.grid()

    ax = fig.add_subplot(4, 2, 7)
    ax.plot(ss1_cum_ret, color='red', linewidth=line_width)
    ax.plot(ss2_cum_ret, color='green', linewidth=line_width)
    ax.plot(itd_cum_ret, color='royalblue', linewidth=line_width)
    ax.plot(ovn_cum_ret, color='dimgray', linewidth=line_width)
    ax.set_title('Intraday(Blue) / Overnight(Gray) / Day(Red) / Night(Green)', fontsize=title_size)
    ax.tick_params(labelsize=label_size)
    ax.grid()

    ax = fig.add_subplot(4, 4, 15)
    ss = prev_corr.copy()
    ss.index = [str(idx) for idx in ss.index]
    ax.bar(ss.index, ss.values, color='royalblue', width=0.8)
    ax.set_title('Trend', fontsize=title_size)
    ax.tick_params(labelsize=label_size)
    ax.grid()

    ax = fig.add_subplot(4, 4, 16)
    ss = next_corr.copy()
    ss.index = [str(idx) for idx in ss.index]
    ax.bar(ss.index, ss.values, color='royalblue', width=0.8)
    ax.set_title('IC', fontsize=title_size)
    ax.tick_params(labelsize=label_size)
    ax.grid()

    plt.tight_layout()
    if save_plot:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(f'{save_path}/{title}.png', format='png', dpi=100)
    if show_plot:
        plt.show()
    plt.close()
    return None


def draw_plot2(stats, title, show_plot, save_plot, save_path):
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans Mono']
    title_size = 12
    label_size = 12

    names = stats.columns.to_list()
    n = len(names)
    num_cols = 2
    num_rows = int(np.ceil(n / num_cols))

    fig = plt.figure(figsize=(num_cols * 10, num_rows * 4))
    for i, name in enumerate(names):
        ss = stats[name]
        mm = ss.mean()
        ax = fig.add_subplot(num_rows, num_cols, i + 1)
        ax.bar(ss.index, ss.values, color='royalblue', width=0.8)
        ax.tick_params(labelsize=label_size)
        ax.xaxis.set_tick_params(rotation=90)
        if 'annual_return' in name:
            ax.yaxis.set_major_formatter(mtk.PercentFormatter(xmax=1, decimals=0))
            ax.set_title(f'{name} ({mm:.2%})', fontsize=title_size)
        elif 'ret_per_trade' in name:
            ax.yaxis.set_major_formatter(mtk.PercentFormatter(xmax=1, decimals=2))
            ax.set_title(f'{name} ({mm:.4%})', fontsize=title_size)
        else:
            ax.set_title(f'{name} ({mm:.4f})', fontsize=title_size)
        ax.grid()

    plt.tight_layout()
    if save_plot:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(f'{save_path}/{title}.png', format='png')
    if show_plot:
        plt.show()
    plt.close()
    return None
