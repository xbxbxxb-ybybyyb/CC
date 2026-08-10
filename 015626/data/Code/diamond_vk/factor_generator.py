from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from diamond_vk.data_center import HistoryData, HotData
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import diamond_vk.utility_helper as uth
import pandas as pd
import numpy as np
import importlib
import os
import datetime, time
import warnings
import bottleneck as bk
from multiprocessing import Pool
from xquant.xqutils.helper import link
import ftplib
from shutil import copyfile
from collections import Counter
lm = link.LinkMessage()

class FactorGenerator:
    __data__ = None
    __mdconstant__ = dict()
    __trade_date__ = None

    def __init__(self, required_columns=None, savepath=hisfactor_path):
        self.required_columns = required_columns
        self.savepath = savepath

    @classmethod
    def prepare_hist_data(inst, trade_date=None, hisdays=40):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        inst.__trade_date__ = trade_date
        ref_date = int(udt.get_trading_day_offset(inst.__trade_date__, -1)[0].strftime('%Y%m%d'))
        zz500_stock_list, hs300_stock_list, zz800_stock_list, sh50_stock_list = get_constituent_stock_list(ref_date)
        index_components = {'zz500_stock_list': zz500_stock_list,
                            'hs300_stock_list': hs300_stock_list,
                            'zz800_stock_list': zz800_stock_list,
                            'sh50_stock_list' : sh50_stock_list}
        inst.__mdconstant__.update(index_components)
        hd = HistoryData(ref_date, hisdays)
        hd.get_all()
        # inst.checker(hd.collector)
        inst.__data__ = hd.collector

    @classmethod
    def dump_hist_data(inst):
        save_path = os.path.join(trade_root, 'history', inst.__trade_date__.strftime('%Y%m%d'))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        diller(os.path.join(save_path, 'history_%s.pkl' % minute_to_daily_tag), (inst.__trade_date__, inst.__data__, inst.__mdconstant__))

    @classmethod
    def load_hist_data(inst, trade_date=None):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        save_path = os.path.join(trade_root, 'history', trade_date.strftime('%Y%m%d'))
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
        # load history data
        inst.load_hist_data(trade_date=trade_date)
        hist_data = inst.__data__
        # retrieve hot data
        hd = HotData(trade_date)
        kzz_minute, stk_minute, const = hd.get_all()

        # handle hot data        
        kzz_stock_mapping_dict = hist_data['kzz_stock_mapping_dict']
        kzz_minute = kzz_minute.reset_index().rename(columns = {'Ticker':'kzz_ticker'})
        kzz_minute = kzz_minute[kzz_minute['dt'] <= stk_minute.index.get_level_values(0)[-1]]
        kzz_minute['Ticker'] = kzz_minute.kzz_ticker.apply(lambda x:kzz_stock_mapping_dict[x])
        kzz_minute = kzz_minute.set_index(['dt','Ticker'])
        minute = kzz_minute.join(stk_minute, how = 'left')
        minute = minute.reset_index().drop(['Ticker'], axis = 1).rename(columns = {'kzz_ticker':'Ticker'}).set_index(['dt','Ticker'])
        clist = minute.columns.tolist()
        minute = minute.unstack()
        hot_data = {}
        for x in clist:
            hot_data[x] = minute[x]

        standard_ticker_list = sorted(list(set(hot_data['open'].columns) & \
                                       set(hist_data['open'].columns)))
        prod_data = {}
        for x in ['open', 'close', 'high', 'low', 'volume', 'amount', 'open_stk', 'high_stk', 'low_stk', 'close_stk', 'volume_stk', 'amount_stk']:
            prod_data[x] = hist_data[x].append(hot_data[x])[standard_ticker_list]
        # for x in ['kzz_onret', 'B_INFO_OUTSTANDINGBALANCE', 'CB_ANAL_CONVPRICE', 'model_file', 'model_raw']:
        for x in ['kzz_onret', 'B_INFO_OUTSTANDINGBALANCE', 'CB_ANAL_CONVPRICE']:
            prod_data[x] = hist_data[x]

        prod_data['universe'] = list(set(hist_data['universe']) & set(standard_ticker_list))

        for x in ['volume', 'volume_stk', 'amount', 'amount_stk']:
            _min = prod_data[x]
            _daily = _min.between_time(data_morning_begin, trade_stop_time)
            _daily = _daily.groupby(_daily.index.date).sum()
            _daily.index = pd.to_datetime(_daily.index)
            _daily.index.name = 'dt'
            prod_data['%s_daily' % x] = _daily.copy()
        for x in ['open', 'open_stk']:
            _min = prod_data[x]
            _daily = _min.between_time(data_morning_begin, trade_stop_time)
            _daily = _daily.groupby(_daily.index.date).first()
            _daily.index = pd.to_datetime(_daily.index)
            _daily.index.name = 'dt'
            prod_data['%s_daily' % x] = _daily.copy()
        for x in ['close', 'close_stk']:
            _min = prod_data[x]
            _daily = _min.between_time(data_morning_begin, trade_stop_time)
            _daily = _daily.groupby(_daily.index.date).last()
            _daily.index = pd.to_datetime(_daily.index)
            _daily.index.name = 'dt'
            prod_data['%s_daily' % x] = _daily.copy()
        for x in ['high', 'high_stk']:
            _min = prod_data[x]
            _daily = _min.between_time(data_morning_begin, trade_stop_time)
            _daily = _daily.groupby(_daily.index.date).max()
            _daily.index = pd.to_datetime(_daily.index)
            _daily.index.name = 'dt'
            prod_data['%s_daily' % x] = _daily.copy()
        for x in ['low', 'low_stk']:
            _min = prod_data[x]
            _daily = _min.between_time(data_morning_begin, trade_stop_time)
            _daily = _daily.groupby(_daily.index.date).min()
            _daily.index = pd.to_datetime(_daily.index)
            _daily.index.name = 'dt'
            prod_data['%s_daily' % x] = _daily.copy()

        inst.__data__ = prod_data

    def slicer(self):
        return {col: self.__data__[col].copy() for col in self.required_columns}

    @staticmethod
    def checker(data, date = None):
        assert len(data) > 0
        pass

    def __callback__(self):
        data = self.slicer()
        factor_name = self.__class__.__name__
        factor_raw = self.on_bar(data).astype('float64')
        return factor_raw
        # try:
        #     factor_raw = self.on_bar(data).astype('float64')
        #     return factor_raw
        # except:
        #     print('*****wrong: ',factor_name,'*'*5)
        #     return None

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


