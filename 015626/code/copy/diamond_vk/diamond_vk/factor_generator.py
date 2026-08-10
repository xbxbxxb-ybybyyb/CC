from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from diamond_vk.data_center import HistoryData, HotData
from diamond_vk.naming_config import *
from diamond_vk.utility import *
# from diamond_vk.signal_dealer import signal_dealer
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

    def __init__(self, required_columns=None, ts_norm_method='ts_rank', ts_norm_bars=20, savepath=hisfactor_path):
        self.required_columns = required_columns
        assert ts_norm_method in ['ts_rank', 'rolling_norm']
        assert isinstance(ts_norm_bars, int)
        self.ts_norm_method = ts_norm_method
        self.ts_norm_bars = ts_norm_bars
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
        for x in ['kzz_onret', 'B_INFO_OUTSTANDINGBALANCE', 'CB_ANAL_CONVPRICE', 'model_file', 'model_raw']:
            prod_data[x] = hist_data[x]
        prod_data['universe'] = list(set(hist_data['universe']) & set(standard_ticker_list))

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


def prepare_history(trade_date=None, hisdays=15):
    inst = FactorGenerator()
    inst.prepare_hist_data(trade_date=trade_date, hisdays=hisdays)
    inst.dump_hist_data()


def get_factors(subcls):
    # print('calculating: ', subcls.__name__)
    return subcls().__callback__()

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

        ts_model = model_raw['et'].append(model_score['et'].to_frame().T)
        ts_model = ts_rank(ts_model, ts_rank_window).iloc[-1]
        ts_select_list = ts_model[ts_model >= ts_rank_threshold].index.tolist()

        select_list = list(set(section_select_list) & set(ts_select_list))
        total_list = total_list + select_list
        
        model_result[k] = {'select_list':select_list, 'section_select_list':section_select_list, 'ts_select_list':ts_select_list}
    open_num = pd.Series(Counter(total_list))
    model_select_list = open_num[open_num > open_num_threshold].index.tolist()
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
            print(x.__class__.__name__, a.columns, time.time() - sstime)
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_factors, subclass_list)
    factor_score = pd.concat(score_list, axis = 1)
    factor_score_mf = median_filter(factor_score.T, mad = 3)
    # factor_score_norm = factor_score_mf.rank(axis = 1, pct = True).T
    factor_score_prod = factor_score_mf.T[factor_trade_list]
    # factor_score_norm = factor_score_norm[factor_trade_list]

    print('calculate model score')
    model_score, model_score_df = model_predict(factor_score_prod, inst.__data__['model_file'])
    model_select_list, model_result = get_result_per_model(model_score, inst.__data__['model_raw'], inst.__data__['universe'])

    amount_select = factor_score['kzz_assuper']
    amount_select_list = amount_select[amount_select >= amount_threshold].index.tolist()
    final_select_list = sorted(list(set(model_select_list) & set(amount_select_list)))
    lm.sendMessage('%s  数量：%s       %s' % (inst.__trade_date__.strftime('%Y%m%d'),str(len(final_select_list)),' '.join(final_select_list)))

    # 以上结果生成后，开始储存结果
    final_select_df = pd.DataFrame(final_select_list)
    final_select_df.columns = ['Ticker']
    if not os.path.exists(kzz_select_list_savepath):
        os.makedirs(kzz_select_list_savepath)
    final_select_df.to_csv(os.path.join(kzz_select_list_savepath, '%s.csv' % inst.__trade_date__.strftime('%Y%m%d')), index = False)

    model_score_df['dt'] = inst.__trade_date__.date()
    model_score_df.index.name = 'Ticker'
    model_score_df = model_score_df.reset_index().set_index(['dt','Ticker'])
    IO.pd_hdf5_writer(model_score_df, kzz_model_value_path, dataset='kzz_model', append = True)

    if not os.path.exists(kzz_model_result_savepath):
        os.makedirs(kzz_model_result_savepath)
    diller(os.path.join(kzz_model_result_savepath, 'model_result_%s.pkl' % inst.__trade_date__.strftime('%Y%m%d')), (model_result))

    if not os.path.exists(factor_savepath):
        os.makedirs(factor_savepath)
    factor_score_prod.to_csv(os.path.join(factor_savepath, '%s.csv' % inst.__trade_date__.strftime('%Y%m%d')))

    return factor_score_prod, model_score, model_result, final_select_list, model_score_df