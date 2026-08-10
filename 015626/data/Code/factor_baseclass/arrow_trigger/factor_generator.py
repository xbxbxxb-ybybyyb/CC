from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
from arrow.data_center import HistoryData, HotData
from arrow.naming_config import *
from arrow.utility import *
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
            histfactor['factor_clip_scope'] = inst.__data__['factor_clip_scope']
            histfactor['mad_startdate'] = inst.__data__['mad_startdate']
            histfactor['rule_blacklist_df'] = inst.__data__['rule_blacklist_df']
            del(inst.__data__['histfactor'], inst.__data__['dummy'], inst.__data__['factor_clip_scope'], inst.__data__['mad_startdate'], inst.__data__['rule_blacklist_df'])
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
    def merge_hot_data(inst, trade_date=None, factor_mode = None, only_data = False):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = IO.str_date_parser(trade_date)
        # load history data
        inst.load_hist_data(trade_date=trade_date, only_data = only_data)
        hist_data = inst.__data__
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
            prod_data['histfactor'] = hist_data['histfactor']
            prod_data['dummy'] = hist_data['dummy']
            prod_data['factor_clip_scope'] = hist_data['factor_clip_scope']
            prod_data['mad_startdate'] = hist_data['mad_startdate']
            inst.__data__ = prod_data
            return

        # retrieve hot data
        hd = HotData(trade_date)
        hot_data = hd.get_all()

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
            prod_data['factor_clip_scope'] = hist_data['factor_clip_scope']
            prod_data['mad_startdate'] = hist_data['mad_startdate']
            prod_data['rule_blacklist_df'] = hist_data['rule_blacklist_df']

        if factor_mode == 't':
            for k in name_dict.keys():
                universe = universe & set(hot_data[k].keys())  & set(hist_data[k].keys()) # 这里要改
            prod_data['universe'] = sorted(list(universe))

            data_t = {}
            for k in name_dict.keys():
                stk_data_t = {}
                for stk in universe:
                    stk_data_t[stk] = hot_data[k][stk]
                data_t[k] = stk_data_t
            prod_data['data_t'] = data_t

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

    factor_score['t_factor_htc_m'] = factor_score['t_factor_htc_buym'] + factor_score['t_factor_htc_sellm']
    factor_score['t_factor_htc_10wm'] = factor_score['t_factor_htc_buy10wm'] + factor_score['t_factor_htc_sell10wm']
    factor_score['t_factor_htc_c'] = factor_score['t_factor_htc_buyc'] + factor_score['t_factor_htc_sellc']
    factor_score['t_factor_htc_10wc'] = factor_score['t_factor_htc_buy10wc'] + factor_score['t_factor_htc_sell10wc']
    factor_score['t_factor_500'] = factor_score['t_factor_htc_m'] / factor_score['t_factor_amount_t_1']
    factor_score['t_factor_501'] = factor_score['t_factor_htc_sellm'] / factor_score['t_factor_htc_m']
    factor_score['t_factor_502'] = factor_score['t_factor_htc_10wm'] / factor_score['t_factor_amount_t_1']
    factor_score['t_factor_503'] = factor_score['t_factor_htc_sell10wm'] / factor_score['t_factor_htc_10wm']
    factor_score['t_factor_504'] = factor_score['t_factor_htc_sellc'] / factor_score['t_factor_htc_c']
    factor_score['t_factor_505'] = factor_score['t_factor_htc_sell10wc'] / factor_score['t_factor_htc_10wc']
    factor_score['t_factor_506'] = factor_score['t_factor_htc_order_buy10wm'] / factor_score['t_factor_htc_order_buym']
    factor_score['t_factor_507'] = factor_score['t_factor_htc_order_sell10wm'] / factor_score['t_factor_htc_order_sellm']
    factor_score['t_factor_508'] = factor_score['t_factor_htc_buyc'] / factor_score['t_factor_htc_order_buyc']
    factor_score['t_factor_509'] = factor_score['t_factor_htc_sellc'] / factor_score['t_factor_htc_order_sellc']
    factor_score['t_factor_510'] = factor_score['t_factor_htc_buy10wc'] / factor_score['t_factor_htc_order_buy10wc']
    factor_score['t_factor_511'] = factor_score['t_factor_htc_sell10wc'] / factor_score['t_factor_htc_order_sell10wc']
    factor_score['t_factor_512'] = factor_score['t_factor_htc_order_sellc'] / (factor_score['t_factor_htc_order_sellc'] + factor_score['t_factor_htc_order_buyc'])
    factor_score['t_factor_513'] = factor_score['t_factor_htc_order_sell10wc'] / (factor_score['t_factor_htc_order_sell10wc'] + factor_score['t_factor_htc_order_buy10wc'])
    factor_score['t_factor_514'] = factor_score['t_factor_htc_order_buym_tranm'] / factor_score['t_factor_htc_order_buym']
    factor_score['t_factor_515'] = factor_score['t_factor_htc_order_sellm_tranm'] / factor_score['t_factor_htc_order_sellm']
    factor_score['t_factor_516'] = factor_score['t_factor_htc_order_buy10wm_tranm'] / factor_score['t_factor_htc_order_buy10wm']
    factor_score['t_factor_517'] = factor_score['t_factor_htc_order_sell10wm_tranm'] / factor_score['t_factor_htc_order_sell10wm']
    factor_score['t_factor_518'] = factor_score['t_factor_htc_order_buym_market_tranm'] / factor_score['t_factor_htc_order_buym']
    factor_score['t_factor_519'] = factor_score['t_factor_htc_order_sellm_market_tranm'] / factor_score['t_factor_htc_order_sellm']
    factor_score['t_factor_520'] = factor_score['t_factor_htc_order_buy10wm_market_tranm'] / factor_score['t_factor_htc_order_buy10wm']
    factor_score['t_factor_521'] = factor_score['t_factor_htc_order_sell10wm_market_tranm'] / factor_score['t_factor_htc_order_sell10wm']
    factor_score['t_factor_522'] = factor_score['t_factor_htc_order_buym_market_tranm'] / factor_score['t_factor_htc_order_buym_tranm']
    factor_score['t_factor_523'] = factor_score['t_factor_htc_order_sellm_market_tranm'] / factor_score['t_factor_htc_order_sellm_tranm']
    factor_score['t_factor_524'] = factor_score['t_factor_htc_order_buy10wm_market_tranm'] / factor_score['t_factor_htc_order_buy10wm_tranm']
    factor_score['t_factor_525'] = factor_score['t_factor_htc_order_sell10wm_market_tranm'] / factor_score['t_factor_htc_order_sell10wm_tranm']
    factor_score['t_factor_526'] = factor_score['t_factor_htc_cancel_buym'] / factor_score['t_factor_htc_order_buym']
    factor_score['t_factor_527'] = factor_score['t_factor_htc_cancel_sellm'] / factor_score['t_factor_htc_order_sellm']
    factor_score['t_factor_528'] = factor_score['t_factor_htc_cancel_buy10wm'] / factor_score['t_factor_htc_order_buy10wm']
    factor_score['t_factor_529'] = factor_score['t_factor_htc_cancel_sell10wm'] / factor_score['t_factor_htc_order_sell10wm']
    factor_score['t_factor_530'] = factor_score['t_factor_htc_cancel_buym'] / factor_score['t_factor_htc_buym']
    factor_score['t_factor_531'] = factor_score['t_factor_htc_cancel_sellm'] / factor_score['t_factor_htc_sellm']
    factor_score['t_factor_532'] = factor_score['t_factor_htc_cancel_buy10wm'] / factor_score['t_factor_htc_buy10wm']
    factor_score['t_factor_533'] = factor_score['t_factor_htc_cancel_sell10wm'] / factor_score['t_factor_htc_sell10wm']
    factor_score['t_factor_534'] = factor_score['t_factor_htc_cancel_buyc'] / factor_score['t_factor_htc_order_buyc']
    factor_score['t_factor_535'] = factor_score['t_factor_htc_cancel_sellc'] / factor_score['t_factor_htc_order_sellc']
    factor_score['t_factor_oth_m'] = factor_score['t_factor_oth_buym'] + factor_score['t_factor_oth_sellm']
    factor_score['t_factor_oth_10wm'] = factor_score['t_factor_oth_buy10wm'] + factor_score['t_factor_oth_sell10wm']
    factor_score['t_factor_oth_c'] = factor_score['t_factor_oth_buyc'] + factor_score['t_factor_oth_sellc']
    factor_score['t_factor_oth_10wc'] = factor_score['t_factor_oth_buy10wc'] + factor_score['t_factor_oth_sell10wc']
    factor_score['t_factor_536'] = factor_score['t_factor_oth_m'] / factor_score['t_factor_amount_t_1']
    factor_score['t_factor_537'] = factor_score['t_factor_oth_sellm'] / factor_score['t_factor_oth_m']
    factor_score['t_factor_538'] = factor_score['t_factor_oth_10wm'] / factor_score['t_factor_amount_t_1']
    factor_score['t_factor_539'] = factor_score['t_factor_oth_sell10wm'] / factor_score['t_factor_oth_10wm']
    factor_score['t_factor_540'] = factor_score['t_factor_oth_sellc'] / factor_score['t_factor_oth_c']
    factor_score['t_factor_541'] = factor_score['t_factor_oth_sell10wc'] / factor_score['t_factor_oth_10wc']
    factor_score['t_factor_542'] = factor_score['t_factor_oth_order_buy10wm'] / factor_score['t_factor_oth_order_buym']
    factor_score['t_factor_543'] = factor_score['t_factor_oth_order_sell10wm'] / factor_score['t_factor_oth_order_sellm']
    factor_score['t_factor_544'] = factor_score['t_factor_oth_buyc'] / factor_score['t_factor_oth_order_buyc']
    factor_score['t_factor_545'] = factor_score['t_factor_oth_sellc'] / factor_score['t_factor_oth_order_sellc']
    factor_score['t_factor_546'] = factor_score['t_factor_oth_buy10wc'] / factor_score['t_factor_oth_order_buy10wc']
    factor_score['t_factor_547'] = factor_score['t_factor_oth_sell10wc'] / factor_score['t_factor_oth_order_sell10wc']
    factor_score['t_factor_548'] = factor_score['t_factor_oth_order_sellc'] / (factor_score['t_factor_oth_order_sellc'] + factor_score['t_factor_oth_order_buyc'])
    factor_score['t_factor_549'] = factor_score['t_factor_oth_order_sell10wc'] / (factor_score['t_factor_oth_order_sell10wc'] + factor_score['t_factor_oth_order_buy10wc'])
    factor_score['t_factor_550'] = factor_score['t_factor_oth_order_buym_tranm'] / factor_score['t_factor_oth_order_buym']
    factor_score['t_factor_551'] = factor_score['t_factor_oth_order_sellm_tranm'] / factor_score['t_factor_oth_order_sellm']
    factor_score['t_factor_552'] = factor_score['t_factor_oth_order_buy10wm_tranm'] / factor_score['t_factor_oth_order_buy10wm']
    factor_score['t_factor_553'] = factor_score['t_factor_oth_order_sell10wm_tranm'] / factor_score['t_factor_oth_order_sell10wm']
    factor_score['t_factor_554'] = factor_score['t_factor_oth_order_buym_market_tranm'] / factor_score['t_factor_oth_order_buym']
    factor_score['t_factor_555'] = factor_score['t_factor_oth_order_sellm_market_tranm'] / factor_score['t_factor_oth_order_sellm']
    factor_score['t_factor_556'] = factor_score['t_factor_oth_order_buy10wm_market_tranm'] / factor_score['t_factor_oth_order_buy10wm']
    factor_score['t_factor_557'] = factor_score['t_factor_oth_order_sell10wm_market_tranm'] / factor_score['t_factor_oth_order_sell10wm']
    factor_score['t_factor_558'] = factor_score['t_factor_oth_order_buym_market_tranm'] / factor_score['t_factor_oth_order_buym_tranm']
    factor_score['t_factor_559'] = factor_score['t_factor_oth_order_sellm_market_tranm'] / factor_score['t_factor_oth_order_sellm_tranm']
    factor_score['t_factor_560'] = factor_score['t_factor_oth_order_buy10wm_market_tranm'] / factor_score['t_factor_oth_order_buy10wm_tranm']
    factor_score['t_factor_561'] = factor_score['t_factor_oth_order_sell10wm_market_tranm'] / factor_score['t_factor_oth_order_sell10wm_tranm']
    factor_score['t_factor_562'] = factor_score['t_factor_oth_cancel_buym'] / factor_score['t_factor_oth_order_buym']
    factor_score['t_factor_563'] = factor_score['t_factor_oth_cancel_sellm'] / factor_score['t_factor_oth_order_sellm']
    factor_score['t_factor_564'] = factor_score['t_factor_oth_cancel_buy10wm'] / factor_score['t_factor_oth_order_buy10wm']
    factor_score['t_factor_565'] = factor_score['t_factor_oth_cancel_sell10wm'] / factor_score['t_factor_oth_order_sell10wm']
    factor_score['t_factor_566'] = factor_score['t_factor_oth_cancel_buym'] / factor_score['t_factor_oth_buym']
    factor_score['t_factor_567'] = factor_score['t_factor_oth_cancel_sellm'] / factor_score['t_factor_oth_sellm']
    factor_score['t_factor_568'] = factor_score['t_factor_oth_cancel_buy10wm'] / factor_score['t_factor_oth_buy10wm']
    factor_score['t_factor_569'] = factor_score['t_factor_oth_cancel_sell10wm'] / factor_score['t_factor_oth_sell10wm']
    factor_score['t_factor_570'] = factor_score['t_factor_oth_cancel_buyc'] / factor_score['t_factor_oth_order_buyc']
    factor_score['t_factor_571'] = factor_score['t_factor_oth_cancel_sellc'] / factor_score['t_factor_oth_order_sellc']
    factor_score['t_factor_572'] = factor_score['t_factor_htc_buym'] / factor_score['t_factor_oth_buym']
    factor_score['t_factor_573'] = factor_score['t_factor_htc_sellm'] / factor_score['t_factor_oth_sellm']
    factor_score['t_factor_574'] = factor_score['t_factor_htc_buy10wm'] / factor_score['t_factor_oth_buy10wm']
    factor_score['t_factor_575'] = factor_score['t_factor_htc_sell10wm'] / factor_score['t_factor_oth_sell10wm']
    factor_score['t_factor_576'] = factor_score['t_factor_htc_buyc'] / factor_score['t_factor_oth_buyc']
    factor_score['t_factor_577'] = factor_score['t_factor_htc_sellc'] / factor_score['t_factor_oth_sellc']
    factor_score['t_factor_578'] = factor_score['t_factor_htc_buy10wc'] / factor_score['t_factor_oth_buy10wc']
    factor_score['t_factor_579'] = factor_score['t_factor_htc_sell10wc'] / factor_score['t_factor_oth_sell10wc']
    factor_score['t_factor_580'] = factor_score['t_factor_htc_order_buym'] / factor_score['t_factor_oth_order_buym']
    factor_score['t_factor_581'] = factor_score['t_factor_htc_order_sellm'] / factor_score['t_factor_oth_order_sellm']
    factor_score['t_factor_582'] = factor_score['t_factor_htc_order_buy10wm'] / factor_score['t_factor_oth_order_buy10wm']
    factor_score['t_factor_583'] = factor_score['t_factor_htc_order_sell10wm'] / factor_score['t_factor_oth_order_sell10wm']
    factor_score['t_factor_584'] = factor_score['t_factor_htc_order_buyc'] / factor_score['t_factor_oth_order_buyc']
    factor_score['t_factor_585'] = factor_score['t_factor_htc_order_sellc'] / factor_score['t_factor_oth_order_sellc']
    factor_score['t_factor_586'] = factor_score['t_factor_htc_order_buy10wc'] / factor_score['t_factor_oth_order_buy10wc']
    factor_score['t_factor_587'] = factor_score['t_factor_htc_order_sell10wc'] / factor_score['t_factor_oth_order_sell10wc']
    factor_score['t_factor_588'] = factor_score['t_factor_htc_order_buym_tranm'] / factor_score['t_factor_oth_order_buym_tranm']
    factor_score['t_factor_589'] = factor_score['t_factor_htc_order_sellm_tranm'] / factor_score['t_factor_oth_order_sellm_tranm']
    factor_score['t_factor_590'] = factor_score['t_factor_htc_order_buy10wm_tranm'] / factor_score['t_factor_oth_order_buy10wm_tranm']
    factor_score['t_factor_591'] = factor_score['t_factor_htc_order_sell10wm_tranm'] / factor_score['t_factor_oth_order_sell10wm_tranm']
    factor_score['t_factor_592'] = factor_score['t_factor_htc_order_buym_market_tranm'] / factor_score['t_factor_oth_order_buym_market_tranm']
    factor_score['t_factor_593'] = factor_score['t_factor_htc_order_sellm_market_tranm'] / factor_score['t_factor_oth_order_sellm_market_tranm']
    factor_score['t_factor_594'] = factor_score['t_factor_htc_order_buy10wm_market_tranm'] /factor_score['t_factor_oth_order_buy10wm_market_tranm']
    factor_score['t_factor_595'] = factor_score['t_factor_htc_order_sell10wm_market_tranm'] / factor_score['t_factor_oth_order_sell10wm_market_tranm']
    factor_score['t_factor_596'] = factor_score['t_factor_htc_cancel_buym'] / factor_score['t_factor_oth_cancel_buym']
    factor_score['t_factor_597'] = factor_score['t_factor_htc_cancel_sellm'] / factor_score['t_factor_oth_cancel_sellm']
    factor_score['t_factor_598'] = factor_score['t_factor_htc_cancel_buy10wm'] / factor_score['t_factor_oth_cancel_buy10wm']
    factor_score['t_factor_599'] = factor_score['t_factor_htc_cancel_sell10wm'] / factor_score['t_factor_oth_cancel_sell10wm']
    factor_score['t_factor_600'] = factor_score['t_factor_htc_cancel_buyc'] / factor_score['t_factor_oth_cancel_buyc']
    factor_score['t_factor_601'] = factor_score['t_factor_htc_cancel_sellc'] / factor_score['t_factor_oth_cancel_sellc']
    factor_score['t_factor_602'] = factor_score['t_factor_htc_tick_numratio'] / factor_score['t_factor_oth_tick_numratio']
    factor_score['t_factor_603'] = factor_score['t_factor_htc_ratio'] / factor_score['t_factor_oth_ratio']
    factor_score['t_factor_604'] = factor_score['t_factor_htc_abspath_ratio'] / factor_score['t_factor_oth_abspath_ratio'] 

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