def prepare_history(trade_date=None, hisdays=40):
    inst = FactorGenerator()
    inst.prepare_hist_data(trade_date=trade_date, hisdays=hisdays)
    inst.dump_hist_data()


def get_factors(subcls):
    # print('calculating: ', subcls.__name__)
    return subcls().__callback__()

def get_black_list_and_amt(trade_date, amt_minute, close_minute):
    if trade_date is None:
        trade_date =  pd.Timestamp.now().date()
    trade_date = IO.str_date_parser(trade_date)
        
    fusing_list = amt_minute.tail(10).sum()
    fusing_list = set(fusing_list[fusing_list == 0].index.tolist())
    print('fusing list:', fusing_list)    
        
    ref_amt = amt_minute.between_time(morning_start_time, ref_close_end_time)
    ref_amt = ref_amt.groupby(ref_amt.index.date).sum().fillna(0)
    ref_amt.index = pd.to_datetime(ref_amt.index)
    ref_amt = ref_amt.stack()
    ref_amt.index.names = ['dt', 'Ticker']
    ref_amt.columns = ['amount']
    _ref_amt = ref_amt.xs(trade_date, level = 0)
    ref_amt_unstacked = ref_amt.unstack()

    morning_close = close_minute.between_time(morning_start_time, morning_end_time)
    morning_close = morning_close.groupby(morning_close.index.date).mean()
    morning_close.index = pd.to_datetime(morning_close.index)
    morning_close = morning_close.stack()
    morning_close.index.names = ['dt', 'Ticker']
    ref_close = close_minute.between_time(ref_close_start_time, ref_close_end_time)
    ref_close = ref_close.groupby(ref_close.index.date).mean()
    ref_close.index = pd.to_datetime(ref_close.index)
    ref_close = ref_close.stack()
    ref_close.index.names = ['dt', 'Ticker']
    ref_intra = ref_close / morning_close - 1
    ref_intra = ref_intra.replace([np.inf, -np.inf], np.nan)
    ref_intra.name = 'return'
    ref_intra.index.names = ['dt', 'Ticker'] 

    # amount jump blacklist
    amt_jump = ref_amt_unstacked / ref_amt_unstacked.shift()
    amt_jump = amt_jump.stack().reindex(ref_intra.index)
    amt_jump = amt_jump.where(ref_intra >= 0.0, other=-amt_jump).xs(trade_date, level = 0)
    amt_jump_blacklist = set(amt_jump.loc[(amt_jump >= 50) | (amt_jump <= -1.5)].index)

    # amount decay blacklist
    amt_ratio = ref_amt_unstacked / ref_amt_unstacked.rolling(10, min_periods=1).max()
    amt_ratio = amt_ratio.rolling(5, min_periods=1).mean().stack().reindex(ref_intra.index)
    amt_ratio = amt_ratio.where(ref_intra >= 0.0, other=-amt_ratio).xs(trade_date, level = 0)
    amt_decay_blacklist = set(amt_ratio.loc[(amt_ratio < 0) & (amt_ratio >= -0.15)].index)
    
    # return lim blacklist
    _ref_intra = ref_intra.xs(trade_date, level = 0)
    retrum_lim_black_list = set(_ref_intra.loc[_ref_intra < return_lim].index)
    
    # close lim blacklist
    _ref_close = ref_close.xs(trade_date, level = 0)
    close_lim_black_list = set(_ref_close.loc[_ref_close < close_lim].index)
    
    return (amt_jump_blacklist | amt_decay_blacklist | retrum_lim_black_list | close_lim_black_list | fusing_list), _ref_amt
    
