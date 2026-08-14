import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体，适用于 Windows
rcParams['axes.unicode_minus'] = False

def sta_profit(index_label,index_label_Tc2b10,index_label_TNo2Tc,index_label_TNv2TNo,profit_pos,profit_neg,profit,signal,exposure):
    res = {}
    res['做多信号天数'] = (signal==1).sum()
    res['做多日均敞口（万元）'] = exposure[exposure>1e8].mean() / 10000
    res['做空信号天数'] = (signal==-1).sum()
    res['做空日均敞口（万元）'] = exposure[exposure<-1e8].mean() / 10000
    res['做多收益（万元）'] = profit_pos.sum()/10000
    res['做空收益（万元）'] = profit_neg.sum()/10000
    res['收益（万元）'] = profit.sum() / 10000
    # 做多收益率
    res['做多平均收益率'] = (index_label * signal.replace(-1, np.nan)).mean()
    res['做多平均收益率_T'] = (index_label_Tc2b10 * signal.replace(-1, np.nan)).mean()
    res['做多平均收益率_隔夜'] = (index_label_TNo2Tc * signal.replace(-1, np.nan)).mean()
    res['做多平均收益率_T1'] = (index_label_TNv2TNo * signal.replace(-1, np.nan)).mean()
    # 做空收益率
    res['做空平均收益率'] = (index_label * signal.replace(1, np.nan)).mean()
    res['做空平均收益率_T'] = (index_label_Tc2b10 * signal.replace(1, np.nan)).mean()
    res['做空平均收益率_隔夜'] = (index_label_TNo2Tc * signal.replace(1, np.nan)).mean()
    res['做空平均收益率_T1'] = (index_label_TNv2TNo * signal.replace(1, np.nan)).mean()
    # 平均收益率
    res['平均收益率'] = (index_label*signal).mean()
    res['平均收益率_T'] = (index_label_Tc2b10 * signal).mean()
    res['平均收益率_隔夜'] = (index_label_TNo2Tc * signal).mean()
    res['平均收益率_T1'] = (index_label_TNv2TNo * signal).mean()
    res['做多最大回撤（万元）'] = (profit_pos.cumsum().cummax() - profit_pos.cumsum()).max() / 10000
    res['做空最大回撤（万元）'] = (profit_neg.cumsum().cummax() - profit_neg.cumsum()).max() / 10000
    res['最大回撤（万元）'] = (profit.cumsum().cummax() - profit.cumsum()).max() / 10000
    res['做多收益风险比'] = res['做多收益（万元）'] / res['做多最大回撤（万元）']
    res['做空收益风险比'] = res['做空收益（万元）'] / res['做空最大回撤（万元）']
    res['收益风险比'] = res['收益（万元）'] / res['最大回撤（万元）']
    res['做多日扣费胜率'] = len(profit_pos[profit_pos > 0]) / len(profit_pos[profit_pos != 0]) if len(profit_pos[profit_pos != 0]) else np.nan
    res['做空日扣费胜率'] = len(profit_neg[profit_neg > 0]) / len(profit_neg[profit_neg != 0]) if len(profit_neg[profit_neg != 0]) else np.nan
    res['日扣费胜率'] = len(profit[profit > 0]) / len(profit[profit != 0]) if len(profit[profit != 0]) else np.nan
    roll_profit_pos = profit_pos.rolling(3, min_periods=1).sum()
    res['做多收益夏普比'] = roll_profit_pos.mean() / roll_profit_pos.std() * 250 ** 0.5 if roll_profit_pos.std() else np.nan
    roll_profit_neg = profit_neg.rolling(3, min_periods=1).sum()
    res['做空收益夏普比'] = roll_profit_neg.mean() / roll_profit_neg.std() * 250 ** 0.5 if roll_profit_neg.std() else np.nan
    roll_profit = profit.rolling(3, min_periods=1).sum()
    res['收益夏普比'] = roll_profit.mean() / roll_profit.std() * 250 ** 0.5 if roll_profit.std() else np.nan
    return pd.Series(res)