def model_predict(factor):
    # path setting
    model_path_dict = {m:os.path.join(model_root,'%s.pkl' % m) for m in model_list}
    stack_model_path = os.path.join(stack_model_root, '%s.pkl' % stack_model)

    pred_raw_dict = {}
    for model in model_list:
        model_save_itr = model_path_dict[model]
        pred_raw = pred_one_helper(factor.copy(), model_save_itr, model).unstack()
        pred_raw_dict[model] = pred_raw.stack().iloc[:,0]
    pred_raw_df = pd.DataFrame(pred_raw_dict)

    model_save_itr = stack_model_path
    x_test_stack = pred_raw_df[model_list]
    pred_stack = pred_one_helper(x_test_stack, model_save_itr, stack_model).unstack()
    pred_raw_dict['stack'] = pred_stack.stack().iloc[:,0]
    pred_raw_df = pd.DataFrame(pred_raw_dict)
    return pred_raw_df

def executor_t_1_factor(trade_date=None, max_workers=24, tag='factors', factor_mode = 't-1', save_factor = True):
    # load factors
    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), tag)):
        if f.endswith('.py'):
            importlib.import_module('arrow.%s.%s' % (tag, f.split('.')[0]))
    subclass_list = FactorGenerator.__subclasses__()
    if factor_mode in ['t', 't-1']:
        subclass_list = [x for x in subclass_list if x().data_mode == factor_mode]
    # merge hot data
    inst = FactorGenerator()
    inst.merge_hot_data(trade_date=trade_date, factor_mode = factor_mode)
    print('universe count: %d' % len(inst.__data__['universe']), 't-1 factor num: %d' % len(subclass_list))
    if len(inst.__data__['universe']) == 0:
        print('univ num is 0, do not trade.')
        return
    score_list = list()
    factor_sstime = time.time()
    if max_workers == 1:
        for x in subclass_list:
            sstime = time.time()
            a = get_factors(x)
            score_list.append(a)
            print(x.__class__.__name__, a.columns[0], time.time() - sstime)
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_factors, subclass_list)
    factor_score = pd.concat(score_list, axis = 1).sort_index()
    factor_score.index.name = 'Ticker'

    print('finish factor calculating, use time: ', time.time() - factor_sstime)
    factor_score['dt'] = inst.__trade_date__
    factor_score = factor_score.reset_index().set_index(['dt', 'Ticker'])
    if save_factor:
        save_path = os.path.join(history_root, inst.__trade_date__.strftime('%Y%m%d'))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        diller(os.path.join(save_path, 'factor_t_1.pkl'), {'factor_t_1':factor_score})
    del(inst)
    # return factor_score

