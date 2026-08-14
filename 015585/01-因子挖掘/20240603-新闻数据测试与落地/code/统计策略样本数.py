import datetime
import pandas as pd
import os
import numpy as np
import IO
# europa basic file

res_dic = {}
for year in [str(i) for i in range(2024,2024+1)]:
    # print('prepare europa basic file')
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
    path = '/dfs/group/800463/data/news_data/AI_newsdata/'
    news_data = pd.DataFrame()
    for i in os.listdir(path):
        if i.startswith(year+'06'):
            print(i)
            news_data = pd.concat([news_data,pd.read_pickle(path + i)[['id','pubDate','new_tags','textTitle']]])
    news_data['dt'] = news_data['pubDate'].apply(lambda x :pd.Timestamp(str(x).split(' ')[0]))
    #
    res = pd.merge(md_data, news_data, left_on='Ticker', right_on='new_tags', how='left')
    res['is_value2'] = (res['dt_y'] == res['dt_x'])
    print('T日：', year)
    print(res.groupby(['dt_x', 'Ticker'])['is_value2'].sum().quantile([0.5]))
    num_zt = res.groupby(['dt_x', 'Ticker'])['is_value2'].sum().groupby('dt_x').count().mean()
    print('涨停股日均数量 from stat：',num_zt)
    print('涨停股日均数量 from md_data：',md_data.groupby('dt').count()['amt'].mean())
    num_hasnews = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['is_value2'].sum()).query('is_value2 >= 1').groupby('dt_x').count().mean()['is_value2']
    print('T日涨停股T日有新闻覆盖的日均数量:',num_hasnews,num_hasnews/num_zt)
    pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['is_value2'].sum()).query('is_value2 >= 1').to_pickle('/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/file/res_AINEWS_T_{}.pkl'.format(year))
    for days in [5,10,20]:
        if year == '2024':
            if days == 5:
                md_data = md_data[md_data['dt'] >= pd.Timestamp('20240606')]
            if days == 10:
                md_data = md_data[md_data['dt'] >= pd.Timestamp('20240611')]
            if days == 20:
                md_data = md_data[md_data['dt'] >= pd.Timestamp('20240621')]
        num_zt = md_data.groupby('dt').count()['amt'].mean()
        md_data['dt_start'] = md_data['dt'].apply(lambda x : x - datetime.timedelta(days = days))
        res = pd.merge(md_data,news_data,left_on = 'Ticker',right_on = 'new_tags',how = 'left')
        res['is_value1'] = (res['dt_y'] < res['dt_x']) & (res['dt_y'] >= res['dt_start'])
        res_dic[(year,days)] = res.groupby(['dt_x','Ticker'])['is_value1'].sum().quantile([0.5])
        print('T-N日：',year,'N=',days,)
        print(res.groupby(['dt_x','Ticker'])['is_value1'].sum().quantile([0.5]))
        num_hasnews_n = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['is_value1'].sum()).query('is_value1 >= 1').groupby('dt_x').count().mean()['is_value1']
        print('T日涨停股T-{}日有新闻覆盖的日均数量:'.format(days), num_zt,num_hasnews_n,num_hasnews_n/num_zt)
        pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['is_value1'].sum()).query('is_value1 >= 1').to_pickle(
            '/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/file/res_AINEWS_T_{}_{}.pkl'.format(days,year))

    # # 统计日均新闻数
    # print('日均新闻数',year)
    # print(news_data[~news_data['id'].duplicated()].groupby('dt').count().mean())
    # # 统计日均覆盖A股数 & 日均新闻数（A股）
    # print('统计日均覆盖A股数 & 日均新闻数（A股）')
    # md_data_all =  IO.read_data([20240601, 20240630], columns=['amt'],
    #                             alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # stock_list = list(set(md_data_all.reset_index()['Ticker']))
    # stock_list = [i for i in stock_list if 'BJ' not in i]
    # stock_list.sort()
    # news_data_tmp = news_data[news_data['new_tags'] != 'nostock']
    # news_data_tmp['is_A_stock'] = news_data_tmp['new_tags'].isin(stock_list)
    # news_data_tmp = news_data_tmp[news_data_tmp['is_A_stock']]
    # print('覆盖A股数：',year)
    # print(news_data_tmp.groupby('dt')['new_tags'].apply(lambda x : len(set(x))).mean())
    # print('A股新闻数：',year)
    # print(news_data_tmp.groupby('dt')['id'].apply(lambda x : len(set(x))).mean())