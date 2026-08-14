# coding: utf-8
# Author：fengchi863
# Date ：2025/7/9 15:35

import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']


def plot_line(data, col1='最高股息率', col2='最低股息率'):
    fig, ax = plt.subplots(figsize=(40, 30), dpi=40)

    ax.plot(data['年度'].iloc[:-1], data[col1].iloc[:-1].values, c='tomato', label=col1, linewidth=8)
    ax.plot(data['年度'].iloc[-2:], data[col1].iloc[-2:].values, c='tomato', label=col1, linewidth=8, linestyle='--')
    ax.scatter(data['年度'].values, data[col1].values, color='r', linewidth=5)

    ax.plot(data['年度'].iloc[:-1], data[col2].iloc[:-1].values, c='firebrick', label=col2, linewidth=8)
    ax.plot(data['年度'].iloc[-2:], data[col2].iloc[-2:].values, c='firebrick', label=col2, linewidth=8, linestyle='--')
    ax.scatter(data['年度'].values, data[col2].values, color='r', linewidth=5)
    ax.set_ylabel('股息率', fontsize=40)

    # ax.legend(loc=2, borderaxespad=1.).set_zorder(2)
    # plt.title(f'股息率Band', fontsize=30)
    for xtick in ax.get_xticklabels():
        xtick.set_fontsize(30)
        # xtick.set_rotation(30)
    for ytick in ax.get_yticklabels():
        ytick.set_fontsize(30)

    # ax.grid(which='major', axis=0, linewidth=5)
    ax.grid()
    plt.xticks(data['年度'].values)

    fig.savefig(f'/data/user/015614/junkData/test.png', bbox_inches='tight', pad_inches=0.1)

def trans_table(df):
    df = df[['净利润', '分红总额', '分红率', 'high', 'low', '最低股息率', '最高股息率', '年度']]
    df = df.rename({'high': '最高价', 'low': '最低价'}, axis=1)
    df['净利润'] = df['净利润'].map(lambda x: round(x, 0))
    df['分红总额'] = df['分红总额'].map(lambda x: round(x, 0))
    df['最高价'] = df['最高价'].map(lambda x: '{:.2f}'.format(x))
    df['最低价'] = df['最低价'].map(lambda x: '{:.2f}'.format(x))
    df['分红率'] = df['分红率'].map(lambda x: '{:.1f}%'.format(x * 100))
    df['最低股息率'] = df['最低股息率'].map(lambda x: '{:.2f}%'.format(x * 100))
    df['最高股息率'] = df['最高股息率'].map(lambda x: '{:.2f}%'.format(x * 100))
    df = df.set_index('年度')
    df.to_excel(f'/data/user/015614/junkData/test.xlsx')

if __name__ == '__main__':
    # df = pd.read_excel('/data/user/015614/junkData/分红养老/格力电器_000651.SZ.xlsx', index_col=0)
    df = pd.read_excel('/data/user/015614/junkData/分红养老/中国神华_601088.SH.xlsx', index_col=0)
    df = df.query('年度 >= 2016')
    df = df.reset_index()
    plot_line(df)
    trans_table(df)