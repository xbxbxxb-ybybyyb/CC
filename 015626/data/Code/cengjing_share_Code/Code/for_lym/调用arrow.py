import sys
# sys.path.insert(4,'/data/user/015626/data/share/Code/factor_baseclass/arrow/') # 因子框架
# sys.path.insert(4,'/data/user/015626/data/share/Code/factor_baseclass/arrow/factors/') # 因子代码路径，有4个示例
sys.path.insert(4,'/data/user/015626/data/share/Code/factor_baseclass/')
sys.path.insert(1,'/data/user/015626/JupyterNotebooks/utils/') # import multifactor 包的路径, 这里可以导入自己的包
from arrow.data_center import HistoryData, HotData
from arrow.factor_generator import *
from arrow.prepare_hot_data import *
import pandas as pd
import numpy as np
import datetime
import re, os, glob, math
import multifactor.utility.common as ut
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from multifactor.IO import IO
%matplotlib inline
import matplotlib.pyplot as plt
from tqdm import tqdm
from pandas.testing import assert_frame_equal, assert_series_equal


_,_,date_list = check_update_date(20230228,20230315)
for date in date_list:
    a = FactorGenerator()

    a.prepare_hist_data(date)
    a.dump_hist_data()
    PrepareHotData(date).get_all()
    executor_t_1_factor(date)
    fact = executor(date)