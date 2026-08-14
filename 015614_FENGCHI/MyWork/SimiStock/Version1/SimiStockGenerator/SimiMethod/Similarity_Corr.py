from SimiStock.Version1.SimiStockGenerator.util import util
from SimiStock.Version1.config.path_config import hedge_path
from SimiStock.Version1.SimiStockGenerator.SimiMethodBase.SimiMethodBase import SimiMethodBase
from SimiStock.dataApi import getData
import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist,squareform
from sklearn.cluster import KMeans,AgglomerativeClustering,Birch  # K-means，层次聚类,基于树的层次聚类
from sklearn.cluster import MeanShift,DBSCAN # 均值飘逸聚类，密度聚类，密度聚类的一种变形
from sklearn.cluster import SpectralClustering,SpectralBiclustering # 谱聚类，光谱双聚类

def get_maxdown(df):
    a = df / np.fmax.accumulate(df,axis=0)-1
    return a.expanding().min()

class SimiMethodDemo(SimiMethodBase):
    def __init__(self, start_date=20200101, end_date=20200110, concept='SW1',use_time = 242,rank=0):
        super().__init__(start_date=start_date, end_date=end_date, concept=concept)
        # TODO：此处定义其他内容
        self.use_time = use_time
        self.rank = rank
        # 个股日频数据
        # open_badj,close_badj,high_badj,low_badj = getData.get_daily_1factor('open_badj'),getData.get_daily_1factor('close_badj'),\
        #                                           getData.get_daily_1factor('high_badj'),getData.get_daily_1factor('low_badj')
        # self.open_badj,self.close_badj,self.high_badj,self.low_badj = open_badj,close_badj,high_badj,low_badj
        #
        # open,close,high,low = getData.get_daily_1factor('open'),getData.get_daily_1factor('close'),\
        #                       getData.get_daily_1factor('high'),getData.get_daily_1factor('low')
        # pre_close = getData.get_daily_1factor('pre_close')
        pct_chg = getData.get_daily_1factor('pct_chg',date_list=self.shift_date_list)

        # self.open, self.close, self.high, self.low = open, close, high, low
        # self.pre_close= pre_close
        self.pct_chg = pct_chg
    # 1、计算简单的相关性
    def cal_corr(self,df,stk_id, trade_date, concept_list,use_time = 242):
        # 1、收益率相关性
        close = df.loc[:trade_date].iloc[-use_time:].fillna(method='ffill').fillna(0)
        corr_result = close[concept_list].corrwith(close[stk_id])
        corr_result = corr_result.sort_values(ascending=False).dropna()

        return corr_result
    # 2、单期相关性：这个东西他评估的是方向，而非
    def period_corr(self,stk_id, trade_date, concept_list,use_time = 242):
        #return_mean = self.pct_chg.loc[:trade_date].mean()
        #return_std = self.pct_chg.loc[:trade_date].std()
        #price_return = self.close_badj.loc[:trade_date].pct_change(use_time)*100
        #Zscore = (price_return - return_mean) / return_std
        #period_corr = Zscore[concept_list].mul(Zscore[stk_id], axis=0) / (((Zscore[concept_list] ** 2).add(Zscore[stk_id] ** 2, axis=0)) / 2)
        #corr_result = period_corr.loc[:trade_date].iloc[-self.use_time:].mean().sort_values(ascending=False).dropna()
        # 单期相关性均值和标准差
        return_mean = self.pct_chg.loc[:trade_date].iloc[-use_time:].mean()
        return_std = self.pct_chg.loc[:trade_date].iloc[-use_time:].std()
        price_return = (self.close_badj.loc[:trade_date].iloc[-use_time:]/self.close_badj.loc[:trade_date].iloc[-use_time:].iloc[0]-1) * 100

        Zscore = (price_return - return_mean) / return_std
        period_corr = (Zscore[concept_list].mul(Zscore[stk_id],axis=0)) / ((Zscore[concept_list] ** 2).add(Zscore[stk_id] ** 2,axis=0) / 2)
        corr_result = period_corr.mean().dropna().sort_values()

        return corr_result
    # 3、K线相似度
    def Kline_corr(self,stk_id, trade_date, concept_list,use_time = 242):
        # 趋势相关性
        #close_corr = self.cal_corr(self.close_badj, stk_id, trade_date, concept_list, use_time=self.use_time)
        #open_corr = self.cal_corr(self.open_badj, stk_id, trade_date, concept_list, use_time=self.use_time)
        #high_corr = self.cal_corr(self.high_badj, stk_id, trade_date, concept_list, use_time=self.use_time)
        #low_corr = self.cal_corr(self.low_badj, stk_id, trade_date, concept_list, use_time=self.use_time)
        #Trend_corr = (close_corr + open_corr + high_corr + low_corr) / 4

        close_corr = self.cal_corr(self.close / self.pre_close, stk_id, trade_date, concept_list,use_time=use_time)
        open_corr = self.cal_corr(self.open / self.pre_close, stk_id, trade_date, concept_list, use_time=use_time)
        high_corr = self.cal_corr(self.high / self.pre_close, stk_id, trade_date, concept_list, use_time=use_time)
        low_corr = self.cal_corr(self.low / self.pre_close, stk_id, trade_date, concept_list, use_time=use_time)
        Trend_corr = (close_corr + open_corr + high_corr + low_corr) / 4
        # 形态相关性：
        inday_pct = self.close / self.open - 1
        up_down_position = (inday_pct > 0)
        up_down_position = (up_down_position[concept_list].T == up_down_position[stk_id]).T
        difference_pct = abs(self.pct_chg[concept_list].T - self.pct_chg[stk_id]).T
        difference_pct = (20 - difference_pct) / 20
        shape_corr = (up_down_position.loc[:trade_date].iloc[-use_time:] * difference_pct.loc[:trade_date].iloc[-use_time:]).sum() / self.use_time
        shape_corr[shape_corr < 0] = 0
        Runaway_corr = (Trend_corr * shape_corr).sort_values().dropna()

        return Runaway_corr
    # 4、风格因子
    def barra_factor(self,trade_date, read_path = '/arch1/group/800442/800319/AAcross/basic/'):
        date_list,code_list = np.load(read_path + 'date_list.npy'),np.load(read_path + 'code_list.npy')
        # (1)规模因子
        LNCAP = pd.DataFrame(np.load(read_path + 'barras/LNCAP.npy')[:,0,:],index=date_list,columns=code_list).loc[trade_date]
        MIDCAP = pd.DataFrame(np.load(read_path + 'barras/MIDCAP.npy')[:,0,:],index=date_list,columns=code_list).loc[trade_date]
        # （2）波动率因子
        BETA = pd.DataFrame(np.load(read_path + 'barras/BETA.npy')[:,0,:],index=date_list,columns=code_list).loc[trade_date] # beta
        HSIGMA = pd.DataFrame(np.load(read_path + 'barras/HSIGMA.npy')[:,0,:],index=date_list,columns=code_list).loc[trade_date] # 残差收益率波动率
        DASTD = pd.DataFrame(np.load(read_path + 'barras/DASTD.npy')[:,0,:],index=date_list,columns=code_list).loc[trade_date] # 标准差
        CMRA = pd.DataFrame(np.load(read_path + 'barras/CMRA.npy')[:,0,:],index=date_list,columns=code_list).loc[trade_date] # 累计收益范围
        # 二级因子
        RV = pd.DataFrame(np.load(read_path + 'barras/RV.npy')[:,0,:],index=date_list,columns=code_list).loc[trade_date] # 残差波动率
        # (3）流动性因子
        STOM = pd.DataFrame(np.load(read_path + 'barras/STOM.npy')[:,0,:],index=date_list,columns=code_list).loc[trade_date] # 月换手率
        STOQ = pd.DataFrame(np.load(read_path + 'barras/STOQ.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 季换手率
        STOA = pd.DataFrame(np.load(read_path + 'barras/STOA.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 年换手率
        ATVR = pd.DataFrame(np.load(read_path + 'barras/ATVR.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 年化交易量比率
        # (4）动量因子
        STREV = pd.DataFrame(np.load(read_path + 'barras/STREV.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 短期反转
        SEASON = pd.DataFrame(np.load(read_path + 'barras/SEASON.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 季节因子
        INDMOM = pd.DataFrame(np.load(read_path + 'barras/INDMOM.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 行业动量因子
        RSTR = pd.DataFrame(np.load(read_path + 'barras/RSTR.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 相对强度
        HA = pd.DataFrame(np.load(read_path + 'barras/HA.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 历史alpha
        # （5）质量因子
        # 杠杆因子
        MLEV = pd.DataFrame(np.load(read_path + 'barras/MLEV.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 市场杠杆
        BLEV = pd.DataFrame(np.load(read_path + 'barras/BLEV.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date] # 账面杠杆
        DTOA = pd.DataFrame(np.load(read_path + 'barras/DTOA.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 资产负债比
        # 盈利能力
        VSAL = pd.DataFrame(np.load(read_path + 'barras/VSAL.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 营业收入波动率
        VERN = pd.DataFrame(np.load(read_path + 'barras/VERN.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 盈利波动率
        VFLO = pd.DataFrame(np.load(read_path + 'barras/VFLO.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 现金流波动率
        ETOPF_STD = pd.DataFrame(np.load(read_path + 'barras/ETOPF_STD.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 分析师预测EP比标准差
        # 应收质量
        ABS = pd.DataFrame(np.load(read_path + 'barras/ABS.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 资产负债表应计项目
        ACF = pd.DataFrame(np.load(read_path + 'barras/ACF.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 现金流量表应计项目
        # 盈利能力
        ATO = pd.DataFrame(np.load(read_path + 'barras/ATO.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 资产周转率
        GP = pd.DataFrame(np.load(read_path + 'barras/GP.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 资产毛利率
        GPM = pd.DataFrame(np.load(read_path + 'barras/GPM.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date] # 销售毛利率
        ROA = pd.DataFrame(np.load(read_path + 'barras/GPM.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 总资产收益率
        # 股本质量
        AGRO = pd.DataFrame(np.load(read_path + 'barras/AGRO.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 总资产增长率
        IGRO = pd.DataFrame(np.load(read_path + 'barras/IGRO.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 股票发行量增长率
        CXGRO = pd.DataFrame(np.load(read_path + 'barras/CXGRO.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 资本支出增长率
        # （6）价值因子：
        BTOP = pd.DataFrame(np.load(read_path + 'barras/BTOP.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 账面市值比
        # 盈利比例
        TETOP = pd.DataFrame(np.load(read_path + 'barras/TETOP.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # EP比
        APETP = pd.DataFrame(np.load(read_path + 'barras/APETP.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 分析师预测EP比
        CETOP = pd.DataFrame(np.load(read_path + 'barras/CETOP.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 现金盈利价格比
        EM = pd.DataFrame(np.load(read_path + 'barras/EM.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 企业价值倍数的倒数
        # 长期回报
        LTRSTR = pd.DataFrame(np.load(read_path + 'barras/LTRSTR.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 长期相对强度
        LTHALPHA = pd.DataFrame(np.load(read_path + 'barras/LTHALPHA.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 长期Alpha
        # （7）成长因子：
        PG3Y = pd.DataFrame(np.load(read_path + 'barras/PG3Y.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 分析师预测长期盈利增长率
        EGRO = pd.DataFrame(np.load(read_path + 'barras/EGRO.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 每股收益增长率
        SGRO = pd.DataFrame(np.load(read_path + 'barras/SGRO.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 每股营业收入增长率
        # （8）情绪因子
        RRIBS = pd.DataFrame(np.load(read_path + 'barras/RRIBS.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 调整比率
        EARNC = pd.DataFrame(np.load(read_path + 'barras/EARNC.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date] # 分析师预测每股收益变化
        EPIBSC = pd.DataFrame(np.load(read_path + 'barras/EARNC.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 分析师预测EP比变化
        # （9）红利因子
        DTOP = pd.DataFrame(np.load(read_path + 'barras/DTOP.npy')[:, 0, :], index=date_list, columns=code_list).loc[trade_date]  # 股息率

        # 最终结果：把所有的结果拼接到一个dataframe钟：
        factor_list = ['LNCAP', 'MIDCAP',
         'BETA', 'HSIGMA', 'DASTD', 'CMRA',
         'STOM', 'STOQ', 'STOQ', 'STOA', 'ATVR',
         'STREV', 'SEASON', 'INDMOM', 'RSTR', 'HA',
         'MLEV', 'BLEV', 'DTOA', 'VSAL', 'VERN', 'VFLO', 'ETOPF_STD', 'ABS', 'ACF', 'ATO', 'GP','GPM','ROA','AGRO','IGRO','CXGRO',
         'BTOP','TETOP','APETP','CETOP','EM','LTRSTR','LTHALPHA',
         'PG3Y','EGRO','SGRO',
         'RRIBS','EARNC','EPIBSC',
         'DTOP']

        factor_result = pd.DataFrame(columns=factor_list)
        for factor in factor_list:
            factor_result[factor] = eval(factor)

        return factor_result
    # 5、个股相似度距离评价
    def stock_distance(self,stk_id,concept_list,df,distance = 'euclidean'):
        # 距离参数：
        # euclidean：欧氏距离     seuclidean：标准化欧氏距离   sqeuclidean：平方欧几里得距离
        # cosine：余弦相似度距离  correlation：相关性距离
        # cityblock：哈曼顿距离   canberra：堪培拉距离（是哈曼顿距离的加权版本） chebyshev：切比雪夫距离
        # braycurtis：衡量微生物菌落相似度的距离

        # 1、先对数据做标准化处理：Z-score
        df.replace([np.inf,-np.inf],np.nan,inplace=True)
        df = (df - df.mean())/df.std()
        df.fillna(0,inplace = True)
        # 2、开始计算距离
        distance_result = pd.DataFrame(squareform(pdist(df, distance),checks = True),index=df.index,columns=df.index)
        distance_result = distance_result.loc[stk_id].loc[concept_list].sort_values().dropna()

        return distance_result
    # 6、个股聚类
    def stock_clustering(self,df,stk_id,Type='Kmeans',n_clusters=50,):
        # 先对数据做标准化处理：Z-score
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df = (df - df.mean()) / df.std()
        df.fillna(0, inplace=True)
        if Type == 'Kmeans':
            # 1、Kmeans聚类：n_clusters-分组数，fit_predict相当于把fit和predict两步作为一步合并起来一起使用
            cluster_Kmean = KMeans(n_clusters=n_clusters).fit(df)
            cluster_result = pd.Series(cluster_Kmean.predict(df),index=df.index)
        elif Type == '层次聚类':
            # 2、层次聚类
            cluster_agglomerative = AgglomerativeClustering(n_clusters=n_clusters, affinity='euclidean', compute_full_tree='True', linkage='ward').fit_predict(df)
            cluster_result = pd.Series(cluster_agglomerative, index=df.index)
        elif Type == '树聚类':
            # 3、基于树的层次聚类
            cluster_birch = Birch(threshold=1, branching_factor=50, n_clusters=n_clusters, compute_labels=True).fit(df)
            cluster_result = pd.Series(cluster_birch.predict(df),index=df.index)
        elif Type == '均值漂移':
            # 4、均值漂移聚类：不太好用
            # cluster_allbool:如果为True，那么所有点都会被聚集；为false，则给离群值标签 -1。
            cluster_meanshfit = MeanShift(bandwidth=None, seeds=None, bin_seeding=True, cluster_all=True).fit(df)
            cluster_result = pd.Series( cluster_meanshfit.labels_, index=df.index)
        elif Type == '谱聚类':
            # 5、谱聚类
            cluster_Spectral =SpectralClustering(n_clusters=n_clusters,eigen_solver='arpack',
                               n_init=10, gamma=1.0, affinity='rbf', assign_labels='kmeans').fit(df)
            cluster_result = pd.Series(cluster_Spectral.labels_, index=df.index)
        elif Type == '光谱双聚类':
            # 6、光谱双聚类
            cluster_SpectralBi = SpectralBiclustering(n_clusters=40, method='bistochastic',n_best=3, svd_method='randomized',init='k-means++').fit(df)
            cluster_result = pd.Series(cluster_SpectralBi.row_labels_, index=df.index)
        elif Type == 'DBSCAN':
            # 6、密度聚类DBSCAN：不太好用
            cluster_dbscan = DBSCAN(eps=0.5,  # 邻域半径
                   min_samples=5,  # 最小样本点数，MinPts
                   metric='euclidean').fit_predict(df)
            cluster_result = pd.Series(cluster_dbscan, index=df.index)

        concept_list = cluster_result[cluster_result == cluster_result.loc[stk_id]].index.to_list()
        return concept_list

    # 计算最终相关性
    def simi_strategy(self, stk_id, trade_date, concept_list):
        #TODO: 此函数必须复写，并返回Hedge类型
        #stk_id,trade_date = 600111,20211231
        #concept_list = self.get_concept_list(stk_id, trade_date)
        ########################################### 相关性维度数据的统计 #####################################################
        # 1、日收益率相关性
        pct_corr = self.cal_corr(self.pct_chg, stk_id, trade_date, concept_list,use_time = self.use_time)  # 日收益率相关系数
        #close_corr = self.cal_corr(self.close, stk_id, trade_date, concept_list,use_time = self.use_time)  # 收盘价的相关系数
        # 2、盈亏比的相关性：当前回撤相关性
        #accumulative_return = (self.pct_chg.loc[:trade_date].iloc[-self.use_time:]/100+1).cumprod()
        #maxdown = accumulative_return / np.fmax.accumulate(accumulative_return, axis=0) - 1
        #maxdown_corr = self.cal_corr(maxdown,stk_id, trade_date, concept_list,use_time = self.use_time)
        # 3、日振幅的相关系数
        #amplitude = pd.concat([self.high,self.pre_close]).max(level=0) / pd.concat([self.low,self.pre_close]).min(level=0) - 1
        #amplitude_corr = self.cal_corr(amplitude, stk_id, trade_date, concept_list, use_time=self.use_time)
        # 4、单期相似度
        #period_corr = self.period_corr(stk_id, trade_date,concept_list,use_time= self.use_time)
        # 5、K线相似度
        #Kline_corr = self.Kline_corr(stk_id, trade_date, concept_list,use_time = self.use_time)
        # 6、净值相关性
        #excess_return = self.pct_chg[concept_list].sub(self.pct_chg[stk_id], axis=0)
        #netvalue_corr = abs(excess_return.mean().apply(lambda x:math.exp(x)-1) * excess_return.std()).sort_values()
        # 7、风格相似度
        #factor_result = self.barra_factor(trade_date)

        # 第一步：需要比较的一共有7个数据
        # pct_corr,close_corr,maxdown_corr,amplitude_corr,period_corr,Kline_corr,netvalue_corr

        code_list = list(pct_corr.index[[self.rank]])
        code_weight = [1]

        return code_list,code_weight


if __name__ == '__main__':
    # for rank in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
    #     print(rank)
    rank =0
    self = SimiMethodDemo(start_date=20200101, end_date=20200110, concept='all_market',rank = rank)
    result = self.get_hedge_list(mode='serial')
    util.save_list2pkl(result, hedge_path, 'pct_corr'+str(rank)+'.pkl')


'''
########################################## 多空净值曲线统计 ##################################################
excess_return = self.pct_chg[concept_list].sub(self.pct_chg[stk_id],axis=0)
excess_value = (excess_return.loc[:trade_date].iloc[-self.use_time:]/100+1).cumprod()
# 1、跟踪误差：收益率排序 * 最大回撤排序 * 最大收益排序
maxdown = (excess_value/ np.fmax.accumulate(excess_value,axis=0)-1).min()
maxup = excess_value.max()-1

value_error = excess_value.loc[trade_date].rank(pct=True,ascending=False) * maxup.rank(pct=True,ascending=False) * maxdown.rank(pct=True)
value_error.rank(pct=True).sort_values()

abs(excess_return.mean()*excess_return.std()).sort_values()
# 单位根检验：平稳性，即是否围绕某一常熟上下波动
p_value = excess_value.apply(lambda x: adfuller(x.dropna())[1] if len(x.dropna())>100 else np.nan)
# 白噪声检验：
'''
