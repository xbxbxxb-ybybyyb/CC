# @Time : 2021/5/16 13:10
# @Author : Zhichen Lu
# @File : copy_file_to_sim.py

from online_conf import local_config_path,vol_info_path,hyper_param_path,matrix_conf,condition_path
import shutil
from dataApi.tradeDate import get_pre_trade_date
from ExtraTools import get_path_conf


import datetime
today = int(datetime.date.today().strftime('%Y%m%d'))
date = get_pre_trade_date(today)

path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3_ForExtra/')


shutil.copy(f'{vol_info_path}{date}.pkl',path_conf['vol_info_path']+f'{date}.pkl')
shutil.copy(f'{hyper_param_path}std{date}.pkl',path_conf['hyper_param_path']+f'std{date}.pkl')
shutil.copy(f'{hyper_param_path}mean{date}.pkl',path_conf['hyper_param_path']+f'mean{date}.pkl')
shutil.copy(f'{local_config_path}morning_model/val_sign/{get_pre_trade_date(date,-1)}.pkl',
            path_conf['local_config_path']+f'morning_model/val_sign/{get_pre_trade_date(date,-1)}.pkl')
shutil.copy(f'{matrix_conf}{date}.pkl',path_conf['matrix_conf']+f'{date}.pkl')
# shutil.copy(f'{condition_path}{date}.pkl',path_conf['condition_path']+f'{date}.pkl')
