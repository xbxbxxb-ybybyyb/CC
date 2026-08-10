import sys

sys.path.insert(0, '/data/user/020529/mobius_monitor/code')

import os
import copy
import ftplib
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import PIL.Image as pi
from toolkit.multifactor.IO.IO import read_data
from toolkit.multifactor.data.utils import get_current_date
from toolkit.multifactor.utility.dt import get_trading_date_range

from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, Table, TableStyle

# copy font files
os.system('cp -r /data/user/015626/data/share/LOCAL_DATA/font/* /opt/anaconda3/lib/python3.6/site-packages/reportlab/fonts/')

# font
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))  # Chinese Simplified (mainland)
pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))  # Song Ti

# text style
styles = getSampleStyleSheet()
title_style_1 = copy.copy(styles['Heading1'])
title_style_1.alignment = 1
title_style_2 = copy.copy(styles['Heading2'])
title_style_2.alignment = 1
head_style = copy.copy(styles['Heading3'])
head_style.alignment = 0
mini_style = copy.copy(styles['Normal'])
mini_style.alignment = 0
mini_style.fontSize = 1
mini_style.leading = 10

# plot style
plt.style.use('ggplot')

# plot parameters
PLOT_WIDTH = 7
PLOT_HEIGHT = 2
PLOT_HEIGHT2 = 2.8
TITLE_FONT_SIZE = 30
TICKS_FONT_SIZE = 25
LINE_WIDTH = 3
MARKER_SIZE = 10
MAIN_COLOR = 'royalblue'
FILL_COLOR = 'chocolate'
COLOR_L = 'indianred'
COLOR_S = 'seagreen'
COLOR_LIST = ['darkorange', 'darkorchid', 'royalblue']
COLOR_LIST2 = ['royalblue', 'dodgerblue', 'deepskyblue', 'skyblue', 'lightblue']


