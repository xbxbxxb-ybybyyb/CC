# coding: utf-8
# Author：fengchi863
# Date ：2020/8/25 13:13
import pandas as pd
from tqdm import tqdm

from BullClient.RecordDataSet.RecordDataSet import RecordDataSet
from BullClient.conf.path_conf import fc_out_path
from BullClient.dataApi.getData import get_daily_1factor, get_date_range

date_list = get_date_range(20140401, 20151231)
rds = RecordDataSet()
deliver = rds.get_clean_deliver_data()

close = get_daily_1factor('close', date_list=date_list)
deliver['当日收盘价'] = deliver[['委托日期', '证券代码']]. \
    apply(lambda x: close.loc[x['委托日期'], x['证券代码']], axis=1)
pre_close = get_daily_1factor('pre_close', date_list=date_list)
deliver['前收盘价'] = deliver[['委托日期', '证券代码']]. \
    apply(lambda x: pre_close.loc[x['委托日期'], x['证券代码']], axis=1)

group = deliver.sort_values(['委托日期', '证券代码', '成交时间'])
group = group.groupby(['委托日期', '证券代码'])['剩余股数'].apply(lambda x: x.iloc[-1])
daily_cap = group.unstack()

no_trading_day = list(set(date_list) - set(daily_cap.index.tolist()))
blank_df = pd.DataFrame(index=no_trading_day, columns=daily_cap.columns)
daily_cap = daily_cap.append(blank_df)
daily_cap = daily_cap.sort_index()
daily_cap = daily_cap.fillna(method='ffill').fillna(0)
daily_cap = daily_cap * close
daily_holding_cap = daily_cap.sum(axis=1)
daily_cap = daily_cap.shift(1).fillna(0)  # 持仓市值为昨天的，计算当日收益时用昨天的持仓市值
yesteday_holding_cap = daily_holding_cap.shift(1).fillna(0)

pct_chg = close / pre_close - 1
holding_profit = (pct_chg * daily_cap).fillna(0)
daily_holding_profit = holding_profit.sum(axis=1)

# 计算每日交易收益
deliver_date_list = sorted(list(set(deliver['委托日期'].tolist())))
daily_deal_profit = dict()
for date in tqdm(date_list):
    deal_profit = 0
    # 无交易
    if date not in deliver_date_list:
        daily_deal_profit.update({date: 0})
    else:
        tmp_deliver = deliver[deliver['委托日期'] == date]
        for idx in range(len(tmp_deliver)):
            tmp_deal = tmp_deliver.iloc[idx]
            deal_profit += (tmp_deal['当日收盘价'] - tmp_deal['成交价格']) * tmp_deal['成交数量']
    daily_deal_profit.update({date: deal_profit})

daily_deal_profit = pd.Series(daily_deal_profit)


# 计算每日收益率
daily_net_pctchg = dict()
for date in tqdm(date_list):
    net_pctchg = (daily_holding_profit[date] + daily_deal_profit[date]) / max(daily_holding_cap[date],
                                                                              yesteday_holding_cap[date])
    daily_net_pctchg.update({date: net_pctchg})

# 整合
daily_net_pctchg = pd.Series(daily_net_pctchg)
res = pd.concat([daily_holding_cap, yesteday_holding_cap, daily_holding_profit, daily_deal_profit, daily_net_pctchg],
                axis=1)
res.columns = ['当日持仓市值', '昨日持仓市值', '当日持仓收益', '当日交易收益', '当日收益率']
res.to_excel(fc_out_path + '净值走势.xlsx')
