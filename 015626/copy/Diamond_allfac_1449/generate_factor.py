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

_,_,cdate_list = check_update_date(20240601, 20240801)
for date in cdate_list:
    executor_raw_factor(date, max_workers = 24, mode = 'history')
    print(date, 'done')
