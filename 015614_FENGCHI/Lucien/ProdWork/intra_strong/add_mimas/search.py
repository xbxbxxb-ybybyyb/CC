# coding: utf-8
# Author：fengchi863
# Date ：2023/12/8 9:47

import pandas as pd

europa = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/Europa成交记录-20231206.xlsx', sheet_name='累计买入明细')
jupiter = pd.read_excel('/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/jupiter成交记录-20231206.xlsx', sheet_name='累计买入明细')


check1 = europa.query('成交数量==0')[['发生日期', '证券代码']].set_index('发生日期').to_dict()['证券代码']
check2 = jupiter.query('成交数量!=0')[['发生日期', '证券代码']].set_index('发生日期').to_dict()['证券代码']
check1 = list(zip(check1.keys(), check2.values()))
check2 = list(zip(check2.keys(), check2.values()))
set(check1).intersection(set(check2))

check1 = europa.query('成交数量!=0')[['发生日期', '证券代码']].set_index('发生日期').to_dict()['证券代码']
check2 = jupiter.query('成交数量==0')[['发生日期', '证券代码']].set_index('发生日期').to_dict()['证券代码']
check1 = list(zip(check1.keys(), check2.values()))
check2 = list(zip(check2.keys(), check2.values()))
set(check1).intersection(set(check2))
