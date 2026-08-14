# @Time : 2021/1/14 19:56
# @Author : Zhichen Lu
# @File : check_daily_output.py
import pandas as pd
from online_conf import daily_out_path
import os

os.listdir(daily_out_path + '20210114_Xtrader/')

check = pd.read_pickle(daily_out_path + '20210114_Xtrader/pred_signal_1000.pkl')