def executor_all_factor(trade_date=None, max_workers=24, tag='factors', only_data = True):
    # load factors
    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), tag)):
        if f.endswith('.py'):
            importlib.import_module('arrow.%s.%s' % (tag, f.split('.')[0]))
    subclass_list = FactorGenerator.__subclasses__()
    # merge hot data
    inst = FactorGenerator()
    inst.merge_hot_data(trade_date=trade_date, only_data = only_data)
    print('universe count: %d' % len(inst.__data__['universe']), ' factor num: %d' % len(subclass_list))
    if len(inst.__data__['universe']) == 0:
        print('univ num is 0, do not trade.')
        return
    # if len(inst.__data__['universe']) > 100:
    #     print(f"univ num is {len(inst.__data__['universe'])}")
    #     return
    score_list = list()
    factor_sstime = time.time()
    if max_workers == 1:
        for x in subclass_list:
            sstime = time.time()
            a = get_factors(x)
            score_list.append(a)
            print(x.__class__.__name__, a.columns[0], time.time() - sstime)
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_factors, subclass_list)
    factor_score = pd.concat(score_list, axis = 1).sort_index()
    factor_score.index.name = 'Ticker'

    print('finish factor calculating, use time: ', time.time() - factor_sstime)
    factor_score['dt'] = inst.__trade_date__
    factor_score = factor_score.reset_index().set_index(['dt', 'Ticker'])

    factor_score = get_res_factor(factor_score)
    
    for path in [factor_savepath]:
        if not os.path.exists(path):
            os.makedirs(path)
    str_date = inst.__trade_date__.strftime('%Y%m%d')
    factor_score.reset_index(level = 0, drop = True).to_csv(os.path.join(factor_savepath, '%s.csv' % str_date))

    del(inst)

