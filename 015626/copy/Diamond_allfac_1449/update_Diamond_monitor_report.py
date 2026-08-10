import os
import time
import numpy as np
import pandas as pd
from copy import copy
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
from multifactor.IO import IO
from multifactor.utility import dt as udt
from overnight.naming_config import TRADING_PLAN
from overnight.utility import get_current_date, get_sharpe, get_annualized_return, get_max_drawdown, replace_zero, factor_aggregation


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


# In[9]:


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


# In[10]:


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


# In[11]:


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


# In[12]:


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


# In[13]:


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


# In[14]:


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


# In[15]:


# font
os.system('cp -r /data/user/015626/data/share/LOCAL_DATA/font/* /opt/anaconda3/lib/python3.6/site-packages/reportlab/fonts/')
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


end_date = get_current_date()
#end_date = 20240524
this_year = end_date // 10000
this_year_end = this_year * 10000 + 1231    
end_date_t1 = udt.get_trading_day_offset(end_date, -1)[0]
bgn_date = udt.get_trading_day_offset(end_date, -10)[0]



def minute_flag_check(date):
    path1 = '/data/group/800466/trade/overnight/flag/' + str(date) + '/' + str(date) + '_Diamond_factors_afterday.success'
    path2 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_future_overnight_return_multitime.success'
    path3 = '/data/group/800466/trade/overnight/flag/' + str(date) + '/' + str(date) + '_Diamond_sig.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3)


flag_root = '/data/group/800466/trade/overnight/flag/' + str(end_date) + '/'
os.makedirs(flag_root, exist_ok=True)
flag_path_start = flag_root + str(end_date) + '_Diamond_monitor_report.start'
with open(flag_path_start,'w') as file:
    pass 

print('------wait minute flag')
while True:
    if minute_flag_check(end_date):
        break
    time.sleep(60)
print('flag check finished!')


# In[19]:


