import sys
sys.path.insert(4, '/data/user/015626/data/share/Code/factor_test/')
from multifactor.IO import IO
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from operators import *
import os
from SIF_Factor_Test24 import SIF_Factor_Test
from multiprocessing import Pool
import glob



libname = 'POOL'
# libname = 'IH_IC_gp'
# libname = 'IH_IF_factors'
# libname = 'IH_IC_factors'
ticker = 'IC.CFE'
# start_date, end_date = 20210101, 20220801
start_date, end_date = 20170101, 20201231
# start_date, end_date = 20210101, 20220101
save_image = True
show_image=False
savepath = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/factor_report/' + libname 

# libpath = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/' + libname + '/minute_norm'
libpath = '/data/user/016700/Data/Factors/' + libname 
savepath = os.path.join(savepath, libname + '_'+str(start_date) + '_'+str(end_date) + '_'+ticker)
if not os.path.exists(savepath):
    os.makedirs(savepath)
    
origindata = IO.read_data([str(start_date),str(end_date) + '235959'], columns = ['twap'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')
origindata = origindata.xs(ticker, level = 1)
origindata['ret'] = origindata['twap'].shift(-2) / origindata['twap'].shift(-1) - 1
origindata = origindata[['ret','twap']]
    
def test_factor(factorpath):
#     try:
    factorname = factorpath.split('/')[-1][:-3]
#     if str.lower(factorname[-3:]) != '_if':
#         return
    print(factorname)
    f = pd.read_hdf(factorpath).loc[str(start_date):str(end_date)]
    if isinstance(f, pd.Series):
        f = f.to_frame()
        f.columns = [factorname]
    f.index.name = 'dt'
    sif = SIF_Factor_Test(f.join(origindata, how = 'inner').sort_index(),factor_kind='1min',save_image=save_image,show_image=show_image, signal_lims=(-1, 1), savepath=savepath)
    stats = sif.draw_result()
    stats['IC_duration'] = str(stats['IC_duration'])
    del(sif)
    return pd.DataFrame(stats, index=[f.columns.tolist()[0]]) 
#     except Exception as e:
#         print(e)
#         return

pathlist = glob.glob(libpath + '/*.h5')

rlist = []
with Pool(processes = 24) as pool:
    rlist = pool.map(test_factor, pathlist)
result = pd.concat(rlist, axis = 0)
result.to_csv(os.path.join(savepath , libname + '_' + str(start_date) + '_'+str(end_date)+'.csv'))