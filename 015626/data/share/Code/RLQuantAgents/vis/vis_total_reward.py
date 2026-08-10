import math
import pickle
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import io
import os
from PIL import Image
import pandas as pd

def plot_return_by_position_bins(pos, arr1, bin_width=0.1):
    bins = np.arange(-1.0, 1.0 + bin_width, bin_width)
    bin_lables = [f"{round(bins[i], 1)}~{round(bins[i+1], 1)}" for i in range(len(bins)-1)]
    total_returns = []
    sample_counts = []
    #timestamps_np = np.array(timestamp_list, dtype='datatime64[m]')
    for i in range(len(bins)-1):
        mask = (pos>=bins[i]) & (pos<bins[i+1])
        selected_returns = arr1[mask]
        total_returns.append(selected_returns.sum())
        sample_counts.append(len(selected_returns))
    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=bin_lables,
            y=total_returns,
            marker=dict(
                color='rgba(100,149,237,0.7)',
                line=dict(color='rgba(30,90,180,1.0)',width=1.2)
            ),
            name='Total Return',
            customdata=np.array(sample_counts).reshape(-1,1),
            hovertemplate=(
                'Pos Range: %{x}<br>'
                'Total Reward: %{y:.6f}<br>'
                'Sample Count: %{custumdata[0]<extra></extra>}'
            )
        )
    )
    fig3.update_layout(
        title='Position and Reward Distribution',
        xaxis_title='Position Range',
        yaxis_title='Total Reward',
        font=dict(family='Times New Roman', size=14),
        template='plotly_white',
        height=500,
        margin=dict(l=60, r=30,t=60,b=80),
        bargap=0.15
    )
    return fig3
def plot_long_short_curve(arr1, pos, timestamp_list):
    arr1 = np.asarray(arr1)
    pos = np.asarray(pos)
    long_returns = arr1 * (pos > 0)
    long_cumsum = np.cumsum(long_returns)
    short_returns = arr1 * (pos < 0)
    short_cumsum = np.cumsum(short_returns)

    net_returns = arr1
    net_cumsum = np.cumsum(net_returns)
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(x=timestamp_list, y=long_cumsum, mode='lines', line=dict(color='red', width=3), name='Long Only')
    )
    fig2.add_trace(
        go.Scatter(x=timestamp_list, y=short_cumsum, mode='lines', line=dict(color='green', width=3), name='Short Only')
    )
    fig2.add_trace(
        go.Scatter(x=timestamp_list,y=net_cumsum, mode='lines', line=dict(color='blue', width=3), name='Total')
    )
    fig2.update_layout(
        width=2000,
        height=500
    )
    fig2.update_layout(
        title='Long/Short Cumulative Returns',
        xaxis_title='Time',
        yaxis_title='Cumulative Return',
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        font=dict(family='Times New Roman, Times, serif', size=12),
        legend=dict(x=0.01, y=0.99)
    )
    return fig2


def calc_sharpe_ratio(returns):
    excess_returns = returns
    mean = np.mean(excess_returns)
    print(mean)
    std = np.std(excess_returns)
    print(std)
    sharpe = mean / std * math.sqrt(250) if std > 1e-8 else 0
    print(sharpe)
    return sharpe


def calc_max_drawdown(cumulative_returns):
    peak = np.maximum.accumulate(cumulative_returns)
    drawdowns = (cumulative_returns - peak)
    max_drawdown = drawdowns.min()
    return max_drawdown

def autocorr_at_lag(signal, lag=5):
    signal = np.asarray(signal)
    if len(signal) <= lag:
        return np.nan
    x = signal[:-lag]
    y = signal[lag:]
    x_mean = np.mean(signal)
    numerator = np.mean((x-x_mean)*(y-x_mean))
    denominator = np.var(signal)
    return numerator / denominator

def cal_turnover(pos, timestamp_list):
    pos = np.array(pos)
    timestamp_list = pd.to_datetime(timestamp_list)
    pos_change = np.abs(np.diff(pos, prepend=0))
    total_turnover = pos_change.sum()
    leveraged_turnover = np.sum(np.abs(pos_change * pos))
    trading_days = timestamp_list.normalize().nunique()
    turnover_per_day = total_turnover / trading_days
    leveraged_turnover_per_day = leveraged_turnover / trading_days
    print(total_turnover)
    print(leveraged_turnover_per_day)
    print(trading_days)
    print(turnover_per_day)
    return turnover_per_day, leveraged_turnover_per_day


