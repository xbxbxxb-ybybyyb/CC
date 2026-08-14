import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.getData import get_quarter_1factor, get_ttm_quarter, \
    get_single_quarter, fill_quarter2daily_by_issue_date, get_qoq
from dataApi.tradeDate import get_date_range, get_pre_trade_date, \
    get_recent_trade_date
from dataApi.stockList import trans_windcode2int
from dataApi.dividend import getEXRightDividend
from dataApi.sendInfo import send_message
from HFfactor.MinFactorSuper.Utility.LoadBigData import \
    get_minute_data, get_daily_data, get_con_data
from HFfactor.MinFactorSuper.Utility.Parallel import multidask
from HFfactor.MinFactorSuper.RealTime.UsefulList import \
    MaterialList, DesampleMethod, MaterialDistAdjust
from HFfactor.MinFactorSuper.RealTime.Desample import ReduceMaterial
from HFfactor.MinFactorSuper.RealTime.Operators import *
import pandas as pd
import numpy as np
import bottleneck
import shutil
import time
import os
import gc
import re


class MakeTmrMaterial(object):

    def __init__(self, end_date=None, factor_list=None, desample_factor_list=None,
                 sleep=0, offline_day_offset=79, use_days=40, threads=24,
                 root_path='/data/group/800442/800319/strategy_HFfactor/'):
        gc.collect()
        time.sleep(sleep)
        t = time.time()
        self.offline_day_offset = offline_day_offset
        self.use_days = use_days
        self.end_date = get_recent_trade_date(end_date)
        self.start_date = get_pre_trade_date(self.end_date, offline_day_offset)
        self.date_list = get_date_range(self.start_date, self.end_date)
        self._date = get_pre_trade_date(end_date, -1)
        self.root_path = root_path
        self.make_fold()
        self.set_code_list()
        self.set_factor_list(factor_list, desample_factor_list)
        self.Data = {}
        self.Data['MV'] = {'mean': {}, 'std': {}}
        self.Data['DpMV'] = {'mean': {}, 'std': {}}

        multidask('导入历史分钟数据', [
            [self.calc_min_data, ('close', 'close')],
            [self.calc_min_data, ('open', 'opn')],
            [self.calc_min_data, ('high', 'high')],
            [self.calc_min_data, ('low', 'low')],
            [self.calc_min_data, ('volume', 'vol')],
            [self.calc_min_data, ('amt', 'adj_amt')],
            [self.calc_min_data, ('close_adj', 'adj_close')],
            [self.calc_min_data, ('open_adj', 'adj_opn')],
            [self.calc_min_data, ('high_adj', 'adj_high')],
            [self.calc_min_data, ('low_adj', 'adj_low')],
            [self.calc_min_data, ('volume_adj', 'adj_vol')],
            [self.calc_min_data, ('buytradenum', 'num_buy')],
            [self.calc_min_data, ('selltradenum', 'num_sell')],
            [self.calc_min_data, ('numtrade', 'num_total')],
            [self.calc_min_data, ('accamountbuy', 'accamountbuy')],
            [self.calc_min_data, ('accamountsell', 'accamountsell')],
            [self.calc_min_data, ('activebuyorderamt', 'activebuyorderamt')],
            [self.calc_min_data, ('activebuyordervol', 'activebuyordervol')],
            [self.calc_min_data, ('activesellorderamt', 'activesellorderamt')],
            [self.calc_min_data, ('activesellordervol', 'activesellordervol')],
            [self.calc_min_data, ('buyorderamt', 'buyorderamt')],
            [self.calc_min_data, ('buyordercanceledamt', 'buyordercanceledamt')],
            [self.calc_min_data, ('buyordercanceledvol', 'buyordercanceledvol')],
            [self.calc_min_data, ('buyordervol', 'buyordervol')],
            [self.calc_min_data, ('buytradeamt', 'buytradeamt')],
            [self.calc_min_data, ('buytradevol', 'buytradevol')],
            [self.calc_min_data, ('passivebuyorderamt', 'passivebuyorderamt')],
            [self.calc_min_data, ('passivebuyordervol', 'passivebuyordervol')],
            [self.calc_min_data, ('passivesellorderamt', 'passivesellorderamt')],
            [self.calc_min_data, ('passivesellordervol', 'passivesellordervol')],
            [self.calc_min_data, ('sellorderamt', 'sellorderamt')],
            [self.calc_min_data, ('sellordercanceledamt', 'sellordercanceledamt')],
            [self.calc_min_data, ('sellordercanceledvol', 'sellordercanceledvol')],
            [self.calc_min_data, ('sellordervol', 'sellordervol')],
            [self.calc_min_data, ('selltradeamt', 'selltradeamt')],
            [self.calc_min_data, ('selltradevol', 'selltradevol')],
        ])

        # 日频数据
        self.Data['_free_float_shares'], self.Data['_free_float_shares_tmr'] = get_daily_data(
            'free_float_shares', self.date_list, self.code_list)
        self.Data['_total_shares'], self.Data['_total_shares_tmr'] = get_daily_data(
            'total_shares', self.date_list, self.code_list)
        self.Data['_close'], self.Data['_close_tmr'] = get_daily_data(
            'close', self.date_list, self.code_list)
        self.Data['_pre_close'] = get_daily_data(
            'pre_close', self.date_list, self.code_list, lag=False, ffill=False)
        self.Data['_adj_close'] = get_minute_data(
            'close_adj', [get_pre_trade_date(self.date_list[0])], self.code_list)[-1, -1:]

        self.Data['_dividend'] = getEXRightDividend()
        self.Data['_payout_ratio'] = self.Data['_dividend'].pivot(
            'date', 'code', 'payoutRatio')
        self.Data['_payout_ratio_tmr'] = self.Data['_payout_ratio'].reindex(
            [get_pre_trade_date(self.date_list[-1], -1)], self.code_list).fillna(0).values
        self.Data['_payout_ratio'] = self.Data['_payout_ratio'].reindex(
            self.date_list, self.code_list).fillna(0).values[:, None]

        self.Data['_receive_ratio'] = self.Data['_dividend'].pivot(
            'date', 'code', 'receiveRatio')
        self.Data['_receive_ratio_tmr'] = self.Data['_receive_ratio'].reindex(
            [get_pre_trade_date(self.date_list[-1], -1)], self.code_list).fillna(0).values
        self.Data['_receive_ratio'] = self.Data['_receive_ratio'].reindex(
            self.date_list, self.code_list).fillna(0).values[:, None]

        self.Data['_share_ratio'] = self.Data['_dividend'].pivot(
            'date', 'code', 'shareRatio')
        self.Data['_share_ratio_tmr'] = self.Data['_share_ratio'].reindex(
            [get_pre_trade_date(self.date_list[-1], -1)], self.code_list).fillna(0).values
        self.Data['_share_ratio'] = self.Data['_share_ratio'].reindex(
            self.date_list, self.code_list).fillna(0).values[:, None]

        self.Data['_participation'] = np.where(self.Data['_share_ratio'] > 0, (
                self.Data['_close'] - self.Data['_pre_close'] - self.Data['_payout_ratio']) / (
                                                       self.Data['_pre_close'] * self.Data['_share_ratio'] - self.Data[
                                                   '_receive_ratio']), 1)
        self.Data['_share_adjust'] = 1 + self.Data['_share_ratio'] * self.Data['_participation']
        self.Data['_share_adjust'][~ np.isfinite(self.Data['_share_adjust'])] = 1
        self.Data['_free_float_shares'] *= self.Data['_share_adjust']
        self.Data['_total_shares'] *= self.Data['_share_adjust']

        # 财报数据
        self.Data['profit'] = fill_quarter2daily_by_issue_date(get_single_quarter(
            'net_profit_after_ded_nr_lp')).ffill()
        self.Data['profit_tmr'] = self.Data['profit'].loc[self.date_list[-1]].reindex(self.code_list).values[None, :]
        self.Data['profit'] = self.Data['profit'].shift().reindex(self.date_list, self.code_list).values[:, None, :]

        self.Data['rtdearn'] = fill_quarter2daily_by_issue_date(
            get_quarter_1factor('surplus_rsrv').add(get_quarter_1factor(
                'undistributed_profit_b'), fill_value=0).sub(get_quarter_1factor('less_tsy_stk'), fill_value=0)).ffill()
        self.Data['rtdearn_tmr'] = self.Data['rtdearn'].loc[self.date_list[-1]].reindex(self.code_list).values[None, :]
        self.Data['rtdearn'] = self.Data['rtdearn'].shift().reindex(self.date_list, self.code_list).values[:, None, :]

        self.Data['ocf'] = fill_quarter2daily_by_issue_date(get_ttm_quarter('net_cash_flows_oper_act')).ffill()
        self.Data['ocf_tmr'] = self.Data['ocf'].loc[self.date_list[-1]].reindex(self.code_list).values[None, :]
        self.Data['ocf'] = self.Data['ocf'].shift().reindex(self.date_list, self.code_list).values[:, None, :]

        self.Data['growth'] = fill_quarter2daily_by_issue_date(
            get_qoq(get_ttm_quarter('oper_profit').add(get_ttm_quarter(
                'less_selling_dist_exp'), fill_value=0).add(get_ttm_quarter('less_gerl_admin_exp'), fill_value=0).add(
                get_ttm_quarter('less_fin_exp'), fill_value=0).add(get_ttm_quarter(
                'less_impair_loss_assets'), fill_value=0))).ffill()
        self.Data['growth_tmr'] = self.Data['growth'].loc[self.date_list[-1]].reindex(self.code_list).values[None, :]
        self.Data['growth'] = self.Data['growth'].shift().reindex(self.date_list, self.code_list).values[:, None, :]

        # 预期数据
        self.Data['f_eps'], self.Data['f_eps_tmr'] = get_con_data('cfs_c1', self.date_list, self.code_list, 2)
        self.Data['f_profit'], self.Data['f_profit_tmr'] = get_con_data('cfc2s_c13', self.date_list, self.code_list)
        self.Data['f_equity'], self.Data['f_equity_tmr'] = get_con_data('cfc3s_cgb', self.date_list, self.code_list)

        # 财务辅助
        self.Data['_pe_hist'] = self.Data['profit'] / self.Data['_total_shares'] / 1e4
        self.Data['_pb_hist'] = self.Data['rtdearn'] / self.Data['_total_shares'] / 1e4
        self.Data['_pcf_hist'] = self.Data['ocf'] / self.Data['_total_shares'] / 1e4
        self.Data['_peg_hist'] = self.Data['profit'] * self.Data['growth'] / self.Data['_total_shares'] / 1e4
        self.Data['_pe_f2'] = self.Data['f_eps']
        self.Data['_pe_f1'] = self.Data['f_profit'] / self.Data['_total_shares']
        self.Data['_pb_f1'] = self.Data['f_equity'] / self.Data['_total_shares']

        # 基础处理
        self.Data['ret_close'] = self.Data['adj_close'].reshape(-1, self.Data['adj_close'].shape[2])
        self.Data['ret_close_lag'] = np.empty_like(self.Data['ret_close'])
        self.Data['ret_close_lag'][0] = self.Data['_adj_close']
        self.Data['ret_close_lag'][1:] = self.Data['ret_close'][:-1]
        self.Data['ret_close'] = self.Data['ret_close'] / self.Data['ret_close_lag']
        np.log(self.Data['ret_close'], out=self.Data['ret_close'])
        self.Data['ret_close'] *= 1e3
        self.Data['ret_close'] = self.Data['ret_close'].reshape(-1, 242, self.Data['ret_close'].shape[1])
        self.Data['_adj_close_tmr'] = self.Data['adj_close'][-1, -1:]

        self.Data['vwap'] = np.where(self.Data['vol'] > 99, self.Data['adj_amt'] / self.Data['vol'], self.Data['opn'])
        self.Data['ret_vwap'] = np.empty_like(self.Data['vwap'])
        self.Data['ret_vwap'][:, 0] = self.Data['ret_close'][:, 0]
        self.Data['ret_vwap'][:, 1:] = np.log(self.Data['vwap'][:, 1:] / self.Data['vwap'][:, :-1]) * 1e3

        # 调整量纲_增强合并_高频财务_基础收益
        multidask('调整量纲_增强合并_高频财务_基础收益', [
            [self.calc_dimension, ('num_buy',)],
            [self.calc_dimension, ('num_sell',)],
            [self.calc_dimension, ('num_total',)],
            [self.calc_dimension, ('adj_amt',)],
            [self.calc_dimension, ('adj_vol',)],
            [self.calc_dev_add, ('buyordercanceledamt', 'sellordercanceledamt', 'ordercanceledamt')],
            [self.calc_dev_add, ('buyordercanceledvol', 'sellordercanceledvol', 'ordercanceledvol')],
            [self.calc_dev_add, ('passivebuyorderamt', 'passivesellorderamt', 'passiveorderamt')],
            [self.calc_dev_add, ('passivebuyordervol', 'passivesellordervol', 'passiveordervol')],
            [self.calc_dev_add, ('activebuyorderamt', 'activesellorderamt', 'activeorderamt')],
            [self.calc_dev_add, ('activebuyordervol', 'activesellordervol', 'activeordervol')],
            [self.calc_dev_add, ('accamountbuy', 'accamountsell', 'accamount')],
            [self.calc_dev_add, ('buytradeamt', 'selltradeamt', 'tradeamt')],
            [self.calc_dev_add, ('buytradevol', 'selltradevol', 'tradevol')],
            [self.calc_dev_add, ('buyorderamt', 'sellorderamt', 'orderamt')],
            [self.calc_dev_add, ('buyordervol', 'sellordervol', 'ordervol')],
            [self.calc_fin_ratio, ('_pe_hist', 'pe_hist')],
            [self.calc_fin_ratio, ('_pb_hist', 'pb_hist')],
            [self.calc_fin_ratio, ('_pcf_hist', 'pcf_hist')],
            [self.calc_fin_ratio, ('_peg_hist', 'peg_hist')],
            [self.calc_fin_ratio, ('_pe_f2', 'pe_f2')],
            [self.calc_fin_ratio, ('_pe_f1', 'pe_f1')],
            [self.calc_fin_ratio, ('_pb_f1', 'pb_f1')],
            [self.calc_base_ret, ('close', 'vwap', 'ret_close_vwap')],
            [self.calc_base_ret, ('high', 'vwap', 'ret_high')],
            [self.calc_base_ret, ('low', 'vwap', 'ret_low')],
            [self.calc_base_ret, ('high', 'close', 'ret_high_close')],
            [self.calc_base_ret, ('low', 'close', 'ret_low_close')],
        ])

        # 增强收益
        multidask('计算增强收益', [
            [self.calc_dev_ret, ('trade', 'ret_trade')],
            [self.calc_dev_ret, ('order', 'ret_order')],
            [self.calc_dev_ret, ('buytrade', 'ret_trade_buy')],
            [self.calc_dev_ret, ('selltrade', 'ret_trade_sell')],
            [self.calc_dev_ret, ('ordercanceled', 'ret_cancel')],
            [self.calc_dev_ret, ('buyordercanceled', 'ret_cancel_buy')],
            [self.calc_dev_ret, ('sellordercanceled', 'ret_cancel_sell')],
            [self.calc_dev_ret, ('buyorder', 'ret_order_buy')],
            [self.calc_dev_ret, ('sellorder', 'ret_order_sell')],
            [self.calc_dev_ret, ('activeorder', 'ret_order_active')],
            [self.calc_dev_ret, ('activebuyorder', 'ret_order_active_buy')],
            [self.calc_dev_ret, ('activesellorder', 'ret_order_active_sell')],
            [self.calc_dev_ret, ('passiveorder', 'ret_order_passive')],
            [self.calc_dev_ret, ('passivebuyorder', 'ret_order_passive_buy')],
            [self.calc_dev_ret, ('passivesellorder', 'ret_order_passive_sell')],
        ])

        # 增强换手
        multidask('计算增强换手', [
            [self.calc_dev_turn, ('', 'turn_total')],
            [self.calc_dev_turn, ('buytrade', 'turn_trade_buy')],
            [self.calc_dev_turn, ('selltrade', 'turn_trade_sell')],
            [self.calc_dev_turn, ('ordercanceled', 'turn_cancel')],
            [self.calc_dev_turn, ('buyordercanceled', 'turn_cancel_buy')],
            [self.calc_dev_turn, ('sellordercanceled', 'turn_cancel_sell')],
            [self.calc_dev_turn, ('order', 'turn_order')],
            [self.calc_dev_turn, ('buyorder', 'turn_order_buy')],
            [self.calc_dev_turn, ('sellorder', 'turn_order_sell')],
            [self.calc_dev_turn, ('activeorder', 'turn_order_active')],
            [self.calc_dev_turn, ('activebuyorder', 'turn_order_active_buy')],
            [self.calc_dev_turn, ('activesellorder', 'turn_order_active_sell')],
            [self.calc_dev_turn, ('passiveorder', 'turn_order_passive')],
            [self.calc_dev_turn, ('passivebuyorder', 'turn_order_passive_buy')],
            [self.calc_dev_turn, ('passivesellorder', 'turn_order_passive_sell')],
            [self.calc_dev_turn_acc, ('accamount', 'turn_acc')],
            [self.calc_dev_turn_acc, ('accamountbuy', 'turn_acc_buy')],
            [self.calc_dev_turn_acc, ('accamountsell', 'turn_acc_sell')],
        ])

        multidask('基础因子异常值处理', [[self.calc_clip_arr, (x,)] for x in MaterialList])

        multidask('准备次日基础材料', [[self.calc_f1_arr, (x,)] for x in MaterialList] + [
            [self.calc_f1_sq, ('_adj_close_tmr', '_adj_close')],
            [self.calc_f1_sq, ('_close_tmr', '_close')],
            [self.calc_f1_sq, ('_total_shares_tmr', 'total_shares')],
            [self.calc_f1_sq, ('_free_float_shares_tmr', 'free_float_shares')],
            [self.calc_f1_sq, ('_payout_ratio_tmr', 'payout_ratio')],
            [self.calc_f1_sq, ('_share_ratio_tmr', 'share_ratio')],
            [self.calc_f1_sq, ('_receive_ratio_tmr', 'receive_ratio')],
            [self.calc_f1_sq, ('profit_tmr', 'profit')],
            [self.calc_f1_sq, ('rtdearn_tmr', 'rtdearn')],
            [self.calc_f1_sq, ('ocf_tmr', 'ocf')],
            [self.calc_f1_sq, ('growth_tmr', 'growth')],
            [self.calc_f1_sq, ('f_eps_tmr', 'f_eps')],
            [self.calc_f1_sq, ('f_profit_tmr', 'f_profit')],
            [self.calc_f1_sq, ('f_equity_tmr', 'f_equity')],
            [self.calc_f1_del, ()],
        ])

        # 均值标准差
        factor_list = pd.read_pickle(f'{self.root_path}/{self._date}/DateCode/factor_list.pkl')
        multidask('计算均值标准差', [[self.calc_f1_mv, (factor_list[x::24],)] for x in range(24)])
        pd.to_pickle(self.Data['MV'], f'{self.root_path}/{self._date}/TmrMeanStd/MV.pkl')

        # 降采样材料
        reduce = ReduceMaterial()
        multidask('准备次日降采样材料', [[self.calc_desample_f1_arr, (x, reduce)] for x in MaterialList])

        # 降均值标准差
        desample_factor_list = pd.read_pickle(
            f'{self.root_path}/{self._date}/DateCode/desample_factor_list.pkl')
        multidask('计算降均值标准差', [[self.calc_desample_f1_mv, (
            desample_factor_list[x::threads],)] for x in range(threads)])
        pd.to_pickle(self.Data['DpMV'], f'{self.root_path}/{self._date}/TmrMeanStd/DpMV.pkl')

        print('总用时秒数：', time.time() - t)
        del self.Data
        gc.collect()

    def make_fold(self):
        for j in ['DateCode', 'TmrLowFreq', 'TmrMinMaterial', 'TmrMeanStd', 'TmrDesampleMaterial']:
            if not os.path.exists(f'{self.root_path}/{self._date}/{j}'):
                os.makedirs(f'{self.root_path}/{self._date}/{j}')

    def set_code_list(self, code_list=None):
        if not code_list:
            file = '/data/group/800080/Apollo/AlphaDataBase/CompleteStockList.csv'
            if not int(time.strftime('%Y%m%d', time.localtime(os.path.getmtime(file)))) >= self.end_date:
                raise ValueError("CompleteStockList not update.")
            code_list = [trans_windcode2int(x) for x in pd.read_csv(
                '/data/group/800080/Apollo/AlphaDataBase/CompleteStockList.csv')['Stock_code'].to_list()]
        pd.to_pickle(code_list, f'{self.root_path}/{self._date}/DateCode/code_list.pkl')
        pd.to_pickle(self.date_list, f'{self.root_path}/{self._date}/DateCode/date_list.pkl')
        self.code_list = code_list

    def set_factor_list(self, factor_list=None, desample_factor_list=None):
        today = str(get_pre_trade_date(offset=-1))
        if factor_list != None:
            pd.to_pickle(factor_list, f'{self.root_path}/{self._date}/DateCode/factor_list.pkl')
        else:
            fll = sorted([x for x in os.listdir(f'{self.root_path}/subscript_factor_list/')
                          if x.startswith('factor_list') & (x[-12:-4] <= today)])[-1]
            shutil.copy(f'{self.root_path}/subscript_factor_list/{fll}',
                        f'{self.root_path}/{self._date}/DateCode/factor_list.pkl')
            print("No specific factor_list given, using default instead.")
        fl_len = len(pd.read_pickle(f'{self.root_path}/{self._date}/DateCode/factor_list.pkl'))
        if desample_factor_list != None:
            pd.to_pickle(desample_factor_list, f'{self.root_path}/{self._date}/DateCode/desample_factor_list.pkl')
        else:
            dfll = sorted([x for x in os.listdir(f'{self.root_path}/subscript_factor_list/')
                          if x.startswith('desample_factor_list') & (x[-12:-4] <= today)])[-1]
            shutil.copy(f'{self.root_path}/subscript_factor_list/{dfll}',
                        f'{self.root_path}/{self._date}/DateCode/desample_factor_list.pkl')
            print("No specific desample_factor_list given, using default instead.")
        dfl_len = len(pd.read_pickle(f'{self.root_path}/{self._date}/DateCode/desample_factor_list.pkl'))
        send_message(['015664', '015836'], f'次日实盘高频因子1分钟频率共{fl_len}个，5分钟频率共{dfl_len}个。')

    def calc_min_data(self, name_in, name_out):
        self.Data[name_out] = get_minute_data(name_in, self.date_list, self.code_list)

    def calc_dev_add(self, name1_in, name2_in, name_out):
        self.Data[name_out] = self.Data[name1_in] + self.Data[name2_in]

    def calc_fin_ratio(self, name_in, name_out):
        self.Data[name_out] = self.Data[name_in] / self.Data['close']

    def calc_base_ret(self, name1_in, name2_in, name_out):
        self.Data[name_out] = np.log(self.Data[name1_in] / self.Data[name2_in]) * 1e3

    def calc_dimension(self, name_in):
        if name_in in ['num_buy', 'num_sell', 'num_total']:
            self.Data[name_in] *= 1e-2
        if name_in in ['adj_amt', 'adj_vol']:
            self.Data[name_in] *= 1e-4

    def calc_dev_ret(self, name_in, name_out):
        self.Data[name_in + 'amt'] /= self.Data[name_in + 'vol']
        self.Data[name_in + 'amt'] /= self.Data['vwap']
        self.Data[name_in + 'amt'][~ (self.Data[name_in + 'vol'] > 99)] = 1
        np.log(self.Data[name_in + 'amt'], out=self.Data[name_in + 'amt'])
        self.Data[name_in + 'amt'] *= 1e3
        self.Data[name_out] = self.Data[name_in + 'amt']
        del self.Data[name_in + 'amt']

    def calc_dev_turn(self, name_in, name_out):
        self.Data[name_in + 'vol'] /= self.Data['_free_float_shares']
        self.Data[name_out] = self.Data[name_in + 'vol']
        del self.Data[name_in + 'vol']

    def calc_dev_turn_acc(self, name_in, name_out):
        self.Data[name_in] /= self.Data['vwap']
        self.Data[name_in] /= self.Data['_free_float_shares']
        self.Data[name_out] = self.Data[name_in]
        del self.Data[name_in]

    def calc_f1_del(self):
        address = f'{self.root_path}/{self._date}/TmrLowFreq/'
        if os.path.exists(f'{address}/pre_close.npy'):
            os.remove(f'{address}/pre_close.npy')

    def calc_f1_sq(self, name_in, name_out):
        address = f'{self.root_path}/{self._date}/TmrLowFreq/'
        np.save(f'{address}/{name_out}.npy', self.Data[name_in])

    def calc_clip_arr(self, name_in):
        max_val = MaterialDistAdjust[name_in][0]
        min_val = MaterialDistAdjust[name_in][1]
        np.clip(self.Data[name_in], min_val, max_val, self.Data[name_in])

    def calc_f1_arr(self, name_in):
        address = f'{self.root_path}/{self._date}/TmrMinMaterial/'
        head = [
            147, 78, 85, 77, 80, 89, 1, 0, 118, 0, 123, 39, 100, 101, 115, 99, 114, 39, 58, 32,
            39, 60, 102, 56, 39, 44, 32, 39, 102, 111, 114, 116, 114, 97, 110, 95, 111, 114, 100, 101,
            114, 39, 58, 32, 70, 97, 108, 115, 101, 44, 32, 39, 115, 104, 97, 112, 101, 39, 58, 32,
            40, 41, 44, 32, 125, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
            32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
            32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
            32, 32, 32, 32, 32, 32, 32, 10
        ]
        dtype_dict = {
            'bool': [124, 98, 49],
            'int8': [124, 105, 49],
            'int16': [60, 105, 50],
            'int32': [60, 105, 52],
            'int64': [60, 105, 56],
            'float32': [60, 102, 52],
            'float64': [60, 102, 56]
        }
        shape_map = {
            '0': 48,
            '1': 49,
            '2': 50,
            '3': 51,
            '4': 52,
            '5': 53,
            '6': 54,
            '7': 55,
            '8': 56,
            '9': 57,
            ',': 44,
            ' ': 32
        }
        shape = self.Data[name_in][-self.use_days:].shape
        self.Data[name_in] = self.Data[name_in].astype('float32')
        amend_shape = (shape[0] + 1,) + shape[1:]
        dtype_value = dtype_dict['float32']
        shape_value = [shape_map[x] for x in str(amend_shape)[1: -1]] + [41, 44, 32, 125]
        head[21: 24] = dtype_value
        head[61: 61 + len(shape_value)] = shape_value
        fp = np.memmap(f'{address}/{name_in}.npy', dtype='uint8', mode='w+', offset=0, shape=128)
        fp[:] = head
        del fp
        fp = np.memmap(f'{address}/{name_in}.npy', dtype='float32', mode='r+', offset=128, shape=shape)
        fp[:] = self.Data[name_in][-self.use_days:]
        del fp
        fp = np.memmap(f'{address}/{name_in}.npy', dtype='float32', mode='r+',
                       offset=128 + self.Data[name_in][-self.use_days:].nbytes, shape=shape[1:])
        fp[:] = np.nan
        del fp

    def calc_desample_f1_arr(self, name_in, reduce):
        address = f'{self.root_path}/{self._date}/TmrDesampleMaterial/'
        head = [
            147, 78, 85, 77, 80, 89, 1, 0, 118, 0, 123, 39, 100, 101, 115, 99, 114, 39, 58, 32,
            39, 60, 102, 56, 39, 44, 32, 39, 102, 111, 114, 116, 114, 97, 110, 95, 111, 114, 100, 101,
            114, 39, 58, 32, 70, 97, 108, 115, 101, 44, 32, 39, 115, 104, 97, 112, 101, 39, 58, 32,
            40, 41, 44, 32, 125, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
            32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
            32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
            32, 32, 32, 32, 32, 32, 32, 10
        ]
        dtype_dict = {
            'bool': [124, 98, 49],
            'int8': [124, 105, 49],
            'int16': [60, 105, 50],
            'int32': [60, 105, 52],
            'int64': [60, 105, 56],
            'float32': [60, 102, 52],
            'float64': [60, 102, 56]
        }
        shape_map = {
            '0': 48,
            '1': 49,
            '2': 50,
            '3': 51,
            '4': 52,
            '5': 53,
            '6': 54,
            '7': 55,
            '8': 56,
            '9': 57,
            ',': 44,
            ' ': 32
        }
        self.Data[name_in] = getattr(reduce, DesampleMethod[name_in])(self.Data[name_in])
        shape = self.Data[name_in][-self.use_days:].shape
        amend_shape = (shape[0] + 1,) + shape[1:]
        dtype_value = dtype_dict['float32']
        shape_value = [shape_map[x] for x in str(amend_shape)[1: -1]] + [41, 44, 32, 125]
        head[21: 24] = dtype_value
        head[61: 61 + len(shape_value)] = shape_value
        fp = np.memmap(f'{address}/{name_in}.npy', dtype='uint8', mode='w+', offset=0, shape=128)
        fp[:] = head
        del fp
        fp = np.memmap(f'{address}/{name_in}.npy', dtype='float32', mode='r+', offset=128, shape=shape)
        fp[:] = self.Data[name_in][-self.use_days:]
        del fp
        fp = np.memmap(f'{address}/{name_in}.npy', dtype='float32', mode='r+',
                       offset=128 + self.Data[name_in][-self.use_days:].nbytes, shape=shape[1:])
        fp[:] = np.nan
        del fp

    def calc_f1_mv(self, factor_list):
        for name, formula, _, _ in factor_list:
            mean, std = self.factor_test_mv(formula)
            self.Data['MV']['mean'][name] = mean
            self.Data['MV']['std'][name] = std

    def calc_desample_f1_mv(self, factor_list):
        for name, formula, _, _ in factor_list:
            mean, std = self.factor_test_mv(formula)
            self.Data['DpMV']['mean'][name] = mean
            self.Data['DpMV']['std'][name] = std

    def factor_test_mv(self, formula, standardize_days=40):
        program = formula.replace('\n', '').replace(' ', '').replace(',', ', ')
        replace = lambda x: x[1] + ("self.Data['%s']") % x[2] + x[3]
        program = re.sub('([\u0020\u0028])([a-zA-Z_]+[12]?)([\u0029\u002c])', replace, program)
        factor = eval(program)
        factor_finite = np.isfinite(factor)
        bottleneck2.clip_array_3d(factor)
        factor[~ factor_finite] = 0
        factor2 = factor ** 2

        d_cf = factor.sum(axis=1)
        d_cf2 = factor2.sum(axis=1)
        d_cn = factor_finite.sum(axis=1)

        rd_cf = bottleneck2.dt_sum(d_cf, standardize_days)
        rd_cf2 = bottleneck2.dt_sum(d_cf2, standardize_days)
        rd_cn = bottleneck.move_sum(d_cn.astype('float32'), standardize_days, axis=0)
        rd_cn[rd_cn < standardize_days * factor.shape[1] / 2] = np.nan

        rd_mean = rd_cf / rd_cn
        rd_std = ((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5
        rd_std[rd_std == 0] = np.nan
        return rd_mean[-1], rd_std[-1]
