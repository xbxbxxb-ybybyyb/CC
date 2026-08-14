# @Time : 2021/8/10 18:03
# @Author : Zhichen Lu
# @File : bug_report.py
import pandas as pd
from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering
from FactorCalculator_.RealTime import MinFactorCalculator
from dataApi.getData import trans_windcode2int


def compare_factor(date,local_config_path):
    # path_conf = online_path_conf
    # local_config_path = '/data/group/800319/strategy_local_path3_ForMix20210803_V20210907/'  # path_conf['local_config_path']
    fix_online = pd.read_pickle(f'{local_config_path}validation/factor{date}.pkl')
    min5_online = {x:pd.read_pickle(f'{local_config_path}daily_output/{date}/5min_factor_{x}.pkl').T for x in fix_online}

    fix_online_df, min5_online_df = [], []
    for time_point in fix_online:
        fix_online_df.append(fix_online[time_point].rename(index={x: (trans_windcode2int(x), time_point) for x in fix_online[time_point].index}))
        min5_online_df.append(min5_online[time_point].rename(index={x: (trans_windcode2int(x), time_point) for x in min5_online[time_point].index}))
    fix_online_df, min5_online_df = pd.concat(fix_online_df), pd.concat(min5_online_df)
    fix_online_df.index = pd.MultiIndex.from_tuples(fix_online_df.index.tolist())
    min5_online_df.index = pd.MultiIndex.from_tuples(min5_online_df.index.tolist())
    return fix_online_df, min5_online_df

def get_factor_5min_online(date):
    mfc = MinFactorCalculator(date)
    factor = {}
    for bar in [1000,1030,1100,1130,1330,1400,1430]:
        mfc.calc_bar_data(bar,0,threads=10)
        if bar==1130:
            bar[1300] = mfc.factor.copy()
        else:
            factor[bar] = mfc.factor.copy()
    return factor

local_path = '/data/group/800319/strategy_local_path3_ForMix20210803_ray/'
min5_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_HFfactor4/20210803/DateCode/factor_list.pkl')
min5_factor_list = [x[0] for x in min5_factor_list]

desample_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_HFfactor4/20210803/DateCode/desample_factor_list.pkl')
desample_factor_path = '/arch1/group/800442/800319/MinFactor/FactorDpFixData/Factor/'

desample_factor_list = [x[0] for x in desample_factor_list]


# factor_online = mfc.factor.T[min5_factor_list].copy()


start = 20210802
end = 20210816

check_date = 20210803

X_fix_online, X_5min_online = compare_factor(check_date,local_path)

fix_factor_list = X_fix_online.columns.tolist()
code_list = X_fix_online.index.levels[0].tolist()

X_5min, y_5min, nolimit_5min, idx_date_5min, idx_code_5min, idx_time_5min = load_fix_data(start_date=start, end_date=end, factor_list=min5_factor_list,
                                                                                          address='/arch1/group/800442/800319/MinFactorSuper/FactorFixData/Factor/')

X_fix, y_fix, nolimit_fix, idx_date_fix, idx_code_fix, idx_time_fix = load_fix_data(start_date=start, end_date=end, factor_list=fix_factor_list)

X_desample, y_desample, nolimit_desample, idx_date_desample, idx_code_desample, idx_time_desample = load_fix_data(start_date=start, end_date=end, factor_list=desample_factor_list,
                                                                                          address='/arch1/group/800442/800319/MinFactorSuper/FactorFixData/Factor/')

X_fix, y_fix, idx_date_fix, idx_code_fix, idx_time_fix = feature_engineering(X_fix, y_fix, nolimit_fix, idx_date_fix, idx_code_fix, idx_time_fix,limit=1)
X_5min, y_5min, idx_date_5min, idx_code_5min, idx_time_5min = feature_engineering(X_5min, y_5min, nolimit_fix, idx_date_5min, idx_code_5min, idx_time_5min,limit=1)
X_desample, y_desample, idx_date_desample, idx_code_desample, idx_time_desample = feature_engineering(X_desample, y_desample, nolimit_fix, idx_date_desample, idx_code_desample, idx_time_desample,limit=1)

index_fix = pd.MultiIndex.from_tuples(list(zip(idx_date_fix, idx_code_fix, idx_time_fix)))
# index_5min = pd.MultiIndex.from_tuples(list(zip(idx_date_5min, idx_code_5min, idx_time_5min)))
index_desample = pd.MultiIndex.from_tuples(list(zip(idx_date_desample, idx_code_desample, idx_time_desample)))

