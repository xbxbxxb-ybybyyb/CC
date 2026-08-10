import pandas as pd
import numpy as np
import os
from copy import copy
import matplotlib.pyplot as plt
import itertools
import bisect

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak, SimpleDocTemplate, Image, Spacer

import warnings
warnings.filterwarnings('ignore')
import pickle
def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 

# plot parameters
TITLE_FONT_SIZE = 30
TICKS_FONT_SIZE = 25
LEGEND_FONT_SIZE = 20
PLOT_WIDTH = 7
PLOT_HEIGHT = 2
LINE_WIDTH = 3
MARKER_SIZE = 10
MAIN_COLOR = 'royalblue'
COLOR_L = 'indianred'
COLOR_S = 'seagreen'
COLOR_LIST = ['royalblue', 'dodgerblue', 'deepskyblue', 'lightskyblue']
COLOR_LIST2 = ['darkorange', 'darkorchid', 'darkred', 'red', 'green', 'royalblue', 'deepskyblue', 'lightskyblue']


# In[5]:


def arg_percentile(array, value):
    if np.isnan(value):
        result = np.nan
    else:
        sorted_array = np.sort(array)
        result = np.searchsorted(sorted_array, value) / len(array)
    return result


# In[6]:


def generate_first_page(canvas, document):
    canvas.saveState()
    canvas.restoreState()
    return None


def generate_later_pages(canvas, document):
    canvas.saveState()
    canvas.setFont(psfontname='STSong-Light', size=6)
    canvas.restoreState()
    return None


# In[7]:


def df2list(df, head):
    df_list = []
    df_col_list = df.columns.tolist()
    df_idx_list = df.index.tolist()
    one_row = [head] + df_col_list
    df_list.append(one_row)
    for idx in df_idx_list:
        one_row = [idx]
        for col in df_col_list:
            one_row.append(df.loc[idx, col])
        df_list.append(one_row)
    return df_list


# In[8]:


def generate_table(df, head=''):
    df_list = df2list(df, head)
    df_table = Table(df_list)
    df_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOX', (0, 0), (-1, -1), 0.4, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.2, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
    ]))
    return df_table


