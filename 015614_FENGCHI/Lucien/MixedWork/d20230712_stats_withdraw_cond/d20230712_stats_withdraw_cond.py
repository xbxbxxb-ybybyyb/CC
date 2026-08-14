# coding: utf-8
# Author：fengchi863
# Date ：2023/7/12 9:42
"""
统计成交记录中，形态2个股的买入时间
"""

import pandas as pd
import numpy as np
from dataApi.sendInfo import send_file

profit_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'
end_date = 20230711

europa_fpath = profit_path + 'Europa成交记录-20230711.xlsx'

europa_record = pd.read_excel(europa_fpath, sheet_name='累计卖出明细').query('是否全部卖出 == 1 &  "2022-05-18" <= 买入日期 <= "2023-05-18"')
pattern2_samples = europa_record.query('买入时形态 == 2')
pattern3_samples = europa_record.query('买入时形态 == 3')

res_df = pd.DataFrame(columns=['pattern2', 'pattern3'], index=['个数', '卖出部分盈利总金额', '卖出部分平均盈利', '卖出部分收益率(%)'])
res_df['pattern2'] = [pattern2_samples.shape[0], pattern2_samples['卖出部分盈利金额'].sum(), pattern2_samples['卖出部分盈利金额'].mean(), pattern2_samples['卖出部分收益率(%)'].mean()]
res_df['pattern3'] = [pattern3_samples.shape[0], pattern3_samples['卖出部分盈利金额'].sum(), pattern3_samples['卖出部分盈利金额'].mean(), pattern3_samples['卖出部分收益率(%)'].mean()]
res_df['合计'] = res_df.sum(axis=1)
send_file(res_df)

