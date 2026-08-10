import numpy as np
import pandas as pd
from xquant.marketdata import MarketData


def tick_try(self, context, taskmeta):
    # 生成基于tick的中间变量
    stock = taskmeta.get_stock()
    date = taskmeta.get_date()
    #注意：MarketData初始化时需传入hdfs连                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             接，如下所示
    mdp = MarketData(dfs=context.get_hdfs())
    df = mdp.get_data_by_date('Stock', stock, date)
    if df.empty==False:
        min_list = get_num_time('9:25','9:25')+get_num_time('9:30','11:29')+get_num_time('13:00','15:00') #确定242个时间戳
        conp = ((df['MDTime']>='093000000')&(df['MDTime']<'113000000'))|((df['MDTime']>='130000000')&(df['MDTime']<'150000000'))
        col_list = ['Buy'+str(x)+'OrderQty' for x in range(1,11)]+['Sell'+str(x)+'OrderQty' for x in range(1,11)]
        tmp_use_df = df.loc[conp,['MDTime']+col_list]
        tmp_use_df['minute'] = tmp_use_df['MDTime'].apply(lambda x:int(str(x)[:4]))
        #补上9:25、11:30和15:30的信息:抽取9:25、15:00的第一条tick作为该分钟的数据，抽取11:30的第一个tick合并入11:29
        def tmp_func(df,stime,etime,col_list,minute):
            tmp_df = df.loc[(df['MDTime']>=stime)&(df['MDTime']<etime),['MDTime']+col_list]
            if tmp_df.empty==False:
                tmp_df = tmp_df.sort_values('MDTime').iloc[[0]]
                tmp_df['minute'] = minute
            return tmp_df
        tmp925_df = tmp_func(df,'092500000','093000000',col_list,925)
        tmp1130_df = tmp_func(df,'113000000','113500000',col_list,1129)
        tmp1500_df = tmp_func(df,'150000000','150500000',col_list,1500)
        use_df = pd.concat([tmp_use_df,tmp925_df,tmp1130_df,tmp1500_df]).sort_values('MDTime')
        '''
        ---计算tick1：将(1, 5, 10)档口买、 卖盘口的总挂单量先按SUM聚合到分钟级别（记为BV, SV)。
        最终计算(BV - SV) / (BV + SV)， 并保留BV, SV原始值。 共9个因子。(BV1,SV1,BV5,SV5,BV10,SV10,BS_ratio1,BS_ratio5,BS_ratio10)
        '''
        raw_BV = use_df[['minute']+['Buy'+str(x)+'OrderQty' for x in range(1,11)]].groupby('minute').sum()
        raw_SV = use_df[['minute']+['Sell'+str(x)+'OrderQty' for x in range(1,11)]].groupby('minute').sum()
        BV1,SV1 = raw_BV['Buy1OrderQty'], raw_SV['Sell1OrderQty']
        BV5,SV5 = raw_BV[['Buy'+str(x)+'OrderQty' for x in range(1,6)]].sum(axis=1), raw_SV[['Sell'+str(x)+'OrderQty' for x in range(1,6)]].sum(axis=1)
        BV10,SV10 = raw_BV[['Buy'+str(x)+'OrderQty' for x in range(1,11)]].sum(axis=1), raw_SV[['Sell'+str(x)+'OrderQty' for x in range(1,11)]].sum(axis=1)
        BS_ratio1,BS_ratio5,BS_ratio10 = (BV1-SV1)/(BV1+SV1),(BV5-SV5)/(BV5+SV5),(BV10-SV10)/(BV10+SV10)
        '''
        ---计算tick2：将前5档口买、 卖盘口的挂单量先分别纵向取max，每分钟得到5个值,再横向取max，即5个值中的max，得到每分钟一个值（记为BMV, SMV)。
        最终计算(BMV - SMV) / (BMV + SMV)，并保留BMV, SMV原始值。 共3个因子。(BMV5,SMV5,BSM_ratio5)
        '''
        raw_BMV = use_df[['minute'] + ['Buy' + str(x) + 'OrderQty' for x in range(1, 6)]].groupby('minute').max()
        raw_SMV = use_df[['minute'] + ['Sell' + str(x) + 'OrderQty' for x in range(1, 6)]].groupby('minute').max()
        BMV5 = raw_BMV.max(axis=1)
        SMV5 = raw_SMV.max(axis=1)
        BSM_ratio5 = (BMV5-SMV5)/(BMV5+SMV5)
        '''
        ---计算tick3：先按SUM将前10档买、 卖盘口的挂单量聚合到分钟级别，然后分别计算1-10盘口挂单量的lambda x: x.diff().mean() / x.sum()
        若x.sum=0 则为nan。 共2个因子(BKV10,SKV10)
        '''
        BKV10 = raw_BV.diff(axis=1).mean(axis=1)/raw_BV.sum(axis=1)
        SKV10 = raw_SV.diff(axis=1).mean(axis=1)/raw_SV.sum(axis=1)
        '''
        ---计算tick4：按照Tick计算前(5, 10)档盘口的vwap价格与当前成交价的距离，然后计算买卖距离的比值(price-B_vwap)/(S_vwap-price)。
        取均值聚合到分钟。若买盘或卖盘的vwap为0则因子值为nan。 共2个因子(BSdst_ratio5,BSdst_ratio10)
        '''
        # 提取价格数据
        col_list2 = ['LastPx']+['Buy'+str(x)+'Price' for x in range(1,11)]+['Sell'+str(x)+'Price' for x in range(1,11)]
        tmp_use_df2 = df.loc[conp,['MDTime']+col_list2]
        tmp_use_df2['minute'] = tmp_use_df['MDTime'].apply(lambda x:int(str(x)[:4]))
        #补上9:25、11:30和15:30的信息:抽取9:25、15:00的第一条tick作为该分钟的数据，抽取11:30的第一个tick合并入11:29
        tmp925_df2 = tmp_func(df,'092500000','093000000',col_list2,925)
        tmp1130_df2 = tmp_func(df,'113000000','113500000',col_list2,1129)
        tmp1500_df2 = tmp_func(df,'150000000','150500000',col_list2,1500)
        use_df2 = pd.concat([tmp_use_df2,tmp925_df2,tmp1130_df2,tmp1500_df2]).sort_values('MDTime')
        merge_df = pd.merge(use_df,use_df2,on=['MDTime','minute'],how='outer')
        # 计算前五档对应因子
        amt5_B_tick = np.sum(merge_df[['Buy'+str(x)+'Price' for x in range(1,6)]].values*merge_df[['Buy' + str(x) + 'OrderQty' for x in range(1, 6)]].values,axis=1)
        amt5_S_tick = np.sum(merge_df[['Sell'+str(x)+'Price' for x in range(1,6)]].values*merge_df[['Sell' + str(x) + 'OrderQty' for x in range(1, 6)]].values,axis=1)
        vwap5_B_tick = pd.Series(amt5_B_tick/np.sum(merge_df[['Buy' + str(x) + 'OrderQty' for x in range(1, 6)]].values,axis=1)).replace(0,np.nan)
        vwap5_S_tick = pd.Series(amt5_S_tick/np.sum(merge_df[['Sell' + str(x) + 'OrderQty' for x in range(1, 6)]].values,axis=1)).replace(0,np.nan)
        tmp_BSdst_ratio5 = pd.DataFrame((merge_df['LastPx'].values-vwap5_B_tick.values)/(vwap5_S_tick.values-merge_df['LastPx'].values),index=merge_df['minute'].tolist(),columns=['BSdst_ratio5'])
        BSdst_ratio5 = tmp_BSdst_ratio5.reset_index().groupby('index').mean()['BSdst_ratio5'].replace([np.inf,-np.inf],np.nan)
        BSdst_ratio5.index.name = 'minute'
        # 计算前十档对应因子
        amt10_B_tick = np.sum(merge_df[['Buy'+str(x)+'Price' for x in range(1,11)]].values*merge_df[['Buy' + str(x) + 'OrderQty' for x in range(1, 11)]].values,axis=1)
        amt10_S_tick = np.sum(merge_df[['Sell'+str(x)+'Price' for x in range(1,11)]].values*merge_df[['Sell' + str(x) + 'OrderQty' for x in range(1, 11)]].values,axis=1)
        vwap10_B_tick = pd.Series(amt10_B_tick/np.sum(merge_df[['Buy' + str(x) + 'OrderQty' for x in range(1, 11)]].values,axis=1)).replace(0,np.nan)
        vwap10_S_tick = pd.Series(amt10_S_tick/np.sum(merge_df[['Sell' + str(x) + 'OrderQty' for x in range(1, 11)]].values,axis=1)).replace(0,np.nan)
        tmp_BSdst_ratio10 = pd.DataFrame((merge_df['LastPx'].values-vwap10_B_tick.values)/(vwap10_S_tick.values-merge_df['LastPx'].values),index=merge_df['minute'].tolist(),columns=['BSdst_ratio10'])
        BSdst_ratio10 = tmp_BSdst_ratio10.reset_index().groupby('index').mean()['BSdst_ratio10'].replace([np.inf,-np.inf],np.nan)
        BSdst_ratio10.index.name = 'minute'
        #整合因子值
        results = pd.DataFrame([BV1,BV5,BV10,SV1,SV5,SV10,BS_ratio1,BS_ratio5,BS_ratio10,BMV5,SMV5,BSM_ratio5,BKV10,SKV10,BSdst_ratio5,BSdst_ratio10],index=['BV1','BV5','BV10','SV1','SV5','SV10','BS_ratio1','BS_ratio5','BS_ratio10','BMV5','SMV5','BSM_ratio5','BKV10','SKV10','BSdst_ratio5','BSdst_ratio10']).T.reset_index()
        if len(results)!=242: #若每日数据不足242条，用nan补齐
            idx_min = list(set(min_list).difference(results['minute'].tolist()))
            tmp_min = pd.DataFrame(np.nan,columns=results.columns.difference(['minute']),index=range(len(idx_min)))
            tmp_min['minute'] = idx_min
            adj_results = pd.concat([results,tmp_min]).sort_values('minute')
        else:
            adj_results = results.copy()
        adj_results['minute'] = adj_results['minute'].apply(lambda x:int(x))
        adj_results.index = pd.Series(adj_results['minute']).apply(lambda x:date+'_'+str(x))
        adj_results = adj_results.drop(columns=['minute'])
        context.save_as_pickle(adj_results, '{}.pickle'.format(stock))


