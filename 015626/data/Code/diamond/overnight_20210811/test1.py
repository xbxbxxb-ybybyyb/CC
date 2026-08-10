from overnight.factor_generator import *
from overnight.insight_retrieve_mdconstant import *
from overnight.insight_retrieve_alla import *
from overnight.insight_retrieve_misc_minute import *
from overnight.naming_config import *
from overnight.utility import *
from multiprocessing import Process
import datetime
from xquant.xqutils.helper import link
lm = link.LinkMessage()
    
        
def executor(trade_date=None, max_workers=12, mode = 'realtime', tag='factors'):
    # load factors
    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), tag)):
        if f.endswith('.py'):
            importlib.import_module('overnight.%s.%s' % (tag, f.split('.')[0]))
    subclass_list = FactorGenerator.__subclasses__()
    print('total factor num: %d' % len(subclass_list))
    # merge hot data
    inst = FactorGenerator()
    inst.merge_hot_data(trade_date=trade_date, mode = mode)
    score_list = list()
    if max_workers == 1:
        for x in subclass_list:
            score_list.append(get_factors(x))
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_factors, subclass_list)
    factor_score = pd.DataFrame(score_list).set_index('name')
    if mode == 'history':
        return factor_score
    elif tag != 'factors':
        return factor_score
    # call model here
    spot_close_dict = inst.get_spot_close_dict()
    recent_contract = re.sub("\D", "", get_current_futures_contract('IC.CFE',trade_date, mode = 'recent'))
    season_contract = re.sub("\D", "", get_current_futures_contract('IC.CFE',trade_date, mode = 'season'))

    volume_limit_dict = {}
    tdays = [x.strftime('%Y%m%d') for x in udt.get_trading_day_offset(inst.__trade_date__, list(range(-1 * calculate_volume_histdays, 0)))]
    for key in ['IC.CFE', 'IF.CFE', 'IH.CFE']:
        future_kind = key.split('.')[0]
        recent_month_df = inst.__data__['volume_%s' % key][inst.__data__['recent_month_mask']].mean(axis = 1).loc[tdays[0]:tdays[-1]]
        recent_month_df = recent_month_df.between_time(calculate_volume_start_time,calculate_volume_stop_time)
        volume_limit_dict['%s%s' % (future_kind, recent_contract)] = recent_month_df.groupby(recent_month_df.index.date).sum().mean() * calculate_volume_ratio
        season_df = inst.__data__['volume_%s' % key][season_contract].loc[tdays[0]:tdays[-1]]
        season_df = season_df.between_time(calculate_volume_start_time,calculate_volume_stop_time)
        volume_limit_dict['%s%s' % (future_kind, season_contract)] = season_df.groupby(season_df.index.date).sum().mean() * calculate_volume_ratio

    settlement_ratio_dict = {}
    for key in ['IC.CFE', 'IF.CFE', 'IH.CFE']:
        future_close = inst.__data__['close_%s' % key]
        future_mask = inst.__data__['recent_month_mask']
        future_amount = inst.__data__['amount_%s' % key]
        future_volume = inst.__data__['volume_%s' % key]
        amount_sum = ts_sum(future_amount, 60)
        volume_sum = ts_sum(future_volume, 60)
        vwap_60 = (amount_sum / volume_sum)[future_mask].sum(axis=1)
        vwap_60 = vwap_60.iloc[vwap_60.index.indexer_at_time(trade_stop_time)].values[-1]
        close_stop_time = future_close[future_mask].sum(axis=1)
        close_stop_time = close_stop_time.iloc[close_stop_time.index.indexer_at_time(trade_stop_time)].values[-1]
        settlement_ratio_dict[key] = round(vwap_60 / price_per_point[key] / close_stop_time, 5)

    trading_plan_1_0, trading_plan_2_0, trading_plan_2_0_05 = signal_dealer(factor_score['norm'], spot_close_dict, recent_contract, season_contract, volume_limit_dict, settlement_ratio_dict)
    print('-' * 60)
    print('Diamond 1.0:')
    print(trading_plan_1_0)
    # lm.sendMessage('Diamond 1.0:\n' + str(trading_plan_1_0))
    print('-' * 60)
    print('Diamond 2.0:')
    print(trading_plan_2_0)
    lm.sendMessage('Diamond 2.0:\n' + str(trading_plan_2_0))
    # lm.sendMessage('Diamond 1.0:\n' + str(trading_plan_1_0[['Contract', 'Contract_Num','Seconds_Interval']]))
    # lm.sendMessage('Diamond 2.0:\n' + str(trading_plan_2_0[['Contract', 'Contract_Num','Seconds_Interval']]))
    print('-' * 60)
    print('Diamond 2.0 0.5版本:')
    print(trading_plan_2_0_05)
    lm.sendMessage('Diamond 2.0 0.5版本:\n' + str(trading_plan_2_0_05))
    
    
    
if __name__ == '__main__':
    executor(trade_date='20210720')