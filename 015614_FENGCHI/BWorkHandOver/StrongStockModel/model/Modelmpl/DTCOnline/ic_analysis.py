# @Time : 2021/1/22 9:09
# @Author : Zhichen Lu
# @File : ic_analysis.py
import pandas as pd
import os
from StrongStockModel.conf.path_config import root_path


ic_res = pd.read_pickle(root_path+'external_data/ic_half.pkl')
check = pd.DataFrame(ic_res)
std = check.groupby(level=0).std()
mean = check.groupby(level=0).mean()

std.index = [x+'_std' for x in std.index]
mean.index = [x+'_mean' for x in mean.index]

res = pd.concat([std,mean]).sort_index().T
res.to_excel(root_path+'external_data/ic_mean_std.xlsx')
check_corr  =mean.corr()