def main():
    str_date = '20250401'
    end_date = '20250429'

    if end_date is None:
        end_date = str(get_current_date(new_date_time=18))

    YMD = '%Y%m%d'
    trade_date_list = get_trading_date_range(start_date='20190101', end_date=end_date)
    trade_date_list = [x.strftime(YMD) for x in trade_date_list]

    if str_date is None:
        str_date = trade_date_list[-5]

    stats_date_list = pd.DatetimeIndex(trade_date_list)
    stats_date_list = stats_date_list[(stats_date_list >= str_date) & (stats_date_list <= end_date)]
    stats_date_list = [x.strftime(YMD) for x in stats_date_list]

    date_list_from_2021 = get_trading_date_range(start_date='20210101', end_date=end_date)
    date_list_from_2021 = [x.strftime(YMD) for x in date_list_from_2021]
    date_list_from_2025 = get_trading_date_range(start_date='20250101', end_date=end_date)
    date_list_from_2025 = [x.strftime(YMD) for x in date_list_from_2025]

    output_path = f'/data/user/020529/mobius_monitor/report/MobiusMonitor_{str_date}_{end_date}.pdf'
    ftplib_root = None

    data_root = '/data/user/020529/mobius_monitor/data'
    track_root = '/data/user/020529/share/mobius_tracking'
    stats_root = '/data/group/800466/warehouse/prod/tradingstats/Mobius/tracking'

    ticker_type_list = ['IF', 'IC', 'IM']
    ticker_pnl_dict = {
        'IF': '/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl_if.xlsx',
        'IC': '/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl.xlsx',
        'IM': '/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl_im.xlsx',
    }
    ticker_strategy_dict = {
        'IF': '20250328_if_mobius',
        'IC': '20250328_ic_mobius',
        'IM': '20250328_im_mobius',
    }
    ticker_models_dict = {
        'IF': ['20250328_if_mobius_zsj', '20250328_if_mobius_crn'],
        'IC': ['20250328_ic_mobius_zsj', '20250328_ic_mobius_crn'],
        'IM': ['20250328_im_mobius_zsj', '20250328_im_mobius_crn'],
    }
    ticker_strategy_filt_dict = {
        'IF': '20250328_if_mobius_filt',
        'IC': '20250328_ic_mobius_filt',
        'IM': '20250328_im_mobius_filt',
    }
    ticker_factor_dict = {
        'IF': 'if_linear_v7_ew',
        'IC': 'ic_linear_v7_ew',
        'IM': 'im_linear_v1_ew',
    }

    spot_code_list = ['000300.SH', '000905.SH', '000852.SH', '932000.CSI', '000985.CSI']
    spot_code_dict = {'000300.SH': 'HS300', '000905.SH': 'ZZ500', '000852.SH': 'ZZ1000', '932000.CSI': 'ZZ2000', '000985.CSI': 'ALLA'}

    # ****************************************************************************************************

    elements = []
    elements.append(Paragraph(f'Mobius Monitor {end_date}', title_style_1))

    # ****************************************************************************************************

    elements.append(Paragraph('Market Statistics', title_style_2))

    elements.append(Paragraph('Futures Volatility (Recent Month)', head_style))
    res = {}
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/market_futures_volatility.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.loc[:end_date]
        res[ticker_type] = get_market_statistics(data, str_date, end_date)
    res = pd.DataFrame(res).T
    for col in res.columns:
        if '分位数' in col:
            res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
        else:
            res[col] = res[col].map(lambda x: f'{x:.5f}' if not np.isnan(x) else 'nan')
    res = res.replace('nan', '-')
    table = generate_table(res)
    elements.append(table)

    elements.append(Paragraph('Futures Volume (All Contracts)', head_style))
    res = {}
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/market_futures_total_volume.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.loc[:end_date]
        res[ticker_type] = get_market_statistics(data, str_date, end_date)
    res = pd.DataFrame(res).T
    for col in res.columns:
        if '分位数' in col:
            res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
        else:
            res[col] = res[col].map(lambda x: f'{int(x):,}' if not np.isnan(x) else 'nan')
    res = res.replace('nan', '-')
    table = generate_table(res)
    elements.append(table)

    elements.append(Paragraph('Bid-Ask Spread (Recent Month)', head_style))
    res = {}
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/market_bid_ask_spread.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.loc[:end_date]
        res[ticker_type] = get_market_statistics(data, str_date, end_date)
    res = pd.DataFrame(res).T
    for col in res.columns:
        if '分位数' in col:
            res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
        else:
            res[col] = res[col].map(lambda x: f'{x:.5f}' if not np.isnan(x) else 'nan')
    res = res.replace('nan', '-')
    table = generate_table(res)
    elements.append(table)

    elements.append(Paragraph('.', mini_style))

    data_dict = {}
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/market_futures_volatility.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(stats_date_list))
        data_dict[ticker_type] = data
    df = pd.DataFrame(data_dict)
    plot = generate_plot_with_colors_and_values(df, 'Futures Volatility (Recent Month)', COLOR_LIST[:len(ticker_type_list)], value_type='float5')
    elements.append(plot)

    data_dict = {}
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/market_futures_total_volume.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(stats_date_list))
        data_dict[ticker_type] = data
    df = pd.DataFrame(data_dict)
    plot = generate_plot_with_colors_and_values(df, 'Futures Volume (All Contracts)', COLOR_LIST[:len(ticker_type_list)], value_type='int')
    elements.append(plot)

    elements.append(PageBreak())

    elements.append(Paragraph(f'Futures Volatility (Recent Month)', head_style))
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/market_futures_volatility.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(trade_date_list))
        data = data.rolling(5).mean()
        plot = generate_plot_with_median_line(data, f'[{ticker_type}] Futures Volatility (Recent Month)')
        elements.append(plot)

    elements.append(PageBreak())

    elements.append(Paragraph(f'Futures Volume (All Contracts)', head_style))
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/market_futures_total_volume.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(trade_date_list))
        data = data.rolling(5).mean()
        plot = generate_plot_with_median_line(data, f'[{ticker_type}] Futures Volume (All Contracts)')
        elements.append(plot)

    elements.append(PageBreak())

    elements.append(Paragraph(f'Futures Volume (Recent Month)', head_style))
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/market_futures_volume.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(trade_date_list))
        data = data.rolling(5).mean()
        plot = generate_plot_with_median_line(data, f'[{ticker_type}] Futures Volume (Recent Month)')
        elements.append(plot)

    elements.append(PageBreak())

    elements.append(Paragraph(f'Bid-Ask Spread (Recent Month)', head_style))
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/market_bid_ask_spread.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(trade_date_list))
        data = data.rolling(5).mean()
        plot = generate_plot_with_median_line(data, f'[{ticker_type}] Bid-Ask Spread (Recent Month)')
        elements.append(plot)

    elements.append(PageBreak())

    elements.append(Paragraph(f'Index Amount', head_style))
    data_dict = {}
    for spot_code in spot_code_list:
        data_path = f'{data_root}/market_spot_amount.xlsx'
        data = pd.read_excel(data_path, sheet_name=spot_code, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(stats_date_list))
        data_dict[spot_code] = data
    df = pd.DataFrame(data_dict)
    df.columns = [spot_code_dict[spot_code] for spot_code in spot_code_list]
    columns = list(df.columns)
    columns.remove('ALLA')
    df['ALLA'] = df['ALLA'] - df[columns].sum(axis=1)
    df = df.rename(columns={'ALLA': 'Others'})
    plot = generate_stackplot_with_values(df.div(1e8), 'Index Amount (1e8)', COLOR_LIST2[:len(spot_code_list)], value_type='int')
    elements.append(plot)

    for spot_code in spot_code_list[0:3]:
        data_path = f'{data_root}/market_spot_amount.xlsx'
        data = pd.read_excel(data_path, sheet_name=spot_code, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(trade_date_list))
        data = data.rolling(5).mean()
        plot = generate_plot_with_median_line(data.div(1e8), f'[{spot_code_dict[spot_code]}] Index Amount (1e8)')
        elements.append(plot)

    elements.append(PageBreak())

    # ****************************************************************************************************

    elements.append(Paragraph('Signal Statistics', title_style_2))

    elements.append(Paragraph('Realized Return Ratio', head_style))
    res = {}
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/signal_realized_return_ratio.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.loc[:end_date]
        res[ticker_type] = get_market_statistics(data, str_date, end_date)
    res = pd.DataFrame(res).T
    for col in res.columns:
        if '分位数' in col:
            res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
        else:
            res[col] = res[col].map(lambda x: f'{x:.5f}' if not np.isnan(x) else 'nan')
    res = res.replace('nan', '-')
    table = generate_table(res)
    elements.append(table)

    elements.append(Paragraph('Information Coefficient', head_style))
    res = {}
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/signal_information_coefficient.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.loc[:end_date]
        res[ticker_type] = get_market_statistics(data, str_date, end_date)
    res = pd.DataFrame(res).T
    for col in res.columns:
        if '分位数' in col:
            res[col] = res[col].map(lambda x: f'{x:.2f}' if not np.isnan(x) else 'nan')
        else:
            res[col] = res[col].map(lambda x: f'{x:.5f}' if not np.isnan(x) else 'nan')
    res = res.replace('nan', '-')
    table = generate_table(res)
    elements.append(table)

    elements.append(Paragraph('.', mini_style))

    data_dict = {}
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/signal_realized_return_ratio.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(stats_date_list))
        data_dict[ticker_type] = data
    df = pd.DataFrame(data_dict)
    plot = generate_plot_with_colors_and_values(df, 'Realized Return Ratio', COLOR_LIST[:len(ticker_type_list)], value_type='float5')
    elements.append(plot)

    data_dict = {}
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/signal_information_coefficient.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(stats_date_list))
        data_dict[ticker_type] = data
    df = pd.DataFrame(data_dict)
    plot = generate_plot_with_colors_and_values(df, 'Information Coefficient', COLOR_LIST[:len(ticker_type_list)], value_type='float5')
    elements.append(plot)

    elements.append(PageBreak())

    elements.append(Paragraph(f'Realized Return Ratio', head_style))
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/signal_realized_return_ratio.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2021))
        data = data.rolling(5).mean()
        plot = generate_plot_with_median_line(data, f'[{ticker_type}] Realized Return Ratio')
        elements.append(plot)

    elements.append(PageBreak())

    elements.append(Paragraph(f'Information Coefficient', head_style))
    for ticker_type in ticker_type_list:
        data_path = f'{data_root}/signal_information_coefficient.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2021))
        data = data.rolling(5).mean()
        plot = generate_plot_with_median_line(data, f'[{ticker_type}] Information Coefficient')
        elements.append(plot)

    elements.append(PageBreak())

    # ****************************************************************************************************

    elements.append(Paragraph('Trading Statistics', title_style_2))

    # dt, contract -> volume
    data_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5'
    all_contract_vol = read_data(trading_days=[pd.Timestamp(str_date), pd.Timestamp(end_date) + pd.Timedelta(days=1)], columns=['volume'], alt=data_path)

    # trade and order record
    trade_record = pd.read_pickle(f'{data_root}/record_trade.pkl')
    order_record = pd.read_pickle(f'{data_root}/record_order.pkl')
    order_b1px = pd.read_pickle(f'{data_root}/record_order_b1px.pkl')
    order_s1px = pd.read_pickle(f'{data_root}/record_order_s1px.pkl')
    order_last = pd.read_pickle(f'{data_root}/record_order_last.pkl')

    recent_stats_dict = {}
    ticker_stats_dict = {}
    for ticker_type in ticker_type_list:
        # profit and volume
        profit_list = []
        volume_list = []
        data_path = ticker_pnl_dict[ticker_type]
        data = pd.read_excel(data_path, parse_dates=['date'], index_col=0)
        for date in stats_date_list:
            try:
                profit = data.loc[date]['pnl']
                volume = data.loc[date]['contracts_traded']
            except Exception:
                profit = np.nan
                volume = np.nan
            profit_list.append(profit)
            volume_list.append(volume)
        daily_profit = pd.Series(profit_list, index=pd.to_datetime(stats_date_list))
        daily_volume = pd.Series(volume_list, index=pd.to_datetime(stats_date_list))

        # proportion
        proportion_list = []
        for date in stats_date_list:
            try:
                data = trade_record[ticker_type].loc[date].copy()
                trade_number = data['成交数量']
                trade_number = trade_number.groupby(trade_number.index.strftime('%Y%m%d%H%M')).apply(lambda x: x.sum())
                trade_number.index = pd.to_datetime(trade_number.index)
                trade_ticker = data['证券代码']
                trade_ticker = trade_ticker.groupby(trade_ticker.index.strftime('%Y%m%d%H%M')).apply(lambda x: x.iloc[0])
                trade_ticker.index = pd.to_datetime(trade_ticker.index)
                trade_ticker = trade_ticker.apply(lambda x: x + '.CFE')
                market_number = []
                for idx, val in trade_ticker.items():
                    market_number.append(all_contract_vol['volume'].loc[idx, val])
                market_number = pd.Series(market_number, index=trade_ticker.index)
                proportion = (trade_number / market_number).mean()
            except Exception:
                proportion = np.nan
            proportion_list.append(proportion)
        daily_proportion = pd.Series(proportion_list, index=pd.to_datetime(stats_date_list))

        # completion
        completion_list = []
        for date in stats_date_list:
            try:
                data = order_record[ticker_type].loc[date].copy()
                completion = data['成交数量'].sum() / data['委托数量'].sum()
            except Exception:
                completion = np.nan
            completion_list.append(completion)
        daily_completion = pd.Series(completion_list, index=pd.to_datetime(stats_date_list))

        # slippage
        slippage_list = []
        slippage_twap_list = []
        for date in stats_date_list:
            try:
                df = order_record[ticker_type].loc[date].copy()
                bp = order_b1px[ticker_type].loc[date].copy()
                sp = order_s1px[ticker_type].loc[date].copy()
                lp = order_last[ticker_type].loc[date].copy()

                df = df[['证券代码', '委托方向', '成交数量', '成交均价']]
                df.columns = ['contract', 'direction', 'number', 'price']
                bs_mapping = {'买': 1, '卖': -1}
                df['direction'] = df['direction'].map(lambda x: bs_mapping[x[0]])
                cond1 = df['price'] >= bp.min(axis=1)
                cond2 = df['price'] <= sp.max(axis=1)
                df['number'] = df['number'].where(cond1 & cond2, 0)
                df['price'] = df['price'].where(cond1 & cond2, 0)

                b_flag = df['direction'] > 0
                s_flag = df['direction'] < 0
                b_px_diff = ((df['price'] - sp[0]) * df['number'])[b_flag].sum(axis=0) / df['number'][b_flag].sum(axis=0)
                s_px_diff = ((df['price'] - bp[0]) * df['number'])[s_flag].sum(axis=0) / df['number'][s_flag].sum(axis=0)
                slippage = (b_px_diff - s_px_diff) / 2
                b_px_diff_twap = ((df['price'] - lp.iloc[:, 0:20].mean(axis=1)) * df['number'])[b_flag].sum(axis=0) / df['number'][b_flag].sum(axis=0)
                s_px_diff_twap = ((df['price'] - lp.iloc[:, 0:20].mean(axis=1)) * df['number'])[s_flag].sum(axis=0) / df['number'][s_flag].sum(axis=0)
                slippage_twap = (b_px_diff_twap - s_px_diff_twap) / 2
            except Exception:
                slippage = np.nan
                slippage_twap = np.nan
            slippage_list.append(slippage)
            slippage_twap_list.append(slippage_twap)
        daily_slippage = pd.Series(slippage_list, index=pd.to_datetime(stats_date_list))  # compare to the 1st tick
        daily_slippage_twap = pd.Series(slippage_twap_list, index=pd.to_datetime(stats_date_list))  # compare to the 10s twap

        recent_stats_dict[ticker_type] = [daily_profit.sum(), daily_volume.sum(), daily_completion.mean(), daily_proportion.mean(), daily_slippage.mean(), daily_slippage_twap.mean()]

        ticker_stats = pd.concat([daily_profit, daily_volume, daily_completion, daily_proportion, daily_slippage, daily_slippage_twap], axis=1)
        ticker_stats.columns = ['Profit', 'Volume', 'Completion', 'Proportion', 'Slippage', 'Slippage2']
        ticker_stats.index = ticker_stats.index.strftime('%Y-%m-%d').to_list()
        ticker_stats['Profit'] = ticker_stats['Profit'].map(lambda x: f'{int(x):,}' if not np.isnan(x) else 'nan')
        ticker_stats['Volume'] = ticker_stats['Volume'].map(lambda x: f'{int(x):,}' if not np.isnan(x) else 'nan')
        ticker_stats['Proportion'] = ticker_stats['Proportion'].map(lambda x: f'{x:.2%}' if not np.isnan(x) else 'nan')
        ticker_stats['Completion'] = ticker_stats['Completion'].map(lambda x: f'{x:.2%}' if not np.isnan(x) else 'nan')
        ticker_stats['Slippage'] = ticker_stats['Slippage'].map(lambda x: f'{x:.4f}' if not np.isnan(x) else 'nan')
        ticker_stats['Slippage2'] = ticker_stats['Slippage2'].map(lambda x: f'{x:.4f}' if not np.isnan(x) else 'nan')
        ticker_stats = ticker_stats.replace('nan', '-')
        ticker_stats = ticker_stats.rename(columns={'Profit': '当日盈亏', 'Volume': '成交量', 'Completion': '成交率', 'Proportion': '成交占比', 'Slippage': '成交滑点（1st Tick）', 'Slippage2': '成交滑点（10s Twap）'})
        ticker_stats_dict[ticker_type] = ticker_stats.copy()

    elements.append(Paragraph('Recent Summary', head_style))
    recent_stats = pd.DataFrame(recent_stats_dict, index=['Profit', 'Volume', 'Completion', 'Proportion', 'Slippage', 'Slippage2']).T
    append_stats = [recent_stats['Profit'].sum(), recent_stats['Volume'].sum(), recent_stats['Completion'].mean(), recent_stats['Proportion'].mean(), recent_stats['Slippage'].mean(), recent_stats['Slippage2'].mean()]
    append_stats = pd.DataFrame({'Total': append_stats}, index=['Profit', 'Volume', 'Completion', 'Proportion', 'Slippage', 'Slippage2']).T
    recent_stats = pd.concat([recent_stats, append_stats], axis=0)
    recent_stats['Profit'] = recent_stats['Profit'].map(lambda x: f'{int(x):,}' if not np.isnan(x) else 'nan')
    recent_stats['Volume'] = recent_stats['Volume'].map(lambda x: f'{int(x):,}' if not np.isnan(x) else 'nan')
    recent_stats['Proportion'] = recent_stats['Proportion'].map(lambda x: f'{x:.2%}' if not np.isnan(x) else 'nan')
    recent_stats['Completion'] = recent_stats['Completion'].map(lambda x: f'{x:.2%}' if not np.isnan(x) else 'nan')
    recent_stats['Slippage'] = recent_stats['Slippage'].map(lambda x: f'{x:.4f}' if not np.isnan(x) else 'nan')
    recent_stats['Slippage2'] = recent_stats['Slippage2'].map(lambda x: f'{x:.4f}' if not np.isnan(x) else 'nan')
    recent_stats = recent_stats.replace('nan', '-')
    recent_stats = recent_stats.rename(columns={'Profit': '近期盈亏', 'Volume': '成交量', 'Completion': '成交率', 'Proportion': '成交占比', 'Slippage': '成交滑点(1st Tick)', 'Slippage2': '成交滑点(10s Twap)'})
    table = generate_table(recent_stats)
    elements.append(table)

    elements.append(Paragraph('Year-to-date Profit', head_style))
    profit_dict = {}
    for ticker_type in ticker_type_list:
        data_path = ticker_pnl_dict[ticker_type]
        data = pd.read_excel(data_path, parse_dates=['date'], index_col=0)
        data = data['pnl']
        data = data.reindex(pd.to_datetime(date_list_from_2025), fill_value=0)
        profit_dict[ticker_type] = data
    profit = pd.concat(profit_dict, axis=1)
    profit['Total'] = profit.sum(axis=1)

    total_profit_sum = profit['Total'].sum(axis=0)
    total_profit_curve = profit['Total'].cumsum(axis=0)
    plot = generate_plot(total_profit_curve, title=f'Total Profit: {int(total_profit_sum):,}')
    elements.append(plot)

    ticker_profit_sum = profit[ticker_type_list].sum(axis=0)
    ticker_profit_curve = profit[ticker_type_list].cumsum(axis=0)
    ticker_profit_title = [f'{ticker_type}: {int(ticker_profit_sum[ticker_type]):,}' for ticker_type in ticker_type_list]
    ticker_profit_title = ', '.join(ticker_profit_title)
    plot = generate_plot_with_colors(ticker_profit_curve, title=ticker_profit_title, color_list=COLOR_LIST[:len(ticker_type_list)])
    elements.append(plot)

    elements.append(PageBreak())

    for ticker_type in ticker_type_list:
        ticker_stats = ticker_stats_dict[ticker_type]
        table = generate_table(ticker_stats, head=ticker_type)
        elements.append(table)
        elements.append(Paragraph('', head_style))

    for ticker_type in ticker_type_list:
        data_path = f'{stats_root}/pics/{ticker_type.lower()}.xlsx'
        data = pd.read_excel(data_path, parse_dates=['open_time', 'close_time'], index_col='open_time')
        data = data.sort_index()
        data = data.loc[str_date:end_date]
        trade_stats = get_trade_stats(data)
        trade_stats = trade_stats.T
        trade_stats = trade_stats.replace('nan', '-')
        table = generate_table(trade_stats, head=ticker_type)
        elements.append(table)
        elements.append(Paragraph('', head_style))

    elements.append(PageBreak())

    num_ticks = 120
    date = end_date
    elements.append(Paragraph(f'Price Movement (Volume-Weighted Price, {date})', head_style))
    for ticker_type in ticker_type_list:
        try:
            df = order_record[ticker_type].loc[date].copy()
            bp = order_b1px[ticker_type].loc[date].copy()
            sp = order_s1px[ticker_type].loc[date].copy()

            df = df[['证券代码', '委托方向', '成交数量', '成交均价']]
            df.columns = ['contract', 'direction', 'number', 'price']
            bs_mapping = {'买': 1, '卖': -1}
            df['direction'] = df['direction'].map(lambda x: bs_mapping[x[0]])
            cond1 = df['price'] >= bp.min(axis=1)
            cond2 = df['price'] <= sp.max(axis=1)
            df['number'] = df['number'].where(cond1 & cond2, 0)
            df['price'] = df['price'].where(cond1 & cond2, 0)

            b_flag = df['direction'] > 0
            s_flag = df['direction'] < 0
            b_px_move = sp.sub(sp[0], axis=0).mul(df['number'], axis=0)[b_flag].sum(axis=0) / df['number'][b_flag].sum(axis=0)
            s_px_move = bp.sub(bp[0], axis=0).mul(df['number'], axis=0)[s_flag].sum(axis=0) / df['number'][s_flag].sum(axis=0)
            b_px_diff = ((df['price'] - sp[0]) * df['number'])[b_flag].sum(axis=0) / df['number'][b_flag].sum(axis=0)
            s_px_diff = ((df['price'] - bp[0]) * df['number'])[s_flag].sum(axis=0) / df['number'][s_flag].sum(axis=0)
            b_px_diff = pd.Series(b_px_diff, index=b_px_move.index)
            s_px_diff = pd.Series(s_px_diff, index=s_px_move.index)
        except Exception:
            b_px_move = pd.Series(0.0, index=[i for i in range(num_ticks)])
            s_px_move = pd.Series(0.0, index=[i for i in range(num_ticks)])
            b_px_diff = pd.Series(0.0, index=[i for i in range(num_ticks)])
            s_px_diff = pd.Series(0.0, index=[i for i in range(num_ticks)])
        df = pd.concat([b_px_move, s_px_move, b_px_diff, s_px_diff], axis=1)
        df.columns = ['Sell1Price', 'Buy1Price', 'AvgBuyPrice', 'AvgSellPrice']
        df.index = [i / 2 for i in df.index]
        color_list = [COLOR_L, COLOR_S, COLOR_L, COLOR_S]
        style_list = ['-', '-', '--', '--']
        plot = generate_plot_with_colors_and_styles(df, f'[{ticker_type}] Price Movement', color_list, style_list, legend_loc='upper right')
        elements.append(plot)

    elements.append(PageBreak())

    date = end_date
    elements.append(Paragraph(f'Time Distribution ({date})', head_style))
    seconds = [i for i in range(60)]
    for ticker_type in ticker_type_list:
        try:
            data = order_record[ticker_type].loc[date].copy()
            sec_order = data.groupby(data.index.second)['委托数量'].sum().reindex(seconds).fillna(0)
        except Exception:
            sec_order = pd.Series(0.0, index=seconds)
        try:
            data = trade_record[ticker_type].loc[date].copy()
            sec_trade = data.groupby(data.index.second)['成交数量'].sum().reindex(seconds).fillna(0)
        except Exception:
            sec_trade = pd.Series(0.0, index=seconds)
        df = pd.concat([sec_order, sec_trade], axis=1)
        df.columns = ['order', 'transaction']
        plot = generate_plot_with_colors(df, f'[{ticker_type}] Time Distribution', COLOR_LIST[:2], legend_loc='upper right')
        elements.append(plot)

    elements.append(PageBreak())

    # ****************************************************************************************************

    elements.append(Paragraph('Trading Figures', title_style_2))

    # elements.append(Paragraph('Prod Signal Back Test', head_style))
    # for ticker_type in ticker_type_list:
    #     data_path = f'{stats_root}/back_test/{end_date}/{ticker_type}/{end_date}.png'
    #     if os.path.exists(data_path):
    #         image = pi.open(data_path)
    #     else:
    #         image = pi.new('RGB', (15, 10), (240, 240, 240))
    #         print(f'[{ticker_type}] no trade figure', flush=True)
    #     plot = generate_plot_from_image(image)
    #     elements.append(plot)

    elements.append(Paragraph('Research Signal Back Test', head_style))
    for ticker_type in ticker_type_list:
        strategy = ticker_strategy_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/total_trade_from_2025/{end_date}.png'
        if os.path.exists(data_path):
            image = pi.open(data_path)
        else:
            image = pi.new('RGB', (15, 10), (240, 240, 240))
            print(f'[{ticker_type}] no trade figure', flush=True)
        plot = generate_plot_from_image(image)
        elements.append(plot)

    elements.append(PageBreak())

    # ****************************************************************************************************

    elements.append(Paragraph('Strategy Back Test', title_style_2))

    elements.append(Paragraph('Back Test Result', head_style))
    result_dict = {}
    for ticker_type in ticker_type_list:
        strategy = ticker_strategy_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_recent_10/{strategy}_results.csv'
        data = pd.read_csv(data_path, encoding='gbk', index_col=0)
        data = data[data.columns[0]]
        result_dict[f'{ticker_type} Recent'] = data
    for ticker_type in ticker_type_list:
        strategy = ticker_strategy_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_from_2025/{strategy}_results.csv'
        data = pd.read_csv(data_path, encoding='gbk', index_col=0)
        data = data[data.columns[0]]
        result_dict[f'{ticker_type} 2025'] = data
    results = pd.concat(result_dict, axis=1)
    metrics = ['夏普比率', '年化收益', '最大回撤', '平均每天交易笔数', '每笔交易平均盈亏', '平均每笔市值收益', '平均持仓周期', '胜率', '盈亏收益比', '做多收益', '做空收益', '做多胜率', '做空胜率', '做多盈亏比', '做空盈亏比']
    results = results.loc[metrics]
    table = generate_table(results)
    elements.append(table)

    elements.append(Paragraph('Back Test Return', head_style))
    return_dict = {}
    for ticker_type in ticker_type_list:
        strategy = ticker_strategy_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_from_2025/{strategy}_daily_return.csv'
        data = pd.read_csv(data_path, parse_dates=['date'], index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(stats_date_list), fill_value=0)
        return_dict[ticker_type] = data
    daily_return = pd.concat(return_dict, axis=1)
    daily_return.index = daily_return.index.strftime('%Y-%m-%d').to_list()
    daily_return = pd.concat([daily_return, daily_return.sum(axis=0).to_frame(name='Total').T], axis=0)
    daily_return = daily_return.applymap(lambda x: f'{x:.5f}')
    table = generate_table(daily_return)
    elements.append(table)

    elements.append(PageBreak())

    for ticker_type in ticker_type_list:
        elements.append(Paragraph(f'Back Test Curve - {ticker_type}', head_style))

        # back test from 2025
        strategy = ticker_strategy_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_from_2025/{strategy}_daily_return.csv'
        data = pd.read_csv(data_path, parse_dates=['date'], index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2025), fill_value=0)
        cum_ret = data.cumsum()
        data_path = f'{data_root}/market_futures_volatility.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2025), fill_value=0)
        fut_vol = data.rolling(5, min_periods=1).mean()
        plot = generate_plot_with_shadow(cum_ret, fut_vol, title=f'[{ticker_type}] Cumulative Return & Futures Volatility')
        elements.append(plot)

        # long/short return
        strategy = ticker_strategy_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_from_2025/{strategy}_total_trade_detail.csv'
        data = pd.read_csv(data_path, parse_dates=['open_time', 'close_time'], index_col=0)
        long_trade = data[data['pos'] > 0]
        long_trade = long_trade[['close_time', 'change']].set_index('close_time')['change']
        long_cum_ret = long_trade.groupby(long_trade.index.date).sum()
        long_cum_ret.index = pd.to_datetime(long_cum_ret.index)
        long_cum_ret = long_cum_ret.reindex(pd.to_datetime(date_list_from_2025), fill_value=0)
        long_cum_ret = long_cum_ret.cumsum()
        short_trade = data[data['pos'] < 0]
        short_trade = short_trade[['close_time', 'change']].set_index('close_time')['change']
        short_cum_ret = short_trade.groupby(short_trade.index.date).sum()
        short_cum_ret.index = pd.to_datetime(short_cum_ret.index)
        short_cum_ret = short_cum_ret.reindex(pd.to_datetime(date_list_from_2025), fill_value=0)
        short_cum_ret = short_cum_ret.cumsum()
        ls_cum_ret = pd.concat({'long': long_cum_ret, 'short': short_cum_ret}, axis=1)
        plot = generate_plot_with_colors(ls_cum_ret, title=f'[{ticker_type}] Long/Short Return', color_list=[COLOR_L, COLOR_S])
        elements.append(plot)

        # model return
        cum_ret_dict = {}
        model_list = ticker_models_dict[ticker_type]
        for model in model_list:
            data_path = f'{track_root}/{model}/backtest_from_2025/{model}_daily_return.csv'
            data = pd.read_csv(data_path, parse_dates=['date'], index_col=0)
            data = data[data.columns[0]]
            data = data.reindex(pd.to_datetime(date_list_from_2025), fill_value=0)
            cum_ret = data.cumsum()
            cum_ret_dict[model] = cum_ret
        model_cum_ret = pd.concat(cum_ret_dict, axis=1)
        plot = generate_plot_with_colors(model_cum_ret, title=f'[{ticker_type}] Model Return', color_list=COLOR_LIST[:len(model_list)])
        elements.append(plot)

        # back test from 2021
        strategy = ticker_strategy_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_from_2021/{strategy}_daily_return.csv'
        data = pd.read_csv(data_path, parse_dates=['date'], index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2021), fill_value=0)
        cum_ret = data.cumsum()
        data_path = f'{data_root}/market_futures_volatility.xlsx'
        data = pd.read_excel(data_path, sheet_name=ticker_type, index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2021), fill_value=0)
        fut_vol = data.rolling(5, min_periods=1).mean()
        plot = generate_plot_with_shadow(cum_ret, fut_vol, title=f'[{ticker_type}] Cumulative Return & Futures Volatility')
        elements.append(plot)

        elements.append(PageBreak())

    for ticker_type in ticker_type_list:
        elements.append(Paragraph(f'Equal Weight Factors - {ticker_type}', head_style))

        # back test from 2025
        strategy = ticker_factor_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_from_2025/{strategy}_daily_return.csv'
        data = pd.read_csv(data_path, parse_dates=['date'], index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2025), fill_value=0)
        cum_ret = data.cumsum()
        plot = generate_plot(cum_ret, title=f'[{ticker_type}] Cumulative Return')
        elements.append(plot)

        # back test from 2021
        strategy = ticker_factor_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_from_2021/{strategy}_daily_return.csv'
        data = pd.read_csv(data_path, parse_dates=['date'], index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2021), fill_value=0)
        cum_ret = data.cumsum()
        cum_ret.name = 'profit'
        plot = generate_plot(cum_ret, title=f'[{ticker_type}] Cumulative Return')
        elements.append(plot)

        elements.append(Paragraph(f'Filtered Version - {ticker_type}', head_style))

        # back test from 2025
        strategy = ticker_strategy_filt_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_from_2025/{strategy}_daily_return.csv'
        data = pd.read_csv(data_path, parse_dates=['date'], index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2025), fill_value=0)
        cum_ret = data.cumsum()
        plot = generate_plot(cum_ret, title=f'[{ticker_type}] Cumulative Return')
        elements.append(plot)

        # back test from 2021
        strategy = ticker_strategy_filt_dict[ticker_type]
        data_path = f'{track_root}/{strategy}/backtest_from_2021/{strategy}_daily_return.csv'
        data = pd.read_csv(data_path, parse_dates=['date'], index_col=0)
        data = data[data.columns[0]]
        data = data.reindex(pd.to_datetime(date_list_from_2021), fill_value=0)
        cum_ret = data.cumsum()
        plot = generate_plot(cum_ret, title=f'[{ticker_type}] Cumulative Return')
        elements.append(plot)

        elements.append(PageBreak())

    # ****************************************************************************************************

    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.8 * inch, bottomMargin=0.8 * inch)
    doc.build(elements, onFirstPage=generate_first_page, onLaterPages=generate_later_pages)
    print(f'save to {output_path}', flush=True)

    # ****************************************************************************************************

    if ftplib_root is not None:
        ftp = ftplib.FTP('168.8.2.68')
        ftp.login('xquant', 'Xquant-32')
        ftp.cwd(ftplib_root)
        ftp.storbinary(f'STOR {os.path.split(output_path)[-1]}', open(output_path, 'rb'))
        ftp.quit()
        print(f'save to {ftplib_root}/{os.path.split(output_path)[-1]}', flush=True)
    return None


