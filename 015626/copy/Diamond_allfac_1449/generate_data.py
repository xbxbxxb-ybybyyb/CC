import sys, os, importlib, datetime, glob
sys.path.insert(4, '/dfs/user/015626/JupyterNotebooks/utils/')
sys.path.insert(4, '/data/user/015626/data/Code/git_space/diamond_research_all/Diamond_allfac_1449/')
# sys.path.insert(4, '/data/user/015626/data/Code/git_space/diamond_research_all/Diamond_allfac_1449/overnight/')
from multifactor.IO import IO
from multifactor.data.utils import *
import pandas as pd
import numpy as np
from overnight.naming_config import *
from overnight.factor_generator import *
from overnight.prepare_hot_dummy import prepare_hot_dummy
from multiprocessing import Pool

def get_data(date):
    try:
        print(date)
        prepare_hot_dummy(date)
        
        a = FactorGenerator()
        a.prepare_hist_data(trade_date=date, hisdays=15)
        a.dump_hist_data()
        del(a)
        print(date, 'done')
    except Exception as e:
        print(date, e)
        
_,_,cdate_list = check_update_date(20240601, 20240801)
#cdate_list.reverse()
#for date in cdate_list:
#    get_data(date)
with Pool(5) as pool:
    pool.map(get_data, cdate_list)