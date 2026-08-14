# coding: utf-8
# Author：fengchi863
# Date ：2023/10/9 22:28
import sys
sys.path.append('/data/user/015614/fcfactor')
sys.path.append('/data/user/015614/Lucien')

import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from dataApi import tradeDate
from MixedWork.GreyStockGenerator import IO

s = FactorData()
from tqdm import tqdm

date_list = tradeDate.get_date_range(20200701, 20211231)
path_user = '/data/user/015614/daily/灰名单生成/异常波动历史测试/'

def excel_saver(output_dict, excel_name, index):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key, index=index)
    writer.save()
    return


def cal_return(data):
    x = data[np.isnan(data) == False]
    return x[~0] / x[0] - 1


def cal_largest_return(data):
    x = data[np.isnan(data) == False]
    return x[~0] / x.min() - 1


def fun_append_next_tradingday(factor_df):
    # 实盘中需要在T日开盘之前取到T-1日的因子，为了shift之后能有T日的时间戳，所以先把T日的时间戳加上去，取历史数据则没有该问题
    factor_df_unstack = factor_df.unstack()
    last_timestamp = factor_df_unstack.index[-1]
    next_tradingday_timestamp = pd.Timestamp(s.tradingday(last_timestamp.strftime('%Y%m%d'), 2)[-1])
    next_tradingday_df = pd.DataFrame(np.zeros((1, factor_df_unstack.shape[1])), columns=factor_df_unstack.columns,
                                      index=[next_tradingday_timestamp])
    factor_df = (factor_df_unstack.append(next_tradingday_df)).stack()
    factor_df.index.names = ['dt', 'Ticker']
    return factor_df

def basic_sample_out_nice(data_in):
    data_in_temp = data_in.reset_index()
    data_in_temp['dt'] = data_in_temp['dt'].apply(lambda x: x.strftime('%Y-%m-%d'))
    return data_in_temp