def create_plot(data,title):
    fig, ax = plt.subplots(figsize=(6, 4))
    for period in ['sc_mid_vote4_min10','sc_mid_vote3_min10','sc_mid_vote2_min10']:# ['sc_short', 'sc_mid', 'sc_long', 's1_short', 's1_mid', 's1_long']:
        ax.plot(data.index, data[f'profit_index_{period}'].cumsum(), label=f'{period}')
    ax.set_title(title)
    ax.set_xlabel('日期')
    ax.set_ylabel('累计收益')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    ax.grid(True)
    plt.setp(ax.get_xticklabels(), rotation=45)
    plt.tight_layout()
    img = io.BytesIO()
    fig.savefig(img, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    img.seek(0)
    return img

def create_plot_modified(data,title):
    fig, ax = plt.subplots(figsize=(6, 4))
    for period in ['sc_mid_vote4_min10','sc_mid_vote3_min10','sc_mid_vote2_min10']:# ['sc_short', 'sc_mid', 'sc_long', 's1_short', 's1_mid', 's1_long']:
        ax.plot(data.index, data[f'profit_future_{period}'].cumsum(), label=f'{period}')
    ax.set_title(title)
    ax.set_xlabel('日期')
    ax.set_ylabel('累计收益')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    ax.grid(True)
    plt.setp(ax.get_xticklabels(), rotation=45)
    plt.tight_layout()
    img = io.BytesIO()
    fig.savefig(img, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    img.seek(0)
    return img

def calc_exposure(df, label):
    tp = label.split('_')[0]
    period = label.split('_')[1]
    vote = label.split('_')[2]
    pr = label.split('_')[3]
    df[f'{tp}_{period}_{vote}_{pr}'] = df[f'{tp}_pos_{period}_{vote}_{pr}'] - df[f'{tp}_neg_{period}_{vote}_{pr}']
    return df

def calc_signal(df, label):
    df[f'signal_{label}'] = df[f'{label}'].apply(lambda x: 1 if x>1e8 else -1 if x<-1e8 else np.nan)
    return df

def calc_profit(df, label):
    # 多空收益分开看
    tp = label.split('_')[0]
    period = label.split('_')[1]
    vote = label.split('_')[2]
    pr = label.split('_')[3]

    df[f'profit_index_{tp}_{period}_{vote}_{pr}_pos'] = df.apply(lambda x: x[f'{tp}_{period}_{vote}_{pr}'] * x[f'signal_{tp}_{period}_{vote}_{pr}'] * (x[f'index_label_{tp}_{period}'] - 0.001) if x[f'signal_{tp}_{period}_{vote}_{pr}'] == 1 else 0, axis=1)
    df[f'profit_index_{tp}_{period}_{vote}_{pr}_neg'] = df.apply(lambda x: x[f'{tp}_{period}_{vote}_{pr}'] * x[f'signal_{tp}_{period}_{vote}_{pr}'] * (-x[f'index_label_{tp}_{period}'] - 0.0015) if x[f'signal_{tp}_{period}_{vote}_{pr}'] == -1 else 0, axis=1)
    df[f'profit_index_{tp}_{period}_{vote}_{pr}'] = df[f'profit_index_{tp}_{period}_{vote}_{pr}_pos'] + df[f'profit_index_{tp}_{period}_{vote}_{pr}_neg']

    df[f'profit_future_{tp}_{period}_{vote}_{pr}_pos'] = df.apply(lambda x: x[f'{tp}_{period}_{vote}_{pr}'] * x[f'signal_{tp}_{period}_{vote}_{pr}'] * (x[f'future_label_{tp}_{period}'] - 0.0005) \
        if (x[f'signal_{tp}_{period}_{vote}_{pr}'] == 1 and x.name >= pd.Timestamp('20220722'))
        else x[f'{tp}_{period}_{vote}_{pr}'] * x[f'signal_{tp}_{period}_{vote}_{pr}'] * (x[f'future_label_{tp}_{period}'] - 0.001) if (x[f'signal_{tp}_{period}_{vote}_{pr}'] == 1 and x.name < pd.Timestamp('20220722'))
        else 0,axis=1)
    df[f'profit_future_{tp}_{period}_{vote}_{pr}_neg'] = df.apply(lambda x: x[f'{tp}_{period}_{vote}_{pr}'] * x[f'signal_{tp}_{period}_{vote}_{pr}'] * (-x[f'future_label_{tp}_{period}'] - 0.0005) \
        if (x[f'signal_{tp}_{period}_{vote}_{pr}'] == -1 and x.name >= pd.Timestamp('20220722'))
        else x[f'{tp}_{period}_{vote}_{pr}'] * x[f'signal_{tp}_{period}_{vote}_{pr}'] * (-x[f'future_label_{tp}_{period}'] - 0.0015) if (x[f'signal_{tp}_{period}_{vote}_{pr}'] == -1 and x.name < pd.Timestamp('20220722'))
        else 0,axis=1)
    df[f'profit_future_{tp}_{period}_{vote}_{pr}'] = df[f'profit_future_{tp}_{period}_{vote}_{pr}_pos'] + df[f'profit_future_{tp}_{period}_{vote}_{pr}_neg']
    return df

# baseline: 信号独立开仓，合并计算收益
def calc_profit_all_independent(df,time_points,periods):
    df['profit_all_pos'] = df[[f'profit_{tp}_{period}_pos' for tp in time_points for period in periods]].sum(axis=1)
    df['profit_all_neg'] = df[[f'profit_{tp}_{period}_neg' for tp in time_points for period in periods]].sum(axis=1)
    df['profit_all'] = df[[f'profit_{tp}_{period}' for tp in time_points for period in periods]].sum(axis=1)
    return df

# 定义信号路径与延续规则
def compute_modified_profit(df):
    df = df.copy()
    dates = df.index
    N = len(dates)
    # profit = pd.Series(0.0, index=dates)
    # profit_pos = pd.Series(0.0, index=dates)
    # profit_neg = pd.Series(0.0, index=dates)
    for path in ['s1_short_vote3','sc_mid_vote3','s1_short_vote2','sc_mid_vote2']:
        df[f'profit_modified_{path}_pos'] = 0.0
        df[f'profit_modified_{path}_neg'] = 0.0
        df[f'profit_modified_{path}'] = 0.0
    # 所有信号路径延续图
    signal_path_graph_early_close = {
        's1_short_vote3': '',
        's1_short_vote2': '',
        # 's1_mid': '',
        # 's1_long': 'sc_short',  # 先判断在sc是否提前平仓
        # 'sc_short': '',
        'sc_mid_vote3': 's1_short_vote3',  # 判断是否在s1提前平仓
        'sc_mid_vote2': 's1_short_vote2',  # 判断是否在s1提前平仓
        # 'sc_long': 's1_mid',  # 判断在s1是否提前平仓
    }
    signal_path_graph = {
        's1_short_vote3': [],
        's1_short_vote2': [],
        # 's1_mid': ['sc_short', 'sc_mid', 'sc_long'],
        # 's1_long': ['s1_short','s1_mid', 's1_long'],
        # 'sc_short': ['s1_short', 's1_mid', 's1_long'],
        'sc_mid_vote3': [],
        'sc_mid_vote2': [],
        # 'sc_long': ['sc_short', 'sc_mid', 'sc_long'],
    }

    # 所有路径（统一处理）
    all_paths = list(signal_path_graph.keys())

    for i in range(N):
        dt = dates[i]

        for path in all_paths:
            signal_col = f'signal_{path}'
            expo_col   = path

            if signal_col not in df.columns:
                continue

            signal = df.at[dt, signal_col]
            expo   = df.at[dt, expo_col]

            if signal == 0 or expo == 0:
                continue

            position = signal * expo
            cumulative_return = 1.0  # 用于复利累乘

            # 初始化递归路径追踪器
            current_signal = signal
            current_path = path
            current_label = path[:-6]
            current_day_idx = i
            visited = set()

            while current_day_idx < N:
                cur_dt = dates[current_day_idx]
                sig_col = f'signal_{current_path}'
                ret_col = f'index_label_{current_label}'

                # 当前路径收益（按方向修正）
                sig = df.at[cur_dt, sig_col]
                ret = df.at[cur_dt, ret_col]

                if sig != current_signal:
                    break  # 方向变化则不再延续

                cumulative_return = cumulative_return*(1+ret)
                visited.add((current_day_idx, current_path))

                # 查找下一跳路径
                found_next = False

                # -----------------提前平仓模块-------------------
                if current_path.startswith(('s1_long','sc_mid','sc_long')):
                    if current_path.startswith('s1_long'):
                        next_day_idx = current_day_idx

                    else:
                        next_day_idx = current_day_idx + 1
                        if next_day_idx >= N:
                            break # 无下一天

                    next_path = signal_path_graph_early_close.get(current_path, '')
                    next_label = next_path[:-6]
                    next_dt = dates[next_day_idx]
                    next_sig_col = f'signal_{next_path}'
                    next_ret_col = f'index_label_{next_label}'
                    if df.at[next_dt, next_sig_col] * current_signal == -1:
                        next_return = df.at[next_dt, next_ret_col]
                        cumulative_return = (cumulative_return / (1 + next_return))
                        break

                # -------------------延续模块------------------
                if current_path.startswith(('s1_short','s1_mid')):
                    next_day_idx = current_day_idx
                    next_candidates = signal_path_graph.get(current_path, [])
                elif current_path.startswith(('sc','s1_long')):
                    next_day_idx = current_day_idx + 1
                    if next_day_idx >= N:
                        break # 无下一天
                    next_candidates = signal_path_graph.get(current_path, [])
                else:
                    break # 已开启提前平仓

                next_dt = dates[next_day_idx]

                for next_path in next_candidates:

                    next_sig_col = f'signal_{next_path}'
                    if df.at[next_dt, next_sig_col] == current_signal:
                        current_day_idx = next_day_idx
                        current_path = next_path
                        found_next = True
                        break

                if not found_next:
                    break  # 无后续路径

            total_return_pos = position * (cumulative_return - 1 - 0.001) if signal == 1 else 0
            total_return_neg = position * (1 - cumulative_return - 0.001) if signal == -1 else 0
            total_return = total_return_pos + total_return_neg

            df.loc[dt, f'index_label_{path}_modified'] = cumulative_return - 1
            df.loc[dt, f'profit_modified_{path}_pos'] = total_return_pos
            df.loc[dt, f'profit_modified_{path}_neg'] = total_return_neg
            df.loc[dt, f'profit_modified_{path}'] = total_return
            # profit_pos[dt] += total_return_pos
            # profit_neg[dt] += total_return_neg
            # profit[dt] += total_return

    # df['profit_modified_pos'] = profit_pos
    # df['profit_modified_neg'] = profit_neg
    # df['profit_modified'] = profit
    return df


labels = ['sc_mid_vote4_min10','sc_mid_vote3_min10','sc_mid_vote2_min10']
end_date = 20240630

# # 区间1
data_period1 = pd.read_excel('/data/user/013550/For_TSQ/neptune/fac_20250609_sc_mid/区间1_区间8_min10_vote234_单日模拟成交金额_sc.xlsx',sheet_name='区间1',index_col=0)
data_period1 = data_period1.rename(columns={'sc_pos_mid_vote4':'sc_pos_mid_vote4_min10','sc_neg_mid_vote4':'sc_neg_mid_vote4_min10',\
                                   'sc_pos_mid_vote3':'sc_pos_mid_vote3_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10',\
                                   'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_neg_mid_vote2':'sc_neg_mid_vote2_min10'})

# data_period1_vote4_min10 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间4_min10_vote4_每日投资金额汇总.xlsx',sheet_name='区间1',index_col=0)[['sc_pos_mid','sc_neg_mid']]
# data_period1_vote4_min10 = data_period1_vote4_min10.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min10','sc_neg_mid':'sc_neg_mid_vote4_min10'})
# data_period1_vote4_min20 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间4_min20_vote4_每日投资金额汇总.xlsx',sheet_name='区间1',index_col=0)[['sc_pos_mid','sc_neg_mid']]
# data_period1_vote4_min20 = data_period1_vote4_min20.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min20','sc_neg_mid':'sc_neg_mid_vote4_min20'})
# data_period1_vote23 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间7_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间1',index_col=0)
# data_period1_vote23 = data_period1_vote23.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period1 = pd.concat([data_period1_vote4_min10,data_period1_vote4_min20,data_period1_vote23],axis=1)

# data_period1_vote23_min10_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间1_下限10',index_col=0)
# data_period1_vote23_min10_s1 = data_period1_vote23_min10_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min10','s1_pos_short_vote3':'s1_pos_short_vote3_min10','s1_pos_short_vote4':'s1_pos_short_vote4_min10',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min10','s1_neg_short_vote3':'s1_neg_short_vote3_min10','s1_neg_short_vote4':'s1_neg_short_vote4_min10'})
# data_period1_vote23_min20_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间1_下限20',index_col=0)
# data_period1_vote23_min20_s1 = data_period1_vote23_min20_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min20','s1_pos_short_vote3':'s1_pos_short_vote3_min20','s1_pos_short_vote4':'s1_pos_short_vote4_min20',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min20','s1_neg_short_vote3':'s1_neg_short_vote3_min20','s1_neg_short_vote4':'s1_neg_short_vote4_min20'})
# data_period1_vote23_min10_sc = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间6_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间1',index_col=0)[['sc_pos_mid_vote2','sc_pos_mid_vote3','sc_neg_mid_vote2','sc_neg_mid_vote3']]
# data_period1_vote23_min10_sc = data_period1_vote23_min10_sc.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period1 = pd.concat([data_period1_vote4_min10,data_period1_vote4_min20,data_period1_vote23_min10_s1,data_period1_vote23_min20_s1,data_period1_vote23_min10_sc],axis=1)
# 
# # 区间2
data_period2 = pd.read_excel('/data/user/013550/For_TSQ/neptune/fac_20250609_sc_mid/区间1_区间8_min10_vote234_单日模拟成交金额_sc.xlsx',sheet_name='区间2',index_col=0)
data_period2 = data_period2.rename(columns={'sc_pos_mid_vote4':'sc_pos_mid_vote4_min10','sc_neg_mid_vote4':'sc_neg_mid_vote4_min10',\
                                   'sc_pos_mid_vote3':'sc_pos_mid_vote3_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10',\
                                   'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_neg_mid_vote2':'sc_neg_mid_vote2_min10'})
# data_period2_vote4_min10 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间4_min10_vote4_每日投资金额汇总.xlsx',sheet_name='区间2',index_col=0)[['sc_pos_mid','sc_neg_mid']]
# data_period2_vote4_min10 = data_period2_vote4_min10.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min10','sc_neg_mid':'sc_neg_mid_vote4_min10'})
# data_period2_vote4_min20 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间4_min20_vote4_每日投资金额汇总.xlsx',sheet_name='区间2',index_col=0)[['sc_pos_mid','sc_neg_mid']]
# data_period2_vote4_min20 = data_period2_vote4_min20.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min20','sc_neg_mid':'sc_neg_mid_vote4_min20'})
# data_period2_vote23 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间7_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间2',index_col=0)
# data_period2_vote23 = data_period2_vote23.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period2 = pd.concat([data_period2_vote4_min10,data_period2_vote4_min20,data_period2_vote23],axis=1)

# data_period2_vote23_min10_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间2_下限10',index_col=0)
# data_period2_vote23_min10_s1 = data_period2_vote23_min10_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min10','s1_pos_short_vote3':'s1_pos_short_vote3_min10','s1_pos_short_vote4':'s1_pos_short_vote4_min10',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min10','s1_neg_short_vote3':'s1_neg_short_vote3_min10','s1_neg_short_vote4':'s1_neg_short_vote4_min10'})
# data_period2_vote23_min20_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间2_下限20',index_col=0)
# data_period2_vote23_min20_s1 = data_period2_vote23_min20_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min20','s1_pos_short_vote3':'s1_pos_short_vote3_min20','s1_pos_short_vote4':'s1_pos_short_vote4_min20',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min20','s1_neg_short_vote3':'s1_neg_short_vote3_min20','s1_neg_short_vote4':'s1_neg_short_vote4_min20'})
# data_period2_vote23_min10_sc = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间6_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间2',index_col=0)[['sc_pos_mid_vote2','sc_pos_mid_vote3','sc_neg_mid_vote2','sc_neg_mid_vote3']]
# data_period2_vote23_min10_sc = data_period2_vote23_min10_sc.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period2 = pd.concat([data_period2_vote4_min10,data_period2_vote4_min20,data_period2_vote23_min10_s1,data_period2_vote23_min20_s1,data_period2_vote23_min10_sc],axis=1)
# 
# # 区间3
data_period3 = pd.read_excel('/data/user/013550/For_TSQ/neptune/fac_20250609_sc_mid/区间1_区间8_min10_vote234_单日模拟成交金额_sc.xlsx',sheet_name='区间3',index_col=0)
data_period3 = data_period3.rename(columns={'sc_pos_mid_vote4':'sc_pos_mid_vote4_min10','sc_neg_mid_vote4':'sc_neg_mid_vote4_min10',\
                                   'sc_pos_mid_vote3':'sc_pos_mid_vote3_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10',\
                                   'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_neg_mid_vote2':'sc_neg_mid_vote2_min10'})
# data_period3_vote4_min10 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间4_min10_vote4_每日投资金额汇总.xlsx',sheet_name='区间3',index_col=0)[['sc_pos_mid','sc_neg_mid']]
# data_period3_vote4_min10 = data_period3_vote4_min10.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min10','sc_neg_mid':'sc_neg_mid_vote4_min10'})
# data_period3_vote4_min20 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间4_min20_vote4_每日投资金额汇总.xlsx',sheet_name='区间3',index_col=0)[['sc_pos_mid','sc_neg_mid']]
# data_period3_vote4_min20 = data_period3_vote4_min20.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min20','sc_neg_mid':'sc_neg_mid_vote4_min20'})
# data_period3_vote23 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间7_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间3',index_col=0)
# data_period3_vote23 = data_period3_vote23.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period3 = pd.concat([data_period3_vote4_min10,data_period3_vote4_min20,data_period3_vote23],axis=1)

# data_period3_vote23_min10_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间3_下限10',index_col=0)
# data_period3_vote23_min10_s1 = data_period3_vote23_min10_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min10','s1_pos_short_vote3':'s1_pos_short_vote3_min10','s1_pos_short_vote4':'s1_pos_short_vote4_min10',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min10','s1_neg_short_vote3':'s1_neg_short_vote3_min10','s1_neg_short_vote4':'s1_neg_short_vote4_min10'})
# data_period3_vote23_min20_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间3_下限20',index_col=0)
# data_period3_vote23_min20_s1 = data_period3_vote23_min20_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min20','s1_pos_short_vote3':'s1_pos_short_vote3_min20','s1_pos_short_vote4':'s1_pos_short_vote4_min20',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min20','s1_neg_short_vote3':'s1_neg_short_vote3_min20','s1_neg_short_vote4':'s1_neg_short_vote4_min20'})
# data_period3_vote23_min10_sc = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间6_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间3',index_col=0)[['sc_pos_mid_vote2','sc_pos_mid_vote3','sc_neg_mid_vote2','sc_neg_mid_vote3']]
# data_period3_vote23_min10_sc = data_period3_vote23_min10_sc.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period3 = pd.concat([data_period3_vote4_min10,data_period3_vote4_min20,data_period3_vote23_min10_s1,data_period3_vote23_min20_s1,data_period3_vote23_min10_sc],axis=1)
# 
# # 区间4
data_period4 = pd.read_excel('/data/user/013550/For_TSQ/neptune/fac_20250609_sc_mid/区间1_区间8_min10_vote234_单日模拟成交金额_sc.xlsx',sheet_name='区间4',index_col=0)
data_period4 = data_period4.rename(columns={'sc_pos_mid_vote4':'sc_pos_mid_vote4_min10','sc_neg_mid_vote4':'sc_neg_mid_vote4_min10',\
                                   'sc_pos_mid_vote3':'sc_pos_mid_vote3_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10',\
                                   'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_neg_mid_vote2':'sc_neg_mid_vote2_min10'})
# data_period4_vote4_min10 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间4_min10_vote4_每日投资金额汇总.xlsx',sheet_name='区间4',index_col=0)[['sc_pos_mid','sc_neg_mid']]
# data_period4_vote4_min10 = data_period4_vote4_min10.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min10','sc_neg_mid':'sc_neg_mid_vote4_min10'})
# data_period4_vote4_min20 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间4_min20_vote4_每日投资金额汇总.xlsx',sheet_name='区间4',index_col=0)[['sc_pos_mid','sc_neg_mid']]
# data_period4_vote4_min20 = data_period4_vote4_min20.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min20','sc_neg_mid':'sc_neg_mid_vote4_min20'})
# data_period4_vote23 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间7_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间4',index_col=0)
# data_period4_vote23 = data_period4_vote23.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period4 = pd.concat([data_period4_vote4_min10,data_period4_vote4_min20,data_period4_vote23],axis=1)

# data_period4_vote23_min10_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间4_下限10',index_col=0)
# data_period4_vote23_min10_s1 = data_period4_vote23_min10_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min10','s1_pos_short_vote3':'s1_pos_short_vote3_min10','s1_pos_short_vote4':'s1_pos_short_vote4_min10',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min10','s1_neg_short_vote3':'s1_neg_short_vote3_min10','s1_neg_short_vote4':'s1_neg_short_vote4_min10'})
# data_period4_vote23_min20_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间4_下限20',index_col=0)
# data_period4_vote23_min20_s1 = data_period4_vote23_min20_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min20','s1_pos_short_vote3':'s1_pos_short_vote3_min20','s1_pos_short_vote4':'s1_pos_short_vote4_min20',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min20','s1_neg_short_vote3':'s1_neg_short_vote3_min20','s1_neg_short_vote4':'s1_neg_short_vote4_min20'})
# data_period4_vote23_min10_sc = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间6_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间4',index_col=0)[['sc_pos_mid_vote2','sc_pos_mid_vote3','sc_neg_mid_vote2','sc_neg_mid_vote3']]
# data_period4_vote23_min10_sc = data_period4_vote23_min10_sc.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period4 = pd.concat([data_period4_vote4_min10,data_period4_vote4_min20,data_period4_vote23_min10_s1,data_period4_vote23_min20_s1,data_period4_vote23_min10_sc],axis=1)
# 
# # 区间5
data_period5 = pd.read_excel('/data/user/013550/For_TSQ/neptune/fac_20250609_sc_mid/区间1_区间8_min10_vote234_单日模拟成交金额_sc.xlsx',sheet_name='区间5',index_col=0)
data_period5 = data_period5.rename(columns={'sc_pos_mid_vote4':'sc_pos_mid_vote4_min10','sc_neg_mid_vote4':'sc_neg_mid_vote4_min10',\
                                   'sc_pos_mid_vote3':'sc_pos_mid_vote3_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10',\
                                   'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_neg_mid_vote2':'sc_neg_mid_vote2_min10'})
# data_period5_vote4_min10 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/20220701~20221231_vote4_单日模拟成交金额_sc.xlsx',sheet_name='下限10_区间5',index_col=0)
# data_period5_vote4_min10 = data_period5_vote4_min10.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min10','sc_neg_mid':'sc_neg_mid_vote4_min10'})
# data_period5_vote4_min20 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/20220701~20221231_vote4_单日模拟成交金额_sc.xlsx',sheet_name='下限20_区间5',index_col=0)
# data_period5_vote4_min20 = data_period5_vote4_min20.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min20','sc_neg_mid':'sc_neg_mid_vote4_min20'})
# data_period5_vote23 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间7_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间5',index_col=0)
# data_period5_vote23 = data_period5_vote23.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period5 = pd.concat([data_period5_vote4_min10,data_period5_vote4_min20,data_period5_vote23],axis=1)

# data_period5_vote23_min10_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间5_下限10',index_col=0)
# data_period5_vote23_min10_s1 = data_period5_vote23_min10_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min10','s1_pos_short_vote3':'s1_pos_short_vote3_min10','s1_pos_short_vote4':'s1_pos_short_vote4_min10',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min10','s1_neg_short_vote3':'s1_neg_short_vote3_min10','s1_neg_short_vote4':'s1_neg_short_vote4_min10'})
# data_period5_vote23_min20_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间5_下限20',index_col=0)
# data_period5_vote23_min20_s1 = data_period5_vote23_min20_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min20','s1_pos_short_vote3':'s1_pos_short_vote3_min20','s1_pos_short_vote4':'s1_pos_short_vote4_min20',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min20','s1_neg_short_vote3':'s1_neg_short_vote3_min20','s1_neg_short_vote4':'s1_neg_short_vote4_min20'})
# 
# data_period5_vote23_min10_sc = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间6_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间5',index_col=0)[['sc_pos_mid_vote2','sc_pos_mid_vote3','sc_neg_mid_vote2','sc_neg_mid_vote3']]
# data_period5_vote23_min10_sc = data_period5_vote23_min10_sc.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period5 = pd.concat([data_period5_vote4_min10_sc,data_period5_vote4_min20_sc,data_period5_vote23_min10_s1,data_period5_vote23_min20_s1,data_period5_vote23_min10_sc],axis=1)
# 
# # 区间6
data_period6 = pd.read_excel('/data/user/013550/For_TSQ/neptune/fac_20250609_sc_mid/区间1_区间8_min10_vote234_单日模拟成交金额_sc.xlsx',sheet_name='区间6',index_col=0)
data_period6 = data_period6.rename(columns={'sc_pos_mid_vote4':'sc_pos_mid_vote4_min10','sc_neg_mid_vote4':'sc_neg_mid_vote4_min10',\
                                   'sc_pos_mid_vote3':'sc_pos_mid_vote3_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10',\
                                   'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_neg_mid_vote2':'sc_neg_mid_vote2_min10'})
# data_period6_vote4_min10 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/20230101~20230630_vote4_单日模拟成交金额_sc总.xlsx',sheet_name='下限10_区间6',index_col=0)
# data_period6_vote4_min10 = data_period6_vote4_min10.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min10','sc_neg_mid':'sc_neg_mid_vote4_min10'})
# data_period6_vote4_min20 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/20230101~20230630_vote4_单日模拟成交金额_sc总.xlsx',sheet_name='下限20_区间6',index_col=0)
# data_period6_vote4_min20 = data_period6_vote4_min20.rename(columns={'sc_pos_mid':'sc_pos_mid_vote4_min20','sc_neg_mid':'sc_neg_mid_vote4_min20'})
# data_period6_vote23 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间7_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间6',index_col=0)
# data_period6_vote23 = data_period6_vote23.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period6 = pd.concat([data_period6_vote4_min10,data_period6_vote4_min20,data_period6_vote23],axis=1)

# data_period6_vote23_min10_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间6_下限10',index_col=0)
# data_period6_vote23_min10_s1 = data_period6_vote23_min10_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min10','s1_pos_short_vote3':'s1_pos_short_vote3_min10','s1_pos_short_vote4':'s1_pos_short_vote4_min10',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min10','s1_neg_short_vote3':'s1_neg_short_vote3_min10','s1_neg_short_vote4':'s1_neg_short_vote4_min10'})
# data_period6_vote23_min20_s1 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/单日模拟成交金额.xlsx',sheet_name='区间6_下限20',index_col=0)
# data_period6_vote23_min20_s1 = data_period6_vote23_min20_s1.rename(columns={'s1_pos_short_vote2':'s1_pos_short_vote2_min20','s1_pos_short_vote3':'s1_pos_short_vote3_min20','s1_pos_short_vote4':'s1_pos_short_vote4_min20',\
#                                                                             's1_neg_short_vote2':'s1_neg_short_vote2_min20','s1_neg_short_vote3':'s1_neg_short_vote3_min20','s1_neg_short_vote4':'s1_neg_short_vote4_min20'})
# data_period6_vote23_min10_sc = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间1_区间6_min10_vote23_单日模拟成交金额_sc.xlsx',sheet_name='区间6',index_col=0)[['sc_pos_mid_vote2','sc_pos_mid_vote3','sc_neg_mid_vote2','sc_neg_mid_vote3']]
# data_period6_vote23_min10_sc = data_period6_vote23_min10_sc.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10',\
#                                                                             'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10'})
# data_period6 = pd.concat([data_period6_vote4_min10_sc,data_period6_vote4_min20_sc,data_period6_vote23_min10_s1,data_period6_vote23_min20_s1,data_period6_vote23_min10_sc],axis=1)

# 区间7
data_period7 = pd.read_excel('/data/user/013550/For_TSQ/neptune/fac_20250609_sc_mid/区间1_区间8_min10_vote234_单日模拟成交金额_sc.xlsx',sheet_name='区间7',index_col=0)
data_period7 = data_period7.rename(columns={'sc_pos_mid_vote4':'sc_pos_mid_vote4_min10','sc_neg_mid_vote4':'sc_neg_mid_vote4_min10',\
                                   'sc_pos_mid_vote3':'sc_pos_mid_vote3_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10',\
                                   'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_neg_mid_vote2':'sc_neg_mid_vote2_min10'})
# data_period7_min10 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间7单日模拟成交金额.xlsx',sheet_name='区间7_下限10',index_col=0)
# data_period7_min10 = data_period7_min10.rename(columns={'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_pos_mid_vote3':'sc_pos_mid_vote3_min10','sc_pos_mid_vote4':'sc_pos_mid_vote4_min10',\
#                                                         'sc_neg_mid_vote2':'sc_neg_mid_vote2_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10','sc_neg_mid_vote4':'sc_neg_mid_vote4_min10'})
# data_period7_min20 = pd.read_excel('/dfs/user/003371/share_files/for_tsq/neptune/区间7单日模拟成交金额.xlsx',sheet_name='区间7_下限20',index_col=0)[['sc_pos_mid_vote4','sc_neg_mid_vote4']]
# data_period7_min20 = data_period7_min20.rename(columns={'sc_pos_mid_vote4':'sc_pos_mid_vote4_min20','sc_neg_mid_vote4':'sc_neg_mid_vote4_min20'})
# data_period7 = pd.concat([data_period7_min10,data_period7_min20],axis=1)
# 区间8
data_period8 = pd.read_excel('/data/user/013550/For_TSQ/neptune/fac_20250609_sc_mid/区间1_区间8_min10_vote234_单日模拟成交金额_sc.xlsx',sheet_name='区间8',index_col=0)
data_period8 = data_period8.rename(columns={'sc_pos_mid_vote4':'sc_pos_mid_vote4_min10','sc_neg_mid_vote4':'sc_neg_mid_vote4_min10',\
                                   'sc_pos_mid_vote3':'sc_pos_mid_vote3_min10','sc_neg_mid_vote3':'sc_neg_mid_vote3_min10',\
                                   'sc_pos_mid_vote2':'sc_pos_mid_vote2_min10','sc_neg_mid_vote2':'sc_neg_mid_vote2_min10'})


data_period1['时间区间'] = 1
data_period2['时间区间'] = 2
data_period3['时间区间'] = 3
data_period4['时间区间'] = 4
data_period5['时间区间'] = 5
data_period6['时间区间'] = 6
data_period7['时间区间'] = 7
data_period8['时间区间'] = 8


data_period_all = pd.concat([data_period1,data_period2,data_period3,data_period4,data_period5,data_period6,data_period7,data_period8])
data_period_all = data_period_all.rename_axis('dt')
data_period_all.index = pd.to_datetime(data_period_all.index.astype(str))

# 增加封板样本规模
udl_amt_df = pd.read_pickle('/dfs/user/023859/neptune/sc_udl_amt_20200701_20241231.pkl')
udl_amt_df = udl_amt_df.rename_axis('dt')
udl_amt_df.index = pd.to_datetime(udl_amt_df.index.astype(str))

for label in ['mid_vote4_min10','mid_vote3_min10','mid_vote2_min10']:
    data_period_all[f'sc_pos_{label}'] += udl_amt_df['sc_ul']
    data_period_all[f'sc_neg_{label}'] -= udl_amt_df['sc_dl']

index_pct_s1 = pd.read_pickle('/dfs/user/023859/share_file/for_wys/zz1000/20250612/index_label_s1_20170110_20241231.pkl').droplevel(1)
index_pct_sc = pd.read_pickle('/dfs/user/023859/share_file/for_wys/zz1000/20250612/index_label_sc_20170110_20241231.pkl').droplevel(1)

IM_pct = pd.read_pickle('/dfs/user/023859/neptune/label_df_IM_20220722_20241231.pkl')
IM_target_pct = pd.read_pickle('/dfs/user/023859/share_file/for_wys/zz1000/20250513/IM_label_20220722_20250331.pkl')
IM_pct = IM_pct.reindex(IM_target_pct.index).loc[:pd.Timestamp('20241231')]
IM_pct = IM_pct.droplevel(1)

# data_period_all['index_label_sc_short'] = index_pct_sc['label_pct_short_term']
# data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'index_label_sc_short'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_sc_short']
data_period_all['index_label_sc_mid'] = index_pct_sc['label_pct_mid_term']
data_period_all['index_label_sc_mid_Tc2b10'] = index_pct_sc['label_pct_mid_term_Tc2b10']
data_period_all['index_label_sc_mid_TNo2Tc'] = index_pct_sc['label_pct_mid_term_TNo2Tc']
data_period_all['index_label_sc_mid_TNv2TNo'] = index_pct_sc['label_pct_mid_term_TNv2TNo']

data_period_all['future_label_sc_mid'] = index_pct_sc['label_pct_mid_term']
data_period_all['future_label_sc_mid_Tc2b10'] = index_pct_sc['label_pct_mid_term_Tc2b10']
data_period_all['future_label_sc_mid_TNo2Tc'] = index_pct_sc['label_pct_mid_term_TNo2Tc']
data_period_all['future_label_sc_mid_TNv2TNo'] = index_pct_sc['label_pct_mid_term_TNv2TNo']

data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'future_label_sc_mid'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_sc_mid']
data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'future_label_sc_mid_Tc2b10'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_sc_mid_Tc2b10']
data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'future_label_sc_mid_TNo2Tc'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_sc_mid_TNo2Tc']
data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'future_label_sc_mid_TNv2TNo'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_sc_mid_TNv2TNo']

# data_period_all['index_label_sc_long'] = index_pct_sc['label_pct_long_term']
# data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'index_label_sc_long'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_sc_long']

# data_period_all['index_label_s1_short'] = index_pct_s1['label_pct_short_term']
# data_period_all['index_label_s1_short_Tc2b10'] = index_pct_s1['label_pct_short_term']
# data_period_all['index_label_s1_short_TNo2Tc'] = index_pct_s1['label_pct_short_term']
# data_period_all['index_label_s1_short_TNv2TNo'] = index_pct_s1['label_pct_short_term']
# 
# data_period_all['future_label_s1_short'] = index_pct_s1['label_pct_short_term']
# data_period_all['future_label_s1_short_Tc2b10'] = index_pct_s1['label_pct_short_term']
# data_period_all['future_label_s1_short_TNo2Tc'] = index_pct_s1['label_pct_short_term']
# data_period_all['future_label_s1_short_TNv2TNo'] = index_pct_s1['label_pct_short_term']
# 
# data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'future_label_s1_short'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_s1_short']
# data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'future_label_s1_short_Tc2b10'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_s1_short']
# data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'future_label_s1_short_TNo2Tc'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_s1_short']
# data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'future_label_s1_short_TNv2TNo'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_s1_short']
# data_period_all['index_label_s1_mid'] = index_pct_s1['label_pct_mid_term']
# data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'index_label_s1_mid'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_s1_mid']
# data_period_all['index_label_s1_long'] = index_pct_s1['label_pct_long_term']
# data_period_all.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'index_label_s1_long'] = IM_pct.loc[pd.Timestamp('20220722'):pd.Timestamp(str(end_date)),'label_s1_long']

# data_period_all[['index_label_s1_short_vote3_modified','index_label_sc_mid_vote3_modified']] = data_period_all[['index_label_s1_short','index_label_sc_mid']]
# data_period_all[['index_label_s1_short_vote2_modified','index_label_sc_mid_vote2_modified']] = data_period_all[['index_label_s1_short','index_label_sc_mid']]

for label in labels:
    data_period_all = calc_exposure(data_period_all,label) # 计算敞口
    data_period_all = calc_signal(data_period_all,label) # 计算信号
    data_period_all = calc_profit(data_period_all,label)

# data_period_all = compute_modified_profit(data_period_all)

# 计算累计收益
for label in labels:
    data_period_all[f'profit_index_cumsum_{label}'] = data_period_all[f'profit_index_{label}'].cumsum()
    data_period_all[f'profit_future_cumsum_{label}'] = data_period_all[f'profit_future_{label}'].cumsum()

outer_labels = labels
inner_periods = ['区间1','区间2','区间3','区间4','区间5','区间6','区间7','区间8','全部区间']
res_index = {}
res_future = {}

for outer in outer_labels:
    outer_ = outer[:-12]
    for inner in inner_periods:
        if inner == '全部区间':
            res_index[(f'{outer}_index',inner)] = sta_profit(data_period_all[f'index_label_{outer_}'],
                                                             data_period_all[f'index_label_{outer_}_Tc2b10'],
                                                             data_period_all[f'index_label_{outer_}_TNo2Tc'],
                                                             data_period_all[f'index_label_{outer_}_TNv2TNo'],
                                                             data_period_all[f'profit_index_{outer}_pos'],
                                                             data_period_all[f'profit_index_{outer}_neg'],
                                                             data_period_all[f'profit_index_{outer}'],
                                                             data_period_all[f'signal_{outer}'],
                                                             data_period_all[f'{outer}'])
            res_future[(f'{outer}_future',inner)] = sta_profit(data_period_all[f'future_label_{outer_}'],
                                                               data_period_all[f'future_label_{outer_}_Tc2b10'],
                                                               data_period_all[f'future_label_{outer_}_TNo2Tc'],
                                                               data_period_all[f'future_label_{outer_}_TNv2TNo'],
                                                               data_period_all[f'profit_future_{outer}_pos'],
                                                               data_period_all[f'profit_future_{outer}_neg'],
                                                               data_period_all[f'profit_future_{outer}'],
                                                               data_period_all[f'signal_{outer}'],
                                                               data_period_all[f'{outer}'])
        elif inner == '区间1':
            data_period_1 = data_period_all[data_period_all['时间区间']==1]
            res_index[(f'{outer}_index', inner)] = sta_profit(data_period_1[f'index_label_{outer_}'],
                                                              data_period_1[f'index_label_{outer_}_Tc2b10'],
                                                              data_period_1[f'index_label_{outer_}_TNo2Tc'],
                                                              data_period_1[f'index_label_{outer_}_TNv2TNo'], \
                                                              data_period_1[f'profit_index_{outer}_pos'],
                                                              data_period_1[f'profit_index_{outer}_neg'],
                                                              data_period_1[f'profit_index_{outer}'],
                                                              data_period_1[f'signal_{outer}'],
                                                              data_period_1[f'{outer}'])
            res_future[(f'{outer}_future', inner)] = sta_profit(data_period_1[f'future_label_{outer_}'],
                                                                data_period_1[f'future_label_{outer_}_Tc2b10'],
                                                                data_period_1[f'future_label_{outer_}_TNo2Tc'],
                                                                data_period_1[f'future_label_{outer_}_TNv2TNo'], \
                                                                data_period_1[f'profit_future_{outer}_pos'],
                                                                data_period_1[f'profit_future_{outer}_neg'],
                                                                data_period_1[f'profit_future_{outer}'],
                                                                data_period_1[f'signal_{outer}'],
                                                                data_period_1[f'{outer}'])
        elif inner == '区间2':
            data_period_2 = data_period_all[data_period_all['时间区间']==2]
            res_index[(f'{outer}_index', inner)] = sta_profit(data_period_2[f'index_label_{outer_}'],
                                                              data_period_2[f'index_label_{outer_}_Tc2b10'],
                                                              data_period_2[f'index_label_{outer_}_TNo2Tc'],
                                                              data_period_2[f'index_label_{outer_}_TNv2TNo'], \
                                                              data_period_2[f'profit_index_{outer}_pos'],
                                                              data_period_2[f'profit_index_{outer}_neg'],
                                                              data_period_2[f'profit_index_{outer}'],
                                                              data_period_2[f'signal_{outer}'],
                                                              data_period_2[f'{outer}'])
            res_future[(f'{outer}_future', inner)] = sta_profit(data_period_2[f'future_label_{outer_}'],
                                                                data_period_2[f'future_label_{outer_}_Tc2b10'],
                                                                data_period_2[f'future_label_{outer_}_TNo2Tc'],
                                                                data_period_2[f'future_label_{outer_}_TNv2TNo'], \
                                                                data_period_2[f'profit_future_{outer}_pos'],
                                                                data_period_2[f'profit_future_{outer}_neg'],
                                                                data_period_2[f'profit_future_{outer}'],
                                                                data_period_2[f'signal_{outer}'],
                                                                data_period_2[f'{outer}'])
        elif inner == '区间3':
            data_period_3 = data_period_all[data_period_all['时间区间'] == 3]
            res_index[(f'{outer}_index', inner)] = sta_profit(data_period_3[f'index_label_{outer_}'],
                                                              data_period_3[f'index_label_{outer_}_Tc2b10'],
                                                              data_period_3[f'index_label_{outer_}_TNo2Tc'],
                                                              data_period_3[f'index_label_{outer_}_TNv2TNo'], \
                                                              data_period_3[f'profit_index_{outer}_pos'],
                                                              data_period_3[f'profit_index_{outer}_neg'],
                                                              data_period_3[f'profit_index_{outer}'],
                                                              data_period_3[f'signal_{outer}'],
                                                              data_period_3[f'{outer}'])
            res_future[(f'{outer}_future', inner)] = sta_profit(data_period_3[f'future_label_{outer_}'],
                                                                data_period_3[f'future_label_{outer_}_Tc2b10'],
                                                                data_period_3[f'future_label_{outer_}_TNo2Tc'],
                                                                data_period_3[f'future_label_{outer_}_TNv2TNo'], \
                                                                data_period_3[f'profit_future_{outer}_pos'],
                                                                data_period_3[f'profit_future_{outer}_neg'],
                                                                data_period_3[f'profit_future_{outer}'],
                                                                data_period_3[f'signal_{outer}'],
                                                                data_period_3[f'{outer}'])
        elif inner == '区间4':
            data_period_4 = data_period_all[data_period_all['时间区间'] == 4]
            res_index[(f'{outer}_index', inner)] = sta_profit(data_period_4[f'index_label_{outer_}'],
                                                              data_period_4[f'index_label_{outer_}_Tc2b10'],
                                                              data_period_4[f'index_label_{outer_}_TNo2Tc'],
                                                              data_period_4[f'index_label_{outer_}_TNv2TNo'], \
                                                              data_period_4[f'profit_index_{outer}_pos'],
                                                              data_period_4[f'profit_index_{outer}_neg'],
                                                              data_period_4[f'profit_index_{outer}'],
                                                              data_period_4[f'signal_{outer}'],
                                                              data_period_4[f'{outer}'])
            res_future[(f'{outer}_future', inner)] = sta_profit(data_period_4[f'future_label_{outer_}'],
                                                                data_period_4[f'future_label_{outer_}_Tc2b10'],
                                                                data_period_4[f'future_label_{outer_}_TNo2Tc'],
                                                                data_period_4[f'future_label_{outer_}_TNv2TNo'], \
                                                                data_period_4[f'profit_future_{outer}_pos'],
                                                                data_period_4[f'profit_future_{outer}_neg'],
                                                                data_period_4[f'profit_future_{outer}'],
                                                                data_period_4[f'signal_{outer}'],
                                                                data_period_4[f'{outer}'])
        elif inner == '区间5':
            data_period_5 = data_period_all[data_period_all['时间区间'] == 5]
            res_index[(f'{outer}_index', inner)] = sta_profit(data_period_5[f'index_label_{outer_}'],
                                                              data_period_5[f'index_label_{outer_}_Tc2b10'],
                                                              data_period_5[f'index_label_{outer_}_TNo2Tc'],
                                                              data_period_5[f'index_label_{outer_}_TNv2TNo'], \
                                                              data_period_5[f'profit_index_{outer}_pos'],
                                                              data_period_5[f'profit_index_{outer}_neg'],
                                                              data_period_5[f'profit_index_{outer}'],
                                                              data_period_5[f'signal_{outer}'],
                                                              data_period_5[f'{outer}'])
            res_future[(f'{outer}_future', inner)] = sta_profit(data_period_5[f'future_label_{outer_}'],
                                                                data_period_5[f'future_label_{outer_}_Tc2b10'],
                                                                data_period_5[f'future_label_{outer_}_TNo2Tc'],
                                                                data_period_5[f'future_label_{outer_}_TNv2TNo'], \
                                                                data_period_5[f'profit_future_{outer}_pos'],
                                                                data_period_5[f'profit_future_{outer}_neg'],
                                                                data_period_5[f'profit_future_{outer}'],
                                                                data_period_5[f'signal_{outer}'],
                                                                data_period_5[f'{outer}'])
        elif inner == '区间6':
            data_period_6 = data_period_all[data_period_all['时间区间'] == 6]
            res_index[(f'{outer}_index', inner)] = sta_profit(data_period_6[f'index_label_{outer_}'],
                                                              data_period_6[f'index_label_{outer_}_Tc2b10'],
                                                              data_period_6[f'index_label_{outer_}_TNo2Tc'],
                                                              data_period_6[f'index_label_{outer_}_TNv2TNo'], \
                                                              data_period_6[f'profit_index_{outer}_pos'],
                                                              data_period_6[f'profit_index_{outer}_neg'],
                                                              data_period_6[f'profit_index_{outer}'],
                                                              data_period_6[f'signal_{outer}'],
                                                              data_period_6[f'{outer}'])
            res_future[(f'{outer}_future', inner)] = sta_profit(data_period_6[f'future_label_{outer_}'],
                                                                data_period_6[f'future_label_{outer_}_Tc2b10'],
                                                                data_period_6[f'future_label_{outer_}_TNo2Tc'],
                                                                data_period_6[f'future_label_{outer_}_TNv2TNo'], \
                                                                data_period_6[f'profit_future_{outer}_pos'],
                                                                data_period_6[f'profit_future_{outer}_neg'],
                                                                data_period_6[f'profit_future_{outer}'],
                                                                data_period_6[f'signal_{outer}'],
                                                                data_period_6[f'{outer}'])
        elif inner == '区间7':
            data_period_7 = data_period_all[data_period_all['时间区间'] == 7]
            res_index[(f'{outer}_index', inner)] = sta_profit(data_period_7[f'index_label_{outer_}'],
                                                              data_period_7[f'index_label_{outer_}_Tc2b10'],
                                                              data_period_7[f'index_label_{outer_}_TNo2Tc'],
                                                              data_period_7[f'index_label_{outer_}_TNv2TNo'], \
                                                              data_period_7[f'profit_index_{outer}_pos'],
                                                              data_period_7[f'profit_index_{outer}_neg'],
                                                              data_period_7[f'profit_index_{outer}'],
                                                              data_period_7[f'signal_{outer}'],
                                                              data_period_7[f'{outer}'])
            res_future[(f'{outer}_future', inner)] = sta_profit(data_period_7[f'future_label_{outer_}'],
                                                                data_period_7[f'future_label_{outer_}_Tc2b10'],
                                                                data_period_7[f'future_label_{outer_}_TNo2Tc'],
                                                                data_period_7[f'future_label_{outer_}_TNv2TNo'], \
                                                                data_period_7[f'profit_future_{outer}_pos'],
                                                                data_period_7[f'profit_future_{outer}_neg'],
                                                                data_period_7[f'profit_future_{outer}'],
                                                                data_period_7[f'signal_{outer}'],
                                                                data_period_7[f'{outer}'])
        elif inner == '区间8':
            data_period_8 = data_period_all[data_period_all['时间区间'] == 8]
            res_index[(f'{outer}_index', inner)] = sta_profit(data_period_8[f'index_label_{outer_}'],
                                                              data_period_8[f'index_label_{outer_}_Tc2b10'],
                                                              data_period_8[f'index_label_{outer_}_TNo2Tc'],
                                                              data_period_8[f'index_label_{outer_}_TNv2TNo'], \
                                                              data_period_8[f'profit_index_{outer}_pos'],
                                                              data_period_8[f'profit_index_{outer}_neg'],
                                                              data_period_8[f'profit_index_{outer}'],
                                                              data_period_8[f'signal_{outer}'],
                                                              data_period_8[f'{outer}'])
            res_future[(f'{outer}_future', inner)] = sta_profit(data_period_8[f'future_label_{outer_}'],
                                                                data_period_8[f'future_label_{outer_}_Tc2b10'],
                                                                data_period_8[f'future_label_{outer_}_TNo2Tc'],
                                                                data_period_8[f'future_label_{outer_}_TNv2TNo'], \
                                                                data_period_8[f'profit_future_{outer}_pos'],
                                                                data_period_8[f'profit_future_{outer}_neg'],
                                                                data_period_8[f'profit_future_{outer}'],
                                                                data_period_8[f'signal_{outer}'],
                                                                data_period_8[f'{outer}'])
        else:
            raise TypeError


res_df_index = pd.DataFrame(res_index)
res_df_index.columns = pd.MultiIndex.from_tuples(res_df_index.columns)
# res_df_index = res_df_index.rename_axis('future')

res_df_future = pd.DataFrame(res_future)
res_df_future.columns = pd.MultiIndex.from_tuples(res_df_future.columns)

# 绘制收益曲线
# img1 = create_plot(data_period_all[data_period_all['时间区间']==1],'区间1收益曲线')
# img2 = create_plot(data_period_all[data_period_all['时间区间']==2],'区间2收益曲线')
# img3 = create_plot(data_period_all[data_period_all['时间区间']==3],'区间3收益曲线')
# img4 = create_plot(data_period_all[data_period_all['时间区间']==4],'区间4收益曲线')
# img5 = create_plot(data_period_all[data_period_all['时间区间']==5],'区间5收益曲线')
# img6 = create_plot(data_period_all[data_period_all['时间区间']==6],'区间6收益曲线')
img8 = create_plot(data_period_all[data_period_all['时间区间']==8],'区间8收益曲线（指数标签）')
img_all = create_plot(data_period_all,'全区间收益曲线（指数标签）')

# img1_modified = create_plot_modified(data_period_all[data_period_all['时间区间']==1],'调整后区间1收益曲线')
# img2_modified = create_plot_modified(data_period_all[data_period_all['时间区间']==2],'调整后区间2收益曲线')
# img3_modified = create_plot_modified(data_period_all[data_period_all['时间区间']==3],'调整后区间3收益曲线')
# img4_modified = create_plot_modified(data_period_all[data_period_all['时间区间']==4],'调整后区间4收益曲线')
# img5_modified = create_plot_modified(data_period_all[data_period_all['时间区间']==5],'调整后区间5收益曲线')
# img6_modified = create_plot_modified(data_period_all[data_period_all['时间区间']==6],'调整后区间6收益曲线')
img8_modified = create_plot_modified(data_period_all[data_period_all['时间区间']==8],'区间8收益曲线（期货标签）')
img_all_modified = create_plot_modified(data_period_all,'全区间收益曲线（期货标签）')

# keep_columns = ['sc_mid_vote4_min10','sc_mid_vote4_min20','sc_mid_vote3_min10','sc_mid_vote2_min10','s1_short_vote4_min10','s1_short_vote4_min20',
#                 's1_short_vote3_min10','s1_short_vote3_min20','s1_short_vote2_min10','s1_short_vote2_min20',
#                 'index_label_s1_short','index_label_s1_short_Tc2b10','index_label_s1_short_TNo2Tc','index_label_s1_short_TNv2TNo',
#                 'index_label_sc_mid','index_label_sc_mid_Tc2b10','index_label_sc_mid_TNo2Tc','index_label_sc_mid_TNv2TNo',
#                 'profit_index_sc_mid_vote4_min10','profit_index_sc_mid_vote4_min20','profit_index_sc_mid_vote3_min10','profit_index_sc_mid_vote2_min10',
#                 'profit_index_s1_short_vote4_min10','profit_index_s1_short_vote4_min20','profit_index_s1_short_vote3_min10','profit_index_s1_short_vote3_min20',
#                 'profit_index_s1_short_vote2_min10','profit_index_s1_short_vote2_min20',
#                 'profit_future_sc_mid_vote4_min10','profit_future_sc_mid_vote4_min20','profit_future_sc_mid_vote3_min10','profit_future_sc_mid_vote2_min10',
#                 'profit_future_s1_short_vote4_min10','profit_future_s1_short_vote4_min20','profit_future_s1_short_vote3_min10','profit_future_s1_short_vote3_min20',
#                 'profit_future_s1_short_vote2_min10','profit_future_s1_short_vote2_min20',
#                 'profit_index_cumsum_sc_mid_vote4_min10','profit_index_cumsum_sc_mid_vote4_min20','profit_index_cumsum_sc_mid_vote3_min10','profit_index_cumsum_sc_mid_vote2_min10',
#                 'profit_index_cumsum_s1_short_vote4_min10','profit_index_cumsum_s1_short_vote4_min20','profit_index_cumsum_s1_short_vote3_min10','profit_index_cumsum_s1_short_vote3_min20',
#                 'profit_index_cumsum_s1_short_vote2_min10','profit_index_cumsum_s1_short_vote2_min20',
#                 'profit_future_cumsum_sc_mid_vote4_min10','profit_future_cumsum_sc_mid_vote4_min20','profit_future_cumsum_sc_mid_vote3_min10','profit_future_cumsum_sc_mid_vote2_min10',
#                 'profit_future_cumsum_s1_short_vote4_min10','profit_future_cumsum_s1_short_vote4_min20','profit_future_cumsum_s1_short_vote3_min10','profit_future_cumsum_s1_short_vote3_min20',
#                 'profit_future_cumsum_s1_short_vote2_min10','profit_future_cumsum_s1_short_vote2_min20',
#                 ]
keep_columns = ['sc_mid_vote4_min10','sc_mid_vote3_min10','sc_mid_vote2_min10','index_label_sc_mid','index_label_sc_mid_Tc2b10','index_label_sc_mid_TNo2Tc','index_label_sc_mid_TNv2TNo',\
                'future_label_sc_mid','future_label_sc_mid_Tc2b10','future_label_sc_mid_TNo2Tc','future_label_sc_mid_TNv2TNo',\
                'profit_index_sc_mid_vote4_min10','profit_index_sc_mid_vote3_min10','profit_index_sc_mid_vote2_min10',\
                'profit_future_sc_mid_vote4_min10','profit_future_sc_mid_vote3_min10','profit_future_sc_mid_vote2_min10',\
                'profit_index_cumsum_sc_mid_vote4_min10','profit_index_cumsum_sc_mid_vote3_min10','profit_index_cumsum_sc_mid_vote2_min10',\
                'profit_future_cumsum_sc_mid_vote4_min10','profit_future_cumsum_sc_mid_vote3_min10','profit_future_cumsum_sc_mid_vote2_min10']
#
with pd.ExcelWriter('/dfs/user/023859/share_file/for_wys/zz1000/20250612/20200701_20240630_min10_vote234_index_0.001_0.0015_future_0.0005_0.0005_Neptune指数择时收益分析.xlsx',engine='xlsxwriter') as writer:
    data_period_all[keep_columns].to_excel(writer, sheet_name='前八区间数据')
    res_df_index.to_excel(writer, sheet_name='收益统计')
    res_df_future.to_excel(writer, sheet_name='收益统计',startrow = 35, startcol = 0)
    workbook = writer.book
    worksheet = writer.sheets['收益统计']
    # worksheet.insert_image('A32','区间1收益曲线.png',{'image_data':img1})
    # worksheet.insert_image('G32','区间2收益曲线.png',{'image_data':img2})
    # worksheet.insert_image('M32','区间3收益曲线.png',{'image_data':img3})
    # worksheet.insert_image('S32','区间4收益曲线.png',{'image_data':img4})
    # worksheet.insert_image('A53','区间6收益曲线.png',{'image_data':img6})
    worksheet.insert_image('A72','区间8收益曲线.png',{'image_data':img8})
    worksheet.insert_image('G72','全区间收益曲线.png',{'image_data': img_all})
    # worksheet.insert_image('A56', '调整后区间1收益曲线.png', {'image_data': img1_modified})
    # worksheet.insert_image('G56', '调整后区间2收益曲线.png', {'image_data': img2_modified})
    # worksheet.insert_image('M56', '调整后区间3收益曲线.png', {'image_data': img3_modified})
    # worksheet.insert_image('S56', '调整后区间4收益曲线.png', {'image_data': img4_modified})
    # worksheet.insert_image('A74', '调整后区间6收益曲线.png', {'image_data': img6_modified})
    worksheet.insert_image('A96', '调整后区间8收益曲线.png', {'image_data': img8_modified})
    worksheet.insert_image('G96', '调整后全区间收益曲线.png', {'image_data': img_all_modified})
    writer.save()