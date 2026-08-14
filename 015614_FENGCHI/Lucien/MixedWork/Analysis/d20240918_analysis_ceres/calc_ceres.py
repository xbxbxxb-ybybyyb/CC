# coding: utf-8
# Author：fengchi863
# Date ：2024/9/18 17:43

from dataApi.sendInfo import *
import pandas as pd
import numpy as np

ceres_samples = pd.read_pickle('/data/group/800463/sunss/ceres/20240807/factor_df_931_20160101_20201130.pkl')

label_list = list(filter(lambda x: x.startswith('label_'), ceres_samples.columns.tolist()))
ceres_samples = pd.read_