# coding: utf-8
# Author：fengchi863
# Date ：2022/3/17 14:10

from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from SimiStock.dataApi import getData, tradeDate
import pandas as pd
import numpy as np


def get_future120_pctchg(stk_id, trade_date, close_badj):
    start_date = trade_date
    try:
        end_date = tradeDate.get_pre_trade_date(trade_date, -120)
    except:
        end_date = tradeDate.get_today()
    today = tradeDate.get_today()
    if end_date >= today:
        end_date = tradeDate.get_pre_trade_date(tradeDate.get_today(), 1)
    return close_badj.loc[end_date, stk_id] / close_badj.loc[start_date, stk_id] - 1


if __name__ == '__main__':
    block_data = pd.read_pickle(data_path + 'raw_block_data2.pkl')
    date_list = tradeDate.get_date_range(20180101)
    close_badj = getData.get_daily_1factor('close_badj', date_list=date_list)
    block_data = block_data.query('20180101 <= 交易日期 <= 20211231')
    # block_data['future120_pctchg'] = block_data[['交易日期', '股票代码']].apply(lambda x:
    #                     get_future120_pctchg(x['股票代码'], x['交易日期'], close_badj), axis=1)
    # block_data.to_pickle(data_path + 'raw_block_data2.pkl')

    ret_df1 = pd.DataFrame()
    ret_df2 = pd.DataFrame()
    ret_df3 = pd.DataFrame()
    ret_df4 = pd.DataFrame()
    ret_df5 = pd.DataFrame()
    ret_df6 = pd.DataFrame()
    disc_list = [1.5, 1, 0.95, 0.9, 0.85, 0.8]
    # 统计全部样本

    print('大宗数量：', len(block_data))
    print('大宗涉及个股数量：', len(set(block_data['股票代码'])))
    for disc in disc_list:
        tmp = block_data[block_data['折价比例'] <= disc]
        index1 = f'折价小于{disc}'
        ret_df1.loc[index1, '比例'] = len(tmp) / np.isfinite(block_data['折价比例']).sum()
        ret_df1.loc[index1, '未来120天涨跌幅均值'] = tmp['future120_pctchg'].mean()
        ret_df1.loc[index1, '未来120天涨跌幅中位数'] = tmp['future120_pctchg'].median()

    for idx in range(1, len(disc_list)):
        high = disc_list[idx-1]
        low = disc_list[idx]
        tmp = block_data.query(f'{low} < 折价比例 <= {high}')
        index1 = f'折价位于({low},{high})'
        ret_df1.loc[index1, '比例'] = len(tmp) / np.isfinite(block_data['折价比例']).sum()
        ret_df1.loc[index1, '未来120天涨跌幅均值'] = tmp['future120_pctchg'].mean()
        ret_df1.loc[index1, '未来120天涨跌幅中位数'] = tmp['future120_pctchg'].median()

    # 分半年度统计样本
    trade_year_dict = {
        '2018': [20180103, 20181228],
        '2019': [20181228, 20191231],
        '2020': [20191231, 20201231],
        '2021': [20201231, 20211231]
    }
    for year in trade_year_dict:
        start_date, end_date = trade_year_dict[year]
        year_data = block_data.query(f'{start_date} <= 交易日期 <= {end_date}')
        # df = year_data.groupby(['股票代码']).count()
        index1 = year
        ret_df2.loc[year, '大宗涉及个股数量'] = len(set(year_data['股票代码']))
        for disc in disc_list:
            index2 = f'折价小于{disc}'
            tmp = year_data[year_data['折价比例'] < disc]
            ret_df2.loc[year, f'{index2}比例'] = len(tmp) / np.isfinite(year_data['折价比例']).sum()
            ret_df2.loc[year, f'{index2}未来120天涨跌幅均值'] = tmp['future120_pctchg'].mean()
            ret_df2.loc[year, f'{index2}未来120天涨跌幅中位数'] = tmp['future120_pctchg'].median()
            ret_df2.loc[year, f'{index2}大宗涉及个股数量'] = len(set(tmp['股票代码']))

        for idx in range(1, len(disc_list)):
            high = disc_list[idx - 1]
            low = disc_list[idx]
            tmp = block_data.query(f'{low} < 折价比例 <= {high}')
            index = f'折价位于({low},{high})'
            ret_df2.loc[year, f'{index}比例'] = len(tmp) / np.isfinite(block_data['折价比例']).sum()
            ret_df2.loc[year, f'{index}未来120天涨跌幅均值'] = tmp['future120_pctchg'].mean()
            ret_df2.loc[year, f'{index}未来120天涨跌幅中位数'] = tmp['future120_pctchg'].median()
            ret_df2.loc[year, f'{index}大宗涉及个股数量'] = len(set(tmp['股票代码']))

    count_list = [100, 15, 10, 3, 1]
    for year in trade_year_dict:
        start_date, end_date = trade_year_dict[year]
        year_data = block_data.query(f'{start_date} <= 交易日期 <= {end_date}')
        groupby_data_all = year_data.groupby(['股票代码']).agg(['count', 'mean'])
        for jj in range(1, len(count_list)):
            j_high = count_list[jj - 1]
            j_low = count_list[jj]
            groupby_data = groupby_data_all[(groupby_data_all['交易日期', 'count'] > j_low) &
                                            (groupby_data_all['交易日期', 'count'] <= j_high)]
            index1 = f'天数在({j_low},{j_high})'
            for disc in disc_list:
                index2 = f'折价小于{disc}'
                tmp = groupby_data[groupby_data['折价比例', 'mean'] < disc]
                ret_df3.loc[year, f'{index1}{index2}比例'] = len(tmp) / np.isfinite(groupby_data['折价比例', 'mean']).sum()
                ret_df3.loc[year, f'{index1}{index2}未来120天涨跌幅均值'] = tmp['future120_pctchg', 'mean'].mean()
                ret_df3.loc[year, f'{index1}{index2}未来120天涨跌幅中位数'] = tmp['future120_pctchg', 'mean'].median()

            for idx in range(1, len(disc_list)):
                high = disc_list[idx - 1]
                low = disc_list[idx]
                tmp = groupby_data[(groupby_data['折价比例', 'mean'] <= high) &
                                   (groupby_data['折价比例', 'mean'] > low)]
                index2 = f'折价位于({low},{high})'

                ret_df3.loc[year, f'{index1}{index2}比例'] = len(tmp) / np.isfinite(groupby_data['折价比例', 'mean']).sum()
                ret_df3.loc[year, f'{index1}{index2}未来120天涨跌幅均值'] = tmp['future120_pctchg', 'mean'].mean()
                ret_df3.loc[year, f'{index1}{index2}未来120天涨跌幅中位数'] = tmp['future120_pctchg', 'mean'].median()

    block_data['年份'] = block_data['交易日期'].apply(lambda x: x // 10000)
    for year in [2018, 2019, 2020, 2021]:
        tmp = block_data.query(f'年份 == {year}')
        ret_df4.loc[year, '总样本数'] = len(tmp)
        ret_df4.loc[year, '涉及股票样本数'] = len(set(tmp['股票代码']))
        ret_df4.loc[year, '平均折价率'] = tmp['折价比例'].mean()
        ret_df4.loc[year, '折价比例: >=1'] = len(tmp.query('折价比例 >= 1')) / len(tmp)
        ret_df4.loc[year, '折价比例: [0.95, 1)'] = len(tmp.query('0.95 <= 折价比例 < 1')) / len(tmp)
        ret_df4.loc[year, '折价比例: [0.9, 0.95)'] = len(tmp.query('0.9 <= 折价比例 < 0.95')) / len(tmp)
        ret_df4.loc[year, '折价比例: [0.85, 0.9)'] = len(tmp.query('0.85 <= 折价比例 < 0.9')) / len(tmp)
        ret_df4.loc[year, '折价比例: <0.85'] = len(tmp.query('折价比例 < 0.85')) / len(tmp)

    for year in [2018, 2019, 2020, 2021]:
        tmp = block_data.query(f'年份 == {year}')
        ret_df5.loc[year, '折价比例: >=1'] = tmp.query('折价比例 >= 1')['future120_pctchg'].median()
        ret_df5.loc[year, '折价比例: [0.95, 1)'] = tmp.query('0.95 <= 折价比例 < 1')['future120_pctchg'].median()
        ret_df5.loc[year, '折价比例: [0.9, 0.95)'] = tmp.query('0.9 <= 折价比例 < 0.95')['future120_pctchg'].median()
        ret_df5.loc[year, '折价比例: [0.85, 0.9)'] = tmp.query('0.85 <= 折价比例 < 0.9')['future120_pctchg'].median()
        ret_df5.loc[year, '折价比例: <0.85'] = tmp.query('折价比例 < 0.85')['future120_pctchg'].median()

    for year in [2018, 2019, 2020, 2021]:
        tmp = block_data.query(f'年份 == {year}')
        group_data = tmp.groupby(['股票代码']).agg({'折价比例': ['count', 'mean'],
                                                'future120_pctchg': 'mean'})
        for jj in range(1, len(count_list)):
            j_high = count_list[jj - 1]
            j_low = count_list[jj]
            groupby_data = group_data[(group_data['折价比例', 'count'] > j_low) &
                                      (group_data['折价比例', 'count'] <= j_high)]
            index = f'大宗天数({j_low}, {j_high})'
            ret_df6.loc[year, f'{index}平均折价率'] = groupby_data['折价比例', 'mean'].mean()
            ret_df6.loc[year, f'{index}平均收益率'] = groupby_data['future120_pctchg', 'mean'].median()

    ret_dict = {'总体': ret_df1,
                '分年度': ret_df2,
                '分数量': ret_df3,
                '汇总表': ret_df4,
                '涨跌中位值': ret_df5,
                '按天数': ret_df6
                }
    util.save_dict2xls(ret_dict, bt_summary_path, '大宗统计.xlsx')

