# coding: utf-8
# Author：fengchi863
# Date ：2023/7/11 11:05

import pandas as pd
from Zeus.Europa.v2_0_10.path_conf import *

root_path = '/data/user/015614/Zeus/pred/Europa/v2_0_10/LgbRegModel/'

signal1 = pd.read_csv(root_path + '20191001~20200331_LgbRegModel_v1.csv')
signal2 = pd.read_csv(root_path + '20200401~20201231_LgbRegModel_v1.csv')
# signal3 = pd.read_csv(root_path + '20200401~20200930_LgbRegModel_v2.csv')
signal4 = pd.read_csv(root_path + '20201001~20210630_LgbRegModel_v2.csv').query('20210101 <= datelist <= 20210630')
signal5 = pd.read_csv(root_path + '20201001~20210331_LgbRegModel_v3.csv')
signal6 = pd.read_csv(root_path + '20210401~20211231_LgbRegModel_v3.csv').query('20210701 <= datelist <= 20211231')

concat_df = pd.concat([signal1, signal2, signal4, signal6], axis=0)
concat_df.to_csv('/data/user/015614/Zeus/pred/Europa/v2_1_0/XgbFSV8RegModel/' + 'all_pred0.csv')


