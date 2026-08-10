from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from arrow.data_center_perstock import HistoryData
from arrow.prepare_hot_data_perstock import PrepareHotData
from arrow.naming_config import *
from arrow.utility import *
import pandas as pd
import numpy as np
import importlib
import os, copy
import datetime, time, json
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

    def __init__(self, data_mode = None, required_columns=None, savepath=factor_savepath):
        assert data_mode in [None, 't', 't-1', 'all']
        self.data_mode = data_mode
        self.required_columns = required_columns
        self.savepath = savepath

    @classmethod
    def prepare_hist_data(inst, trade_date=None, hisdays=0, data_kind = 'all'):
        assert data_kind in ['all', 'data', 'factor']
        if trade_date is None:
            trade_date = pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        inst.__trade_date__ = trade_date
        ref_date = int(udt.get_trading_day_offset(inst.__trade_date__, -1)[0].strftime('%Y%m%d'))
        hd = HistoryData(ref_date, hisdays)
        hd.get_all(data_kind = data_kind)
        # inst.checker(hd.collector)
        inst.__data__ = hd.collector

    @classmethod
    def dump_hist_data(inst, data_kind = 'all'):
        save_path = os.path.join(history_root, inst.__trade_date__.strftime('%Y%m%d'))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        histfactor = {}
        if data_kind == 'all':
            histfactor['histfactor'] = inst.__data__['histfactor']
            histfactor['dummy'] = inst.__data__['dummy']
            # histfactor['factor_clip_scope'] = inst.__data__['factor_clip_scope']
            # histfactor['mad_startdate'] = inst.__data__['mad_startdate']
            histfactor['rule_blacklist_df'] = inst.__data__['rule_blacklist_df']
            # del(inst.__data__['histfactor'], inst.__data__['dummy'], inst.__data__['factor_clip_scope'], inst.__data__['mad_startdate'], inst.__data__['rule_blacklist_df'])
            del(inst.__data__['histfactor'], inst.__data__['dummy'], inst.__data__['rule_blacklist_df'])
            diller(os.path.join(save_path, 'history.pkl'), (inst.__trade_date__, inst.__data__, inst.__mdconstant__))
            diller(os.path.join(save_path, 'histfactor_dummy_scope_rule_blacklist.pkl'), histfactor)
        elif data_kind == 'data':
            diller(os.path.join(save_path, 'history.pkl'), (inst.__trade_date__, inst.__data__, inst.__mdconstant__))
        elif data_kind == 'factor':
            diller(os.path.join(save_path, 'histfactor_dummy_scope_rule_blacklist.pkl'), inst.__data__)

    @classmethod
    def load_hist_data(inst, trade_date=None, only_data = False):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        save_path = os.path.join(history_root, trade_date.strftime('%Y%m%d'))
        _trade_date, _data, _mdconstant = diller(os.path.join(save_path, 'history.pkl'))
        assert _trade_date == trade_date
        if not only_data:
            _histfactor = diller(os.path.join(save_path, 'histfactor_dummy_scope_rule_blacklist.pkl'))
            _data.update(_histfactor)
        inst.__trade_date__ = _trade_date
        inst.__data__ = _data
        inst.__mdconstant__ = _mdconstant

    @classmethod
    def merge_hot_data(inst, trade_date=None, ticker = None, factor_mode = None, only_data = False, kind = 'history'):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        inst.__trade_date__ = trade_date
        # load history data
        ref_date = int(udt.get_trading_day_offset(trade_date, -1)[0].strftime('%Y%m%d'))
        hd = HistoryData(ref_date, ticker)
        hd.get_all(data_kind = 'data')
        hist_data = hd.collector
        del(hd)

        if factor_mode == 't-1':
            universe = set(hist_data['universe'])
            for k in name_dict.keys():
                universe = universe & set(hist_data[k].keys())
            prod_data = {}
            prod_data['universe'] = sorted(list(universe))
            data_t_1 = {}
            for k in name_dict.keys():
                stk_data_t_1 = {}
                for stk in universe:
                    stk_data_t_1[stk] = hist_data[k][stk]
                data_t_1[k] = stk_data_t_1
            prod_data['data_t_1'] = data_t_1
            
            # prod_data['histfactor'] = hist_data['histfactor']
            # prod_data['dummy'] = hist_data['dummy']
            # prod_data['factor_clip_scope'] = hist_data['factor_clip_scope']
            # prod_data['mad_startdate'] = hist_data['mad_startdate']
            inst.__data__ = prod_data
            return

        # retrieve hot data
        hd = PrepareHotData(trade_date, ticker)
        hot_data = hd.get_all()
        del(hd)
        # 只保留低开
        # open_low_stk_list = []
        # for stk in hot_data['tick'].keys():
        #     tick = hot_data['tick'][stk]
        #     if stk not in hot_data['transaction'].keys():
        #         continue
        #     transaction = hot_data['transaction'][stk]
        #     tick = tick[tick.PreClosePx > 0]
        #     transaction = transaction[transaction.TradePrice > 0]
        #     if (len(tick) == 0) or (len(transaction) == 0):
        #         continue
        #     pre_close = tick.iloc[-1]['PreClosePx']
        #     trade_price = transaction.iloc[-1]['TradePrice']
        #     if trade_price < pre_close:
        #         open_low_stk_list.append(stk)

        # universe = set(open_low_stk_list)
        universe = set(hist_data['universe'])
        # 处理异常数据
        prod_data = {}
        
        if not only_data:
            prod_data['histfactor'] = hist_data['histfactor']
            prod_data['dummy'] = hist_data['dummy']
            # prod_data['factor_clip_scope'] = hist_data['factor_clip_scope']
            # prod_data['mad_startdate'] = hist_data['mad_startdate']
            prod_data['rule_blacklist_df'] = hist_data['rule_blacklist_df']

        if factor_mode == 't':
            for k in name_dict.keys():
                universe = universe & set(hot_data[k].keys())  & set(hist_data[k].keys()) # 这里要改
            prod_data['universe'] = sorted(list(universe))

            data_t = {}
            data_t_1 = {}
            for k in name_dict.keys():
                stk_data = {}
                stk_data_t = {}
                stk_data_t_1 = {}
                for stk in universe:
                    stk_data[stk] = pd.concat([hist_data[k][stk], hot_data[k][stk]], axis = 0)
                    stk_data_t[stk] = hot_data[k][stk]
                    stk_data_t_1[stk] = hist_data[k][stk]
                prod_data[k] = stk_data
                data_t[k] = stk_data_t
                data_t_1[k] = stk_data_t_1
            prod_data['data_t'] = data_t
            prod_data['data_t_1'] = data_t_1

            save_path = os.path.join(history_root, trade_date.strftime('%Y%m%d'))
            _factor_t_1 = diller(os.path.join(save_path, 'factor_t_1.pkl'))
            prod_data.update(_factor_t_1)
            inst.__data__ = prod_data
            return

        for k in name_dict.keys():
            universe = universe & set(hist_data[k].keys()) & set(hot_data[k].keys()) 
        prod_data['universe'] = sorted(list(universe))
        data_t = {}
        data_t_1 = {}
        for k in name_dict.keys():
            stk_data = {}
            stk_data_t = {}
            stk_data_t_1 = {}
            for stk in universe:
                stk_data[stk] = pd.concat([hist_data[k][stk], hot_data[k][stk]], axis = 0)
                stk_data_t[stk] = hot_data[k][stk]
                stk_data_t_1[stk] = hist_data[k][stk]
            prod_data[k] = stk_data
            data_t[k] = stk_data_t
            data_t_1[k] = stk_data_t_1
        prod_data['data_t'] = data_t
        prod_data['data_t_1'] = data_t_1

        inst.__data__ = prod_data

    def slicer(self):
        if self.data_mode not in ['t', 't-1']:
            # data = {col: self.__data__[col].copy() for col in self.required_columns}
            data = {}
            for col in self.required_columns:
                if '_t_1' in col:
                    data[col] = self.__data__['data_t_1'][col.split('_')[0]].copy()
                elif '_t' in col:
                    data[col] = self.__data__['data_t'][col.split('_')[0]].copy()
                else:
                    data[col] = self.__data__[col].copy()
        # handle_cols = list(set(name_dict.keys()) & set(self.required_columns))
        if self.data_mode == 't':
            data = {col: self.__data__['data_t'][col].copy() for col in self.required_columns}
        elif self.data_mode == 't-1':
            data = {col: self.__data__['data_t_1'][col].copy() for col in self.required_columns}
            # last_trade_date = udt.get_trading_day_offset(self.__trade_date__, -1)[0].strftime('%Y%m%d')
            # for col in handle_cols:
            #     for stk in data[col].keys():
            #         data[col][stk] = data[col][stk].set_index('dt').loc[last_trade_date].reset_index()
        data['universe'] = self.__data__['universe'].copy()
        return data
        
        

    @staticmethod
    def checker(data, date = None):
        assert len(data) > 0
        pass

    def __callback__(self):
        data = self.slicer()
        factor_raw = self.on_bar(data).astype('float64')
        return factor_raw

    def get_avaliable_columns(self):
        return list(self.__data__.keys())

    def get_data(self):
        return self.__data__

    def get_mdconstant(self, k):
        return self.__mdconstant__.get(k, None)

    def get_available_mdconstants(self):
        return list(self.__mdconstant__.keys())

