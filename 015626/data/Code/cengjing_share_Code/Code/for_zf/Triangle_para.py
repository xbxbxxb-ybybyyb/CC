import pandas as pd
import numpy as np
import os
import multifactor.utility.common as ut
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from multifactor.IO import IO
import shutil

_,date,_ = check_update_date()
#source_root = '/data/user/011477/Trade_Docs/'
source_root = '/data/user/015626/data/share/para/'
target_root = '/data/user/015626/data/share/para/'
target_trader_root = '/data/user/011477/Trade_Docs/'

next_date = udt.get_trading_day_offset(str(date),[1])[0].strftime('%Y%m%d')
target_path = os.path.join(target_root,'Tri_%s' % next_date)
target_trader_path = os.path.join(target_trader_root, next_date, 'Tri_%s' % next_date)
#source_path = os.path.join(source_root, str(date), 'Tri_%s' % date)
source_path = os.path.join(source_root, 'Tri_%s' % date)
if not os.path.exists(target_path):
    os.makedirs(target_path)
    for x in os.listdir(source_path):
        if not x.endswith('xlsx'):
            continue
        new_name = x.replace(str(date), next_date)
        shutil.copyfile(os.path.join(source_path,x), os.path.join(target_path, new_name))
        print(os.path.join(source_path,x),' copied as ', os.path.join(target_path, new_name))
        
if not os.path.exists(target_trader_path):
    os.makedirs(target_trader_path)
    for x in os.listdir(source_path):
        if not x.endswith('xlsx'):
            continue
        new_name = x.replace(str(date), next_date)
        shutil.copyfile(os.path.join(source_path,x), os.path.join(target_trader_path, new_name))
        print(os.path.join(source_path,x),' copied as ', os.path.join(target_trader_path, new_name))

    
if 'PIN' in os.listdir(source_path):
    source_path = os.path.join(source_path, 'PIN')
    target_path = os.path.join(target_path, 'PIN')
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    for x in os.listdir(source_path):
        if not x.endswith('xlsx'):
            continue
        new_name = x.replace(str(date), next_date)
        shutil.copyfile(os.path.join(source_path,x), os.path.join(target_path, new_name))
        print(os.path.join(source_path,x),' copied as ', os.path.join(target_path, new_name))