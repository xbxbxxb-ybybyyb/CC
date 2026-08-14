# coding: utf-8
# Author：fengchi863
# Date ：2024/9/3 20:12

import importlib
import pandas as pd
import numpy as np
from Zeus.Saturn.v5_0_3.config.path_conf import *
from Zeus.Saturn.v5_0_3.config.strat_conf import *

def fetch_label(config_flag):
    module_name = f'Zeus.Saturn.v5_0_3.config.path_conf'
    module = importlib.import_module(module_name)
    PT = getattr(module, config_flag)
    label = PT['label']
    data_df = pd.read_pickle(f'/data/user/015614/Zeus/label/{STRATEGY_NAME}/{STRATEGY_VERSION}/{label}.pkl')
    return data_df[[label]]
