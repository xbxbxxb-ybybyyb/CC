import sys
sys.path.insert(4,'./prod_factors')
sys.path.insert(4,'./utils')
from factor_generator import FactorGenerator
from factor_generator_complex import FactorGeneratorComplex
import os
import pandas as pd
from multiprocessing import Pool
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import gc
import os, importlib
import datetime
import warnings
warnings.filterwarnings('ignore')
from SIF_Factor_Test13 import SIF_Factor_Test
import glob
#from factor_report_everyday import get_report

fs = [f for f in os.listdir('./prod_factors') if f.endswith('.py')]
for f in fs:
    importlib.import_module(f[:-3])
        
if __name__ == '__main__':
    _,end_date,_ = check_update_date()
    report_flag_date = end_date
#    start_date = int((pd.to_datetime(str(end_date)) - datetime.timedelta(days = 31)).strftime('%Y%m%d'))
#    prev_date = int((pd.to_datetime(str(end_date)) - datetime.timedelta(days = 62)).strftime('%Y%m%d'))
    start_date = end_date
#    start_date = 20200301
    prev_date = 20200101
    
    print(prev_date, start_date, end_date)
    
    def minute_flag_check(date):
        path1 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_IC_cfg_and_mask.success'
        path2 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_spot_minute.success'
        path3 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_tick_to_minute_future_data_and_mask.success'
        path4 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_cfg_hf.success'
        return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)
    
    flag_root = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(end_date) + '/'
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    flag_path_start = flag_root + str(end_date) + '_IC_factors.start'
    with open(flag_path_start,'w') as file:
        pass 

    print('------wait minute flag')
    while True:
        if minute_flag_check(end_date):
            break
        time.sleep(60)
    print('flag check finished!')
    

    FactorGenerator().prepare_hot_data(prev_date,end_date, ticker = 'IC.CFE', datakind = 'outsample')
    subclass_list = FactorGenerator.__subclasses__()
#    for subcls in subclass_list:
#        subcls().__callback__(start_date,end_date)
#        gc.collect()

    FactorGeneratorComplex().prepare_hot_data(prev_date,end_date,use_cache = False, save_cache = False, ticker='IC.CFE', datakind = 'outsample')
    subclass_list_cfg = FactorGeneratorComplex.__subclasses__()
#    for subcls in subclass_list:
#        subcls().__callback__(start_date,end_date)
#        gc.collect()

    print('factor count: ',len(subclass_list + subclass_list_cfg))
    
    def get_factors(subcls):
        print(subcls().__class__.__name__)
        subcls().__callback__(start_date,end_date)
        
    with Pool(processes=8) as pool:
        pool.map(get_factors, subclass_list + subclass_list_cfg)
        
    flag_path_success = flag_root + str(end_date) + '_IC_factors.success'
    with open(flag_path_success,'w') as file:
        pass
        
    for libname in ['IC_stage','IC_all','IC_prod']:
        ticker = 'IC.CFE'
        start_date, end_date = 20200101, 21000101
        save_image = True
        show_image=False
        savepath = '/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/factor_report/'

        libpath = '/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/' + libname
        savepath = os.path.join(savepath, libname + '_outsample')
        if not os.path.exists(savepath):
            os.makedirs(savepath)
            
        origindata = IO.read_data([start_date,end_date], columns = ['vwap'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')
        origindata = origindata.xs(ticker, level = 1)
        origindata['ret'] = origindata['vwap'].shift(-2) / origindata['vwap'].shift(-1) - 1
        origindata = origindata[['ret']]
            
        def test_factor(factorpath):
            factorname = factorpath.split('/')[-1][:-3]
            print(factorname)
            f = pd.read_hdf(factorpath).loc[str(start_date):str(end_date)]
            sif = SIF_Factor_Test(f.join(origindata, how = 'inner').sort_index(),factor_kind='1min',save_image=save_image,show_image=show_image, signal_lims=(-1, 1), savepath=savepath)
            stats = sif.draw_result()
            del(sif)
            return pd.DataFrame(stats, index=[f.columns.tolist()[0]]) 

        pathlist = glob.glob(libpath + '/*.h5')

        rlist = []
        with Pool(processes = 8) as pool:
            rlist = pool.map(test_factor, pathlist)
        result = pd.concat(rlist, axis = 0)
        result.to_csv(os.path.join(savepath , libname + '_' + str(start_date) + '_'+str(end_date)+'.csv'))

#    def if_flag_check(date):
#        path1 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_IF_factors.success'
#        return os.path.exists(path1) 

#    print('------wait report flag')
#    while True:
#        if if_flag_check(report_flag_date):
#            break
#        time.sleep(60)
#    print('flag check finished!')
    
#    get_report(end_date, '/data/user/015626/data/share/alpha/CHINA_FUTURES/MINUTE/factor_report/factor_report_pdf/')