def get_arrow_black_list(four_factor, rule_data):
    data = four_factor.join(rule_data, how = 'inner').rename(columns = {'factor_1':'bsp', 'factor_openPct':'open_to_preclose', 'factor_s1_high_to_limit':'s1_high_to_limit', 'factor_s2_high_to_limit':'s2_high_to_limit'})
    data = data[rule_blacklist_columns]

    # last_day_tail5_ll: 14:50以后开板
    # last_day_rolling_60min_drawdown: 滚动60分钟最大回撤
    d1 = data[(data['filter_1']) & (data['last_day_close_to_open'] < -0.05) & (data['open_to_preclose'] < -0.05) & (
            data['last_day_amount_ratio'] > 1.5)]
    d2 = data[(data['filter_1']) & (data['last_day_close_to_open'] < -0.03) & (data['bsp'] < 0.2) & (
            data['last_day_amount_ratio'] > 1.5)]
    d3 = data[(data['filter_1']) & (data['last_day_close_to_open'] < -0.05) & (data['last_day_high_to_open'] == 0) & (
            data['last_day_amount_ratio'] > 1.5)]
    d4 = data[(data['filter_1']) & (data['open_to_preclose'] < -0.07) & (data['last_day_amount_ratio'] > 1.5)]
    d5 = data[(data['filter_1']) & (data['last_day_high_to_open'] < 0.03) & (data['last_day_close_to_open'] < 0) & (
            data['bsp'] < 0.2) & (data['last_day_amount_ratio'] > 1.5)]
    d6 = data[(data['filter_1']) & (data['last_day_high_to_close'] > 0.05) & (data['last_day_close_to_open'] < 0) & (
            data['bsp'] < 0.2) & (data['last_day_amount_ratio'] > 1.5)]
    d7 = data[(data['filter_1']) & (data['last_day_high_to_close'] > 0.08) & (data['bsp'] < 0.2) & (
            data['last_day_amount_ratio'] > 1.5)]
    d8 = data[(data['filter_1']) & (data['last_day_high_to_close'] > 0.11) & (data['last_day_amount_ratio'] > 1.5)]
    d9 = data[(data['filter_1']) & (data['last_day_tail5_ll'])]
    d10 = data[(data['filter_1']) & (data['last_day_xyx'] > 0.03)]
    d11 = data[(data['filter_2']) & (data['last_day_close_to_open'] < -0.07) & (data['bsp'] < 0.2) & (
            data['last_day_amount_ratio'] > 1.5)]
    d12 = data[(data['filter_2']) & (data['last_day_xyx'] > 0.05) & (data['bsp'] < 0.2)]
    d13 = data[(data['filter_2']) & (data['last_day_xyx'] > 0.08)]
    d14 = data[(data['filter_3']) & (data['last_day_high_to_open'] == 0) & (data['open_to_preclose'] < -0.05) & (
            data['last_day_amount_ratio'] > 1.5)]
    d15 = data[(data['filter_3']) & (data['dby_high_to_low'] == 0) & (data['open_to_preclose'] < -0.05) & (
            data['last_day_amount_ratio'] > 1.5)]
    d16 = data[(data['filter_3']) & (data['last_day_close_to_open'] < -0.07) & (data['bsp'] < 0.2) & (
            data['last_day_amount_ratio'] > 1.5)]
    d17 = data[(data['filter_3']) & (data['last_day_high_to_close'] > 0.1) & (data['last_day_close_to_open'] < 0) & (
            data['bsp'] < 0.2) & (data['last_day_amount_ratio'] > 1.5)]
    d18 = data[(data['last_day_rolling_60min_drawdown'] > 0) & (data['bsp'] < 0.2) & (
            data['last_day_amount_ratio'] > 1.5)]
    d19 = data[data['amount'] < 1e7]
    d20 = data[data['last_day_tail10_close_to_low'] > 0.03]
    d21 = data[((data['s1_high_to_limit'] > 0.999) | (data['s2_high_to_limit'] > 0.95)) & (data['bsp'] < 0.2)]
    d_all = pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15, d16, d17, d18, d19, d20, d21])
    # assert d_all.index.is_unique
    return d_all.index.unique().to_list()

