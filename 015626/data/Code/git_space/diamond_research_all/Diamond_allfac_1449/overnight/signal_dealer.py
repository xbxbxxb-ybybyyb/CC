from overnight.factor_generator import *
from overnight.naming_config import *
import re, os
from overnight.link_v3 import LinkMessage
lm = LinkMessage(['015626'])

def get_signal(factor_series, plan_name='Diamond_1_0'):
    if plan_name == 'Diamond_4_0':
        vollong = max(0, factor_series.loc['ic_if_std'])
        fac_df = factor_series.reindex(TRADING_PLAN[plan_name]).copy()
        fac_df = fac_df >= 0.75
        sig = fac_df.sum() / 190
        signal_final = sig * vollong
        print('Diamond_4_0 raw: signal_final:', round(signal_final, 3), 'sig:', round(sig, 3), 'vollong:', round(vollong, 3))
        lm.sendMessage(f'Diamond_4_0 raw: signal_final: {round(signal_final, 3)} sig: {round(sig, 3)} vollong: {round(vollong, 3)}')
        if signal_final < 0.1:
            signal_final = 0
    elif plan_name == 'Diamond_volsig':
        volsig = factor_series.loc['ic_if_std']
        signal_final = 1 if volsig >= 0.9 else 0
        print('Diamond_volsig raw: ', round(volsig, 6))
        lm.sendMessage(f'Diamond_volsig raw: {round(volsig, 3)}')
    else:
        factor_series = factor_series.reindex(TRADING_PLAN[plan_name]).copy()
        factor_series_open = factor_series[factor_series >= 0.75]
        signal_raw = factor_series_open.shape[0] / factor_series.shape[0]
        adjust_coef = np.searchsorted([0.75, 0.8, 0.85, 0.9, 0.95, 1], factor_series_open.mean()) * 0.2 + 0.4
        signal_final = signal_raw * adjust_coef
    return signal_final

def get_allocation(a, intervals): 
    for lower, upper, amount in intervals:
        if lower <= a < upper:
            return amount
    return None  # 如果a不在任何区间内，返回None或处理异常情况

def calc_position_from_signal_4_0(signal, signal_4_0, signal_volsig, index_prices, recent_contract, season_contract, volume_limit_dict, settlement_ratio_dict, trading_day):
    """
    :param signal: float
        当日信号值
    :param index_prices: dict
        尾盘指数价格
    :param recent_contract: str
        近月连续合约编号
    :param season_contract: str
        当季连续合约编号
    :param volume_limit_dict: dict
        各个合约的交易数量上限
    :param settlement_ratio_dict: dict
        各个品种近月连续合约的尾盘结算比率
    """
    assert signal >= 0
    assert signal_4_0 >= 0
    assert signal_volsig >= 0
    assert isinstance(index_prices, dict)
    assert isinstance(recent_contract, str) and re.search('^\d{4}$', recent_contract)
    assert isinstance(season_contract, str) and re.search('^\d{4}$', season_contract)
    assert isinstance(trading_day,str)
    trading_plan = dict()
    
#    amp_5d = pd.read_pickle(os.path.join(trade_root, 'hot', pd.Timestamp.now().strftime('%Y%m%d'), 'amp_5d.pkl'))
    amp_5d = pd.read_pickle(os.path.join(trade_root, 'hot', trading_day, 'amp_5d.pkl'))
    ret_flag = int(amp_5d > amp_threshold)
    
    # settlement_ratio_mean = (settlement_ratio_dict['IC.CFE'] + settlement_ratio_dict['IF.CFE'] + settlement_ratio_dict['IH.CFE']) / 3
    total_margin = 0
    for k, v in index_prices.items():
        if k == '000905.SH':
            trade_recent_contract = 'IC' + recent_contract
            trade_season_contract = 'IC' + season_contract
            trade_multiplier = 200
            settlement_ratio = settlement_ratio_dict['IC.CFE']
            margin_ratio = 0.14
        elif k == '000300.SH':
            trade_recent_contract = 'IF' + recent_contract
            trade_season_contract = 'IF' + season_contract
            trade_multiplier = 300
            settlement_ratio = settlement_ratio_dict['IF.CFE']
            margin_ratio = 0.12
        elif k == '000016.SH':
            trade_recent_contract = 'IH' + recent_contract
            trade_season_contract = 'IH' + season_contract
            trade_multiplier = 300
            settlement_ratio = settlement_ratio_dict['IH.CFE']
            margin_ratio = 0.14
        else:
            raise AssertionError
        if signal < low_amp_long_threshold:
            signal_temp = signal * ret_flag
        else:
            signal_temp = signal
        if (signal_temp < short_threshold) & open_short:
            signal_temp = -1 * short_money / get_allocation(amp_5d, init_money_1_vals)  # -0.136
        elif (signal_temp <= long_threshold) & (signal_temp > 0):
            signal_temp = 0
