import datetime
import pandas as pd
import os
import numpy as np
import IO
# europa basic file
news_data = pd.read_hdf('/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/通联-新闻数据/统计结果.h5')
news_data = news_data.reset_index()
news_data['dt'] = news_data['dt'].apply(lambda x : pd.Timestamp(x))
news_data['year'] = news_data['dt'].apply(lambda x : x.year)
res_dic = {}
for year in ['2016','2017','2018','2019','2020']:
# for year in ['2024']:
    # print('prepare europa basic file')
    def cal_ul_price(pre_close_dataframe, ratio = 0.1):
        pre_close_dataframe = pre_close_dataframe.reset_index()
        after_824 = pre_close_dataframe['dt']>=pd.Timestamp('20200824')
        cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='30')
        kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2]=='68')
        pre_close_dataframe['ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+ratio) + 0.5) / 100
        pre_close_dataframe.loc[(after_824 & cyb)| kcb, 'ul_price'] = np.floor(pre_close_dataframe['pre_close'] * 100 * (1+2*ratio) + 0.5) / 100
        return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']
    md_data = IO.read_data([int(str(year + '0101')), int(str(year + '1231'))], columns=['amt', 'high','open','close','pre_close','vwap','adjfactor'],
                            alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['ul_price'] = cal_ul_price(md_data)
    md_data['trigger_price'] = md_data['ul_price'] - 0.01
    md_data['is_zt'] = (md_data['high'] >= md_data['ul_price']).apply(int)
    md_data['last_is_zt'] = md_data['is_zt'].unstack().shift(1).stack()
    # md_data = md_data.query('high >= trigger_price and open < ul_price and last_is_zt == 0')[['amt']].reset_index()
    md_data = md_data.query('close >= ul_price')[['amt']].reset_index()
    md_data = md_data[~md_data['Ticker'].str.contains('BJ')]
    #
    res = pd.merge(md_data, news_data, left_on='Ticker', right_on='Ticker', how='left')
    res['is_value2'] = (res['dt_y'] == res['dt_x'])
    res['effective_count'] = res['newsID']
    res.loc[res['is_value2'] == False, 'effective_count'] = 0
    # res = res[res['is_value']==True]
    print('T日：', year)
    print(res.groupby(['dt_x', 'Ticker'])['effective_count'].sum().quantile([0.5]))
    num_zt = res.groupby(['dt_x', 'Ticker'])['effective_count'].sum().groupby('dt_x').count().mean()
    print('涨停股日均数量 from stat：', num_zt)
    print('涨停股日均数量 from md_data：', md_data.groupby('dt').count()['amt'].mean())
    num_hasnews = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['effective_count'].sum()).query('effective_count >= 1').groupby(
        'dt_x').count().mean()['effective_count']
    print('T日涨停股T日有新闻覆盖的日均数量:', num_hasnews, num_hasnews / num_zt)
    df_IT_num = pd.read_pickle('/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/file/res_AINEWS_T_{}.pkl'.format(year))
    df_IT_num.columns = ['IT_news']
    df_tl_num = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['effective_count'].sum()).query('effective_count >= 1')
    df_tl_num = pd.merge(df_tl_num, df_IT_num, left_index=True, right_index=True, how='left')
    print('T日日均增量覆盖股票数：', len(df_tl_num[df_tl_num['IT_news'].isna()]) / len(set(md_data['dt'])))
    for days in [5,10,20]:
        md_data['dt_start'] = md_data['dt'].apply(lambda x : x - datetime.timedelta(days = days))
        res = pd.merge(md_data[['dt','Ticker','dt_start']],news_data,left_on = 'Ticker',right_on = 'Ticker',how = 'left')
        res['is_value'] = (res['dt_y'] < res['dt_x']) & (res['dt_y'] >= res['dt_start'])
        res['effective_count'] = res['newsID']
        res.loc[res['is_value']==False,'effective_count'] = 0
        # res = res[res['is_value']==True]
        res_dic[(year,days)] = res.groupby(['dt_x','Ticker'])['is_value'].sum().quantile([0.5])
        print(year,days,)
        print(res.groupby(['dt_x','Ticker'])['effective_count'].sum().quantile([0.5]))
        num_hasnews_n = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['effective_count'].sum()).query('effective_count >= 1').groupby(
            'dt_x').count().mean()['effective_count']
        print('T日涨停股T-{}日有新闻覆盖的日均数量:'.format(days), num_zt, num_hasnews_n, num_hasnews_n / num_zt)
        df_IT_num = pd.read_pickle(
            '/data/user/015585/01-因子挖掘/20240603-新闻数据测试与落地/file/res_AINEWS_T_{}_{}.pkl'.format(days, year))
        df_IT_num.columns = ['IT_news']
        df_tl_num = pd.DataFrame(res.groupby(['dt_x', 'Ticker'])['effective_count'].sum()).query('effective_count >= 1')
        df_tl_num = pd.merge(df_tl_num, df_IT_num, left_index=True, right_index=True, how='left')
        print('T日日均增量覆盖股票数：', len(df_tl_num[df_tl_num['IT_news'].isna()]) / len(set(md_data['dt'])))
        # print(year,days,len(md_data))