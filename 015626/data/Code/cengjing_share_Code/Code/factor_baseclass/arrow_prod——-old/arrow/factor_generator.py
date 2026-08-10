from arrow.data_center import HotData
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
import ftplib
from shutil import copyfile
from collections import Counter

class FactorGenerator:
    __data__ = None
    __mdconstant__ = dict()
    __trade_date__ = None

    def __init__(self, data_mode = None, required_columns=None, savepath=factor_savepath):
        assert data_mode in [None, 't', 't-1']
        self.data_mode = data_mode
        self.required_columns = required_columns
        self.savepath = savepath

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
            del(inst.__data__['histfactor'], inst.__data__['dummy'], inst.__data__['factor_clip_scope'], inst.__data__['mad_startdate'])
            diller(os.path.join(save_path, 'history.pkl'), (inst.__trade_date__, inst.__data__, inst.__mdconstant__))
            diller(os.path.join(save_path, 'histfactor_dummy_scope.pkl'), histfactor)
        elif data_kind == 'data':
            diller(os.path.join(save_path, 'history.pkl'), (inst.__trade_date__, inst.__data__, inst.__mdconstant__))
        elif data_kind == 'factor':
            diller(os.path.join(save_path, 'histfactor_dummy_scope.pkl'), inst.__data__)

    @classmethod
    def load_hist_data(inst, trade_date=None):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = str_date_parser(trade_date)
        save_path = os.path.join(history_root, trade_date.strftime('%Y%m%d'))
        _trade_date, _data, _mdconstant = diller(os.path.join(save_path, 'history.pkl'))
        _histfactor = diller(os.path.join(save_path, 'histfactor_dummy_scope.pkl'))
        assert _trade_date == trade_date
        _data.update(_histfactor)
        inst.__trade_date__ = _trade_date
        inst.__data__ = _data
        inst.__mdconstant__ = _mdconstant

    @classmethod
    def merge_hot_data(inst, trade_date=None, factor_mode = None):
        if trade_date is None:
            trade_date =  pd.Timestamp.now().date()
        trade_date = str_date_parser(trade_date)
        # load history data
        inst.load_hist_data(trade_date=trade_date)
        hist_data = inst.__data__
        if factor_mode == 't-1':
            universe = set(hist_data['universe'])
            for k in name_dict.keys():
                universe = universe & set(hist_data[k].keys())
            prod_data = {}
            prod_data['universe'] = sorted(list(universe))
            for k in name_dict.keys():
                stk_data = {}
                for stk in universe:
                    stk_data[stk] = hist_data[k][stk]
                prod_data[k] = stk_data
            prod_data['histfactor'] = hist_data['histfactor']
            prod_data['dummy'] = hist_data['dummy']
            prod_data['factor_clip_scope'] = hist_data['factor_clip_scope']
            prod_data['mad_startdate'] = hist_data['mad_startdate']
            inst.__data__ = prod_data
            return
        # retrieve hot data
        hd = HotData(trade_date)
        hot_data = hd.get_all()

        # 处理异常数据
        universe = set(hist_data['universe'])
        for k in name_dict.keys():
            universe = universe & set(hist_data[k].keys()) & set(hot_data[k].keys()) 
        prod_data = {}
        prod_data['universe'] = sorted(list(universe))
        for k in name_dict.keys():
            stk_data = {}
            for stk in universe:
                stk_data[stk] = pd.concat([hist_data[k][stk], hot_data[k][stk]], axis = 0)
            prod_data[k] = stk_data
        prod_data['histfactor'] = hist_data['histfactor']
        prod_data['dummy'] = hist_data['dummy']
        prod_data['factor_clip_scope'] = hist_data['factor_clip_scope']
        prod_data['mad_startdate'] = hist_data['mad_startdate']

        if factor_mode == 't':
            save_path = os.path.join(history_root, trade_date.strftime('%Y%m%d'))
            _factor_t_1 = diller(os.path.join(save_path, 'factor_t_1.pkl'))
            prod_data.update(_factor_t_1)
        inst.__data__ = prod_data

    def slicer(self):
        data = {col: self.__data__[col].copy() for col in self.required_columns}
        handle_cols = list(set(name_dict.keys()) & set(self.required_columns))
        if self.data_mode == 't':
            trade_date = self.__trade_date__.strftime('%Y%m%d')
            for col in handle_cols:
                for stk in data[col].keys():
                    data[col][stk] = data[col][stk].set_index('dt').loc[trade_date].reset_index()
        elif self.data_mode == 't-1':
            pass
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


def prepare_history(trade_date=None, hisdays=0):
    inst = FactorGenerator()
    inst.prepare_hist_data(trade_date=trade_date, hisdays=hisdays)
    inst.dump_hist_data()


def get_factors(subcls):
    # print('calculating: ', subcls.__name__)
    try:
        return subcls().__callback__()
    except Exception as e:
        print(subcls.__name__, e)

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


def executor(trade_date=None, max_workers=12, tag='factors', factor_mode = 't'):
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
    inst.merge_hot_data(trade_date=trade_date, factor_mode = factor_mode)
    print('universe count: %d' % len(inst.__data__['universe']), 'total factor num: %d' % len(subclass_list))
    # if len(inst.__data__['universe']) > 200:
    #     print('univ num bigger than 200, calculate this day later !!!')
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
    if factor_mode == 't':
        factor_score = factor_score.join(inst.__data__['factor_t_1'])

    factor_score = factor_score[inst.__data__['factor_clip_scope']['down'].index.tolist()]
    factor_clip = np_clip(factor_score, inst.__data__['factor_clip_scope']['down'], inst.__data__['factor_clip_scope']['up'])

    factor_all = inst.__data__['histfactor'].append(factor_clip).sort_index()
    factor_prod = factor_all[factor_final_list]

    flist = [inst.__data__['dummy']]
    mad_dict = inst.__data__['mad_startdate']
    for x in mad_dict.keys():
        flist.append(mad(factor_prod.loc[mad_dict[x]:]).loc[inst.__trade_date__:].add_suffix(f'_z{x}'))

    factor_input = pd.concat(flist, axis = 1, join = 'inner').fillna(0)

    model_sstime = time.time()
    print('start model predict')
    pred_raw_df = model_predict(factor_input)
    print('end model predict, time use: ', time.time() - model_sstime)

    final_score = pred_raw_df['stack']

    del(inst)
    return pred_raw_df

  