def executor(trade_date=None, max_workers=24, tag='factors', factor_mode = 't'):
    # load factors
    assert factor_mode != 't-1'
    for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), tag)):
        if f.endswith('.py'):
            importlib.import_module('arrow.%s.%s' % (tag, f.split('.')[0]))
    subclass_list = FactorGenerator.__subclasses__()
    if factor_mode in ['t']:
        subclass_list = [x for x in subclass_list if x().data_mode == factor_mode]
    # merge hot data
    inst = FactorGenerator()
    data_stime = time.time()
    inst.merge_hot_data(trade_date=trade_date, factor_mode = factor_mode)
    print('finish merge hot data, use time: ', time.time() - data_stime)
    print('universe count: %d' % len(inst.__data__['universe']), 'total factor num: %d' % len(subclass_list))
    if len(inst.__data__['universe']) == 0:
        print('univ num is 0, do not trade.')
        return
    score_list = list()
    factor_sstime = time.time()
    if max_workers == 1:
        for x in subclass_list:
            sstime = time.time()
            a = get_factors(x)
            score_list.append(a)
            print(x.__class__.__name__, a.columns[0], time.time() - sstime)
    else:
        with Pool(processes=max_workers) as pool:
            score_list = pool.map(get_factors, subclass_list)
    factor_score = pd.concat(score_list, axis = 1).sort_index()
    factor_score.index.name = 'Ticker'

    print('finish factor calculating, use time: ', time.time() - factor_sstime)
    factor_score['dt'] = inst.__trade_date__
    factor_score = factor_score.reset_index().set_index(['dt', 'Ticker'])
    if factor_mode == 't':
        factor_score = factor_score.join(inst.__data__['factor_t_1'])

    factor_score = factor_score[inst.__data__['factor_clip_scope']['down'].index.tolist()].replace([np.inf, -np.inf], np.nan)
    factor_clip = np_clip(factor_score, inst.__data__['factor_clip_scope']['down'], inst.__data__['factor_clip_scope']['up'])

    factor_all = inst.__data__['histfactor'].append(factor_clip).sort_index()
    factor_prod = factor_all[factor_final_list]

    flist = [inst.__data__['dummy']]
    mad_dict = inst.__data__['mad_startdate']
    for x in mad_dict.keys():
        flist.append(mad(factor_prod.loc[pd.to_datetime(mad_dict[x]):]).loc[inst.__trade_date__:].add_suffix(f'_z{x}'))

    factor_input = pd.concat(flist, axis = 1, join = 'inner').replace([np.inf, -np.inf], np.nan).fillna(0)

    model_sstime = time.time()
    print('start model predict')
    pred_raw_df = model_predict(factor_input)
    print('end model predict, time use: ', time.time() - model_sstime)

    final_score = pred_raw_df['stack']

    # rule blacklist
    rule_blacklist = get_arrow_black_list(factor_score[['factor_1', 'factor_openPct', 'factor_s1_high_to_limit', 'factor_s2_high_to_limit']], inst.__data__['rule_blacklist_df'])
    rule_filtered = [x for x in rule_blacklist if x in final_score[final_score > threshold].index.get_level_values(level = 1)]
    if len(rule_filtered) > 0:
        print('rule blacklist: ', rule_blacklist)
        send_link('rule blacklist: ' + str(rule_blacklist))
        pd.DataFrame(rule_filtered).to_csv(os.path.join(factor_savepath, '%s_rule_blacklist.csv' % str_date), index = False)
    final_score = final_score.drop(rule_blacklist, errors = 'ignore')

    # pred_raw_df.to_pickle('./model_value.pkl')
    buy_plan = final_score[final_score > threshold].nlargest(daily_max_num).reset_index().Ticker.to_frame()
    # save result
    for path in [plan_savepath, model_value_path, factor_savepath]:
        if not os.path.exists(path):
            os.makedirs(path)
    str_date = inst.__trade_date__.strftime('%Y%m%d')
    if len(buy_plan) > daily_min_num:
        buy_plan.to_csv(os.path.join(plan_savepath, '%s.csv' % str_date), index = False)
        buy_list = ' '.join(buy_plan.Ticker.tolist())
        send_link(f'{str_date} trade plan: {len(buy_plan)} stocks    {buy_list}')
        print(f'{str_date} trade plan: {len(buy_plan)} stocks    {buy_list}')
    else:
        buy_plan.to_csv(os.path.join(plan_savepath, '%s_no_plan.csv' % str_date), index = False)
        buy_list = ' '.join(buy_plan.Ticker.tolist())
        send_link(f'{str_date} no trade plan: {len(buy_plan)} stocks    {buy_list}')
        print(f'{str_date} no trade plan: {len(buy_plan)} stocks    {buy_list}')

    print('start save result')
    pred_raw_df.reset_index(level = 0, drop = True).to_csv(os.path.join(model_value_path, '%s.csv' % str_date))

    factor_score.reset_index(level = 0, drop = True).to_csv(os.path.join(factor_savepath, '%s.csv' % str_date))
    # IO.pd_hdf5_writer(factor_score, rawfactor_path, dataset = rawfactor_dataset, append = True, data_columns=['dt', 'Ticker'])
    # IO.pd_hdf5_writer(factor_clip, histfactor_path, dataset = histfactor_dataset, append = True, data_columns=['dt', 'Ticker'])
    # IO.pd_hdf5_writer(factor_input, factorinput_path, dataset = factorinput_dataset, append = True, data_columns=['dt', 'Ticker'])

    del(inst)
    return 

