import pandas as pd
import os
from xquant.factordata import FactorData
import IO
import numpy as np
s = FactorData()
suspension = s.get_factor_value('WIND_AShareTradingSuspension',S_DQ_SUSPENDDATE=['>=20230101', '<=20241111'])
# 筛选和并购重组有关的停复牌信息
'''['OBJECT_ID', 'S_INFO_WINDCODE', 'S_DQ_SUSPENDDATE', 'S_DQ_SUSPENDTYPE',
       'S_DQ_RESUMPDATE', 'S_DQ_CHANGEREASON', 'S_DQ_TIME',
       'S_DQ_CHANGEREASONTYPE', 'OPDATE', 'OPMODE']
'''
'''
204007000 204007015 股本重组生效
204011000 204011035 重大资产重组(港美上市/发债企业)
          204011046 并购重组筹划(收购方)
          204011047 并购重组筹划(标的方)
204023000 204023001 重大资产重组停牌
'''
text_filter1 = suspension['S_DQ_CHANGEREASON'].str.contains('并购')
text_filter2 = suspension['S_DQ_CHANGEREASON'].str.contains('重组')
code_filter1 = suspension['S_DQ_CHANGEREASONTYPE'] == 204007015
code_filter2 = suspension['S_DQ_CHANGEREASONTYPE'] == 204011035
code_filter3 = suspension['S_DQ_CHANGEREASONTYPE'] == 204011046
code_filter4 = suspension['S_DQ_CHANGEREASONTYPE'] == 204011047
code_filter5 = suspension['S_DQ_CHANGEREASONTYPE'] == 204023001
suspension_filtered = suspension[text_filter1 | text_filter2 | code_filter1 | code_filter2 | code_filter3 | code_filter4 | code_filter5]
suspension_filtered = suspension_filtered.sort_values(['S_INFO_WINDCODE','S_DQ_RESUMPDATE'])
# 筛选已复牌的
suspension_resumped = suspension_filtered[suspension_filtered['S_DQ_RESUMPDATE'] >= '19000101'].drop_duplicates(subset=['S_INFO_WINDCODE','S_DQ_RESUMPDATE'], keep='last')
# 统计行情信息
md = IO.read_data([20230101, 20241110],columns = ['adjfactor','close','pct_chg','pre_close','high','amt'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
# md = md.sort_values(['dt','Ticker'],ascending = False)

md = md.reset_index()
md_filter = md[md['Ticker'].isin(list(suspension_resumped['S_INFO_WINDCODE']))]
# zcz与bjs
after_824 = md_filter['dt'] >= pd.Timestamp('20200824')
cyb = md_filter['Ticker'].apply(lambda x: x[:2] == '30')
kcb = md_filter['Ticker'].apply(lambda x: x[:2] == '68')
bj = md_filter['Ticker'].apply(lambda x: x[-2:] == 'BJ')
md_filter['ul_price'] = np.floor(md_filter['pre_close'] * 100 * 1.1 + 0.5 + 1e-8) / 100
md_filter.loc[(after_824 & cyb) | kcb, 'ul_price'] = np.floor(md_filter['pre_close'] * 100 * 1.2 + 0.5 + 1e-8) / 100
md_filter.loc[bj, 'ul_price'] = np.floor(md_filter['pre_close'] * 100 * 1.3 + 1e-8) / 100
md_filter['is_zt'] = (md_filter['close'] == md_filter['ul_price']).apply(lambda x : 1 if x == True else 0)
#
md_filter['close_adj'] = md_filter['close'] * md_filter['adjfactor']
md_filter['pre_close_adj'] = md_filter['pre_close'] * md_filter['adjfactor']
md_filter = md_filter.set_index(['dt','Ticker'])
for lag in [3,5,10,20]:
    md_filter[f'close_adj_{lag}'] = md_filter['close_adj'].unstack().shift(-lag+1).stack().apply(lambda x : round(x,5))
    md_filter[f'pct_chg_{lag}'] = md_filter[f'close_adj_{lag}'] / md_filter['pre_close_adj'] - 1
md_filter['zt_num_last20'] = md_filter['is_zt'].unstack().rolling(21,1).sum().stack()
md_filter['zt_num_next20'] = md_filter['zt_num_last20'].unstack().shift(-20).stack()
#
suspension_resumped_sta = suspension_resumped.rename(columns = {'S_DQ_RESUMPDATE':'dt','S_INFO_WINDCODE':'Ticker',
                                                                'S_DQ_CHANGEREASON':'reason','S_DQ_CHANGEREASONTYPE':'reasoncode'})
suspension_resumped_sta = suspension_resumped_sta[['dt','Ticker','reason','reasoncode']]
suspension_resumped_sta['dt'] = suspension_resumped_sta['dt'].apply(lambda x : pd.Timestamp(x))
suspension_resumped_sta = suspension_resumped_sta.set_index(['dt','Ticker'])

res = pd.merge(suspension_resumped_sta,md_filter[['close','pct_chg','pct_chg_3','pct_chg_5','pct_chg_10','pct_chg_20','zt_num_next20']],left_index=True,right_index=True,how = 'left')
res.to_csv('res.csv')