def wrapper(dat_list):
    for _dat in tqdm(dat_list):
        try:
            rolling_period = 1
            # nowdate = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
            nowdate = str(_dat)
            nextdate = nowdate
            date = s.tradingday(nextdate, -2)[0]
            lastdate = s.tradingday(date, -2)[0]

            f_data = IO.read_data([s.tradingday(date, -50)[0], date], columns=['close', 'adjfactor'],
                                  alt='/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
            close_adj = f_data['close'] * f_data['adjfactor']

            # 5日、7日、10日、40日涨跌幅
            # Ret_5 = pd.DataFrame(close_adj.unstack().rolling(6, 6).apply(cal_return).stack(), columns=['Ret_5']).reindex(
            #     f_data.index)
            # Ret_7 = pd.DataFrame(close_adj.unstack().rolling(8, 8).apply(cal_return).stack(), columns=['Ret_7']).reindex(
            #     f_data.index)
            # Ret_10 = pd.DataFrame(close_adj.unstack().rolling(11, 11).apply(cal_return).stack(), columns=['Ret_10']).reindex(
            #     f_data.index)
            Ret_40 = pd.DataFrame(close_adj.unstack().rolling(41, 41).apply(cal_return).stack(), columns=['Ret_40']).reindex(
                f_data.index)
            Ret_10_largest = pd.DataFrame(close_adj.unstack().rolling(11, 11).apply(cal_largest_return).stack(),
                                          columns=['Ret_10_largest']).reindex(f_data.index)

            MD_data = IO.read_data([s.tradingday(str(date), -300)[0], date],
                                   columns=['pre_close', 'open', 'close', 'high', 'low', 'adjfactor', 'amt', 'volume'],
                                   alt='/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
            # 计算股票的上市时间长度
            ipo_data = IO.read_data([20000101, 20990101],
                                    alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')
            ipo_data = ipo_data.rename(columns={'S_INFO_LISTDATE': 'list_date', 'S_INFO_CODE': 'code'})
            ipo_data = ipo_data.reset_index()
            ipo_data = ipo_data[ipo_data['code'].apply(lambda x: x[:2] in ['60', '30', '00'])]  # 筛选上交所和深交所股票，不包括科创板
            ipo_data = ipo_data[~ipo_data['list_date'].isnull()]  # 去掉没有上市日期的股票，包括IPO终止和还未上市的股票
            ipo_data['list_date'] = ipo_data['list_date'].apply(lambda x: pd.Timestamp(str(int(x))))
            ipo_data['dt'] = ipo_data['list_date']
            ipo_data['is_list_date'] = True
            ipo_data = ipo_data.set_index(['dt', 'Ticker'])[['is_list_date']]

            md_df = MD_data.copy()
            md_df = md_df.join(ipo_data)
            md_df['after_list'] = md_df['is_list_date'].unstack().fillna(method='ffill').stack()  # 上市后的标记
            md_df.loc[md_df['amt'] == 0]['after_list'] = np.nan
            md_df['list_len'] = md_df['after_list'].unstack().rolling(10000000, 1).sum().stack()
            md_df.loc[(md_df['list_len'].isnull() & (md_df['amt'] > 0)), 'list_len'] = 250  # sss：大部分股票上市日期小于md的起始日期，导致为空，直接填充250
            md_df['list_len'] = md_df['list_len'].unstack().fillna(method='ffill').stack()
            # list_len和after_not_ul_len要加1
            md_df['list_len'] = md_df['list_len'] + 1  # TODO:这里为什么加1
            md_df.loc[(md_df['list_len'] > 250), 'list_len'] = 250
            md_df['1_1_ul_price'] = (md_df['pre_close'] * 100 * 1.1 + 0.5).apply(np.floor) / 100  # 正常的涨停价
            md_df['1_44_ul_price'] = (md_df['pre_close'] * 100 * 1.44 + 0.5).apply(np.floor) / 100  # 首日的涨停价
            md_df['is_one_ul'] = np.nan
            md_df.loc[md_df['amt'] > 0, 'is_one_ul'] = 0  # 有交易的变为0
            md_df.loc[(md_df['is_list_date'] & (md_df['close'] == md_df['1_44_ul_price'])), 'is_one_ul'] = 2  # 第一天涨停变为2
            md_df.loc[(md_df['open'] == md_df['close']) & (md_df['high'] == md_df['low']) & (
                        md_df['close'] == md_df['1_1_ul_price']), 'is_one_ul'] = 1  # 正常一字板变为1
            md_df['is_list_ul'] = (md_df['is_one_ul'].unstack().rolling(10000, 1).mean() > 1).stack()
            md_df['is_list_ul'] = md_df['is_list_ul'] == True
            md_df['first_not_ul'] = ((md_df['is_list_ul'].unstack().shift(1).stack() == True) & (md_df['is_list_ul'] == False) |
                                     (md_df['is_list_date'] & (md_df['is_list_ul'] == False)))  # 前日是上市涨停，当日不涨停; 或者上市首日开板
            md_df.loc[md_df['first_not_ul'] != True, 'first_not_ul'] = np.nan

            md_df['after_first_not_ul'] = md_df['first_not_ul'].unstack().fillna(method='ffill').stack()  # 上市后的标记
            md_df.loc[md_df['amt'] == 0]['after_first_not_ul'] = np.nan
            md_df['after_not_ul_len'] = md_df['after_first_not_ul'].unstack().rolling(10000000, 1).sum().stack()
            md_df.loc[(md_df['after_not_ul_len'].isnull() & (md_df['amt'] > 0) & (md_df['is_list_ul'] == False)), 'after_not_ul_len'] = 200
            md_df['after_not_ul_len'] = md_df['after_not_ul_len'].unstack().fillna(method='ffill').stack()
            # list_len和after_not_ul_len要加1
            md_df['after_not_ul_len'] = md_df['after_not_ul_len'] + 1
            md_df.loc[(md_df['after_not_ul_len'] > 200), 'after_not_ul_len'] = 200

            all_sample = list(f_data['close'].unstack().columns)

            from xquant.textdata import NewsData

            nd = NewsData()
            ycbd_tot = pd.DataFrame(columns=['dt', 'Ticker', 'id', 'ycbd_indicator']).set_index(['dt', 'Ticker'])
            jyfxts_tot = pd.DataFrame(columns=['dt', 'Ticker', 'id', 'jyfxts_indicator']).set_index(['dt', 'Ticker'])
            for stock in all_sample:
                print(stock)
                data_info = nd.getNewsInfoByStockCode(stock[:~2])
                # data_info = data_info[data_info['textcategory'].apply(lambda x: x not in [303604, 303605, 303606, 303607, 303608, 303609, 303610, 303611, 303612, 303613, 303614,303615])]
                data_info = data_info[data_info['textcategory'].astype('str').str.startswith('2')]
                if len(data_info) == 0:
                    continue

                data_info = data_info.rename(columns={'pubdate': 'dt'})
                data_info['Ticker'] = stock
                data_info = data_info.reset_index().set_index(['dt', 'Ticker']).sort_index()
                data_info = data_info[data_info['texttitle'].apply(lambda x: x != None)]

                if len(data_info) != 0:
                    data_info = data_info.loc[pd.Timestamp(s.tradingday(date, -30)[0]):, ]
                    ycbd_warning = data_info[['id', 'texttitle']][
                        data_info['texttitle'].apply(lambda x: (('异常波动' in x) | ('异动' in x)) & ('回复' not in x) & \
                                                               ('回复函' not in x) & ('复函' not in x) & \
                                                               ('回函' not in x) & ('补充' not in x) & ('说明' not in x) & ('海外' not in x))]
                    ycbd_warning['ycbd_indicator'] = 1
                    jyfxts_warning = data_info[['id', 'texttitle']][
                        data_info['texttitle'].apply(lambda x: ('风险' in x) & ('回复' not in x) & \
                                                               ('回复函' not in x) & ('复函' not in x) & \
                                                               ('回函' not in x))]
                    jyfxts_warning['jyfxts_indicator'] = 1
                    if len(ycbd_warning) != 0:
                        ycbd_tot = pd.concat([ycbd_tot, ycbd_warning[['id', 'ycbd_indicator']]])
                    if len(jyfxts_warning) != 0:
                        for index, row in jyfxts_warning.iterrows():
                            tt = row['texttitle']
                            id = row['id']
                            newsBody = nd.getNewsBody([str(id)])
                            if len(newsBody) == 0:
                                jyfxts_warning.loc[index, 'jyfxts_indicator'] = 0
                            else:
                                if ('交易风险' in tt) & ('撤销' not in tt):
                                    jyfxts_warning.loc[index, 'jyfxts_indicator'] = 1
                                else:
                                    newsBody = newsBody.reset_index()['newsBody'].loc[0]
                                    if ('交易' in newsBody) & (('涨停' in newsBody) | ('偏离' in newsBody)):
                                        jyfxts_warning.loc[index, 'jyfxts_indicator'] = 1
                                    else:
                                        jyfxts_warning.loc[index, 'jyfxts_indicator'] = 0
                        jyfxts_warning = jyfxts_warning[jyfxts_warning['jyfxts_indicator'] == 1]
                        jyfxts_tot = pd.concat([jyfxts_tot, jyfxts_warning[['id', 'jyfxts_indicator']]])
            ycbd_tot = ycbd_tot.reset_index()
            ycbd_tot['dt_old'] = ycbd_tot['dt']
            ycbd_tot['dt'] = ycbd_tot['dt'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
            ycbd_tot = ycbd_tot.set_index(['dt', 'Ticker']).sort_index()
            ycbd_tot = ycbd_tot.loc[~ycbd_tot.index.duplicated(keep='first')].sort_index()

            jyfxts_tot = jyfxts_tot.reset_index()
            jyfxts_tot['dt_old'] = jyfxts_tot['dt']
            jyfxts_tot['dt'] = jyfxts_tot['dt'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
            jyfxts_tot = jyfxts_tot.set_index(['dt', 'Ticker']).sort_index()
            jyfxts_tot = jyfxts_tot.loc[~jyfxts_tot.index.duplicated(keep='first')].sort_index()

            all_index = fun_append_next_tradingday(f_data).index
            # 1、条件一（新加的条件）
            ycbd_20 = ycbd_tot['ycbd_indicator'].reindex(all_index).unstack().fillna(0).rolling(20, 20).sum().stack()
            jyfxts_20 = jyfxts_tot['jyfxts_indicator'].reindex(all_index).unstack().fillna(0).rolling(20, 20).sum().stack()
            ret_40_next = fun_append_next_tradingday(Ret_40['Ret_40']).unstack().shift().stack()
            joined_condition_1 = (ret_40_next >= 1.5) & ((ycbd_20 + jyfxts_20) >= 1)
            joined_condition_1_need = joined_condition_1[joined_condition_1].loc[nowdate]

            # 2、条件二（原本的条件）
            ycbd_10 = ycbd_tot['ycbd_indicator'].reindex(all_index).unstack().fillna(0).rolling(10, 10).sum().stack()
            jyfxts_10 = jyfxts_tot['jyfxts_indicator'].reindex(all_index).unstack().fillna(0).rolling(10, 10).sum().stack()
            ret_largest_10_next = fun_append_next_tradingday(Ret_10_largest['Ret_10_largest']).unstack().shift().stack()
            joined_condition = (ret_largest_10_next >= 0.3) & ((ycbd_10 + jyfxts_10) >= 1)

            joined_condition_notice_date = pd.DataFrame(joined_condition).copy()
            joined_condition_notice_date['dt_dummy'] = joined_condition.reset_index()['dt'].values
            date_covered_dummy = ret_largest_10_next.unstack().index

            joined_condition_5_days = joined_condition.astype(float).unstack().fillna(0).rolling(rolling_period,
                                                                                                 rolling_period).sum()
            joined_condition_5_days_fulfilled = (joined_condition_5_days >= 1).stack().loc[nextdate]
            joined_condition_5_days_fulfilled = pd.DataFrame(joined_condition_5_days_fulfilled[joined_condition_5_days_fulfilled],
                                                             columns=['banned_indicator'])
            joined_condition_5_days_fulfilled['异常波动公告数'] = ycbd_10.reindex(joined_condition_5_days_fulfilled.index).fillna(0)
            joined_condition_5_days_fulfilled['风险提示公告数'] = jyfxts_10.reindex(joined_condition_5_days_fulfilled.index).fillna(0)
            joined_condition_5_days_fulfilled['10日最大涨幅'] = ret_largest_10_next.reindex(joined_condition_5_days_fulfilled.index)
            joined_condition_5_days_fulfilled['上一个提示日期'] = joined_condition_notice_date[joined_condition_notice_date[0]][
                'dt_dummy'].unstack(). \
                reindex(date_covered_dummy).fillna(method='ffill').stack().reindex(joined_condition_5_days_fulfilled.index)
            joined_condition_5_days_fulfilled['上一个提示日期'] = joined_condition_5_days_fulfilled['上一个提示日期'].apply(
                lambda x: x.strftime('%m%d'))
            joined_condition_5_days_fulfilled['公告总数'] = joined_condition_5_days_fulfilled['异常波动公告数'] + \
                                                        joined_condition_5_days_fulfilled['风险提示公告数']
            f_data1 = IO.read_data([lastdate, lastdate],
                                   alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
            joined_condition_5_days_fulfilled = pd.concat([joined_condition_5_days_fulfilled, joined_condition_1_need])
            joined_condition_5_days_fulfilled = joined_condition_5_days_fulfilled[
                ~joined_condition_5_days_fulfilled.index.duplicated(keep='first')]
            joined_condition_5_days_fulfilled['证券名称'] = np.nan
            for index, row in joined_condition_5_days_fulfilled.iterrows():
                if (str(lastdate), row.name[1]) in f_data1.index:
                    joined_condition_5_days_fulfilled.loc[index, '证券名称'] = \
                        f_data1.loc[str(lastdate), row.name[1]]['STOCK_NAME'].values[0]
            joined_condition_5_days_fulfilled['证券名称'] = joined_condition_5_days_fulfilled['证券名称'].astype(str)

            after_not_ul_len = fun_append_next_tradingday(md_df['after_not_ul_len'].loc[date]).unstack().shift().stack().loc[nextdate] \
                .reindex(joined_condition_5_days_fulfilled.index)
            joined_condition_5_days_fulfilled['after_not_ul_len'] = after_not_ul_len
            joined_condition_5_days_fulfilled = joined_condition_5_days_fulfilled[joined_condition_5_days_fulfilled['after_not_ul_len'] > 10]
            joined_condition_5_days_fulfilled = joined_condition_5_days_fulfilled.sort_values(by='公告总数', ascending=False)

            # 加入备查列表
            data = joined_condition_5_days_fulfilled.copy()
            out = data.reset_index().rename(columns={'Ticker': '证券代码'})
            out['证券代码'] = out['证券代码'].apply(lambda x: x[:~2])
            out = out[['证券名称', '证券代码', '异常波动公告数', '风险提示公告数', '10日最大涨幅', '上一个提示日期', '公告总数', 'after_not_ul_len']]

            out2 = pd.DataFrame(index=all_index)
            out2['ycbd_20'] = ycbd_20
            out2['jyfxts_20'] = jyfxts_20
            out2['ycbd_10'] = ycbd_10
            out2['jyfxts_10'] = jyfxts_10
            out2['20'] = out2['ycbd_20'] + out2['jyfxts_20']
            out2['10'] = out2['ycbd_10'] + out2['jyfxts_10']
            out2 = out2[out2['20'] > 0].loc[nextdate]
            out2 = out2.sort_values('10', ascending=False).reset_index().drop(columns=['dt', '20', '10'])

            excel_saver({'Sheet1': out,
                         '备选检查': out2},
                        path_user + 'abnormal_notice_list_%s.xlsx' % nextdate, index=False)
        except Exception as e:
            pd.DataFrame().to_excel(path_user + 'abnormal_notice_list_%s_error.xlsx' % nextdate)

from LucienUtil.SpeedUtil import SpeedUtil
# wrapper([20210304])
import os
file_list = os.listdir('/data/user/015614/daily/灰名单生成/异常波动历史测试/')
file_list = list(filter(lambda x: len(x) == 34, file_list))
exist_date_list = list(map(lambda x: int(x[-13:-5]), file_list))
date_list = list(set(date_list).difference(set(exist_date_list)))
SpeedUtil.multiprocess(24, wrapper, date_list)