# coding: utf-8
# Author：fengchi863
# Date ：2020/6/12 10:58

from conf.path_config import *
import pandas as pd

result = pd.read_pickle(junk_clf_path + 'fengchi/Signal1min_mlp_v4_20200710.pkl')
avg_price, deal_vol, record_dict, fulfill_percent, out_performance = result.values()
pfm = out_performance['all'].sum(axis=1) / 500000000
res = pfm.cumsum()
print('年化收益：', str(res.iloc[-1]))
print('日均收益：', str(pfm.mean()))
print('完成率：', str(fulfill_percent['all'].mean()))


# out_performance['buy'].to_excel(junk_clf_path + 'fengchi/out_performance_buy.xlsx')
# out_performance['all'].to_excel(junk_clf_path + 'fengchi/out_performance_all.xlsx')
# out_performance['sell'].to_excel(junk_clf_path + 'fengchi/out_performance_sell.xlsx')
#
# out_performance['sell'].loc[pd.to_datetime('20180723')].sort_values(ascending=False)
# record_df = record_dict['000523.SZ', '20180123']