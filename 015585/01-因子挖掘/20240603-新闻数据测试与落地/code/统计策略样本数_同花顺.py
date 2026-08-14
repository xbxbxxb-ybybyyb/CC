import datetime
import pandas as pd
import os
import numpy as np
import IO
# europa basic file
def time_transfer(x):
    return datetime.datetime.fromtimestamp(int(x)).strftime("%Y-%m-%d %H:%M:%S")
def get_stock_list(x):
    res = []
    try:
        for i in eval(x)['stockInfo']:
            res.append(i['additionalParams']['hqCode'])
        return res
    except:
        return []
def split_stock_tags(df, col_name='related_stock'): # 根据tags里在沪深的股票，记录一行变为多行，每行代表一只股票
    df_tmp = df[['itemId',col_name]]
    df_tmp_columns_list = df_tmp.columns.tolist()
    df_tmp_columns_list.remove(col_name)
    df_tmp = (df_tmp.set_index(df_tmp_columns_list)[col_name].apply(pd.Series).stack().reset_index().drop('level_' + str(len(df_tmp_columns_list)), axis=1)
          .rename(columns={0: 'Ticker'}))
    df = pd.merge(df,df_tmp,how = 'outer',left_on='itemId',right_on='itemId')
    return df
res_dic = {}

for year in [str(x) for x in range(2024,2024+1)]:
    # print('prepare europa basic file')
    print(year)
    def cal_ul_price(pre_close_dataframe, ratio = 0.1):
        pre_close_dataframe = pre_close_dataframe.reset_index()
        after_824 = pre_close_dataframe['dt']>=pd.Timestamp('20200824')
        cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='30')
        kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='68')
        pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+ratio) + 0.5) / 100
        pre_close_dataframe.loc[(after_824 & cyb)| kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+2*ratio) + 0.5) / 100
        return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']
    md_data = IO.read_data([int(str(year + '0601')), int(str(year + '0630'))], columns=['amt', 'high','open','close','pre_close','vwap','adjfactor'],
                            alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['ul_price'] = cal_ul_price(md_data)
    md_data['trigger_price'] = md_data['ul_price'] - 0.01
    md_data['is_zt'] = (md_data['high'] >= md_data['ul_price']).apply(int)
    md_data['last_is_zt'] = md_data['is_zt'].unstack().shift(1).stack()
    # md_data = md_data.query('high >= trigger_price and open < ul_price and last_is_zt == 0')[['amt']].reset_index()
    md_data = md_data.query('close >= ul_price')[['amt']].reset_index()
    md_data = md_data[~md_data['Ticker'].str.contains('BJ')]
    # merge news data
    # print('merge news data')
    path = '/dfs/group/800463/data/news_data/ths_basicinfo/'
    news_data = pd.DataFrame()
    for i in os.listdir(path):
        if i.startswith(year):
            # print(i)
            data_i = pd.read_hdf(path + i)
            data_i['related_stock'] = data_i['entityLabel'].apply(lambda x: get_stock_list(x))
            data_i = split_stock_tags(data_i)
            news_data = pd.concat([news_data,data_i[['itemId','time','Ticker','title']]])

    for col in ['time']:
        news_data[col] = news_data[col].apply(lambda x: time_transfer(x))
    news_data['dt'] = news_data['time'].apply(lambda x :pd.Timestamp(str(x).split(' ')[0]))
    #
    res = pd.merge(md_data, news_data, left_on='Ticker', right_on='Ticker', how='left')
    res['is_value2'] = (res['dt_y'] == res['dt_x'])
    print('T日：', year)
    print(res.groupby(['dt_x', 'Ticker'])['is_value2'].sum().quantile([0.5]))
    num_zt = res.groupby(['dt_x', 'Ticker'])['is_value2'].sum().groupby('dt_x').count().mean()
    print('涨停股日均数量 from stat：', num_zt)
    print('涨停股日均数量 from md_data：', md_data.groupby('dt').count()['amt'].mean())
    num_hasnews = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['is_value2'].sum()).query('is_value2 >= 1').groupby(
        'dt_x').count().mean()['is_value2']
    print('T日涨停股T日有新闻覆盖的日均数量:', num_hasnews, num_hasnews / num_zt)
    df_IT_num = pd.read_pickle('/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/file/res_AINEWS_T_{}.pkl'.format(year))
    df_IT_num.columns = ['IT_news']
    df_ths_num = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['is_value2'].sum()).query('is_value2 >= 1')
    df_ths_num = pd.merge(df_ths_num,df_IT_num,left_index=True,right_index=True,how='left')
    print('T日日均增量覆盖股票数：',len(df_ths_num[df_ths_num['IT_news'].isna()]) / len(set(md_data['dt'])))
    for days in [5,10,20]:
    # for days in [5]:
        if year == '2024':
            if days == 5:
                md_data = md_data[md_data['dt'] >= pd.Timestamp('20240606')]
            if days == 10:
                md_data = md_data[md_data['dt'] >= pd.Timestamp('20240611')]
            if days == 20:
                md_data = md_data[md_data['dt'] >= pd.Timestamp('20240621')]
        num_zt = md_data.groupby('dt').count()['amt'].mean()
        md_data['dt_start'] = md_data['dt'].apply(lambda x : x - datetime.timedelta(days = days))
        res = pd.merge(md_data,news_data,left_on = 'Ticker',right_on = 'Ticker',how = 'left')
        res['is_value1'] = (res['dt_y'] < res['dt_x']) & (res['dt_y'] >= res['dt_start'])
        # res['is_value'] = (res['dt_y'] == res['dt_x'])
        res_dic[(year,days)] = res.groupby(['dt_x','Ticker'])['is_value1'].sum().quantile([0.5])
        print(year,days,)
        print(res.groupby(['dt_x','Ticker'])['is_value1'].sum().quantile([0.5]))
        num_hasnews_n = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['is_value1'].sum()).query('is_value1 >= 1').groupby(
            'dt_x').count().mean()['is_value1']
        print('T日涨停股T-{}日有新闻覆盖的日均数量:'.format(days), num_zt, num_hasnews_n, num_hasnews_n / num_zt)
        df_IT_num = pd.read_pickle('/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/file/res_AINEWS_T_{}_{}.pkl'.format(days, year))
        df_IT_num.columns = ['IT_news']
        df_ths_num = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['is_value1'].sum()).query('is_value1 >= 1')
        df_ths_num = pd.merge(df_ths_num,df_IT_num,left_index=True,right_index=True,how='left')
        print('T日日均增量覆盖股票数：',len(df_ths_num[df_ths_num['IT_news'].isna()]) / len(set(md_data['dt'])))
    # # 统计日均新闻数
    # print(year,'统计日均新闻数')
    # print(news_data[~news_data['itemId'].duplicated()].groupby('dt').count().mean())
    # # 统计日均覆盖A股数 & 日均新闻数（A股）
    # print(year,'统计日均覆盖A股数 & 日均新闻数（A股）')
    # md_data_all =  IO.read_data([20240601, 20240630], columns=['amt'],
    #                             alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # stock_list = list(set(md_data_all.reset_index()['Ticker']))
    # stock_list = [i for i in stock_list if 'BJ' not in i]
    # stock_list.sort()
    # news_data_tmp = news_data[~news_data['Ticker'].isna()]
    # news_data_tmp['is_A_stock'] = news_data_tmp['Ticker'].isin(stock_list)
    # news_data_tmp = news_data_tmp[news_data_tmp['is_A_stock']]
    # print(news_data_tmp.groupby('dt')['Ticker'].apply(lambda x : len(set(x))).mean())
    # print(news_data_tmp.groupby('dt')['itemId'].apply(lambda x : len(set(x))).mean())
    # # 统计A股数的增幅：取“信息技术部新闻未覆盖，但待测数据源覆盖”的股票数量，除以信息技术部覆盖的数量，取日均值
    # news_data_dt_stock = pd.DataFrame(news_data_tmp.groupby('dt')['Ticker'].apply(lambda x : set([i for i in set(x) if i in stock_list])))
    # news_data_dt_stock.columns = ['stock_set_ths']
    # news_data_dt_stock['stock_set_IT'] = 0
    # for dt in news_data_dt_stock.index:
    #     dt = dt.strftime('%Y%m%d')
    #     benchmark_path = '/dfs/group/800463/data/news_data/AI_newsdata/'
    #     df_benchmark = pd.read_pickle(benchmark_path + dt + '.pkl')
    #     news_data_dt_stock.loc[dt,'stock_set_IT'] = str(set([i for i in set(df_benchmark[df_benchmark['new_tags'] != 'nostock']['new_tags']) if i in stock_list]))
    # news_data_dt_stock['length_more_stock'] = (news_data_dt_stock['stock_set_ths'] - news_data_dt_stock['stock_set_IT'].apply(lambda x : eval(x))).apply(lambda x : len(x))
    # news_data_dt_stock['ratio'] = news_data_dt_stock['length_more_stock'] / news_data_dt_stock['stock_set_IT'].apply(lambda x : len(eval(x)))
    # print(news_data_dt_stock.mean())
    # # 去重后强势股T日新闻数量增幅:取待测数据源去重后的新闻，选择和已有新闻匹配度低于0.8的部分，筛选出T日Europa相关新闻数量，除以信息技术部新闻源T日Europa相关新闻数量
    # res = pd.merge(md_data, news_data, left_on='Ticker', right_on='Ticker', how='left')
    # res['is_value2'] = (res['dt_y'] == res['dt_x'])
    # list_delsimi_id = []
    # for file in os.listdir('/dfs/group/800463/data/news_data/ths_basicinfo_delsimi/'):
    #     if file.startswith('202406'):
    #         df_delsimi_date = pd.read_pickle('/dfs/group/800463/data/news_data/ths_basicinfo_delsimi/' + file)
    #         for newsID in df_delsimi_date[df_delsimi_date['max_similarity_ITnews'] >= 0.8]['itemId']:
    #             list_delsimi_id.append(newsID)
    # res = res[res['itemId'].isin(list_delsimi_id)]
    # print('去重后强势股T日新增新闻数量：', year)
    # print(res.groupby(['dt_x'])['is_value2'].sum().quantile([0.1, 0.25, 0.5]))
    # print(res.groupby(['dt_x'])['is_value2'].sum().mean())
    # print(res.groupby(['dt_x', 'Ticker'])['is_value2'].sum().quantile([0.1, 0.25, 0.5]))