def model_predict(factor, model_file):
    # lgbm rank
    lgbm_rank_score = model_file['lgb_rk'].predict(factor, raw_score=True)
    lgbm_rank_score = pd.Series(lgbm_rank_score, index=factor.index)
    # lgbm bin
    lgb_bin_score = model_file['lgb_bin'].predict_proba(factor, raw_score=False)
    lgb_bin_score = pd.Series(lgb_bin_score[:, 1], index=factor.index)
    # et bin
    et_bin_score = model_file['et_bin'].predict_proba(factor.fillna(0))
    et_bin_score = pd.Series(et_bin_score[:, 1], index=factor.index)
    # lr bin
    lr_score = model_file['lr'].predict_proba(factor.fillna(0))
    lr_score = pd.Series(lr_score[:, 1], index=factor.index)
    # lasso 
    def sklearn_predictor(x, res):
        assert np.all([isinstance(item, pd.DataFrame) for item in [x]])
        assert len(res['valid_cols']) != 0
        x_ = (x[res['valid_cols']].replace([np.inf, -np.inf], 0)).values
        return pd.Series(res['model'].predict(x_).ravel(), index=x.index)
    lasso_score = sklearn_predictor(factor.fillna(0), model_file['lasso'])

    model_score_df = pd.concat([lasso_score, lr_score, et_bin_score, lgb_bin_score, lgbm_rank_score], axis = 1)
    model_score_df.columns = ['lasso', 'lr', 'et', 'lgb-bin', 'lgb-rank']
    model_score = {'lasso':lasso_score, 'lr':lr_score, 'et':et_bin_score, 'lgb-bin':lgb_bin_score, 'lgb-rank':lgbm_rank_score}
    return model_score, model_score_df

