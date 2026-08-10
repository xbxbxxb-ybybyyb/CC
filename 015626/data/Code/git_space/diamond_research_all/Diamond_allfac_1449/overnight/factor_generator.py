from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from overnight.data_center import HistoryData, HotData
from overnight.naming_config import *
from overnight.utility import *
from overnight.signal_dealer import signal_dealer
import pandas as pd
import numpy as np
import importlib
import os
import warnings
#import multiprocessing
#multiprocessing.set_start_method('spawn')
from multiprocessing import Pool
from xquant.investment.strategyfile import *
import ftplib
from shutil import copyfile
from overnight.link_v3 import LinkMessage
lm = LinkMessage(['015626', '012398'])


class FactorGenerator:
    __data__ = None
    __mdconstant__ = dict()
    __trade_date__ = None

    def __init__(self, required_columns=None, ts_norm_method='ts_rank', ts_norm_bars=20, savepath=hisfactor_path):
        self.required_columns = required_columns
        assert ts_norm_method in ['ts_rank', 'rolling_norm']
        assert isinstance(ts_norm_bars, int)
        self.ts_norm_method = ts_norm_method
        self.ts_norm_bars = ts_norm_bars
        self.savepath = savepath

    @classmethod
    def prepare_hist_data(inst, trade_date=None, hisdays=15):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        inst.__trade_date__ = trade_date
        ref_date = int(udt.get_trading_day_offset(inst.__trade_date__, -1)[0].strftime('%Y%m%d'))
        zz500_stock_list, hs300_stock_list, zz800_stock_list, sh50_stock_list = get_constituent_stock_list(ref_date)
        alla_stock_list = IO.read_data(ref_date, columns = ['S_DQ_CLOSE'], alt = alla_eod_path).index.get_level_values(1).unique().tolist()
        st_stock_list = get_st_stock_list(trade_date)
        index_components = {'zz500_stock_list': zz500_stock_list,
                            'hs300_stock_list': hs300_stock_list,
                            'zz800_stock_list': zz800_stock_list,
                            'sh50_stock_list' : sh50_stock_list,
                            'st_stock_list': st_stock_list,
                            'alla_stock_list': alla_stock_list}
        inst.__mdconstant__.update(index_components)
        hd = HistoryData(ref_date, hisdays)
        hd.get_all()
        inst.checker(hd.collector)
        inst.__data__ = hd.collector

    @classmethod
    def dump_hist_data(inst):
        save_path = os.path.join(hisdata_path, inst.__trade_date__.strftime('%Y%m%d'))
        os.makedirs(save_path, exist_ok=True)
        diller(os.path.join(save_path, f'history_{minute_to_daily_tag}.pkl'), (inst.__trade_date__, inst.__data__, inst.__mdconstant__))
        diller(os.path.join(save_path, 'zz800_stock_list.pkl'), inst.__mdconstant__['zz800_stock_list'])
        diller(os.path.join(save_path, 'alla_stock_list.pkl'), inst.__mdconstant__['alla_stock_list'])

    @classmethod
    def load_hist_data(inst, trade_date=None):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        save_path = os.path.join(hisdata_path, trade_date.strftime('%Y%m%d'))
        _trade_date, _data, _mdconstant = diller(os.path.join(save_path, 'history_%s.pkl' % minute_to_daily_tag))
        assert _trade_date == trade_date
        inst.__trade_date__ = _trade_date
        inst.__data__ = _data
        inst.__mdconstant__ = _mdconstant

    @classmethod
    def merge_hot_data(inst, trade_date=None, mode='realtime'):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        sstime = time.time()
        # load history data
        inst.load_hist_data(trade_date=trade_date)
        hist_data = inst.__data__
        # retrieve hot data
        hd = HotData(trade_date, mode = mode)
        hd.get_all()
        hot_data = hd.collector
