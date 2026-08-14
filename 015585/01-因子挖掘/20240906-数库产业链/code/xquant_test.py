import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from xquant.thirdpartydata.factordata import FactorData
import pandas as pd
import numpy as np
import os
import IO
import networkx as nx
import itertools
import pickle
from multiprocessing import Pool
from itertools import product
from joblib import Parallel, delayed
from xquant.factordata import FactorData as FactorData2
s = FactorData()
# 输入到图中
def get_graph(tradingday, df_product_ori, df_chain_ori):
    graph = nx.Graph()
    # 根据日期筛选没有未来信息的基础数据
    df_product = df_product_ori[df_product_ori['create_time'] < pd.Timestamp(tradingday)]
    # df_product = df_product_ori.copy() # 有产品在公司-产品表中先出现，所以df_product输入全量
    if tradingday <= '20181231':
        df_chain = df_chain_ori[df_chain_ori['create_time'] <= pd.Timestamp('20181231')]
    else:
        df_chain = df_chain_ori[df_chain_ori['create_time'] < pd.Timestamp(tradingday)]

    ## 输入产品和子产品关系，距离为1/级别
    def get_weight_from_level(level):
        if level >= 5:
            return 0
        elif level == 4:
            return 1
        elif level == 3:
            return 2
        elif level == 2:
            return 3
        elif level == 1:
            return 4
        else:
            return np.nan
    df_product['weight'] = df_product['level'].apply(lambda x : get_weight_from_level(x))
    graph.add_edges_from(list(df_product[df_product['level'] >= 1].apply(lambda x : (x['code'],x['parent'],{'weight':x['weight']}),axis=1)))
    ## 输入产业链关系
    graph.add_edges_from(list(df_chain[df_chain['importance_update'] >= 3].apply(lambda x : (x['primary_code'],x['related_code'],{'weight':2.5}),axis=1)))
    return graph
