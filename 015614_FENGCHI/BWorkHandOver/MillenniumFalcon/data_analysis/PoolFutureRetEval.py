# @Time : 2021/6/11 9:55
# @Author : Zhichen Lu
# @File : run_backtest.py

import sys

sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])
import pandas as pd
from dataApi.getData import get_daily_1factor


def get_alphapool( alpha_pool_tag,pool_num=600):

    start = 20170101
    end = 20210531

    if pool_dict[alpha_pool_tag] is None:
        alpha_pool = pd.DataFrame()
    elif isinstance(pool_dict[alpha_pool_tag], pd.DataFrame):
        alpha_pool = pool_dict[alpha_pool_tag].shift(1).loc[start:end]
    elif isinstance(pool_dict[alpha_pool_tag], str):
        if alpha_pool_tag.startswith('pool_mix_integrate_replace') or 'Human' in alpha_pool_tag:
            alpha_pool = pd.read_pickle(f'/data/group/800442/800319/AlphaPool/{pool_dict[alpha_pool_tag]}').shift(1).loc[start:end].astype(
                bool)  # .rank(ascending=False, axis=1) < pool_num
        else:
            alpha_pool = pd.read_pickle(f'/data/group/800442/800319/AlphaPool/{pool_dict[alpha_pool_tag]}').shift(1).loc[start:end].rank(ascending=False, axis=1) < pool_num

    else:
        raise Exception('Wrong type')
    # alpha_pool = pd.read_pickle('/data/group/800442/800319/信号存储/daily_stock_score_v3Trigger_20210127.pkl').shift(1).loc[start:end]
    original_pool = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/stock_pool_without_limit_up_down.pkl').shift(1).loc[start:end]
    original_pool = original_pool.drop(alpha_pool.index, axis=0)
    alpha_pool = pd.concat([original_pool, alpha_pool]).sort_index() > 0.5
    return alpha_pool

def eval_stockpool(stock_pool):

    vwap = get_daily_1factor('open')
    # vol = get_daily_1factor('volume')
    # amt = get_daily_1factor('amt')
    # vwap = amt/vol
    adf_factor = get_daily_1factor('adjfactor')
    vwap_badj = adf_factor*vwap
    ret = vwap_badj.pct_change()
    future = ret.shift(-1).reindex(stock_pool.index,axis=0).reindex(stock_pool.columns,axis=1)

    return future[stock_pool].mean(axis=1)

pool_dict = {
    'CS_XGB_OLS_condition_style_rank_ex20': 'CS_XGB|OLS_condition_style_rank_ex20_F600T488P1_future925t241h123d_uniform20t50.pkl'
}

pool_dict.update({x:f'{x}.pkl' for x in [
'HumanAmendPoolRaw','HumanAmendPoolPlan1','HumanAmendPoolPlan2'

]})

from tqdm import tqdm

pool = {}

for each in tqdm(pool_dict):
    if each not in pool:
        pool[each] = get_alphapool(each)

eval_res = {}
for each in tqdm(pool):
    eval_res[each] = eval_stockpool(pool[each])

eval_res = pd.DataFrame(eval_res)
eval_res.to_excel('./PoolRes.xlsx')


eval_res.mean().to_excel('./PoolResMean.xlsx')

eval_res['year'] = eval_res.index.map(lambda x :x//10000)

eval_res.groupby('year').mean().to_excel('./PoolResMeanYealy.xlsx')

from dataApi.sendInfo import send_file

send_file(['015664'],'./PoolRes.xlsx')
send_file(['015664'],'./PoolResMean.xlsx')
send_file(['015664'],'./PoolResMeanYealy.xlsx')