def transaction_try(self, context, taskmeta):
    # 生成基于transaction的中间变量
    stock = taskmeta.get_stock()
    date = taskmeta.get_date()
    #注意：MarketData初始化时需传入hdfs连                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             接，如下所示
    mdp = MarketData(dfs=context.get_hdfs())
    df = mdp.get_data_by_date('Transaction', stock, date)
    if df.empty == False:
        min_list = get_num_time('9:25', '9:25') + get_num_time('9:30', '11:29') + get_num_time('13:00', '15:00') #确定242个时间戳
        use_df = df.loc[(df['TradeType']==0)&(df['TradeQty']>0),['MDTime','TradeBSFlag','TradePrice','TradeQty']].sort_values('MDTime')
        use_df['minute'] = use_df['MDTime'].apply(lambda x:int(str(x)[:4]))
        use_df['TradeMoney'] = use_df['TradePrice']*use_df['TradeQty']
        '''
        ---计算tran1：每分钟总成交笔数。 共1个因子(tranNum)
        '''
        tranNum = use_df[['minute','TradeQty']].groupby('minute').count()['TradeQty']
        '''
        ---计算tran2： 每分钟B/S成交笔数的比值。 共1个因子(BSNum_ratio)
        '''
        tranNum_B = use_df.loc[use_df['TradeBSFlag'] == 1,['minute','TradeQty']].groupby('minute').count()['TradeQty']
        tranNum_S = use_df.loc[use_df['TradeBSFlag'] == 2, ['minute', 'TradeQty']].groupby('minute').count()['TradeQty']
        BSNum_ratio = tranNum_B/tranNum_S
        '''
        ---计算tran3： B、S每笔平均成交金额的比值。 共1个因子(BSavgamt_ratio)
        '''
        tranamt_B = use_df.loc[use_df['TradeBSFlag'] == 1,['minute','TradeMoney']].groupby('minute').sum()['TradeMoney']
        tranamt_S = use_df.loc[use_df['TradeBSFlag'] == 2, ['minute', 'TradeMoney']].groupby('minute').sum()['TradeMoney']
        BSavgamt_ratio = (tranamt_B/tranNum_B)/(tranamt_S/tranNum_S)
        '''
        ---计算tran4： 取全天成交明细，计算quantile 10%分位数的单笔成交金额（设为LV)，标记所有成交金额大于LV的成交明细为1（Tag)
        然后区分B、 S将Tag SUM聚合到分钟，最后统一除以全天总成交笔数归一化。共2个因子(BNum_trun, SNum_trun)
        '''
        LV = use_df['TradeMoney'].quantile(0.1)
        BNum_trun = use_df.loc[(use_df['TradeBSFlag'] == 1)&(use_df['TradeMoney']>LV),['minute','TradeQty']].groupby('minute').count()['TradeQty']/len(use_df)
        SNum_trun = use_df.loc[(use_df['TradeBSFlag'] == 2) & (use_df['TradeMoney']>LV),['minute', 'TradeQty']].groupby('minute').count()['TradeQty']/len(use_df)
        '''
        ---计算tran5： 从daily数据获得当天股票的自由流通市值（记为FFV)，标记所有成交金额大于FFV * 1E-4的成交明细为1.
        然后区分B、 S将单笔成交金额SUM聚合到分钟。共2个因子(Bamt_trun, Samt_trun)
        '''
        FFV = self._FFV.loc[pd.to_datetime(date,format='%Y%m%d'),stock]
        Bamt_trun = use_df.loc[(use_df['TradeBSFlag'] == 1)&(use_df['TradeMoney']>FFV*1e-4),['minute','TradeMoney']].groupby('minute').sum()['TradeMoney']
        Samt_trun = use_df.loc[(use_df['TradeBSFlag'] == 2)&(use_df['TradeMoney']>FFV*1e-4),['minute','TradeMoney']].groupby('minute').sum()['TradeMoney']
        # 整合因子值
        results = pd.DataFrame([tranNum,BSNum_ratio,BSavgamt_ratio,BNum_trun,SNum_trun,Bamt_trun,Samt_trun],
                               index=['tranNum','BSNum_ratio','BSavgamt_ratio','BNum_trun','SNum_trun','Bamt_trun','Samt_trun']).T.reset_index()
        if len(results)!=242: #若每日数据不足242条，用nan补齐
            idx_min = list(set(min_list).difference(results['minute'].tolist()))
            tmp_min = pd.DataFrame(np.nan,columns=results.columns.difference(['minute']),index=range(len(idx_min)))
            tmp_min['minute'] = idx_min
            adj_results = pd.concat([results,tmp_min]).sort_values('minute')
        else:
            adj_results = results.copy()
        adj_results['minute'] = adj_results['minute'].apply(lambda x:int(x))
        adj_results.index = pd.Series(adj_results['minute']).apply(lambda x:date+'_'+str(x))
        adj_results = adj_results.drop(columns=['minute'])
        context.save_as_pickle(adj_results, '{}.pickle'.format(stock))

def get_num_time(stime,etime,freq='1min'):
    #计算区间内指定步长的分钟时间列表，时间为int
    t_list = pd.date_range(start=stime,end=etime,freq='1min').strftime('%H%M').tolist()
    output = pd.Series(t_list).apply(lambda x:int(x))
    return output.tolist()