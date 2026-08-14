# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 10:52:20 2020

@author: 013600
"""

import pandas as pd
import re
import numpy as np
import os
import datetime as dt
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
import warnings
warnings.filterwarnings('ignore')
from ProdWork.CommonTools import getValueByKeyFromLine, getValueByKeyFromLine2,isException,trans_str2dic,getMriskFlag,getRejectReason,getMriskInfo, format_unix2dt, getRiskViolateRemark

class LogParse_Tool:
    def __init__(self, environment, date, log_line):
        self.environment = str(environment)
        self.date = str(date)
        self.log_lines = log_line
        self.all_lines = list(map(self.openpx_determine, log_line))
        self.lines = self.filter_triggered_line(log_line)
        self.algo_code_dict = self.get_algo_code_dict()
        self.machine_code_dict, self.machine_counter_dict = self.get_machine_code_dict()
        self.log_dic = self.split_log_algo()

    @staticmethod
    def get_keys_with_value(selfdict, value):
        return [k for k, v in selfdict.items() if v == value]

    @staticmethod
    def getAlgoCode(line):
        return re.findall(r"\[(.*?)]", line)[0]


    @staticmethod
    def getMachineNoFromLine(line):
        try:
            return line[line.index('168.'):line.index(']')]
        except:
            return 'no machine'

    @staticmethod
    def getSymbolFromStartSuccessLine(line):
        return line[line.index('LedaStrategy-CPP for ') + 28 : line.index(' Version')]

    @staticmethod
    def openpx_determine(x):
        if type(x) != str:
            x = bytes.decode(x, errors='ignore')
        if 'OpenPX' not in x:
            return x
        else:
            return ''

    def algocode2code(self,x, algo_dic):
        try:
            code = algo_dic[x]
            return code
        except KeyError:
            return ''

    def filter_triggered_line(self, log_line):
        # triggered_lines = list(filter(lambda x: 'Triggered' in str(x), log_line))
        triggered_lines = list(filter(lambda x: 'Calculate factors' in str(x), log_line))
        # triggered_lines = list(filter(lambda x: '002819' not in str(x), triggered_lines))
        # triggered_lines = list(filter(lambda x: '603985' not in str(x), triggered_lines))
        algo_code_set = set()
        for triggered_line in triggered_lines:
            algo_code = self.getAlgoCode(str(triggered_line))
            symbol = getValueByKeyFromLine2(str(triggered_line), by='symbol')
            algo_code_set.add(algo_code + ' ' + symbol)
        print(f'共有{len(algo_code_set)}个实例触发')
        # 这里肯定有symbol了
        log_line_ = list(filter(lambda x: self.getAlgoCode(str(x)) + ' ' + getValueByKeyFromLine2(str(x), by='symbol') in algo_code_set, log_line))
        # log_line_ = list(filter(lambda x: self.filter_wrong_lastMatchTime_line(str(x)), log_line_))
        if type(log_line_[0]) != str:
            log_line_ = list(map(lambda x: bytes.decode(x, errors='ignore'), log_line_))
        print(f'非本实例触发票删除完毕，之前{len(log_line)}行，现在{len(log_line_)}行')
        return log_line_

    def get_algo_code_dict(self):
        algo_code_dict = {}
        selkey = []
        selcode = []
        for line in self.lines:
            line = str(line)
            try:
                algo_code = self.getAlgoCode(str(line))
                code = getValueByKeyFromLine2(line, by='symbol')
                if ('symbol=' in line) & (algo_code + ' ' + code not in algo_code_dict.keys()):
                    if code in list(algo_code_dict.values()):
                        selcode = list(set(selcode + [code]))
                        selkey = self.get_keys_with_value(algo_code_dict, code)#[-1]
                        # if len(algo_code) > 1:
                        #     print(1)
                        print(code, algo_code)
                        # for tmp_key in selcode[1:]:
                        #     algo_code_dict.pop(tmp_key)
                        pass
                    algo_code_dict[algo_code + ' ' + code] = code
            except IndexError:
                # print(line)
                pass
        algo_code_dict = {key: val for key, val in algo_code_dict.items() if key not in selkey[:-1]}
        for tmocode in selcode:
            print(tmocode, self.get_keys_with_value(algo_code_dict, tmocode))
        return algo_code_dict

    def get_machine_code_dict(self):
        machine_code_dict = {}
        machine_counter_dict = {}
        for line in self.lines:
            if 'symbol=' not in line:
                continue
            try:
                algo_code = self.getAlgoCode(line)
                code = getValueByKeyFromLine(line, by='symbol')
                stock_code = self.algo_code_dict[algo_code + ' ' + code]
                if stock_code not in machine_code_dict.keys():
                    machine_code = self.getMachineNoFromLine(line)
                    machine_code_dict[stock_code] = machine_code
            except:
                pass

        for line in self.all_lines:
            try:
                if 'Start Success' in line:
                    machine_code = self.getMachineNoFromLine(line)
                    if machine_code not in machine_counter_dict.keys():
                        machine_counter_dict[machine_code] = 1
                    elif machine_code in machine_counter_dict.keys():
                        machine_counter_dict[machine_code] = machine_counter_dict[machine_code] + 1
            except:
                pass
        return machine_code_dict, machine_counter_dict

    def split_log_algo(self):
        '''
        用来根据by区分不同的关键词对应的行
        返回一个dict，key为by的不同枚举值，value为各枚举值下对应的所有行
        '''
        resultDic = {}
        for line in self.lines:
            try:
                key = self.getAlgoCode(line)
                code = getValueByKeyFromLine2(line, by='symbol')
                if key + ' ' + code in self.algo_code_dict.keys():
                    if key + ' ' + code not in resultDic:
                        resultDic[key + ' ' + code] = [line]
                    else:
                        resultDic[key + ' ' + code].append(line)
            except ValueError:
                pass
        return resultDic

    def get_except_df(self):
        exceptionList = []
        algo_dic = {}
        tmp_lines = list(filter(lambda x: 'symbol=' in x, self.all_lines))
        for line in tmp_lines:
            try:
                algo_code = self.getAlgoCode(line)
                code = getValueByKeyFromLine2(line, by='symbol')
                if isException(line) and ('INFO' not in line):
                    exceptionList.append([algo_code + ' ' + code, line])
                if (algo_code not in algo_dic) and len(code) > 0:
                    algo_dic[algo_code + ' ' + code] = code
            except IndexError:
                pass
        except_df = pd.DataFrame(exceptionList, columns=['algo_code', 'line'])
        except_df['code'] = except_df['algo_code'].apply(lambda x: self.algocode2code(x, algo_dic))
        return except_df

    def get_inf_from_log(self):
        inf_list = []
        factor_list = []
        factor_list_all = []
        daily_zt_list = []
        trade_dic = {}
        order_info_dic = {}
        all_code_model_data = {}
        unfilled_info_dic = {}
        for key, log in self.log_dic.items():
            # key = '20210302-092955-809-0000112-168.62.9.55'
            # log = log_dic[key]
            key_code = self.algo_code_dict[key]
            # if key_code == '603778.SH':
            #     print(1)
            if key_code == '601688.SH':
                continue
            inf_dic = {}
            factor_dic_all = {}
            daily_zt_dic = {}
            for line in log:
                order_count = 0
                # list(filter(lambda x: 'Order was rejected' in x, log))    # 测试用，看到底有没有这一行
                if 'Calculate factors' in line:
                    inf_dic['factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))

                elif 'Triggered' in line:
                    inf_dic['ZT_Time'] = int(getValueByKeyFromLine(line, by='reachedZTTime'))

                elif 'Total unscaled factors' in line:
                    factor_dic_all = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')

                elif ('Model prediction' in line) & ('parentPath' not in line):
                    inf_dic['shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldBuySignal')
                    inf_dic['model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))

                elif ('riskSummary' in line) & ('拉抬打压' in line):
                    inf_dic['MRisk_info'] = '触发拉抬打压'

                elif ('predict signals' in line) & ('parentPath' not in line):
                    inf_dic['sum_signals'] = getValueByKeyFromLine(line, by='predict signals')

                if ('parentPath' in line) & ('Single model' not in line):
                    model_name = getValueByKeyFromLine(line, by='parentPath')
                    if model_name not in all_code_model_data.keys():
                        all_code_model_data[model_name] = {}
                    code = getValueByKeyFromLine(line, by='symbol')
                    inf_dic[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')

                if ('Order info' in line) & ('rejected' not in line) & ('placeType=odd_sell' not in line):  #  触发并准备下单,odd_sell小单测试过滤掉
                    order_count += 1
                    trade_type = getValueByKeyFromLine(line, by='placeType')
                    order_type = getValueByKeyFromLine(line, by='orderType')
                    quantity = getValueByKeyFromLine(line, by='quantity')
                    quantity = float(quantity)
                    if (trade_type == 'SplitLastShot') | (trade_type == 'JupiterFirstOrder') | (trade_type == 'MRiskSplitLastShotBuy') | (order_type == 'MRiskSplitShot'):
                        daily_zt_dic['order_direction'] = trade_type
                        daily_zt_dic['quantity'] = getValueByKeyFromLine(line, by='quantity')
                        daily_zt_dic['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                        daily_zt_dic['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                        daily_zt_dic['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                        daily_zt_dic['price'] = getValueByKeyFromLine(line, by='price')
                        daily_zt_dic['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                        daily_zt_dic['totalOrderAmt'] = float(daily_zt_dic['quantity']) * float(daily_zt_dic['price']) * float(daily_zt_dic['splitOrderNum'])
                        inf_dic['totalOrderAmt'] = daily_zt_dic['totalOrderAmt']
                        daily_zt_ser = pd.Series(daily_zt_dic, name=key_code)
                        daily_zt_list.append(daily_zt_ser)
                if 'Order updated' in line:  # 单子实际的进行情况
                    code = getValueByKeyFromLine(line, by='symbol')
                    if key not in order_info_dic.keys():
                        order_info_dic[key] = []
                    order = {'transactionTime': format_unix2dt(getValueByKeyFromLine(line, by='transactionTime')),
                    # order = {'transactionTime': '20141008150000',
                             'clOrdId': getValueByKeyFromLine(line, by='clOrdId'),
                             'ordStatus': getValueByKeyFromLine(line, by='ordStatus'),
                             'price': getValueByKeyFromLine(line, by='price'),
                             'quantity': getValueByKeyFromLine(line, by='quantity'), # 委托量
                             'lastQty': getValueByKeyFromLine(line, by='lastQty'), # 实际成交量
                             'cumQty': getValueByKeyFromLine(line, by='cumQty'),
                             'avgPx': getValueByKeyFromLine(line, by='avgPx'),
                             'lastPx': getValueByKeyFromLine(line, by='lastPx'),
                             'orderSide': getValueByKeyFromLine(line, by='orderSide'),
                             'orderType': getValueByKeyFromLine(line, by='orderType'),
                             'actionSource':getValueByKeyFromLine(line, by='actionSource'),
                             'lastMatchTime': format_unix2dt(getValueByKeyFromLine(line, by='lastMatchTime')),
                             # 'lastMatchTime': format_lastMatchTime2dt(getValueByKeyFromLine(line, by='lastMatchTime')),
                             'stockcode': code,
                             'firstTradeIndex': getValueByKeyFromLine(line, by='firstTradeIndex')}
                    try:
                        order_info_dic[key].append(pd.Series(order))
                    except:
                        print('Order Update append Error')
                if 'Order was rejected' in line: # 拒单情况
                    code = getValueByKeyFromLine(line, by='symbol')
                    if key not in unfilled_info_dic.keys():
                        unfilled_info_dic[key] = []
                    unfilled_info = {'riskSummary': getRejectReason(line, by1 = 'riskOperation',by2='riskSummary'),
                                     'riskViolateRemark': getRiskViolateRemark(line, by1='riskViolateRemark'),
                                     'orderSide': getValueByKeyFromLine(line, by='orderSide'),
                                     'stockcode': code,
                                     'transactTime': format_unix2dt(getValueByKeyFromLine(line, by='transactTime')),\
                                     'riskOperation': getValueByKeyFromLine(line, by='riskOperation'), \
                                     'riskType': getValueByKeyFromLine(line, by='riskType'), \
                                     'MriskFlag':getMriskFlag(line,by1 = 'riskOperation',by2='riskType'),\
                                     'riskInfo': getMriskInfo(line, by1='riskSummary')}
                    unfilled_info_dic[key].append(pd.Series(unfilled_info))

            if key_code in trade_dic.keys():
                trade_dic[code] = pd.concat(trade_dic[code], axis=1).T
            if key_code in order_info_dic.keys():
                try:
                    order_info_dic[code] = pd.concat(order_info_dic[code], axis=1).T
                except:
                    print(1)
            if key_code in unfilled_info_dic.keys():
                unfilled_info_dic[code] = pd.concat(unfilled_info_dic[code], axis=1).T
            if len(inf_dic) != 0:
                inf_ser = pd.Series(inf_dic, name=key_code)
                inf_list.append(inf_ser)

            factor_dic = factor_dic_all

            if len(factor_dic) != 0:
                factor_ser = pd.Series(factor_dic, name=key_code)
                factor_list.append(factor_ser)
            if len(factor_dic_all) != 0:
                factor_ser_all = pd.Series(factor_dic_all, name=key_code)
                factor_list_all.append(factor_ser_all)
        if len(inf_list) == 0:
            print('没有leda样本！！！')
            inf_df = pd.DataFrame()
        else:
            inf_df = pd.concat(inf_list, axis=1).T.sort_index()
            # if self.environment not in ['UAT']:
            # inf_df_mrisk_info = inf_df[~inf_df['MRisk_info'].isna()]
            # inf_df_mrisk_info = inf_df_mrisk_info.reset_index().drop_duplicates('index').set_index('index')
            # inf_df.loc[inf_df_mrisk_info.index, 'MRisk_info'] = inf_df_mrisk_info.loc[inf_df_mrisk_info.index, 'MRisk_info']
            if 'ZT_Time' in inf_df.columns:
                inf_df = inf_df.loc[inf_df['ZT_Time'].notnull()]
                inf_df = inf_df.query('ZT_Time > 0') # 剔除ZT_Time为空的行；由于“Mrisk_Info”这一个不能区分jup还是eur，所以会导致inf_list中存在重复的个股，实则一个jupiter一个europa，但都纳入到了inf_df
            else:
                inf_df = pd.DataFrame()

        if len(factor_list)==0:
            factor_df = pd.DataFrame()
        else:
            factor_df = pd.concat(factor_list, axis=1).T.sort_index()

        if len(daily_zt_list) != 0:
            daily_zt_df = pd.concat(daily_zt_list, axis=1).T.sort_index()
        else:
            daily_zt_df = pd.DataFrame()

        order_info_df = pd.DataFrame()
        for keys, info in order_info_dic.items():
            order_info_df = pd.concat([order_info_df, pd.DataFrame(info)])

        unfilled_info_df = pd.DataFrame()
        for keys, info in unfilled_info_dic.items():
            unfilled_info_df = pd.concat([unfilled_info_df, pd.DataFrame(info)])

        return inf_df, factor_df, trade_dic, all_code_model_data, daily_zt_df, order_info_df, unfilled_info_df