# factor_score['factor_order_bo_m'] = factor_score['factor_order_bo_buym'] + factor_score['factor_order_bo_sellm']
# factor_score['factor_order_so_m'] = factor_score['factor_order_so_buym'] + factor_score['factor_order_so_sellm']
# factor_score['factor_412']=factor_score['factor_order_bo_buym'] / (factor_score['factor_order_bo_buym'] + factor_score['factor_order_so_buym'])
# factor_score['factor_413']=factor_score['factor_order_bo_sellm'] / (factor_score['factor_order_bo_sellm'] + factor_score['factor_order_so_sellm'])
# factor_score['factor_414']=factor_score['factor_order_bo10w_buym'] / factor_score['factor_order_bo_buym']
# factor_score['factor_415']=factor_score['factor_order_bo10w_sellm'] / factor_score['factor_order_bo_sellm']
# factor_score['factor_416']=factor_score['factor_order_so10w_buym'] / factor_score['factor_order_so_buym']
# factor_score['factor_417']=factor_score['factor_order_so10w_sellm'] / factor_score['factor_order_so_sellm']
# factor_score['factor_418']=factor_score['factor_order_bo10w_buym'] / factor_score['factor_order_bo10w_sellm']
# factor_score['factor_419']=factor_score['factor_order_so10w_buym'] / factor_score['factor_order_so10w_sellm']
# factor_score['factor_420']=factor_score['factor_order_bo_buym'] / factor_score['factor_order_bo_sellm']
# factor_score['factor_421']=factor_score['factor_order_so_buym'] / factor_score['factor_order_so_sellm']
# factor_score['factor_order_bo_c']=factor_score['factor_order_bo_buyc'] + factor_score['factor_order_bo_sellc']
# factor_score['factor_order_so_c']=factor_score['factor_order_so_buyc'] + factor_score['factor_order_so_sellc']
# factor_score['factor_422']=factor_score['factor_order_bo_buym'] / factor_score['factor_order_bo_buyc']
# factor_score['factor_423']=factor_score['factor_order_bo_sellm'] / factor_score['factor_order_bo_sellc']
# factor_score['factor_424']=factor_score['factor_order_so_buym'] / factor_score['factor_order_so_buyc']
# factor_score['factor_425']=factor_score['factor_order_so_sellm'] / factor_score['factor_order_so_sellc']
# factor_score['factor_426']=factor_score['factor_422'] / factor_score['factor_423'] - 1
# factor_score['factor_427']=factor_score['factor_424'] / factor_score['factor_425'] - 1
# factor_score['factor_tran_bo_m']=factor_score['factor_tran_bo_buym'] + factor_score['factor_tran_bo_sellm']
# factor_score['factor_tran_so_m']=factor_score['factor_tran_so_buym'] + factor_score['factor_tran_so_sellm']
# factor_score['factor_428']=factor_score['factor_tran_bo_buym'] / (factor_score['factor_tran_bo_buym'] + factor_score['factor_tran_so_buym'])
# factor_score['factor_429']=factor_score['factor_tran_bo_sellm'] / (factor_score['factor_tran_bo_sellm'] + factor_score['factor_tran_so_sellm'])
# factor_score['factor_430']=factor_score['factor_tran_bo10w_buym'] / factor_score['factor_tran_bo_buym']
# factor_score['factor_431']=factor_score['factor_tran_bo10w_sellm'] / factor_score['factor_tran_bo_sellm']
# factor_score['factor_432']=factor_score['factor_tran_so10w_buym'] / factor_score['factor_tran_so_buym']
# factor_score['factor_433']=factor_score['factor_tran_so10w_sellm'] / factor_score['factor_tran_so_sellm']
# factor_score['factor_434']=factor_score['factor_tran_bo10w_buym'] / factor_score['factor_tran_bo10w_sellm']
# factor_score['factor_435']=factor_score['factor_tran_so10w_buym'] / factor_score['factor_tran_so10w_sellm']
# factor_score['factor_436']=factor_score['factor_tran_bo_buym'] / factor_score['factor_tran_bo_sellm']
# factor_score['factor_437']=factor_score['factor_tran_so_buym'] / factor_score['factor_tran_so_sellm']
# factor_score['factor_438']=factor_score['factor_order_bo10w_buym'] / factor_score['factor_order_bo10w_buym_tranm']
# factor_score['factor_439']=factor_score['factor_order_bo10w_sellm'] / factor_score['factor_order_bo10w_sellm_tranm']
# factor_score['factor_440']=factor_score['factor_order_bo_buym'] / factor_score['factor_order_bo_buym_tranm']
# factor_score['factor_441']=factor_score['factor_order_bo_sellm'] / factor_score['factor_order_bo_sellm_tranm']
# factor_score['factor_442']=factor_score['factor_order_so10w_buym'] / factor_score['factor_order_so10w_buym_tranm']
# factor_score['factor_443']=factor_score['factor_order_so10w_sellm'] / factor_score['factor_order_so10w_sellm_tranm']
# factor_score['factor_444']=factor_score['factor_order_so_buym'] / factor_score['factor_order_so_buym_tranm']
# factor_score['factor_445']=factor_score['factor_order_so_sellm'] / factor_score['factor_order_so_sellm_tranm'] 

