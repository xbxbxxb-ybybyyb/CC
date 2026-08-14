import numpy as np
import pandas as pd
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()

start_date, end_date = 20201201, 20230531
basic_schl_pct_thresh = 0
vote_num = 4

index_list=['000852.SH']
index_md = pd.read_pickle('/data/user/023859/Hedging/index_price_%s_%s.pkl'%(start_date,end_date))
df_ceres = pd.read_pickle('/data/user/023859/Hedging/ceres/ceres_price_%s_%s.pkl'%(start_date,end_date))
df_ceres_hl = df_ceres.copy()

zcz = (((df_ceres.reset_index()['Ticker'].apply(lambda x: x[0] == '3')) & (df_ceres.reset_index()['dt'] >= '2020-08-24')) |
       (df_ceres.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values

minute_df_hl_amt_all = pd.read_pickle('/data/user/023859/Hedging/ceres/ceres_minute_high_to_close_amt_%s_%s.pkl'%(start_date,end_date))
minute_df_close_all = pd.read_pickle('/data/user/023859/Hedging/ceres/ceres_minute_close_%s_%s.pkl'%(start_date,end_date))

minute_list = [minute for minute in minute_df_hl_amt_all.columns]
df_ceres[minute_list] = minute_df_close_all
df_ceres[minute_list] = df_ceres[minute_list].div(df_ceres[931],axis=0)-1 #相对于0931的收益率
df_ceres_hl[minute_list] = minute_df_hl_amt_all
df_ceres_hl[minute_list] = df_ceres_hl[minute_list].div(df_ceres_hl['pre_close'],axis=0)
df_ceres_hl.loc[zcz,minute_list]=df_ceres_hl.loc[zcz,minute_list]/2

daymin_ceres_basic_hl_pct = df_ceres_hl[minute_list].groupby('dt').mean()
daymin_ceres_basic_hl_pct = daymin_ceres_basic_hl_pct[[col for col in daymin_ceres_basic_hl_pct.columns if col >= 931]]

df_ceres = df_ceres.rename(columns={'label_pct':'pct','label_buy_amt':'buy_amt'})
df_ceres['profit']=df_ceres['buy_amt']*(df_ceres['pct']-0.002)
df_ceres['sign'] = (df_ceres['vote_sum_pred'] >= vote_num).astype(float) #投票数
df_ceres_sign = df_ceres[df_ceres['sign']==1]
print(len(df_ceres),len(df_ceres_sign),len(df_ceres_sign)/len(df_ceres))

day_df_ceres = pd.DataFrame()
day_df_ceres['ceres_basic_num'] = df_ceres.groupby('dt').size()
day_df_ceres['ceres_basic_pct'] = df_ceres.groupby('dt')['pct'].mean()

day_df_ceres['ceres_sign_num'] = df_ceres_sign.groupby('dt').size()
day_df_ceres['ceres_sign_ratio'] = df_ceres.groupby('dt')['sign'].mean()
day_df_ceres['ceres_sign_pct'] = df_ceres_sign.groupby('dt')['pct'].mean()

day_df_ceres['ceres_sign_buy_amt'] = df_ceres_sign.groupby('dt')['buy_amt'].sum()
day_df_ceres['ceres_sign_profit'] = df_ceres_sign.groupby('dt')['profit'].sum()

day_df_ceres['ceres_sign_buy_amt'] = day_df_ceres['ceres_sign_buy_amt'].replace(np.nan, 0)
day_df_ceres['ceres_sign_profit'] = day_df_ceres['ceres_sign_profit'].replace(np.nan, 0)

for dt in daymin_ceres_basic_hl_pct.index:
    daymin_ceres_basic_hl_pct_series = daymin_ceres_basic_hl_pct.loc[dt]
    if daymin_ceres_basic_hl_pct_series.max() >= basic_schl_pct_thresh/100:
        open_time = daymin_ceres_basic_hl_pct_series[
            daymin_ceres_basic_hl_pct_series >= basic_schl_pct_thresh/100].index.min()
        if open_time >= 931:
            day_df_ceres.loc[dt, 'timing_open_ceres_basic_hl_pct'] = open_time
            if (open_time < 1430) and (daymin_ceres_basic_hl_pct_series[1430] < basic_schl_pct_thresh/100):
                close_time = 1430
                day_df_ceres.loc[dt, 'timing_close_ceres_basic_hl_pct'] = close_time
            else:
                day_df_ceres.loc[dt, 'timing_close_ceres_basic_hl_pct'] = np.nan

dates = day_df_ceres[~day_df_ceres['timing_open_ceres_basic_hl_pct'].isna()].index
for date in dates:
    open_time = int(day_df_ceres.loc[date,'timing_open_ceres_basic_hl_pct'])
    day_df_ceres.loc[date,'ceres_basic_pct_from_open'] = df_ceres[df_ceres.index.get_level_values(0)==date][open_time].mean()
    day_df_ceres.loc[date,'ceres_sign_pct_from_open'] = df_ceres[(df_ceres.index.get_level_values(0)==date)&(df_ceres['sign']==1)][open_time].mean()

day_df_ceres['ceres_sign_buy_amt_mean'] = day_df_ceres['ceres_sign_buy_amt'].expanding(min_periods=1).mean()
day_df_ceres['total_hedging_amt'] = day_df_ceres.apply(lambda x: x['ceres_sign_buy_amt'] if x['ceres_sign_buy_amt'] < x['ceres_sign_buy_amt_mean'] else x['ceres_sign_buy_amt_mean'],axis=1)

for index in index_md.index:
    dt, code = index
    index_md.loc[index, 'label_0931_next_0940'] = index_md.loc[index, 'next_0940'] / index_md.loc[index, 931] - 1
    if not np.isnan(day_df_ceres.loc[dt, 'timing_open_ceres_basic_hl_pct']):
        open_time = int(day_df_ceres.loc[dt, 'timing_open_ceres_basic_hl_pct'])
        index_md.loc[index, 'label_time_close'] = index_md.loc[index, 'close'] / index_md.loc[index, open_time] - 1
        index_md.loc[index, 'label_time_next_0940'] = index_md.loc[index, 'next_0940'] / index_md.loc[
            index, open_time] - 1
        if not np.isnan(day_df_ceres.loc[dt, 'timing_close_ceres_basic_hl_pct']):
            close_time = int(day_df_ceres.loc[dt, 'timing_close_ceres_basic_hl_pct'])
            index_md.loc[index, 'label_intraday'] = index_md.loc[index, close_time] / index_md.loc[
                index, open_time] - 1  # 日内平仓
            index_md.loc[index, 'label_open_time_close_time'] = index_md.loc[index, close_time] / index_md.loc[
                index, open_time] - 1
        else:
            index_md.loc[index, 'label_open_time_close_time'] = index_md.loc[index, 'next_0940'] / index_md.loc[
                index, open_time] - 1
            index_md.loc[index, 'label_intraday'] = np.nan


    else:
        index_md.loc[index, 'label_time_close'] = np.nan
        index_md.loc[index, 'label_intraday'] = np.nan
        index_md.loc[index, 'label_time_next_0940'] = np.nan
        index_md.loc[index, 'label_open_time_close_time'] = np.nan

index_md = index_md.sort_index().loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
index_md_unstack = index_md.unstack()

col_list = ['label_time_close', 'label_close_next_open', 'label_next_open_next_0940', 'label_next_0940_next_twap',
            'label_time_next_0940', \
            'label_0931_next_0940', 'label_open_time_close_time', 'label_intraday']
for index in index_list:
    day_df_ceres['%s' % (index)] = index_md_unstack[('close', index)]
    for col in col_list:
        day_df_ceres['%s_%s' % (index, col)] = index_md_unstack[(col, index)]

    day_df_ceres['%s_equal_profit_time_close' % index] = day_df_ceres['ceres_sign_buy_amt'] * day_df_ceres[
        '%s_label_time_close' % index]
    day_df_ceres['%s_aum_profit_time_close' % index] = day_df_ceres['total_hedging_amt'] * day_df_ceres[
        '%s_label_time_close' % index]

    day_df_ceres['%s_equal_profit_close_next_open' % index] = day_df_ceres['ceres_sign_buy_amt'] * day_df_ceres[
        '%s_label_close_next_open' % index]
    day_df_ceres['%s_aum_profit_close_next_open' % index] = day_df_ceres['total_hedging_amt'] * day_df_ceres[
        '%s_label_close_next_open' % index]

    day_df_ceres['%s_equal_profit_next_open_next_0940' % index] = day_df_ceres['ceres_sign_buy_amt'] * day_df_ceres[
        '%s_label_next_open_next_0940' % index]
    day_df_ceres['%s_aum_profit_next_open_next_0940' % index] = day_df_ceres['total_hedging_amt'] * day_df_ceres[
        '%s_label_next_open_next_0940' % index]

    day_df_ceres['%s_equal_profit_next_0940_next_twap' % index] = day_df_ceres['ceres_sign_buy_amt'] * day_df_ceres[
        '%s_label_next_0940_next_twap' % index]
    day_df_ceres['%s_aum_profit_next_0940_next_twap' % index] = day_df_ceres['total_hedging_amt'] * day_df_ceres[
        '%s_label_next_0940_next_twap' % index]

    day_df_ceres['%s_equal_profit_time_next_0940' % index] = day_df_ceres['ceres_sign_buy_amt'] * day_df_ceres[
        '%s_label_time_next_0940' % index]
    day_df_ceres['%s_aum_profit_time_next_0940' % index] = day_df_ceres['total_hedging_amt'] * day_df_ceres[
        '%s_label_time_next_0940' % index]

    day_df_ceres['%s_equal_profit_open_time_close_time' % index] = day_df_ceres['ceres_sign_buy_amt'] * \
                                                                    day_df_ceres[
                                                                        '%s_label_open_time_close_time' % index]
    day_df_ceres['%s_aum_profit_open_time_close_time' % index] = day_df_ceres['total_hedging_amt'] * day_df_ceres[
        '%s_label_open_time_close_time' % index]

    day_df_ceres['%s_equal_profit_intraday' % index] = day_df_ceres['ceres_sign_buy_amt'] * day_df_ceres[
        '%s_label_intraday' % index]
    day_df_ceres['%s_aum_profit_intraday' % index] = day_df_ceres['total_hedging_amt'] * day_df_ceres[
        '%s_label_intraday' % index]

day_df_ceres = day_df_ceres.sort_index()

#策略(对冲)收益
day_df_ceres['ceres_sign_cumprofit']=day_df_ceres['ceres_sign_profit'].cumsum()

day_df_ceres['all']=1

day_df_ceres['ceres_sign_index_equal_profit_intraday']=day_df_ceres['ceres_sign_profit']-day_df_ceres['000852.SH_equal_profit_intraday'].replace(np.nan,0)
day_df_ceres['ceres_sign_index_equal_cumprofit_intraday']=day_df_ceres['ceres_sign_index_equal_profit_intraday'].cumsum()
day_df_ceres['ceres_sign_index_aum_profit_intraday']=day_df_ceres['ceres_sign_profit']-day_df_ceres['000852.SH_aum_profit_intraday'].replace(np.nan,0)
day_df_ceres['ceres_sign_index_aum_cumprofit_intraday']=day_df_ceres['ceres_sign_index_aum_profit_intraday'].cumsum()

day_df_ceres['ceres_sign_index_equal_profit_time_next_0940']=day_df_ceres['ceres_sign_profit']-day_df_ceres['000852.SH_equal_profit_time_next_0940'].replace(np.nan,0)
day_df_ceres['ceres_sign_index_equal_cumprofit_time_next_0940']=day_df_ceres['ceres_sign_index_equal_profit_time_next_0940'].cumsum()
day_df_ceres['ceres_sign_index_aum_profit_time_next_0940']=day_df_ceres['ceres_sign_profit']-day_df_ceres['000852.SH_aum_profit_time_next_0940'].replace(np.nan,0)
day_df_ceres['ceres_sign_index_aum_cumprofit_time_next_0940']=day_df_ceres['ceres_sign_index_aum_profit_time_next_0940'].cumsum()

day_df_ceres['ceres_sign_index_equal_profit_open_time_close_time']=day_df_ceres['ceres_sign_profit']-day_df_ceres['000852.SH_equal_profit_open_time_close_time'].replace(np.nan,0)
day_df_ceres['ceres_sign_index_equal_cumprofit_open_time_close_time']=day_df_ceres['ceres_sign_index_equal_profit_open_time_close_time'].cumsum()
day_df_ceres['ceres_sign_index_aum_profit_open_time_close_time']=day_df_ceres['ceres_sign_profit']-day_df_ceres['000852.SH_aum_profit_open_time_close_time'].replace(np.nan,0)
day_df_ceres['ceres_sign_index_aum_cumprofit_open_time_close_time']=day_df_ceres['ceres_sign_index_aum_profit_open_time_close_time'].cumsum()

day_df_ceres['ceres_index_equal_profit_time_next_0940'] = -day_df_ceres['000852.SH_equal_profit_time_next_0940'].replace(np.nan,0)
day_df_ceres['ceres_index_equal_cumprofit_time_next_0940'] = day_df_ceres['ceres_index_equal_profit_time_next_0940'].cumsum()
day_df_ceres['ceres_index_aum_profit_time_next_0940'] = -day_df_ceres['000852.SH_aum_profit_time_next_0940'].replace(np.nan,0)
day_df_ceres['ceres_index_aum_cumprofit_time_next_0940'] = day_df_ceres['ceres_index_aum_profit_time_next_0940'].cumsum()

day_df_ceres['ceres_index_equal_profit_intraday'] = -day_df_ceres['000852.SH_equal_profit_intraday'].replace(np.nan,0)
day_df_ceres['ceres_index_equal_cumprofit_intraday'] = day_df_ceres['ceres_index_equal_profit_intraday'].cumsum()
day_df_ceres['ceres_index_aum_profit_intraday'] = -day_df_ceres['000852.SH_aum_profit_intraday'].replace(np.nan,0)
day_df_ceres['ceres_index_aum_cumprofit_intraday'] = day_df_ceres['ceres_index_aum_profit_intraday'].cumsum()

day_df_ceres['ceres_index_equal_profit_open_time_close_time'] = -day_df_ceres['000852.SH_equal_profit_open_time_close_time'].replace(np.nan,0)
day_df_ceres['ceres_index_equal_cumprofit_open_time_close_time'] = day_df_ceres['ceres_index_equal_profit_open_time_close_time'].cumsum()
day_df_ceres['ceres_index_aum_profit_open_time_close_time'] = -day_df_ceres['000852.SH_aum_profit_open_time_close_time'].replace(np.nan,0)
day_df_ceres['ceres_index_aum_cumprofit_open_time_close_time'] = day_df_ceres['ceres_index_aum_profit_open_time_close_time'].cumsum()


def sta_timing(day_df, col):
    day_df1 = day_df[~day_df[col].isna()]
    res = {}
    res['日期个数'] = len(day_df1)
    res['日均规模'] = day_df1['ceres_sign_buy_amt'].mean()
    res['ceres基础样本平均收益率'] = day_df1['ceres_basic_pct'].mean()
    res['ceres信号样本平均收益率'] = day_df1['ceres_sign_pct'].mean()

    res['ceres基础样本0931_time平均收益率'] = day_df1['ceres_basic_pct_from_open'].mean()
    res['ceres信号样本0931_time平均收益率'] = day_df1['ceres_sign_pct_from_open'].mean()
    res['指数time_next_0940平均收益率'] = day_df1['000852.SH_label_time_next_0940'].mean()
    res['指数open_time_close_time平均收益率'] = day_df1['000852.SH_label_open_time_close_time'].mean()

    res['指数time_close平均收益率'] = day_df1['000852.SH_label_time_close'].mean()

    res['指数close_next_open平均收益率'] = day_df1['000852.SH_label_close_next_open'].mean()
    res['指数next_open_next_0940平均收益率'] = day_df1['000852.SH_label_next_open_next_0940'].mean()
    res['指数next_0940_next_twap平均收益率'] = day_df1['000852.SH_label_next_0940_next_twap'].mean()

    res['ceres信号样本收益之和（万元）'] = day_df1['ceres_sign_profit'].sum() / 10000

    res['指数time_next_0940等量规模收益之和（万元）'] = day_df1['000852.SH_equal_profit_time_next_0940'].sum() / 10000

    res['指数open_time_close_time等量规模收益之和（万元）'] = day_df1[
                                                                '000852.SH_equal_profit_open_time_close_time'].sum() / 10000

    res['指数time_close等量规模收益之和（万元）'] = day_df1['000852.SH_equal_profit_time_close'].sum() / 10000
    res['指数close_next_open等量规模收益之和（万元）'] = day_df1['000852.SH_equal_profit_close_next_open'].sum() / 10000
    res['指数next_open_next_0940等量规模收益之和（万元）'] = day_df1[
                                                               '000852.SH_equal_profit_next_open_next_0940'].sum() / 10000
    res['指数next_0940_next_twap等量规模收益之和（万元）'] = day_df1[
                                                               '000852.SH_equal_profit_next_0940_next_twap'].sum() / 10000

    res['指数time_next_0940动态规模收益之和（万元）'] = day_df1['000852.SH_aum_profit_time_next_0940'].sum() / 10000

    res['指数open_time_close_time动态规模收益之和（万元）'] = day_df1[
                                                                '000852.SH_aum_profit_open_time_close_time'].sum() / 10000

    res['指数time_close动态规模收益之和（万元）'] = day_df1['000852.SH_aum_profit_time_close'].sum() / 10000
    res['指数close_next_open动态规模收益之和（万元）'] = day_df1['000852.SH_aum_profit_close_next_open'].sum() / 10000
    res['指数next_open_next_0940动态规模收益之和（万元）'] = day_df1[
                                                               '000852.SH_aum_profit_next_open_next_0940'].sum() / 10000
    res['指数next_0940_next_twap动态规模收益之和（万元）'] = day_df1[
                                                               '000852.SH_aum_profit_next_0940_next_twap'].sum() / 10000

    return pd.Series(res)


timing_df = pd.DataFrame()
timing_df['择时对冲time_next_0940'] = sta_timing(day_df_ceres, 'timing_open_ceres_basic_hl_pct')
timing_df['择时对冲日内平仓'] = sta_timing(day_df_ceres, 'timing_close_ceres_basic_hl_pct')

timing_df = timing_df.T

def sta_profit(profit):
    res={}
    res['收益（万元）']=profit.sum()/10000
    res['最大回撤（万元）']=(profit.cumsum().cummax()-profit.cumsum()).max()/10000
    res['收益风险比']=res['收益（万元）']/res['最大回撤（万元）']
    res['日扣费胜率']=len(profit[profit>0])/len(profit[profit!=0])

    roll_profit=profit.rolling(3,min_periods=1).sum()
    res['收益夏普比'] =roll_profit.mean()/roll_profit.std()*250**0.5
    return pd.Series(res)

netvalue_df=day_df_ceres[['000852.SH','ceres_sign_cumprofit',\
                           'ceres_sign_index_equal_cumprofit_time_next_0940',\
                           'ceres_sign_index_aum_cumprofit_time_next_0940',\
                           'ceres_index_equal_cumprofit_time_next_0940',\
                           'ceres_index_aum_cumprofit_time_next_0940',\
                           'ceres_sign_index_equal_cumprofit_open_time_close_time',\
                           'ceres_sign_index_aum_cumprofit_open_time_close_time',\
                           'ceres_index_equal_cumprofit_open_time_close_time',\
                           'ceres_index_aum_cumprofit_open_time_close_time']]

rename_dic={'ceres_sign_cumprofit':'ceres信号样本',\
            'ceres_sign_index_equal_cumprofit_time_next_0940':'等量规模择时对冲time_next_0940',\
            'ceres_sign_index_equal_cumprofit_open_time_close_time':'等量规模择时对冲open_time_close_time',\
            'ceres_sign_index_aum_cumprofit_time_next_0940':'动态规模择时对冲time_next_0940',\
            'ceres_sign_index_aum_cumprofit_open_time_close_time':'动态规模择时对冲open_time_close_time'}

netvalue_df=netvalue_df.rename(columns=rename_dic)
netvalue_df['ceres信号样本'] = netvalue_df['ceres信号样本'].fillna(method='ffill')

netvalue_df['等量规模择时对冲basic_time_next_0940'] = netvalue_df['等量规模择时对冲time_next_0940'].fillna(method='ffill')
netvalue_df['动态规模择时对冲basic_time_next_0940'] = netvalue_df['动态规模择时对冲time_next_0940'].fillna(method='ffill')

netvalue_df['等量规模择时对冲basic_open_time_close_time'] = netvalue_df['等量规模择时对冲open_time_close_time'].fillna(method='ffill')
netvalue_df['动态规模择时对冲basic_open_time_close_time'] = netvalue_df['动态规模择时对冲open_time_close_time'].fillna(method='ffill')

netvalue_df['等量规模择时对冲basic_time_next_0940指数'] =  netvalue_df['ceres_index_equal_cumprofit_time_next_0940'].fillna(method='ffill')
netvalue_df['动态规模择时对冲basic_time_next_0940指数'] =  netvalue_df['ceres_index_aum_cumprofit_time_next_0940'].fillna(method='ffill')

netvalue_df['等量规模择时对冲basic_open_time_close_time指数'] =  netvalue_df['ceres_index_equal_cumprofit_open_time_close_time'].fillna(method='ffill')
netvalue_df['动态规模择时对冲basic_open_time_close_time指数'] =  netvalue_df['ceres_index_aum_cumprofit_open_time_close_time'].fillna(method='ffill')


netvalue_df['ceres回撤'] = netvalue_df['ceres信号样本'].diff().apply(lambda x:max(-x,0))
netvalue_df['等量规模择时对冲basic_time_next_0940回撤'] = netvalue_df['等量规模择时对冲basic_time_next_0940'].diff().apply(lambda x:max(-x,0))
netvalue_df['动态规模择时对冲basic_time_next_0940回撤'] = netvalue_df['动态规模择时对冲basic_time_next_0940'].diff().apply(lambda x:max(-x,0))

netvalue_df['等量规模择时对冲basic_open_time_close_time回撤'] = netvalue_df['等量规模择时对冲basic_open_time_close_time'].diff().apply(lambda x:max(-x,0))
netvalue_df['动态规模择时对冲basic_open_time_close_time回撤'] = netvalue_df['动态规模择时对冲basic_open_time_close_time'].diff().apply(lambda x:max(-x,0))

day_df_ceres.loc[pd.to_datetime('20201201'):pd.to_datetime('20210531'),'period']=1
day_df_ceres.loc[pd.to_datetime('20210601'):pd.to_datetime('20211130'),'period']=2
day_df_ceres.loc[pd.to_datetime('20211201'):pd.to_datetime('20220531'),'period']=3
day_df_ceres.loc[pd.to_datetime('20220601'):pd.to_datetime('20221130'),'period']=4
day_df_ceres.loc[pd.to_datetime('20221201'):pd.to_datetime('20230531'),'period']=5

#基础统计
des=day_df_ceres.describe()
corr_pearson=day_df_ceres.corr(method='pearson')
corr_spearman=day_df_ceres.corr(method='spearman')

sta_df=pd.DataFrame()
for cumprofit in rename_dic.keys():
    sta_df[rename_dic[cumprofit]]=sta_profit(day_df_ceres[cumprofit.replace('_cumprofit','_profit')])
sta_df=sta_df.T

sta_period=pd.DataFrame()
for cumprofit in rename_dic.keys():
    for period in day_df_ceres['period'].unique():
        sta_period[(rename_dic[cumprofit],period)]=sta_profit(day_df_ceres.loc[day_df_ceres['period']==period,cumprofit.replace('_cumprofit','_profit')])

sta_period=sta_period.T
sta_period.index=pd.MultiIndex.from_tuples(list(sta_period.index))
sta_period1=sta_period.groupby(level=0,sort=False).mean()

excel_writer = pd.ExcelWriter('/data/user/023859/Hedging/ceres/ceres-vote%s-pct%s择时策略样本和指数统计%s_%s.xlsx'%(vote_num,basic_schl_pct_thresh,start_date,end_date))
day_df_ceres.to_excel(excel_writer, sheet_name='day_df_ceres')
des.to_excel(excel_writer, sheet_name='describe')
corr_pearson.to_excel(excel_writer, sheet_name='corr_pearson')
corr_spearman.to_excel(excel_writer, sheet_name='corr_spearman')
netvalue_df.to_excel(excel_writer, sheet_name='netvalue')
timing_df.to_excel(excel_writer, sheet_name='timing')
sta_df.to_excel(excel_writer, sheet_name='sta')
sta_period.to_excel(excel_writer, sheet_name='sta_period')
sta_period1.to_excel(excel_writer, sheet_name='sta_period1')
excel_writer.save()