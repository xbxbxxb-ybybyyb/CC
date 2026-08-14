# coding: utf-8
# Author：fengchi863
# Date ：2023/7/12 15:14

import pandas as pd
import numpy as np
import re
import datetime as dt
from dataApi.sendInfo import send_file
from xquant.marketdata import MarketData
mdp = MarketData()

def getValueByKeyFromLine(line, by, form='(.*?)[,\n]'):
    """给java日志使用，或者cpp日志使用"""
    if by not in line:
        return ''
    try:
        return re.findall(r"%s=%s" % (by, form), line)[0]
    except:
        return 'other'

def calc_time_interval(time1, time2):
    # time1 被减数  time2 减数  time1-time2
    if time1 > time2:
        return (time1 - time2).seconds + (time1 - time2).microseconds / 1e6
    else:
        return -((time2 - time1).seconds + (time2 - time1).microseconds / 1e6)

profit_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'
end_date = 20230711

europa_fpath = profit_path + 'Europa成交记录-20230711.xlsx'
log_path = '/data/group/800463/日内强势股/log_parse/日志拆分/'

zb_info_fpath = '/data/user/018107/share_file/for_fc/europa_ul_time_20220518_20230528.pkl'
zb_info = pd.read_pickle(zb_info_fpath)

europa_record = pd.read_excel(europa_fpath, sheet_name='累计卖出明细').query('是否全部卖出 == 1 &  "2022-05-18" <= 买入日期 <= "2023-05-18"')
pattern2_samples = europa_record.query('买入时形态 == 2')
pattern3_samples = europa_record.query('买入时形态 == 3')
pattern23_samples = europa_record.query('买入时形态 == 2 | 买入时形态 == 3')


for idx in range(len(pattern23_samples)):
    row = pattern23_samples.iloc[idx]
    index = row.name
    stock_code = row['证券代码']
    buy_date = row['买入日期'].replace('-', '')
    # if stock_code == '' and buy_date == '':
    #     print(1)
    # else:
    #     continue
    # print(buy_date, stock_code)
    file = open(log_path + f'{buy_date}_prod环境/{buy_date}-{stock_code}-prod环境.txt')
    lines = file.readlines()
    filter_line = list(filter(lambda x: 'Order updated' in x and 'ordStatus=FILLED' in x, lines))

    transaction_time_list = list(map(lambda x: getValueByKeyFromLine(x, 'transactionTime'), filter_line))
    order_qty_list = list(map(lambda x: float(getValueByKeyFromLine(x, 'quantity')), filter_line))
    price_list = list(map(lambda x: float(getValueByKeyFromLine(x, 'price')), filter_line))
    amt_list = (pd.Series(order_qty_list) * pd.Series(price_list)).values
    transaction_time_list = list(map(lambda x: pd.to_datetime(x[:-5]), transaction_time_list))

    # transaction_time_list = list(map(lambda x: int(x[11:13] + x[14:16] + x[17:19] + x[20:23]), transaction_time_list))
    first_ul_end_time = zb_info.loc[pd.to_datetime(buy_date), stock_code]['label_firstUL_end_Time']
    first_ul_time = zb_info.loc[pd.to_datetime(buy_date), stock_code]['label_touch_ul_time']
    first_ul_end_time_dt = dt.datetime.strptime(str(buy_date + str(int(first_ul_end_time))), '%Y%m%d%H%M%S%f')
    first_ul_time_dt = dt.datetime.strptime(str(buy_date + str(int(first_ul_time))), '%Y%m%d%H%M%S%f')

    trans_df = mdp.get_data_by_date("Transaction", stock_code, buy_date, ["2", "3"])
    trans_df = trans_df.query('TradePrice != 0')

    try:
        trans1_vs_ul = calc_time_interval(transaction_time_list[0], pd.to_datetime(first_ul_time_dt))

        # 对于trans1_vs_ul超过80000的，说明是第一笔成交时间在ZT之前
        # 对于last_trans_vs_zb超过8000的，说明是触板之后立刻炸板
        # if last_trans_vs_zb.seconds == 86399:
        #     print(1)

        first_trans_mdtime = transaction_time_list[0].strftime('%H%M%S%f')[:-3]
        last_trans_mdtime = transaction_time_list[-1].strftime('%H%M%S%f')[:-3]
        last_trans_ul_end_mdtime = trans_df.query(f'MDTime >= "{last_trans_mdtime}"').query(f'TradePrice != {trans_df.TradePrice.max()}').iloc[0]['MDTime']
        first_ul_end_mdtime = first_ul_end_time_dt.strftime('%H%M%S%f')[:-3]
        last_trans_ul_end_mdtime = max(last_trans_ul_end_mdtime, first_ul_end_mdtime)

        pattern23_samples.loc[index, '涨停时间'] = str(int(first_ul_time))
        pattern23_samples.loc[index, '第一笔成交单时间'] = first_trans_mdtime   # 可能是负
        pattern23_samples.loc[index, '最后一笔成交单时间'] = last_trans_mdtime   # 也可能是负，即在还没有触板前就成交完了
        pattern23_samples.loc[index, '第一次炸板时间'] = last_trans_ul_end_mdtime

        last_trans_ul_end_dt = dt.datetime.strptime(buy_date + last_trans_ul_end_mdtime + '000', '%Y%m%d%H%M%S%f')
        last_trans_vs_zb = calc_time_interval(pd.to_datetime(last_trans_ul_end_dt), transaction_time_list[-1])
        on_b_time = calc_time_interval(pd.to_datetime(last_trans_ul_end_dt), pd.to_datetime(first_ul_time_dt))

        pattern23_samples.loc[index, 'trans1_vs_ul'] = trans1_vs_ul
        pattern23_samples.loc[index, 'last_trans_vs_zb'] = last_trans_vs_zb
        pattern23_samples.loc[index, '触板时长'] = on_b_time

        print(trans1_vs_ul, last_trans_vs_zb, on_b_time)
    except:
        print(buy_date, stock_code, 'ERROR!!!!!!')

