import sys
sys.path.insert(4, '/data/user/017024/share/overnight/factors/prod_26_new/')
sys.path.insert(4, './operators/')
sys.path.insert(4, './utils/')

import os
import time
import math
import ftplib
import pandas as pd
import numpy as np
import importlib
import datetime as dt
from multiprocessing import Pool
# from joblib import Parallel, delayed
import warnings
warnings.filterwarnings('ignore')

from factor_generator import FactorGenerator
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from utils.date_helper import *




fs = [f for f in os.listdir('/data/user/017024/share/overnight/factors/prod_26_new/') if f.endswith('.py')]
for f in fs:
    importlib.import_module(f[:-3])
    


if __name__ == '__main__':
    start_date = end_date = int(dt.datetime.now().strftime("%Y%m%d"))    

    prev_date = 20200101
    print(dt.datetime.now())
    print(prev_date, start_date, end_date)
    FactorGenerator().prepare_hot_data(prev_date, end_date)
    print(dt.datetime.now())
    subclass_list = FactorGenerator.__subclasses__()     
    print('factor count: ', len(subclass_list))
        
    for i, subcls in enumerate(subclass_list):
        print(i+1, subcls().__class__.__name__, dt.datetime.now())
        subcls(savepath='/data/user/017024/share/overnight/alpha_intraday/prod_26_new').__callback__(start_date, end_date)

    print(dt.datetime.now())


