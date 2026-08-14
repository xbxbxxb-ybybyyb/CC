# coding: utf-8
# Author：fengchi863
# Date ：2020/5/25 9:38

from FaaMonitor.Util.tools import send_file
import pandas as pd
import os

path = '/data/group/800080/Apollo/AlphaDataBase/'
df = pd.read_pickle(path + 'index/high.pkl')
print(1)
