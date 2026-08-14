# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
# import IO
import networkx as nx
import itertools
import pickle
from joblib import Parallel, delayed
from itertools import product

# 读取数据样例
path = '/data/user/015585/01-因子挖掘/20240906-数库产业链/sample/'
df_product = pd.read_csv(path + 'dict_product_rs-产品字典表-全量.csv',encoding="gbk")
df_chain = pd.read_csv(path + 'supply_chain_relation-产业链关系表-全量.csv',encoding="gbk")
df_stock_product = pd.read_csv(path + 'fin_secu_sam_product-公司原始产品分项表（A股全量）_2020-2023.csv',encoding="gbk")
stock_sample = pd.read_excel(path + '典型的上下游样例.xlsx')
# 预处理
## 产品中英文对应
dic_product = df_product[['CODE','NAME']].set_index('CODE')['NAME'].to_dict()
## 产品等级和剔除
df_product['ANCESTORS'] = df_product['ANCESTORS'].apply(lambda x : x.replace(' ','').replace('，',',').split(',') if type(x)==str else [])
df_product['level'] = df_product['ANCESTORS'].apply(len) # 第N级产品
df_product = df_product[~df_product['CODE'].isin(['0x2x','0x0x'])]
## 股票产品表格式处理
df_stock_product['REPORT_DATE'] = df_stock_product['REPORT_DATE'].apply(lambda x : pd.Timestamp(x))
df_stock_product = df_stock_product[df_stock_product['SECU'].apply(lambda x : x.split('_')).apply(lambda x : x[1] in ['SH','SZ'])]
df_stock_product['SECU'] = df_stock_product['SECU'].apply(lambda x : x.split('_')[0] + '.' + x.split('_')[1])
df_stock_product = df_stock_product[~df_stock_product['PRODUCT_CODE'].isin(['0x0x','0x2x'])]
## 修正产业链importance
df_chain['product_pair'] = df_chain.apply(lambda x : (x['PRIMARY_CODE'],x['RELATED_CODE']),axis=1)
df_chain['product_pair_anti'] = df_chain.apply(lambda x : (x['RELATED_CODE'],x['PRIMARY_CODE']),axis=1)
df_chain_anti = df_chain[['product_pair_anti','IMPORTANCE']].rename(columns={'IMPORTANCE':'IMPORTANCE_ANTI','product_pair_anti':'product_pair'})
df_chain = pd.merge(df_chain,df_chain_anti, left_on='product_pair', right_on='product_pair',how = 'left')
df_chain['IMPORTANCE_UPDATE'] = 0.5*(df_chain['IMPORTANCE_ANTI'] + df_chain['IMPORTANCE'])
# 输入到图中
# graph = nx.Graph()
# ## 输入产品和子产品关系，距离为1/级别
# def get_weight_from_level(level):
#     if level >= 5:
#         return 0
#     elif level == 4:
#         return 1
#     elif level == 3:
#         return 2
#     elif level == 2:
#         return 3
#     elif level == 1:
#         return 4
#     else:
#         return np.nan
# df_product['weight'] = df_product['level'].apply(lambda x : get_weight_from_level(x))
# graph.add_edges_from(list(df_product[df_product['level'] >= 1].apply(lambda x : (x['CODE'],x['PARENT'],{'weight':x['weight']}),axis=1)))
# ## 输入产业链关系
# graph.add_edges_from(list(df_chain[df_chain['IMPORTANCE_UPDATE'] >= 3].apply(lambda x : (x['PRIMARY_CODE'],x['RELATED_CODE'],{'weight':2.5}),axis=1)))

## 最短路径查找
'''
1、得到股票A和股票B各自的产品，形成产品对
2、分别计算产品间的最短距离
3、输出最短距离
'''
df_stock_product = df_stock_product[df_stock_product['REPORT_DATE'] == pd.Timestamp('20231231')]
def get_stock_pair_path(Ticker1,Ticker2,graph,little_ratio = 0.05,little_punish = 4):
    df_stock_product1 = df_stock_product[df_stock_product['SECU'] == Ticker1].copy()
    df_stock_product1['product_ratio'] = df_stock_product1['PRODUCT_INCOME_ORGIN'] / df_stock_product1['PRODUCT_INCOME_ORGIN'].sum()
    list_product1 = list(set(df_stock_product1['PRODUCT_CODE']))
    list_product1_little = list(set(df_stock_product1[df_stock_product1['product_ratio'] <= little_ratio]['PRODUCT_CODE']))
    #
    df_stock_product2 = df_stock_product[df_stock_product['SECU'] == Ticker2].copy()
    df_stock_product2['product_ratio'] = df_stock_product2['PRODUCT_INCOME_ORGIN'] / df_stock_product2[
        'PRODUCT_INCOME_ORGIN'].sum()
    list_product2 = list(set(df_stock_product2['PRODUCT_CODE']))
    list_product2_little = list(set(df_stock_product2[df_stock_product2['product_ratio'] <= little_ratio]['PRODUCT_CODE']))
    #
    distance_res = pd.DataFrame(columns = ['distance','path_code','path_chinese'])
    for product_pair in list(itertools.product(list_product1, list_product2)):
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
            pass
    return distance_res
