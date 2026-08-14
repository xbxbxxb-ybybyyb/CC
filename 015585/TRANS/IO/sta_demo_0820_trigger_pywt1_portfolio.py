import IO
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from joblib import Parallel, delayed
'''
1、931判断，最新价 > open 且 最新涨跌幅>-2%，则931买入
2、否则，对价格序列进行小波变换，剔除噪音后，在RSI(6)背离时、MACD背离时买入，取两者的首个时间点
'''
s = FactorData()
from xquant.marketdata import MarketData
import pywt
mdp = MarketData()
def add_time(start, adding):
    start_str = str(start)
    end_int = int(start_str[:~6]) * 3600000 + \
              int(start_str[~6:~4]) * 60000 + \
              int(start_str[~4:~2]) * 1000 + \
              int(start_str[~2:]) + adding
    end_time = int((end_int - np.floor(end_int / 1000) * 1000) + \
                   (np.floor(end_int / 1000) - np.floor(end_int / 60000) * 60) * 1000 + \
                   (np.floor(end_int / 60000) - np.floor(end_int / 3600000) * 60) * 100000 + \
                   (np.floor(end_int / 3600000)) * 10000000)
    if (start < 113000000) & (end_time > 113000000) & (end_time < 130000000):
        end_time = add_time(end_time, 5400000)
    if (start > 130000000) & (end_time < 130000000) & (end_time > 113000000):
        end_time = add_time(end_time, -5400000)
    return max(93000000, end_time)

#参数设置
start_date, end_date = 20170101, 20170630
df=IO.read_data([start_date,end_date],alt='/data/user/015585/01-因子挖掘/20240812-Ceres新增买入时点/file/Basic_closed_hf_finish_20160101_20191231.h5')
df['st_indicator']=pd.read_pickle('/data/group/800463/data/st_indicator.pkl')['st_indicator']
df['st_indicator']=df['st_indicator'].fillna(0)
print('读取样本：',len(df))