if __name__ == '__main__':
    #val_dir = '/home/appadmin/RLQuantAgents/engine/runs/20250417-090949_dmodel128_lr1e-05_test'
    #val_dir = '/home/appadmin/RLQuantAgents/runs/20250416-142212_dmodel128_lr1e-05'
    #val_dir = '/home/appadmin/RLQuantAgents/runs/20250421-191309_dmodel128_lr1e-05' 13
    val_dir = '/home/appadmin/RLQuantAgents/runs/20250423-155015_dmodel128_lr1e-05'

    f = open(os.path.join(val_dir,'val_minute_reward_epoch11.pkl'),
             'rb')
    minute_data_22 = pickle.load(f)
    f.close()
    f = open(os.path.join(val_dir, 'val_day_reward_epoch11.pkl'), 'rb')
    day_data_22 = pickle.load(f)
    f.close()
    f = open(os.path.join(val_dir, 'val_minute_pos_epoch11.pkl'), 'rb')
    minute_pos_data_22 = pickle.load(f)
    # for i in range(int(7.7/11*len(minute_pos_data)), len(minute_pos_data)):
    #     if minute_pos_data[i] > 0:
    #         minute_pos_data[i] = 0
    f.close()
    # f = open(os.path.join(val_dir, 'val_minute_pos.pkl'), 'wb')
    # pickle.dump(minute_pos_data, f)
    f = open(os.path.join(val_dir, 'val_minute_time_stamp_epoch11.pkl'),
             'rb')
    val_minute_time_stamp_22 = pickle.load(f)
    f.close()
    f = open(os.path.join(val_dir, 'val_day_time_stamp_epoch11.pkl'),
             'rb')
    val_day_time_stamp_22 = pickle.load(f)
    f.close()

    #val_dir = '/home/appadmin/RLQuantAgents/runs/20250421-193755_dmodel128_lr1e-05' 7
    val_dir = '/home/appadmin/RLQuantAgents/runs/20250423-161342_dmodel128_lr1e-05'

    f = open(os.path.join(val_dir,'val_minute_reward_epoch16.pkl'),
             'rb')
    minute_data_23 = pickle.load(f)
    f.close()
    f = open(os.path.join(val_dir, 'val_day_reward_epoch16.pkl'), 'rb')
    day_data_23 = pickle.load(f)
    f.close()
    f = open(os.path.join(val_dir, 'val_minute_pos_epoch16.pkl'), 'rb')
    minute_pos_data_23 = pickle.load(f)
    # for i in range(int(7.7/11*len(minute_pos_data)), len(minute_pos_data)):
    #     if minute_pos_data[i] > 0:
    #         minute_pos_data[i] = 0
    f.close()
    # f = open(os.path.join(val_dir, 'val_minute_pos.pkl'), 'wb')
    # pickle.dump(minute_pos_data, f)
    f = open(os.path.join(val_dir, 'val_minute_time_stamp_epoch16.pkl'),
             'rb')
    val_minute_time_stamp_23 = pickle.load(f)
    f.close()
    f = open(os.path.join(val_dir, 'val_day_time_stamp_epoch16.pkl'),
             'rb')
    val_day_time_stamp_23 = pickle.load(f)
    f.close()


    val_dir = '/home/appadmin/RLQuantAgents/runs/20250423-161437_dmodel128_lr1e-05'
    f = open(os.path.join(val_dir,'val_minute_reward_epoch6.pkl'),
             'rb')
    minute_data_24 = pickle.load(f)
    f.close()
    f = open(os.path.join(val_dir, 'val_day_reward_epoch6.pkl'), 'rb')
    day_data_24 = pickle.load(f)
    f.close()
    f = open(os.path.join(val_dir, 'val_minute_pos_epoch6.pkl'), 'rb')
    minute_pos_data_24 = pickle.load(f)
    # for i in range(int(7.7/11*len(minute_pos_data)), len(minute_pos_data)):
    #     if minute_pos_data[i] > 0:
    #         minute_pos_data[i] = 0
    f.close()
    # f = open(os.path.join(val_dir, 'val_minute_pos.pkl'), 'wb')
    # pickle.dump(minute_pos_data, f)
    f = open(os.path.join(val_dir, 'val_minute_time_stamp_epoch6.pkl'),
             'rb')
    val_minute_time_stamp_24 = pickle.load(f)
    f.close()
    f = open(os.path.join(val_dir, 'val_day_time_stamp_epoch6.pkl'),
             'rb')
    val_day_time_stamp_24 = pickle.load(f)
    f.close()

    arr1 = minute_data_22 + minute_data_23 + minute_data_24
    arr1 = np.array(arr1)
    arr2 = np.array(day_data_22 + day_data_23 + day_data_24)
    arr2 = np.array(arr2)
    #assert len(val_day_time_stamp) == len(day_data)
    #assert len(val_minute_time_stamp) == len(minute_pos_data)
    negative_count = 0
    positive_count = 0
    arr3 = minute_pos_data_22 + minute_pos_data_23 + minute_pos_data_24
    arr3 = np.array(arr3)
    for i in range(len(arr3)):
        if arr3[i] > 0.8:
            positive_count += 1
        if arr3[i] < -0.8:
            negative_count += 1
    print(negative_count)
    print(positive_count)
    print(len(arr3)-negative_count)
    arr1_cumsum = np.cumsum(arr1)
    arr2_cumsum = np.cumsum(arr2)
    # arr3_cumsum = np.cumsum(arr3)
    # x = range(len(arr1_cumsum))
    sharpe = calc_sharpe_ratio(arr1)
    max_dd = calc_max_drawdown(arr1_cumsum)
    val_minute_time_stamp = val_minute_time_stamp_22 + val_minute_time_stamp_23 + val_minute_time_stamp_24
    x = list(val_minute_time_stamp)
    turnover_day, leveraged_turnover_day = cal_turnover(arr3, x)
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.update_layout(
        width=2000,
        height=500
    )

    winrate = np.sum(arr2 > 0) / len(arr2)
    corr_lag5 = autocorr_at_lag(arr3, lag=5)
    annotation_text = (
        f"shrp/min: {sharpe:.4f}<br>"
        f"bdd/min: {max_dd:.2f}%<br>"
        f"wr/day: {winrate:.2f}<br>"
        f"lag5-corr: {corr_lag5:.3f}<br>"
        f"to/day:{turnover_day:.2f}<br>"
        f"lto/day:{leveraged_turnover_day:.2f}"
    )
    fig1.add_annotation(
        xref='paper', yref='paper',
        x=0.01, y=0.99,
        text=annotation_text,
        showarrow=False,
        align="left",
        font=dict(family='Times New Roman, Times, serif', size=12, color='black'),
        # bgcolor='rgba(255,255,255,0.85)',
        # bordercolor='black',
        # borderwidth=1
    )

    fig1.add_trace(go.Scatter(x=x, y=arr1_cumsum, mode='lines+markers', line=dict(width=2), marker=dict(size=2),
                              name='reward ratio'), secondary_y=False)
    fig1.add_trace(go.Scatter(x=x, y=arr3, mode='lines+markers', line=dict(width=0.1), marker=dict(size=0.1),
                              name='position ratio'), secondary_y=True)
    fig1.update_layout(
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickmode='auto',
            nticks=20,
            tickangle=45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title='Cumsum Ratio',
            showgrid=True,
            gridcolor='lightgray'
        ),
        yaxis2=dict(
            title='Position Ratio',
            showgrid=False,
            range=[-3, 3]
        )
    )
    fig1.update_layout(
        font=dict(
            family='Times New Roman, Times,serif'
        ),
        plot_bgcolor='#F5F5F5',
        paper_bgcolor='#FFFFFF',
        title='reward and postion ratio',
        xaxis_title='time/minute',
        # yaxis_title = 'cumulative reward & pos_num',
        template='plotly_white',
    )
    # fig1.show()
    fig1.write_image('/dfs/group/800466/intern/wyb/reward_pos.png')
    fig2 = plot_long_short_curve(arr1, arr3, x)
    fig2.write_image('/dfs/group/800466/intern/wyb/reward_pos_longshort.png')
    fig3 = plot_return_by_position_bins(arr3, arr1)
    fig3.write_image('/dfs/group/800466/intern/wyb/pos_reward_ratio.png')
