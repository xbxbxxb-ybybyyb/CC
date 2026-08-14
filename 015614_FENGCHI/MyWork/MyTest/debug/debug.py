# coding: utf-8
# Author：fengchi863
# Date ：2020/4/29 13:41

# import os
# os.remove('/data/group/800319/storeFactor/combine_ffactor20200428/ffactor_1_1_1.h5')
# print('删除成功')

####################

# import matplotlib.pyplot as plt
# import matplotlib
# matplotlib.use('Agg')
# import xquant.xqutils.xqdraw as xd
# import seaborn as sns
#
# plt.plot([1,2,3,4,5])
# plt.savefig('plot.png')
# xd.showfig("plot.png")

#####################################

# import matplotlib
# matplotlib.use('Agg')
# import numpy as np
# import matplotlib.pyplot as plt
# import xquant.xqutils.xqdraw as xd
#
# plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
# plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
#
# xData = np.arange(0, 10, 1)
# yData1 = xData.__pow__(2.0)
# yData2 = np.arange(15, 61, 5)
# plt.figure(num=1, figsize=(8, 6))
# plt.title('绘图1', size=14)
# plt.xlabel('x-轴', size=14)
# plt.ylabel('y-轴', size=14)
# plt.plot(xData, yData1, color='b', linestyle='--', marker='o', label='y1 data')
# plt.plot(xData, yData2, color='r', linestyle='-', label='y2 data')
# plt.legend(loc='upper left')
# plt.savefig('plot.png', format='png')
# #`显示绘制的图片`
# xd.showfig("plot.png")

###########################

# import os
# # corrcoef_path = '/data/group/800319/storeFactor/corrcoef/'
# # factor_list = os.listdir(corrcoef_path)
# # try:
# #     for file_name in sorted(factor_list):
# #         os.remove(corrcoef_path + file_name)
# # except Exception as e:
# #     print(file_name)
# #     print(e)

#############################

# import pandas as pd
# import os
#
# has_run_stk_file_name = os.listdir('/data/group/800319/junkData/IntraFactorModel/predictions/xgb_rise_down_zero_1min_20200605/')
# has_run_stk_id = list(map(lambda x: int(x[:-4]) if not x.startswith('Wrong') else int(x.split('_')[1][:-4]), has_run_stk_file_name))

###########################

# from math import ceil
# import numpy as np
#
# def divide(lst, slice_num):
#     size = len(lst) // slice_num + 1
#     if size <= 0:
#         return [lst]
#     ret = [lst[i * size:(i+1)*size] for i in range(0, ceil(len(lst)/size))]
#     for i in range(np.array(ret).shape[0]):
#         print(len(ret[i]), end=' ')
#
# print(divide([1,2,3,4,5,6,7],3))

##############################

from xquant.marketdata import MarketData
from datetime import datetime
from xquant.strategy.trademocker import ExchangeHouse
from xquant.strategy.trademocker import Order
from xquant.strategy.trademocker import DataProvider
import time

mdp = MarketData()
data = mdp.getMDTransactionDataFrame("601688.SH","20171201090000","20171201100000")

# transaction两市都有
data = mdp.get_data_by_date("Transaction", "000001.SZ", "20180301")

# 逐笔委托order数据只有深市有，沪市没有
# data = mdp.get_data_by_time_frame("Order", "601688.SZ", "20180301 093000000", "20180305 150000250")

e1 = time.time()
# 创建一个订单
order1 = Order(stock_code='000002.SZ', order_time=datetime(2018, 8, 1, 10, 30, 30), order_price=22.73, order_volume=3500, bs_flag='B')
# 实例化一个ExchangeHouse，撮合模式为TICK
exchange_house1 = ExchangeHouse(mode='TICK')
# 模拟下单
order_number1 = exchange_house1.send(orders=order1)
# 模拟挂单
exchange_house1.drive(order_number=order_number1, hold_time=2 * 60)
# 模拟撤单
exchange_house1.back(order_number=order_number1, back_date_time=5 * 60)
# 获取交易订单的成交信息
print(order1.get_record())
print(time.time() - e1)