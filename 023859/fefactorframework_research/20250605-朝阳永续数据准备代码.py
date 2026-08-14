import pandas as pd
from h5data.IO import IO
import numpy as np
from xquant.factordata import FactorData
s = FactorData()

start_date = '20210101'
end_date = '20231231'
save_path = '/dfs/group/800463/data/xdb_data_lag3_new/'
strategy = 'neptunelong'
table_list = [
    'DWD_EXP_RESEARCHREPORT',
    'DWD_EXP_REPORTRATINGADJ',
    'DWD_EXP_REPORTTARGETPRICEADJ',
    'DWD_EXP_RESEARCHREPORTADJ']
basic_file = pd.read_pickle('/dfs/user/023859/neptune/basic_file_neptune_all_20160101_20250630.pkl')
# basic_file = pd.read_pickle('/dfs/user/023859/share_file/for_sss/basic_file_zz1000_20160101_20250630.pkl')
root_path = '/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/'
# ==============================================================================================================
tradingday_list = s.tradingday(start_date, end_date)
path_dic = dict(zip(table_list, [f'{root_path}{x}/{x}.h5' for x in table_list]))
file_dic = dict(zip(table_list, [IO.read_data([20120101,20250630], alt = path_dic[x]) for x in table_list]))


def subtract_three_years(date_str):
    import datetime
    import calendar
    date_obj = datetime.datetime.strptime(date_str, "%Y%m%d")
    new_year = date_obj.year - 3
    new_month = date_obj.month
    new_day = date_obj.day
    last_day = calendar.monthrange(new_year, new_month)[1]
    adjusted_day = min(new_day, last_day)
    new_date = date_obj.replace(year=new_year, day=adjusted_day)
    return new_date.strftime("%Y%m%d")
# for tradingday in tradingday_list:
def get_zyyx_date(tradingday, strategy, type, save_path):
    try:
        print(tradingday, strategy, type)
        basic_file_date = basic_file.loc[pd.Timestamp(tradingday):pd.Timestamp(tradingday)]
        stock_list = list(set(basic_file_date.index.get_level_values(1)))
        df_zyyx = file_dic[type].reset_index()
        # 根据tradingday获取最近3年的数据
        tradingday_3yearbefore = subtract_three_years(tradingday)
        df_zyyx_date = df_zyyx[(df_zyyx['dt'] < pd.Timestamp(tradingday)) & (df_zyyx['dt'] >= pd.Timestamp(tradingday_3yearbefore))]
        # 筛选票池
        df_zyyx_date = df_zyyx_date[df_zyyx_date['Ticker'].isin(stock_list)]
        #
        df_zyyx_date = df_zyyx_date.rename(columns = {'dt':'MDDate'})
        df_zyyx_date['MDDate'] = df_zyyx_date['MDDate'].apply(lambda x : x.strftime('%Y%m%d'))
        df_zyyx_date['dt'] = pd.Timestamp(tradingday)
        df_zyyx_date = df_zyyx_date.set_index(['dt','Ticker'])
        if 'FORECASTYEAR' in df_zyyx_date.columns:
            df_zyyx_date = df_zyyx_date.sort_values(['dt','Ticker','MDDate','REPORTID','FORECASTYEAR'])
        else:
            df_zyyx_date = df_zyyx_date.sort_values(['dt','Ticker','MDDate','REPORTID'])
        df_zyyx_date = df_zyyx_date.drop(['ID','SECUABBR','ENTRYTIME','UPDATETIME','UPDATEID','RESOURCEID','RECORDID'],axis=1)
        df_zyyx_date.to_pickle(f'{save_path}{strategy}/{type.replace("DWD_EXP","xdb").lower()}/{tradingday}.pkl')
    except:
        print(tradingday, strategy, type, '未成功保存，请检查！！！！')
    return
# ======================================================================================================
from multiprocessing import Pool
import os
pool = Pool(30)
task_list = []
# 构造目录
for type in table_list:
    if not os.path.exists(f'{save_path}{strategy}/{type.replace("DWD_EXP","xdb").lower()}'):
        os.makedirs(f'{save_path}{strategy}/{type.replace("DWD_EXP","xdb").lower()}')

for tradingday in tradingday_list:
    for type in table_list:
        task_list.append(pool.apply_async(get_zyyx_date, args=(tradingday, strategy, type, save_path)))
pool.close()
pool.join()

