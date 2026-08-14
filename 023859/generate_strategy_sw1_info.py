import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()

start_date, end_date = 20210701, 20241216
# end_date_next = int(s.tradingday(end_date,2)[-1])
trading_days = s.tradingday(start_date, end_date)

print('交易日个数：%s'%(len(trading_days)))
vote_num = 2
# 读取策略数据

# df_saturn = pd.read_pickle('/data/user/018107/share_file/for_tsq/saturn/saturn_v6_20160101_20241202_931_1000_0.10_0.10_1000_1500_250_20.pkl')
# df_saturn = df_saturn.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
# df_saturn = df_saturn[['buy_amt','pct']]

# path='/data/user/018107/share_file/for_tsq/SaturnS1_v6/'
# pred1=pd.read_csv(path+'vote_test/maxbeta_signal/SaturnS1_out_20191001_20200701_20201231_testfit_fac_20230415_final_maxbeta9_noroll_merge6models_平均收益夏普比率_20230614.csv').set_index('datelist').loc[20200701:20201231]
# pred1['period']='区间1'
# pred2=pd.read_csv(path+'vote_test/maxbeta_signal/SaturnS1_out_20200401_20210101_20210630_testfit_fac_20230415_final_maxbeta9_noroll_merge6models_平均收益夏普比率_20230614.csv').set_index('datelist').loc[20210101:20210630]
# pred2['period']='区间2'
# pred3=pd.read_csv(path+'vote_test/maxbeta_signal/SaturnS1_out_20201001_20210701_20211231_testfit_fac_20230415_final_maxbeta9_noroll_merge6models_平均收益夏普比率_20230614.csv').set_index('datelist').loc[20210701:20211231]
# pred3['period']='区间3'
# pred4=pd.read_csv(path+'/vote_test/maxbeta_signal/SaturnS1_out_20210401_20220101_20220630_testfit_fac_20230415_final_maxbeta10_noroll_merge6models_avg_test4_20230627.csv').set_index('datelist').loc[20220101:20220630]
# pred4['period']='区间4'
# pred5=pd.read_csv(path+'/vote_test/maxbeta_signal/SaturnS1_out_20211001_20220701_20221231_testfit_fac_20230415_final_maxbeta10_noroll_merge6models_avg_test4_20230629.csv').set_index('datelist').loc[20220701:20221231]
# pred5['period']='区间5'

profit = pd.read_hdf('/data/group/800463/sunss/saturn/profit/20241129/p2_profit_interval_s1_0.10_0.10_1000_1500_250_20.h5')
profit = profit.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

df_saturn = pd.read_csv('/data/user/013550/For_TSQ/saturn_v6/20230101_20241216_signal.csv')
df_saturn['dt'] = pd.to_datetime(df_saturn['datelist'].astype(str))
df_saturn['Ticker'] = df_saturn['stockID']
df_saturn = df_saturn.set_index(['dt','Ticker'])[['vote_sum_pred']] #对齐
df_saturn = pd.concat([df_saturn,profit[['pct','buy_amt']]],axis=1,join='inner')

df_saturn['sign'] = (df_saturn['vote_sum_pred'] >= vote_num).astype(float)
df_saturn['strategy'] = 'saturn'
df_saturn_sign = df_saturn[df_saturn['sign']==1]
print('saturn基础样本个数：%s saturn信号样本个数：%s 参与率：%s'%(len(df_saturn),len(df_saturn_sign),len(df_saturn_sign)/len(df_saturn)))