def get_distance_matrix_from_stocklist(stock_list1,stock_list2,graph,little_punish=4):
    '''
    :param stock_list:
    :return:stock_list中两两间的最短距离构成的矩阵
    '''
    stock_list1 = list(set(stock_list1))
    stock_list1.sort()
    stock_list2 = list(set(stock_list2))
    stock_list2.sort()
    distance_matrix = pd.DataFrame(index = stock_list1, columns = stock_list2)
    for i in stock_list1:
        for j in stock_list2:
            # print(i,j)
            distance_matrix.loc[i,j] = get_stock_pair_path(i,j,graph,little_punish=little_punish)['distance'].min()
    return distance_matrix
def estimate_parameter(parameter_name,stock_sample):
    parameter = dic_parameter[parameter_name]
    litle_punish = parameter['little_punish']
    def get_weight_from_level_parameter(x,parameter):
        res = np.nan
        for i in parameter:
            if x == i:
                res = parameter[i]
        return res
    graph = nx.Graph()
    df_product['weight'] = df_product['level'].apply(lambda x: get_weight_from_level_parameter(x,parameter))
    graph.add_edges_from(list(df_product[df_product['level'] >= 1].apply(lambda x: (x['CODE'], x['PARENT'], {'weight': x['weight']}),
                         axis=1)))
    graph.add_edges_from(list(df_chain[df_chain['IMPORTANCE_UPDATE'] >= 3].apply(
        lambda x: (x['PRIMARY_CODE'], x['RELATED_CODE'], {'weight': parameter['chain']}), axis=1)))
    industry_list = list(set(stock_sample['行业']))
    industry_list.sort()
    def parallel_get_distance_matrix_from_industry(industry1,industry2):
        if industry2 >= industry1:
            print(industry1,industry2)
            stock_list1 = stock_sample[stock_sample['行业'] == industry1]['S_INFO_WINDCODE']
            stock_list1 = [x for x in stock_list1 if type(x) == str]
            stock_list2 = stock_sample[stock_sample['行业'] == industry2]['S_INFO_WINDCODE']
            stock_list2 = [x for x in stock_list2 if type(x) == str]
            return [industry1 + '_' + industry2,get_distance_matrix_from_stocklist(stock_list1,stock_list2,graph,little_punish=litle_punish)]
        else:
            return [industry2 + '_' + industry1,pd.DataFrame()]
    res = Parallel(n_jobs=8)(delayed(parallel_get_distance_matrix_from_industry)(industry1,industry2) for industry1,industry2 in product(industry_list,industry_list))
    save_pickle(res, '/data/user/015585/01-因子挖掘/20240906-数库产业链/sample/get_best_parameter/{}.pkl'.format(parameter_name))
    return
def save_pickle(result_dic, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(result_dic, input, protocol=pickle.HIGHEST_PROTOCOL)
#
# res = {}
# industry_list = list(set(stock_sample['行业']))
# industry_list.sort()
# for industry1 in industry_list:
#     for industry2 in industry_list:
#         if industry2 >= industry1:
#             print(industry1,industry2)
#             stock_list1 = stock_sample[stock_sample['行业'] == industry1]['S_INFO_WINDCODE']
#             stock_list1 = [x for x in stock_list1 if type(x) == str]
#             stock_list2 = stock_sample[stock_sample['行业'] == industry2]['S_INFO_WINDCODE']
#             stock_list2 = [x for x in stock_list2 if type(x) == str]
#             res[industry1 + '_' + industry2] = get_distance_matrix_from_stocklist(stock_list1,stock_list2,graph)
# save_pickle(res, '/data/user/015585/01-因子挖掘/20240906-数库产业链/sample/res.pkl')
'''
para1:基准
*para2:减小边缘业务距离
para3:4级产品距离也为0，原先为1
*para4:增加产业链距离
'''
dic_parameter = {
    'para1':{
        8:0,
        7:0,
        6:0,
        5:0,
        4:1,
        3:2,
        2:3,
        1:4,
        'chain':2.5,
        'little_punish':4
    },
    'para2':{
        8:0,
        7:0,
        6:0,
        5:0,
        4:1,
        3:2,
        2:3,
        1:4,
        'chain':2.5,
        'little_punish':3
    },
    'para3': {
        8: 0,
        7: 0,
        6: 0,
        5: 0,
        4: 0,
        3: 1,
        2: 2,
        1: 3,
        'chain': 1.5,
        'little_punish': 3
    },
    'para4': {
        8: 0,
        7: 0,
        6: 0,
        5: 0,
        4: 1,
        3: 2,
        2: 3,
        1: 4,
        'chain': 6,
        'little_punish': 4
    },
}

from xquant.factordata import FactorData
s = FactorData()
map_df=s.get_factor_value('WIND_AShareDescription')[['S_INFO_NAME','S_INFO_WINDCODE']]
stock_sample = pd.merge(stock_sample,map_df,left_on='公司名称',right_on='S_INFO_NAME',how='left')[['行业','子行业','S_INFO_WINDCODE','公司名称']]

for parameter_name in dic_parameter:
    estimate_parameter(parameter_name,stock_sample)
for parameter_name in dic_parameter:
    res_df = pd.read_pickle('/data/user/015585/01-因子挖掘/20240906-数库产业链/sample/get_best_parameter/{}.pkl'.format(parameter_name))
    res = []
    res.append(parameter_name)
    res_same = []
    res_notsame = []
    for i in res_df:
        if not np.isnan(i[1].mean().mean()):
            if i[0].split('_')[0] == i[0].split('_')[1]:
                res_same.append(i[1].median().median())
            else:
                res_notsame.append(i[1].median().median())
    res.append(np.mean(res_same))
    res.append(np.mean(res_notsame))
    print(res,res[2]/res[1])

