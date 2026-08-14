# coding: utf-8
# Author：fengchi863
# Date ：2021/6/11 14:27

from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.dataApi import getData
from ShortTermTrading.dataApi.tradeDate import get_pre_trade_date
import pandas as pd

def calc_profit(s: pd.Series):
    res1 = s.mean() # 平均盈亏
    res2 = (s > 0).sum() / len(s) # 胜率
    res3 = -1 * s[s>0].sum() / s[s<0].sum() # 盈亏比
    return {'平均盈亏': res1,
            '胜率': res2,
            '盈亏比': res3}

start_date = 20140101
end_date = 20201231
minutely_true_data_path = junk_path + 'minutely_true_df.xlsx'
minute_close_badj = getData.get_minute_1factor('close_badj', start_datetime=start_date, end_datetime=end_date)

deal_data = pd.read_excel(minutely_true_data_path, index_col=0)
deal_data = deal_data[(deal_data['date'] >= start_date) & (deal_data['date'] <= end_date)]
deal_data['买入价'] = deal_data[['stk_id', 'date', 'time']].apply(lambda x: minute_close_badj.loc[(x['date'], x['time']), x['stk_id']], axis=1)
deal_data['T日收盘价'] = deal_data[['stk_id', 'date', 'time']].apply(lambda x: minute_close_badj.loc[(x['date'], 1500), x['stk_id']], axis=1)
deal_data['T+1日开盘价'] = deal_data[['stk_id', 'date', 'time']].apply(lambda x: minute_close_badj.loc[(get_pre_trade_date(x['date'], -1), 925), x['stk_id']], axis=1)
deal_data['T+1日开盘5分钟平均价'] = deal_data[['stk_id', 'date', 'time']].apply(lambda x: minute_close_badj.loc[(get_pre_trade_date(x['date'], -1), 925): (get_pre_trade_date(x['date'], -1), 935), x['stk_id']].mean(), axis=1)
deal_data['T+1日开盘10分钟平均价'] = deal_data[['stk_id', 'date', 'time']].apply(lambda x: minute_close_badj.loc[(get_pre_trade_date(x['date'], -1), 925): (get_pre_trade_date(x['date'], -1), 940), x['stk_id']].mean(), axis=1)
deal_data['T+1日开盘30分钟平均价'] = deal_data[['stk_id', 'date', 'time']].apply(lambda x: minute_close_badj.loc[(get_pre_trade_date(x['date'], -1), 925): (get_pre_trade_date(x['date'], -1), 1000), x['stk_id']].mean(), axis=1)

for i in range(1, 7):
    deal_data['T+%d日收盘价' % i] = deal_data[['stk_id', 'date', 'time']].apply(lambda x: minute_close_badj.loc[(get_pre_trade_date(x['date'], -1 * i), 1500), x['stk_id']], axis=1)

deal_data['T日收盘价收益'] = deal_data['T日收盘价'] / deal_data['买入价'] - 1
deal_data['T+1日开盘价收益'] = deal_data['T+1日开盘价'] / deal_data['买入价'] - 1
deal_data['T+1日开盘5分钟平均价收益'] = deal_data['T+1日开盘5分钟平均价'] / deal_data['买入价'] - 1
deal_data['T+1日开盘10分钟平均价收益'] = deal_data['T+1日开盘10分钟平均价'] / deal_data['买入价'] - 1
deal_data['T+1日开盘30分钟平均价收益'] = deal_data['T+1日开盘30分钟平均价'] / deal_data['买入价'] - 1
for i in range(1, 7):
    deal_data['T+%d日收盘价收益' % i] = deal_data['T+%d日收盘价' % i] / deal_data['买入价'] - 1

index_dict = {'T日收盘价收益': 'T日收盘价',
              'T+1日开盘价收益': 'T+1日开盘价',
              'T+1日开盘5分钟平均价收益': 'T+1日开盘5分钟平均价',
              'T+1日开盘10分钟平均价收益': 'T+1日开盘10分钟平均价',
              'T+1日开盘30分钟平均价收益': 'T+1日开盘30分钟平均价',
              'T+1日收盘价收益': 'T+1日收盘价',
              'T+2日收盘价收益': 'T+2日收盘价',
              'T+3日收盘价收益': 'T+3日收盘价',
              'T+4日收盘价收益': 'T+4日收盘价',
              'T+5日收盘价收益': 'T+5日收盘价',
              'T+6日收盘价收益': 'T+6日收盘价'}

res = pd.DataFrame()
for key in list(index_dict.keys()):
    tmp = pd.DataFrame(calc_profit(deal_data.loc[deal_data['date']>=start_date][key]),
                           index=[index_dict[key]])
    res = res.append(tmp)

save_dict = dict()
save_dict['买入卖出及收益明细'] = deal_data
save_dict['收益统计'] = res
with pd.ExcelWriter(junk_path + '日内详情及收益统计.xlsx') as writer:
    for each in save_dict:
        save_dict[each].to_excel(writer, each)