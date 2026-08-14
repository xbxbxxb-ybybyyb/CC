import os
import pickle
import numpy as np
import pandas as pd
from math import isnan
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from alphagen_qlib.calculator import QLibStockDataCalculator
from alphagen_qlib.utils import load_alpha_pool_by_path, load_recent_data
from alphagen.data.expression import *
from alphagen_qlib.stock_data import StockData, FeatureType, TargetType

# POOL_PATH = '/DATA/xuehy/logs/kdd_csi300_20_4_20230410071036/301056_steps_pool.json'
# POOL_PATH = "/data/user/000021/gjx/alphagen-change-reward存档8.7反正还没改feature，这个能跑但结果不太理想/path/for/checkpoints/new_100_2_20240815165001/262144_steps_pool.json"
POOL_PATH = '/data/user/000021/gjx/alphagen-high时序也用filter版本/path/for/checkpoints/new_100_2_20240820005940/55296_steps_pool.json'
# data, latest_date = load_recent_data(instrument='csi300', window_size=365, offset=1)

exprs = load_alpha_pool_by_path(POOL_PATH)
print(exprs)

POOL_PATH = '/data/user/000021/gjx/alphagen-high时序也用filter版本/path/for/checkpoints/new_100_2_20240821183739/55296_steps_pool.json'
# data, latest_date = load_recent_data(instrument='csi300', window_size=365, offset=1)

exprs = load_alpha_pool_by_path(POOL_PATH)
print(exprs)