# df_saturn['vote_sum_pred'] = pred.set_index(['dt','Ticker'])['vote_sum_pred'] #对齐
# df_saturn['sign'] = (df_saturn['vote_sum_pred'] >= vote_num).astype(float)
# df_saturn['strategy'] = 'saturn'
# df_saturn_sign = df_saturn[df_saturn['sign']==1]
# print('saturn基础样本个数：%s saturn信号样本个数：%s 参与率：%s'%(len(df_saturn),len(df_saturn_sign),len(df_saturn_sign)/len(df_saturn)))
#
# df_saturn_20210701_20220630 = pd.read_csv('/data/user/013550/For_TSQ/signal/saturn/fac_20241129/集成信号_20210701_20220630.csv')
# df_saturn_20220701_20240630 = pd.read_csv('/data/user/021012/团队分享/for_tsq/saturn/fac_20241129_s1/集成信号_20220701_20240630_all.csv')
# df_saturn = pd.concat([df_saturn_20210701_20220630, df_saturn_20220701_20240630])
#
# df_saturn = pd.read_csv('/data/user/013550/For_TSQ/signal/saturn/fac_20241129_label/集成信号_20210701_20240630.csv')
#
# df_saturn['dt'] = pd.to_datetime(df_saturn['dt'])
# df_saturn = df_saturn.set_index(['dt','Ticker'])
# df_saturn = df_saturn.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
# df_saturn = df_saturn[['label_pct','label_buy_amt','vote_sum_pred']].rename(columns={'label_pct':'pct','label_buy_amt':'buy_amt'})
# df_saturn['strategy'] = 'saturn'
# df_saturn['sign'] = (df_saturn['vote_sum_pred'] >= vote_num).astype(float)
# df_saturn_sign = df_saturn[df_saturn['sign']==1]
# print('saturn基础样本个数：%s saturn信号样本个数：%s 参与率：%s'%(len(df_saturn),len(df_saturn_sign),len(df_saturn_sign)/len(df_saturn)))

# df_ceres = pd.read_csv('/data/user/021012/团队分享/for_tsq/ceres/fac_20241203/集成信号_20210701_20220630.csv')
# df_ceres['dt'] = pd.to_datetime(df_ceres['dt'])
# df_ceres = df_ceres.set_index(['dt','Ticker'])
# df_ceres = df_ceres.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
# df_ceres = df_ceres[['label_pct','label_buy_amt','vote_sum_pred']].rename(columns={'label_pct':'pct','label_buy_amt':'buy_amt'})
# df_ceres['strategy'] = 'ceres'
# df_ceres['sign'] = (df_ceres['vote_sum_pred'] >= vote_num).astype(float)
# df_ceres_sign = df_ceres[df_ceres['sign']==1]
# print('ceres基础样本个数：%s ceres信号样本个数：%s 参与率：%s'%(len(df_ceres),len(df_ceres_sign),len(df_ceres_sign)/len(df_ceres)))
#
# df_mimas = pd.read_csv('/data/user/013550/For_TSQ/signal/mimas/fac_20241203/集成信号_20210701_20220630.csv')
# df_mimas['dt'] = pd.to_datetime(df_mimas['dt'])
# df_mimas = df_mimas.set_index(['dt','Ticker'])
# df_mimas = df_mimas.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
# df_mimas = df_mimas[['label_pct','label_buy_amt','vote_sum_pred']].rename(columns={'label_pct':'pct','label_buy_amt':'buy_amt'})
# df_mimas['strategy'] = 'mimas'
# df_mimas['sign'] = (df_mimas['vote_sum_pred'] >= vote_num).astype(float)
# df_mimas_sign = df_mimas[df_mimas['sign']==1]
# print('mimas基础样本个数：%s mimas信号样本个数：%s 参与率：%s'%(len(df_mimas),len(df_mimas_sign),len(df_mimas_sign)/len(df_mimas)))