#        elif (settlement_ratio < 0.997) & (signal_temp < 0.15):
#            signal_temp = 0
#        elif signal_temp > 0.5:
#            signal_temp = 0.5
#        elif (settlement_ratio > 1.003) & (signal_temp > 0.15):
#            signal_temp = signal_temp * 2
        trade_money_per_contract = min(get_allocation(amp_5d, init_money_1_vals) * abs(signal_temp) + get_allocation(amp_5d, init_money_2_vals) * signal_4_0, get_allocation(amp_5d, total_money_limit_vals))
        if signal_volsig == 1:
            trade_money_per_contract = min(trade_money_per_contract + init_money_3 * signal_volsig, max_money_3)
        if trade_money_per_contract < least_money:
            trade_money_per_contract = 0
            print(f'trade_money_per_contract: {trade_money_per_contract}, less than least_money: {least_money}')
            lm.sendMessage(f'trade_money_per_contract: {trade_money_per_contract}, less than least_money: {least_money}')
        total_margin += (trade_money_per_contract * margin_ratio)
        item_num = np.round(trade_money_per_contract / v / trade_multiplier)
        if item_num > min(TRADING_PLAN['max_num_per_contract'], volume_limit_dict[trade_recent_contract]):
            recent_ratio = volume_limit_dict[trade_recent_contract] / (volume_limit_dict[trade_season_contract] + volume_limit_dict[trade_recent_contract])
            recent_item_num = np.floor(min(item_num * recent_ratio, volume_limit_dict[trade_recent_contract], TRADING_PLAN['max_num_per_contract']))
            season_item_num = np.floor(min(item_num - recent_item_num, volume_limit_dict[trade_season_contract], TRADING_PLAN['max_num_per_contract']))
#            print(volume_limit_dict[trade_season_contract])
            trading_plan[trade_recent_contract] = recent_item_num
            trading_plan[trade_season_contract] = season_item_num
            print(k, v, item_num, recent_ratio, recent_item_num, season_item_num)
        else:
            trading_plan[trade_recent_contract] = item_num
    trading_plan = pd.Series(trading_plan)
    trading_plan.name = 'Contract_Num'
    trading_plan = trading_plan.to_frame()
    trading_plan['Seconds_Interval'] = np.floor(TRADING_PLAN['trade_seconds'] / trading_plan['Contract_Num'])
    trading_plan['Signal_1_0'] = signal
    trading_plan['Signal_4_0'] = signal_4_0
    trading_plan['Signal_volsig'] = signal_volsig
    if signal_temp >= 0:
        trading_plan['Account_Num'] = [account_number_long[''.join(re.findall(r'\D+', i))] for i in trading_plan.index]
    else:
        trading_plan['Account_Num'] = [account_number_short[''.join(re.findall(r'\D+', i))] for i in trading_plan.index]
    trading_plan['Settlement_Ratio'] = [settlement_ratio_dict[re.findall(r'\D+', i)[0] + '.CFE'] for i in trading_plan.index]
    trading_plan.index.name = 'Contract'
    trading_plan = trading_plan.reset_index().set_index('Account_Num')
    trading_plan = trading_plan[['Contract', 'Contract_Num', 'Seconds_Interval', 'Signal_1_0', 'Signal_4_0', 'Signal_volsig', 'Settlement_Ratio']]
    # lm.sendMessage(f'Total margin: {total_margin}')
    return trading_plan

def signal_dealer(factor_series, index_prices, recent_contract, season_contract, volume_limit_dict, settlement_ratio_dict, trading_version, trading_day):
    signal_1_0 = get_signal(factor_series, plan_name=trading_version_1)
    signal_4_0 = get_signal(factor_series, plan_name=trading_version_2)
    signal_volsig = get_signal(factor_series, plan_name=trading_version_3)
    trading_plan_1_0 = calc_position_from_signal_4_0(signal_1_0, signal_4_0, signal_volsig, index_prices, recent_contract, season_contract, volume_limit_dict, settlement_ratio_dict, trading_day)
    return trading_plan_1_0