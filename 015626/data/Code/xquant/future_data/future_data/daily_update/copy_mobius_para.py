import sys
sys.path.insert(1,'/data/user/015626/JupyterNotebooks/utils/')
import os, shutil
from multifactor.data.utils import *
import multifactor.utility.dt as udt
_,end_date,_ = check_update_date()
next_tday = udt.get_trading_day_offset(end_date, [1])[0].strftime('%Y%m%d')
para_root_path = '/data/user/016700/Data/para/'
target_path1 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/test_samples/Mobius_para/'
shutil.copytree(os.path.join(para_root_path, f'Mobius_{next_tday}'), os.path.join(target_path1, f'Mobius_{next_tday}'))
