"""
过去半个月中股票复权收盘价与换手率pearson相关系数
"""
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.backtest.factor_test import SingleFactorTest
import pandas as pd
import numpy as np
import time
import os

factor_name = 'Pearson_rolling_15_days'
start_date, end_date = 20120101, 20180630

nowdate = str(time.strftime('%Y%m%d',time.localtime(time.time())))
factor_baseDir = '/data/user/015626/factor/' + nowdate + '_' + factor_name  #因子及报告储存路径
if not os.path.exists(factor_baseDir):
    os.makedirs(factor_baseDir)

print('read data...')
data = IO.read_data([start_date, end_date],  ftype = FType.MD, dsource = DSource.WIND)

print('start calculating...')
data['turnover_rate'] = data.volume * 100 /data.free_float_shares / 10000
df = data[['close','turnover_rate']]
newdf = df.unstack()
df_roll = newdf['close'].rolling(15,15).corr(newdf['turnover_rate'])
data = df_roll.stack()
data = pd.DataFrame(data)
data.columns = ['Pearson']

print('save h5...')
h5name = factor_baseDir+'/' + factor_name + '.h5'
if os.path.exists(h5name):
    os.remove(h5name)
IO.pd_hdf5_writer(data, hdf5=h5name, dataset=factor_name)

sft = SingleFactorTest(start_date, end_date, holding_period=1, benchmark='zz500',
                       segment_number=15, transaction_cost=0.002, ret_price = 'open', ret_shift = 'True',easy_test= 'True')
                    
sft.load_factor(factor_data=data, name=factor_name)
sft.shoot(result_folder=factor_baseDir)   # 输出因子测试报告