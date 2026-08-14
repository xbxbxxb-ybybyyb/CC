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
import time
import warnings
warnings.filterwarnings('ignore')
import IO
from CommonTools import excel_saver, ftp_download,ftp_upload,getValueByKeyFromLine,strTime2MDTime,isException,cal_time_delta,trans_str2dic,getMriskFlag,getRejectReason,getMriskInfo, getRiskViolateRemark
class LogParse:
    def __init__(self, environment,date,log_line):
        self.environment = str(environment)
        self.date = str(date)
        self.log_lines = self.log_preprocess(log_line)
        self.lines = list(map(self.openpx_determine, self.log_lines))
        self.algo_code_dict = self.get_algo_code_dict()
        self.machine_code_dict, self.machine_counter_dict = self.get_machine_code_dict()
        self.log_dic = self.split_log_algo()

    # 20230516 by fengc：去掉的Mock，isMock可能既预热又触发
    def log_preprocess(self, log_line):
        mock_lines = log_line
        # algo_code_set = set()
        # for mock_line in mock_lines:
        #     algo_code = self.getAlgoCode(str(mock_line))
        #     algo_code_set.add(algo_code)
        # log_line_ = list(filter(lambda x: self.getAlgoCode(str(x)) not in algo_code_set, log_line))
        # print(f'mock票删除完毕，之前{len(log_line)}行，现在{len(log_line_)}行')
        return mock_lines

    def get_keys_with_value(self, selfdict, value, default=None):
        return [k for k, v in selfdict.items() if v == value]
    def getAlgoByalgoFromLine(self, line):
        if self.environment == 'prod_test':
            return line[line.index('StrongStrategy2-algo-') + 21:line.index('-n0]')]
        elif 'test' in self.environment:
            return line[line.index('StrongStrategy-StrongStrategy-') + 30:line.index('-n0]')]
        elif (self.environment == 'prod') | ('UAT' in self.environment) | ('night' in self.environment) | (self.environment == 'SHEX') | (self.environment in [ 'SZEX','SZEX_udp']):
            return re.findall(r"SellStrategy-algo-(.*?)]", line)[0]

    def getAlgoCode(self,line):
        if self.environment == 'prod_test':
            return re.findall(r"StrongStrategy2-algo-(.*)-n0", line)[0]
        elif 'test' in self.environment:
            return re.findall(r"StrongStrategy-StrongStrategy-(.*)-n0", line)[0]#line[line.index('StrongStrategy-StrongStrategy-') + 30:line.index('-n0]')]
        elif (self.environment == 'prod') |  ('night' in self.environment) | (self.environment == 'SHEX') | (self.environment in [ 'SZEX','SZEX_udp']):
            return re.findall(r"StrongStrategy-algo-(.*)-n0", line)[0]
        elif 'UAT' in self.environment:
            return re.findall(r"SellStrategy-algo-(.*?)]", line)[0]

    # TODO:change this
    def getMachineNoFromLine(self,line):
        if  (self.environment == 'UAT_lite') or ('uat_lite' in self.environment):
            return line[line.index('168.') + 4:line.index('-n0]')]
        elif ('UAT' in self.environment) |('night' in self.environment):
            return line[line.index('168.62.') + 7:line.index(']')]
        elif (self.environment == 'SHEX'):
            return line[line.index('168.') + 4:line.index(']')]
        elif (self.environment == 'SZEX'):
            return line[line.index('168.') + 4:line.index(']')]
        elif self.environment == 'SZEX_udp':
            return line[line.index('168.80.') + 7:line.index(']')]
        elif ('test' in self.environment):
            return line[line.index('168.7.') + 6:line.index(']')]
        else:
            #return line[line.index('1') + 1:line.index('-n0]')]
            try:
                return line[line.index('168.') + 7:line.index('-n0]')]
            except:
                return line[line.index('100.') + 7:line.index('-n0]')]
    def openpx_determine(self,x):
        if self.environment == 'prod':
            x = bytes.decode(x,errors='ignore')
            if 'OpenPX' not in x:
                return x
            else:
                #print('OPenPX is in line!!!!')
                return ''
        elif ('UAT' in self.environment) | ('night' in self.environment) | (self.environment == 'SHEX') | (self.environment in ['SZEX','SZEX_udp'])|('test' in self.environment):
            x = bytes.decode(x,errors='ignore')
            if 'OpenPX' not in x:
                return x
            else:
                #print('OPenPX is in line!!!!')
                return ''

    def algocode2code(self,x, algo_dic):
        try:
            code = algo_dic[x]
            return code
        except KeyError:
            return ''

    def get_algo_code_dict(self):
        algo_code_dict = {}
        selkey = []
        selcode = []
        for line in self.lines:
            try:
                algo_code = self.getAlgoCode(line)
                code = getValueByKeyFromLine(line, by='symbol')
                if len(code) >= 6 and not (code.endswith('SH') or code.endswith('SZ')): # 解决日志中有些symbol不含.SH .SZ的问题
                    code = code + '.SH' if code.startswith('6') else code + '.SZ'
                if ('symbol=' in line) & ((algo_code + ' ' + code) not in algo_code_dict.keys()):
                    if code in list(algo_code_dict.values()):
                        selcode = list(set(selcode + [code]))
                        selkey = self.get_keys_with_value(algo_code_dict, code) # [-1]
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
        # NOTE: 历史遗留问题，不知道为啥这里要写这一句，导致algo_code_dict缺少一个实例，20231023由fengc注释掉，样例：20231019 603388
        # algo_code_dict = {key: val for key, val in algo_code_dict.items() if key not in selkey[:-1]}
        for tmocode in selcode:
            print(tmocode, self.get_keys_with_value(algo_code_dict, tmocode))
        return algo_code_dict

    def get_machine_code_dict(self):
        machine_code_dict = {}
        machine_counter_dict = {}
        for line in self.lines:
            try:
                algo_code = self.getAlgoCode(line)
                code = getValueByKeyFromLine(line, by='symbol')
                try:
                    stock_code = self.algo_code_dict[algo_code + ' ' + code]
                    if stock_code not in machine_code_dict.keys():
                        machine_code = self.getMachineNoFromLine(line)
                        machine_code_dict[stock_code] = machine_code
                except:
                    pass
                if 'Start Success' in line:
                #if ('Pause strategy' in line or 'Pause Strategy' in line) and 'reason=' in line :
                    machine_code = self.getMachineNoFromLine(line)
                    if machine_code not in machine_counter_dict.keys():
                        machine_counter_dict[machine_code] = 1
                    elif machine_code in machine_counter_dict.keys():
                        machine_counter_dict[machine_code] = machine_counter_dict[machine_code] + 1
            except IndexError:
                pass
        return machine_code_dict, machine_counter_dict

    def split_log_algo(self):
        '''
        用来根据by区分不同的关键词对应的行
        返回一个dict，key为by的不同枚举值，value为各枚举值下对应的所有行
        '''
        resultDic = {}
        for line in self.lines:
            if line == '':
                continue
            try:
                key = self.getAlgoByalgoFromLine(line)
                code = getValueByKeyFromLine(line, by='symbol')
                if len(code) >= 6:
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
        algo_dic = {}  # 个股代码对应的实例号
        for line in self.lines:
            try:
                if isException(line) and ('INFO' not in line):
                    algo_code = self.getAlgoCode(line)
                    exceptionList.append([algo_code, line])
                algo_code = self.getAlgoCode(line)
                code = getValueByKeyFromLine(line, by='symbol')
                if (algo_code not in algo_dic) and len(code) > 0:
                    algo_dic[algo_code + ' ' + code] = code
            except IndexError:
                pass
        except_df = pd.DataFrame(exceptionList, columns=['algo_code', 'line'])
        except_df['code'] = except_df['algo_code'].apply(lambda x: self.algocode2code(x, algo_dic))
        return except_df

    def start_parsing(self):
        inf_jupz_list = []
        inf_list_931_sellv1 = []
        inf_list_930_sellv1 = []
        factor_list_jupz = []
        factor_list_931_sellv1 = []
        factor_list_930_sellv1 = []
        daily_jupz_list = []
        daily_list_sellv1 = []
        trade_dic = {}
        now_trade_dic = {}
        new_trade_dic = {}
        order_info_dic = {}
        all_code_model_data_jupz = {}
        all_code_model_data_931_sellv1 ={}
        unfilled_info_dic = {}
        for key, log in self.log_dic.items():
            key_code = self.algo_code_dict[key]
            if key_code != '601688.SH':
                inf_dic_jupz = {}
                inf_dic_931_sellv1 = {}
                factor_dic_jupz = {}
                factor_dic_931_sellv1 = {}
                factor_dic_930_sellv1 = {}
                daily_zt_dic = {}
                daily_dic_sellv1 = {}
                for line in log:
                    order_count = 0
                    if 'sell calculate factors' in line and '931' in line:
                        inf_dic_931_sellv1['factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))
                    if 'JupiterN Calculate factors' in line:
                        inf_dic_jupz['factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))
                    if 'sell model prediction' in line and '931' in line and 'parentPath' not in line:
                        inf_dic_931_sellv1['model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))
                    if 'ZT Model prediction' in line:
                        inf_dic_jupz['model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))
                    elif 'Triggered' in line and 'JupiterN' in line:
                        inf_dic_jupz['ZT_Time'] = int(getValueByKeyFromLine(line, by='reachedZTTime'))
                        # inf_dic_jupz['system_time'] = getValueByKeyFromLine(line, by='now')
                        factor_dic_jupz = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                    elif 'Total unscaled factors' in line:
                        factor_dic_jupz = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                    elif 'nowTrade' in line:
                        trade_str = line
                        code = getValueByKeyFromLine(trade_str, by='symbol')
                        if key not in now_trade_dic.keys():
                            now_trade_dic[key] = []
                        trade = {'TradePrice': float(getValueByKeyFromLine(trade_str, by='price')),
                                 'TradeQty': float(getValueByKeyFromLine(trade_str, by='quantity')),
                                 'TradeMoney': float(getValueByKeyFromLine(trade_str, by='turnover')),
                                 'TradeIndex': int(getValueByKeyFromLine(trade_str, by='tradeIndex')),
                                 'TradeBuyNo': int(getValueByKeyFromLine(trade_str, by='tradeBuyNo')),
                                 'TradeSellNo': int(getValueByKeyFromLine(trade_str, by='tradeSellNo')),
                                 'TradeBSFlag': (getValueByKeyFromLine(trade_str, by='side') == 'Offer') + 1,
                                 'TradeType': int(getValueByKeyFromLine(trade_str, by='type') == 'Canceled'),
                                 'MDTime': strTime2MDTime(getValueByKeyFromLine(trade_str, by='nowTradeTimestamp'))}
                        now_trade_dic[key].append(pd.Series(trade))
                    elif 'New trade' in line:
                        trade_str = line
                        code = getValueByKeyFromLine(trade_str, by='symbol')
                        if key not in new_trade_dic.keys():
                            new_trade_dic[key] = []
                        trade = {'TradePrice': float(getValueByKeyFromLine(trade_str, by='price')),
                                 'TradeQty': float(getValueByKeyFromLine(trade_str, by='quantity')),
                                 'TradeMoney': float(getValueByKeyFromLine(trade_str, by='turnover')),
                                 'TradeIndex': int(getValueByKeyFromLine(trade_str, by='tradeIndex')),
                                 'TradeBuyNo': int(getValueByKeyFromLine(trade_str, by='tradeBuyNo')),
                                 'TradeSellNo': int(getValueByKeyFromLine(trade_str, by='tradeSellNo')),
                                 'TradeBSFlag': (getValueByKeyFromLine(trade_str, by='side') == 'Offer') + 1,
                                 'TradeType': int(getValueByKeyFromLine(trade_str, by='type') == 'Canceled'),
                                 'log_ReceiveDateTime': trade_str[11:13] + trade_str[14:16] + trade_str[17:19] + trade_str[20:23]}
                        new_trade_dic[key].append(pd.Series(trade))
                    elif ('Model prediction' in line) & ('parentPath' not in line):
                        inf_dic_jupz['shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldBuySignal')
                        inf_dic_jupz['model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('predict signals' in line) & ('parentPath' not in line):
                        inf_dic_jupz['sum_signals'] = getValueByKeyFromLine(line, by='predict signals')
                    elif ('ZT Model predict' in line) & ('parentPath' not in line):
                        inf_dic_jupz['sum_signals'] = getValueByKeyFromLine(line, by='sum_signals')
                    elif ('sell model prediction' in line) & ('parentPath' in line) & ('sellKey=931' in line): # sellv1子模型预测
                        print('sell1')
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data_931_sellv1.keys():
                            all_code_model_data_931_sellv1[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic_931_sellv1[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('sell model predict' in line) &  ('parentPath' not in line) & ('sellKey=931' in line) & ('timeCost' not in line):
                        inf_dic_931_sellv1['sum_signals'] = getValueByKeyFromLine(line, by='v1Signals')
                    elif ('parentPath' in line) & ('ZT Model prediction' in line):
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data_jupz.keys():
                            all_code_model_data_jupz[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic_jupz[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('parentPath' in line) & ('Single model predict timeCost' in line):  # 进不来,计算其中一个的耗时
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        time_cost = int(getValueByKeyFromLine(line, by='Single model predict timeCost'))
                        if model_name + '_tot_time_cost' in inf_dic_jupz.keys():
                            inf_dic_jupz[model_name + '_tot_time_cost'] = inf_dic_jupz[model_name + '_tot_time_cost'] + time_cost
                        else:
                            inf_dic_jupz[model_name + '_tot_time_cost'] = time_cost
                        print('Jupiter: Single model predict timeCost, parentPath !!!!查看样例', model_name, time_cost)
                    elif ('parentPath' in line) & ('Single model scale timeCost' in line):  # 进不来,计算另一类耗时并加和
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        time_cost = int(getValueByKeyFromLine(line, by='Single model scale timeCost'))
                        if model_name + '_tot_time_cost' in inf_dic_jupz.keys():
                            inf_dic_jupz[model_name + '_tot_time_cost'] = inf_dic_jupz[model_name + '_tot_time_cost'] + time_cost
                        else:
                            inf_dic_jupz[model_name + '_tot_time_cost'] = time_cost
                        print('Jupiter: Single model scale timeCost, parentPath !!!!查看样例', model_name, time_cost)

                    elif ('Order info' in line) & ('rejected' not in line)&('placeType=odd_sell' not in line):  #  触发并准备下单,odd_sell小单测试过滤掉
                        order_count += 1
                        trade_type = getValueByKeyFromLine(line, by='placeType')
                        order_type = getValueByKeyFromLine(line, by='orderType')

                        action_type = getValueByKeyFromLine(line, by='actionSource')
                        if len(action_type)==0:
                            action_type = 'JupiterN'
                        quantity = getValueByKeyFromLine(line, by='quantity')

                        if len(quantity)==0:
                            print(key_code, 'quantity=', quantity)
                            print(line)
                            if 'firstJupiterOrderQty' in line and 'secondJupiterOrderQty' in line:
                                print('二次下单：%s'%key_code)
                                quantity = float(getValueByKeyFromLine(line, by='firstJupiterOrderQty'))+float(getValueByKeyFromLine(line, by='secondJupiterOrderQty'))
                            else:
                                print('用0填充quantity：%s'%key_code)
                                quantity = 0
                        quantity = float(quantity)

                        if (quantity > 0) & (action_type != 'JupiterNew') & ((trade_type == 'SplitLastShot') | (trade_type == 'JupiterFirstOrder')| (trade_type == 'MRiskSplitLastShotBuy')| (order_type == 'MRiskSplitShot')): # 捕捉jupiter的下单
                            daily_zt_dic['order_direction'] = trade_type
                            daily_zt_dic['quantity'] = getValueByKeyFromLine(line, by='quantity')
                            daily_zt_dic['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                            daily_zt_dic['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                            daily_zt_dic['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                            daily_zt_dic['price'] = getValueByKeyFromLine(line, by='price')
                            daily_zt_dic['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                            daily_zt_dic['totalOrderAmt'] = float(daily_zt_dic['quantity']) * float(daily_zt_dic['price']) * float(daily_zt_dic['splitOrderNum'])#getValueByKeyFromLine(line, by='totalOrderAmt')
                            inf_dic_jupz['totalOrderAmt'] = daily_zt_dic['totalOrderAmt']
                            daily_jupz_ser = pd.Series(daily_zt_dic, name=key_code)
                            daily_jupz_list.append(daily_jupz_ser)
                        if (quantity > 0) & (action_type != 'JupiterNew') & ((trade_type == 'SplitLastShot') | (trade_type == 'JupiterFirstOrder')| (trade_type == 'MRiskSplitLastShotBuy')| (order_type == 'MRiskSplitShot')): # 捕捉jupiter的下单
                            daily_dic_sellv1['order_direction'] = trade_type
                            daily_dic_sellv1['quantity'] = getValueByKeyFromLine(line, by='quantity')
                            daily_dic_sellv1['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                            daily_dic_sellv1['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                            daily_dic_sellv1['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                            daily_dic_sellv1['price'] = getValueByKeyFromLine(line, by='price')
                            daily_dic_sellv1['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                            daily_dic_sellv1['totalOrderAmt'] = float(daily_dic_sellv1['quantity']) * float(daily_dic_sellv1['price']) * float(daily_dic_sellv1['splitOrderNum'])#getValueByKeyFromLine(line, by='totalOrderAmt')
                            inf_dic_931_sellv1['totalOrderAmt'] = daily_dic_sellv1['totalOrderAmt']
                            daily_sellv1_ser = pd.Series(daily_dic_sellv1, name=key_code)
                            daily_list_sellv1.append(daily_sellv1_ser)
                    elif 'Order updated' in line:  # 单子实际的进行情况
                        code = getValueByKeyFromLine(line, by='symbol')
                        if key not in order_info_dic.keys():
                            order_info_dic[key] = []
                        order = {'transactionTime': getValueByKeyFromLine(line, by='transactionTime'),
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
                                 'lastMatchTime': getValueByKeyFromLine(line, by='lastMatchTime'),
                                 'stockcode': code,
                                 'firstTradeIndex': getValueByKeyFromLine(line, by='firstTradeIndex')}
                        order_info_dic[key].append(pd.Series(order))
                    elif 'Order was rejected' in line: # 拒单情况
                        code = getValueByKeyFromLine(line, by='symbol')
                        if key not in unfilled_info_dic.keys():
                            unfilled_info_dic[key] = []
                        unfilled_info = {'riskSummary': getRejectReason(line, by1 = 'riskOperation',by2='riskSummary'),
                                         'riskViolateRemark': getRiskViolateRemark(line, by1='riskViolateRemark'),
                                         'orderSide': getValueByKeyFromLine(line, by='orderSide'),
                                         'stockcode': code,
                                         'transactTime': getValueByKeyFromLine(line, by='transactTime'),\
                                         'riskOperation': getValueByKeyFromLine(line, by='riskOperation'), \
                                         'riskType': getValueByKeyFromLine(line, by='riskType'), \
                                         'MriskFlag':getMriskFlag(line,by1 = 'riskOperation',by2='riskType'),\
                                         'riskInfo': getMriskInfo(line, by1='riskSummary')}
                        unfilled_info_dic[key].append(pd.Series(unfilled_info))

                    elif ('sell factor' in line) & ('sellKey=931' in line):
                        factor_dic_931_sellv1 = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                    elif ('sell factor' in line) & ('sellKey=930' in line):
                        factor_dic_930_sellv1 = trans_str2dic(line[line.index('{'): line.index('}') + 1])

                if key_code in trade_dic.keys():
                    trade_dic[code] = pd.concat(trade_dic[code], axis=1).T
                if key_code in new_trade_dic.keys():
                    new_trade_dic[code] = pd.concat(new_trade_dic[code], axis=1).T
                if key_code in now_trade_dic.keys():
                    print(key_code, code, key_code == code)
                    if key_code == code:
                        now_trade_dic[code] = pd.concat(now_trade_dic[code], axis=1).T
                if key_code in order_info_dic.keys():
                    order_info_dic[code] = pd.concat(order_info_dic[code], axis=1).T
                if key_code in unfilled_info_dic.keys():
                    unfilled_info_dic[code] = pd.concat(unfilled_info_dic[code], axis=1).T

                if len(inf_dic_jupz) != 0:
                    inf_ser = pd.Series(inf_dic_jupz, name=key_code)
                    inf_jupz_list.append(inf_ser)
                if len(inf_dic_931_sellv1) != 0:
                    inf_ser_931 = pd.Series(inf_dic_931_sellv1, name=key_code)
                    inf_list_931_sellv1.append(inf_ser_931)

                if len(factor_dic_jupz) != 0:
                    factor_ser = pd.Series(factor_dic_jupz, name=key_code)
                    factor_list_jupz.append(factor_ser)
                if len(factor_dic_931_sellv1) != 0:
                    factor_ser_931_sell = pd.Series(factor_dic_931_sellv1, name=key_code)
                    factor_list_931_sellv1.append(factor_ser_931_sell)
                if len(factor_dic_930_sellv1) != 0:
                    factor_ser_930_sellv1 = pd.Series(factor_dic_930_sellv1, name=key_code)
                    factor_list_930_sellv1.append(factor_ser_930_sellv1)

        if len(inf_jupz_list) == 0:
            print('没有jupiterZ样本！！！')
            inf_df_jupz = pd.DataFrame()
        else:
            inf_df_jupz = pd.concat(inf_jupz_list, axis=1).T.sort_index()
        if len(inf_list_931_sellv1) == 0:
            print('没有sell样本！！！')
            inf_df_931_sellv1 = pd.DataFrame()
        else:
            inf_df_931_sellv1 = pd.concat(inf_list_931_sellv1, axis=1).T.sort_index()
        if len(inf_list_930_sellv1) == 0:
            print('没有sell样本！！！')
            inf_df_930_sellv1 = pd.DataFrame()
        else:
            inf_df_930_sellv1 = pd.concat(inf_list_930_sellv1, axis=1).T.sort_index()

        if len(factor_list_jupz)==0:
            factor_df_jupz = pd.DataFrame()
        else:
            factor_df_jupz = pd.concat(factor_list_jupz, axis=1).T.sort_index()
        if len(factor_list_931_sellv1) == 0:
            factor_df_931_sellv1 = pd.DataFrame()
        else:
            factor_df_931_sellv1 = pd.concat(factor_list_931_sellv1, axis=1).T.sort_index()
        if len(factor_list_930_sellv1) == 0:
            factor_df_930_sellv1 = pd.DataFrame()
        else:
            factor_df_930_sellv1 = pd.concat(factor_list_930_sellv1, axis=1).T.sort_index()

        if len(daily_jupz_list) != 0:
            daily_df_jupz = pd.concat(daily_jupz_list, axis=1).T.sort_index()
        else:
            daily_df_jupz = pd.DataFrame()
        if len(daily_list_sellv1) != 0:
            daily_df_sellv1 = pd.concat(daily_list_sellv1, axis=1).T.sort_index()
        else:
            daily_df_sellv1 = pd.DataFrame()

        order_info_df = pd.DataFrame()
        for keys, info in order_info_dic.items():
            order_info_df = pd.concat([order_info_df, pd.DataFrame(info)])
        unfilled_info_df = pd.DataFrame()
        for keys, info in unfilled_info_dic.items():
            unfilled_info_df = pd.concat([unfilled_info_df, pd.DataFrame(info)])
        return inf_df_930_sellv1, inf_df_931_sellv1, inf_df_jupz, trade_dic, now_trade_dic, order_info_df, unfilled_info_df, new_trade_dic, \
               factor_df_930_sellv1, factor_df_931_sellv1, factor_df_jupz, \
               all_code_model_data_jupz, all_code_model_data_931_sellv1, \
               daily_df_jupz, daily_df_sellv1