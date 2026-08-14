# coding: utf-8
# Author：fengchi863
# Date ：2023/9/21 10:53

import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']

def plot_bar(data, file_name):
    fig, ax1 = plt.subplots(figsize=(36, 20), dpi=80)
    label1 = '活跃概念数量'
    ax1.bar(range(0, len(data)), data.values, label=label1)
    ax1.set_ylabel(label1, fontsize=20)
    ax1.legend(loc=2, borderaxespad=1.).set_zorder(2)
    plt.title(f'{label1}相关走势图', fontsize='large')
    for xtick in ax1.get_xticklabels():
        xtick.set_rotation(75)
        xtick.set_fontsize(20)
    for ytick in ax1.get_yticklabels():
        ytick.set_fontsize(20)
    # 设置横坐标等间隔，不然太密集
    plt.xticks(range(0, len(data), 30), data.index.astype(str)[range(0, len(data), 30)].tolist())
    fig.savefig(f'/data/user/015614/{file_name}.png', bbox_inches='tight', pad_inches=0.1)

active_concept = pd.read_pickle('/data/user/015614/TEST/active_concept_test/active_concept.pkl')
daily_active_concept_num = active_concept.sum(axis=1)
active_concept_rolling10 = active_concept.rolling(10).sum() > 1
daily_active_concept_rolling10_num = active_concept_rolling10.sum(axis=1)
plot_bar(daily_active_concept_num, '每日概念数量')
daily_active_concept_num.describe()
plot_bar(daily_active_concept_rolling10_num, '日间筛选后每日概念数量')
daily_active_concept_rolling10_num.describe()