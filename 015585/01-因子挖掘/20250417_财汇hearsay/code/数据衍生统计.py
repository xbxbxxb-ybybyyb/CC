import pandas as pd
from xquant.thirdpartydata.factordata import FactorData
s = FactorData()
from xquant.textdata import NewsData
nd = NewsData()
import datetime
import os
import IO
import numpy as np

root_path = '/dfs/user/015585/20250423_财汇hearsay数据/原始结果/'
# date = '20231120'
save_path = '/dfs/user/015585/20250423_财汇hearsay数据/衍生结果/'

ipo_data = IO.read_data([19000101, 20990101], alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5').reset_index()
ipo_data = ipo_data[~ipo_data['S_INFO_LISTDATE'].isna()]
def map_Ticker(x):
    try:
        return ipo_data[ipo_data['S_INFO_NAME'] == x]['Ticker'].values[0]
    except:
        return np.nan
def calc_stat(root_path, date, save_path):
    df = pd.read_pickle(f'{root_path}{date}.pkl')
    res = pd.DataFrame()
    res['allday'] = df.groupby(['medianame','channel']).count()['id']
    df['hms'] = df['pubdate'].apply(lambda x : str(x).split(' ')[1]) # 当日的具体时分秒
    res['pm15pm21'] = df[(df['hms'] < '21:00:00') & (df['hms'] >= '15:00:00')].groupby(['medianame','channel']).count()['id']
    res['dt'] = pd.Timestamp(str(date))
    res = res.reset_index()
    res['Ticker'] = res['channel'].apply(map_Ticker)
    res = res[~res['Ticker'].isna()].set_index(['dt','Ticker'])
    res.to_pickle(f'{save_path}{date}.pkl')
    return res

from multiprocessing import Pool
pool = Pool(6)
start_date = '20230101'
end_date = '20250331'
task_list = []

start_date_ = pd.Timestamp(start_date)
end_date_ = pd.Timestamp(end_date)
date_list = [start_date_ + datetime.timedelta(days=i) for i in range((end_date_ - start_date_).days + 1)]
date_list = [i.strftime('%Y%m%d') for i in date_list]

for date in date_list:
    task_list.append(pool.apply_async(calc_stat, args=(root_path, date, save_path)))
pool.close()
pool.join()


