import pandas as pd
import IO
import numpy as np
import os
from xquant.factordata import FactorData
import datetime as dt
from sklearn.cluster import KMeans
'''
对同花顺、同花顺数据在europa样本上聚类，观察当日事后聚类的效果
'''
# 同花顺
ths_correlation = pd.read_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/res_theme_stock_xquant.pkl')
'''
# ths_heat = pd.read_pickle('/dfs/user/015585/20240318-同花顺概念热度/file_res/res_theme_heat.pkl')
# ths_correlation = pd.merge(ths_correlation.reset_index(),ths_heat[['dt','themeID','heat']],left_on=['dt','themeID'],right_on=['dt','themeID'],how = 'left').set_index(['dt','Ticker'])
# ths_correlation.to_pickle('/dfs/user/015585/20240318-同花顺概念热度/file_res/correlation_heat_all.pkl')
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
date = '20231020'
ths_basicinfo = pd.read_pickle('/dfs/user/015585/20240327-同花顺概念热度/file/ths_theme_basicinfo_xquant.pkl')
ths_basicinfo = ths_basicinfo[['themeID','themeName']].drop_duplicates()

basic_file_europa = pd.read_pickle('/data/group/800463/data/project1_prod/tick_europa/' + date + '.pkl')
# basic_file_saturn = pd.read_pickle('/data/group/800463/data/project2_prod/everyday_Data/tick/' + date + '.pkl')
basic_file_saturn = pd.DataFrame()
basic_file = basic_file_europa.append(basic_file_saturn)
basic_file = basic_file[~basic_file.index.duplicated()]
ths_correlation_date = ths_correlation.loc[pd.Timestamp(date)].reset_index()
ths_correlation_date['is_member'] = 1
ths_correlation_date = ths_correlation_date.drop_duplicates()
ths_correlation_filter = ths_correlation_date[ths_correlation_date['Ticker'].isin(basic_file.index.get_level_values(1))]
## 聚类
'''
统计高频概念，对概念的频率从高到低，定义概念间的距离为全市场共同股票数占比，如果概念和入池概念距离较近，归为同一概念，不纳入概念池。
最终概念池与对应的高频概念作为初始点，概念池大小作为聚类个数，距离初始点很远的样本剔除（作为“其他”）
'''
def func_distance(id1,id2,distance_themeID):# 主题间的距离：拥有的个股重合度; 注意不能填充0，必须是nan
    num_common_stock = (distance_themeID[id1] + distance_themeID[id2]).sum() / 2
    num_all_stock = distance_themeID[id1].sum() + distance_themeID[id2].sum() - num_common_stock
    distance = num_common_stock / num_all_stock  # distance越大，靠的越近
    return distance
def get_high_num_themeID(ths_correlation_filter, n=4):# 返回当日>=n的概念series与对应股票数
    num_themeID = ths_correlation_filter.groupby('themeID')['is_member'].count()
    num_themeID = num_themeID.sort_values(ascending = False)
    num_themeID = num_themeID[num_themeID >= n] # 删去特别小的概念,x为规模效应的底线
    num_themeID = num_themeID[~num_themeID.index.isin(list_del)] # 候选的高频概念池
    return num_themeID
num_themeID = get_high_num_themeID(ths_correlation_filter, 4)
print('当日高频概念一览：',pd.merge(num_themeID,ths_basicinfo[['themeID','themeName']],left_index = True,right_on = 'themeID',how ='left'))
## 生成核心概念
## 新增初始质心隔离列表：列表中的概念排不到前5名则不纳入池中

def get_themeID_pool(distance_themeID, distance_themeID2,
                     ratio1=0.06,ratio2=0.15,
                     ratio3=0.1,ratio4=0.2,
                     list_del_init_centroid = [], ratio5 = 5
                     ):# 返回最终入选的高频概念（概念池）
    '''
    :param distance_themeID: 全市场当日的股票-主题对应关系
    :param distance_themeID2:basic文件过滤后当日的股票-主题对应关系
    :param ratio1:全市场概念重合度阈值，小于该阈值则认为非同类概念
    :param ratio2:样本集概念重合度阈值，小于该阈值则认为非同类概念
    :param ratio3:共同归为质心的全市场概念重合度阈值，大于该阈值则认为同类概念
    :param ratio4:共同归为质心的样本集概念重合度阈值，大于该阈值则认为同类概念
    :return:概念池
    '''
    themeID_pool = []
    for themeID in num_themeID.index:
        distance_max = 0 # 全市场的概念间重合度
        distance_max2 = 0 # 当日样本上的重合度
        for themeID_in in themeID_pool:
            distance = func_distance(themeID,themeID_in,distance_themeID)
            distance2 = func_distance(themeID,themeID_in,distance_themeID2)
            if distance > distance_max:
                distance_max = distance
            if distance2 > distance_max2:
                distance_max2 = distance2
        if (distance_max < ratio1) & (distance_max2 < ratio2):
            if (themeID in list_del_init_centroid) & (len(themeID_pool) < ratio5):
                themeID_pool.append(themeID)
            elif not themeID in list_del_init_centroid:
                themeID_pool.append(themeID)
    themeID_neartheme = {} # 高频概念和重合度较高的其他高频概念
    for themeID_in in themeID_pool:
        neartheme_list = []
        for themeID in num_themeID.index:
            distance = func_distance(themeID,themeID_in,distance_themeID)
            distance2 = func_distance(themeID,themeID_in,distance_themeID2)
            if (distance > ratio3) | (distance2 > ratio4):
                neartheme_list.append(themeID)
        themeID_neartheme[themeID_in] = neartheme_list
    return themeID_pool,themeID_neartheme
list_del_init_centroid = []
themeID_pool,themeID_neartheme = get_themeID_pool(ths_correlation_date.set_index(['Ticker','themeID'])['is_member'].unstack(),
                                                  ths_correlation_filter.set_index(['Ticker','themeID'])['is_member'].unstack(),
                                                  0.06,0.15,
                                                  0.1,0.2,
                                                  list_del_init_centroid,3)
## 初始质心 = 核心概念 + 附属高频概念
ths_correlation_clean = ths_correlation_filter.set_index(['Ticker', 'themeID'])['is_member'].unstack().fillna(0)
def get_init_centroid(themeID_neartheme,ths_correlation_clean): # 初始质心
    for i in themeID_neartheme:
        for j in themeID_neartheme[i]:
            if j == i:
                ths_correlation_clean.loc[i, j] = 1
            else:
                if not j in list_del_init_centroid:
                    ths_correlation_clean.loc[i, j] = 0.75
    init_centroid = ths_correlation_clean.loc[list(themeID_neartheme.keys())].fillna(0)
    return init_centroid
init_centroid = get_init_centroid(themeID_neartheme,ths_correlation_clean.copy())

def get_stock_others(list_stock,ths_correlation_clean,init_centroid,
                     ratio = 0.1):# 对list_stock中股票，通过ths_correlation_clean得到坐标，计算和init_centroid距离（对于这个质心，股票有几个质心涉及的概念的占比值），低的作为“其他”返回
    stock_others = []
    for i in list_stock:
        distance_max = 0 # 到初始质心相关概念的占比的最大值
        l1 = list(ths_correlation_clean.loc[i])
        l1 = [np.nan if kk == 0 else kk for kk in l1]
        for j in init_centroid.index:
            l2 = list(init_centroid.loc[j])
            l2 = [np.nan if kk == 0 else kk for kk in l2]
            common = (np.array(l1) + np.array(l2))
            common = common[common>0].sum()/2
            common = 0 if not common < 1e8 else common
            distance = common / (np.array(l1)[np.array(l1)>0].sum() + np.array(l2)[np.array(l2)>0].sum() - common)
            if distance > distance_max:
                distance_max = distance
        if distance_max < ratio:
            stock_others.append(i)
    return stock_others
stock_others = get_stock_others(ths_correlation_clean.index,ths_correlation_clean.copy(),init_centroid,0.1)
def func_Kmeans(ths_correlation_clean,
                    stock_others,
                    init_centroid):
    ths_correlation_clean_res = ths_correlation_clean[~ths_correlation_clean.index.isin(stock_others)]
    X = np.array(ths_correlation_clean_res)
    Kmeans = KMeans(n_clusters=len(init_centroid),init=np.array(init_centroid))
    Kmeans.fit(X)
    final_centroid = pd.DataFrame(index = ths_correlation_clean_res.columns)    # 最终质心坐标
    ths_correlation_clean_res['label'] = Kmeans.labels_
    ths_correlation_clean_res['distance_to_cluster'] = np.nan
    for i in range(len(init_centroid)):
        final_centroid['center_' + str(i)] = Kmeans.cluster_centers_[i]
    return Kmeans,ths_correlation_clean_res,final_centroid
init_centroid_tmp = init_centroid.copy()
# init_centroid_tmp.iloc[7] = (init_centroid_tmp.iloc[7] + init_centroid_tmp.iloc[4])/2
# init_centroid_tmp.iloc[2] = (init_centroid_tmp.iloc[2] + init_centroid_tmp.iloc[6])/2
# Kmeans,ths_correlation_clean_res,final_centroid = func_Kmeans(ths_correlation_clean,stock_others,init_centroid_tmp[~init_centroid_tmp.index.isin([8490298])])
Kmeans,ths_correlation_clean_res,final_centroid = func_Kmeans(ths_correlation_clean,stock_others,init_centroid)
#------------------------------------------------------------------------------------------------------------
def minkov_distance(l1,l2):
    return ((l1-l2)**2).sum()**0.5
ths_correlation_date_clean = ths_correlation_date.set_index(['Ticker', 'themeID'])['is_member'].unstack().fillna(0)
final_centroid_stock = {}
res = pd.DataFrame()
for i in final_centroid.columns:
    final_centroid_stock_i = (np.mat(np.array(ths_correlation_date_clean[final_centroid.index])) * np.mat(np.array(final_centroid[i])).T).T
    final_centroid_stock[i] = final_centroid_stock_i
for i in final_centroid.columns:
    for j in final_centroid.columns:
        l1 = np.array(final_centroid_stock[i])[0]
        l1 = np.array([x if x > 0.1 else 0 for x in l1 ])
        l2 = np.array(final_centroid_stock[j])[0]
        l2 = np.array([x if x > 0.1 else 0 for x in l2 ])
        res.loc[i,j] = minkov_distance(np.array(final_centroid_stock[i])[0],np.array(final_centroid_stock[j])[0])
#------------------------------------------------------------------------------------------------------------

# 该样本最终到质心的距离
print('最终质心：')
for i in final_centroid.columns:
    final_centroid_i = final_centroid[i]
    result_i = []
    for j in final_centroid_i[final_centroid_i>0.5].sort_values(ascending = False).index:
        result_i.append(ths_basicinfo[ths_basicinfo['themeID']==j]['themeName'].values[0])
    print(i,result_i)
print('初始质心：')
count = 0
for i in themeID_pool:
    print(count, ths_basicinfo[ths_basicinfo['themeID']==i]['themeName'].values[0])
    count += 1
print('个股归属：')
for i in range(len(themeID_neartheme)):
    l2 = Kmeans.cluster_centers_[i] # 质心坐标
    for j in ths_correlation_clean_res[ths_correlation_clean_res['label'] == i].index:
        l1 = np.array(ths_correlation_clean_res.loc[j])[:-2]
        ths_correlation_clean_res.loc[j,'distance_to_cluster'] = ((l1-l2)**2).sum()
        # print(j,i,ths_correlation_clean_res.loc[j,'distance_to_cluster'])
print('others:',stock_others)