#        save_pickle(hot_data, '/data/user/017024/cache/temp_hot_data.pkl')
        inst.checker(hot_data, date = trade_date)
        time1 = time.time()
        # combine history and hot
        
        # preadj
        alla_ticker_list = sorted(list(set(hot_data['adjfactor_alla_daily'].columns) & \
                                       set(hist_data['close_alla'].columns) & \
                                       set(hist_data['open_alla'].columns) & \
                                       set(hot_data['close_alla'].columns) & \
                                       set(hist_data['close_alla_daily'].columns) & \
                                       set(hot_data['close_alla_daily'].columns)))
        # handle weight stock list
        for k, v in inst.__mdconstant__.items():
            inst.__mdconstant__[k] = sorted(list(set(v) & set(alla_ticker_list)))

        hisadj = hist_data['adjfactor_alla_daily'][alla_ticker_list].fillna(method='ffill')
        hisadj = hisadj.reindex(hist_data['close_alla'].index, method='pad')
        hotadj = hot_data['adjfactor_alla_daily'][alla_ticker_list]
        adj = pd.DataFrame(hisadj.values / np.tile(hotadj.values, (len(hisadj), 1)), index=hisadj.index, columns=hisadj.columns)
        for m in ['open', 'high', 'low', 'close']:
            hist_data['%s_alla_preadj' % m] = hist_data['%s_alla' % m][alla_ticker_list] * adj
            hot_data['%s_alla_preadj' % m] = hot_data['%s_alla' % m][alla_ticker_list]
        for m in ['volume']:
            hist_data['%s_alla_preadj' % m] = hist_data['%s_alla' % m][alla_ticker_list] / adj
            hot_data['%s_alla_preadj' % m] = hot_data['%s_alla' % m][alla_ticker_list]
        time2 = time.time()
        prod_data = {}
        t = minute_to_daily_tag
        for k, v in hot_data.items():
            if k in ['AUDJPY', 'SHIBOR']:
                prod_data[k] = v
            elif k.endswith('.SH') or k.endswith('.CFE') or k.endswith('_daily') or \
                k.endswith('_daily_%s' % minute_to_daily_tag) or (k.split('_')[-1] in ['zz500','hs300','sh50','preadj', '500', 'spot']):
                prod_data[k] = pd.concat([hist_data[k], v], axis=0, sort=False)
            elif k.endswith('_mask'):
                prod_data[k] = pd.concat([hist_data[k], v], axis=0, sort=False).fillna(False).astype('bool')
            elif k.endswith('_alla'):
                minute_to_daily = pd.concat([hist_data[k], v], axis=0, sort=False)
                prod_data[k] = minute_to_daily
                minute_to_daily = minute_to_daily.between_time(minute_to_daily_start_time, minute_to_daily_stop_time).sort_index()
                idx_date_list = pd.to_datetime(minute_to_daily.index.date)
                if k.startswith('open'):
                    minute_to_daily = minute_to_daily.groupby(idx_date_list).fillna(method = 'bfill')
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).first()
                elif k.startswith('high'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).max()
                elif k.startswith('low'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).min()
                elif k.startswith('close'):
                    minute_to_daily = minute_to_daily.groupby(idx_date_list).fillna(method='ffill')
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).last()
                elif k.startswith('volume'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).sum()
                elif k.startswith('amount'):
                    prod_data['%s_daily_%s' % (k, t)] = minute_to_daily.groupby(idx_date_list).sum()
        time3 = time.time()
        float_share_alla_daily = hist_data['float_share_alla_daily']
        float_share_alla_daily.loc[trade_date] = np.nan
        prod_data['float_share_alla_daily'] = float_share_alla_daily.fillna(method='ffill')
        prod_data['raw_factors'] = hist_data['raw_factors']
        for k in prod_data.keys():
            if '_alla' in k:
                prod_data[k] = prod_data[k][alla_ticker_list]

        # sort futures data columns
        futures_column_list = sorted(prod_data['recent_month_mask'].columns.tolist())
        for k in prod_data.keys():
            if k.endswith('.CFE') or ('mask' in k):
                prod_data[k] = prod_data[k][futures_column_list]
        time4 = time.time()
        print(time1 - sstime, time2 - time1, time3 - time2, time4 - time3)

        inst.__data__ = prod_data

    def slicer(self):
        return {col: self.__data__[col].copy() for col in self.required_columns}

    @staticmethod
    def checker(data, date=None):
        assert len(data) > 0
        assert data['recent_month_mask'].sum(axis = 1).sum() == len(data['recent_month_mask']), 'recent_month_mask is wrong'
        for k, v in data.items():
            if k in ['raw_factors']:
                continue
            if date is not None:
                assert len(v.loc[date:].dropna(axis = 0, how = 'all')) >= 0, '%s %s has no data' % (str(date), k)
            if k.endswith('.CFE') or k.endswith('.SH'):
                if k.endswith('.CFE'):
                    if date is None:
                        assert data[k].shape == data['recent_month_mask'].shape , '%s has different shape with mask' % k
                    df = data[k][data['recent_month_mask']].sum(axis = 1)
                else:
                    df = data[k]
                richness = len(df[df > 0]) / len(df)
            else:
                df = data[k]
                richness = len(df.dropna(axis = 0, how = 'all')) / len(df)
                su = k.split('_')[-1]
                if su in ['hs300', 'zz500', 'sh50']:
                    if int(df.shape[1]) != int(re.sub("\D", "", su)):
                        warnings.warn('%s has %f stocks' % (k, int(df.shape[1])))
            assert richness > min_data_richness_threshold, '%s richness is %f' % (k, richness)
            if richness < data_richness_threshold:
                warnings.warn('%s richness is %f' % (k, richness))

    def __callback__(self, only_raw = False):
        data = self.slicer()
        factor_name = self.__class__.__name__
        try:
            factor_raw = self.on_bar(data).loc[self.__trade_date__:].astype('float64')
        except Exception as e:
            factor_raw = pd.DataFrame(np.nan,index=[self.__trade_date__],columns=[factor_name])
            warnings.warn(f'{factor_name} has exception: {e}')
        assert factor_raw.shape[1] == 1, factor_name
        raw_score = factor_raw.loc[self.__trade_date__, factor_name]
        if only_raw:
            return {'name': factor_name, 'raw': raw_score}
        if self.ts_norm_bars in [0, 1]:
            factor_norm = factor_raw
        else:
            factor_raw_whole = pd.concat([self.__data__['raw_factors'][factor_name].astype('float64'), factor_raw], axis=0)
            if self.ts_norm_method == 'ts_rank':
                factor_norm = ts_rank(factor_raw_whole, self.ts_norm_bars)
            elif self.ts_norm_method == 'rolling_norm':
                factor_norm = rolling_norm(factor_raw_whole, self.ts_norm_bars)
        norm_score = factor_norm.loc[self.__trade_date__, factor_name]
        if np.isnan(raw_score) or np.isnan(norm_score):
            warnings.warn(f'{factor_name} returned nan!')
        return {'name': factor_name, 'raw': raw_score, 'norm': norm_score}

    def get_avaliable_columns(self):
        return list(self.__data__.keys())

    def get_data(self):
        return self.__data__

    def get_mdconstant(self, k):
        return self.__mdconstant__.get(k, None)

    def get_available_mdconstants(self):
        return list(self.__mdconstant__.keys())

    def get_spot_close_dict(self):
        target_spot_close_list = ['000905.SH', '000300.SH', '000016.SH']
        return {k:self.__data__['close_%s' % k].iloc[-1] for k in target_spot_close_list}


