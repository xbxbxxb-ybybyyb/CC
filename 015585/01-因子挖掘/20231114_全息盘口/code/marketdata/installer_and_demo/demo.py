from xdb.stockdata import StockData
from xdb.factordata import FactorData
import pandas as pd
import time
import os

a = StockData()

# get num系列方法，第三项参数为可选参数，支持传入列表或单个标的。
# 若不填或传入""或[""]则为查询该市场所有标的 (较慢)
# 如果该标的当日无交易，则返回0。如{'000671.SZ': 0}

# (由于当日没有这个标的的数据，因此会打印错误日志：“数据读取错误: 未查询到标的=000671.SZ在该日的相关信息！”， 并返回{'000671.SZ': 0})
# dic1 = a.get_order_num("20230612", "SZ","000671.SZ")
dic2 = a.get_trade_num("20230612", "SZ",["000001.SZ"])
dic3 = a.get_cancel_num("20230612", "SZ","")
did4 = a.get_tick1s_num("20230612", "SZ",[""])
dic5 = a.get_tickfull_num("20230612", "SZ",["000001.SZ", "000786.SZ"])

# 获取标的秒级盘口
df = a.get_tick1s("20230524", "000001.SZ")

# 获取标的成交
df2 = a.get_order("20230524", "300698.SZ")

# 获取标的委托
df3 = a.get_trade("20230524", "300528.SZ")

# 获取标的撤单
df4 = a.get_cancel("20230524", "300528.SZ")

# 获取标的全息盘口 (由于当日没有这个标的的数据，因此会打印错误日志：“未找到数据: symbol=000671.SZ, 请检查标的及后缀是否正确，或检查标的是否交易”， 并返回空的dataframe)
df5 = a.get_tickfull("20230612", "000671.SZ")

# 获取标的分钟K数据
df6 = a.get_kline1m("20230524", "300698.SZ")

# 获取交易所tick
df7 = a.get_tickex("20230524", "300698.SZ")

# 获取标的日频数据
df8 = a.get_dailydata("20230524", "300698.SZ")



b = FactorData()
# 目前只有 sappe 数据 和 trend数据，第三个参数固定为sappe_factor或trend_factor
df9 = b.get_factor("20230612", "000918.SZ", "sappe_factor")


print("end")
