# coding: utf-8
# Author：fengchi863
# Date ：2020/8/24 8:34

import pandas as pd

from BullClient.RecordDataSet.RecordDataSet import RecordDataSet
from StrongStockModel.dataApi.getData import get_daily_1factor, get_date_range

date_list = get_date_range(20140401, 20151231)
rds = RecordDataSet()
deliver = rds.get_clean_deliver_data()
close = get_daily_1factor('close', date_list=date_list)
deliver['当日收盘价'] = deliver[['委托日期', '证券代码']]. \
    apply(lambda x: close.loc[x['委托日期'], x['证券代码']], axis=1)

group = deliver.sort_values(['委托日期', '证券代码', '成交时间'])
group = group.groupby(['委托日期', '证券代码'])['剩余股数'].apply(lambda x: x.iloc[-1])
daily_cap = group.unstack()

no_trading_day = list(set(date_list) - set(daily_cap.index.tolist()))
blank_df = pd.DataFrame(index=no_trading_day, columns=daily_cap.columns)
daily_cap = daily_cap.append(blank_df)
daily_cap = daily_cap.sort_index()
daily_cap = daily_cap.fillna(method='ffill').fillna(0)

res = daily_cap * close
res = res.fillna(method='ffill').fillna(0)
daily_total_cap = res.sum(axis=1)

# 持仓股票数量
daily_cap = daily_cap > 0
daily_stock_num = daily_cap.sum(axis=1)
