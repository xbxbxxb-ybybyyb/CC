# coding: utf-8
# Author：fengchi863
# Date ：2020/6/30 8:56

import pandas as pd
import os
from conf.path_config import *
from System.ReadFileData import get_tick_data

# 检测有没有信号
# signal = pd.read_pickle(
#         junk_clf_path + 'predict_signal_lr_rise_down_zero_1min_from2017_selected50factor_20200611.pkl')

tick = get_tick_data(2422, 20180103)
pass