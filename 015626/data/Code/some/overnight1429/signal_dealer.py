from overnight.factor_generator import *
from overnight.naming_config import *
import re, os
from xquant.xqutils.helper import link
lm = link.LinkMessage()

TRADING_PLAN = read_json(os.path.join(json_path, 'trading_plan.json'))


def get_signal(factor_series):
    factor_series_open = factor_series[factor_series >= 0.75]
    signal_raw = factor_series_open.shape[0] / factor_series.shape[0]
    adjust_coef = np.searchsorted([0.75, 0.8, 0.85, 0.9, 0.95, 1], factor_series_open.mean()) * 0.2 + 0.4
    signal_final = signal_raw * adjust_coef
    return signal_final


def get_signal_final_Diamond_2_3(factor_series):
    signal = get_signal(factor_series.reindex(TRADING_PLAN['Diamond_2_3_1429']))
    return signal


def calc_position_from_signal(signal, index_prices, recent_contract, season_contract, volume_limit_dict, settlement_ratio_dict):
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
    assert isinstance(index_prices, dict)
    assert isinstance(recent_contract, str) and re.search('^\d{4}$', recent_contract)
    assert isinstance(season_contract, str) and re.search('^\d{4}$', season_contract)
    trading_plan = dict()
    # settlement_ratio_mean = (settlement_ratio_dict['IC.CFE'] + settlement_ratio_dict['IF.CFE'] + settlement_ratio_dict['IH.CFE']) / 3
    for k, v in index_prices.items():
        if k == '000905.SH':
            trade_recent_contract = 'IC' + recent_contract
            trade_season_contract = 'IC' + season_contract
            trade_multiplier = 200
            settlement_ratio = settlement_ratio_dict['IC.CFE']
        elif k == '000300.SH':
            trade_recent_contract = 'IF' + recent_contract
            trade_season_contract = 'IF' + season_contract
            trade_multiplier = 300
            settlement_ratio = settlement_ratio_dict['IF.CFE']
        elif k == '000016.SH':
            trade_recent_contract = 'IH' + recent_contract
            trade_season_contract = 'IH' + season_contract
            trade_multiplier = 300
            settlement_ratio = settlement_ratio_dict['IH.CFE']
        else:
            raise AssertionError
        signal_temp = signal
        if signal_temp < 0.1:
            signal_temp = 0
#        elif (settlement_ratio < 0.997) & (signal_temp < 0.15):
#            signal_temp = 0
        elif signal_temp > 0.5:
            signal_temp = 0.5
#        elif (settlement_ratio > 1.003) & (signal_temp > 0.15):
#            signal_temp = signal_temp * 2
        trade_money_per_contract = min(TRADING_PLAN['init_money_1429'] * signal_temp, TRADING_PLAN['total_money_limit_1429'])
        item_num = np.round(trade_money_per_contract / v / trade_multiplier)
        if item_num > min(TRADING_PLAN['max_num_per_contract'], volume_limit_dict[trade_recent_contract]):
            recent_ratio = volume_limit_dict[trade_recent_contract] / (volume_limit_dict[trade_season_contract] + volume_limit_dict[trade_recent_contract])
            recent_item_num = np.floor(min(item_num * recent_ratio, volume_limit_dict[trade_recent_contract], TRADING_PLAN['max_num_per_contract']))
            season_item_num = np.floor(min(item_num - recent_item_num, volume_limit_dict[trade_season_contract], TRADING_PLAN['max_num_per_contract']))
            print(volume_limit_dict[trade_season_contract])
            trading_plan[trade_recent_contract] = recent_item_num
            trading_plan[trade_season_contract] = season_item_num
        else:
            trading_plan[trade_recent_contract] = item_num
    trading_plan = pd.Series(trading_plan)
    trading_plan.name = 'Contract_Num'
    trading_plan = trading_plan.to_frame()
    trading_plan['Seconds_Interval'] = np.floor(TRADING_PLAN['trade_seconds'] / trading_plan['Contract_Num'])
    trading_plan['Signal'] = signal
    trading_plan['Account_Num'] = [account_number[''.join(re.findall(r'\D+', i))] for i in trading_plan.index]
    trading_plan['Settlement_Ratio'] = [settlement_ratio_dict[re.findall(r'\D+', i)[0] + '.CFE'] for i in trading_plan.index]
    trading_plan.index.name = 'Contract'
    trading_plan = trading_plan.reset_index().set_index('Account_Num')
    trading_plan = trading_plan[['Contract', 'Contract_Num', 'Seconds_Interval', 'Signal', 'Settlement_Ratio']]
    return trading_plan


def signal_dealer(factor_series, index_prices, recent_contract, season_contract, volume_limit_dict, settlement_ratio_dict):
    signal_2_3 = get_signal_final_Diamond_2_3(factor_series)
    trading_plan_2_3 = calc_position_from_signal(signal_2_3, index_prices, recent_contract, season_contract, volume_limit_dict, settlement_ratio_dict)
    return trading_plan_2_3


