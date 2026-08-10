import sys
sys.path.insert(4, '/dfs/user/015626/JupyterNotebooks/utils/')

import pandas as pd
import numpy as np
import datetime
from multifactor.IO import IO
from tqdm import tqdm
import os
from copy import copy
import matplotlib.pyplot as plt
import itertools
import multifactor.utility.dt as udt
import warnings
from multiprocessing import Pool

# from ts_backtest_minute_com import *

from io import BytesIO
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak, SimpleDocTemplate, Image
from xquant.xqutils.xqfile import FTPFile
from multifactor.utility import dt as udt

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
COLOR_LIST2 = ['darkorange', 'darkorchid', 'royalblue', 'deepskyblue', 'lightskyblue']


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


def generate_plot_with_colors_1x2_raw(data1, data2, title1, title2, color_list):
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
head_style = copy(styles['Heading3'])
head_style.alignment = 0

def transfer_dataframe(results):
    _ = pd.concat([results.iloc[:10].reset_index(),results.iloc[10:20].reset_index(),results.iloc[20:].reset_index()],axis = 1)
    _new = _.iloc[1:]
    _new.columns = _.iloc[0].tolist()
    _new = _new.set_index('累积净值').replace(np.nan, '')
    return _new

def generate_plot_with_colors(data, title, color_list, legend_loc='upper left'):
    assert isinstance(data, pd.DataFrame)
    assert data.shape[1] == len(color_list)
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    for col, color in zip(data.columns, color_list):
        ax.plot(data[col], label=col, color=color, linewidth=LINE_WIDTH)
    ax.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(labelsize=TICKS_FONT_SIZE)
    ax.legend(fontsize=TICKS_FONT_SIZE, loc=legend_loc, framealpha=1.0)
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

def generate_plot_with_colors_1x2_raw(data1, data2, title1, title2, color_list):
    assert isinstance(data1, pd.DataFrame)
    assert isinstance(data2, pd.DataFrame)
    assert data1.shape[1] <= len(color_list)
    assert data2.shape[1] <= len(color_list)
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


