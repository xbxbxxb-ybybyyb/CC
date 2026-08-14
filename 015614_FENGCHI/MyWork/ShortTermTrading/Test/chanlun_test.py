# coding: utf-8
# Author：fengchi863
# Date ：2020/9/29 15:10

import pandas as pd

val = pd.read_hdf('/data/group/800319/Faamonitor/回测数据/指数高低点.h5', 'SZZZ')
test = val.loc['202009011500']
pass