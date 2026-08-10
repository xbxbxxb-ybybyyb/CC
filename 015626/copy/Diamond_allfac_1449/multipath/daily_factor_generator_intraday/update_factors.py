import sys
sys.path.insert(4, './daily_factor_generator_intraday/overnight_prod_20210119/')
sys.path.insert(4, './operators/')
sys.path.insert(4, './utils/')

import os
import time
import importlib
import datetime as dt
import warnings
warnings.filterwarnings('ignore')

from factor_generator import FactorGenerator
from factor_generator_xdy import FactorGeneratorXdy
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from utils.date_helper import *




fs = [f for f in os.listdir('./daily_factor_generator_intraday/overnight_prod_20210119/') if f.endswith('.py')]
for f in fs:
    importlib.import_module(f[:-3])
    


if __name__ == '__main__':
    start_date = end_date = int(dt.datetime.now().strftime('%Y%m%d'))
    
    fdate_list_dt = IO.read_data([19980101, 21000101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    last_trade_date = fdate_list[fdate_list.index(end_date)-1]
    
    
    def minute_flag_check(date1, date2):
        path1 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date1) + '/' + str(date1) + '_spot_minute.success'
        path2 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date1) + '/' + str(date1) + '_tick_to_minute_future_data_and_mask.success'
        path3 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date1) + '/' + str(date1) + '_cfg_hf.success'
        path4 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date1) + '/' + str(date1) + '_overnight_dailydata.success'
        path5 = os.path.join('/data/user/012245/warehouse/flags/', str(date2), str(date2)+'_CLOSURE.success')
        return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4) and os.path.exists(path5)
    
    flag_root = '/data/user/017024/data/flag/' + str(end_date) + '/'
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    flag_path_start = flag_root + str(end_date) + '_overnight_factors_intraday_index_future.start'
    with open(flag_path_start,'w') as file:
        pass 

    print('------wait minute flag')
    while True:
        if minute_flag_check(last_trade_date, end_date):
            break
        time.sleep(1)
    print('flag check finished!')
    

    prev_date = 20200101
    print(dt.datetime.now())
    print(prev_date, start_date, end_date)
    FactorGenerator().prepare_hot_data(prev_date, end_date)
    print(dt.datetime.now())
    subclass_list = FactorGenerator.__subclasses__()     
    print('factor count: ', len(subclass_list))
        
    for i, subcls in enumerate(subclass_list):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        subcls().__callback__(start_date, end_date)

    
    prev_date = 20120101
    print(dt.datetime.now())
    print(prev_date, start_date, end_date)
    FactorGeneratorXdy().prepare_hot_data(prev_date, end_date)
    print(dt.datetime.now())
    subclass_list = FactorGeneratorXdy.__subclasses__()     
    print('factor count: ', len(subclass_list))
        
    for i, subcls in enumerate(subclass_list):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        subcls().__callback__(start_date, end_date)


    flag_path_success = flag_root + str(end_date) + '_overnight_factors_intraday_index_future.success'
    with open(flag_path_success, 'w') as file:
        pass

        
    # 下面是根据因子值计算仓位
    ic_prod_path = '/data/user/017024/share/overnight/alpha_intraday/'
    ic_factor_list = sorted(os.listdir(ic_prod_path))
    ic_factors = [os.path.join(ic_prod_path, i) for i in ic_factor_list]

    factor_prod = None
    for i, i_name in enumerate(ic_factors):
        factor_minute = pd.read_hdf(i_name) 
        factor_prod = factor_minute if factor_prod is None else pd.concat([factor_prod, factor_minute], axis=1)
    
    factor_prod[factor_prod<0.75] = np.nan
    temp1 = factor_prod.count(axis=1) / factor_prod.shape[1]
    temp2 = pd.Series(np.searchsorted([0.75, 0.8, 0.85, 0.9, 0.95, 1], factor_prod.mean(axis=1).dropna()).flatten(), 
                                        index=factor_prod.mean(axis=1).dropna().index) * 0.2 + 0.4
    temp2 = temp2.reindex(temp1.index)
    factors_signal = temp1 * temp2
    print("Today's position is: " + str(factors_signal.iloc[-1]))
    print(dt.datetime.now())


