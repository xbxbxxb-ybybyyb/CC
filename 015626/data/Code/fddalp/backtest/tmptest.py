import FactorTool
from IO import IO
import os

# read factors
sdate = 20130101
edate = 20180101

filePath = 'S:/Quant/data/alpha/CHINA_STOCK/DAILY/zf/test'
fileNames = os.listdir(filePath)

factor_dict = {}
for fileName in fileNames:
    alpName = fileName.split('.')[0]
    data = IO.read_data([sdate,edate],alt = os.path.join(filePath,fileName))
    factor_dict[fileName] = data[alpName].unstack()

# read holding period return

data1 = IO.read_data([sdate,edate],columns = ['close','adjfactor'],alt = 'S:/Quant/data/md/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
closePrice = (data1['close']*data1['adjfactor']).unstack()

FactorTool.max_icir_rolling(factor_dict,closePrice,10,ic_win=30,weight_roll=None,solve_type='optimize',cov_type='sample',plot=True)