def get_res_factor(factor_score):
    factor_score['factor_order_bo_m'] = factor_score['factor_order_bo_buym'] + factor_score['factor_order_bo_sellm']
    factor_score['factor_order_so_m'] = factor_score['factor_order_so_buym'] + factor_score['factor_order_so_sellm']
    factor_score['factor_412']=factor_score['factor_order_bo_buym'] / (factor_score['factor_order_bo_buym'] + factor_score['factor_order_so_buym'])
    factor_score['factor_413']=factor_score['factor_order_bo_sellm'] / (factor_score['factor_order_bo_sellm'] + factor_score['factor_order_so_sellm'])
    factor_score['factor_414']=factor_score['factor_order_bo10w_buym'] / factor_score['factor_order_bo_buym']
    factor_score['factor_415']=factor_score['factor_order_bo10w_sellm'] / factor_score['factor_order_bo_sellm']
    factor_score['factor_416']=factor_score['factor_order_so10w_buym'] / factor_score['factor_order_so_buym']
    factor_score['factor_417']=factor_score['factor_order_so10w_sellm'] / factor_score['factor_order_so_sellm']
    factor_score['factor_418']=factor_score['factor_order_bo10w_buym'] / factor_score['factor_order_bo10w_sellm']
    factor_score['factor_419']=factor_score['factor_order_so10w_buym'] / factor_score['factor_order_so10w_sellm']
    factor_score['factor_420']=factor_score['factor_order_bo_buym'] / factor_score['factor_order_bo_sellm']
    factor_score['factor_421']=factor_score['factor_order_so_buym'] / factor_score['factor_order_so_sellm']
    factor_score['factor_order_bo_c']=factor_score['factor_order_bo_buyc'] + factor_score['factor_order_bo_sellc']
    factor_score['factor_order_so_c']=factor_score['factor_order_so_buyc'] + factor_score['factor_order_so_sellc']
    factor_score['factor_422']=factor_score['factor_order_bo_buym'] / factor_score['factor_order_bo_buyc']
    factor_score['factor_423']=factor_score['factor_order_bo_sellm'] / factor_score['factor_order_bo_sellc']
    factor_score['factor_424']=factor_score['factor_order_so_buym'] / factor_score['factor_order_so_buyc']
    factor_score['factor_425']=factor_score['factor_order_so_sellm'] / factor_score['factor_order_so_sellc']
    factor_score['factor_426']=factor_score['factor_422'] / factor_score['factor_423'] - 1
    factor_score['factor_427']=factor_score['factor_424'] / factor_score['factor_425'] - 1
    factor_score['factor_tran_bo_m']=factor_score['factor_tran_bo_buym'] + factor_score['factor_tran_bo_sellm']
    factor_score['factor_tran_so_m']=factor_score['factor_tran_so_buym'] + factor_score['factor_tran_so_sellm']
    factor_score['factor_428']=factor_score['factor_tran_bo_buym'] / (factor_score['factor_tran_bo_buym'] + factor_score['factor_tran_so_buym'])
    factor_score['factor_429']=factor_score['factor_tran_bo_sellm'] / (factor_score['factor_tran_bo_sellm'] + factor_score['factor_tran_so_sellm'])
    factor_score['factor_430']=factor_score['factor_tran_bo10w_buym'] / factor_score['factor_tran_bo_buym']
    factor_score['factor_431']=factor_score['factor_tran_bo10w_sellm'] / factor_score['factor_tran_bo_sellm']
    factor_score['factor_432']=factor_score['factor_tran_so10w_buym'] / factor_score['factor_tran_so_buym']
    factor_score['factor_433']=factor_score['factor_tran_so10w_sellm'] / factor_score['factor_tran_so_sellm']
    factor_score['factor_434']=factor_score['factor_tran_bo10w_buym'] / factor_score['factor_tran_bo10w_sellm']
    factor_score['factor_435']=factor_score['factor_tran_so10w_buym'] / factor_score['factor_tran_so10w_sellm']
    factor_score['factor_436']=factor_score['factor_tran_bo_buym'] / factor_score['factor_tran_bo_sellm']
    factor_score['factor_437']=factor_score['factor_tran_so_buym'] / factor_score['factor_tran_so_sellm']
    factor_score['factor_438']=factor_score['factor_order_bo10w_buym'] / factor_score['factor_order_bo10w_buym_tranm']
    factor_score['factor_439']=factor_score['factor_order_bo10w_sellm'] / factor_score['factor_order_bo10w_sellm_tranm']
    factor_score['factor_440']=factor_score['factor_order_bo_buym'] / factor_score['factor_order_bo_buym_tranm']
    factor_score['factor_441']=factor_score['factor_order_bo_sellm'] / factor_score['factor_order_bo_sellm_tranm']
    factor_score['factor_442']=factor_score['factor_order_so10w_buym'] / factor_score['factor_order_so10w_buym_tranm']
    factor_score['factor_443']=factor_score['factor_order_so10w_sellm'] / factor_score['factor_order_so10w_sellm_tranm']
    factor_score['factor_444']=factor_score['factor_order_so_buym'] / factor_score['factor_order_so_buym_tranm']
    factor_score['factor_445']=factor_score['factor_order_so_sellm'] / factor_score['factor_order_so_sellm_tranm'] 

    factor_score['factor_htc_m'] = factor_score['factor_htc_buym'] + factor_score['factor_htc_sellm']
    factor_score['factor_htc_10wm'] = factor_score['factor_htc_buy10wm'] + factor_score['factor_htc_sell10wm']
    factor_score['factor_htc_c'] = factor_score['factor_htc_buyc'] + factor_score['factor_htc_sellc']
    factor_score['factor_htc_10wc'] = factor_score['factor_htc_buy10wc'] + factor_score['factor_htc_sell10wc']
    factor_score['factor_500'] = factor_score['factor_htc_m'] / factor_score['factor_amount_t_1']
    factor_score['factor_501'] = factor_score['factor_htc_sellm'] / factor_score['factor_htc_m']
    factor_score['factor_502'] = factor_score['factor_htc_10wm'] / factor_score['factor_amount_t_1']
    factor_score['factor_503'] = factor_score['factor_htc_sell10wm'] / factor_score['factor_htc_10wm']
    factor_score['factor_504'] = factor_score['factor_htc_sellc'] / factor_score['factor_htc_c']
    factor_score['factor_505'] = factor_score['factor_htc_sell10wc'] / factor_score['factor_htc_10wc']
    factor_score['factor_506'] = factor_score['factor_htc_order_buy10wm'] / factor_score['factor_htc_order_buym']
    factor_score['factor_507'] = factor_score['factor_htc_order_sell10wm'] / factor_score['factor_htc_order_sellm']
    factor_score['factor_508'] = factor_score['factor_htc_buyc'] / factor_score['factor_htc_order_buyc']
    factor_score['factor_509'] = factor_score['factor_htc_sellc'] / factor_score['factor_htc_order_sellc']
    factor_score['factor_510'] = factor_score['factor_htc_buy10wc'] / factor_score['factor_htc_order_buy10wc']
    factor_score['factor_511'] = factor_score['factor_htc_sell10wc'] / factor_score['factor_htc_order_sell10wc']
    factor_score['factor_512'] = factor_score['factor_htc_order_sellc'] / (factor_score['factor_htc_order_sellc'] + factor_score['factor_htc_order_buyc'])
    factor_score['factor_513'] = factor_score['factor_htc_order_sell10wc'] / (factor_score['factor_htc_order_sell10wc'] + factor_score['factor_htc_order_buy10wc'])
    factor_score['factor_514'] = factor_score['factor_htc_order_buym_tranm'] / factor_score['factor_htc_order_buym']
    factor_score['factor_515'] = factor_score['factor_htc_order_sellm_tranm'] / factor_score['factor_htc_order_sellm']
    factor_score['factor_516'] = factor_score['factor_htc_order_buy10wm_tranm'] / factor_score['factor_htc_order_buy10wm']
    factor_score['factor_517'] = factor_score['factor_htc_order_sell10wm_tranm'] / factor_score['factor_htc_order_sell10wm']
    factor_score['factor_518'] = factor_score['factor_htc_order_buym_market_tranm'] / factor_score['factor_htc_order_buym']
    factor_score['factor_519'] = factor_score['factor_htc_order_sellm_market_tranm'] / factor_score['factor_htc_order_sellm']
    factor_score['factor_520'] = factor_score['factor_htc_order_buy10wm_market_tranm'] / factor_score['factor_htc_order_buy10wm']
    factor_score['factor_521'] = factor_score['factor_htc_order_sell10wm_market_tranm'] / factor_score['factor_htc_order_sell10wm']
    factor_score['factor_522'] = factor_score['factor_htc_order_buym_market_tranm'] / factor_score['factor_htc_order_buym_tranm']
    factor_score['factor_523'] = factor_score['factor_htc_order_sellm_market_tranm'] / factor_score['factor_htc_order_sellm_tranm']
    factor_score['factor_524'] = factor_score['factor_htc_order_buy10wm_market_tranm'] / factor_score['factor_htc_order_buy10wm_tranm']
    factor_score['factor_525'] = factor_score['factor_htc_order_sell10wm_market_tranm'] / factor_score['factor_htc_order_sell10wm_tranm']
    factor_score['factor_526'] = factor_score['factor_htc_cancel_buym'] / factor_score['factor_htc_order_buym']
    factor_score['factor_527'] = factor_score['factor_htc_cancel_sellm'] / factor_score['factor_htc_order_sellm']
    factor_score['factor_528'] = factor_score['factor_htc_cancel_buy10wm'] / factor_score['factor_htc_order_buy10wm']
    factor_score['factor_529'] = factor_score['factor_htc_cancel_sell10wm'] / factor_score['factor_htc_order_sell10wm']
    factor_score['factor_530'] = factor_score['factor_htc_cancel_buym'] / factor_score['factor_htc_buym']
    factor_score['factor_531'] = factor_score['factor_htc_cancel_sellm'] / factor_score['factor_htc_sellm']
    factor_score['factor_532'] = factor_score['factor_htc_cancel_buy10wm'] / factor_score['factor_htc_buy10wm']
    factor_score['factor_533'] = factor_score['factor_htc_cancel_sell10wm'] / factor_score['factor_htc_sell10wm']
    factor_score['factor_534'] = factor_score['factor_htc_cancel_buyc'] / factor_score['factor_htc_order_buyc']
    factor_score['factor_535'] = factor_score['factor_htc_cancel_sellc'] / factor_score['factor_htc_order_sellc']
    factor_score['factor_oth_m'] = factor_score['factor_oth_buym'] + factor_score['factor_oth_sellm']
    factor_score['factor_oth_10wm'] = factor_score['factor_oth_buy10wm'] + factor_score['factor_oth_sell10wm']
    factor_score['factor_oth_c'] = factor_score['factor_oth_buyc'] + factor_score['factor_oth_sellc']
    factor_score['factor_oth_10wc'] = factor_score['factor_oth_buy10wc'] + factor_score['factor_oth_sell10wc']
    factor_score['factor_536'] = factor_score['factor_oth_m'] / factor_score['factor_amount_t_1']
    factor_score['factor_537'] = factor_score['factor_oth_sellm'] / factor_score['factor_oth_m']
    factor_score['factor_538'] = factor_score['factor_oth_10wm'] / factor_score['factor_amount_t_1']
    factor_score['factor_539'] = factor_score['factor_oth_sell10wm'] / factor_score['factor_oth_10wm']
    factor_score['factor_540'] = factor_score['factor_oth_sellc'] / factor_score['factor_oth_c']
    factor_score['factor_541'] = factor_score['factor_oth_sell10wc'] / factor_score['factor_oth_10wc']
    factor_score['factor_542'] = factor_score['factor_oth_order_buy10wm'] / factor_score['factor_oth_order_buym']
    factor_score['factor_543'] = factor_score['factor_oth_order_sell10wm'] / factor_score['factor_oth_order_sellm']
    factor_score['factor_544'] = factor_score['factor_oth_buyc'] / factor_score['factor_oth_order_buyc']
    factor_score['factor_545'] = factor_score['factor_oth_sellc'] / factor_score['factor_oth_order_sellc']
    factor_score['factor_546'] = factor_score['factor_oth_buy10wc'] / factor_score['factor_oth_order_buy10wc']
    factor_score['factor_547'] = factor_score['factor_oth_sell10wc'] / factor_score['factor_oth_order_sell10wc']
    factor_score['factor_548'] = factor_score['factor_oth_order_sellc'] / (factor_score['factor_oth_order_sellc'] + factor_score['factor_oth_order_buyc'])
    factor_score['factor_549'] = factor_score['factor_oth_order_sell10wc'] / (factor_score['factor_oth_order_sell10wc'] + factor_score['factor_oth_order_buy10wc'])
    factor_score['factor_550'] = factor_score['factor_oth_order_buym_tranm'] / factor_score['factor_oth_order_buym']
    factor_score['factor_551'] = factor_score['factor_oth_order_sellm_tranm'] / factor_score['factor_oth_order_sellm']
    factor_score['factor_552'] = factor_score['factor_oth_order_buy10wm_tranm'] / factor_score['factor_oth_order_buy10wm']
    factor_score['factor_553'] = factor_score['factor_oth_order_sell10wm_tranm'] / factor_score['factor_oth_order_sell10wm']
    factor_score['factor_554'] = factor_score['factor_oth_order_buym_market_tranm'] / factor_score['factor_oth_order_buym']
    factor_score['factor_555'] = factor_score['factor_oth_order_sellm_market_tranm'] / factor_score['factor_oth_order_sellm']
    factor_score['factor_556'] = factor_score['factor_oth_order_buy10wm_market_tranm'] / factor_score['factor_oth_order_buy10wm']
    factor_score['factor_557'] = factor_score['factor_oth_order_sell10wm_market_tranm'] / factor_score['factor_oth_order_sell10wm']
    factor_score['factor_558'] = factor_score['factor_oth_order_buym_market_tranm'] / factor_score['factor_oth_order_buym_tranm']
    factor_score['factor_559'] = factor_score['factor_oth_order_sellm_market_tranm'] / factor_score['factor_oth_order_sellm_tranm']
    factor_score['factor_560'] = factor_score['factor_oth_order_buy10wm_market_tranm'] / factor_score['factor_oth_order_buy10wm_tranm']
    factor_score['factor_561'] = factor_score['factor_oth_order_sell10wm_market_tranm'] / factor_score['factor_oth_order_sell10wm_tranm']
    factor_score['factor_562'] = factor_score['factor_oth_cancel_buym'] / factor_score['factor_oth_order_buym']
    factor_score['factor_563'] = factor_score['factor_oth_cancel_sellm'] / factor_score['factor_oth_order_sellm']
    factor_score['factor_564'] = factor_score['factor_oth_cancel_buy10wm'] / factor_score['factor_oth_order_buy10wm']
    factor_score['factor_565'] = factor_score['factor_oth_cancel_sell10wm'] / factor_score['factor_oth_order_sell10wm']
    factor_score['factor_566'] = factor_score['factor_oth_cancel_buym'] / factor_score['factor_oth_buym']
    factor_score['factor_567'] = factor_score['factor_oth_cancel_sellm'] / factor_score['factor_oth_sellm']
    factor_score['factor_568'] = factor_score['factor_oth_cancel_buy10wm'] / factor_score['factor_oth_buy10wm']
    factor_score['factor_569'] = factor_score['factor_oth_cancel_sell10wm'] / factor_score['factor_oth_sell10wm']
    factor_score['factor_570'] = factor_score['factor_oth_cancel_buyc'] / factor_score['factor_oth_order_buyc']
    factor_score['factor_571'] = factor_score['factor_oth_cancel_sellc'] / factor_score['factor_oth_order_sellc']
    factor_score['factor_572'] = factor_score['factor_htc_buym'] / factor_score['factor_oth_buym']
    factor_score['factor_573'] = factor_score['factor_htc_sellm'] / factor_score['factor_oth_sellm']
    factor_score['factor_574'] = factor_score['factor_htc_buy10wm'] / factor_score['factor_oth_buy10wm']
    factor_score['factor_575'] = factor_score['factor_htc_sell10wm'] / factor_score['factor_oth_sell10wm']
    factor_score['factor_576'] = factor_score['factor_htc_buyc'] / factor_score['factor_oth_buyc']
    factor_score['factor_577'] = factor_score['factor_htc_sellc'] / factor_score['factor_oth_sellc']
    factor_score['factor_578'] = factor_score['factor_htc_buy10wc'] / factor_score['factor_oth_buy10wc']
    factor_score['factor_579'] = factor_score['factor_htc_sell10wc'] / factor_score['factor_oth_sell10wc']
    factor_score['factor_580'] = factor_score['factor_htc_order_buym'] / factor_score['factor_oth_order_buym']
    factor_score['factor_581'] = factor_score['factor_htc_order_sellm'] / factor_score['factor_oth_order_sellm']
    factor_score['factor_582'] = factor_score['factor_htc_order_buy10wm'] / factor_score['factor_oth_order_buy10wm']
    factor_score['factor_583'] = factor_score['factor_htc_order_sell10wm'] / factor_score['factor_oth_order_sell10wm']
    factor_score['factor_584'] = factor_score['factor_htc_order_buyc'] / factor_score['factor_oth_order_buyc']
    factor_score['factor_585'] = factor_score['factor_htc_order_sellc'] / factor_score['factor_oth_order_sellc']
    factor_score['factor_586'] = factor_score['factor_htc_order_buy10wc'] / factor_score['factor_oth_order_buy10wc']
    factor_score['factor_587'] = factor_score['factor_htc_order_sell10wc'] / factor_score['factor_oth_order_sell10wc']
    factor_score['factor_588'] = factor_score['factor_htc_order_buym_tranm'] / factor_score['factor_oth_order_buym_tranm']
    factor_score['factor_589'] = factor_score['factor_htc_order_sellm_tranm'] / factor_score['factor_oth_order_sellm_tranm']
    factor_score['factor_590'] = factor_score['factor_htc_order_buy10wm_tranm'] / factor_score['factor_oth_order_buy10wm_tranm']
    factor_score['factor_591'] = factor_score['factor_htc_order_sell10wm_tranm'] / factor_score['factor_oth_order_sell10wm_tranm']
    factor_score['factor_592'] = factor_score['factor_htc_order_buym_market_tranm'] / factor_score['factor_oth_order_buym_market_tranm']
    factor_score['factor_593'] = factor_score['factor_htc_order_sellm_market_tranm'] / factor_score['factor_oth_order_sellm_market_tranm']
    factor_score['factor_594'] = factor_score['factor_htc_order_buy10wm_market_tranm'] / factor_score['factor_oth_order_buy10wm_market_tranm']
    factor_score['factor_595'] = factor_score['factor_htc_order_sell10wm_market_tranm'] / factor_score['factor_oth_order_sell10wm_market_tranm']
    factor_score['factor_596'] = factor_score['factor_htc_cancel_buym'] / factor_score['factor_oth_cancel_buym']
    factor_score['factor_597'] = factor_score['factor_htc_cancel_sellm'] / factor_score['factor_oth_cancel_sellm']
    factor_score['factor_598'] = factor_score['factor_htc_cancel_buy10wm'] / factor_score['factor_oth_cancel_buy10wm']
    factor_score['factor_599'] = factor_score['factor_htc_cancel_sell10wm'] / factor_score['factor_oth_cancel_sell10wm']
    factor_score['factor_600'] = factor_score['factor_htc_cancel_buyc'] / factor_score['factor_oth_cancel_buyc']
    factor_score['factor_601'] = factor_score['factor_htc_cancel_sellc'] / factor_score['factor_oth_cancel_sellc']
    factor_score['factor_602'] = factor_score['factor_htc_tick_numratio'] / factor_score['factor_oth_tick_numratio']
    factor_score['factor_603'] = factor_score['factor_htc_ratio'] / factor_score['factor_oth_ratio']
    factor_score['factor_604'] = factor_score['factor_htc_abspath_ratio'] / factor_score['factor_oth_abspath_ratio'] 
    return factor_score

