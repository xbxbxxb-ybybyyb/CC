import os
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import json
from xquant.xqutils.helper import link
from xquant.investment.strategyfile import *

model_name_list = ['if_v7c', 'if_v7_crn',  'ic_v7c','ic_v7unifac', 'ic_v7unifac_crn']
path_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/'
path_list = sorted(os.listdir(path_root))
wrong_holder = []

for model_name in model_name_list:
    temp_list = sorted([item for item in path_list if (item.endswith(model_name))])
    check_date = sorted(os.listdir(path_root + temp_list[-2] + '/model_value/model_raw/'))[3]
    

    raw_old = path_root + temp_list[-2] + '/model_value/model_raw/' + check_date + '/'
    
    date_for_new = (sorted(os.listdir(path_root + temp_list[-1] + '/model_value/model_raw/')))[0]
    
    raw_new = path_root + temp_list[-1] + '/model_value/model_raw/' + date_for_new + '/'
    
    for sub_model in os.listdir(raw_old):
        temp_raw_old = pd.read_pickle(raw_old + sub_model)
        temp_raw_new = pd.read_pickle(raw_new + sub_model)
        if abs((temp_raw_old.loc[check_date] - temp_raw_new.loc[check_date]).sum()).sum() != 0:
            wrong_holder.append([model_name, sub_model, check_date])

lm = link.LinkMessage()
if len(wrong_holder) > 0:
    for item in wrong_holder:      
        lm = link.LinkMessage()
        lm.sendMessage(str(item))
        del lm

else:
    lm.sendMessage('New Model Value Fine')