drop_samples = pattern23_samples[pattern23_samples['trans1_vs_ul'].isna()]
pattern23_samples = pattern23_samples.query('trans1_vs_ul > -1')
pattern23_samples['剩余时间所占比例'] = pattern23_samples['last_trans_vs_zb'] / pattern23_samples['触板时长']
pattern23_samples.to_excel('/data/user/015614/TEST/触板时长统计.xlsx')

send_file(pattern23_samples, )


"""
trans1_vs_ul 第一笔成交时间距离ZT时间
last_trans_vs_zb 最后一笔成交时间距离ZB时间
触板时长 最后一笔
"""
pattern23_samples = pd.read_excel('/data/user/015614/TEST/触板时长统计.xlsx', index_col=0)
des1 = pattern23_samples['last_trans_vs_zb'].describe()
des2 = pattern23_samples['触板时长'].describe()
des3 = pattern23_samples['trans1_vs_ul'].describe()
stats1 = pd.concat([des1, des2, des3], axis=1)
send_file(stats1)

pattern_samples_copy = pattern23_samples.copy()
pattern_samples_copy = pattern_samples_copy.sort_values('last_trans_vs_zb', ascending=False)

def stats_diff_attend(df):
    group_num = 10
    total_num = len(df)
    group_id_list = np.repeat(np.array(range(1, 10)), total_num // group_num, axis=0)
    group_id_list = np.concatenate([group_id_list, np.array([group_num] * (total_num - len(group_id_list)))])
    df['id'] = group_id_list
    ret = df.groupby('id').agg({'卖出部分盈利金额': 'sum',
                                '卖出部分收益率(%)': 'mean',
                                '实际是否正收益': 'mean'})
    ret['区间'] = df.groupby('id')['last_trans_vs_zb'].apply(lambda x: f'{x.iloc[0]}-{x.iloc[-1]}')
    return ret

stats2 = stats_diff_attend(pattern_samples_copy)
send_file(stats2)