## 最短路径查找
def get_stock_pair_path(Ticker1,Ticker2,graph,df_stock_product,little_ratio = 0.05,little_punish = 3):
    print(Ticker1, Ticker2)
    df_stock_product1 = df_stock_product[df_stock_product['secu'] == Ticker1].copy()
    df_stock_product1['product_ratio'] = df_stock_product1['product_income_orgin'] / df_stock_product1['product_income_orgin'].sum()
    list_product1 = list(set(df_stock_product1['product_code']))
    list_product1_little = list(set(df_stock_product1[df_stock_product1['product_ratio'] <= little_ratio]['product_code']))
    #
    df_stock_product2 = df_stock_product[df_stock_product['secu'] == Ticker2].copy()
    df_stock_product2['product_ratio'] = df_stock_product2['product_income_orgin'] / df_stock_product2[
        'product_income_orgin'].sum()
    list_product2 = list(set(df_stock_product2['product_code']))
    list_product2_little = list(set(df_stock_product2[df_stock_product2['product_ratio'] <= little_ratio]['product_code']))
    #
    distance_res = pd.DataFrame(columns = ['distance','path_code','path_chinese'])
    for product_pair in list(itertools.product(list_product1, list_product2)):
        if product_pair[0] in graph.node and product_pair[1] in graph.node:
            try:
                path = nx.shortest_path(graph, product_pair[0], product_pair[1],weight = 'weight')
                length = sum(graph[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
                if product_pair[0] in list_product1_little:
                    length = length + little_punish
                if product_pair[1] in list_product2_little:
                    length = length + little_punish
                distance_res_path = {'distance':length,
                                     'path_code':path,
                                     'path_chinese':[dic_product[x] for x in path]}
                distance_res = distance_res.append(distance_res_path, ignore_index = True)
            except nx.NetworkXNoPath:
                distance_res_path = {'distance':200,
                                     'path_code':[''],
                                     'path_chinese':['']}
                distance_res = distance_res.append(distance_res_path, ignore_index = True)
        else:
            distance_res_path = {'distance': 200,
                                 'path_code': [''],
                                 'path_chinese': ['']}
            distance_res = distance_res.append(distance_res_path, ignore_index=True)
    return distance_res
def parallel_get_stock_pair_path(Ticker1,Ticker2,graph,df_stock_product_code_list,little_ratio = 0.05,little_punish = 3):
    print(Ticker1, Ticker2)
    #
    list_product1 = df_stock_product_code_list[Ticker1][0]
    list_product1_little = df_stock_product_code_list[Ticker1][1]
    list_product2 = df_stock_product_code_list[Ticker2][0]
    list_product2_little = df_stock_product_code_list[Ticker2][1]
    distance_res = pd.DataFrame(columns = ['distance','path_code','path_chinese'])
    for product_pair in list(itertools.product(list_product1, list_product2)):
        if product_pair[0] in graph.node and product_pair[1] in graph.node:
            try:
                path = nx.shortest_path(graph, product_pair[0], product_pair[1],weight = 'weight')
                length = sum(graph[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
                if product_pair[0] in list_product1_little:
                    length = length + little_punish
                if product_pair[1] in list_product2_little:
                    length = length + little_punish
                distance_res_path = {'distance':length,
                                     'path_code':path,
                                     'path_chinese':[dic_product[x] for x in path]}
                distance_res = distance_res.append(distance_res_path, ignore_index = True)
            except nx.NetworkXNoPath:
                distance_res_path = {'distance':200,
                                     'path_code':[''],
                                     'path_chinese':['']}
                distance_res = distance_res.append(distance_res_path, ignore_index = True)
        else:
            distance_res_path = {'distance': 200,
                                 'path_code': [''],
                                 'path_chinese': ['']}
            distance_res = distance_res.append(distance_res_path, ignore_index=True)
    res = {(Ticker1,Ticker2):distance_res['distance'].min()}
    return pd.Series(res)
def save_pickle(result_dic, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(result_dic, input, protocol=pickle.HIGHEST_PROTOCOL)
def get_distance_matrix_from_stocklist(stock_list1,stock_list2,graph,df_stock_product,little_punish=4):
    '''
    :param stock_list:
    :return:stock_list中两两间的最短距离构成的矩阵
    '''
    stock_list1 = list(set(stock_list1))
    stock_list1.sort()
    stock_list2 = list(set(stock_list2))
    stock_list2.sort()
    stock_pair_list = itertools.product(stock_list1,stock_list2)
    stock_pair_list = [i for i in stock_pair_list if i[0]>=i[1]]

    pool_num = 30
    pool_num=min(pool_num,len(stock_pair_list))

    pool = Pool(pool_num)
    task_list = []
    for stock_pair in stock_pair_list:
        task_list.append(pool.apply_async(parallel_get_stock_pair_path,args=(stock_pair[0],stock_pair[1],
                                                                               graph.copy(),df_stock_product.copy(),little_punish)))
    pool.close()
    pool.join()
    return [i.get() for i in task_list]
def parallel_date_matrix(tradingday, md_data, df_product_ori, df_chain_ori, df_stock_product_ori, save_path):
        graph = get_graph(tradingday, df_product_ori, df_chain_ori)
        if tradingday <= '20171231':
            report_judge_date = '20171231'
        else:
            report_judge_date = (pd.Timestamp(tradingday) - pd.Timedelta(days=120)).strftime('%Y%m%d')
        df_stock_product = df_stock_product_ori[df_stock_product_ori['report_date'] <= pd.Timestamp(report_judge_date)]
        df_stock_product = df_stock_product.sort_values('report_date', ascending=False)
        df_stock_product = df_stock_product.drop_duplicates(subset=['secu', 'product_code'], keep='first')
        #
        stock_list1 = list(md_data.loc[pd.Timestamp(str(tradingday))].reset_index()['Ticker'])
        stock_list2 = stock_list1
        matrix_distance = pd.concat(get_distance_matrix_from_stocklist(stock_list1,stock_list2,graph,df_stock_product,little_punish=4))
        matrix_distance = matrix_distance.unstack()
        matrix_distance.to_pickle(f'{save_path}{tradingday}.pkl')
        return
#
if __name__ == '__main__':
    # 获取xquant源的产业链基础数据
    df_product = s.get_factor_value('STK_sktech_dict_product_rs')  # 产品字典表
    df_chain = s.get_factor_value('STK_sktech_supply_chain_relation')  # 产业链关系表
    df_stock_product = s.get_factor_value('STK_sktech_fin_secu_sam_product')  # 公司原始产品分项表
    df_stock_product = df_stock_product[df_stock_product['report_date'] >= pd.Timestamp('20160101')]
    dic_product = df_product[['code', 'name']].set_index('code')['name'].to_dict()    ## 产品中英文对应
    df_product['ancestors'] = df_product['ancestors'].apply(
        lambda x: x.replace(' ', '').replace('，', ',').split(',') if type(x) == str else [])
    df_product['level'] = df_product['ancestors'].apply(len)  # 第N级产品
    df_product_ori = df_product[~df_product['code'].isin(['0x2x', '0x0x'])]    ## 产品等级和剔除
    df_stock_product['report_date'] = df_stock_product['report_date'].apply(lambda x: pd.Timestamp(x))
    df_stock_product = df_stock_product[
        df_stock_product['secu'].apply(lambda x: x[-3:] in ['.SZ', '.SH'] if type(x) == str else False)]
    df_stock_product_ori = df_stock_product[~df_stock_product['product_code'].isin(['0x0x', '0x2x'])]    ## 股票产品表格式处理
    df_chain['product_pair'] = df_chain.apply(lambda x: (x['primary_code'], x['related_code']), axis=1)
    df_chain['product_pair_anti'] = df_chain.apply(lambda x: (x['related_code'], x['primary_code']), axis=1)
    df_chain_anti = df_chain[['product_pair_anti', 'importance']].rename(
        columns={'importance': 'importance_anti', 'product_pair_anti': 'product_pair'})
    df_chain = pd.merge(df_chain, df_chain_anti, left_on='product_pair', right_on='product_pair', how='left')
    df_chain['importance_update'] = 0.5 * (df_chain['importance_anti'] + df_chain['importance'])
    df_chain_ori = df_chain.copy()## 修正产业链importance
    # 获取运行时间
    year_list = [i for i in range(2016,2024+1)]
    end_dates = []
    for year in year_list:
        for month in range(1, 13):
            start_date = datetime(year, month, 1)
            end_date = start_date + relativedelta(months = 1, days=-1)
            end_dates.append(end_date.strftime('%Y%m%d'))
    s2 = FactorData2()
    end_dates = [str(s2.tradingday(i,-1)[0]) for i in end_dates]
    print(end_dates)

    start_date = 20160101  # 北交所上市交易时间21-11-15，但显示的最早日期2020-07-27
    end_date = 20241030
    little_punish = 4
    # 获取md
    md_data_ori = IO.read_data([start_date, end_date],
                      columns=['amt'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    save_path = '/dfs/user/015585/20241107-数库产业链/20241107_月末样本距离_2016_2024/'

    tradingday = '20241030'
    little_ratio = 0.05
    md_data = md_data_ori.loc[pd.Timestamp(tradingday):pd.Timestamp(tradingday)].head(100) # test
    time1 = time.localtime()
    #
    graph = get_graph(tradingday, df_product_ori, df_chain_ori)
    if tradingday <= '20171231':
        report_judge_date = '20171231'
    else:
        report_judge_date = (pd.Timestamp(tradingday) - pd.Timedelta(days=120)).strftime('%Y%m%d')
    df_stock_product = df_stock_product_ori[df_stock_product_ori['report_date'] <= pd.Timestamp(report_judge_date)]
    df_stock_product = df_stock_product.sort_values('report_date', ascending=False)
    df_stock_product = df_stock_product.drop_duplicates(subset=['secu', 'product_code'], keep='first')
    df_stock_product_code_list = df_stock_product.groupby('secu').apply(lambda x : [list(set(x['product_code'])),
                                                       list(set(x[x['product_income_orgin']/x['product_income_orgin'].sum() <= little_ratio]['product_code']))])
    #
    stock_list1 = list(md_data.loc[pd.Timestamp(str(tradingday))].reset_index()['Ticker'])
    stock_list1.sort()
    stock_list2 = stock_list1
    stock_pair_list = itertools.product(stock_list1,stock_list2)
    stock_pair_list = [i for i in stock_pair_list if i[0]>=i[1]]

    pool_num = 30
    pool_num=min(pool_num,len(stock_pair_list))
    pool = Pool(pool_num)
    task_list = []

    for stock_pair in stock_pair_list:
        task_list.append(pool.apply_async(parallel_get_stock_pair_path,args=(stock_pair[0],stock_pair[1],
                                                                               graph,df_stock_product_code_list,little_punish)))
    pool.close()
    pool.join()

    matrix_distance = pd.concat([i.get() for i in task_list])
    matrix_distance = matrix_distance.unstack()
    matrix_distance.to_pickle(f'{save_path}{tradingday}.pkl')
    print(time1)
    print(time.localtime())

