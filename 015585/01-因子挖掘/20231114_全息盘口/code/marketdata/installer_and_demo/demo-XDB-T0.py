from xdbT0.stockdata import StockData
from xdbT0.factordata import FactorData
import pandas as pd
import time
import numpy as np
import os

a = StockData()

# 获取标的成交
df = a.get_trade("20230704", "000786.SZ")

# 获取标的委托
df2 = a.get_order("20230704", "000786.SZ")

# 获取标的秒级盘口
df3 = a.get_tick1s("20230704", "000786.SZ")

# 获取标的3妙Tick 参数3为行情路数
# 0: 036, 1:147, 2:258
df4 = a.get_tick3s("20230704", "601860.SH", 0)
df5 = a.get_tick3s("20230704", "601860.SH", 1)
df6 = a.get_tick3s("20230704", "601860.SH", 2)

# 获取标的撤单
df7 = a.get_cancel("20230704", "000786.SZ")

# 获取标的全息盘口
df8 = a.get_tickfull("20230704", "000786.SZ")

# 获取标的日频数据
df9 = a.get_dailydata("20230704", "000786.SZ")

# 获取标的分钟K数据
df10 = a.get_kline1m("20230704", "000786.SZ")

# 获取交易所tick
df11 = a.get_tickex("20230704", "000786.SZ")


# get num系列方法，第三项参数为可选参数，支持传入列表或单个标的。
# 若不填或传入""或[""]则为查询该市场所有标的 (较慢)
# 如果该标的当日无交易，则返回0。如{'000671.SZ': 0}

dic1 = a.get_order_num("20230612", "SZ","000671.SZ")
dic2 = a.get_trade_num("20230612", "SZ",["000001.SZ"])
dic3 = a.get_cancel_num("20230612", "SZ","")
did4 = a.get_tick1s_num("20230612", "SZ",[""])
dic5 = a.get_tickfull_num("20230612", "SZ",["000001.SZ", "000786.SZ"])


f = FactorData()
# 目前只有 sappe 数据 和 trend数据，第三个参数固定为sappe_factor或trend_factor
df16 = f.get_factor("20230704", "000001.SZ", "sappe_factor")


print("end")
