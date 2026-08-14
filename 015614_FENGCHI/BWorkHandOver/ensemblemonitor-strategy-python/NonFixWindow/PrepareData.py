# @Time : 2022/2/18 10:02
# @Author : Zhichen Lu
# @File : PrepareData.py
from ExtraTools import get_path_conf
# from online_conf import non_fix_path,non_fix_in_path,non_fix_output_path
from dataApi.tradeDate import get_date_range,get_pre_trade_date
import shutil,os

non_fix_path = '/data/group/800319/strategy_local_path_nonfixCondition/'
non_fix_930_path = f'{non_fix_path}FolderFor930/'
non_fix_in_path = f'{non_fix_path}daily_input/'

path_conf = get_path_conf('/data/user/015664/StrategyBackUp/strategy_local_path3DailyBackup/')

ratio_path,code_list_path,vol_info_path,hyper_param_path,matrix_conf,condition_path,init_conf_path,local_config_path = \
    [path_conf[x] for x in 'ratio_path,code_list_path,vol_info_path,hyper_param_path,matrix_conf,condition_path,init_conf_path,local_config_path'.split(',')]

start,end = 20220303,20220316
date_list = get_date_range(start,end)

for date in date_list:
    pre_date = get_pre_trade_date(date)
    target_path = f'{non_fix_in_path}{date}/'
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    shutil.copy(f'{code_list_path}{pre_date}.pkl',f'{target_path}code_list{pre_date}.pkl')
    # if os.path.exists(f'{vol_info_path}{pre_date}_backup.pkl'):
    #     shutil.copy(f'{vol_info_path}{pre_date}_backup.pkl',f'{target_path}vol_info{pre_date}.pkl')
    # else:
    #     shutil.copy(f'{vol_info_path}{pre_date}.pkl', f'{target_path}vol_info{pre_date}.pkl')
    shutil.copy(f'{matrix_conf}{pre_date}.pkl',f'{target_path}matrix{pre_date}.pkl')
    # shutil.copy(f'{condition_path}{pre_date}.pkl',f'{target_path}condition{pre_date}.pkl')
    # shutil.copy(f'{hyper_param_path}mean{pre_date}.pkl',f'{target_path}mean{pre_date}.pkl')
    # shutil.copy(f'{hyper_param_path}std{pre_date}.pkl',f'{target_path}std{pre_date}.pkl')
    shutil.copy(f'{local_config_path}restrict_list.pkl',f'{target_path}restrict_list{pre_date}.pkl')
    # shutil.copy(f'{local_config_path}index_map.pkl',f'{target_path}index_map{pre_date}.pkl')

