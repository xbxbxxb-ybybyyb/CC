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
# 参数设置
start_date, end_date = 20170101, 20181231
df_name = '_p4_portfolio6'
# 拼接df
df_rehigh_build = pd.DataFrame()
for i in range(2,4):
    df_i = pd.read_pickle(f'/data/user/015585/01-因子挖掘/20240812-Ceres新增买入时点/file_p4/test_trigger_p4_portfolio7_{i}.pkl')
    df_rehigh_build = df_rehigh_build.append(df_i)
df_rehigh_build.to_pickle(f'/data/user/015585/01-因子挖掘/20240812-Ceres新增买入时点/file_p4/test_trigger{df_name}.pkl')
# 测试
for name in [df_name]:
    print(name)
    # 读取样本集
    df_s1=pd.read_pickle('/data/user/018107/share_file/for_qyh/sft_init_normal931_p4_20160101_20191231.pkl').loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
    df_rehigh=pd.read_pickle('/data/user/015585/01-因子挖掘/20240812-Ceres新增买入时点/file_p4/test_trigger{}.pkl'.format(name)).loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
    # 涨停情况
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
        # open_filter = (sample['T_open_is_zt'] == False) & (sample['T_open_is_dt'] == False)
        after_not_ul_len_filter = sample['after_not_ul_len'] > 10
        # can_buy_filter = sample['T_first_trans_ZT'] != 1
        # base_filter = st_filter & open_filter & after_not_ul_len_filter & can_buy_filter
        base_filter = st_filter  & after_not_ul_len_filter
        zt_dt_filter1 = (sample['label_T_first_dl_time'].fillna(150000000) > 93100000) & (
                    sample['label_T_first_ul_time'].fillna(150000000) > 93100000)
        sample_filter931 = sample[base_filter & zt_dt_filter1 & (~sample['label_TN_v2o10d1'].isna())].copy()
        sample_filter931['label']=sample_filter931['label_TN_v2o10d1']
        sample_filter931['label_T_is_zt']=md['label_T_is_zt']
        sample_filter931['label_T1_is_zt'] = md['label_T1_is_zt']
        # sample_filter931['pct_s1'] = pct_s1['pct']
        # sample_filter931['pct_diff'] = sample_filter931['pct'] - sample_filter931['pct_s1']
        return sample_filter931
    sample_s1=filer_s1(df_s1)

    def filter_trigger(sample):
        sample['st_indicator']=pd.read_pickle('/data/group/800463/data/st_indicator.pkl')['st_indicator']
        sample['st_indicator']=sample['st_indicator'].fillna(0)
        st_filter = sample['st_indicator'] != 1
        # open_filter = (sample['T_open_is_zt'] == False) & (sample['T_open_is_dt'] == False)
        after_not_ul_len_filter = sample['after_not_ul_len'] > 10
        # can_buy_filter = sample['T_first_trans_ZT'] != 1
        # base_filter = st_filter & open_filter & after_not_ul_len_filter & can_buy_filter
        base_filter = st_filter & after_not_ul_len_filter
        zt_dt_filter2 = (sample['label_T_first_dl_time'].fillna(150000000) > sample['trigger_time']) & (
                    sample['label_T_first_ul_time'].fillna(150000000) > sample['trigger_time'])
        sample_filter_t = sample[base_filter & zt_dt_filter2 & (~sample['label_v2t10'].isna())].copy()
        sample_filter_t['label'] = sample_filter_t['label_v2t10']
        sample_filter_t['label_T_is_zt'] = md['label_T_is_zt']
        sample_filter_t['label_T1_is_zt'] = md['label_T1_is_zt']
        sample_filter_t['pct_time_ms'] = sample_filter_t['trigger_time'].apply(lambda x: int(cal_time_delta(93000000, x)))
        # sample_filter_t['pct_s1'] = pct_s1['pct']
        # sample_filter_t['pct_diff'] = sample_filter_t['pct'] - sample_filter_t['pct_s1']
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
        res_dic['重叠部分label_delta均值'] = (df1['label'] - df1['label_TN_v2o10d1']).mean()
        # res_dic['pct均值'] = df1['pct'].mean()
        # res_dic['pct中位数'] = df1['pct'].median()
        # res_dic['pct标准差'] = df1['pct'].std()
        # res_dic['pct胜率'] = len(df1[df1['pct']>0])/len(df1) if len(df1)>0 else np.nan
        # res_dic['pct>0均值'] = df1.loc[df1['pct'] > 0, 'pct'].mean()
        # res_dic['pct<0均值'] = df1.loc[df1['pct'] < 0, 'pct'].mean()
        # res_dic['pct盈亏比'] = -res_dic['pct>0均值']/res_dic['pct<0均值']
        # res_dic['pct差异均值']=df1['pct_diff'].mean()
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
    sta_df=get_sta(sta_df,sample_rehigh,'qyh{}'.format(name))

    sta_df=sta_df.T
    # sta_df.to_excel('/data/user/015585/01-因子挖掘/20240812-Ceres新增买入时点/file_p4/qyh{}.xlsx'.format(name))
'''
1、931选出来的，要比所有的931的均值高
2、931以后选出来的，要比剔除931选出来的部分的931均值高
'''
#
print('931选出来的，要比所有的931的均值高')
print('所有的931均值：')
print(df_rehigh['label_TN_v2o10d1'].mean())
print('选出来在931买入的均值：')
print(df_rehigh[(df_rehigh['trigger_time'] == 93100000)]['label_TN_v2o10d1'].mean())

print('931以后触发的，要比剔除931选出来的部分的931均值高')
print('剔除931选出来的，剩余所有样本的931均值：')
print(df_rehigh[~(df_rehigh['trigger_time'] == 93100000)]['label_TN_v2o10d1'].mean())
print('931以后选出来的新时点均值：')
print(df_rehigh[(df_rehigh['trigger_time'] > 93100000)]['label_v2t10'].mean())
print('进一步分析，931以后新条件触发的样本，它们的label_TN_v2o10d1：')
print(df_rehigh[(df_rehigh['trigger_time'] > 93100000)]['label_TN_v2o10d1'].mean())