# 获取每个模型的横截面与时序选债结果
def get_result_per_model(model_score, model_raw, universe):
    model_result = {}
    total_list = []
    for k in model_score.keys():
        model_today = model_score[k]
        model_today_rank = model_today.loc[universe].rank(pct = True)
        section_select_list = model_today_rank[model_today_rank >= section_rank_threshold].index.tolist()

        ts_model = model_raw[k].append(model_score[k].to_frame().T)
        ts_model = ts_rank(ts_model, ts_rank_window).iloc[-1]
        ts_select_list = ts_model[ts_model >= ts_rank_threshold].index.tolist()

        select_list = list(set(section_select_list) & set(ts_select_list))
        total_list = total_list + select_list
        
        model_result[k] = {'select_list':select_list, 'section_select_list':section_select_list, 'ts_select_list':ts_select_list}
    open_num = pd.Series(Counter(total_list))
    model_select_list = open_num[open_num >= open_num_threshold].index.tolist()
    return model_select_list, model_result

def executor(trade_date=None, max_workers=12, mode = 'realtime', tag='factors'):
    # load factors
    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), tag)):
        if f.endswith('.py') and ('-' not in f):
            importlib.import_module('diamond_vk.%s.%s' % (tag, f.split('.')[0]))
    subclass_list = FactorGenerator.__subclasses__()
    print('total factor num: %d' % len(subclass_list))
    # merge hot data
    inst = FactorGenerator()
    inst.merge_hot_data(trade_date=trade_date, mode = mode)
    score_list = list()
    if max_workers == 1:
        for x in subclass_list:
            sstime = time.time()
            a = get_factors(x)
            score_list.append(a)
            print(x.__class__.__name__, a.columns[0], time.time() - sstime)
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_factors, subclass_list)
    factor_score = pd.concat(score_list, axis = 1)
    factor_score_mf = median_filter(factor_score.T, mad = 3)
    # factor_score_norm = factor_score_mf.rank(axis = 1, pct = True).T
    factor_score_prod = factor_score_mf.T[factor_trade_list]
    # factor_score_norm = factor_score_norm[factor_trade_list]

    print('calculate model score')
    model_score, model_score_df = model_predict(factor_score_prod[factor_final_list], inst.__data__['model_file'])
    model_select_list, model_result = get_result_per_model(model_score, inst.__data__['model_raw'], inst.__data__['universe'])

    amount_select = factor_score['kzz_assuper']
    amount_select_list = amount_select[amount_select >= amount_threshold].index.tolist()
    black_list, _ref_amt = get_black_list_and_amt(trade_date, inst.__data__['amount'], inst.__data__['close'])
    final_select_list = sorted(list(set(model_select_list) & set(amount_select_list) - black_list))
    print(len(final_select_list), final_select_list)
    
    clipped_tickers = list(_ref_amt.loc[final_select_list].sort_values().tail(num_lim).index)
    # estimate target quota
    quota_estimate = _ref_amt.loc[clipped_tickers] * quota_limit
    quota_estimate = quota_estimate.clip(0, quota_estimate.min() * quota_scaler).sort_values()
    target_quota = len(clipped_tickers) / num_lim * total_quota
    quota_assigned = pd.Series(uth.slot_even_filler(list(quota_estimate), target_quota), index=quota_estimate.index)
    weight_estimate = uth.vec_normalize(quota_assigned)
    print('FINAL SELECTED NUM: %d' % len(clipped_tickers))
    # retrieve ref close for trading
    trade_price_ref = inst.__data__['close'].fillna(method='pad').iloc[-1, :]
    out_path = os.path.join(json_result_savepath, inst.__trade_date__.strftime('%Y%m%d'))
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    uth.dump_json(os.path.join(out_path, 'target.json'), {'target': clipped_tickers,
                                                         'ref_price': trade_price_ref.to_dict(),
                                                         'quota': quota_assigned.sum(),
                                                         'weight': weight_estimate.to_dict()})