def merge_evaluate(total_trade, total_daily_return, long_ret, short_ret, total_daily_profit, total_daily_open_value):
    trade = total_trade.sort_values(by = ['open_time'])
    
    # ===新建一个dataframe保存回测指标
    results = pd.DataFrame()
    
    # ===计算累积净值
    results.loc[0, '累积净值'] = round(total_daily_return.sum() + 1, 3)
    
    # 计算夏普比率
    sharpedailyreturn = total_daily_return.to_frame(name = 'change')
    sharpedailyreturn.index.name = 'date'
    sharpedailyreturn = sharpedailyreturn.reset_index()
    
    tradedays = len(sharpedailyreturn)
    sharpe_ratio = round(sharpedailyreturn['change'].mean() / sharpedailyreturn['change'].std() * np.sqrt(252), 3)
    results.loc[0, '夏普比率'] = sharpe_ratio
    
    # ===计算年化收益
    annual_return = (total_daily_return.sum()) * (
            '365 days 00:00:00' / (sharpedailyreturn['date'].iloc[-1] - sharpedailyreturn['date'].iloc[0]))
    
    results.loc[0, '年化收益率'] = format(round(annual_return, 3), '.2%')
    _annual_return = (total_daily_profit.sum()) * (
            '365 days 00:00:00' / (sharpedailyreturn['date'].iloc[-1] - sharpedailyreturn['date'].iloc[0]))
    results.loc[0, '年化收益'] = "{:.3e}".format(_annual_return)

    results.loc[0, '累计盈利'] = "{:.3e}".format(total_daily_profit.sum())
    results.loc[0, '平均日占资'] = "{:.3e}".format(total_daily_open_value.mean())
    results.loc[0, '最大日占资'] = "{:.3e}".format(total_daily_open_value.max())
    
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
    results.loc[0, '最大回撤'] = format(max_draw_down, '.2%')
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
    
    
    results.loc[0, '每笔交易平均盈亏'] = format(trade['change'].mean(), '.4%')  # 每笔交易平均盈亏
    results.loc[0, '盈亏收益比'] = round(trade.loc[trade['change'] > 0]['change'].mean() / \
                                    trade.loc[trade['change'] < 0][
                                        'change'].mean() * (-1), 2)  # 盈亏比
    
    results.loc[0, '单笔最大盈利'] = format(trade['change'].max(), '.2%')  # 单笔最大盈利
    results.loc[0, '单笔最大亏损'] = format(trade['change'].min(), '.2%')  # 单笔最大亏损
    
    # ===统计持仓时间
    trade['持仓时间'] = trade['holding_time']
    max_minutes = trade['持仓时间'].max()
    results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) #+ ' 分钟'  # 单笔最长持有时间
    
    min_minutes = trade['持仓时间'].min()
    results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) #+ ' 分钟'  # 单笔最短持有时间
    
    mean_minutes = trade['持仓时间'].mean()
    results.loc[0, '平均持仓周期'] = str(round(mean_minutes, 1))# + ' 分钟'  # 平均持仓周期
    
    # ===连续盈利亏算
    results.loc[0, '最大连续盈利笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
    results.loc[0, '最大连续亏损笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数
    
    if len(longtrade) > 0:
        results.loc[0, '做多收益'] = format(long_ret, '.4%')
        results.loc[0, '做多盈亏比'] = round(longtrade.loc[longtrade['change'] > 0]['change'].mean() / longtrade.loc[longtrade['change'] < 0]['change'].mean() * (-1), 2)  
    else:
        results.loc[0, '做多收益'] = np.nan
        results.loc[0, '做多盈亏比'] = np.nan
    if len(shorttrade) > 0:
        results.loc[0, '做空收益'] = format(short_ret, '.4%')
        results.loc[0, '做空盈亏比'] = round(shorttrade.loc[shorttrade['change'] > 0]['change'].mean() / shorttrade.loc[shorttrade['change'] < 0]['change'].mean() * (-1), 2)  
    else:
        results.loc[0, '做空收益'] = np.nan
        results.loc[0, '做空盈亏比'] = np.nan
    results = results.T
    results.columns = ['num']
    return results

def final_generate_pdf(trade_df, daily_df, _sdate, _edate, output_path):
    # trade_df = pd.read_hdf('/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/trade_df.h5')
    # trade_df.swaplevel().sort_index().loc[pd.to_datetime('20190101'):pd.to_datetime('20221231')].swaplevel().sort_index()
    # daily_df = pd.read_hdf('/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/daily_df.h5').loc[pd.to_datetime('20190101'):pd.to_datetime('20230101')]
    
    trade_df = trade_df.swaplevel().sort_index().loc[pd.to_datetime(str(_sdate)):pd.to_datetime(str(_edate))].swaplevel().sort_index()
    daily_df = daily_df.loc[pd.to_datetime(str(_sdate)):pd.to_datetime(str(_edate))]
    
    multiplier = pd.read_csv('/dfs/group/800466/warehouse/test/CHINA_COMMODITIES/INFO/multiplier.csv')
    daily_df = pd.merge(daily_df.reset_index(), multiplier, on = 'Ticker').set_index(['dt', 'Ticker']).sort_index()
    daily_df['open_value'] = daily_df['inpriceorg'] * daily_df['multiplier'] * daily_df['shares'] 
    
    total_daily_return = daily_df['dailyret'].unstack().mean(axis = 1)#.cumsum().plot()
    total_daily_profit = daily_df['dailypnl'].unstack().sum(axis = 1)#.cumsum().plot()
    total_daily_open_value = daily_df['open_value'].unstack().sum(axis = 1)#.cumsum().plot()
    total_trade = trade_df.reset_index().rename(columns = {'intime':'open_time', 'perret':'change', 'hds':'holding_time'})
    
    # daily_return = total_daily_return.to_frame(name = 'daily_ret')
    # daily_return['daily_equty_curve'] = daily_return['daily_ret'].cumsum()
    
    ticker_list = sorted(daily_df.index.get_level_values(1).unique().tolist())
    
    long_list = []
    short_list = []
    results_list = []
    for ticker in ticker_list:
        ticker_daily_df = daily_df.xs(ticker, level = 1)
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
    
        if len(total_trade[total_trade['Ticker'] == ticker]) == 0 or ticker_daily_df['dailyret'].sum() == 0:
            _result_ticker = pd.DataFrame(columns = [ticker])
        else:
            _result_ticker = merge_evaluate(total_trade[total_trade['Ticker'] == ticker], ticker_daily_df['dailyret'], long_ticker_daily_df['dailyret'].sum(), short_ticker_daily_df['dailyret'].sum(), ticker_daily_df['dailypnl'], ticker_daily_df['open_value'])
            _result_ticker.columns = [ticker]
        results_list.append(_result_ticker)
    
    long_daily_df = pd.concat(long_list).sort_index()
    short_daily_df = pd.concat(short_list).sort_index()
    
    results = merge_evaluate(total_trade, total_daily_return, long_daily_df['dailyret'].unstack().mean(axis = 1).sum(), short_daily_df['dailyret'].unstack().mean(axis = 1).sum(), total_daily_profit, total_daily_open_value)
    
    
    total_trade_nodce = total_trade[~total_trade['Ticker'].str.endswith('DCE')]
    long_daily_df_nodce = long_daily_df[~long_daily_df.index.get_level_values(1).str.endswith('DCE')]
    short_daily_df_nodce = short_daily_df[~short_daily_df.index.get_level_values(1).str.endswith('DCE')]
    daily_df_nodce = daily_df[~daily_df.index.get_level_values(1).str.endswith('DCE')]
    total_daily_return_nodce = daily_df_nodce['dailyret'].unstack().mean(axis = 1)
    total_daily_profit_nodce = daily_df_nodce['dailypnl'].unstack().sum(axis = 1)
    total_daily_open_value_nodce = daily_df_nodce['open_value'].unstack().sum(axis = 1)
    results_nodce = merge_evaluate(total_trade_nodce, total_daily_return_nodce, long_daily_df_nodce['dailyret'].unstack().mean(axis = 1).sum(), short_daily_df_nodce['dailyret'].unstack().mean(axis = 1).sum(), total_daily_profit_nodce, total_daily_open_value_nodce)
    
    tdr_list = []
    ld_dict = {}
    sd_dict = {}
    
    results.columns = ['Total']
    results_nodce.columns = ['Total_noDCE']
    rjys_list = [results, results_nodce]
    for jys in ['SHF', 'CZC', 'DCE', 'INE', 'GFE']:
        total_trade_jys = total_trade[total_trade['Ticker'].str.endswith(jys)]
        long_daily_df_jys = long_daily_df[long_daily_df.index.get_level_values(1).str.endswith(jys)]
        short_daily_df_jys = short_daily_df[short_daily_df.index.get_level_values(1).str.endswith(jys)]
        daily_df_jys = daily_df[daily_df.index.get_level_values(1).str.endswith(jys)]
        total_daily_return_jys = daily_df_jys['dailyret'].unstack().mean(axis = 1)
        total_daily_profit_jys = daily_df_jys['dailypnl'].unstack().sum(axis = 1)
        total_daily_open_value_jys = daily_df_jys['open_value'].unstack().sum(axis = 1)
        if total_daily_return_jys.sum() == 0:
            _result_ticker = pd.DataFrame(columns = [jys])
            continue
        else:
            results_jys = merge_evaluate(total_trade_jys, total_daily_return_jys, long_daily_df_jys['dailyret'].unstack().mean(axis = 1).sum(), short_daily_df_jys['dailyret'].unstack().mean(axis = 1).sum(), total_daily_profit_jys, total_daily_open_value_jys)
            results_jys.columns = [jys]
        rjys_list.append(results_jys)
    
        tdr_list.append(total_daily_return_jys.to_frame(name = jys))
        # tdr_dict[jys] = total_daily_return_jys
        ld_dict[jys] = long_daily_df_jys
        sd_dict[jys] = short_daily_df_jys
    rjys = pd.concat(rjys_list, axis = 1)
    tdrjys = pd.concat(tdr_list, axis = 1)
    
    _rjys = rjys.loc[['累计盈利', '年化收益', '年化收益率', '最大回撤', '夏普比率', '平均日占资', '最大日占资', '胜率', '盈亏收益比', '平均持仓周期','做多收益', '做空收益']]
    # _rjys.index = ['net','sharpe','annret','mdd','winrt','ret_pt','win/loss','hold','lret', 'sret']
    
    results_tickers = pd.concat(results_list, axis = 1)
    
    shar = results_tickers.loc['夏普比率'].sort_values(ascending = False)
    no_trade_tickers = shar[shar.isna()].index.tolist()
    
    results_tickers = results_tickers[shar.dropna().index]
    
    ls_df = pd.concat([long_daily_df['dailyret'], short_daily_df['dailyret']], axis = 1)
    ls_df.columns = ['long', 'short']
    
    # ax1 = fig.add_subplot(2, 1, 2)
    # if len(daily_return) > 1:
    #     xlist = [x.strftime('%Y%m%d') for x in daily_df.index.tolist()]
    #     ylist = daily_df.daily_equty_curve.tolist()
    #     ax1.plot(np.arange(len(xlist)), ylist, color='dodgerblue')
    #     ax1.set_xticks(np.arange(0,len(xlist),step = max(len(xlist)//8, 1)))
    #     ax1.set_xticklabels([xlist[i] for i in np.arange(0,len(xlist),step = max(len(xlist)//8, 1))])
    #     plt.ylabel('Return', fontsize='medium')
    #     ax_right = ax1.twinx()
    #     ax_right.stackplot(np.arange(daily_df.shape[0]), daily_df.open_value_intraday.values, labels=['open_value'] ,alpha=0.3)
    #     plt.xlabel('Segment', fontsize='medium')
    #     plt.ylabel('open value', fontsize='medium')
    #     plt.title('Daily Results', fontsize='large')
    
    
    
    
    elements = []
    elements.append(Paragraph(f'Commodity Daily CTA Report', title_style_1))
    
    # elements.append(Paragraph(f'Merge Statistics, total {len(ticker_list)} tickers, {len(no_trade_tickers)} tickers no trade', title_style_2))
    # table = generate_table(transfer_dataframe(results), head = '累积净值')
    table = generate_table(_rjys)
    elements.append(table)
    
    elements.append(Paragraph('Total Profit with Openvalue', title_style_2))
    pic = generate_plot_xy(total_daily_profit, total_daily_open_value, '')
    elements.append(pic)
    
    # elements.append(PageBreak())
    
    elements.append(Paragraph('Total noDCE Profit with Openvalue', title_style_2))
    pic = generate_plot_xy(total_daily_profit_nodce, total_daily_open_value_nodce, '')
    elements.append(pic)
    
    elements.append(Paragraph('Total Curve', title_style_2))
    _tdr = pd.concat([total_daily_return, total_daily_return_nodce], axis = 1).cumsum()
    _tdr.columns = ['total', 'total_noDCE']
    # pic = generate_plot(total_daily_return.cumsum(), '')
    pic = generate_plot_with_colors(_tdr, '', COLOR_LIST2[:2])
    elements.append(pic)
    
    
    elements.append(Paragraph('Daily Trade Counts', title_style_2))
    trade_counts = daily_df['dailyret'].unstack().replace(0, np.nan)
    trade_counts_nodce = daily_df_nodce['dailyret'].unstack().replace(0, np.nan)
    tc = pd.concat([trade_counts.count(axis = 1), trade_counts_nodce.count(axis = 1)], axis = 1)
    tc.columns = ['total', 'total_noDCE']
    pic = generate_plot_with_colors(tc, '', COLOR_LIST2[:2])
    elements.append(pic)
    
    
    
    elements.append(Paragraph('Long Short Curve', title_style_2))
    ls = pd.concat([long_daily_df['dailyret'].unstack().mean(axis = 1), short_daily_df['dailyret'].unstack().mean(axis = 1)], axis = 1).fillna(0).cumsum()
    ls.columns = ['long', 'short']
    ls_nodce = pd.concat([long_daily_df_nodce['dailyret'].unstack().mean(axis = 1), short_daily_df_nodce['dailyret'].unstack().mean(axis = 1)], axis = 1).fillna(0).cumsum()
    ls_nodce.columns = ['long', 'short']
    pic2 = generate_plot_with_colors_1x2_raw(ls, ls_nodce, 'Total', 'No DCE', COLOR_LIST2[:2])
    elements.append(pic2)
    
    elements.append(PageBreak())
    
    elements.append(Paragraph('Exchange Curve', title_style_2))
    pic = generate_plot_with_colors(tdrjys.cumsum(), '', COLOR_LIST2[:tdrjys.shape[1]])
    elements.append(pic)
    
    # for jys in ['SHF', 'CZC', 'DCE', 'INE', 'GFE']:
    #     if jys in ['SHF', 'INE']:
    #         elements.append(PageBreak())
    #     if not jys in ld_dict.keys():
    #         continue
    #     elements.append(Paragraph(f'{jys} Long Short Curve', title_style_2))
    #     ls = pd.concat([ld_dict[jys]['dailyret'].unstack().mean(axis = 1), sd_dict[jys]['dailyret'].unstack().mean(axis = 1)], axis = 1).fillna(0).cumsum()
    #     ls.columns = ['long', 'short']
    #     pic = generate_plot_with_colors(ls, '', COLOR_LIST2[:2])
    #     elements.append(pic)
    jys_ls_dict = {}
    for jys in ['SHF', 'CZC', 'DCE', 'INE', 'GFE']:
        if not jys in ld_dict.keys():
            continue
        ls = pd.concat([ld_dict[jys]['dailyret'].unstack().mean(axis = 1), sd_dict[jys]['dailyret'].unstack().mean(axis = 1)], axis = 1).fillna(0).cumsum()
        ls.columns = ['long', 'short']
        jys_ls_dict[jys] = ls
    
    elements.append(Paragraph(f'Exchange Long Short Curve', title_style_2))
    pic2 = generate_plot_with_colors_1x2_raw(jys_ls_dict['SHF'], jys_ls_dict['CZC'], 'SHF', 'CZC', COLOR_LIST2[:2])
    elements.append(pic2)
    pic2 = generate_plot_with_colors_1x2_raw(jys_ls_dict['DCE'], jys_ls_dict['INE'], 'DCE', 'INE', COLOR_LIST2[:2])
    elements.append(pic2)
    # pic2 = generate_plot_with_colors_1x2_raw(jys_ls_dict['DCE'], pd.DataFrame(), 'DCE', '', COLOR_LIST2[:2])
    # elements.append(pic2)
    elements.append(Paragraph(f"total {len(ticker_list)} tickers, {len(no_trade_tickers)} tickers no trade", head_style))
    elements.append(Paragraph(f"No Trade List: {' '.join(no_trade_tickers)}", head_style))
    elements.append(PageBreak())
    
    elements.append(Paragraph('All Ticker Results, Sorted By SharpeRatio', head_style))
    elements.append(Paragraph('Statistics', head_style))
    
    _rt = results_tickers.loc[['累积净值', '夏普比率', '年化收益', '最大回撤','胜率','每笔交易平均盈亏', '盈亏收益比', '平均持仓周期','做多收益', '做空收益']]
    _rt = _rt.T
    _rt.columns = ['net','sharpe','annret','mdd','winrt','ret_pt','win/loss','hold','lret', 'sret']
    table = generate_table(_rt)
    elements.append(table)
    elements.append(Paragraph('', head_style))
    # for i in range(0, len(_rt.columns)//10+1):
    #     table = generate_table(_rt[_rt.columns[i*10:(i+1)*10]])
    #     elements.append(table)
    #     elements.append(Paragraph('', head_style))
    i = 0
    for ticker in results_tickers.columns:
        if i % 3 == 0 and i > 1:
            elements.append(PageBreak())
        elements.append(Paragraph(ticker, head_style))
        # table = generate_table(transfer_dataframe(results_tickers[ticker]), head = '累积净值')
        # elements.append(table)
        
        pic2 = generate_plot_with_colors_1x2_raw(daily_df['dailyret'].xs(ticker, level = 1).to_frame(name = 'total').cumsum(), ls_df.xs(ticker, level = 1).cumsum(), '', '', COLOR_LIST2[:2])
        elements.append(pic2)
        i += 1
    
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.8 * inch, bottomMargin=0.8 * inch)
    doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)

output_path = f'/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/wyc/commodity_report/Commodity_Daily_CTA_2019_2022_report_v4.pdf'

trade_df = pd.read_hdf('/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/trade_df.h5')
daily_df = pd.read_hdf('/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/daily_df.h5')

final_generate_pdf(trade_df, daily_df, 20190101, 20221231, output_path)