# coding: utf-8
# Author：fengchi863
# Date ：2022/5/17 14:13

"""
统计新旧申万一级行业的变化情况
"""

import pandas as pd
import numpy as np
from xquant.factordata import FactorData

from SimiStock.dataApi import indName, getData, tradeDate
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
fd = FactorData()

sw1_data = fd.get_factor_value('WIND_AShareSWIndustriesClass')
# sw1 = fd.hind('SW2021', 1)
# sw1['code'] = sw1['industry_code'].map(lambda x: x+'0'*12)
# index_sectors = fd.get_factor_value('WIND_IndexContrastSector')[['S_INFO_INDEXCODE',
#                                                                  'S_INFO_NAME', 'S_INFO_INDUSTRYCODE']]
# sw_index_sector = pd.merge(sw1, index_sectors, how='left', left_on='code', right_on='S_INFO_INDUSTRYCODE')
old_ind = list(indName.sw_level1.values())
new_ind = list(indName.sw2021_level1.values())

diff_ind1 = list(set(old_ind).difference(set(new_ind)))  # 删掉的
diff_ind2 = list(set(new_ind).difference(set(old_ind)))  # 新增的
common_ind = list(set(old_ind).intersection(set(new_ind)))  # 重合的

print('删掉的', ','.join(diff_ind1), '\n',
      '新增的', ','.join(diff_ind2), '\n',
      '重合的', ','.join(common_ind), '\n')
start_date = 20210101
end_date = 20220501
date_list = tradeDate.get_date_range(start_date, end_date)
sw1_old = getData.get_daily_1factor('SW1', date_list)
sw1_new = getData.get_daily_1factor('SW20211', date_list)

old_date = 20210729
new_date = 20210730
# 对于删掉的
delete_df = pd.DataFrame(index=diff_ind1, columns=['旧的'])
for ind1 in diff_ind1:
    _sw1_old = sw1_old.loc[old_date]
    _sw1_old = _sw1_old.apply(lambda x: indName.sw_level1[x] if ~np.isnan(x) else np.nan)
    old_list = _sw1_old[_sw1_old == ind1]
    delete_df.loc[ind1, '旧的'] = len(old_list)

# 对于新增的
add_df = pd.DataFrame(index=diff_ind2, columns=['新的'])
for ind2 in diff_ind2:
    _sw1_new = sw1_new.loc[new_date]
    _sw1_new = _sw1_new.apply(lambda x: indName.sw2021_level1[x] if ~np.isnan(x) else np.nan)
    new_list = _sw1_new[_sw1_new == ind2]
    add_df.loc[ind2, '新的'] = len(new_list)

# 对于重合的
common_df = pd.DataFrame(index=common_ind, columns=['旧的', '新的', '新增个数', '删除个数', '重合个数'])
for ind in common_ind:
    _sw1_old = sw1_old.loc[old_date]
    _sw1_old = _sw1_old.apply(lambda x: indName.sw_level1[x] if ~np.isnan(x) else np.nan)
    _sw1_new = sw1_new.loc[new_date]
    _sw1_new = _sw1_new.apply(lambda x: indName.sw2021_level1[x] if ~np.isnan(x) else np.nan)
    old_list = _sw1_old[_sw1_old == ind]
    new_list = _sw1_new[_sw1_new == ind]
    common_df.loc[ind, '旧的'] = len(old_list)
    common_df.loc[ind, '新的'] = len(new_list)
    common_df.loc[ind, '新增个数'] = len(set(new_list.index).difference(set(old_list.index)))
    common_df.loc[ind, '删除个数'] = len(set(old_list.index).difference(set(new_list.index)))
    common_df.loc[ind, '重合个数'] = len(set(new_list.index).intersection(set(old_list.index)))

output_dict = {
    '删掉的': delete_df,
    '新增的': add_df,
    '重合的': common_df
}
util.save_dict2xls(output_dict, other_stats_path, '新老申万行业分析.xlsx')
util.send_file(other_stats_path, '新老申万行业分析.xlsx')