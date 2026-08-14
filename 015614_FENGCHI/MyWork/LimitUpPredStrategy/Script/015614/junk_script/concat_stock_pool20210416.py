# coding: utf-8
# Author：fengchi863
# Date ：2021/4/16 21:28

'''
为了拼接我自己的分歧转一致板使用
'''

from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.dataApi import getData
import pandas as pd

file_name_list = ['fenqizhuanyizhi_%d.pkl' % i for i in range(1,5)]

res = pd.DataFrame()
for file_name in file_name_list:
    tmp = pd.read_pickle(junk_path + file_name)
    res = res.append(tmp, ignore_index=True)

res = res.sort_values([0,1,2])
print('drop前：', len(res))
res = res.drop_duplicates([0,1,2], keep='first')
res = res[res[0]>=20140101]
print('drop后：', len(res))

data = res[[0, 2]]
data[3] = True
data2 = data.set_index([0,2])
data3 = data2[3].unstack()
data3 = data3.fillna(False)
data3.to_pickle(junk_path + 'virga2consis_board20210419.pkl')

# limit_max = getData.get_daily_1factor('limit_max')
# high = getData.get_daily_1factor('high')
# limit_days = limit_max == high
#
# limit_days = limit_days.reindex_like(data3)
# board_res = limit_days & data3
# board_res2 = board_res.stack()
#
