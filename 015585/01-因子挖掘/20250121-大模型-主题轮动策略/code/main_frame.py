import pandas as pd
import IO
from xquant.factordata import FactorData
from joblib import Parallel, delayed
import numpy as np
import bisect
'''
1、通用的测试框架
2、框架中设置”触发条件“，计算每个标的（行业指数）的买入时机、价格，再根据次日均价计算label，形成basic文件
--条件想法1
    931以后
    行业指数过去1分钟的涨幅达到0.25%
    行业指数过去1分钟的涨幅排名达到前5（共计31个行业）
    行业指数涨幅 > 0
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
start_date, end_date = 20180101, 20181231

df = pd.read_pickle('/data/user/015585/01-因子挖掘/20250121-大模型-主题轮动策略/file/basic_file_sw_20160101_20241231.pkl').sort_index()
df = df.loc[pd.Timestamp(str(start_date)) : pd.Timestamp(str(end_date))]
print('读取样本：',len(df))

#统计情况
sample=df.copy()
error_list = []

def get_trigger(index):
    print(index)
    try:
        dt,Ticker=index
        date=dt.strftime('%Y%m%d')
        pre_close = sample.loc[index,'pre_close']
        #读取数据
        tick_df = pd.read_pickle(f'/dfs/user/015585/04_行业指数数据/申万2021/{date}.pkl')
        tick_df['MDTime']=tick_df['MDTime'].astype(int)
        tick_df = tick_df[((tick_df['MDTime'] >= 92500000) & (tick_df['MDTime'] <= 113000000))
                               | ((tick_df['MDTime'] >= 130000000) & (tick_df['MDTime'] <= 150000000))]
        tick_df = tick_df[tick_df['LastPx'] > 0] # qyh：新增了时间筛选和无效数据剔除
        zcz = ((Ticker[0:2] == '30') & (date >= '20200824')) | (Ticker[0:2] == '68')
        # 计算trigger_time
        trigger_time = np.nan
        tick_df_indu = tick_df.query(f'Ticker == "{Ticker}"').copy()
        para_pct_1min = 0.0025
        para_rank = 5

        tick_df_indu['pct_1min'] = (tick_df_indu['LastPx'] - tick_df_indu['LastPx'].shift(20)) / tick_df_indu['LastPx']
        def calc_pct_1min(df):
            res = (df['LastPx'] - df['LastPx'].shift(20)) / df['LastPx']
            return res.tail(1).values[0] if not res.empty else np.nan
        def get_rank(num, lst):
            notnan_lst = [i for i in lst if (i is not np.nan) and (i is not None)]
            sorted_lst = sorted(notnan_lst,  reverse = True)
            position = 1
            for value in sorted_lst:
                if num < value:
                    position += 1
                else:
                    break
            return position
        pct_1min_rank = []
        for mdtime in tick_df_indu['MDTime']:
            tick_df_time_filter = tick_df[tick_df['MDTime'] <= mdtime].copy()
            last_pct_1min = tick_df_time_filter.groupby('Ticker').apply(calc_pct_1min)
            pct_1min_rank.append(get_rank(last_pct_1min[Ticker], list(last_pct_1min)))
        tick_df_indu['pct_1min_rank'] = pct_1min_rank # 注意排名越小代表涨幅越大
        filter1 = tick_df_indu['pct_1min'] >= para_pct_1min
        filter2 = tick_df_indu['pct_1min_rank'] <= para_rank
        trigger_time = tick_df_indu[filter1 & filter2]['MDTime'].min()

        #计算未来十分钟twap
        if not np.isnan(trigger_time):
            buy_end_time=min(150000000, add_time(trigger_time, 10 * 60 * 1000))
            tick_buy = tick_df_indu[tick_df_indu['MDTime'] > trigger_time]
            tick_buy = tick_buy[tick_buy['MDTime'] < buy_end_time]
            if len(tick_buy) > 0:
                T_trigger_10_twap_before_ZT = tick_buy['LastPx'].mean()
            else:
                T_trigger_10_twap_before_ZT = np.nan
        else:
            T_trigger_10_twap_before_ZT = np.nan

        res = pd.DataFrame({'trigger_time':[trigger_time],
                            'T_trigger_10_twap_before_ZT' : [T_trigger_10_twap_before_ZT],
                            'dt':[index[0]],'Ticker':[index[1]]})
        return res
    except:
        error_list.append(index)
        return
factor_df_list = Parallel(n_jobs=28)(delayed(get_trigger)(index) for index in sample.index)
factor_df_list = pd.concat(factor_df_list,axis=0).set_index(['dt','Ticker'])
sample = pd.merge(sample,factor_df_list,left_index=True,right_index=True,how='left')

MD_data = pd.read_pickle('/data/user/015585/01-因子挖掘/20250121-大模型-主题轮动策略/file/basic_file_sw_20160101_20241231.pkl').sort_index()

sample['next_vwap']=MD_data['vwap'].unstack().fillna(method='bfill').shift(-1).stack()
sample['label_v2t10']=sample['next_vwap']/sample['T_trigger_10_twap_before_ZT']-1



sample_filter_t = sample[(~sample['label_v2t10'].isna())]
print('筛选样本：',len(sample),len(sample_filter_t))
print('label:', sample_filter_t['label_v2t10'].mean())
sample.to_pickle('/data/user/015585/01-因子挖掘/20250121-大模型-主题轮动策略/file/test_trigger_solution_1.pkl')
#指标：T日收盘涨停率、T+1日收盘涨停率、T日和T+1日收盘涨停率、label均值、中位数、标准差、胜率
#样本：ceres的931（基准）、新触发时点
#时间区间：全部和分年度



# 20180102 801180