def get_market_statistics(data, str_date, end_date):
    value_list = []
    index_list = []
    recent_mean = data.loc[str_date:end_date].mean()
    value_list.append(recent_mean)
    index_list.append('近期均值')
    base = data.loc['2019':]
    recent_quantile = len(base[base <= recent_mean]) / len(base)
    value_list.append(recent_quantile)
    index_list.append('2019以来分位数')
    base = data.iloc[-120:]
    recent_quantile = len(base[base <= recent_mean]) / len(base)
    value_list.append(recent_quantile)
    index_list.append('近120日分位数')
    year_mean = data.loc['2025':'2025'].mean()
    value_list.append(year_mean)
    index_list.append('2025年均值')
    year_mean = data.loc['2024':'2024'].mean()
    value_list.append(year_mean)
    index_list.append('2024年均值')
    year_mean = data.loc['2023':'2023'].mean()
    value_list.append(year_mean)
    index_list.append('2023年均值')
    year_mean = data.loc['2022':'2022'].mean()
    value_list.append(year_mean)
    index_list.append('2022年均值')
    # year_mean = data.loc['2021':'2021'].mean()
    # value_list.append(year_mean)
    # index_list.append('2021年均值')
    stats = pd.Series(value_list, index=index_list)
    return stats


def get_stats(df, cnt):
    ret = df['change']
    trade_cnt = len(df)
    trade_ratio = trade_cnt / cnt if cnt > 0 else 0
    right_cnt = (ret > 0).sum()
    wrong_cnt = (ret < 0).sum()
    win_ratio = right_cnt / trade_cnt if trade_cnt > 0 else 0
    win_loss_ratio = abs(ret[ret > 0].mean() / ret[ret < 0].mean())
    cum_ret = ret.sum()
    hold_time = df['holding_time'].mean()
    trade_cnt = f'{trade_cnt}'
    right_cnt = f'{right_cnt}'
    wrong_cnt = f'{wrong_cnt}'
    win_ratio = f'{win_ratio * 100:.2f}%'
    win_loss_ratio = f'{win_loss_ratio:.2f}'
    cum_ret = f'{cum_ret * 100:.2f}%'
    hold_time = f'{hold_time:.2f}'
    trade_ratio = f'{trade_ratio * 100:.2f}%'
    output = pd.Series([trade_cnt, right_cnt, wrong_cnt, win_ratio, win_loss_ratio, cum_ret, hold_time, trade_ratio],
                       index=['交易笔数', '正确笔数', '错误笔数', '胜率', '盈亏比', '累积收益', '持仓时间', '交易占比'])
    return output


