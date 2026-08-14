# coding: utf-8
# Author：fengchi863
# Date ：2022/11/14 14:11

"""
复盘时提出的问题，统计被划分为申万行业的数量
"""

from LucienUtil import IO

start_date = 20220101
end_date = 20221111
data = IO.read_data([start_date, end_date], alt='/data/group/800463/fengc/daily/concept/jupiter_concept.h5')
jupiter_data = IO.read_data([start_date, end_date], alt='/data/group/800463/project/project1_prod/generalStrong_v3/Basic_zt/Basic_zt.h5')
data = data.reindex(index=jupiter_data.index)
data['SW'] = data['概念代码'].apply(lambda x: 1 if str(x).endswith('.SI') else 0)
data['SW'].sum() / len(data)