# df_ceres_p4 = pd.read_csv('/dfs/user/023859/Hedging/ceres/集成信号_20201201_20211130_withp4_sample.csv',index_col=0)
# df_ceres_p4['dt'] = pd.to_datetime(df_ceres_p4['dt'])
# df_ceres_p4 = df_ceres_p4.set_index(['dt','Ticker'])
# df_ceres_p4 = df_ceres_p4.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
# df_ceres_p4 = df_ceres_p4[['label_pct','label_buy_amt','vote_sum_pred']].rename(columns={'label_pct':'pct','label_buy_amt':'buy_amt'})
# df_ceres_p4['sign'] = (df_ceres_p4['vote_sum_pred'] >= vote_num).astype(float)
# df_ceres_p4['strategy'] = 'p4'
# df_ceres_p4.loc[df_ceres_p4.index.isin(df_ceres.index),'strategy'] = 'ceres'
# df_ceres_p4_sign = df_ceres_p4[df_ceres_p4['sign']==1]
# print('ceres+p4基础样本个数：%s ceres+p4信号样本个数：%s 参与率：%s'%(len(df_ceres_p4),len(df_ceres_p4_sign),len(df_ceres_p4_sign)/len(df_ceres_p4)))
#
# df_p4 = df_ceres_p4[df_ceres_p4['strategy']=='p4'].sort_index()
# df_p4_sign = df_p4[df_p4['sign']==1]
# print('p4基础样本个数：%s p4信号样本个数：%s 参与率：%s'%(len(df_p4),len(df_p4_sign),len(df_p4_sign)/len(df_p4)))
#
# df_strategy_basic = pd.concat([df_saturn,df_ceres,df_mimas],axis=0).sort_index() # saturn、ceres、mimas策略样本一起考虑
# df_strategy_sign = pd.concat([df_saturn_sign,df_ceres_sign,df_mimas_sign],axis=0).sort_index() # saturn、ceres、mimas策略样本一起考虑
df_strategy_basic = df_saturn.sort_index() # saturn、ceres、mimas策略样本一起考虑
df_strategy_sign = df_saturn_sign.sort_index() # saturn、ceres、mimas策略样本一起考虑

# df_strategy_sign['profit'] = df_strategy_sign['buy_amt']*(df_strategy_sign['pct']-0.004) # europa、jupiter、metis、leda扣千2，saturn、ceres、mimas扣千4
# df_saturn_sign['profit'] = df_saturn_sign['buy_amt']*(df_saturn_sign['pct']-0.004)
# df_ceres_sign['profit'] = df_ceres_sign['buy_amt']*(df_ceres_sign['pct']-0.004)

dt_strategy_basic_stock_list = df_strategy_basic.reset_index().groupby('dt')['Ticker'].agg(lambda x: list(set(x)))

strategy_basic_sw1_info = []
for dt in tqdm(dt_strategy_basic_stock_list.index):
    date = dt.strftime('%Y%m%d')
    if date < '20211213':
        flag = 'SW'
    else:
        flag = 'SW2021'
    sw_index_date = pd.DataFrame(index = dt_strategy_basic_stock_list.loc[dt], columns = ['sw_industry_code_1','sw_industry_name_1'])
    sw_index_date.index.names = ['stock']
    sw1 = s.hsi(dt_strategy_basic_stock_list.loc[dt], date, flag, 1).set_index('stock')
    sw_index_date[['sw_industry_code_1','sw_industry_name_1']] = sw1[['industry_code','industry_name']]
    sw_index_date = sw_index_date.reset_index()
    sw_index_date['dt'] = dt
    sw_index_date = sw_index_date.rename(columns={'stock':'Ticker'})
    sw_index_date = sw_index_date.set_index(['dt','Ticker'])[['sw_industry_code_1','sw_industry_name_1']]
    strategy_basic_sw1_info.append(sw_index_date)

strategy_basic_sw1_info = pd.concat(strategy_basic_sw1_info,axis=0)
df_strategy_sign_sw1 = df_strategy_sign.reset_index().merge(strategy_basic_sw1_info.reset_index(),on=['dt','Ticker'],how='left').set_index(['dt','Ticker']).sort_index() #策略信号样本收益信号及所属申万一级行业

df_strategy_sign_sw1.to_pickle('/data/user/023859/Hedging/saturn_v6/df_strategy_sign_vote%s_sw1_%s_%s.pkl'%(vote_num, start_date, end_date))