def prepare_history(trade_date=None, hisdays=15):
    inst = FactorGenerator()
    inst.prepare_hist_data(trade_date=trade_date, hisdays=hisdays)
    inst.dump_hist_data()
    del(inst)

def merge_data(k, hist_data, hot_data):
    print(k)
    v = hot_data[k]
    t = minute_to_daily_tag
    if k in ['AUDJPY', 'SHIBOR']:
        return v
    elif k.endswith('.SH') or k.endswith('.CFE') or k.endswith('_daily') or \
        k.endswith('_daily_%s' % minute_to_daily_tag) or (k.split('_')[-1] in ['zz500','hs300','sh50','preadj', '500', 'spot']):
        return pd.concat([hist_data[k], v], axis=0, sort=False)
    elif k.endswith('_mask'):
        return pd.concat([hist_data[k], v], axis=0, sort=False).fillna(False).astype('bool')
    elif k.endswith('_alla'):
        minute_to_daily = pd.concat([hist_data[k], v], axis=0, sort=False)
        _minute_to_daily = minute_to_daily.copy()
        minute_to_daily = minute_to_daily.between_time(minute_to_daily_start_time, minute_to_daily_stop_time).sort_index()
        idx_date_list = pd.to_datetime(minute_to_daily.index.date)
        if k.startswith('open'):
            minute_to_daily = minute_to_daily.groupby(idx_date_list).fillna(method = 'bfill')
            return _minute_to_daily, minute_to_daily.groupby(idx_date_list).first()
        elif k.startswith('high'):
            return _minute_to_daily, minute_to_daily.groupby(idx_date_list).max()
        elif k.startswith('low'):
            return _minute_to_daily, minute_to_daily.groupby(idx_date_list).min()
        elif k.startswith('close'):
            minute_to_daily = minute_to_daily.groupby(idx_date_list).fillna(method='ffill')
            return _minute_to_daily, minute_to_daily.groupby(idx_date_list).last()
        elif k.startswith('volume'):
            return _minute_to_daily, minute_to_daily.groupby(idx_date_list).sum()
        elif k.startswith('amount'):
            return _minute_to_daily, minute_to_daily.groupby(idx_date_list).sum()