# factor_score['factor_htc_m'] = factor_score['factor_htc_buym'] + factor_score['factor_htc_sellm']
# factor_score['factor_htc_10wm'] = factor_score['factor_htc_buy10wm'] + factor_score['factor_htc_sell10wm']
# factor_score['factor_htc_c'] = factor_score['factor_htc_buyc'] + factor_score['factor_htc_sellc']
# factor_score['factor_htc_10wc'] = factor_score['factor_htc_buy10wc'] + factor_score['factor_htc_sell10wc']
# factor_score['factor_500'] = factor_score['factor_htc_m'] / factor_score['factor_amount_t_1']
# factor_score['factor_501'] = factor_score['factor_htc_sellm'] / factor_score['factor_htc_m']
# factor_score['factor_502'] = factor_score['factor_htc_10wm'] / factor_score['factor_amount_t_1']
# factor_score['factor_503'] = factor_score['factor_htc_sell10wm'] / factor_score['factor_htc_10wm']
# factor_score['factor_504'] = factor_score['factor_htc_sellc'] / factor_score['factor_htc_c']
# factor_score['factor_505'] = factor_score['factor_htc_sell10wc'] / factor_score['factor_htc_10wc']
# factor_score['factor_506'] = factor_score['factor_htc_order_buy10wm'] / factor_score['factor_htc_order_buym']
# factor_score['factor_507'] = factor_score['factor_htc_order_sell10wm'] / factor_score['factor_htc_order_sellm']
# factor_score['factor_508'] = factor_score['factor_htc_buyc'] / factor_score['factor_htc_order_buyc']
# factor_score['factor_509'] = factor_score['factor_htc_sellc'] / factor_score['factor_htc_order_sellc']
# factor_score['factor_510'] = factor_score['factor_htc_buy10wc'] / factor_score['factor_htc_order_buy10wc']
# factor_score['factor_511'] = factor_score['factor_htc_sell10wc'] / factor_score['factor_htc_order_sell10wc']
# factor_score['factor_512'] = factor_score['factor_htc_order_sellc'] / (factor_score['factor_htc_order_sellc'] + factor_score['factor_htc_order_buyc'])
# factor_score['factor_513'] = factor_score['factor_htc_order_sell10wc'] / (factor_score['factor_htc_order_sell10wc'] + factor_score['factor_htc_order_buy10wc'])
# factor_score['factor_514'] = factor_score['factor_htc_order_buym_tranm'] / factor_score['factor_htc_order_buym']
# factor_score['factor_515'] = factor_score['factor_htc_order_sellm_tranm'] / factor_score['factor_htc_order_sellm']
# factor_score['factor_516'] = factor_score['factor_htc_order_buy10wm_tranm'] / factor_score['factor_htc_order_buy10wm']
# factor_score['factor_517'] = factor_score['factor_htc_order_sell10wm_tranm'] / factor_score['factor_htc_order_sell10wm']
# factor_score['factor_518'] = factor_score['factor_htc_order_buym_market_tranm'] / factor_score['factor_htc_order_buym']
# factor_score['factor_519'] = factor_score['factor_htc_order_sellm_market_tranm'] / factor_score['factor_htc_order_sellm']
# factor_score['factor_520'] = factor_score['factor_htc_order_buy10wm_market_tranm'] / factor_score['factor_htc_order_buy10wm']
# factor_score['factor_521'] = factor_score['factor_htc_order_sell10wm_market_tranm'] / factor_score['factor_htc_order_sell10wm']
# factor_score['factor_522'] = factor_score['factor_htc_order_buym_market_tranm'] / factor_score['factor_htc_order_buym_tranm']
# factor_score['factor_523'] = factor_score['factor_htc_order_sellm_market_tranm'] / factor_score['factor_htc_order_sellm_tranm']
# factor_score['factor_524'] = factor_score['factor_htc_order_buy10wm_market_tranm'] / factor_score['factor_htc_order_buy10wm_tranm']
# factor_score['factor_525'] = factor_score['factor_htc_order_sell10wm_market_tranm'] / factor_score['factor_htc_order_sell10wm_tranm']
# factor_score['factor_526'] = factor_score['factor_htc_cancel_buym'] / factor_score['factor_htc_order_buym']
# factor_score['factor_527'] = factor_score['factor_htc_cancel_sellm'] / factor_score['factor_htc_order_sellm']
# factor_score['factor_528'] = factor_score['factor_htc_cancel_buy10wm'] / factor_score['factor_htc_order_buy10wm']
# factor_score['factor_529'] = factor_score['factor_htc_cancel_sell10wm'] / factor_score['factor_htc_order_sell10wm']
# factor_score['factor_530'] = factor_score['factor_htc_cancel_buym'] / factor_score['factor_htc_buym']
# factor_score['factor_531'] = factor_score['factor_htc_cancel_sellm'] / factor_score['factor_htc_sellm']
# factor_score['factor_532'] = factor_score['factor_htc_cancel_buy10wm'] / factor_score['factor_htc_buy10wm']
# factor_score['factor_533'] = factor_score['factor_htc_cancel_sell10wm'] / factor_score['factor_htc_sell10wm']
# factor_score['factor_534'] = factor_score['factor_htc_cancel_buyc'] / factor_score['factor_htc_order_buyc']
# factor_score['factor_535'] = factor_score['factor_htc_cancel_sellc'] / factor_score['factor_htc_order_sellc']
# factor_score['factor_oth_m'] = factor_score['factor_oth_buym'] + factor_score['factor_oth_sellm']
# factor_score['factor_oth_10wm'] = factor_score['factor_oth_buy10wm'] + factor_score['factor_oth_sell10wm']
# factor_score['factor_oth_c'] = factor_score['factor_oth_buyc'] + factor_score['factor_oth_sellc']
# factor_score['factor_oth_10wc'] = factor_score['factor_oth_buy10wc'] + factor_score['factor_oth_sell10wc']
# factor_score['factor_536'] = factor_score['factor_oth_m'] / factor_score['factor_amount_t_1']
# factor_score['factor_537'] = factor_score['factor_oth_sellm'] / factor_score['factor_oth_m']
# factor_score['factor_538'] = factor_score['factor_oth_10wm'] / factor_score['factor_amount_t_1']
# factor_score['factor_539'] = factor_score['factor_oth_sell10wm'] / factor_score['factor_oth_10wm']
# factor_score['factor_540'] = factor_score['factor_oth_sellc'] / factor_score['factor_oth_c']
# factor_score['factor_541'] = factor_score['factor_oth_sell10wc'] / factor_score['factor_oth_10wc']
# factor_score['factor_542'] = factor_score['factor_oth_order_buy10wm'] / factor_score['factor_oth_order_buym']
# factor_score['factor_543'] = factor_score['factor_oth_order_sell10wm'] / factor_score['factor_oth_order_sellm']
# factor_score['factor_544'] = factor_score['factor_oth_buyc'] / factor_score['factor_oth_order_buyc']
# factor_score['factor_545'] = factor_score['factor_oth_sellc'] / factor_score['factor_oth_order_sellc']
# factor_score['factor_546'] = factor_score['factor_oth_buy10wc'] / factor_score['factor_oth_order_buy10wc']
# factor_score['factor_547'] = factor_score['factor_oth_sell10wc'] / factor_score['factor_oth_order_sell10wc']
# factor_score['factor_548'] = factor_score['factor_oth_order_sellc'] / (factor_score['factor_oth_order_sellc'] + factor_score['factor_oth_order_buyc'])
# factor_score['factor_549'] = factor_score['factor_oth_order_sell10wc'] / (factor_score['factor_oth_order_sell10wc'] + factor_score['factor_oth_order_buy10wc'])
# factor_score['factor_550'] = factor_score['factor_oth_order_buym_tranm'] / factor_score['factor_oth_order_buym']
# factor_score['factor_551'] = factor_score['factor_oth_order_sellm_tranm'] / factor_score['factor_oth_order_sellm']
# factor_score['factor_552'] = factor_score['factor_oth_order_buy10wm_tranm'] / factor_score['factor_oth_order_buy10wm']
# factor_score['factor_553'] = factor_score['factor_oth_order_sell10wm_tranm'] / factor_score['factor_oth_order_sell10wm']
# factor_score['factor_554'] = factor_score['factor_oth_order_buym_market_tranm'] / factor_score['factor_oth_order_buym']
# factor_score['factor_555'] = factor_score['factor_oth_order_sellm_market_tranm'] / factor_score['factor_oth_order_sellm']
# factor_score['factor_556'] = factor_score['factor_oth_order_buy10wm_market_tranm'] / factor_score['factor_oth_order_buy10wm']
# factor_score['factor_557'] = factor_score['factor_oth_order_sell10wm_market_tranm'] / factor_score['factor_oth_order_sell10wm']
# factor_score['factor_558'] = factor_score['factor_oth_order_buym_market_tranm'] / factor_score['factor_oth_order_buym_tranm']
# factor_score['factor_559'] = factor_score['factor_oth_order_sellm_market_tranm'] / factor_score['factor_oth_order_sellm_tranm']
# factor_score['factor_560'] = factor_score['factor_oth_order_buy10wm_market_tranm'] / factor_score['factor_oth_order_buy10wm_tranm']
# factor_score['factor_561'] = factor_score['factor_oth_order_sell10wm_market_tranm'] / factor_score['factor_oth_order_sell10wm_tranm']
# factor_score['factor_562'] = factor_score['factor_oth_cancel_buym'] / factor_score['factor_oth_order_buym']
# factor_score['factor_563'] = factor_score['factor_oth_cancel_sellm'] / factor_score['factor_oth_order_sellm']
# factor_score['factor_564'] = factor_score['factor_oth_cancel_buy10wm'] / factor_score['factor_oth_order_buy10wm']
# factor_score['factor_565'] = factor_score['factor_oth_cancel_sell10wm'] / factor_score['factor_oth_order_sell10wm']
# factor_score['factor_566'] = factor_score['factor_oth_cancel_buym'] / factor_score['factor_oth_buym']
# factor_score['factor_567'] = factor_score['factor_oth_cancel_sellm'] / factor_score['factor_oth_sellm']
# factor_score['factor_568'] = factor_score['factor_oth_cancel_buy10wm'] / factor_score['factor_oth_buy10wm']
# factor_score['factor_569'] = factor_score['factor_oth_cancel_sell10wm'] / factor_score['factor_oth_sell10wm']
# factor_score['factor_570'] = factor_score['factor_oth_cancel_buyc'] / factor_score['factor_oth_order_buyc']
# factor_score['factor_571'] = factor_score['factor_oth_cancel_sellc'] / factor_score['factor_oth_order_sellc']
# factor_score['factor_572'] = factor_score['factor_htc_buym'] / factor_score['factor_oth_buym']
# factor_score['factor_573'] = factor_score['factor_htc_sellm'] / factor_score['factor_oth_sellm']
# factor_score['factor_574'] = factor_score['factor_htc_buy10wm'] / factor_score['factor_oth_buy10wm']
# factor_score['factor_575'] = factor_score['factor_htc_sell10wm'] / factor_score['factor_oth_sell10wm']
# factor_score['factor_576'] = factor_score['factor_htc_buyc'] / factor_score['factor_oth_buyc']
# factor_score['factor_577'] = factor_score['factor_htc_sellc'] / factor_score['factor_oth_sellc']
# factor_score['factor_578'] = factor_score['factor_htc_buy10wc'] / factor_score['factor_oth_buy10wc']
# factor_score['factor_579'] = factor_score['factor_htc_sell10wc'] / factor_score['factor_oth_sell10wc']
# factor_score['factor_580'] = factor_score['factor_htc_order_buym'] / factor_score['factor_oth_order_buym']
# factor_score['factor_581'] = factor_score['factor_htc_order_sellm'] / factor_score['factor_oth_order_sellm']
# factor_score['factor_582'] = factor_score['factor_htc_order_buy10wm'] / factor_score['factor_oth_order_buy10wm']
# factor_score['factor_583'] = factor_score['factor_htc_order_sell10wm'] / factor_score['factor_oth_order_sell10wm']
# factor_score['factor_584'] = factor_score['factor_htc_order_buyc'] / factor_score['factor_oth_order_buyc']
# factor_score['factor_585'] = factor_score['factor_htc_order_sellc'] / factor_score['factor_oth_order_sellc']
# factor_score['factor_586'] = factor_score['factor_htc_order_buy10wc'] / factor_score['factor_oth_order_buy10wc']
# factor_score['factor_587'] = factor_score['factor_htc_order_sell10wc'] / factor_score['factor_oth_order_sell10wc']
# factor_score['factor_588'] = factor_score['factor_htc_order_buym_tranm'] / factor_score['factor_oth_order_buym_tranm']
# factor_score['factor_589'] = factor_score['factor_htc_order_sellm_tranm'] / factor_score['factor_oth_order_sellm_tranm']
# factor_score['factor_590'] = factor_score['factor_htc_order_buy10wm_tranm'] / factor_score['factor_oth_order_buy10wm_tranm']
# factor_score['factor_591'] = factor_score['factor_htc_order_sell10wm_tranm'] / factor_score['factor_oth_order_sell10wm_tranm']
# factor_score['factor_592'] = factor_score['factor_htc_order_buym_market_tranm'] / factor_score['factor_oth_order_buym_market_tranm']
# factor_score['factor_593'] = factor_score['factor_htc_order_sellm_market_tranm'] / factor_score['factor_oth_order_sellm_market_tranm']
# factor_score['factor_594'] = factor_score['factor_htc_order_buy10wm_market_tranm'] / factor_score['factor_oth_order_buy10wm_market_tranm']
# factor_score['factor_595'] = factor_score['factor_htc_order_sell10wm_market_tranm'] / factor_score['factor_oth_order_sell10wm_market_tranm']
# factor_score['factor_596'] = factor_score['factor_htc_cancel_buym'] / factor_score['factor_oth_cancel_buym']
# factor_score['factor_597'] = factor_score['factor_htc_cancel_sellm'] / factor_score['factor_oth_cancel_sellm']
# factor_score['factor_598'] = factor_score['factor_htc_cancel_buy10wm'] / factor_score['factor_oth_cancel_buy10wm']
# factor_score['factor_599'] = factor_score['factor_htc_cancel_sell10wm'] / factor_score['factor_oth_cancel_sell10wm']
# factor_score['factor_600'] = factor_score['factor_htc_cancel_buyc'] / factor_score['factor_oth_cancel_buyc']
# factor_score['factor_601'] = factor_score['factor_htc_cancel_sellc'] / factor_score['factor_oth_cancel_sellc']
# factor_score['factor_602'] = factor_score['factor_htc_tick_numratio'] / factor_score['factor_oth_tick_numratio']
# factor_score['factor_603'] = factor_score['factor_htc_ratio'] / factor_score['factor_oth_ratio']
# factor_score['factor_604'] = factor_score['factor_htc_abspath_ratio'] / factor_score['factor_oth_abspath_ratio']