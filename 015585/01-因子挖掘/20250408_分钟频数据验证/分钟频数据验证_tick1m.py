import pandas as pd
import os
import decimal

os.system("pip uninstall xdbJG -y")
os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdbJG-2.0.0-cp36-cp36m-linux_x86_64.whl")
from xdbJG.stockdata import StockData
xdb_datasource = StockData()

df_tick1m = xdb_datasource.get_tick_1min('20170110','000001.SZ')
df_tick1s = xdb_datasource.get_tick1s('20170110','000001.SZ')


def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
def convert_to_next_minute(time_num):
    # 确保整数长度为8位
    time_str = f"{time_num:09d}"
    # 分解时间单位
    hour = int(time_str[:2])
    minute = int(time_str[2:4])
    second = int(time_str[4:6])
    millisecond = int(time_str[6:9])
    # 检查是否需要进位到下一个分钟
    if second != 0 or millisecond != 0:
        minute += 1
        second = 0
        millisecond = 0
        # 处理分钟的进位情况
        if minute > 59:
            hour += 1
            minute = 0

    # 重新组合时间
    new_time = f"{hour:02d}{minute:02d}{second:02d}{millisecond:03d}"
    new_time_num = int(new_time)

    return new_time_num
df_tick1s['md_minute'] = df_tick1s['md_time'].apply(lambda x : convert_to_next_minute(x))
df_tick1s['num_trades'] = df_tick1s['total_num_trades'].diff().fillna(0)
# 取mean的字段
res = df_tick1s.groupby('md_minute').mean().reset_index()
res['md_minute'] = res['md_minute'].astype(int)
columns_mean_1m = ['last_px_mean','ask_order_qty_mean','bid_order_qty_mean','ask_avg_price_mean','bid_avg_price_mean']
res = res.rename(columns = {
    'last_px':'last_px_mean',
    'ask_order_qty':'ask_order_qty_mean',
    'bid_order_qty':'bid_order_qty_mean',
    'ask_avg_px':'ask_avg_price_mean',
    'bid_avg_px':'bid_avg_price_mean',
})
for col in columns_mean_1m:
    res[col] = res[col].apply(lambda x : round_(x,8))
    df_tick1m[col] = df_tick1m[col].apply(lambda x : round_(x,8))
filter_res_1 = res['md_minute'] >= 93000000
filter_res_2 = res['md_minute'] <= 145700000
filter_1m_1 = df_tick1m['md_time'] >= 93000000
filter_1m_2 = df_tick1m['md_time'] <= 145700000
for col in columns_mean_1m:
    print(col)
    if abs(res[filter_res_1 & filter_res_2][col] - df_tick1m[filter_1m_1 & filter_1m_2][col]).max() > 1e-8:
        print('不一致！！！！！！')

# 取sum的字段
res = df_tick1s.groupby('md_minute').sum().reset_index()
res['md_minute'] = res['md_minute'].astype(int)
columns_mean_1m = ['num_trades','volume']
res = res.rename(columns = {
})
for col in columns_mean_1m:
    res[col] = res[col].apply(lambda x : round_(x,8))
    df_tick1m[col] = df_tick1m[col].apply(lambda x : round_(x,8))
filter_res_1 = res['md_minute'] >= 93000000
filter_res_2 = res['md_minute'] <= 145700000
filter_1m_1 = df_tick1m['md_time'] >= 93000000
filter_1m_2 = df_tick1m['md_time'] <= 145700000
for col in columns_mean_1m:
    print(col)
    if abs(res[filter_res_1 & filter_res_2][col] - df_tick1m[filter_1m_1 & filter_1m_2][col]).max() > 1e-8:
        print('不一致！！！！！！')