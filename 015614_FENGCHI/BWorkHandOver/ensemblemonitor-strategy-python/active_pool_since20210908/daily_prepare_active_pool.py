# @Time : 2021/9/9 13:18
# @Author : Zhichen Lu
# @File : daily_prepare_active_pool.py
import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading'])


import pandas as pd
from dataApi.tradeDate import get_pre_trade_date
from ExtraTools import get_path_conf
from active_pool_since20210908.daily_update_pre_night_sim import calc_two_part_ratio,get_vol_info
import shutil,configparser,os
from dataApi.sendInfo import send_message
from dataApi.getData import get_daily_1factor,trans_int2windcode
import time

def calc_halved_vol(today,replace=False,extra_stk_list=[],target_stk=None):
    if target_stk is None:
        target_stk = get_restrict_factor_list(today,extra_stk_list=extra_stk_list)
    elif not (isinstance(target_stk,list) or isinstance(target_stk,set)):
        raise Exception('target stk wrong type')

    date = get_pre_trade_date(today)
    conf = configparser.ConfigParser()
    conf.read(f'{init_conf_path}{today}.ini')
    strategy_init = dict(conf['strategy_init'])
    strategy_init_930 = pd.read_pickle(f'{path_for_930}{today}/StrategyIn/init{today}.pkl')

    target_amt_fix = float(strategy_init['per_amt']) * 0.5
    target_amt_930 = float(strategy_init_930['per_amt']) * 0.5

    if not os.path.exists(f'{vol_info_path}{date}_backup.pkl'):
        shutil.copy(f'{vol_info_path}{date}.pkl', f'{vol_info_path}{date}_backup.pkl')
    if not os.path.exists(f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}_backup.pkl'):
        shutil.copy(f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}.pkl',
                    f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}_backup.pkl')
    vol = pd.read_pickle(f'{vol_info_path}{date}_backup.pkl')
    vol_930 = pd.read_pickle(f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}_backup.pkl')

    if set(vol_930.index) != set(vol.columns):
        send_message(['015664'], 'vol930 和 vol 股票列表不一致')

    involved_stk = list(target_stk.intersection(vol.columns).intersection(vol_930.index))

    adj_factor = get_daily_1factor('adjfactor', date_list=[date]).loc[date]
    close = get_daily_1factor('close', date_list=[date]).loc[date]
    close.index = close.index.map(trans_int2windcode)
    adj_factor.index = adj_factor.index.map(trans_int2windcode)
    close = pd.Series(close.tolist(), index=close.index)
    adj_factor = pd.Series(adj_factor.tolist(), index=adj_factor.index)

    target_vol_fix = (target_amt_fix / close / adj_factor).loc[involved_stk] * 10
    target_vol_930 = (target_amt_930 / close).loc[involved_stk] * 10
    target_vol_930.index.names = vol_930.index.names
    target_vol_fix.index.names = vol.index.names

    send_message(['015664'], f'930 Target:\n{target_vol_930 // 100 * 100 * close.loc[target_vol_930.index] * 0.1}')
    send_message(['015664'], f'FIX Target:\n{target_vol_fix * adj_factor.loc[target_vol_fix.index] // 100 * 100 * close.loc[target_vol_fix.index] * 0.1}')

    send_message(['015664'], f'930 before: {vol_930.loc[target_vol_930.index] // 100 * 100 * close.loc[target_vol_930.index] * 0.1}')
    send_message(['015664'], f'Fix before: {vol[target_vol_fix.index] * adj_factor.loc[target_vol_fix.index] // 100 * 100 * close.loc[target_vol_fix.index] * 0.1}')

    vol_930.loc[target_vol_930.index] = target_vol_930
    for bar in vol.index:
        vol.loc[bar, target_vol_fix.index] = target_vol_fix

    send_message(['015664'], f'930 after: {vol_930.loc[target_vol_930.index] // 100 * 100 * close.loc[target_vol_930.index] * 0.1}')
    send_message(['015664'], f'Fix after: {vol[target_vol_fix.index] * adj_factor.loc[target_vol_fix.index] // 100 * 100 * close.loc[target_vol_fix.index] * 0.1}')
    if replace:
        pd.to_pickle(vol, f'{vol_info_path}{date}.pkl')
        pd.to_pickle(vol_930, f'{path_for_930}{get_pre_trade_date(date, -1)}/StrategyIn/vol_info{get_pre_trade_date(date, -1)}.pkl')

        send_message(['015664'], f'{vol_info_path}{target_vol_fix.index.tolist()}成功改变下单上限')
    return vol,vol_930,target_stk

