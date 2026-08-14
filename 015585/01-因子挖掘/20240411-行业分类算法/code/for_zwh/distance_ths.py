import pandas as pd
import os
import numpy as np
'''
对同花顺数据在T-1日全市场计算个股距离
'''
# 同花顺
ths_correlation = pd.read_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/res_theme_stock_xquant.pkl')
'''
'''
list_del = [
'30109',
'32619',
'32557',
'32503',
'32061',
'31976',
'31037',
'30442',
'30360',
'32690',
'30213',
'30003',
'32577',
'31828',
'30665',
'30658',
'32533',
'32923',
'31930',
'30088',
'32664',
'60023',
'32666',
        ] # 删去特别通用或无意义的概念
list_del = ['000' + i for i in list_del]
ths_correlation = ths_correlation[~ths_correlation['themeID'].isin(list_del)]
ths_basicinfo = pd.read_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/ths_theme_basicinfo_xquant.pkl')
ths_basicinfo = ths_basicinfo[['themeID','themeName']].drop_duplicates()
#
def generate_contact_ratio(date,out_path):
    # date这里为T-1日日期
    from xquant.factordata import FactorData
    s = FactorData()
    date_T = str(s.tradingday(str(date), 2)[-1])
    if not os.path.exists(out_path + date_T + '.pkl'):
        try:
            ths_correlation_date = ths_correlation.loc[pd.Timestamp(date)].reset_index()
            ths_correlation_date['is_member'] = 1
            ths_correlation_date = ths_correlation_date.drop_duplicates()
            # 重合度
            '''
            1、股票有重合概念(即数目>0)，计算共同概念占比
            2、计算所属主题的重合度：对个股A的每一个主题，计算其和个股B的每个主题重合度的max；对个股B同理，计算两次max序列的均值；
            '''
            def col_distance(distance_themeID):
                matrix = np.matrix(distance_themeID.fillna(0))
                res = pd.DataFrame(matrix * matrix.T)
                res.columns = distance_themeID.index
                res.index = distance_themeID.index
                return res
            # 直接计算个股重合度
            distance_themeID = ths_correlation_date.set_index(['Ticker','themeID'])['is_member'].unstack()
            res_common_stock = col_distance(distance_themeID)
            mat = np.matrix(distance_themeID.sum(axis=1)).T
            res = pd.DataFrame(mat * np.ones((1,mat.shape[0])))
            res.index = res_common_stock.index
            res.columns = res_common_stock.columns
            res = res_common_stock / (res + res.T - res_common_stock)
            # 储存结果
            print(date,date_T)
            res.to_pickle(out_path + date_T + '.pkl')
        except:
            print('T-1 = {}, 生成错误'.format(date))
    return
# #------------------------------------------------------------------------------------------------------------
file_list = [i.replace('.pkl','') for i in os.listdir('/data/group/800463/data/project1_prod/tick_europa/')]
date_list = []
for i in file_list:
    if i >='20151220' and i <='20240331':
        date_list.append(i)
date_list.sort()
out_path = '/dfs/user/015585/999_sharefiles/01_relationship_on_conception/market_contact_ratio/'
from joblib import Parallel, delayed
factor_df_list = Parallel(n_jobs=10)(delayed(generate_contact_ratio)(date, out_path) for date in date_list)