#  plt.figure(figsize=(6,4))
#  plt.plot(x, arr1_cumsum, marker='o', label='Cumulative Minute Reward:%', markersize=0.2)
#  #plt.plot(x, arr3, marker='o', label='position ratio')
#  plt.title('Cumulative Minute Reward: 2021-10-25 09:45:00---2022-12-30 14:41:00')
#  plt.xlabel('time/minute')
#  plt.ylabel('total minute reward/%')
#  plt.grid(True)
#  plt.tight_layout()
#  plt.savefig('/dfs/group/800466/intern/reward_minute.png')
#
#  plt.figure(figsize=(6,4))
#  plt.plot(x, arr3, marker='o', label='Position Ratio/%', markersize=0.2)
#  #plt.plot(x, arr3, marker='o', label='position ratio')
#  plt.title('Position Ratio')
#  plt.xlabel('Position Ratio')
#  plt.ylabel('Ratio')
#  plt.grid(True)
#  plt.tight_layout()
#  plt.savefig('/dfs/group/800466/intern/pos_ratio.png')
#  x = range(len(arr2_cumsum))
#  plt.figure(figsize=(6,4))
#  plt.title('Cumulative Daily Reward: 2021-10-25---2022-12-30')
#  plt.plot(x, arr2_cumsum, marker='o', markersize=0.2, label='Daily Reward: %')
# # plt.title('Cumulative Daily Reward')
#  plt.xlabel('time/day')
#  plt.ylabel('total daily reward/%')
#  plt.grid(True)
#  plt.tight_layout()
#  plt.savefig('/dfs/group/800466/intern/reward_daily.png')
#