#    uth.put_ftp_file_with_retry(file_name='target.json', file_path=out_path,
#                            output_name=f'CCBond_{inst.__trade_date__:%Y%m%d}.sig')
    
    
    clipped_tickers.sort()
    lm.sendMessage('%s  数量：%s       %s' % (inst.__trade_date__.strftime('%Y%m%d'),str(len(clipped_tickers)),' '.join(clipped_tickers)))
    print(clipped_tickers)
    print(set(final_select_list) - set(clipped_tickers))
    # 以上结果生成后，开始储存结果
    final_select_df = pd.DataFrame(clipped_tickers, columns = ['Ticker'])
#    final_select_df.columns = ['Ticker']
    if not os.path.exists(kzz_select_list_savepath):
        os.makedirs(kzz_select_list_savepath)
    final_select_df.to_csv(os.path.join(kzz_select_list_savepath, '%s.csv' % inst.__trade_date__.strftime('%Y%m%d')), index = False)

    model_score_df['dt'] = inst.__trade_date__.date()
    model_score_df.index.name = 'Ticker'
    model_score_df = model_score_df.reset_index().set_index(['dt','Ticker'])
    IO.pd_hdf5_writer(model_score_df, kzz_model_value_path, dataset=kzz_model_value_key, append = True, data_columns=['dt', 'Ticker'])

    if not os.path.exists(kzz_model_result_savepath):
        os.makedirs(kzz_model_result_savepath)
    diller(os.path.join(kzz_model_result_savepath, 'model_result_%s.pkl' % inst.__trade_date__.strftime('%Y%m%d')), (model_result))

    if not os.path.exists(factor_savepath):
        os.makedirs(factor_savepath)
    factor_score_prod.to_csv(os.path.join(factor_savepath, '%s.csv' % inst.__trade_date__.strftime('%Y%m%d')))

    return 


def executor_factor(trade_date=None, max_workers=24, mode = 'realtime', tag='factors'):
    # load factors
    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), tag)):
        if f.endswith('.py') and ('-' not in f):
            importlib.import_module('diamond_vk.%s.%s' % (tag, f.split('.')[0]))
    subclass_list = FactorGenerator.__subclasses__()
    # print('total factor num: %d' % len(subclass_list))
    # merge hot data
    inst = FactorGenerator()
    inst.merge_hot_data(trade_date=trade_date, mode = mode)
    score_list = list()
    if max_workers == 1:
        for x in subclass_list:
            sstime = time.time()
            a = get_factors(x)
            score_list.append(a)
            # print(x.__class__.__name__, len(a), a.columns[0], time.time() - sstime)
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_factors, subclass_list)
    factor_score = pd.concat(score_list, axis = 1)
    factor_score_mf = median_filter(factor_score.T, mad = 3).T
    # factor_score_norm = factor_score_mf.rank(axis = 1, pct = True).T
    # factor_score_prod = factor_score_mf.T[factor_trade_list]
    # factor_score_norm = factor_score_norm[factor_trade_list]

    if not os.path.exists(factor_savepath):
        os.makedirs(factor_savepath)
    factor_score_mf.to_csv(os.path.join(factor_savepath, '%s.csv' % inst.__trade_date__.strftime('%Y%m%d')))
    del(inst)
    return 
'''    
def executor_model(trade_date=None, mode = 'realtime'):
    trade_date = IO.str_date_parser(trade_date)
    factor_score_prod = pd.read_csv(os.path.join(factor_savepath, '%s.csv' % trade_date.strftime('%Y%m%d')), index_col = 0)
    inst = FactorGenerator()
    inst.merge_hot_data(trade_date=trade_date, mode = mode)
    model_file = diller(kzz_model_file_path)
    model_score, model_score_df = model_predict(factor_score_prod[factor_final_list], model_file)
    model_score_df['dt'] = inst.__trade_date__.date()
    model_score_df.index.name = 'Ticker'
    model_score_df = model_score_df.reset_index().set_index(['dt','Ticker'])
    IO.pd_hdf5_writer(model_score_df, kzz_model_value_path, dataset='model_value_v2', append = True)
'''
