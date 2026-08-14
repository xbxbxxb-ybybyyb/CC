# coding: utf-8
# Author：fengchi863
# Date ：2022/4/13 16:17

"""
统计滚动时每隔一个周期的变化
替换率、空值率
"""

import pandas as pd

from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from SimiStock.dataApi import getData, tradeDate, indName
from FaaMonitor.Util.MyUtil import MyUtil

#%% 用来测试前后文件的初始对冲序列是否一致

# filename1 = '滚动_7_(8, 10)_(120, 5)_v3_95_20180101_20200630_result.pkl'
# filename2 = '叠加风格5_14_(8, 10)_v3_95_20180101_20200630_result.pkl'
# check1 = pd.read_pickle(hedge_path + filename1)
# check2 = pd.read_pickle(hedge_path + filename2)
# for idx in range(20):
#     tmp1 = check1[idx]['hedge_list'][0]['hedge_list']
#     tmp2 = check2[idx]['hedge_list']
#     assert tmp1 == tmp2[:len(tmp1)]

#%% 用来检测数据一致性，检测基础数据
filename1 = '叠加风格5_14_(8, 10)_v3_95_20200701_20210930_result.pkl_include_stk.pkl'
filename2 = '叠加风格5_14_(8, 10)_v3_95_20200701_20210630_result.pkl_include_stk.pkl'
check1 = pd.read_pickle(hedge_path + filename1)
check2 = pd.read_pickle(hedge_path + filename2)
for idx in range(419):
    tmp1 = check1[idx]
    tmp2 = check2[idx]
    assert tmp1 == tmp2
#%% 检测真实数据
filename1 = '叠加风格5_14_(6, 10)_v3_95_20200701_20210930_result.pkl'
filename2 = '叠加风格5_14_(6, 10)_v3_95_20200701_20210630_result.pkl'
check1 = pd.read_pickle(hedge_path + filename1)
check2 = pd.read_pickle(hedge_path + filename2)
for idx in range(419):
    tmp1 = check1[idx]['hedge_list']
    tmp2 = check2[idx]['hedge_list']
    assert tmp1 == tmp2
#%% 检测每个的数量
filename1 = '实时_7_(6, 10)_v3_95_20211001_20220415_result.pkl'
check1 = pd.read_pickle(hedge_path + filename1)
for idx in range(len(check1)):
    tmp1 = check1[idx]['hedge_list']
    print(check1[idx]['stk_id'])
    print(tmp1)
    # print(len(tmp1))
#%% 存进文件
filename1 = '实时_7_(6, 10)_v3_95_20211001_20220415_result.pkl'
check1 = pd.read_pickle(hedge_path + filename1)
ret_dict = dict()
for idx in range(len(check1)):
    tmp1 = check1[idx]['hedge_list']
    block_stk = MyUtil.get_1stock_name(check1[idx]['stk_id'])
    hedge_list = list(map(lambda x: MyUtil.get_1stock_name(x), tmp1))
    ret_dict[block_stk] = '，'.join(hedge_list)
    print(check1[idx]['stk_id'])
    print(tmp1)
ret_df = pd.Series(ret_dict)
ret_df.to_excel(hedge_path + '大宗交易预备池.xlsx')

#%%
# flag = '历史'
# start_date = 20180101
# end_date = 20200630
# file_name_dict = {
#     f'滚动_7_(8, 10)_(120, 5)_v3_95_{start_date}_{end_date}_result.pkl': (8, 5),
#     f'滚动_7_(7, 10)_(120, 5)_v3_95_{start_date}_{end_date}_result.pkl': (7, 5),
#     f'滚动_7_(8, 10)_(120, 10)_v3_95_{start_date}_{end_date}_result.pkl': (8, 10),
#     f'滚动_7_(7, 10)_(120, 10)_v3_95_{start_date}_{end_date}_result.pkl': (7, 10)}

flag = '未来'
start_date = 20200701
end_date = 20210630
file_name_dict = {
    f'滚动_7_(8, 10)_(120, 5)_v3_95_{start_date}_{end_date}_result.pkl': (8, 5),
    f'滚动_7_(7, 10)_(120, 5)_v3_95_{start_date}_{end_date}_result.pkl': (7, 5),
    f'滚动_7_(8, 10)_(120, 10)_v3_95_{start_date}_{end_date}_result.pkl': (8, 10),
    f'滚动_7_(7, 10)_(120, 10)_v3_95_{start_date}_{end_date}_result.pkl': (7, 10)}

sw1 = getData.get_daily_1factor('SW1', date_list=tradeDate.get_date_range(20171201, 20220401))