def get_trade_stats(total_trade):
    stats = {}
    total_cnt = len(total_trade)
    stats['全部交易'] = get_stats(total_trade, total_cnt)
    long_trade = total_trade[total_trade['pos'] > 0]
    stats['做多交易'] = get_stats(long_trade, total_cnt)
    short_trade = total_trade[total_trade['pos'] < 0]
    stats['做空交易'] = get_stats(short_trade, total_cnt)
    stats = pd.DataFrame(stats)
    return stats


def generate_first_page(canvas, document):
    canvas.saveState()
    canvas.restoreState()
    return None


def generate_later_pages(canvas, document):
    canvas.saveState()
    canvas.setFont(psfontname='STSong-Light', size=6)
    canvas.restoreState()
    return None


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


def generate_table(df, head=''):
    df_list = df2list(df, head)
    table = Table(df_list)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('BOX', (0, 0), (-1, -1), 0.4, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.2, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),
    ]))
    return table


def get_mean_line(x):
    assert isinstance(x, pd.Series) or isinstance(x, pd.DataFrame)
    line = np.nanmean(x.values, axis=0, keepdims=True).repeat(len(x), axis=0)
    if isinstance(x, pd.Series):
        line = pd.Series(line, index=x.index, name=x.name)
    else:
        line = pd.DataFrame(line, index=x.index, columns=x.columns)
    return line