def generate_plot_bar(data, title):
    assert isinstance(data, pd.Series)
    plt.close()
    fig = plt.figure(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 6))
    plt.bar(data.index.tolist(), data.values, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    plt.title(title, fontsize=TITLE_FONT_SIZE)
    plt.xticks(fontsize=TICKS_FONT_SIZE, rotation=90)
    plt.yticks(fontsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * 2 * inch)

def generate_plot_with_colors_and_values(data, title, color_list, value_type=None):
    assert isinstance(data, pd.DataFrame)
    assert data.shape[1] == len(color_list)
    data.index = data.index.strftime('%Y-%m-%d')
    plt.close()
    fig = plt.figure(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    for col, color in zip(data.columns, color_list):
        plt.plot(data[col], label=col, color=color, linewidth=LINE_WIDTH, marker='o', markersize=MARKER_SIZE)
    for col in data.columns:
        for x, y in zip(data.index, data[col].values):
            if value_type == 'int':
                plt.text(x, y, f'{int(y):,}', va='bottom', ha='center', fontsize=TICKS_FONT_SIZE)
            elif value_type == 'float5':
                plt.text(x, y, f'{y:.5f}', va='bottom', ha='center', fontsize=TICKS_FONT_SIZE)
            else:
                plt.text(x, y, y, va='bottom', ha='center', fontsize=TICKS_FONT_SIZE)

    plt.title(title, fontsize=TITLE_FONT_SIZE)
    plt.xticks(fontsize=TICKS_FONT_SIZE)
    plt.yticks(fontsize=TICKS_FONT_SIZE)
    plt.legend(fontsize=LEGEND_FONT_SIZE)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_plot_1x2(data1, data2, title1, title2):
    assert isinstance(data1, pd.Series)
    assert isinstance(data2, pd.Series)
    plt.close()
    fig = plt.figure(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    fig.add_subplot(1, 2, 1)
    plt.plot(data1, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    plt.title(title1, fontsize=TITLE_FONT_SIZE)
    plt.xticks(fontsize=TICKS_FONT_SIZE, rotation=30)
    plt.yticks(fontsize=TICKS_FONT_SIZE)
    plt.grid()
    fig.add_subplot(1, 2, 2)
    plt.plot(data2, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    plt.title(title2, fontsize=TITLE_FONT_SIZE)
    plt.xticks(fontsize=TICKS_FONT_SIZE, rotation=30)
    plt.yticks(fontsize=TICKS_FONT_SIZE)
    plt.grid()
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_plot_with_colors_1x2_raw_old(data1, data2, title1, title2, color_list):
    assert isinstance(data1, pd.DataFrame)
    assert isinstance(data2, pd.DataFrame)
    assert data1.shape[1] == len(color_list)
    assert data2.shape[1] == len(color_list)
    plt.close()
    fig = plt.figure(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    fig.add_subplot(1, 2, 1)
    for col, color in zip(data1.columns, color_list):
        plt.plot(data1[col], label=col, color=color, linewidth=LINE_WIDTH)
    plt.title(title1, fontsize=TITLE_FONT_SIZE)
    plt.xticks(fontsize=TICKS_FONT_SIZE, rotation=30)
    plt.yticks(fontsize=TICKS_FONT_SIZE)
    plt.legend(fontsize=LEGEND_FONT_SIZE)
    plt.grid()
    fig.add_subplot(1, 2, 2)
    for col, color in zip(data2.columns, color_list):
        plt.plot(data2[col], label=col, color=color, linewidth=LINE_WIDTH)
    plt.title(title2, fontsize=TITLE_FONT_SIZE)
    plt.xticks(fontsize=TICKS_FONT_SIZE, rotation=30)
    plt.yticks(fontsize=TICKS_FONT_SIZE)
    plt.legend(fontsize=LEGEND_FONT_SIZE)
    plt.grid()
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)

def generate_plot_with_colors_1x2_raw(data1, data2, title1, title2, color_list):
    assert isinstance(data1, pd.DataFrame)
    assert isinstance(data2, pd.DataFrame)
    assert data1.shape[1] <= len(color_list)
    assert data2.shape[1] <= len(color_list)
    plt.close()
    fig = plt.figure(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))

    # 创建子图并保存每个子图的 ax 对象
    ax1 = fig.add_subplot(1, 2, 1)
    for col, color in zip(data1.columns, color_list):
        ax1.plot(data1[col], label=col, color=color, linewidth=LINE_WIDTH)
    ax1.set_title(title1, fontsize=TITLE_FONT_SIZE)
    ax1.tick_params(labelsize=TICKS_FONT_SIZE)
    ax1.legend(fontsize=LEGEND_FONT_SIZE)
    ax1.grid()
    ax1.yaxis.get_offset_text().set_fontsize(TICKS_FONT_SIZE)  # ✅ 设置第一个子图的 y 轴偏移量字体

    ax2 = fig.add_subplot(1, 2, 2)
    for col, color in zip(data2.columns, color_list):
        ax2.plot(data2[col], label=col, color=color, linewidth=LINE_WIDTH)
    ax2.set_title(title2, fontsize=TITLE_FONT_SIZE)
    ax2.tick_params(labelsize=TICKS_FONT_SIZE)
    ax2.legend(fontsize=LEGEND_FONT_SIZE)
    ax2.grid()
    ax2.yaxis.get_offset_text().set_fontsize(TICKS_FONT_SIZE)  # ✅ 设置第二个子图的 y 轴偏移量字体

    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)

def generate_plot_with_colors_1x2(data1, data2, title1, title2, color_list):
    assert isinstance(data1, pd.DataFrame)
    assert isinstance(data2, pd.DataFrame)
    assert data1.shape[1] == len(color_list)
    assert data2.shape[1] == len(color_list)
    data1.index = data1.index.strftime('%Y-%m-%d')
    data2.index = data2.index.strftime('%Y-%m-%d')
    plt.close()
    fig = plt.figure(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    fig.add_subplot(1, 2, 1)
    for col, color in zip(data1.columns, color_list):
        plt.plot(data1[col], label=col, color=color, linewidth=LINE_WIDTH)
    plt.title(title1, fontsize=TITLE_FONT_SIZE)
    plt.xticks(fontsize=TICKS_FONT_SIZE)
    plt.yticks(fontsize=TICKS_FONT_SIZE)
    plt.legend(fontsize=LEGEND_FONT_SIZE)
    plt.grid()
    fig.add_subplot(1, 2, 2)
    for col, color in zip(data2.columns, color_list):
        plt.plot(data2[col], label=col, color=color, linewidth=LINE_WIDTH)
    plt.title(title2, fontsize=TITLE_FONT_SIZE)
    plt.xticks(fontsize=TICKS_FONT_SIZE)
    plt.yticks(fontsize=TICKS_FONT_SIZE)
    plt.legend(fontsize=LEGEND_FONT_SIZE)
    plt.grid()
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def get_median_line(x):
    assert isinstance(x, pd.Series) or isinstance(x, pd.DataFrame)
    x_mean = np.nanmedian(x.values, axis=0, keepdims=True).repeat(len(x), axis=0)
    if isinstance(x, pd.Series):
        x_mean = pd.Series(x_mean, index=x.index, name=x.name)
    else:
        x_mean = pd.DataFrame(x_mean, index=x.index, columns=x.columns)
    return x_mean

def generate_plot_with_median_line(data, title, height=PLOT_HEIGHT):
    assert isinstance(data, pd.Series)
    plt.close()
    fig = plt.figure(figsize=(PLOT_WIDTH * 3, height * 3))
    plt.plot(data, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    plt.plot(get_median_line(data), color=MAIN_COLOR, linewidth=LINE_WIDTH * 0.8, linestyle='--')
    plt.title(title, fontsize=TITLE_FONT_SIZE)
    plt.xticks(fontsize=TICKS_FONT_SIZE)
    plt.yticks(fontsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=height * inch)


# font
os.system('cp -r /data/user/015626/data/share/LOCAL_DATA/font/* /opt/anaconda3/lib/python3.8/site-packages/reportlab/fonts/')
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))  # Chinese Simplifie
pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))  # Song Ti


# # PDF

ticker_type_list = ['IC', 'IF', 'IH']

styles = getSampleStyleSheet()
title_style_1 = copy(styles['Heading1'])
title_style_1.alignment = 1
title_style_2 = copy(styles['Heading2'])
title_style_2.alignment = 1
title_style_3 = copy(styles['Heading3'])
title_style_3.alignment = 1
head_style = copy(styles['Heading3'])
head_style.alignment = 0

def transfer_dataframe(results):
    _ = pd.concat([results.iloc[:10].reset_index(),results.iloc[10:20].reset_index(),results.iloc[20:].reset_index()],axis = 1)
    _new = _.iloc[1:]
    _new.columns = _.iloc[0].tolist()
    _new = _new.set_index('累积净值').replace(np.nan, '')
    return _new

def generate_plot_with_colors(data, title, color_list, legend_loc='upper left', ylabel = ''):
    assert isinstance(data, pd.DataFrame)
    assert data.shape[1] == len(color_list)
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    for col, color in zip(data.columns, color_list):
        ax.plot(data[col], label=col, color=color, linewidth=LINE_WIDTH)
    ax.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(labelsize=TICKS_FONT_SIZE)
    ax.legend(fontsize=TICKS_FONT_SIZE, loc=legend_loc, framealpha=1.0)
    ax.yaxis.get_offset_text().set_fontsize(TICKS_FONT_SIZE)
    plt.ylabel(ylabel, fontsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    plt.grid()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)

def generate_plot(data, title):
    assert isinstance(data, pd.Series)
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    ax.plot(data, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    ax.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(labelsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    plt.grid()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)

# def generate_plot_with_colors_1x2_raw(data1, data2, title1, title2, color_list):
#     assert isinstance(data1, pd.DataFrame)
#     assert isinstance(data2, pd.DataFrame)
#     assert data1.shape[1] <= len(color_list)
#     assert data2.shape[1] <= len(color_list)
#     plt.close()
#     fig = plt.figure(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
#     fig.add_subplot(1, 2, 1)
#     for col, color in zip(data1.columns, color_list):
#         plt.plot(data1[col], label=col, color=color, linewidth=LINE_WIDTH)
#     plt.title(title1, fontsize=TITLE_FONT_SIZE)
#     plt.xticks(fontsize=TICKS_FONT_SIZE, rotation=30)
#     plt.yticks(fontsize=TICKS_FONT_SIZE)
#     plt.legend(fontsize=LEGEND_FONT_SIZE)
#     plt.grid()
#     fig.add_subplot(1, 2, 2)
#     for col, color in zip(data2.columns, color_list):
#         plt.plot(data2[col], label=col, color=color, linewidth=LINE_WIDTH)
#     plt.title(title2, fontsize=TITLE_FONT_SIZE)
#     plt.xticks(fontsize=TICKS_FONT_SIZE, rotation=30)
#     plt.yticks(fontsize=TICKS_FONT_SIZE)
#     plt.legend(fontsize=LEGEND_FONT_SIZE)
#     plt.grid()
#     plt.tight_layout()
#     img = BytesIO()
#     fig.savefig(img, format='jpg')
#     img.seek(0)
#     plt.close()
#     return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)

def generate_plot_xy(total_daily_profit, total_daily_open_value, title, legend_loc='upper left'):
    fig = plt.figure(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    ax1 = fig.add_subplot(1, 1, 1)
    xlist = [x.strftime('%Y%m%d') for x in total_daily_profit.index.tolist()]
    ylist = total_daily_profit.cumsum().tolist()
    ax1.plot(np.arange(len(xlist)), ylist, color='dodgerblue', linewidth=LINE_WIDTH)
    ax1.set_xticks(np.arange(0,len(xlist),step = max(len(xlist)//8, 1)))
    ax1.set_xticklabels([xlist[i] for i in np.arange(0,len(xlist),step = max(len(xlist)//8, 1))])
    ax1.tick_params(labelsize=TICKS_FONT_SIZE)
    ax1.yaxis.get_offset_text().set_fontsize(TICKS_FONT_SIZE)
    plt.ylabel('Profit', fontsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    plt.grid()
    ax_right = ax1.twinx()
    ax_right.stackplot(np.arange(total_daily_open_value.shape[0]), total_daily_open_value.values, labels=['open_value'] ,alpha=0.3)
    ax_right.tick_params(labelsize=TICKS_FONT_SIZE)
    ax_right.yaxis.get_offset_text().set_fontsize(TICKS_FONT_SIZE)
    plt.xlabel('Segment', fontsize=TICKS_FONT_SIZE)
    plt.ylabel('open value', fontsize=TICKS_FONT_SIZE)
    plt.tight_layout()

    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    plt.close()
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)

def merge_evaluate(total_trade, total_daily_return, long_ret, short_ret, total_daily_profit, total_daily_open_value, trade_counts):
    trade = total_trade.sort_values(by = ['open_time'])
    
    # ===新建一个dataframe保存回测指标
    results = pd.DataFrame()
    
    # ===计算累积净值
    results.loc[0, '累计净值'] = round(total_daily_return.sum() + 1, 3)
    results.loc[0, '累计收益率'] = format(total_daily_return.sum(), '.4%')
    
    # 计算夏普比率
    sharpedailyreturn = total_daily_profit.to_frame(name = 'change')
    sharpedailyreturn.index.name = 'date'
    sharpedailyreturn = sharpedailyreturn.reset_index()
    
    tradedays = len(sharpedailyreturn)
    sharpe_ratio = round(sharpedailyreturn['change'].mean() / sharpedailyreturn['change'].std() * np.sqrt(252), 3)
    results.loc[0, '夏普比率'] = sharpe_ratio
    
    # ===计算年化收益
    annual_return = (total_daily_return.sum()) * (
            '365 days 00:00:00' / (sharpedailyreturn['date'].iloc[-1] - sharpedailyreturn['date'].iloc[0]))
    
    # results.loc[0, '年化收益率'] = format(round(annual_return, 3), '.2%')
    _annual_return = (total_daily_profit.sum()) * (
            '365 days 00:00:00' / (sharpedailyreturn['date'].iloc[-1] - sharpedailyreturn['date'].iloc[0]))
    results.loc[0, '年化收益'] = "{:.2e}".format(_annual_return)

    results.loc[0, '累计收益'] = "{:.2e}".format(total_daily_profit.sum())
    results.loc[0, '平均日占资'] = "{:.2e}".format(total_daily_open_value.mean())
    results.loc[0, '最大日占资'] = "{:.2e}".format(total_daily_open_value.max())
    
    sharpedailyreturn['equity_curve'] = sharpedailyreturn['change'].cumsum()
    sharpedailyreturn = sharpedailyreturn.reset_index()
    # ===计算最大回撤
    # 计算当日之前的资金曲线的最高点
    sharpedailyreturn['max2here'] = sharpedailyreturn['equity_curve'].expanding().max()
    # 计算到历史最高值到当日的跌幅，drowdwon
    sharpedailyreturn['dd2here'] = sharpedailyreturn['equity_curve'] - sharpedailyreturn['max2here']
    # 计算最大回撤，以及最大回撤结束时间
    end_date, max_draw_down = tuple(sharpedailyreturn.sort_values(by=['dd2here']).iloc[0][['date', 'dd2here']])
    # 计算最大回撤开始时间
    start_date = sharpedailyreturn[sharpedailyreturn['date'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0][
        'date']
    # 将无关的变量删除
    sharpedailyreturn.drop(['max2here', 'dd2here'], axis=1, inplace=True)
    sharpedailyreturn = sharpedailyreturn.set_index('date')
    results.loc[0, '最大回撤'] = "{:.2e}".format(max_draw_down)#format(max_draw_down, '.2%')
    results.loc[0, '最大回撤开始时间'] = str(start_date)[:10]
    results.loc[0, '最大回撤结束时间'] = str(end_date)[:10]
    
    
    # ===年化收益/回撤比
    results.loc[0, '年化收益/回撤比'] = round(abs(annual_return / max_draw_down), 2)
    
    # ===统计每笔交易
    results.loc[0, '总交易笔数'] = len(trade)  # 交易笔数
    results.loc[0, '平均每天交易笔数'] = round(len(trade) / tradedays, 2)  # 盈利笔数
    results.loc[0, '亏损笔数'] = len(trade.loc[trade['change'] <= 0])  # 亏损笔数
    results.loc[0, '盈利笔数'] = len(trade.loc[trade['change'] > 0])  # 盈利笔数
    results.loc[0, '胜率'] = format(results.loc[0, '盈利笔数'] / len(trade), '.2%')  # 胜率
    
    longtrade = trade[trade['pos'] == 1]
    shorttrade = trade[trade['pos'] == -1]
    results.loc[0, '做多笔数'] = len(longtrade) 
    if len(longtrade) > 0: 
        results.loc[0, '做多胜率'] = format(len(longtrade[longtrade.change > 0]) / len(longtrade), '.2%')  # 胜率
    results.loc[0, '做空笔数'] = len(shorttrade)  
    if len(shorttrade) > 0:
        results.loc[0, '做空胜率'] = format(len(shorttrade[shorttrade.change > 0]) / len(shorttrade), '.2%')  # 胜率
    
    
    results.loc[0, '每笔交易平均盈亏'] = format(trade['change'].mean(), '.2%')  # 每笔交易平均盈亏
    results.loc[0, '盈亏收益比'] = round(trade.loc[trade['change'] > 0]['change'].mean() / \
                                    trade.loc[trade['change'] < 0][
                                        'change'].mean() * (-1), 2)  # 盈亏比

    results.loc[0, '单笔平均开仓金额'] = "{:.1e}".format(total_trade['open_money'].mean())
    results.loc[0, '单笔最大开仓金额'] = "{:.1e}".format(total_trade['open_money'].max())
    
    results.loc[0, '单笔最大盈利'] = format(trade['change'].max(), '.2%')  # 单笔最大盈利
    results.loc[0, '单笔最大亏损'] = format(trade['change'].min(), '.2%')  # 单笔最大亏损
    
    # ===统计持仓时间
    trade['持仓时间'] = trade['holding_time']
    max_minutes = trade['持仓时间'].max()
    results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) if max_minutes == max_minutes else np.nan
    
    min_minutes = trade['持仓时间'].min()
    results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) if min_minutes == min_minutes else np.nan
    
    mean_minutes = trade['持仓时间'].mean()
    results.loc[0, '平均持仓周期'] = str(round(mean_minutes, 1)) if mean_minutes == mean_minutes else np.nan
    
    # ===连续盈利亏算
    results.loc[0, '最大连续盈利笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
    results.loc[0, '最大连续亏损笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数

    
    if len(longtrade) > 0:
        results.loc[0, '做多收益'] = "{:.1e}".format(long_ret)#format(long_ret, '.4%')
        results.loc[0, '做多盈亏比'] = round(longtrade.loc[longtrade['change'] > 0]['change'].mean() / longtrade.loc[longtrade['change'] < 0]['change'].mean() * (-1), 2)  
    else:
        results.loc[0, '做多收益'] = np.nan
        results.loc[0, '做多盈亏比'] = np.nan
    if len(shorttrade) > 0:
        results.loc[0, '做空收益'] = "{:.1e}".format(short_ret)#format(short_ret, '.4%')
        results.loc[0, '做空盈亏比'] = round(shorttrade.loc[shorttrade['change'] > 0]['change'].mean() / shorttrade.loc[shorttrade['change'] < 0]['change'].mean() * (-1), 2)  
    else:
        results.loc[0, '做空收益'] = np.nan
        results.loc[0, '做空盈亏比'] = np.nan
    if trade_counts is not None:
        results.loc[0, '平均日持仓数量'] = round(trade_counts.mean(), 1)
        results.loc[0, '最大日持仓数量'] = round(trade_counts.max(), 1)
    else:
        results.loc[0, '平均日持仓数量'] = np.nan
        results.loc[0, '最大日持仓数量'] = np.nan
    results = results.T
    results.columns = ['num']
    return results

def get_result_perticker(daily_df_combine2, total_trade_combine2):
    ticker_list = sorted(daily_df_combine2.index.get_level_values(1).unique().tolist())

    long_list = []
    short_list = []
    results_list = []
    for ticker in ticker_list:
        ticker_daily_df = daily_df_combine2.xs(ticker, level = 1)
        ticker_daily_df.loc[(ticker_daily_df['pos'] == 0) & (ticker_daily_df['dailyret']!=0), 'pos'] = np.nan
        ticker_daily_df['pos'] = ticker_daily_df['pos'].fillna(method = 'ffill')
        assert ticker_daily_df[ticker_daily_df['pos'] == 0]['dailyret'].sum() == 0
        
        long_ticker_daily_df = ticker_daily_df[ticker_daily_df['pos'].isin([1])].reindex(ticker_daily_df.index)
        short_ticker_daily_df = ticker_daily_df[ticker_daily_df['pos'].isin([-1])].reindex(ticker_daily_df.index)
        long_ticker_daily_df[['pos', 'dailyret']] = long_ticker_daily_df[['pos', 'dailyret']].fillna(0)
        short_ticker_daily_df[['pos', 'dailyret']] = short_ticker_daily_df[['pos', 'dailyret']].fillna(0)
        
        long_ticker_daily_df['Ticker'] = ticker
        long_ticker_daily_df = long_ticker_daily_df.set_index('Ticker', append = True)
        short_ticker_daily_df['Ticker'] = ticker
        short_ticker_daily_df = short_ticker_daily_df.set_index('Ticker', append = True)

        long_list.append(long_ticker_daily_df)
        short_list.append(short_ticker_daily_df)

        if len(total_trade_combine2[total_trade_combine2['Ticker'] == ticker]) == 0 or ticker_daily_df['dailyret'].sum() == 0:
            _result_ticker = pd.DataFrame(columns = [ticker])
        else:
            _result_ticker = merge_evaluate(total_trade_combine2[total_trade_combine2['Ticker'] == ticker], ticker_daily_df['dailyret'], long_ticker_daily_df['dailypnl'].sum(), short_ticker_daily_df['dailypnl'].sum(), ticker_daily_df['dailypnl'], ticker_daily_df['open_value'], None)
            _result_ticker.columns = [ticker]
        results_list.append(_result_ticker)

    long_daily_df = pd.concat(long_list).sort_index()
    short_daily_df = pd.concat(short_list).sort_index()
    return results_list, long_daily_df, short_daily_df

def get_result_perjys(daily_df2, total_trade2, long_daily_df2, short_daily_df2, jys_list2, rjys_list2):
    tdr_list = []
    ld_dict = {}
    sd_dict = {}
    for jys in jys_list2:
        total_trade_jys = total_trade2[total_trade2['Ticker'].str.endswith(jys)]
        long_daily_df_jys = long_daily_df2[long_daily_df2.index.get_level_values(1).str.endswith(jys)]
        short_daily_df_jys = short_daily_df2[short_daily_df2.index.get_level_values(1).str.endswith(jys)]
        daily_df_jys = daily_df2[daily_df2.index.get_level_values(1).str.endswith(jys)]
        total_daily_return_jys = daily_df_jys['dailyret'].unstack().mean(axis = 1)
        total_daily_profit_jys = daily_df_jys['dailypnl'].unstack().sum(axis = 1)
        total_daily_open_value_jys = daily_df_jys['open_value'].unstack().sum(axis = 1)
        if total_daily_return_jys.sum() == 0:
            _result_ticker = pd.DataFrame(columns = [jys])
            continue
        else:
            results_jys = merge_evaluate(total_trade_jys, total_daily_return_jys, long_daily_df_jys['dailypnl'].unstack().sum(axis = 1).sum(), short_daily_df_jys['dailypnl'].unstack().sum(axis = 1).sum(), total_daily_profit_jys, total_daily_open_value_jys, daily_df_jys['dailyret'].unstack().replace(0, np.nan).count(axis = 1))
            results_jys.columns = [jys]
        rjys_list2.append(results_jys)

        tdr_list.append(total_daily_return_jys.to_frame(name = jys))
        ld_dict[jys] = long_daily_df_jys
        sd_dict[jys] = short_daily_df_jys
    rjys = pd.concat(rjys_list2, axis = 1)
    tdrjys = pd.concat(tdr_list, axis = 1)
    return rjys, tdrjys, ld_dict, sd_dict

def final_generate_pdf(trade_df, daily_df, trade_df_basis, daily_df_basis,_sdate, _sdate2, _edate, output_path, has_DCE = True, has_CFE = True, need_perticker_pdf = True):
    # trade_df = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/trade_df_fix.h5')
    # daily_df = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/trend_strategy/data/daily_df_fix.h5')

    # trade_df_basis = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/basis_strategy/data/trade_df_fix.h5')
    # daily_df_basis = pd.read_hdf('/data/group/800466/warehouse/prod/tradingstats/Spiral/basis_strategy/data/daily_df_fix.h5')

    # _sdate, _sdate2, _edate = 20200101, 20250101, 20250818
    # output_path = '/data/user/015626/data/share/LOCAL_DATA/COMMODITY/test2.pdf'
    # has_DCE = True
    # need_perticker_pdf = True


    if not has_DCE:
        trade_df = trade_df.reset_index()
        trade_df = trade_df[~trade_df['Ticker'].str.endswith('DCE')].set_index(['Ticker', 'intime'])
        daily_df = daily_df.reset_index()
        daily_df = daily_df[~daily_df['Ticker'].str.endswith('DCE')].set_index(['dt', 'Ticker'])

        trade_df_basis = trade_df_basis.reset_index()
        trade_df_basis = trade_df_basis[~trade_df_basis['Ticker'].str.endswith('DCE')].set_index(['Ticker', 'intime'])
        daily_df_basis = daily_df_basis.reset_index()
        daily_df_basis = daily_df_basis[~daily_df_basis['Ticker'].str.endswith('DCE')].set_index(['dt', 'Ticker'])

    if not has_CFE:
        trade_df = trade_df.reset_index()
        trade_df = trade_df[~trade_df['Ticker'].str.endswith('CFE')].set_index(['Ticker', 'intime'])
        daily_df = daily_df.reset_index()
        daily_df = daily_df[~daily_df['Ticker'].str.endswith('CFE')].set_index(['dt', 'Ticker'])

        trade_df_basis = trade_df_basis.reset_index()
        trade_df_basis = trade_df_basis[~trade_df_basis['Ticker'].str.endswith('CFE')].set_index(['Ticker', 'intime'])
        daily_df_basis = daily_df_basis.reset_index()
        daily_df_basis = daily_df_basis[~daily_df_basis['Ticker'].str.endswith('CFE')].set_index(['dt', 'Ticker'])

    trade_df = trade_df.swaplevel().sort_index().loc[pd.to_datetime(str(_sdate)):pd.to_datetime(str(_edate))].swaplevel().sort_index()
    daily_df = daily_df.loc[pd.to_datetime(str(_sdate)):pd.to_datetime(str(_edate))]
    trade_df_basis = trade_df_basis.swaplevel().sort_index().loc[pd.to_datetime(str(_sdate)):pd.to_datetime(str(_edate))].swaplevel().sort_index()
    daily_df_basis = daily_df_basis.loc[pd.to_datetime(str(_sdate)):pd.to_datetime(str(_edate))]

    info = pd.read_csv('/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/INFO/WIND_CFuturesContPro.csv')
    # delete simulation and IB codes
    info.loc[:,'EXCHANGE'] = [i.split('.')[1] for i in info['S_INFO_WINDCODE']]
    info.loc[:,'sim'] = [len(i.split('-')) for i in info['S_INFO_CODE']]
    info.loc[:,'sim2'] = [len(i.split('_')) for i in info['S_INFO_CODE']]
    info_select = info[(info['EXCHANGE']!='IB') & (info['sim'] < 2)& (info['sim2'] < 2)]                    
    info_select.loc[:,'Ticker'] = info_select['S_INFO_CODE'] + '.' + info_select['EXCHANGE']
    info_select.loc[:,'multiplier'] = info_select['S_INFO_PUNIT'].where(np.isnan(info_select['S_INFO_CEMULTIPLIER']),other = info_select['S_INFO_CEMULTIPLIER'])
    info_select['Ticker'] = [i.split('.')[0] + '.ZCE' if i.split('.')[1] == 'CZC' else i for i in info_select['Ticker']]
    multip = info_select.groupby('Ticker')[['multiplier']].last()
    bllist = ['IFM.CFE','SCTAS.INE']
    multiplier = multip.loc[~multip.index.isin(bllist)].reset_index()

    daily_df = pd.merge(daily_df.reset_index(), multiplier, on = 'Ticker').set_index(['dt', 'Ticker']).sort_index()
    daily_df['open_value'] = daily_df['inpriceorg'] * daily_df['multiplier'] * daily_df['shares'] 
    total_daily_return = daily_df['dailyret'].unstack().mean(axis = 1)#.cumsum().plot()
    total_daily_profit = daily_df['dailypnl'].unstack().sum(axis = 1)#.cumsum().plot()
    total_daily_open_value = daily_df['open_value'].unstack().sum(axis = 1)#.cumsum().plot()
    total_trade = trade_df.reset_index().rename(columns = {'intime':'open_time', 'perret':'change', 'hds':'holding_time'})

    daily_df_basis = pd.merge(daily_df_basis.reset_index(), multiplier, on = 'Ticker').set_index(['dt', 'Ticker']).sort_index()
    daily_df_basis['open_value'] = daily_df_basis['inpriceorg'] * daily_df_basis['multiplier'] * daily_df_basis['shares'] 
    total_daily_return_basis = daily_df_basis['dailyret'].unstack().mean(axis = 1)#.cumsum().plot()
    total_daily_profit_basis = daily_df_basis['dailypnl'].unstack().sum(axis = 1)#.cumsum().plot()
    total_daily_open_value_basis = daily_df_basis['open_value'].unstack().sum(axis = 1)#.cumsum().plot()
    total_trade_basis = trade_df_basis.reset_index().rename(columns = {'intime':'open_time', 'perret':'change', 'hds':'holding_time'})

    daily_df_combine = pd.concat([daily_df, daily_df_basis])
    daily_df_combine = daily_df_combine.groupby(['dt', 'Ticker']).agg({'pos':'sum', 'dailypnl':'sum', 'dailyret':'mean', 'open_value':'sum'}).sort_index()
    daily_df_combine.loc[daily_df_combine['pos'] > 0, 'pos'] = 1
    daily_df_combine.loc[daily_df_combine['pos'] < 0, 'pos'] = -1
    total_daily_return_combine = daily_df_combine['dailyret'].unstack().mean(axis = 1)#.cumsum().plot()
    total_daily_profit_combine = daily_df_combine['dailypnl'].unstack().sum(axis = 1)#.cumsum().plot()
    total_daily_open_value_combine = daily_df_combine['open_value'].unstack().sum(axis = 1)#.cumsum().plot()
    total_trade_combine = pd.concat([total_trade, total_trade_basis]).sort_values(by = ['Ticker', 'open_time'])

    # 获取每个ticker
    results_list, long_daily_df, short_daily_df = get_result_perticker(daily_df.copy(), total_trade.copy())
    results_list_basis, long_daily_df_basis, short_daily_df_basis = get_result_perticker(daily_df_basis.copy(), total_trade_basis.copy())
    results_list_combine, long_daily_df_combine, short_daily_df_combine = get_result_perticker(daily_df_combine.copy(), total_trade_combine.copy())

    results = merge_evaluate(total_trade, total_daily_return, long_daily_df['dailypnl'].unstack().sum(axis = 1).sum(), short_daily_df['dailypnl'].unstack().sum(axis = 1).sum(), total_daily_profit, total_daily_open_value, daily_df['dailyret'].unstack().replace(0, np.nan).count(axis = 1))
    results_basis = merge_evaluate(total_trade_basis, total_daily_return_basis, long_daily_df_basis['dailypnl'].unstack().sum(axis = 1).sum(), short_daily_df_basis['dailypnl'].unstack().sum(axis = 1).sum(), total_daily_profit_basis, total_daily_open_value_basis, daily_df_basis['dailyret'].unstack().replace(0, np.nan).count(axis = 1))
    results_combine = merge_evaluate(total_trade_combine, total_daily_return_combine, long_daily_df_combine['dailypnl'].unstack().sum(axis = 1).sum(), short_daily_df_combine['dailypnl'].unstack().sum(axis = 1).sum(), total_daily_profit_combine, total_daily_open_value_combine, daily_df_combine['dailyret'].unstack().replace(0, np.nan).count(axis = 1))

    # 获取每个jys
    results.columns = ['Trend']
    results_basis.columns = ['Basis']
    results_combine.columns = ['Total']
    rjys_list = [results_combine, results, results_basis]

    
    jys_list = ['SHF', 'ZCE', 'INE', 'GFE', 'CFE', 'DCE']
    if not has_DCE:
        jys_list.remove('DCE')
    if not has_CFE:
        jys_list.remove('CFE')

    rjys_combine, tdrjys_combine, ld_dict_combine, sd_dict_combine = get_result_perjys(daily_df_combine, total_trade_combine, long_daily_df_combine, short_daily_df_combine, jys_list, rjys_list)
    _rjys_combine = rjys_combine.loc[['累计收益', '年化收益', '最大回撤', '夏普比率', '平均日占资', '最大日占资', '平均日持仓数量', '最大日持仓数量', '胜率', '盈亏收益比', '平均持仓周期','做多收益', '做空收益']]

    # 阶段2
    _sdate2_dt = pd.to_datetime(str(_sdate2))
    results2 = merge_evaluate(total_trade[total_trade['open_time'] >= _sdate2_dt], total_daily_return.loc[_sdate2_dt:], long_daily_df.loc[_sdate2_dt:]['dailypnl'].unstack().sum(axis = 1).sum(), short_daily_df.loc[_sdate2_dt:]['dailypnl'].unstack().sum(axis = 1).sum(), total_daily_profit.loc[_sdate2_dt:], total_daily_open_value.loc[_sdate2_dt:], daily_df.loc[_sdate2_dt:]['dailyret'].unstack().replace(0, np.nan).count(axis = 1))
    results_basis2 = merge_evaluate(total_trade_basis[total_trade_basis['open_time'] >= _sdate2_dt], total_daily_return_basis.loc[_sdate2_dt:], long_daily_df_basis.loc[_sdate2_dt:]['dailypnl'].unstack().sum(axis = 1).sum(), short_daily_df_basis.loc[_sdate2_dt:]['dailypnl'].unstack().sum(axis = 1).sum(), total_daily_profit_basis.loc[_sdate2_dt:], total_daily_open_value_basis.loc[_sdate2_dt:], daily_df_basis.loc[_sdate2_dt:]['dailyret'].unstack().replace(0, np.nan).count(axis = 1))
    results_combine2 = merge_evaluate(total_trade_combine[total_trade_combine['open_time'] >= _sdate2_dt], total_daily_return_combine.loc[_sdate2_dt:], long_daily_df_combine.loc[_sdate2_dt:]['dailypnl'].unstack().sum(axis = 1).sum(), short_daily_df_combine.loc[_sdate2_dt:]['dailypnl'].unstack().sum(axis = 1).sum(), total_daily_profit_combine.loc[_sdate2_dt:], total_daily_open_value_combine.loc[_sdate2_dt:], daily_df_combine.loc[_sdate2_dt:]['dailyret'].unstack().replace(0, np.nan).count(axis = 1))

    results2.columns = ['Trend']
    results_basis2.columns = ['Basis']
    results_combine2.columns = ['Total']
    rjys_list2 = [results_combine2, results2, results_basis2]

    rjys_combine2, tdrjys_combine2, ld_dict_combine2, sd_dict_combine2 = get_result_perjys(daily_df_combine.loc[_sdate2_dt:], total_trade_combine[total_trade_combine['open_time'] >= _sdate2_dt], long_daily_df_combine.loc[_sdate2_dt:], short_daily_df_combine.loc[_sdate2_dt:], jys_list, rjys_list2)
    _rjys_combine2 = rjys_combine2.loc[['累计收益', '年化收益', '最大回撤', '夏普比率', '平均日占资', '最大日占资', '平均日持仓数量', '最大日持仓数量', '胜率', '盈亏收益比', '平均持仓周期','做多收益', '做空收益']]


    profit_combine = pd.concat([total_daily_profit_combine, long_daily_df_combine['dailypnl'].unstack().sum(axis = 1), short_daily_df_combine['dailypnl'].unstack().sum(axis = 1)], axis = 1)
    profit_combine.columns = ['Total', 'Long', 'Short']
    profit_combine2 = profit_combine.loc[pd.to_datetime(str(_sdate2)):]
    total_daily_open_value_combine2 = total_daily_open_value_combine.loc[pd.to_datetime(str(_sdate2)):]

    profit_merge = pd.concat([total_daily_profit, total_daily_profit_basis], axis = 1)
    profit_merge.columns = ['Trend', 'Basis']

    profit_merge_allsigs = pd.concat([total_daily_profit_combine, total_daily_profit, total_daily_profit_basis], axis = 1)
    profit_merge_allsigs.columns = ['Total', 'Trend', 'Basis']
    profit_merge_allsigs2 = profit_merge_allsigs.loc[pd.to_datetime(str(_sdate2)):]

    ls_merge_allsigs = pd.concat([long_daily_df_combine['dailypnl'].unstack().sum(axis = 1), short_daily_df_combine['dailypnl'].unstack().sum(axis = 1),long_daily_df['dailypnl'].unstack().sum(axis = 1), short_daily_df['dailypnl'].unstack().sum(axis = 1),long_daily_df_basis['dailypnl'].unstack().sum(axis = 1), short_daily_df_basis['dailypnl'].unstack().sum(axis = 1)], axis = 1)
    ls_merge_allsigs.columns = ['Total_Long', 'Total_Short', 'Trend_Long', 'Trend_Short', 'Basis_Long', 'Basis_Short']
    ls_merge_allsigs2 = ls_merge_allsigs.loc[pd.to_datetime(str(_sdate2)):]

    elements = []
    elements.append(Paragraph(f'Commodity Daily CTA Report', title_style_1))
    elements.append(Paragraph(f'{_sdate2} - {_edate}', title_style_3))
    table = generate_table(_rjys_combine2)
    elements.append(table)
    elements.append(Paragraph(f'{_sdate} - {_edate}', title_style_3))
    table = generate_table(_rjys_combine)
    elements.append(table)

    elements.append(PageBreak())

    elements.append(Paragraph(f'Profit {_sdate2} - {_edate}', title_style_2))

    pic2 = generate_plot_with_colors_1x2_raw(profit_merge_allsigs2.cumsum(), ls_merge_allsigs2.cumsum(), '', '', COLOR_LIST2[:6])
    elements.append(pic2)

    # pic = generate_plot_with_colors(profit_combine2.cumsum(), '', COLOR_LIST2[:3])
    # elements.append(pic)
    elements.append(Paragraph('Profit Total', title_style_2))

    # elements.append(Paragraph(f'{_sdate} - {_edate}', title_style_3))
    pic = generate_plot_with_colors(profit_combine.cumsum(), '', COLOR_LIST2[:3], ylabel='  ')
    elements.append(pic)

    elements.append(Paragraph('Profit Per Signal', title_style_2))
    pic = generate_plot_with_colors(profit_merge.cumsum(), '', COLOR_LIST2[:2], ylabel='  ')
    elements.append(pic)

    trend_ls = pd.concat([long_daily_df['dailypnl'].unstack().sum(axis = 1), short_daily_df['dailypnl'].unstack().sum(axis = 1)], axis = 1)
    trend_ls.columns = ['Long', 'Short']
    basis_ls = pd.concat([long_daily_df_basis['dailypnl'].unstack().sum(axis = 1), short_daily_df_basis['dailypnl'].unstack().sum(axis = 1)], axis = 1)
    basis_ls.columns = ['Long', 'Short']
    pic2 = generate_plot_with_colors_1x2_raw(trend_ls.cumsum(), basis_ls.cumsum(), 'Trend', 'Basis', COLOR_LIST2[:2])
    elements.append(pic2)

    elements.append(Paragraph('Daily Trade Counts', title_style_2))
    trade_counts = daily_df['dailyret'].unstack().replace(0, np.nan).count(axis = 1)
    trade_counts_basis = daily_df_basis['dailyret'].unstack().replace(0, np.nan).count(axis = 1)
    trade_counts_combine = daily_df_combine['dailyret'].unstack().replace(0, np.nan).count(axis = 1)
    tc = pd.concat([trade_counts_combine, trade_counts, trade_counts_basis], axis = 1)
    tc.columns = ['Total', 'Trend', 'Basis']
    pic = generate_plot_with_colors(tc, '', COLOR_LIST2[:3])
    elements.append(pic)

    elements.append(Paragraph('Exchange Curve', title_style_2))
    pic = generate_plot_with_colors(tdrjys_combine.cumsum(), '', COLOR_LIST2[:tdrjys_combine.shape[1]])
    elements.append(pic)

    jys_ls_dict = {}
    ls_index = pd.concat([ld_dict_combine['SHF']['dailypnl'].unstack().sum(axis = 1), sd_dict_combine['SHF']['dailypnl'].unstack().sum(axis = 1)], axis = 1).index
    for jys in jys_list:
        if not jys in ld_dict_combine.keys():
            jys_ls_dict[jys] = pd.DataFrame(0, index = ls_index, columns = ['long', 'short'])
            continue
        ls = pd.concat([ld_dict_combine[jys]['dailypnl'].unstack().sum(axis = 1), sd_dict_combine[jys]['dailypnl'].unstack().sum(axis = 1)], axis = 1).fillna(0).cumsum()
        ls.columns = ['long', 'short']
        jys_ls_dict[jys] = ls
    if not has_DCE:
        jys_ls_dict['DCE'] = pd.DataFrame(0, index = ls_index, columns = ['long', 'short'])
    if not has_CFE:
        jys_ls_dict['CFE'] = pd.DataFrame(0, index = ls_index, columns = ['long', 'short'])

    elements.append(PageBreak())

    elements.append(Paragraph(f'Exchange Long Short Curve', title_style_2))   
    pic2 = generate_plot_with_colors_1x2_raw(jys_ls_dict['SHF'], jys_ls_dict['ZCE'], 'SHF', 'ZCE', COLOR_LIST2[:2])
    elements.append(pic2)
    try:
        pic2 = generate_plot_with_colors_1x2_raw(jys_ls_dict['GFE'], jys_ls_dict['INE'], 'GFE', 'INE', COLOR_LIST2[:2])
        elements.append(pic2)
    except:
        pass
    try:
        pic2 = generate_plot_with_colors_1x2_raw(jys_ls_dict['CFE'], jys_ls_dict['DCE'], 'CFE', 'DCE', COLOR_LIST2[:2])
        elements.append(pic2)
    except:
        pass

    if need_perticker_pdf:
        elements.append(PageBreak())
        results_tickers = pd.concat(results_list, axis = 1)
        shar = results_tickers.loc['夏普比率'].sort_values(ascending = False)
        no_trade_tickers = shar[shar.isna()].index.tolist()
        results_tickers = results_tickers[shar.dropna().index]
        _rt = results_tickers.loc[['夏普比率', '年化收益', '最大回撤','胜率','每笔交易平均盈亏', '盈亏收益比', '平均持仓周期','做多收益', '做空收益', '单笔平均开仓金额', '单笔最大开仓金额']]
        _rt = _rt.T.sort_index()
        _rt.columns = ['sharpe','annret','mdd','winrt','ret_pt','w/l','hold','lret', 'sret', 'amt_mean', 'amt_max']

        results_tickers_basis = pd.concat(results_list_basis, axis = 1)
        shar_basis = results_tickers_basis.loc['夏普比率'].sort_values(ascending = False)
        no_trade_tickers_basis = shar_basis[shar_basis.isna()].index.tolist()
        results_tickers_basis = results_tickers_basis[shar_basis.dropna().index]
        _rt_basis = results_tickers_basis.loc[['夏普比率', '年化收益', '最大回撤','胜率','每笔交易平均盈亏', '盈亏收益比', '平均持仓周期','做多收益', '做空收益', '单笔平均开仓金额', '单笔最大开仓金额']]
        _rt_basis = _rt_basis.T.sort_index()
        _rt_basis.columns = ['sharpe','annret','mdd','winrt','ret_pt','w/l','hold','lret', 'sret', 'amt_mean', 'amt_max']

        results_tickers_combine = pd.concat(results_list_combine, axis = 1)
        shar_combine = results_tickers_combine.loc['夏普比率'].sort_values(ascending = False)
        no_trade_tickers_combine = shar_combine[shar_combine.isna()].index.tolist()
        results_tickers_combine = results_tickers_combine[shar_combine.dropna().index]
        _rt_combine = results_tickers_combine.loc[['夏普比率', '年化收益', '最大回撤','胜率','每笔交易平均盈亏', '盈亏收益比', '平均持仓周期','做多收益', '做空收益', '单笔平均开仓金额', '单笔最大开仓金额']]
        _rt_combine = _rt_combine.T.sort_index()
        _rt_combine.columns = ['sharpe','annret','mdd','winrt','ret_pt','w/l','hold','lret', 'sret', 'amt_mean', 'amt_max']

        ls_df = pd.concat([long_daily_df['dailypnl'], short_daily_df['dailypnl']], axis = 1)
        ls_df.columns = ['long', 'short']
        ls_df_basis = pd.concat([long_daily_df_basis['dailypnl'], short_daily_df_basis['dailypnl']], axis = 1)
        ls_df_basis.columns = ['long', 'short']
        ls_df_combine = pd.concat([long_daily_df_combine['dailypnl'], short_daily_df_combine['dailypnl']], axis = 1)
        ls_df_combine.columns = ['long', 'short']

        elements.append(Paragraph('All Ticker Results', title_style_2))
        elements.append(Paragraph(f'Statistics {_sdate} - {_edate}', title_style_2))
        table = generate_table(pd.concat([_rt_combine[['sharpe','annret','mdd']],_rt[['sharpe','annret','mdd']].add_prefix('T_'),_rt_basis[['sharpe','annret','mdd']].add_prefix('B_')], axis = 1))
        elements.append(table)

        elements.append(Paragraph('', head_style))

        i = 0
        for ticker in _rt.index:
            if i % 3 == 0:
                elements.append(PageBreak())
            elements.append(Paragraph(ticker, head_style))

            temp_left = pd.concat([daily_df_combine['dailypnl'].xs(ticker, level = 1), daily_df['dailypnl'].xs(ticker, level = 1), daily_df_basis['dailypnl'].xs(ticker, level = 1)], axis = 1)
            temp_left.columns = ['Total', 'Trend', 'Basis']
            temp_right = pd.concat([ls_df_combine.xs(ticker, level = 1).add_prefix('Total_'), ls_df.xs(ticker, level = 1).add_prefix('Trend_'), ls_df_basis.xs(ticker, level = 1).add_prefix('Basis_')], axis = 1)

            pic2 = generate_plot_with_colors_1x2_raw(temp_left.fillna(0).cumsum(), temp_right.fillna(0).cumsum(), '', '', COLOR_LIST2[:6])
            elements.append(pic2)
            i += 1

    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.8 * inch, bottomMargin=0.8 * inch)
    doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)

def calculate_quantile(df, s):
    result = {}
    for col, val in s.items():
        if col not in df.columns:
            raise ValueError(f"Column {col} not found in DataFrame")
        col_data = df[col].dropna()
        if len(col_data) == 0:
            raise ValueError(f"Column {col} has no non-NaN values")
        sorted_col = np.sort(col_data.values)
        pos = bisect.bisect_right(sorted_col, val)
        quantile = pos / len(sorted_col)
        result[col] = quantile
    return pd.Series(result)
       
def generate_basis_std_pdf(basis_ratio, std_df, _sdate, _sdate2, _edate, output_path):
    basis_ratio = basis_ratio.loc[pd.to_datetime(str(_sdate)):pd.to_datetime(str(_edate))]
    std_df = std_df.loc[pd.to_datetime(str(_sdate)):pd.to_datetime(str(_edate))]

    bsa = pd.concat([basis_ratio, std_df], axis = 1).sort_index()
    bsa2 = bsa.loc[pd.to_datetime(str(_sdate2)):pd.to_datetime(str(_edate))]

    bsa_daily = bsa.groupby('dt').mean()
    bsa_year = bsa_daily.groupby(bsa_daily.index.year).mean()
    bsa2_daily = bsa2.groupby('dt').mean()
    bsa2_mean = bsa2_daily.mean()

    market_quantile = pd.concat([bsa2_mean, calculate_quantile(bsa_daily, bsa2_mean), calculate_quantile(bsa_daily.iloc[-120:], bsa2_mean)], axis = 1)
    market_quantile.columns =['近期均值', '2010年以来分位数', '近120日分位数']

    market_quantile = market_quantile.join(bsa_year.iloc[-5:].sort_index(ascending = False).T.add_suffix('均值'))

    elements = []
    elements.append(Paragraph(f'Commodity Daily Basis And Std Report', title_style_1))

    elements.append(Paragraph(f'Market Info', title_style_2))
    elements.append(generate_table(round(market_quantile, 5)))
    elements.append(Spacer(1, 8))  # 1 表示宽度（自动填充），12 表示高度（单位：点）
    pic2 = generate_plot_with_colors_1x2_raw(bsa_daily[['basis_ratio']].fillna(method = 'ffill'), bsa_daily[['std_10d']].fillna(method = 'ffill'), '', '', COLOR_LIST2[:2])
    elements.append(pic2)

    elements.append(Paragraph(f'Ticker Info', title_style_2))
    ticker_list = sorted(list(std_df.dropna().index.get_level_values(1).unique()))
    i = 0
    for ticker in ticker_list:
        # if i % 3 == 0 and i > 1:
        #     elements.append(PageBreak())
        try:
            elements.append(Paragraph(ticker, head_style))
            bsa_ticker = bsa.xs(ticker, level = 1)
            bsa_ticker_year = bsa_ticker.groupby(bsa_ticker.index.year).mean()
            bsa2_ticker = bsa_ticker.loc[pd.to_datetime(str(_sdate2)):pd.to_datetime(str(_edate))]
            bsa2_ticker_mean = bsa2_ticker.mean()
            
            market_quantile = pd.concat([bsa2_ticker_mean, calculate_quantile(bsa_ticker, bsa2_ticker_mean), calculate_quantile(bsa_ticker.iloc[-120:], bsa2_ticker_mean)], axis = 1)
            market_quantile.columns =['近期均值', '2010年以来分位数', '近120日分位数']
            market_quantile = market_quantile.join(bsa_ticker_year.iloc[-5:].sort_index(ascending = False).T.add_suffix('均值'))
            elements.append(generate_table(round(market_quantile, 5)))
            elements.append(Spacer(1, 8))  # 1 表示宽度（自动填充），12 表示高度（单位：点）

            pic2 = generate_plot_with_colors_1x2_raw(basis_ratio.xs(ticker, level = 1).fillna(method = 'ffill'), std_df.xs(ticker, level = 1).fillna(method = 'ffill'), '', '', COLOR_LIST2[:2])
            elements.append(pic2)
            i += 1
        except Exception as e:
            print(ticker, e)

    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.8 * inch, bottomMargin=0.8 * inch)
    doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)