def get_factors(subcls):
    print('calculating: ', subcls.__name__)
    return subcls().__callback__()

def get_raw_factors(subcls):
    # print('calculating: ', subcls.__name__)
    return subcls().__callback__(only_raw = True)


def generate_para_excel(trade_date, trading_plan):
    plan = trading_plan[['Contract','Contract_Num','Account_Num']]
    plan['Contract'] = plan.Contract.apply(lambda x:x+'.CF')
    # plan['Contract'] = [i.replace('2208', '2207')if '2208' in i else i for i in plan['Contract']]
    plan = plan.rename(columns = {'Contract':'合约代码','Contract_Num':'合约张数','Account_Num':'买入交易账户'})
    
    contract_max = plan['合约张数'].max()

#    for i_idx in plan['买入交易账户'].index:
#        if plan['买入交易账户'][i_idx] == 5160501:
#            plan['买入交易账户'][i_idx] = '5160501_ff'
    plan['卖出交易账户'] = plan['买入交易账户']
    # if trading_plan['Signal_1_0'].iloc[0] > 0.05:
    #     plan['买卖方向'] = [afternoon_trade_direction_long[i[:2]] for i in plan['合约代码']]
    # elif trading_plan['Signal_1_0'].iloc[0] <= 0.05:
    #     plan['买卖方向'] = [afternoon_trade_direction_short[i[:2]] for i in plan['合约代码']]
    plan['买卖方向'] = [afternoon_trade_direction_long[i[:2]] for i in plan['合约代码']]
    plan['下单开始时间'] = afternoon_system_start_time.strftime('%H:%M:%S')
    plan['下单结束时间'] = afternoon_system_end_time.strftime('%H:%M:%S')
    plan['每次下单数量'] = num_per_order
    plan['买入证券账户'] = security_account
    plan['卖出证券账户'] = security_account
    plan = plan[['合约代码', '合约张数', '买卖方向', '下单开始时间', '下单结束时间', '每次下单数量', '买入交易账户', '卖出交易账户', '买入证券账户', '卖出证券账户']]

    InitialBasicParam = pd.DataFrame(
        [trade_date, max_contracts_total, max_contracts_perseconds, min_order_interval, max_order_num, max_withd_num, max_withd_cancel_num, 
         max_order_num_past_1min, max_withd_num_past_1min, max_cancellation_num],
        index = ['交易日','当日所有合约开仓数量上限','过去1s所有合约开仓成交数量与挂单数量上限','最小下单间隔', '最大下单次数', '最大撤单次数', '最大撤废次数', 
                 '过去1分钟最大下单次数', '过去1分钟最大撤单次数', '当日废单次数上限']).T
    if contract_max > 0:
        writer = pd.ExcelWriter(
            os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')), 'afternoon_Diamond_%s.xlsx' % (trade_date)))
    else:
        writer = pd.ExcelWriter(
            os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')), 'afternoon_Diamond_%s_1.xlsx' % (trade_date)))
    InitialBasicParam.to_excel(writer, 'InitialBasicParam', index=False)
    plan.to_excel(writer, '交易参数列表', index = False)
    writer.save()
    lm.sendMessage('para excel generate done!')
    
    # generate morning sell close excel
    next_trade_date = udt.get_trading_day_offset(trade_date,1)[0].strftime('%Y%m%d')
    next_InitialBasicParam = InitialBasicParam.copy()
    next_InitialBasicParam['交易日'] = next_trade_date
    
    next_plan = plan.copy()
    # if trading_plan['Signal_1_0'].iloc[0] > 0.05:
    #     next_plan['买卖方向'] = [morning_trade_direction_long[i[:2]] for i in plan['合约代码']]
    # elif trading_plan['Signal_1_0'].iloc[0] <=0.05:
    #     next_plan['买卖方向'] = [morning_trade_direction_short[i[:2]] for i in plan['合约代码']]
    next_plan['买卖方向'] = [morning_trade_direction_long[i[:2]] for i in plan['合约代码']]
    next_plan['下单开始时间'] = morning_system_start_time.strftime('%H:%M:%S')
    next_plan['下单结束时间'] = morning_system_end_time.strftime('%H:%M:%S')
    next_trading_plan_savepath = os.path.join(trading_plan_path, '%s_%s' % (next_trade_date, trade_stop_time.strftime('%H%M')))
    os.makedirs(next_trading_plan_savepath, exist_ok=True)
    if contract_max > 0:
        writer = pd.ExcelWriter(os.path.join(next_trading_plan_savepath, 'morning_Diamond_%s.xlsx' % (next_trade_date)))
    else:
        writer = pd.ExcelWriter(os.path.join(next_trading_plan_savepath, 'morning_Diamond_%s_1.xlsx' % (next_trade_date)))
    next_InitialBasicParam.to_excel(writer, 'InitialBasicParam', index=False)
    next_plan.to_excel(writer, '交易参数列表', index = False)
    writer.save()


def generate_para_excel_separate(trade_date, trading_plan):
    plan = trading_plan[['Contract','Contract_Num','Account_Num']]
    plan['Contract'] = plan.Contract.apply(lambda x:x+'.CF')
    plan = plan.rename(columns = {'Contract':'合约代码','Contract_Num':'合约张数','Account_Num':'买入交易账户'})
    
    contract_max = plan['合约张数'].max()
    plan['卖出交易账户'] = plan['买入交易账户']
    # if trading_plan['Signal_1_0'].iloc[0] >= long_threshold:
    #     plan['买卖方向'] = [afternoon_trade_direction_long[i[:2]] for i in plan['合约代码']]
    # elif trading_plan['Signal_1_0'].iloc[0] < short_threshold:
    #     plan['买卖方向'] = [afternoon_trade_direction_short[i[:2]] for i in plan['合约代码']]
    # else:
    #     plan['买卖方向'] = [afternoon_trade_direction_long[i[:2]] for i in plan['合约代码']]
    plan['买卖方向'] = [afternoon_trade_direction_long[i[:2]] for i in plan['合约代码']]
    lm.sendMessage('afternoon买卖方向: ' + str(plan['买卖方向'].tolist()))
    plan['下单开始时间'] = afternoon_system_start_time.strftime('%H:%M:%S')
    plan['下单结束时间'] = afternoon_system_end_time.strftime('%H:%M:%S')
    plan['每次下单数量'] = num_per_order
    plan['买入证券账户'] = security_account
    plan['卖出证券账户'] = security_account
    plan = plan[['合约代码', '合约张数', '买卖方向', '下单开始时间', '下单结束时间', '每次下单数量', '买入交易账户', '卖出交易账户', '买入证券账户', '卖出证券账户']]
    next_plan = plan.copy()
    
    next_trade_date = udt.get_trading_day_offset(trade_date, 1)[0].strftime('%Y%m%d')
    trading_plan_path_a = os.path.join(trading_plan_path, f'{trade_date}_{trade_stop_time.strftime("%H%M")}')
    trading_plan_path_m = os.path.join(trading_plan_path, f'{next_trade_date}_{trade_stop_time.strftime("%H%M")}')
    
    for i in range(len(plan)):
        temp_contract = plan.iloc[i]['合约代码'].split('.')[0]
        InitialBasicParam = pd.DataFrame(
        [trade_date, max_contracts_total, max_contracts_perseconds, min_order_interval, max_order_num, max_withd_num, max_withd_cancel_num, 
         max_order_num_past_1min, max_withd_num_past_1min, max_cancellation_num, 'DiamondStrategy', temp_contract + plan.iloc[i:i+1]['买卖方向'].values[0]],
        index = ['交易日','当日所有合约开仓数量上限','过去1s所有合约开仓成交数量与挂单数量上限','最小下单间隔', '最大下单次数', '最大撤单次数', '最大撤废次数', 
                 '过去1分钟最大下单次数', '过去1分钟最大撤单次数', '当日废单次数上限', '11041', '11201']).T
        
        if contract_max > 0:
            writer = pd.ExcelWriter(os.path.join(trading_plan_path_a, f'afternoon_Diamond_{trade_date}_{temp_contract}.xlsx'))
        else:
            writer = pd.ExcelWriter(os.path.join(trading_plan_path_a, f'afternoon_Diamond_{trade_date}_{temp_contract}_1.xlsx'))
        InitialBasicParam.to_excel(writer, 'InitialBasicParam', index=False)
        plan.iloc[i:i+1].to_excel(writer, '交易参数列表', index = False)
        writer.save()
    
    # generate morning sell close excel
    # if trading_plan['Signal_1_0'].iloc[0] >= long_threshold:
    #     next_plan['买卖方向'] = [morning_trade_direction_long[i[:2]] for i in plan['合约代码']]
    # elif trading_plan['Signal_1_0'].iloc[0] < short_threshold:
    #     next_plan['买卖方向'] = [morning_trade_direction_short[i[:2]] for i in plan['合约代码']]
    next_plan['买卖方向'] = [morning_trade_direction_long[i[:2]] for i in plan['合约代码']]
    lm.sendMessage('next morning买卖方向: ' + str(next_plan['买卖方向'].tolist()))
    next_plan['下单开始时间'] = morning_system_start_time.strftime('%H:%M:%S')
    next_plan['下单结束时间'] = morning_system_end_time.strftime('%H:%M:%S')
    os.makedirs(trading_plan_path_m, exist_ok=True)
    for i in range(len(next_plan)):
        temp_contract = next_plan.iloc[i]['合约代码'].split('.')[0]
        next_InitialBasicParam = pd.DataFrame(
            [next_trade_date, max_contracts_total, max_contracts_perseconds, min_order_interval, max_order_num, max_withd_num, max_withd_cancel_num, 
            max_order_num_past_1min, max_withd_num_past_1min, max_cancellation_num, 'DiamondStrategy', temp_contract + next_plan.iloc[i:i+1]['买卖方向'].values[0]],
        index = ['交易日','当日所有合约开仓数量上限','过去1s所有合约开仓成交数量与挂单数量上限','最小下单间隔', '最大下单次数', '最大撤单次数', '最大撤废次数', 
            '过去1分钟最大下单次数', '过去1分钟最大撤单次数', '当日废单次数上限', '11041', '11201']).T
            
        if contract_max > 0:
            writer = pd.ExcelWriter(os.path.join(
                trading_plan_path_m, f'morning_Diamond_{next_trade_date}_{temp_contract}.xlsx'))
        else:
            writer = pd.ExcelWriter(os.path.join(
                trading_plan_path_m, f'morning_Diamond_{next_trade_date}_{temp_contract}_1.xlsx'))
        next_InitialBasicParam.to_excel(writer, 'InitialBasicParam', index=False)
        next_plan.iloc[i:i+1].to_excel(writer, '交易参数列表', index = False)
        writer.save()
    flag_path_success = os.path.join(trading_plan_path_a, 'task.success')
    with open(flag_path_success,'w'):
        pass
    lm.sendMessage('para excel generate done!')

def excel_transmission(trade_date):
    next_trading_day = udt.get_trading_day_offset(trade_date, 1)[0].strftime('%Y%m%d')
    sourse_path1 = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')), 'afternoon_Diamond_%s.xlsx' % (trade_date))
    sourse_path2 = os.path.join(trading_plan_path, '%s_%s' % (next_trading_day, trade_stop_time.strftime('%H%M')), 'morning_Diamond_%s.xlsx' % (next_trading_day))
    
    if os.path.exists(sourse_path1) & os.path.exists(sourse_path2):
        destination_path1 = '/data/user/011477/Trade_Docs/%s/Diamond_%s' % (trade_date, trade_date)
        destination_path2 = '/data/user/011477/Trade_Docs/%s/Diamond_%s' % (next_trading_day, next_trading_day)
        os.makedirs(destination_path1, exist_ok=True)
        os.makedirs(destination_path2, exist_ok=True)
        copyfile(sourse_path1, os.path.join(destination_path1, 'afternoon_Diamond_%s.xlsx' % trade_date))
        copyfile(sourse_path2, os.path.join(destination_path2, 'morning_Diamond_%s.xlsx' % next_trading_day))
        
#        ftp = ftplib.FTP('168.8.2.68')
#        ftp.login('xquant', 'Xquant-32')
#        ftp_path1 = '/XQuant/011477/%s/Diamond_%s' % (trade_date, trade_date)
#        ftp.cwd(ftp_path1)
#        ftp.storbinary('STOR '+ 'Diamond_%s_afternoon.xlsx' % trade_date, open(sourse_path1, 'rb'))
#        ftp_path2 = '/XQuant/011477/%s/Diamond_%s' % (next_trading_day, next_trading_day)
#        ftp.cwd(ftp_path2)
#        ftp.storbinary('STOR '+ 'Diamond_%s_morning.xlsx' % next_trading_day, open(sourse_path2, 'rb'))


def excel_transmission_separate(trade_date):
    next_trading_day = udt.get_trading_day_offset(trade_date, 1)[0].strftime('%Y%m%d')
    sourse_path1 = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')))
    sourse_path2 = os.path.join(trading_plan_path, '%s_%s' % (next_trading_day, trade_stop_time.strftime('%H%M')))
    destination_path1 = '/data/user/011477/Trade_Docs/%s/Diamond_%s' % (trade_date, trade_date)
    destination_path2 = '/data/user/011477/Trade_Docs/%s/Diamond_%s' % (next_trading_day, next_trading_day)
    os.makedirs(destination_path1, exist_ok=True)
    os.makedirs(destination_path2, exist_ok=True)

    for i in os.listdir(sourse_path1):
        if not i.endswith('_1.xlsx'):
            copyfile(os.path.join(sourse_path1, i), os.path.join(destination_path1, i))
    for i in os.listdir(sourse_path2):
        if not i.endswith('_1.xlsx'):
            copyfile(os.path.join(sourse_path2, i), os.path.join(destination_path2, i))
        
        
def excel_transmission_tyyth(trade_date):
    next_trading_day = udt.get_trading_day_offset(trade_date, 1)[0].strftime('%Y%m%d')
    sourse_path1 = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')), 'Diamond_%s_afternoon.xlsx' % (trade_date))
    sourse_path2 = os.path.join(trading_plan_path, '%s_%s' % (next_trading_day, trade_stop_time.strftime('%H%M')), 'Diamond_%s_morning.xlsx' % (next_trading_day))
    
    if os.path.exists(sourse_path1) & os.path.exists(sourse_path2):
        upload_strategy_file('DiamondStrategy', trade_date, 1, sourse_path1, is_delete = False, is_ready=1)
        upload_strategy_file('DiamondStrategy', next_trading_day, 1, sourse_path2, is_delete = False, is_ready=1)
        
    
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
    # factor_score.to_csv('/data/user/017024/waiting_for_delete/factor_score.csv')
    # if mode == 'history':
    #     return factor_score
    # elif tag != 'factors':
    #     return factor_score
    # call model here
    spot_close_dict = inst.get_spot_close_dict()
    recent_contract = re.sub("\D", "", get_current_futures_contract('IC.CFE',trade_date, mode = 'recent'))
    season_contract = re.sub("\D", "", get_current_futures_contract('IC.CFE',trade_date, mode = 'season'))

    volume_limit_dict = {}
    tdays = [x.strftime('%Y%m%d') for x in udt.get_trading_day_offset(inst.__trade_date__, list(range(-1 * calculate_volume_histdays, 0)))]
    for key in ['IC.CFE', 'IF.CFE', 'IH.CFE']:
        future_kind = key.split('.')[0]
        recent_month_df = inst.__data__['volume_%s' % key][inst.__data__['recent_month_mask']].mean(axis = 1).loc[tdays[0]:tdays[-1]]
        recent_month_df = recent_month_df.between_time(calculate_volume_start_time, calculate_volume_stop_time)
        volume_limit_dict['%s%s' % (future_kind, recent_contract)] = recent_month_df.groupby(recent_month_df.index.date).sum().mean() * calculate_volume_ratio
        season_df = inst.__data__['volume_%s' % key][season_contract].loc[tdays[0]:tdays[-1]]
        season_df = season_df.between_time(calculate_volume_start_time,calculate_volume_stop_time)
        volume_limit_dict['%s%s' % (future_kind, season_contract)] = season_df.groupby(season_df.index.date).sum().mean() * calculate_volume_ratio
    print('volume_limit_dict', volume_limit_dict)
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
    trade_date = inst.__trade_date__.strftime('%Y%m%d')
    trading_plan_1_0 = signal_dealer(
        factor_score['norm'], spot_close_dict, recent_contract, season_contract, volume_limit_dict, settlement_ratio_dict, trading_version_2, trade_date)
    print('-' * 60)
    print('trading plan')
    print(trading_plan_1_0[['Contract', 'Contract_Num', 'Signal_1_0', 'Signal_4_0', 'Signal_volsig', 'Settlement_Ratio']])
    lm.sendMessage(f'trading plan:\n' + str(trading_plan_1_0[['Contract', 'Contract_Num', 'Signal_1_0', 'Signal_4_0', 'Signal_volsig', 'Settlement_Ratio']]))
    print('-' * 60)
    # dump factor
    # dump trading plan
    trading_plan_savepath = os.path.join(trading_plan_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M')))
    os.makedirs(trading_plan_savepath, exist_ok=True)
    generate_para_excel(trade_date, trading_plan_1_0.reset_index())
    excel_transmission(trade_date)
    generate_para_excel_separate(trade_date, trading_plan_1_0.reset_index())
    excel_transmission_separate(trade_date)
    excel_transmission_tyyth(trade_date)
    trading_plan_1_0.to_csv(os.path.join(trading_plan_savepath, '%s_%s_1_0.csv' % (trade_date, trade_stop_time.strftime('%H%M'))))
    # dump factor
    factor_savepath = os.path.join(factor_path, '%s' % (trade_date + '_' + trade_stop_time.strftime('%H%M')))
    os.makedirs(factor_savepath, exist_ok=True)
    factor_score.to_csv(os.path.join(factor_savepath, '%s_%s.csv' % (trade_date, trade_stop_time.strftime('%H%M'))))
    lm.sendMessage(f'diamond: factor csv success!')

def executor_factor(trade_date=None, max_workers=12, mode = 'realtime', tag='factors'):
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
    trade_date = inst.__trade_date__.strftime('%Y%m%d')
    _savepath = os.path.join(os.path.join(hisfactor_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M'))))
    os.makedirs(_savepath, exist_ok = True)
    factor_score.to_csv(os.path.join(_savepath, '%s_%s.csv' % (trade_date, trade_stop_time.strftime('%H%M'))))

def executor_raw_factor(trade_date=None, max_workers=24, mode = 'realtime', tag='factors'):
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
            score_list.append(get_raw_factors(x))
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_raw_factors, subclass_list)
    factor_score = pd.DataFrame(score_list).set_index('name')
    trade_date = inst.__trade_date__.strftime('%Y%m%d')
    _savepath = os.path.join(os.path.join(hisfactor_path, '%s_%s' % (trade_date, trade_stop_time.strftime('%H%M'))))
    os.makedirs(_savepath, exist_ok = True)
    factor_score.to_csv(os.path.join(_savepath, '%s_%s.csv' % (trade_date, trade_stop_time.strftime('%H%M'))))
    del(inst)
    # return factor_score


