import IO
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
s = FactorData()
def cal_time_delta(start, end):
    start_str = str(int(start))
    end_str = str(int(end))
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    if (start < 120000000) & (end > 120000000):
        time_delta = time_delta - 5400000
    return time_delta


#参数设置
start_date, end_date = 20160101, 20211231

#读取样本集
df_s1=pd.read_pickle('/data/user/018107/sta/20240826_sample_basic.pkl').loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
df_rehigh=pd.read_pickle('/data/user/018107/sta/20240826_sample_rehigh.pkl').loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]


#读取模拟收益率
pct_s1=pd.read_hdf('/data/group/800463/project/project3_prod/profit_backtest/sp2_profit_interval_931_1000_0.10_0.10_500_1500_250_20.h5')
df_s1['pct']=pct_s1['pct']
df_rehigh['pct']=pd.read_hdf('/data/group/800463/project/project3_prod/profit_backtest_newtime/sp2_profit_rehigh_0.10_0.10_500_1500_250_20.h5')['pct']

#涨停情况
md = IO.read_data([start_date, s.tradingday(end_date,100)[-1]],columns=['pre_close','open','low','high','close','amt','vwap','adjfactor']
                       , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md=md[md['amt'] > 0]
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))
              & (md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['zt_price']= np.floor(md['pre_close'] * 100 * 1.1 + 0.5+1e-8) / 100
md['zt_price'][md['zcz']]= np.floor(md['pre_close'] * 100 * 1.2 + 0.5+1e-8) / 100
md['label_T_is_zt']=md['close']==md['zt_price']
md=md.sort_index(level=['Ticker','dt'])
md['label_T1_is_zt']=md.groupby('Ticker')['label_T_is_zt'].shift(-1)

def filer_s1(sample):
    sample['st_indicator']=pd.read_pickle('/data/group/800463/data/st_indicator.pkl')['st_indicator']
    sample['st_indicator']=sample['st_indicator'].fillna(0)
    st_filter = sample['st_indicator'] != 1
    open_filter = (sample['T_open_is_zt'] == False) & (sample['T_open_is_dt'] == False)
    after_not_ul_len_filter = sample['after_not_ul_len'] > 10
    can_buy_filter = sample['T_first_trans_ZT'] != 1
    base_filter = st_filter & open_filter & after_not_ul_len_filter & can_buy_filter
    sample_filter931 = sample[base_filter&((sample['T_day_first_ZT_Time'] <=93100000) == False)&((sample['T_day_first_DT_Time'] <=93100000) == False)&(~sample['label_v2o10d1'].isna())].copy()
    sample_filter931['label']=sample_filter931['label_v2o10d1']
    sample_filter931['label_T_is_zt']=md['label_T_is_zt']
    sample_filter931['label_T1_is_zt'] = md['label_T1_is_zt']
    sample_filter931['pct_s1'] = pct_s1['pct']
    sample_filter931['pct_diff'] = sample_filter931['pct'] - sample_filter931['pct_s1']
    return sample_filter931
sample_s1=filer_s1(df_s1)

def filter_trigger(sample):
    sample['st_indicator']=pd.read_pickle('/data/group/800463/data/st_indicator.pkl')['st_indicator']
    sample['st_indicator']=sample['st_indicator'].fillna(0)
    st_filter = sample['st_indicator'] != 1
    open_filter = (sample['T_open_is_zt'] == False) & (sample['T_open_is_dt'] == False)
    after_not_ul_len_filter = sample['after_not_ul_len'] > 10
    can_buy_filter = sample['T_first_trans_ZT'] != 1
    base_filter = st_filter & open_filter & after_not_ul_len_filter & can_buy_filter
    sample_filter_t = sample[base_filter & ((sample['T_day_first_ZT_Time'] <= sample['trigger_time']) == False) & ((sample['T_day_first_DT_Time'] <= sample['trigger_time']) == False) & (~sample['label_v2t10'].isna())].copy()
    sample_filter_t['label'] = sample_filter_t['label_v2t10']
    sample_filter_t['label_T_is_zt'] = md['label_T_is_zt']
    sample_filter_t['label_T1_is_zt'] = md['label_T1_is_zt']
    sample_filter_t['pct_time_ms'] = sample_filter_t['trigger_time'].apply(lambda x: int(cal_time_delta(93000000, x)))
    sample_filter_t['pct_s1'] = pct_s1['pct']
    sample_filter_t['pct_diff'] = sample_filter_t['pct'] - sample_filter_t['pct_s1']
    return sample_filter_t
sample_rehigh=filter_trigger(df_rehigh)

def sta(df1):
    res_dic = {'数量': len(df1)}
    res_dic['T日封板率']=df1['label_T_is_zt'].mean()
    res_dic['T+1日封板率'] = df1['label_T1_is_zt'].mean()
    res_dic['T日&T+1日封板率'] = ((df1['label_T_is_zt']==1)&(df1['label_T1_is_zt']==1)).mean()
    res_dic['label均值'] = df1['label'].mean()
    res_dic['label中位数'] = df1['label'].median()
    res_dic['label标准差'] = df1['label'].std()
    res_dic['label胜率'] = len(df1[df1['label']>0])/len(df1) if len(df1)>0 else np.nan
    res_dic['label>0均值'] = df1.loc[df1['label'] > 0, 'label'].mean()
    res_dic['label<0均值'] = df1.loc[df1['label'] < 0, 'label'].mean()
    res_dic['label盈亏比'] = -res_dic['label>0均值']/res_dic['label<0均值']
    res_dic['pct均值'] = df1['pct'].mean()
    res_dic['pct中位数'] = df1['pct'].median()
    res_dic['pct标准差'] = df1['pct'].std()
    res_dic['pct胜率'] = len(df1[df1['pct']>0])/len(df1) if len(df1)>0 else np.nan
    res_dic['pct>0均值'] = df1.loc[df1['pct'] > 0, 'pct'].mean()
    res_dic['pct<0均值'] = df1.loc[df1['pct'] < 0, 'pct'].mean()
    res_dic['pct盈亏比'] = -res_dic['pct>0均值']/res_dic['pct<0均值']
    res_dic['pct差异均值']=df1['pct_diff'].mean()
    return pd.Series(res_dic)

def get_sta(sta_df,df,name):
    sta_df[name]=sta(df)
    sta_df['%s  930-935' % name] = sta(df[df['pct_time_ms'] < 5 * 60 * 1000])
    sta_df['%s  935-940'%name]=sta(df[(df['pct_time_ms']>=5*60*1000)&(df['pct_time_ms']<10*60*1000)])
    sta_df['%s  940-945'%name]=sta(df[(df['pct_time_ms']>=10*60*1000)&(df['pct_time_ms']<15*60*1000)])
    sta_df['%s  945-950'%name]=sta(df[(df['pct_time_ms']>=15*60*1000)&(df['pct_time_ms']<20*60*1000)])
    sta_df['%s  950-955'%name]=sta(df[(df['pct_time_ms']>=20*60*1000)&(df['pct_time_ms']<25*60*1000)])
    sta_df['%s  955-1000'%name]=sta(df[(df['pct_time_ms']>=25*60*1000)&(df['pct_time_ms']<30*60*1000)])
    sta_df['%s  1000-1030'%name]=sta(df[(df['pct_time_ms']>=0.5*60*60*1000)&(df['pct_time_ms']<1*60*60*1000)])
    sta_df['%s  1030-1100'%name]=sta(df[(df['pct_time_ms']>=1*60*60*1000)&(df['pct_time_ms']<1.5*60*60*1000)])
    sta_df['%s  1100-1130'%name]=sta(df[(df['pct_time_ms']>=1.5*60*60*1000)&(df['pct_time_ms']<2*60*60*1000)])
    sta_df['%s  1300-1330'%name]=sta(df[(df['pct_time_ms']>=2*60*60*1000)&(df['pct_time_ms']<2.5*60*60*1000)])
    sta_df['%s  1330-1400'%name]=sta(df[(df['pct_time_ms']>=2.5*60*60*1000)&(df['pct_time_ms']<3*60*60*1000)])
    sta_df['%s  1400-1430'%name]=sta(df[(df['pct_time_ms']>=3*60*60*1000)&(df['pct_time_ms']<=3.5*60*60*1000)])
    sta_df['%s  1430-1500'%name]=sta(df[(df['pct_time_ms']>3.5*60*60*1000)])
    return sta_df

sta_df = pd.DataFrame()
sta_df['s1']=sta(sample_s1)
sta_df=get_sta(sta_df,sample_rehigh,'rehigh')

sta_df=sta_df.T
sta_df.to_excel('/data/user/018107/sta/20240902_Ceres新触发时点统计_20160101_20211231.xlsx')