#统计情况
sample=df.copy()
error_list = []
# for index in sample.index:
def get_trigger(index):
    print(index)
    try:
        dt,Ticker=index
        date=dt.strftime('%Y%m%d')
        pre_close=sample.loc[index,'pre_close']
        if (Ticker[0] == '3') & (date >= '20200824'):
            ul_price = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
            dl_price = np.floor(pre_close * 100 * 0.8 + 0.5) / 100
        else:
            ul_price = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
            dl_price = np.floor(pre_close * 100 * 0.9 + 0.5) / 100

        #读取数据
        tick_df = mdp.get_data_by_date('Stock', Ticker, date)
        tick_df['MDTime']=tick_df['MDTime'].astype(int)
        tick_df = tick_df[((tick_df['MDTime'] >= 92500000) & (tick_df['MDTime'] <= 113000000))
                               | ((tick_df['MDTime'] >= 130000000) & (tick_df['MDTime'] <= 150000000))]
        tick_df = tick_df[tick_df['LastPx'] > 0] # qyh：新增了时间筛选和无效数据剔除
        zcz = ((Ticker[0:2] == '30') & (date >= '20200824')) | (Ticker[0:2] == '68')
        # transaction_df = mdp.get_data_by_date("Transaction", Ticker, date) # qyh：暂时用不到trade数据
        min_price = tick_df[tick_df['MDTime'] <= 93100000]['LastPx'].min()
        new_price = tick_df[tick_df['MDTime'] <= 93100000]['LastPx'].tail(1).mean() if len(tick_df[tick_df['MDTime'] <= 93100000]) > 0 else np.nan
        open_price = tick_df[tick_df['MDTime'] >= 93000000]['LastPx'].head(1).mean()
        if new_price > open_price and new_price > (pre_close * 0.96) and zcz:
            trigger_time = 93100000
        elif new_price > open_price and new_price > (pre_close * 0.98) and (not zcz):
            trigger_time = 93100000
        else:
            def cumstd(series):
                dx = (series ** 2).cumsum() / np.arange(1,len(series)+1) - (series.cumsum() / np.arange(1,len(series)+1))**2
                dx = dx * np.arange(1,len(series)+1) / np.arange(0,len(series))
                return dx**0.5
            def ema(series, period):
                res = pd.Series(index=series.index)
                for i in range(len(series)):
                    res.iloc[0] = series.iloc[0]
                    if i >= 1:
                        res.iloc[i] = res.iloc[i - 1] * (period - 1) / (period + 1) + series.iloc[i] * 2 / (period + 1)
                return res
            ## 数据准备：计算RSI(6)
            period = 6
            # 去噪
            wavelet = 'db4'
            level = 4
            def get_pywt(noisy_signal):
                coeffs = pywt.wavedec(noisy_signal, wavelet, level=level)
                threshold = np.median(np.abs(coeffs[-1])) / 0.6745
                coeffs = [pywt.threshold(coeff, threshold, mode='soft') for coeff in coeffs]
                denoised_signal = pywt.waverec(coeffs, wavelet)
                return denoised_signal[-1]
            noisy_signal = tick_df['LastPx'].values
            tick_df['LastPx_new'] = [get_pywt(noisy_signal[:i]) for i in range(1, len(noisy_signal) + 1)]
            # RSI背离
            tick_df['MDTime_min'] = tick_df['MDTime'].apply(lambda x : int(str(x)[:-5]))
            tick_df_1min = pd.DataFrame(tick_df.groupby('MDTime_min')['LastPx_new'].nth(-1)) # 每分钟最后一个LastPx
            tick_df_1min['LastPx_1min'] = tick_df_1min['LastPx_new']
            tick_df_1min['diff'] = tick_df_1min['LastPx_new'].diff().fillna(0)
            tick_df_1min['diff_positive'] = tick_df_1min['diff'].rolling(period-1,1).apply(lambda x : x[x > 0].sum())
            tick_df_1min['diff_negative'] = tick_df_1min['diff'].rolling(period-1,1).apply(lambda x : x[x < 0].sum())
            tick_df = pd.merge(tick_df,tick_df_1min[['LastPx_1min','diff','diff_positive','diff_negative']],left_on='MDTime_min',right_on='MDTime_min',how = 'left')
            for col in ['diff','diff_positive','diff_negative']:
                tick_df[col].fillna(method = 'ffill',inplace=True)
            for j in tick_df.index:
                MDTime_min = tick_df.loc[j,'MDTime_min']
                tick_df_before = tick_df[tick_df['MDTime_min'] < MDTime_min]
                if len(tick_df_before) > 0:
                    LastPx_1min = tick_df_before.iloc[-1]['LastPx_1min']
                else:
                    LastPx_1min = tick_df[tick_df['MDTime_min'] == MDTime_min].iloc[0]['LastPx_1min']
                tick_df.loc[j, 'diff_real'] = tick_df.loc[j, 'LastPx_new'] - LastPx_1min
                if tick_df.loc[j, 'diff_real'] > 0:
                    tick_df.loc[j, 'rsi_real'] = (tick_df.loc[j, 'diff_real'] + tick_df.loc[j, 'diff_positive']) / \
                                                 (tick_df.loc[j, 'diff_real'] + tick_df.loc[j, 'diff_positive'] - tick_df.loc[j, 'diff_negative'])
                else:
                    tick_df.loc[j, 'rsi_real'] = (tick_df.loc[j, 'diff_positive']) / \
                                                 (tick_df.loc[j, 'diff_positive'] - tick_df.loc[j, 'diff_negative'] - tick_df.loc[j, 'diff_real'])
            tick_df['rsi_real_std'] = cumstd(tick_df['rsi_real'])
            tick_df['new_min1'] = (tick_df['LastPx_new'] <= tick_df['LastPx_new'].cummin())
            tick_df['new_min2'] = (tick_df['LastPx_new'] <= tick_df['LastPx_new'].shift(20) * 0.999)
            tick_df['rsi_real_min'] = tick_df['rsi_real'].cummin()
            tick_df['rsi_real_depart'] = (tick_df['rsi_real'] > ( tick_df['rsi_real_min'] + tick_df['rsi_real_std'] * 0.25))
            tick_df['trigger1'] = (tick_df['new_min1']) & (tick_df['new_min2']) & (tick_df['rsi_real_depart'])
            if zcz:
                trigger_time1 = tick_df[(tick_df['trigger1']==True) & (tick_df['MDTime'] >= 93200000) & (tick_df['LastPx_new'] >= pre_close*0.94)]['MDTime'].min()
            else:
                trigger_time1 = tick_df[(tick_df['trigger1'] == True) & (tick_df['MDTime'] >= 93200000) & (
                            tick_df['LastPx_new'] >= pre_close * 0.97)]['MDTime'].min()
            # MACD背离
            tick_df['ema12_real'] = np.nan
            tick_df['ema26_real'] = np.nan
            tick_df['diff_real'] = np.nan
            tick_df['dea_real'] = np.nan
            tick_df['macd_real'] = np.nan
            tick_df['MDTime_min'] = tick_df['MDTime'].apply(lambda x: int(str(x)[:-5]))
            tick_df_1min = pd.DataFrame(tick_df.groupby('MDTime_min')['LastPx_new'].nth(-1))  # 每分钟最后一个LastPx
            tick_df_1min['ema12'] = ema(tick_df_1min['LastPx_new'], 12)
            tick_df_1min['ema26'] = ema(tick_df_1min['LastPx_new'], 26)
            tick_df_1min['diff'] = tick_df_1min['ema12'] - tick_df_1min['ema26']
            tick_df_1min['dea'] = ema(tick_df_1min['diff'], 9)
            tick_df = pd.merge(tick_df, tick_df_1min[['ema12', 'ema26', 'diff', 'dea']], left_on='MDTime_min',
                               right_on='MDTime_min', how='left')
            tick_df['ema12'].fillna(method='ffill', inplace=True)
            tick_df['ema26'].fillna(method='ffill', inplace=True)
            for j in tick_df.index:
                MDTime_min = tick_df.loc[j, 'MDTime_min']
                tick_df_before = tick_df[tick_df['MDTime_min'] < MDTime_min]
                if len(tick_df_before) > 0:
                    ema12 = tick_df_before.iloc[-1]['ema12']
                    ema26 = tick_df_before.iloc[-1]['ema26']
                else:
                    ema12 = tick_df[tick_df['MDTime_min'] == MDTime_min].iloc[0]['ema12']
                    ema26 = tick_df[tick_df['MDTime_min'] == MDTime_min].iloc[0]['ema26']
                tick_df.loc[j, 'ema12_real'] = ema12 * 11 / 13 + tick_df.loc[j, 'LastPx_new'] * 2 / 13
                tick_df.loc[j, 'ema26_real'] = ema26 * 25 / 27 + tick_df.loc[j, 'LastPx_new'] * 2 / 27
            tick_df['diff_real'] = tick_df['ema12_real'] - tick_df['ema26_real']
            for j in tick_df.index:
                MDTime_min = tick_df.loc[j, 'MDTime_min']
                tick_df_before = tick_df[tick_df['MDTime_min'] < MDTime_min]
                if len(tick_df_before) > 0:
                    dea = tick_df_before.iloc[-1]['dea']
                else:
                    dea = tick_df[tick_df['MDTime_min'] == MDTime_min].iloc[0]['dea']
                tick_df.loc[j, 'dea_real'] = dea * 8 / 10 + tick_df.loc[j, 'diff_real'] * 2 / 10
            tick_df['macd_real'] = 2 * (tick_df['diff_real'] - tick_df['dea_real'])
            tick_df['macd_real_std'] = cumstd(tick_df['macd_real'])
            tick_df['diff_real_std'] = cumstd(tick_df['diff_real'])
            tick_df['new_min1'] = (tick_df['LastPx_new'] <= tick_df['LastPx_new'].cummin())
            tick_df['new_min2'] = (tick_df['LastPx_new'] <= tick_df['LastPx_new'].shift(20) * 0.999)
            tick_df['macd_real_min'] = tick_df['macd_real'].cummin()
            tick_df['macd_real_depart'] = (
                        tick_df['macd_real'] > (tick_df['macd_real_min'] + tick_df['macd_real_std'] * 0.25))
            tick_df['trigger1'] = (tick_df['new_min1']) & (tick_df['new_min2']) & (tick_df['macd_real_depart'])
            if zcz:
                trigger_time2 = tick_df[(tick_df['trigger1'] == True) & (tick_df['MDTime'] >= 93200000) &
                                       (tick_df['LastPx_new'] >= pre_close * 0.94)]['MDTime'].min()
            else:
                trigger_time2 = tick_df[(tick_df['trigger1'] == True) & (tick_df['MDTime'] >= 93200000) &
                                       (tick_df['LastPx_new'] >= pre_close * 0.97)]['MDTime'].min()
            # 取RSI和MACD的首次背离时间作为触发时间，考虑空值情形
            trigger_time1 = 150000000 if not trigger_time1 > 0 else trigger_time1
            trigger_time2 = 150000000 if not trigger_time2 > 0 else trigger_time2
            trigger_time = min(trigger_time1, trigger_time2)
            trigger_time = np.nan if trigger_time == 150000000 else trigger_time
        #计算未来十分钟twap
        if not np.isnan(trigger_time):
            buy_end_time=min(150000000, add_time(trigger_time, 10 * 60 * 1000))
            tick_buy = tick_df[tick_df['MDTime'] > trigger_time]
            tick_buy = tick_buy[tick_buy['MDTime'] < buy_end_time]
            tick_buy = tick_buy[tick_buy['LastPx'].cummax() < ul_price]
            tick_buy = tick_buy[tick_buy['LastPx'].cummin() > dl_price]
            if len(tick_buy) > 0:
                T_trigger_10_twap_before_ZT = tick_buy['LastPx'].mean()
            else:
                T_trigger_10_twap_before_ZT = np.nan
        else:
            T_trigger_10_twap_before_ZT = np.nan

        # 计算未来十分钟twap
        s1_buy_begin_time=93100000
        buy_end_time = min(150000000, add_time(s1_buy_begin_time, 10 * 60 * 1000))
        tick_buy = tick_df[tick_df['MDTime'] > s1_buy_begin_time]
        tick_buy = tick_buy[tick_buy['MDTime'] < buy_end_time]
        tick_buy = tick_buy[tick_buy['LastPx'].cummax() < ul_price]
        tick_buy = tick_buy[tick_buy['LastPx'].cummin() > dl_price]
        if len(tick_buy) > 0:
            T_s1_10_twap_before_ZT = tick_buy['LastPx'].mean()
        else:
            T_s1_10_twap_before_ZT = np.nan
        res = pd.DataFrame({'trigger_time':[trigger_time],
                            'T_trigger_10_twap_before_ZT' : [T_trigger_10_twap_before_ZT],
                            'T_s1_10_twap_before_ZT':[T_s1_10_twap_before_ZT],
                            'dt':[index[0]],'Ticker':[index[1]]})
        return res
    except:
        error_list.append(index)
        return
