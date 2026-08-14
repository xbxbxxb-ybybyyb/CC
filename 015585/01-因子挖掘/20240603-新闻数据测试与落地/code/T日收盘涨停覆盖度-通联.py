import sys

import pandas as pd
import os
import IO
import numpy as np
#
def split_stock_tags(df, col_name='ticker'): # 根据tags里在沪深的股票，记录一行变为多行，每行代表一只股票
    df_tmp = df[['newsID',col_name]]
    df_tmp_columns_list = df_tmp.columns.tolist()
    df_tmp_columns_list.remove(col_name)
    df_tmp = (df_tmp.set_index(df_tmp_columns_list)[col_name].apply(pd.Series).stack().reset_index().drop('level_' + str(len(df_tmp_columns_list)), axis=1)
          .rename(columns={0: 'new_' + col_name}))
    df = pd.merge(df,df_tmp,how = 'outer',left_on='newsID',right_on='newsID')
    return df
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
# 观察新闻中提及概念的情况
for year in [str(i) for i in range(2024,2024+1)]:
    out_path = '/dfs/group/800463/data/news_data/datayes_basicinfo/'
    file_list = os.listdir(out_path)
    file_list = [i for i in file_list if i.replace('.h5','') >= (year + '0101') and i.replace('.h5','') <= (year + '1231')]
    file_list.sort()
    res = pd.DataFrame()
    for file in file_list:
        sys.stdout.write('\r' + str(file))
        sys.stdout.flush()
        news_data = pd.read_hdf(out_path + file)
        news_data['ticker'] = news_data['ticker'].apply(
            lambda x: [i + '.SH' if i.startswith('6') else i + '.SZ' for i in eval(x)] if type(x) == str else [])
        news_data = split_stock_tags(news_data)

        md_data = md_data_all.query('dt == "{}"'.format(file.replace('.h5','')))
        if len(md_data) > 0:
            md_data = md_data[~md_data.index.get_level_values(1).str.contains('BJ')]
            news_data_filter = news_data[news_data['new_ticker'].isin(list(md_data.index.get_level_values(1)))]
            news_data_filter = news_data_filter[~news_data_filter['newsID'].duplicated()]
            df_content = pd.read_hdf('/dfs/group/800463/data/news_data/datayes_content/' + file)
            df_content['newsID'] = df_content['newsID'].apply(lambda x : int(x))
            news_data_filter = pd.merge(news_data_filter,df_content,left_on='newsID',right_on='newsID',how='left')
            res = pd.concat([res,news_data_filter],axis=0)
    print(year)
    res['newsBody'] = res['newsBody'].apply(lambda x : '' if type(x) != str else x)
    if len(res) > 0:
        print(res[res['newsBody'].str.contains('概念')].shape)
        print(len(res[res['newsBody'].str.contains('概念')]) / len(res))
    else:
        print('res == 0')
    # res[res['content'].str.contains('概念')].to_excel('/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/file/带“概念”的新闻.xlsx')