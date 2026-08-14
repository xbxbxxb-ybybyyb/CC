# @Time : 2021/1/21 19:44
# @Author : Zhichen Lu
# @File : ic_select_factor.py
import pandas as pd
import os
from tqdm import tqdm
from multiprocessing import Pool,Manager
from StrongStockModel.conf.path_config import root_path

using_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')
res_path = '/data/group/800319/HFfactor/RealTimeFixRollRobust/result/'
file_list = os.listdir(res_path)

tag = 'ic_all'

ic_res = Manager().dict()
# def get_ic(each):
#     res = pd.read_pickle(res_path+each)
#     target_key = ['ic_half_dtc', 'ic_half_dt', 'ic_half_tc', 'ic_half_dc', 'ic_half_d',
#                   'ic_half_t', 'ic_half_c']
#     temp_stat = {x:res[x] for x in target_key}
#     temp_stat = pd.DataFrame(temp_stat,index=res['date_half_year_ends'])
#     temp_stat = temp_stat.stack()
#     ic_res[each] = temp_stat.swaplevel(0,1)
#     print(each,'done')
def get_ic(each):
    res = pd.read_pickle(res_path+each)
    target_key = ['ic_all_dtc', 'ic_all_dt', 'ic_all_tc', 'ic_all_dc', 'ic_all_d',
                  'ic_all_t', 'ic_all_c']
    temp_stat = {x:res[x] for x in target_key}
    temp_stat = pd.Series(temp_stat)

    ic_res[each] = temp_stat#.swaplevel(0,1)
    print(each,'done')
pool = Pool(10)
pool.map(get_ic,file_list)
pool.close()
pool.join()

pd.to_pickle(ic_res._getvalue(),root_path+'external_data/ic_all.pkl')
