# @Time : 2021/12/6 17:50
# @Author : Zhichen Lu
# @File : SignalAnlysis.py
import pandas as pd
import numpy as np
from dataApi.getData import get_minute_1factor
from dataApi.tradeDate import get_pre_trade_date,get_recent_trade_date
from dataApi.sendInfo import send_file

bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
close = get_minute_1factor('close',start_datetime=20210104,end_datetime=20211206)
close = close.swaplevel(0, 1).loc[bar_list].swaplevel(0, 1)


# file_list = list(filter(lambda x: x.startswith('XGB') and 'Out' not in x, os.listdir(base_path)))
def get_stat(file_name):
    data = pd.read_excel(f'{base_path}{file_name}',sheet_name=None)
    signal_info = data['逐笔持仓统计']
    future_ret = close[sorted(list(set(signal_info['stk_id'])))].pct_change(7).shift(-7).stack()
    signal_info['date'],signal_info['time'] = signal_info['start']//10000,signal_info['start']%10000
    signal_future_ret = future_ret.loc[signal_info.set_index(['date','time','stk_id']).index]
    signal_future_ret = pd.DataFrame({
        '收益率':signal_future_ret,'month':signal_future_ret.index.map(lambda x : x[0]//100),
        '胜率':(signal_future_ret>0.0012)*1.
    })

    daily_info = data['每日持仓统计'].set_index('date')
    daily_info.index = pd.to_datetime(daily_info.index.astype(str))
    daily_info['仓位'] =daily_info['收盘持仓市值']/daily_info['收盘账户市值']
    daily_m_stat = pd.DataFrame({
    '仓位':daily_info['仓位'].resample('1m').mean(),
    '净值收益率':daily_info['账户净值'].resample('1m').last() - daily_info['账户净值'].resample('1m').first(),
    '占资收益率':(daily_info['收盘账户市值'].resample('1m').last() - daily_info['收盘账户市值'].resample('1m').first())/daily_info['收盘持仓市值'].mean()

    })
    daily_m_stat.index = daily_m_stat.index.map(lambda x : int(x.strftime('%Y%m')))
    whole_year = pd.DataFrame({
    '仓位':daily_info['仓位'].resample('1Y').mean(),
    '净值收益率':daily_info['账户净值'].resample('1Y').last() - daily_info['账户净值'].resample('1Y').first(),
    '占资收益率':(daily_info['收盘账户市值'].resample('1Y').last() - daily_info['收盘账户市值'].resample('1Y').first())/daily_info['收盘持仓市值'].mean()
    })
    whole_year.index = ['全时段']
    daily_m_stat = daily_m_stat.append(whole_year)


    monthly_stat = signal_future_ret.groupby('month').mean()
    monthly_stat.loc['全时段'] = signal_future_ret.drop('month',axis=1).mean()
    monthly_stat = pd.concat([monthly_stat,daily_m_stat],axis=1)


    daily_stat = signal_future_ret.groupby(level=0).mean().drop('month',axis=1)
    return monthly_stat,daily_stat

base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/Upgrade2021/'
file_list = {
    '12月迭代前版本':'XGBMonthlyV4_Cat_Light_ValWithoutMax5start20210104_end20211130CS_XGB_OLS_condition_style_rank_ex20Top600_real600_deal_ratio_0.1_per_ratio_0.0050_threshold_0.05_inital_200000000start20210104_end20211130VolConsider_UpBuy100_10bp_cost.xlsx',
    '最新研究成果(暂未上实盘)':'XGBWithSWSHIFReSaveTWithOrigin_Cat_LightWithoutMax5_PredCosiV3_deal0.10_per5.0bp_thre5_cash2e+08_Top600_start20210104_end20211130_s_thre0.10_d_thre0.70_swing0.005VolConsider_UpBuy100_10bp_cost.xlsx',
     '当前线上更新后版本':'XGBWithSWSHIFReSaveTWithOrigin_Cat_LightWithoutMax5start20210104_end20211130CS_XGB_OLS_condition_style_rank_ex20Top600_real600_deal_ratio_0.1_per_ratio_0.0050_threshold_0.05_inital_200000000start20210104_end20211130VolConsider_UpBuy100_10bp_cost.xlsx'
}

d_stat,m_stat = [],[]
for key in file_list:
    f_name = file_list[key]
    temp_m,temp_d  = get_stat(f_name)
    temp_m.columns = pd.MultiIndex.from_tuples(temp_m.columns.map(lambda x : (x,key)).tolist())
    temp_d.columns = pd.MultiIndex.from_tuples(temp_d.columns.map(lambda x : (x,key)).tolist())
    d_stat.append(temp_d)
    m_stat.append(temp_m)

d_stat = pd.concat(d_stat,axis=1).sort_index(axis=1)
m_stat = pd.concat(m_stat,axis=1).sort_index(axis=1)

out_file = './2021各版本信号统计V2_2.xlsx'
with pd.ExcelWriter(out_file) as writer:
    d_stat.to_excel(writer,sheet_name='逐日')
    m_stat.to_excel(writer,sheet_name='逐月')
writer.close()

send_file(['015664'],out_file)