factor_df_list = Parallel(n_jobs=30)(delayed(get_trigger)(index) for index in sample.index)
factor_df_list = pd.concat(factor_df_list,axis=0).set_index(['dt','Ticker'])
sample = pd.merge(sample,factor_df_list,left_index=True,right_index=True,how='left')

MD_data = IO.read_data([start_date, s.tradingday(str(end_date), 30)[~0]],
                       columns=['high','low','vwap','adjfactor']
                       , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
is_yzb = MD_data['low'] == MD_data['high']
MD_data.loc[is_yzb,'vwap']=np.nan
MD_data.loc[is_yzb,'adjfactor']=np.nan
sample['adjfactor']=MD_data['adjfactor']
sample['next_vwap']=MD_data['vwap'].unstack().fillna(method='bfill').shift(-1).stack()
sample['next_adjfactor']=MD_data['adjfactor'].unstack().fillna(method='bfill').shift(-1).stack()
sample['label_v2t10']=sample['next_vwap']*sample['next_adjfactor']/sample['T_trigger_10_twap_before_ZT']/sample['adjfactor']-1
sample['label_v2o10d1']=sample['next_vwap']*sample['next_adjfactor']/sample['T_s1_10_twap_before_ZT']/sample['adjfactor']-1

#样本筛选
st_filter = sample['st_indicator'] != 1
open_filter = (sample['T_open_is_zt'] == False) & (sample['T_open_is_dt'] == False)
after_not_ul_len_filter = sample['after_not_ul_len'] > 10
can_buy_filter = sample['T_first_trans_ZT'] != 1
base_filter = st_filter & open_filter & after_not_ul_len_filter & can_buy_filter

sample_filter931 = sample[base_filter&((sample['T_day_first_ZT_Time'] <=93100000) == False)&((sample['T_day_first_DT_Time'] <=93100000) == False)&(~sample['label_v2o10d1'].isna())]
sample_filter_t = sample[base_filter&((sample['T_day_first_ZT_Time'] <=sample['trigger_time']) == False)&((sample['T_day_first_DT_Time'] <=sample['trigger_time']) == False)&(~sample['label_v2t10'].isna())]
print('筛选样本：',len(sample_filter931),len(sample_filter_t))
print('基准label:', sample_filter931['label_v2o10d1'].mean())
print('新时点label:', sample_filter_t['label_v2t10'].mean())
# sample.to_pickle('/data/user/015585/01-因子挖掘/20240812-Ceres新增买入时点/file/test_trigger5_3_1_2.pkl')
#指标：T日收盘涨停率、T+1日收盘涨停率、T日和T+1日收盘涨停率、label均值、中位数、标准差、胜率
#样本：ceres的931（基准）、新触发时点
#时间区间：全部和分年度