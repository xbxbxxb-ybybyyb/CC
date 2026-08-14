# @Time : 2022/3/2 17:14
# @Author : Zhichen Lu
# @File : FactorComparing.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/BWorkHandOver')
sys.path.append('/data/user/015614/BWorkHandOver/ensemblemonitor-strategy-python')
sys.path.append('/data/user/015614/BWorkHandOver/StrongStockModel')

import pandas as pd
from dataApi.tradeDate import get_date_range,get_pre_trade_date
from tqdm import tqdm
from multiprocessing import Pool
from StrongStockModel.conf.path_config import root_path
import datetime,os
import numpy as np

using_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_local_path/available_factor_list.pkl')

def get_corr(factor_name,date_list):
    factor_res = {}
    for time_point in [1000, 1030, 1100, 1300, 1330, 1400, 1430]:
        if not os.path.exists(f'/data/group/800002/alpha_factor/lib/x_factor_lib/Fix{time_point}_{factor_name}.pkl'):
            continue
        offline_origin_factor = pd.read_pickle(f'/data/group/800002/alpha_factor/lib/x_factor_lib/Fix{time_point}_{factor_name}.pkl')
        for check_date in date_list:
            if not os.path.exists(f'/data/group/800002/realtime/alpha/x_day_lib/{check_date}/{time_point}/Fix{time_point}_{factor_name}.pkl'):
                factor_res[(check_date, time_point)] = np.nan
                continue
            online_origin_factor = pd.read_pickle(f'/data/group/800002/realtime/alpha/x_day_lib/{check_date}/{time_point}/Fix{time_point}_{factor_name}.pkl')
            origin_compare = pd.DataFrame({
                'offline': offline_origin_factor.loc[f'{check_date}'],
                'online': online_origin_factor.loc[f'{check_date}']
            })
            corr = origin_compare.corr().values[0, 1]
            factor_res[(check_date, time_point)] = corr
            if corr < 0.8:
                print(factor_name,check_date, time_point, corr)
    return factor_res

if __name__ == '__main__':
    today = int(datetime.date.today().strftime('%Y%m%d'))
    date_list = get_date_range(get_pre_trade_date(today,20),get_pre_trade_date(today))

    get_corr(using_factor_list[0], date_list[:2])

    bar = tqdm(total=len(using_factor_list))

    def update(*p):
        if bar.last_print_n<bar.total:
            bar.update()
        else:
            bar.close()
    res = {}
    pool = Pool(20)
    for f_name in using_factor_list:
        res[f_name] = pool.apply_async(get_corr,(f_name,date_list),callback=update)
    pool.close()
    pool.join()

    for each in res:
        res[each] = res[each].get()

    res = pd.DataFrame(res)

    condition = {0.98:2,0.97:1,0.95:0}
    blacklist = set([])
    for threshold,count in condition.items():
        unavailable = (res<threshold).groupby(level=0).sum()
        unavailable = (unavailable>count).sum()
        unavailable = unavailable[unavailable>0].index.tolist()
        blacklist = blacklist.union(set(unavailable))

    pd.to_pickle(blacklist,f'{root_path}/external_data/problem_factor/{today}.pkl')