def prepare_history(trade_date=None, hisdays=0):
    inst = FactorGenerator()
    inst.prepare_hist_data(trade_date=trade_date, hisdays=hisdays)
    inst.dump_hist_data()


def get_factors(subcls):
    # print('calculating: ', subcls.__name__)
    try:
        return subcls().__callback__()
    except Exception as e:
        print(subcls.__name__, subcls().__trade_date__.strftime('%Y%m%d'), e)
        with open(os.path.join(trade_root, 'factor_wrong.txt'), 'a') as f:
            f.write(f"{subcls.__name__} {subcls().__trade_date__.strftime('%Y%m%d')} {e}" + '\r\n')

def filter_black_list(trade_date, amt_minute, close_minute):
    pass



def executor_stk_factor(trade_date=None, ticker = None, tag='factors', only_data = True):
    # load factors
    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), tag)):
        if f.endswith('.py'):
            importlib.import_module('arrow.%s.%s' % (tag, f.split('.')[0]))
    subclass_list = FactorGenerator.__subclasses__()
    # merge hot data
    inst = FactorGenerator()
    inst.merge_hot_data(trade_date=trade_date, ticker = ticker, only_data = only_data)
    print('universe count: %d' % len(inst.__data__['universe']), ' factor num: %d' % len(subclass_list))
    if len(inst.__data__['universe']) == 0:
        print('univ num is 0, do not trade.')
        return
    # if len(inst.__data__['universe']) > 100:
    #     print(f"univ num is {len(inst.__data__['universe'])}")
    #     return
    score_list = list()
    time_dict = {}
    factor_sstime = time.time()
    for x in subclass_list:
        sstime = time.time()
        a = get_factors(x)
        score_list.append(a)
        time_dict[a.columns[0]] = time.time() - sstime
    factor_score = pd.concat(score_list, axis = 1).sort_index()
    factor_score.index.name = 'Ticker'

    print('finish factor calculating, use time: ', time.time() - factor_sstime)
    factor_score['dt'] = inst.__trade_date__
    factor_score = factor_score.reset_index().set_index(['dt', 'Ticker'])

    factor_score = get_res_factor(factor_score)

    del(inst)
    return factor_score, time_dict