ret_dict = dict()
for file_name in list(file_name_dict.keys()):
    ret_list = list()
    stats_df = pd.DataFrame(index=[0])
    check = pd.read_pickle(hedge_path + file_name)
    for bd in check:    # 每一个大宗
        replace_time = 0
        blank_time = 0
        stk_id = bd['stk_id']
        trade_date = bd['date']
        ind_code = sw1.loc[trade_date, stk_id]
        ind_name = indName.sw_level1[ind_code]
        bd_hedge_list = bd['hedge_list']
        first_hedge_list = bd_hedge_list[0]['hedge_list']
        last_hedge_list = first_hedge_list
        for roll_hedge_list in bd_hedge_list[1:]:
            if roll_hedge_list['hedge_list'] != last_hedge_list:
                if roll_hedge_list['hedge_list']:
                    last_hedge_list = roll_hedge_list['hedge_list']
                    replace_time += 1
                else:
                    pass
            if not roll_hedge_list['hedge_list']:
                blank_time += 1
        ret_list.append([stk_id, trade_date, ind_name,
                         replace_time, replace_time / len(bd_hedge_list),
                         blank_time, blank_time / len(bd_hedge_list),
                         replace_time + blank_time, (replace_time + blank_time) / len(bd_hedge_list)])
    ret_df = pd.DataFrame(ret_list, columns=['股票代码', '交易日期', '申万一级行业',
                                             '替换次数', '替换率',
                                             '空值次数', '空值率',
                                             '替空次数', '替空率'])
    ret_dict.update({f'{file_name_dict[file_name]}明细': ret_df})
    # 统计次数
    stats_df['replace>=1'] = len(ret_df.query('替换次数 >= 1')) / len(ret_df)
    stats_df['replace>=2'] = len(ret_df.query('替换次数 >= 2')) / len(ret_df)
    stats_df['replace>=3'] = len(ret_df.query('替换次数 >= 3')) / len(ret_df)
    stats_df['replace>=4'] = len(ret_df.query('替换次数 >= 4')) / len(ret_df)
    stats_df['blank>=1'] = len(ret_df.query('空值次数 >= 1')) / len(ret_df)
    stats_df['blank>=3'] = len(ret_df.query('空值次数 >= 3')) / len(ret_df)
    stats_df['blank>=5'] = len(ret_df.query('空值次数 >= 5')) / len(ret_df)
    stats_df['blank>=10'] = len(ret_df.query('空值次数 >= 10')) / len(ret_df)
    stats_df['rb_time>=1'] = len(ret_df.query('替空次数 >= 1')) / len(ret_df)
    stats_df['rb_time>=3'] = len(ret_df.query('替空次数 >= 3')) / len(ret_df)
    stats_df['rb_time>=5'] = len(ret_df.query('替空次数 >= 5')) / len(ret_df)
    stats_df['rb_time>=10'] = len(ret_df.query('替空次数 >= 10')) / len(ret_df)
    stats_df['rb_time>=15'] = len(ret_df.query('替空次数 >= 15')) / len(ret_df)
    ret_dict.update({f'{file_name_dict[file_name]}汇总': stats_df.T})
    # 检测滚动过程中空值的次数
    ret_df['replace >= 1'] = ret_df['替换次数'] >= 1
    ret_df['replace >= 2'] = ret_df['替换次数'] >= 2
    ret_df['replace >= 3'] = ret_df['替换次数'] >= 3
    ret_df['replace >= 4'] = ret_df['替换次数'] >= 4
    ret_df['blank >= 1'] = ret_df['空值次数'] >= 1
    ret_df['blank >= 3'] = ret_df['空值次数'] >= 3
    ret_df['blank >= 5'] = ret_df['空值次数'] >= 5
    ret_df['blank >= 10'] = ret_df['空值次数'] >= 10
    ret_df['rb_time >= 1'] = ret_df['替空次数'] >= 1
    ret_df['rb_time >= 3'] = ret_df['替空次数'] >= 3
    ret_df['rb_time >= 5'] = ret_df['替空次数'] >= 5
    ret_df['rb_time >= 10'] = ret_df['替空次数'] >= 10
    ret_df['rb_time >= 15'] = ret_df['替空次数'] >= 15
    a = ret_df.groupby(['申万一级行业'])[['replace >= 1',
                                    'replace >= 2',
                                    'replace >= 3',
                                    'replace >= 4',
                                    'blank >= 1',
                                    'blank >= 3',
                                    'blank >= 5',
                                    'blank >= 10',
                                    'rb_time >= 1',
                                    'rb_time >= 3',
                                    'rb_time >= 5',
                                    'rb_time >= 10',
                                    'rb_time >= 15']].sum()
    b = ret_df.groupby(['申万一级行业'])[['replace >= 1',
                                    'replace >= 2',
                                    'replace >= 3',
                                    'replace >= 4',
                                    'blank >= 1',
                                    'blank >= 3',
                                    'blank >= 5',
                                    'blank >= 10',
                                    'rb_time >= 1',
                                    'rb_time >= 3',
                                    'rb_time >= 5',
                                    'rb_time >= 10',
                                    'rb_time >= 15']].count()
    a = a.reindex(index=list(indName.sw_level1.values()))
    b = b.reindex(index=list(indName.sw_level1.values()))
    ind_stats_df = a / b
    ind_stats_num_df = a
    ret_dict.update({f'{file_name_dict[file_name]}行业汇总': ind_stats_df})
    ret_dict.update({f'{file_name_dict[file_name]}行业空值个数': a})
    ret_dict.update({f'{file_name_dict[file_name]}行业总个数': b})
util.save_dict2xls(ret_dict, hedge_path, f'滚动分析{flag}.xlsx')