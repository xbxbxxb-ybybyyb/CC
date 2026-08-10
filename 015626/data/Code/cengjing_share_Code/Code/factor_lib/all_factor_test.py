from multifactor.IO import IO
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from operators import *
import os
from SIF_Factor_Test7 import SIF_Factor_Test

kind = 'fullhistory'
ticker = 'IC.CFE'
factorpath = '/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE/IC_test00/'
savepath='/data/user/015626/data/share/factor/factor_test/1min/all_factor_test_20200822/IC_test00_maindata/' + kind +'/'

start_date = 20200101 if kind == 'outsample' else 20160101
end_date = 20210101

origindata = IO.read_data([start_date,end_date], columns = ['vwap'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')
origindata = origindata.xs(ticker, level = 1)
origindata['return_points'] = origindata['vwap'].shift(-2) - origindata['vwap'].shift(-1)
origindata = origindata[['return_points']]

if not os.path.exists(savepath):
    os.makedirs(savepath)
rootpath = factorpath

resultdf = pd.DataFrame()
count = 0
for x in os.listdir(rootpath):
    if not x.endswith('h5'):
        continue
    print(count)
    factorname = x[:-3]
    df = IO.read_data([start_date,end_date], alt = os.path.join(rootpath, x)).xs(ticker, level = 1)

    sif = SIF_Factor_Test(df.join(origindata, how = 'inner'), factorname,factor_kind='1min',save_image=True,show_image=False, signal_lims=(-1, 1), savepath=savepath)
    stats = sif.draw_result()
    
    resultdf.loc[count, 'factor_name'] = factorname
    for key in stats.keys():
        resultdf.loc[count, key] = round(stats[key], 3)    
    count += 1
resultdf.to_csv(savepath + 'IC_testmain'+kind+'.csv', index = False)