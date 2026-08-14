import pandas as pd
import os
import decimal

os.system("pip uninstall xdbJG -y")
os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdbJG-2.0.0-cp36-cp36m-linux_x86_64.whl")
from xdbJG.stockdata import StockData
xdb_datasource = StockData()

df_order1m = xdb_datasource.get_order_1min('20170110','000001.SZ')
df_order = xdb_datasource.get_order('20170110','000001.SZ')


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
df_order['md_minute'] = df_order['md_time'].apply(lambda x : convert_to_next_minute(x))
# 取mean的字段,groupby type, minute, side
res = df_order.groupby(['md_minute','type','side']).mean().reset_index()
res['md_minute'] = res['md_minute'].astype(int)

columns_mean_1m = ['OrderPrice_buy_type1_mean','OrderPrice_buy_type2_mean','OrderPrice_buy_type3_mean',
                   'OrderPrice_sell_type1_mean','OrderPrice_sell_type2_mean','OrderPrice_sell_type3_mean',]
                   # 'OrderPrice_buy_mean','OrderPrice_sell_mean']
for col in columns_mean_1m:
    df_order1m[col] = df_order1m[col].apply(lambda x : round_(x,8))
for col in columns_mean_1m:
    print(col)
    if 'buy' in col:
        res_col = res[res['side'] == 1]
    else:
        res_col = res[res['side'] == 2]
    if 'type1' in col:
        res_col = res_col[res_col['type'] == '1']
    if 'type2' in col:
        res_col = res_col[res_col['type'] == '2']
    if 'type3' in col:
        res_col = res_col[res_col['type'] == '3']
    if abs(res_col.reset_index().set_index('md_minute')['price'] - df_order1m.set_index('md_time')[col]).max() > 1e-8:
        print('不一致！！！！！！')
# 取mean的字段,groupby minute, side
res = df_order.groupby(['md_minute','side']).mean().reset_index()
res['md_minute'] = res['md_minute'].astype(int)

columns_mean_1m = ['OrderPrice_buy_mean', 'OrderPrice_sell_mean']
for col in columns_mean_1m:
    df_order1m[col] = df_order1m[col].apply(lambda x : round_(x,8))
for col in columns_mean_1m:
    print(col)
    if 'buy' in col:
        res_col = res[res['side'] == 1]
    else:
        res_col = res[res['side'] == 2]
    if abs(res_col.reset_index().set_index('md_minute')['price'] - df_order1m.set_index('md_time')[col]).max() > 1e-8:
        print('不一致！！！！！！')
# 取sum的字段验证逻辑自洽
if abs(df_order1m['OrderAmt_buy_type1'].fillna(0)
        + df_order1m['OrderAmt_buy_type2'].fillna(0)
        + df_order1m['OrderAmt_buy_type3'].fillna(0) - df_order1m['OrderAmt_buy'].fillna(0)).max() < 1e-8:
    print('OrderAmt_buy 逻辑自洽，为type123的和')
else:
    print('OrderAmt_buy 逻辑有问题')

if abs(df_order1m['OrderAmt_sell_type1'].fillna(0)
        + df_order1m['OrderAmt_sell_type2'].fillna(0)
        + df_order1m['OrderAmt_sell_type3'].fillna(0) - df_order1m['OrderAmt_sell'].fillna(0)).max() < 1e-8:
    print('OrderAmt_sell 逻辑自洽，为type123的和')
else:
    print('OrderAmt_sell 逻辑有问题')

if abs(df_order1m['OrderQty_buy_type1'].fillna(0)
        + df_order1m['OrderQty_buy_type2'].fillna(0)
        + df_order1m['OrderQty_buy_type3'].fillna(0) - df_order1m['OrderQty_buy'].fillna(0)).max() < 1e-8:
    print('OrderQty_buy 逻辑自洽，为type123的和')
else:
    print('OrderQty_buy 逻辑有问题')

if abs(df_order1m['OrderQty_sell_type1'].fillna(0)
        + df_order1m['OrderQty_sell_type2'].fillna(0)
        + df_order1m['OrderQty_sell_type3'].fillna(0) - df_order1m['OrderQty_sell'].fillna(0)).max() < 1e-8:
    print('OrderQty_sell 逻辑自洽，为type123的和')
else:
    print('OrderQty_sell 逻辑有问题')

if abs(df_order1m['OrderNum_buy_type1'].fillna(0)
        + df_order1m['OrderNum_buy_type2'].fillna(0)
        + df_order1m['OrderNum_buy_type3'].fillna(0) - df_order1m['OrderNum_buy'].fillna(0)).max() < 1e-8:
    print('OrderNum_buy 逻辑自洽，为type123的和')
else:
    print('OrderNum_buy 逻辑有问题')

if abs(df_order1m['OrderNum_sell_type1'].fillna(0)
        + df_order1m['OrderNum_sell_type2'].fillna(0)
        + df_order1m['OrderNum_sell_type3'].fillna(0) - df_order1m['OrderNum_sell'].fillna(0)).max() < 1e-8:
    print('OrderNum_sell 逻辑自洽，为type123的和')
else:
    print('OrderNum_sell 逻辑有问题')

# 验证sum的部分，只需要验证groupby side
df_order['is_valid'] = 1
df_order['amt'] = df_order['qty'] * df_order['price']
res = df_order.groupby(['md_minute','side']).sum().reset_index()
res['md_minute'] = res['md_minute'].astype(int)

columns_mean_1m = ['OrderNum_buy', 'OrderNum_sell',
                   'OrderQty_buy', 'OrderQty_sell',
                   'OrderAmt_buy', 'OrderAmt_sell']
for col in columns_mean_1m:
    df_order1m[col] = df_order1m[col].apply(lambda x : round_(x,8))
for col in columns_mean_1m:
    print(col)
    if 'buy' in col:
        res_col = res[res['side'] == 1]
    else:
        res_col = res[res['side'] == 2]
    dic_res_col_name = {
        'OrderNum_buy':'is_valid',
        'OrderNum_sell':'is_valid',
        'OrderQty_buy':'qty',
        'OrderQty_sell': 'qty',
        'OrderAmt_buy': 'amt',
        'OrderAmt_sell': 'amt',

    }
    res_col_name = dic_res_col_name[col]
    if abs(res_col.reset_index().set_index('md_minute')[res_col_name] - df_order1m.set_index('md_time')[col]).max() > 1e-8:
        print('不一致！！！！！！')
    else:
        print(abs(res_col.reset_index().set_index('md_minute')[res_col_name] - df_order1m.set_index('md_time')[col]).max() )



