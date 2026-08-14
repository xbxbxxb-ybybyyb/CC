from xdbJG.stockdata import StockData
xdb_datasource = StockData()
import pandas as pd

df_order1m = xdb_datasource.get_order_1min('20180109','000418.SZ')
df_order = xdb_datasource.get_order('20180109','000418.SZ')
# print(df_order1m['OrderQty_buy'].sum() + df_order1m['OrderQty_sell'].sum())
# print(df_order['qty'].sum())

time1 = 135600000
time2 = 135700000
df_order_filter = df_order[(df_order['md_time'] > time1) & (df_order['md_time'] <= time2)]
df_order1m_filter = df_order1m[(df_order1m['md_time'] > time1) & (df_order1m['md_time'] <= time2)]
print(df_order1m_filter['OrderQty_buy'].sum() + df_order1m_filter['OrderQty_sell'].sum())
print(df_order_filter['qty'].sum())

# df3 = pd.read_pickle('/dfs/group/800463/data/xdb_data_lag3_new/neptune/xdb_order/20180110.pkl')