X_fix = pd.DataFrame(X_fix, index=index_fix, columns=fix_factor_list)
# X_5min = pd.DataFrame(X_5min, index=index_5min, columns=min5_factor_list)
X_desample = pd.DataFrame(X_desample, index=index_desample, columns=desample_factor_list)

X_fix_offline = X_fix.loc[check_date].loc[code_list]
X_5min_offline = pd.DataFrame()
X_desample_offline = X_desample.loc[check_date].loc[X_5min_online.index.levels[0].tolist()]
# X_desample_offline.columns = X_desample_offline.columns.map(lambda x : f'M5{x}')
# X_desample_offline.shape,X_5min_offline.shape
X_5min_offline = pd.concat([X_5min_offline,X_desample_offline],axis=1)


factor_direction = pd.read_pickle(f'{local_path}factor_direction.pkl')
X_fix_offline = X_fix_offline * factor_direction.loc[X_fix_offline.columns]

set(X_5min_offline.columns) - set(X_5min_online.columns)


fix_eval = pd.DataFrame(dict(
    mae=abs(X_fix_online - X_fix_offline).mean(),
    corr=X_fix_online.corrwith(X_fix_offline)
))

min_5_eval = pd.DataFrame(dict(
    mae=abs(X_5min_online - X_5min_offline).mean(),
    corr=X_5min_online.corrwith(X_5min_offline)
))

fix_eval.mean()
min_5_eval.mean()

using_m5_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path3_ForMix20210803_V20210907/using_5min_list.pkl')

min_5_eval.loc[using_m5_factor_list].mean()

compare = pd.DataFrame({'online':X_5min_online['M520201207125623346'],'offline':X_5min_offline['M520201207125623346']})

out_name = './Fix和5分钟线上线下数据-线下因子差异比对20210909.xlsx'
with pd.ExcelWriter(out_name) as wirter:
    pd.DataFrame({'fix':fix_eval.mean(),'5min':min_5_eval.mean()}).to_excel(wirter,sheet_name='总览')
    fix_eval.to_excel(wirter,sheet_name='fix')
    min_5_eval.to_excel(wirter,sheet_name='5min')

wirter.close()

from dataApi.sendInfo import send_file

send_file(['015664'],out_name)

# sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/EnsembleMonitor',
#                  '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel',
#                  '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master',
#                  '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading'])

import os
import pandas as pd

offline_path = '/data/group/800442/simulate_data/%d/%d/stock/'
realtime_data_path =  '/data/group/800442/realtime_data/%d/%d/stock/'

factor_list = ['buyorderamt.pkl', 'buyordervol.pkl', 'high.pkl', 'activebuyorderamt.pkl', 'accamountbuy.pkl', 'selltradeamt.pkl', 'passivesellorderamt.pkl', 'numtrade.pkl', 'activebuyordervol.pkl', 'volume_adj.pkl', 'activesellordervol.pkl', 'limit_status.pkl', 'selltradevol.pkl', 'sellordervol.pkl', 'accamountsell.pkl', 'activesellorderamt.pkl', 'passivebuyorderamt.pkl', 'close.pkl', 'buyordercanceledamt.pkl', 'volume.pkl', 'sellorderamt.pkl', 'close_adj.pkl', 'passivebuyordervol.pkl', 'open.pkl', 'buytradeamt.pkl', 'sellordercanceledamt.pkl', 'buytradenum.pkl', 'sellordercanceledvol.pkl', 'passivesellordervol.pkl', 'low_adj.pkl', 'high_adj.pkl', 'buyordercanceledprice.pkl', 'buytradevol.pkl', 'selltradenum.pkl', 'amt.pkl', 'buyordercanceledvol.pkl', 'open_adj.pkl', 'low.pkl', 'tradenum.pkl']


date = 20210715

difference = {}

for factor_name in factor_list:
    offline_factor = pd.read_pickle(offline_path%(date,1430)+factor_name)
    online_factor = pd.read_pickle(realtime_data_path%(date,1430)+factor_name)
    difference[factor_name.replace('.pkl','')] = abs(offline_factor.fillna(0) - online_factor.fillna(0)).mean()

difference = pd.DataFrame(difference)