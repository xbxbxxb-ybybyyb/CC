# coding: utf-8
# Author：fengchi863
# Date ：2021/7/15 14:39

from ShortTermTrading.conf.path_conf import junk_path
from FaaMonitor.conf.path_conf import ths_reverse_path
import pandas as pd, numpy as np
from ShortTermTrading.dataApi import getData, tradeDate, stockList
from FaaMonitor.Util.MyUtil import MyUtil

record = pd.read_pickle(junk_path + '20210715_首阴反包交易回测.pkl')
record = record.reset_index()
record.columns = ['date', 'time', 'stk_id', 'True']

start_date = record['date'].iloc[0]
end_date = record['date'].iloc[-1]
end_date = tradeDate.get_pre_trade_date(end_date, -1)
date_list = tradeDate.get_date_range(start_date, end_date)

high_badj = getData.get_daily_1factor('high', date_list=date_list)
twap = getData.get_daily_1factor('twap', date_list=date_list)
record['买入价格'] = record[['date', 'stk_id']].apply(lambda x: high_badj.loc[x['date'], x['stk_id']], axis=1)
record['卖出价格'] = record[['date', 'stk_id']].apply(lambda x: twap.loc[tradeDate.get_pre_trade_date(x['date'], -1), x['stk_id']], axis=1)

record['收益率'] = record['卖出价格'] / record['买入价格'] - 1
target = record.query('20210615 < date < 20210712')
mean_profit = target['收益率'].mean()
winrate = len(target.query('收益率 >= 0')) / len(target)
earning_loss_ratio = -target.query('收益率 >= 0')['收益率'].mean() / target.query('收益率 < 0')['收益率'].mean()
deal_num = len(target)
record['股票名称'] = record['stk_id'].apply(lambda x: MyUtil.get_1stock_name(x))
print('%.4f' % mean_profit, winrate, '%.4f' % earning_loss_ratio, deal_num)

ths_concept = np.load(ths_reverse_path).item()
record['同花顺板块'] = record['stk_id'].apply(lambda x: ths_concept[stockList.trans_int2windcode(x)])

# def isin_judge(concept_str, target_concept=['锂电池', '半导体及元件', '光伏概念', '盐湖提锂']):
#     for concept in target_concept:
#         if concept in concept_str:
#             return True
#     return False
#
# record['是否热点'] = record['同花顺板块'].apply(lambda x: isin_judge(x))
# record = record.query('是否热点 == True')