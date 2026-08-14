# coding: utf-8
# Author：fengchi863
# Date ：2020/8/31 11:06

import pandas as pd

from BullClient.conf.path_conf import fc_out_path, stock_type_path

# 读取陶鑫生成的首次买入
deal = pd.read_excel(fc_out_path + '陶鑫_逐日收益统计.xlsx', sheet_name='个股开平仓周期收益', index_col=0)
deal = deal.reset_index(drop=True)

# 读取股票分类结果
type_1_1 = pd.read_pickle(stock_type_path + 'type_1_1.pkl')
type_1_2 = pd.read_pickle(stock_type_path + 'type_1_2.pkl')
type_2 = pd.read_pickle(stock_type_path + 'type_2.pkl')
type_3 = pd.read_pickle(stock_type_path + 'type_3.pkl')
type_4 = pd.read_pickle(stock_type_path + 'type_4.pkl')
type_5 = pd.read_pickle(stock_type_path + 'type_5.pkl')
type_6 = pd.read_pickle(stock_type_path + 'type_6.pkl')
type_7 = pd.read_pickle(stock_type_path + 'type_7.pkl')

deal['type_1_1'] = deal[['股票代码', '买入日期']].apply(lambda x: '是' if type_1_1.loc[x['买入日期'], x['股票代码']] else '否', axis=1)
deal['type_1_2'] = deal[['股票代码', '买入日期']].apply(lambda x: '是' if type_1_2.loc[x['买入日期'], x['股票代码']] else '否', axis=1)
deal['type_2'] = deal[['股票代码', '买入日期']].apply(lambda x: '是' if type_2.loc[x['买入日期'], x['股票代码']] else '否', axis=1)
deal['type_3'] = deal[['股票代码', '买入日期']].apply(lambda x: '是' if type_3.loc[x['买入日期'], x['股票代码']] else '否', axis=1)
deal['type_4'] = deal[['股票代码', '买入日期']].apply(lambda x: '是' if type_4.loc[x['买入日期'], x['股票代码']] else '否', axis=1)
deal['type_5'] = deal[['股票代码', '买入日期']].apply(lambda x: '是' if type_5.loc[x['买入日期'], x['股票代码']] else '否', axis=1)
deal['type_6'] = deal[['股票代码', '买入日期']].apply(lambda x: '是' if type_6.loc[x['买入日期'], x['股票代码']] else '否', axis=1)
deal['type_7'] = deal[['股票代码', '买入日期']].apply(lambda x: '是' if type_7.loc[x['买入日期'], x['股票代码']] else '否', axis=1)

deal.to_excel(stock_type_path + '个股单次交易的首次买入时特征分类.xlsx')

target_str = 'type_7'
print(deal.groupby([target_str]).size())
deal.groupby([target_str]).size() / len(deal)
