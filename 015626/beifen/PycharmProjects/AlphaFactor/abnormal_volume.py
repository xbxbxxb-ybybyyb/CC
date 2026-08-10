"""
反转因子
异常交易量：当日交易量除以前十日交易量
"""
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.backtest.factor_test import SingleFactorTest
import pandas as pd
import numpy as np

def check_dir(path):
    from xquant.pyfilelib import Pyfile
    py = Pyfile()
    if not py.exists(path):
        py.mkdir(path)
factor_baseDir = '/data/user/015626/factorshare_v1_1'  #因子储存路径
report_baseDir = '/data/user/015626/recordshare_v1_1'  #pdf报告存储路径
check_dir(report_baseDir)
check_dir(factor_baseDir)

date_start, date_end = 20120101, 20180630

#1.读取数据,编写因子逻辑

data = IO.read_data([date_start,date_end],columns=['volume'],ftype=FType.MD,dsource=DSource.WIND)
volume = data.unstack()


#t可以调整
t = 15
ratio = np.divide(volume,volume.rolling(t,t).mean())
print(ratio)

ratio = ratio.stack()
print(ratio)

#给因子起名
hualihushao = 'abnormal_volume_'+str(t)+'_days'
ratio.columns = [hualihushao]

f_fine = ratio
#2.保存为h5文件
#IO.pd_hdf5_writer(f_fine,'/data/user/015663/'+hualihushao+'.h5', dataset=f_fine.columns[0])
IO.pd_hdf5_writer(f_fine, hdf5=factor_baseDir+'/' + hualihushao + '.h5', dataset=f_fine.columns[0])

#3.因子评价
sft = SingleFactorTest(date_start, date_end, holding_period=5, benchmark='zz500',
                       segment_number=15, transaction_cost=0.002)

#4.输出因子报告
#factorNlStd = IO.read_data([date_start, date_end],
#                            ftype=FType.MD, dfreq=DFreq.DAILY, dsource=DSource.WIND)
#factorNlStd = factorNlStd.iloc[:, 1]
sft.load_factor(factor_data=f_fine, name=hualihushao)
sft.shoot(result_folder=report_baseDir)   # 输出因子测试报告