'''原始收益序列导入'''
future_ret_raw = IO.read_data([20190101, this_year_end], universe=['IC.CFE', 'IF.CFE', 'IH.CFE'],
                    alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_ret_multitime.h5')
spot_ret_raw = IO.read_data([20190101, this_year_end], universe=['IC.CFE', 'IF.CFE', 'IH.CFE'], alt = 
                  '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_indexret_10minsclose_multitime.h5')

future_ret_raw_1449 = future_ret_raw['long_ret_930_1450'].unstack() - 0.4646 / 1e4
spot_ret_raw_1449 = spot_ret_raw['ret_930_1450'].unstack()
basis_ret_raw_1449 = future_ret_raw_1449 - spot_ret_raw_1449
basis_value_1449 = future_ret_raw['LastPx_mean_1440_1449'].unstack() / spot_ret_raw[
    'close_noon_1440_1449'].unstack() - 1


# In[20]:


Diamond_sig_raw = pd.read_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_1_0_sig.h5')
Diamond_sig = Diamond_sig_raw.copy()
Diamond_sig[Diamond_sig<0.16] = 0
Diamond_sig[Diamond_sig>0.5] = 0.5
Diamond_sig = Diamond_sig.reindex(future_ret_raw_1449.index)
daily_ret_1 = future_ret_raw_1449.mul(Diamond_sig, axis=0)


# In[ ]:





# In[21]:


output_path = f'/data/group/800466/warehouse/prod/tradingstats/Diamond/monitor_report/DiamondMonitor_{end_date}.pdf'


# In[22]:


elements = []
elements.append(Paragraph(f'Diamond Monitor {end_date}', title_style_1))


# In[23]:


elements.append(Paragraph('Market Statistics', title_style_2))

res = pd.DataFrame(
    index=['Overnight Return', 'Overnight Amplitude', 'Overnight Basis', 'Overnight Basis Convergence'], 
    columns=['近期均值', '2019以来分位数', '近120日分位数', '2024均值', '2023均值', '2022均值', '2021均值'])

temp_ss = future_ret_raw_1449.mean(axis=1)
temp_num = temp_ss.tail(5).mean()
res.loc['Overnight Return', '近期均值'] = temp_num
res.loc['Overnight Return', '2019以来分位数'] = arg_percentile(temp_ss['2019':], temp_num)
res.loc['Overnight Return', '近120日分位数'] = arg_percentile(temp_ss.tail(120), temp_num)    
res.loc['Overnight Return', '2024均值'] = temp_ss['2024'].mean()
res.loc['Overnight Return', '2023均值'] = temp_ss['2023'].mean()
res.loc['Overnight Return', '2022均值'] = temp_ss['2022'].mean()
res.loc['Overnight Return', '2021均值'] = temp_ss['2021'].mean()

temp_ss = future_ret_raw_1449.mean(axis=1).abs()
temp_num = temp_ss.tail(5).mean()
res.loc['Overnight Amplitude', '近期均值'] = temp_num
res.loc['Overnight Amplitude', '2019以来分位数'] = arg_percentile(temp_ss['2019':], temp_num)
res.loc['Overnight Amplitude', '近120日分位数'] = arg_percentile(temp_ss.tail(120), temp_num)    
res.loc['Overnight Amplitude', '2024均值'] = temp_ss['2024'].mean()
res.loc['Overnight Amplitude', '2023均值'] = temp_ss['2023'].mean()
res.loc['Overnight Amplitude', '2022均值'] = temp_ss['2022'].mean()
res.loc['Overnight Amplitude', '2021均值'] = temp_ss['2021'].mean()

temp_ss = basis_value_1449.mean(axis=1)
temp_num = temp_ss.tail(5).mean()
res.loc['Overnight Basis', '近期均值'] = temp_num
res.loc['Overnight Basis', '2019以来分位数'] = 1 - arg_percentile(temp_ss['2019':], temp_num)
res.loc['Overnight Basis', '近120日分位数'] = 1 - arg_percentile(temp_ss.tail(120), temp_num)
res.loc['Overnight Basis', '2024均值'] = temp_ss['2024'].mean()
res.loc['Overnight Basis', '2023均值'] = temp_ss['2023'].mean()
res.loc['Overnight Basis', '2022均值'] = temp_ss['2022'].mean()
res.loc['Overnight Basis', '2021均值'] = temp_ss['2021'].mean()

temp_ss = basis_ret_raw_1449.mean(axis=1)
temp_num = temp_ss.tail(5).mean()
res.loc['Overnight Basis Convergence', '近期均值'] = temp_num
res.loc['Overnight Basis Convergence', '2019以来分位数'] = arg_percentile(temp_ss['2019':], temp_num)
res.loc['Overnight Basis Convergence', '近120日分位数'] = arg_percentile(temp_ss.tail(120), temp_num)    
res.loc['Overnight Basis Convergence', '2024均值'] = temp_ss['2024'].mean()
res.loc['Overnight Basis Convergence', '2023均值'] = temp_ss['2023'].mean()
res.loc['Overnight Basis Convergence', '2022均值'] = temp_ss['2022'].mean()
res.loc['Overnight Basis Convergence', '2021均值'] = temp_ss['2021'].mean()
    
for col in res.columns:
    if '分位数' in col:
        res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
    else:
        res[col] = res[col].map(lambda x: f'{x:.5f}' if not np.isnan(x) else 'nan')
res = res.replace('nan', '-')
table = generate_table(res)
elements.append(table)


# In[24]:


elements.append(Paragraph('Overnight Future & Basis Return', head_style))
data_df_1 = pd.concat([future_ret_raw_1449['2019':].mean(axis=1), basis_ret_raw_1449['2019':].mean(axis=1)], axis=1).cumsum()
data_df_2 = pd.concat([future_ret_raw_1449['2024':].mean(axis=1), basis_ret_raw_1449['2024':].mean(axis=1)], axis=1).cumsum()
data_df_1.columns = data_df_2.columns = ['Future Return', 'Basis Return']
plot = generate_plot_with_colors_1x2_raw(data_df_1, data_df_2, 'since 2019', 'since 2024', COLOR_LIST[:2])
elements.append(plot)

elements.append(Paragraph('Overnight Amplitude', head_style))
data_df_1 = future_ret_raw_1449['2019':].mean(axis=1).abs().rolling(5).mean()
data_df_2 = future_ret_raw_1449['2024':].mean(axis=1).abs().rolling(5).mean()
plot = generate_plot_1x2(data_df_1, data_df_2, 'since 2019', 'since 2024')
elements.append(plot)
elements.append(PageBreak())


# In[25]:


elements.append(Paragraph('Signal Statistics', title_style_2))


# In[26]:


def calc_stats_1(daily_ret):
    result_ss = pd.Series(index=['夏普比率', '年化收益', '最大回撤', '开仓占比', '平均单笔收益率'])
    result_ss['夏普比率'] = get_sharpe(daily_ret)
    result_ss['年化收益'] = get_annualized_return(daily_ret)
    result_ss['最大回撤'] = get_max_drawdown(daily_ret.cumsum())[0]
    result_ss['开仓占比'] = len(daily_ret[daily_ret != 0]) / len(daily_ret)
    result_ss['平均单笔收益率'] = daily_ret[daily_ret != 0].mean()
    return result_ss


# In[27]:


elements.append(Paragraph('Strategy Statistics', head_style))
results_1 = calc_stats_1(daily_ret_1['2021':].mean(axis=1))
results_2 = calc_stats_1(daily_ret_1['2024':].mean(axis=1))
res = pd.concat([results_1, results_2], axis=1).T
res.index = ['since 2021', 'since 2024']
for col in res.columns:
    if '分位数' in col:
        res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
    else:
        res[col] = res[col].map(lambda x: f'{x:.5f}' if not np.isnan(x) else 'nan')
res = res.replace('nan', '-')
table = generate_table(res)
elements.append(table)


# In[28]:


def calc_wr(ret_ss):
    ret_ss = ret_ss.copy()
    ret_ss = ret_ss.dropna()
    return (ret_ss > 0).sum() / replace_zero((ret_ss != 0).sum())

def calc_wlr(ret_ss):
    ret_ss = ret_ss.copy()
    ret_ss = ret_ss.dropna()
    return -1 * ret_ss[ret_ss > 0].mean() / replace_zero(ret_ss[ret_ss < 0].mean())

def calc_recall(sig_ss, raw_ss):
    sig_ss = sig_ss.copy()
    raw_ss = raw_ss.copy()
    raw_ss = raw_ss.dropna()
    sig_ss = sig_ss.loc[raw_ss.index]
    return ((raw_ss > 0) & (sig_ss > 0)).sum() / replace_zero((raw_ss > 0).sum())

def calc_recall_adj(sig_ss, raw_ss):
    sig_ss = sig_ss.copy()
    raw_ss = raw_ss.copy()
    raw_ss = raw_ss[raw_ss > 0]
    sig_ss = sig_ss.loc[raw_ss.index]
    return (sig_ss * raw_ss).sum() / replace_zero(raw_ss.sum()) * 2

def calc_specificity(sig_ss, raw_ss):
    sig_ss = sig_ss.copy()
    raw_ss = raw_ss.copy()
    raw_ss = raw_ss.dropna()
    sig_ss = sig_ss.loc[raw_ss.index]
    return ((raw_ss < 0) & (sig_ss == 0)).sum() / replace_zero((raw_ss < 0).sum())

def calc_specificity_adj(sig_ss, raw_ss):
    sig_ss = sig_ss.copy()
    raw_ss = raw_ss.copy()
    raw_ss = raw_ss[raw_ss < 0]
    sig_ss = sig_ss.loc[raw_ss.index]
    return 1 - (sig_ss * raw_ss).sum() / replace_zero(raw_ss.sum())


def calc_stats(sig_ss, raw_ss):
    ret_ss = raw_ss * sig_ss
    result_ss = pd.DataFrame(
        index=['信息系数', '胜率', '盈亏比', '召回率', '特异度', '加权召回率', '加权特异度'], 
        columns=['近期均值', '2019年以来分位数', '近120日分位数', '2024年均值', '2023年均值', '2022年均值', '2021年均值'])
    temp_ss_1 = sig_ss.rolling(30, min_periods=3).corr(raw_ss)
    result_ss.iloc[0, 0] = temp_ss_1.tail(5).mean()
    result_ss.iloc[0, 1] = arg_percentile(temp_ss_1['2019':], result_ss.iloc[0, 0])
    result_ss.iloc[0, 2] = arg_percentile(temp_ss_1.tail(120), result_ss.iloc[0, 0])
    result_ss.iloc[0, 3] = temp_ss_1['2024'].mean()
    result_ss.iloc[0, 4] = temp_ss_1['2023'].mean()
    result_ss.iloc[0, 5] = temp_ss_1['2022'].mean()
    result_ss.iloc[0, 6] = temp_ss_1['2021'].mean()
    temp_ss_2 = ret_ss.rolling(30, min_periods=3).apply(calc_wr)
    result_ss.iloc[1, 0] = temp_ss_2.tail(5).mean()
    result_ss.iloc[1, 1] = arg_percentile(temp_ss_2['2019':], result_ss.iloc[1, 0])
    result_ss.iloc[1, 2] = arg_percentile(temp_ss_2.tail(120), result_ss.iloc[1, 0])
    result_ss.iloc[1, 3] = temp_ss_2['2024'].mean()
    result_ss.iloc[1, 4] = temp_ss_2['2023'].mean()
    result_ss.iloc[1, 5] = temp_ss_2['2022'].mean()
    result_ss.iloc[1, 6] = temp_ss_2['2021'].mean()
    temp_ss_3 = ret_ss.rolling(30, min_periods=3).apply(calc_wlr)
    result_ss.iloc[2, 0] = temp_ss_3.tail(5).mean()
    result_ss.iloc[2, 1] = arg_percentile(temp_ss_3['2019':], result_ss.iloc[2, 0])
    result_ss.iloc[2, 2] = arg_percentile(temp_ss_3.tail(120), result_ss.iloc[2, 0])
    result_ss.iloc[2, 3] = temp_ss_3['2024'].mean()
    result_ss.iloc[2, 4] = temp_ss_3['2023'].mean()
    result_ss.iloc[2, 5] = temp_ss_3['2022'].mean()
    result_ss.iloc[2, 6] = temp_ss_3['2021'].mean()
    temp_ss_4 = sig_ss.rolling(30, min_periods=10).apply(lambda _: calc_recall(sig_ss.loc[_.index], raw_ss.loc[_.index]))
    result_ss.iloc[3, 0] = temp_ss_4.tail(5).mean()
    result_ss.iloc[3, 1] = arg_percentile(temp_ss_4['2019':], result_ss.iloc[3, 0])
    result_ss.iloc[3, 2] = arg_percentile(temp_ss_4.tail(120), result_ss.iloc[3, 0])
    result_ss.iloc[3, 3] = temp_ss_4['2024'].mean()
    result_ss.iloc[3, 4] = temp_ss_4['2023'].mean()
    result_ss.iloc[3, 5] = temp_ss_4['2022'].mean()
    result_ss.iloc[3, 6] = temp_ss_4['2021'].mean()
    temp_ss_5 = sig_ss.rolling(30, min_periods=10).apply(lambda _: calc_specificity(sig_ss.loc[_.index], raw_ss.loc[_.index]))
    result_ss.iloc[4, 0] = temp_ss_5.tail(5).mean()
    result_ss.iloc[4, 1] = arg_percentile(temp_ss_5['2019':], result_ss.iloc[4, 0])
    result_ss.iloc[4, 2] = arg_percentile(temp_ss_5.tail(120), result_ss.iloc[4, 0])
    result_ss.iloc[4, 3] = temp_ss_5['2024'].mean()
    result_ss.iloc[4, 4] = temp_ss_5['2023'].mean()
    result_ss.iloc[4, 5] = temp_ss_5['2022'].mean()
    result_ss.iloc[4, 6] = temp_ss_5['2021'].mean()
    temp_ss_6 = sig_ss.rolling(30, min_periods=10).apply(lambda _: calc_recall_adj(sig_ss.loc[_.index], raw_ss.loc[_.index]))
    result_ss.iloc[5, 0] = temp_ss_6.tail(5).mean()
    result_ss.iloc[5, 1] = arg_percentile(temp_ss_6['2019':], result_ss.iloc[5, 0])
    result_ss.iloc[5, 2] = arg_percentile(temp_ss_6.tail(120), result_ss.iloc[5, 0])
    result_ss.iloc[5, 3] = temp_ss_6['2024'].mean()
    result_ss.iloc[5, 4] = temp_ss_6['2023'].mean()
    result_ss.iloc[5, 5] = temp_ss_6['2022'].mean()
    result_ss.iloc[5, 6] = temp_ss_6['2021'].mean()
    temp_ss_7 = sig_ss.rolling(30, min_periods=10).apply(lambda _: calc_specificity_adj(sig_ss.loc[_.index], raw_ss.loc[_.index]))
    result_ss.iloc[6, 0] = temp_ss_7.tail(5).mean()
    result_ss.iloc[6, 1] = arg_percentile(temp_ss_7['2019':], result_ss.iloc[6, 0])
    result_ss.iloc[6, 2] = arg_percentile(temp_ss_7.tail(120), result_ss.iloc[6, 0])
    result_ss.iloc[6, 3] = temp_ss_7['2024'].mean()
    result_ss.iloc[6, 4] = temp_ss_7['2023'].mean()
    result_ss.iloc[6, 5] = temp_ss_7['2022'].mean()
    result_ss.iloc[6, 6] = temp_ss_7['2021'].mean()
    
    return result_ss



elements.append(Paragraph('All Trading Days', head_style))
res = calc_stats(Diamond_sig, future_ret_raw_1449.mean(axis=1))
for col in res.columns:
    if '分位数' in col:
        res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
    else:
        res[col] = res[col].map(lambda x: f'{x:.5f}' if not np.isnan(x) else 'nan')
res = res.replace('nan', '-')
table = generate_table(res)
elements.append(table)

elements.append(Paragraph('Extreme Trading Days', head_style))
temp_ret_ss = future_ret_raw_1449.mean(axis=1)
temp_ret_ss[temp_ret_ss.abs() < 3e-3] = np.nan
res = calc_stats(Diamond_sig, temp_ret_ss)
for col in res.columns:
    if '分位数' in col:
        res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
    else:
        res[col] = res[col].map(lambda x: f'{x:.5f}' if not np.isnan(x) else 'nan')
res = res.replace('nan', '-')
table = generate_table(res)
elements.append(table)


# In[34]:


elements.append(Paragraph('Signal Return v.s. Market Return', head_style))
sig_ret1 = daily_ret_1.mean(axis=1)['2021':].cumsum()
sig_ret2 = daily_ret_1.mean(axis=1)['2024':].cumsum()
mkt_ret1 = future_ret_raw_1449.mean(axis=1)['2021':].cumsum() * Diamond_sig['2021': '2023'].mean()
mkt_ret2 = future_ret_raw_1449.mean(axis=1)['2024':].cumsum() * Diamond_sig['2021': '2023'].mean()
data_df1 = pd.concat([sig_ret1, mkt_ret1], axis=1)
data_df2 = pd.concat([sig_ret2, mkt_ret2], axis=1)
data_df1.columns = data_df2.columns = ['Signal Return', 'Market Return']
plot = generate_plot_with_colors_1x2_raw(data_df1, data_df2, 'since 2021', 'since 2024', COLOR_LIST[:2])
elements.append(plot)


# In[35]:


elements.append(PageBreak())


# In[36]:


elements.append(Paragraph('All Trading Days', head_style))

data = Diamond_sig.rolling(30, min_periods=10).corr(future_ret_raw_1449.mean(axis=1)).loc['2021':]
plot = generate_plot_with_median_line(data, f'Information Coefficient(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

data = daily_ret_1.mean(axis=1).rolling(30, min_periods=10).apply(calc_wr).loc['2021':]
plot = generate_plot_with_median_line(data, f'Win Rate(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

data = daily_ret_1.mean(axis=1).rolling(30, min_periods=10).apply(calc_wlr).loc['2021':].clip(upper=10)
plot = generate_plot_with_median_line(data, f'Win Loss Ratio(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

data = Diamond_sig.rolling(30, min_periods=10).apply(lambda _: calc_recall(
    Diamond_sig.loc[_.index], future_ret_raw_1449.mean(axis=1).loc[_.index])).loc['2021':]
plot = generate_plot_with_median_line(data, f'Recall Rate(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

data = Diamond_sig.rolling(30, min_periods=10).apply(lambda _: calc_specificity(
    Diamond_sig.loc[_.index], future_ret_raw_1449.mean(axis=1).loc[_.index])).loc['2021':]
plot = generate_plot_with_median_line(data, f'Specificity Rate(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

elements.append(PageBreak())


# In[37]:


elements.append(Paragraph('Extreme Trading Days', head_style))

temp_ret_ss = future_ret_raw_1449.mean(axis=1)
temp_ret_ss[temp_ret_ss.abs() < 3e-3] = np.nan

data = Diamond_sig.rolling(30, min_periods=10).corr(temp_ret_ss).loc['2021':]
plot = generate_plot_with_median_line(data, f'Information Coefficient(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

data = (temp_ret_ss * Diamond_sig).rolling(30, min_periods=10).apply(calc_wr).loc['2021':]
plot = generate_plot_with_median_line(data, f'Win Rate(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

data = (temp_ret_ss * Diamond_sig).rolling(30, min_periods=10).apply(calc_wlr).loc['2021':]#.clip(upper=10)
plot = generate_plot_with_median_line(data, f'Win Loss Ratio(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

data = Diamond_sig.rolling(30, min_periods=10).apply(lambda _: calc_recall(
    Diamond_sig.loc[_.index], temp_ret_ss.loc[_.index])).loc['2021':]
plot = generate_plot_with_median_line(data, f'Recall Rate(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

data = Diamond_sig.rolling(30, min_periods=10).apply(lambda _: calc_specificity(
    Diamond_sig.loc[_.index], temp_ret_ss.loc[_.index])).loc['2021':]
plot = generate_plot_with_median_line(data, f'Specificity Rate(rolling 30 days)', height=PLOT_HEIGHT*0.75)
elements.append(plot)

elements.append(PageBreak())




#elements.append(Paragraph('Trading Statistics', title_style_2))

#res_raw = pd.read_excel(f'/data/user/011477/Arrow/{end_date_t1.strftime("%Y%m%d")}_Future.xlsx', sheet_name='Diamond', index_col='日期', parse_dates=True)
#rename_columns = list()    
#for col in res_raw.columns:
#    if '交易张数' in col:
#        rename_columns.append(f'Volume({col[:col.find("交易张数")]})')
#    elif '本次开仓盈亏' in col:
#        rename_columns.append(f'Profit({col[:col.find("本次开仓盈亏")]})')
#res_raw.columns = rename_columns
#res = res_raw.loc[bgn_date: pd.Timestamp(str(end_date))].fillna(0)
#res.index = res.index.strftime('%Y-%m-%d')
#res = pd.concat([res, res.sum(axis=0).to_frame(name='Total').T], axis=0)
#profit_ss = res_raw[['Profit(IC)', 'Profit(IF)', 'Profit(IH)']].sum()
#profit_ss.index = ['IC', 'IF', 'IH']
#profit_detail = ', '.join(f'{ticker_type}: {int(profit):,}' for ticker_type, profit in zip(profit_ss.index, profit_ss.values))
#elements.append(Paragraph(f'Year-to-date Profit: {int(profit_ss.sum()):,} ({profit_detail})', head_style))
#recent_volume = res.loc['Total', 'Volume(IC)'] + res.loc['Total', 'Volume(IF)'] + res.loc['Total', 'Volume(IH)']
#recent_profit = res.loc['Total', 'Profit(IC)'] + res.loc['Total', 'Profit(IF)'] + res.loc['Total', 'Profit(IH)']
#res = res.applymap(lambda x: f'{int(x):,}')
#elements.append(Paragraph(f'Recent Volume: {int(recent_volume)}, Recent Profit: {int(recent_profit):,}', head_style))
#table = generate_table(res)
#elements.append(table)

elements.append(Paragraph('Position & Overnight Raw Return', head_style))
res = future_ret_raw_1449.tail(10)
res['Raw Ret(Avg)'] = res.mean(axis=1)
res['Signal'] = Diamond_sig_raw.loc[bgn_date: pd.Timestamp(str(end_date))]
res['Position'] = Diamond_sig.loc[bgn_date: pd.Timestamp(str(end_date))]
res.columns = ['Raw Ret(IC)', 'Raw Ret(IF)', 'Raw Ret(IH)', 'Raw Ret(Avg)', 'Signal', 'Position']
res = res[['Signal', 'Position', 'Raw Ret(IC)', 'Raw Ret(IF)', 'Raw Ret(IH)', 'Raw Ret(Avg)']]
res.index = res.index.strftime('%Y-%m-%d')
for col in res.columns:
    if 'Raw Ret' in col:
        res[col] = res[col].map(lambda x: f'{x:.5f}' if not np.isnan(x) else 'nan')
    else:
        res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
table = generate_table(res)
elements.append(table)
elements.append(PageBreak())


# In[39]:


elements.append(Paragraph('Factor Performance', title_style_2))
factor_list = TRADING_PLAN['Diamond_1_0']
factor_prod = factor_aggregation('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/1449')
factor_temp = factor_prod[factor_list].copy()
factor_temp = factor_temp.reindex(future_ret_raw_1449.index)
factor_temp[factor_temp < 0.75] = 0
factor_temp[factor_temp > 0] = 1
single_factor_ret = factor_temp.mul(future_ret_raw_1449.mean(axis=1), axis=0)

elements.append(Paragraph('Since 2025', head_style))
temp_df1 = single_factor_ret['2025'].sum().sort_values(ascending=False)
plot = generate_plot_bar(temp_df1, title='')
elements.append(plot)

elements.append(Paragraph('Since 2021', head_style))
temp_df2 = single_factor_ret['2021':].sum().sort_values(ascending=False)
plot = generate_plot_bar(temp_df2, title='')
elements.append(plot)

elements.append(PageBreak())


# In[40]:


doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.8 * inch, bottomMargin=0.8 * inch)
doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)
print(f'save to {output_path}', flush=True)


# In[41]:


ftp = FTPFile()
ftp.uploadFile(output_path, f'012398/AlternativeTrading/Diamond/DiamondMonitor_{end_date}.pdf')




flag_path_success = flag_root + str(end_date) + '_Diamond_monitor_report.success'
with open(flag_path_success, 'w') as file:
    pass