def get_median_line(x):
    assert isinstance(x, pd.Series) or isinstance(x, pd.DataFrame)
    line = np.nanmedian(x.values, axis=0, keepdims=True).repeat(len(x), axis=0)
    if isinstance(x, pd.Series):
        line = pd.Series(line, index=x.index, name=x.name)
    else:
        line = pd.DataFrame(line, index=x.index, columns=x.columns)
    return line


def generate_plot(data, title):
    assert isinstance(data, pd.Series)
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    ax.plot(data, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    ax.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(labelsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_plot_with_mean_line(data, title):
    assert isinstance(data, pd.Series)
    line = get_mean_line(data)
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    ax.plot(data, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    ax.plot(line, color=MAIN_COLOR, linewidth=LINE_WIDTH * 0.8, linestyle='--')
    ax.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(labelsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_plot_with_median_line(data, title):
    assert isinstance(data, pd.Series)
    line = get_median_line(data)
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    ax.plot(data, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    ax.plot(line, color=MAIN_COLOR, linewidth=LINE_WIDTH * 0.8, linestyle='--')
    ax.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(labelsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


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
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_plot_with_colors_and_styles(data, title, color_list, style_list, legend_loc='upper left'):
    assert isinstance(data, pd.DataFrame)
    assert data.shape[1] == len(color_list)
    assert data.shape[1] == len(style_list)
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    for col, color, style in zip(data.columns, color_list, style_list):
        ax.plot(data[col], label=col, color=color, linestyle=style, linewidth=LINE_WIDTH)
    ax.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(labelsize=TICKS_FONT_SIZE)
    ax.legend(fontsize=TICKS_FONT_SIZE, loc=legend_loc, framealpha=1.0)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_plot_with_colors_and_values(data, title, color_list, value_type=None, legend_loc='upper left'):
    assert isinstance(data, pd.DataFrame)
    assert data.shape[1] == len(color_list)
    data.index = data.index.strftime('%Y-%m-%d')
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    for col, color in zip(data.columns, color_list):
        ax.plot(data[col], label=col, color=color, linewidth=LINE_WIDTH, marker='o', markersize=MARKER_SIZE)
    for col in data.columns:
        for x, y in zip(data.index, data[col].values):
            if value_type == 'int':
                ax.text(x, y, f'{int(y):,}', va='bottom', ha='center', fontsize=TICKS_FONT_SIZE)
            elif value_type == 'float5':
                ax.text(x, y, f'{y:.5f}', va='bottom', ha='center', fontsize=TICKS_FONT_SIZE)
            else:
                ax.text(x, y, y, va='bottom', ha='center', fontsize=TICKS_FONT_SIZE)
    ax.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(labelsize=TICKS_FONT_SIZE)
    ax.legend(fontsize=TICKS_FONT_SIZE, loc=legend_loc, framealpha=1.0)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_stackplot_with_values(data, title, color_list, value_type=None, legend_loc='upper left'):
    assert isinstance(data, pd.DataFrame)
    assert data.shape[1] == len(color_list)
    data.index = data.index.strftime('%Y-%m-%d')
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    data_list = [val for col, val in data.items()]
    ax.stackplot(data.index, data_list, labels=data.columns, colors=color_list, linewidth=0)
    temp = data.cumsum(axis=1)
    for col in data.columns:
        for x, y, z in zip(data.index, temp[col].values, data[col].values):
            if value_type == 'int':
                ax.text(x, y, f'{int(z):,}', va='bottom', ha='center', fontsize=TICKS_FONT_SIZE)
            else:
                ax.text(x, y, z, va='bottom', ha='center', fontsize=TICKS_FONT_SIZE)
    ax.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(labelsize=TICKS_FONT_SIZE)
    ax.legend(fontsize=TICKS_FONT_SIZE, loc=legend_loc, framealpha=1.0)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_plot_1x2(data1, data2, title):
    assert isinstance(data1, pd.Series)
    assert isinstance(data2, pd.Series)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    ax1.plot(data1, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    ax1.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax1.tick_params(labelsize=TICKS_FONT_SIZE)
    ax2.plot(data2, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    ax2.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax2.tick_params(labelsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_plot_with_colors_1x2(data1, data2, title, color_list, legend_loc='upper left'):
    assert isinstance(data1, pd.DataFrame)
    assert isinstance(data2, pd.DataFrame)
    assert data1.shape[1] == len(color_list)
    assert data2.shape[1] == len(color_list)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    for col, color in zip(data1.columns, color_list):
        ax1.plot(data1[col], label=col, color=color, linewidth=LINE_WIDTH)
    ax1.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax1.tick_params(labelsize=TICKS_FONT_SIZE)
    ax1.legend(fontsize=TICKS_FONT_SIZE, loc=legend_loc, framealpha=1.0)
    for col, color in zip(data2.columns, color_list):
        ax2.plot(data2[col], label=col, color=color, linewidth=LINE_WIDTH)
    ax2.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax2.tick_params(labelsize=TICKS_FONT_SIZE)
    ax2.legend(fontsize=TICKS_FONT_SIZE, loc=legend_loc, framealpha=1.0)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


def generate_plot_from_image(image):
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT2 * 3))
    ax.imshow(image)
    ax.set_axis_off()
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT2 * inch)


def generate_plot_with_shadow(data, fill, title):
    assert isinstance(data, pd.Series)
    assert isinstance(fill, pd.Series)
    zeros = pd.Series(np.zeros_like(fill.values), index=fill.index)
    fig, ax1 = plt.subplots(figsize=(PLOT_WIDTH * 3, PLOT_HEIGHT * 3))
    ax1.fill_between(zeros.index, zeros, fill, facecolor=FILL_COLOR, alpha=0.5)
    ax2 = ax1.twinx()
    ax2.plot(data, color=MAIN_COLOR, linewidth=LINE_WIDTH)
    ax2.grid()
    ax1.yaxis.tick_right()
    ax2.yaxis.tick_left()
    ax1.set_title(title, fontsize=TITLE_FONT_SIZE)
    ax1.tick_params(labelsize=TICKS_FONT_SIZE)
    ax2.tick_params(labelsize=TICKS_FONT_SIZE)
    plt.tight_layout()
    img = BytesIO()
    fig.savefig(img, format='jpg')
    img.seek(0)
    return Image(img, width=PLOT_WIDTH * inch, height=PLOT_HEIGHT * inch)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    main()
