from overnight.factor_generator import *
from overnight.naming_config import *
import re, os

TRADING_PLAN = read_json(os.path.join(json_path, 'trading_plan.json'))


def get_signal(factor_series):
    factor_series_open = factor_series[factor_series >= 0.75]
    signal_raw = factor_series_open.shape[0] / factor_series.shape[0]
    adjust_coef = np.searchsorted([0.75, 0.8, 0.85, 0.9, 0.95, 1], factor_series_open.mean()) * 0.2 + 0.4
    signal_final = signal_raw * adjust_coef
    return signal_final


def get_signal_final_Diamond_2_0(factor_series):
    future_ic = get_signal(factor_series.reindex(TRADING_PLAN['future_ic']))
    spot_ic = get_signal(factor_series.reindex(TRADING_PLAN['spot_ic']))
    future_if = get_signal(factor_series.reindex(TRADING_PLAN['future_if']))
    spot_if = get_signal(factor_series.reindex(TRADING_PLAN['spot_if']))
    future_ih = get_signal(factor_series.reindex(TRADING_PLAN['future_ih']))
    spot_ih = get_signal(factor_series.reindex(TRADING_PLAN['spot_ih']))
    signal_ic = (future_ic + spot_ic) / 2
    signal_if = (future_if + spot_if) / 2
    signal_ih = (future_ih + spot_ih) / 2
    signal = (signal_ic + signal_if + signal_ih) / 3
    return signal


def get_signal_final_Diamond_1_0(factor_series):
    signal = get_signal(factor_series.reindex(TRADING_PLAN['Diamond_1_0']))
    return signal


def calc_position_from_signal(signal, index_prices, recent_contract, season_contract, volume_limit_dict):
    assert signal >= 0
    assert isinstance(index_prices, dict)
    assert isinstance(recent_contract, str) and re.search('^\d{4}$', recent_contract)
    assert isinstance(season_contract, str) and re.search('^\d{4}$', season_contract)
    trade_money = min(TRADING_PLAN['init_money'] * signal, TRADING_PLAN['total_money_limit'])
    trade_money_per_contract = trade_money / len(index_prices)
    trading_plan = dict()
    for k, v in index_prices.items():
        if k == '000905.SH':
            trade_recent_contract = 'IC' + recent_contract
            trade_season_contract = 'IC' + season_contract
            trade_multiplier = 200
        elif k == '000300.SH':
            trade_recent_contract = 'IF' + recent_contract
            trade_season_contract = 'IF' + season_contract
            trade_multiplier = 300
        elif k == '000016.SH':
            trade_recent_contract = 'IH' + recent_contract
            trade_season_contract = 'IH' + season_contract
            trade_multiplier = 300
        else:
            raise AssertionError
        item_num = np.round(trade_money_per_contract / v / trade_multiplier)
        if item_num > min(TRADING_PLAN['max_num_per_contract'], volume_limit_dict[trade_recent_contract]):
            recent_ratio = volume_limit_dict[trade_recent_contract] / (volume_limit_dict[trade_season_contract] + volume_limit_dict[trade_recent_contract])
            recent_item_num = min(np.floor(item_num * recent_ratio), volume_limit_dict[trade_recent_contract], TRADING_PLAN['max_num_per_contract'])
            season_item_num = min(item_num - recent_item_num, volume_limit_dict[trade_season_contract], TRADING_PLAN['max_num_per_contract'])
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
    trading_plan.index.name = 'Contract'
    trading_plan = trading_plan.reset_index().set_index('Account_Num')
    trading_plan = trading_plan[['Contract', 'Contract_Num', 'Seconds_Interval', 'Signal']]
    return trading_plan


def signal_dealer(factor_series, index_prices, recent_contract, season_contract, volume_limit_dict):
    signal_1_0 = get_signal_final_Diamond_1_0(factor_series)
    signal_2_0 = get_signal_final_Diamond_2_0(factor_series)
    trading_plan_1_0 = calc_position_from_signal(signal_1_0, index_prices, recent_contract, season_contract, volume_limit_dict)
    trading_plan_2_0 = calc_position_from_signal(signal_2_0, index_prices, recent_contract, season_contract, volume_limit_dict)
    return trading_plan_1_0, trading_plan_2_0