local_config_path = '/data/group/800442/800319/EMExternalPoolTrace/strategy_local_path_TX/'

path_conf = get_path_conf('/data/group/800442/800319/EMExternalPoolTrace/strategy_local_path_TX/')
code_list_path, vol_info_path, hyper_param_path, path_for_930,init_conf_path = \
    [path_conf[x] for x in 'code_list_path,vol_info_path,hyper_param_path,path_for_930,init_conf_path'.split(',')]

if __name__ == '__main__':
    import datetime
    today = int(datetime.date.today().strftime('%Y%m%d'))
    pre_date = get_pre_trade_date(today)
    # pd.to_pickle(pd.Series(),)
    source_path = '/data/group/800319/strategy_local_path3/'

    use_pre_day_pool = False
    while not (os.path.exists(f'/data/group/800442/800319/ConceptStockPool/{pre_date}_restrict.pkl') and os.path.exists(f'/data/group/800442/800319/ConceptStockPool/{pre_date}.pkl')):

        send_message(['015624','015664'],'回测股票池没有正确存放,请在9:30前及时存放，9:30未存放将沿用昨日股票池')
        now = datetime.datetime.now()
        if now>datetime.datetime(today//10000, today//100%100, today%100, 9, 30, 00, 68266):
            use_pre_day_pool = True
            break
        time.sleep(60)
    if use_pre_day_pool:
        shutil.copy(f'{code_list_path}/{get_pre_trade_date(pre_date)}.pkl', f'{code_list_path}/{pre_date}.pkl')
        restrict_pool_list = list(filter(lambda x : '_restrict' in x and x<f'{today}_restrict.pkl',os.listdir('/data/group/800442/800319/ConceptStockPool/')))
        target_list = pd.read_pickle(f'/data/group/800442/800319/ConceptStockPool/{max(restrict_pool_list)}')
        send_message(['015624','015664'],'股票池未在9:30之前存放，已沿用前一日股票池')
    else:
        shutil.copy(f'/data/group/800442/800319/ConceptStockPool/{pre_date}.pkl', f'{code_list_path}/{pre_date}.pkl')
        target_list = pd.read_pickle(f'/data/group/800442/800319/ConceptStockPool/{pre_date}_restrict.pkl')
    if os.path.exists(f'{source_path}factor_hyper_param/mean{pre_date}_backup.pkl'):
        shutil.copy(f'{source_path}factor_hyper_param/mean{pre_date}_backup.pkl',
                    f'{hyper_param_path}mean{pre_date}.pkl')
    else:
        shutil.copy(f'{source_path}factor_hyper_param/mean{pre_date}.pkl',
                f'{hyper_param_path}mean{pre_date}.pkl')
    if os.path.exists(f'{source_path}factor_hyper_param/std{pre_date}_backup.pkl'):
        shutil.copy(f'{source_path}factor_hyper_param/std{pre_date}_backup.pkl',
                    f'{hyper_param_path}std{pre_date}.pkl')
    else:
        shutil.copy(f'{source_path}factor_hyper_param/std{pre_date}.pkl',
                f'{hyper_param_path}std{pre_date}.pkl')
    if os.path.exists(f'{source_path}vol_info/{pre_date}_backup.pkl'):
        shutil.copy(f'{source_path}vol_info/{pre_date}_backup.pkl',
                f'{vol_info_path}{pre_date}.pkl')
    else:
        shutil.copy(f'{source_path}vol_info/{pre_date}.pkl',
                    f'{vol_info_path}{pre_date}.pkl')
    get_vol_info(pre_date)
    calc_two_part_ratio(pre_date)
    pd.to_pickle(pd.Series(),f'{local_config_path}morning_model/val_sign/{today}.pkl')
    calc_halved_vol(today,replace=True, target_stk=set(target_list))


