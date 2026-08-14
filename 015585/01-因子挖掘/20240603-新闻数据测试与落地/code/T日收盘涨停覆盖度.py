import pandas as pd
import os
import IO
import numpy as np
#
def cal_ul_price(pre_close_dataframe, ratio = 0.1):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt']>=pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='68')
    pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+ratio) + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb)| kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+2*ratio) + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']
md_data_all =  IO.read_data([20240601, 20240630], columns=['amt','close','high','pre_close'],
                            alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data_all['ul_price'] = cal_ul_price(md_data_all, ratio = 0.1)
md_data_all = md_data_all[md_data_all['close'] >= md_data_all['ul_price']]
#
# res = pd.DataFrame(columns = ['num_all_stock','num_news_stock'])
# out_path = '/dfs/group/800463/data/news_data/AI_newsdata/'
# file_list = os.listdir(out_path)
# file_list = [i for i in file_list if i.replace('.pkl','') >= '20230101']
# file_list.sort()
# for file in file_list:
#     news_data = pd.read_pickle(out_path + file)
#     md_data = md_data_all.query('dt == "{}"'.format(file.replace('.pkl','')))
#     if len(md_data) > 0:
#         md_data = md_data[~md_data.index.get_level_values(1).str.contains('BJ')]
#         res.loc[file.replace('.pkl',''),'num_all_stock'] = len(md_data)
#         res.loc[file.replace('.pkl',''),'num_news_stock'] = len(set(news_data['new_tags']) & set(md_data.index.get_level_values(1)))
#         print(file,len(md_data),len(set(news_data['new_tags']) & set(md_data.index.get_level_values(1))))
# res['ratio'] = res['num_news_stock'] / res['num_all_stock']
# 观察新闻中提及概念的情况
for year in [str(i) for i in range(2024,2024+1)]:
    out_path = '/dfs/group/800463/data/news_data/AI_newsdata/'
    file_list = os.listdir(out_path)
    file_list = [i for i in file_list if i.replace('.pkl','') >= (year + '0601') and i.replace('.pkl','') <= (year + '0630')]
    file_list.sort()
    res = pd.DataFrame()
    for file in file_list:
        # print(file)
        news_data = pd.read_pickle(out_path + file)
        md_data = md_data_all.query('dt == "{}"'.format(file.replace('.pkl','')))
        if len(md_data) > 0:
            md_data = md_data[~md_data.index.get_level_values(1).str.contains('BJ')]
            news_data_filter = news_data[news_data['new_tags'].isin(list(md_data.index.get_level_values(1)))]
            news_data_filter = news_data_filter[~news_data_filter['id'].duplicated()]
            res = pd.concat([res,news_data_filter],axis=0)
    print(year)
    if len(res) > 0:
        print(res[res['content'].str.contains('概念')].shape)
        print(len(res[res['content'].str.contains('概念')]) / len(res))
    else:
        print('res == 0')
    # res[res['content'].str.contains('概念')].to_excel('/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/file/带“概念”的新闻.xlsx')