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
from LucienUtil import IO
from ProdWork.CommonTools import excel_saver, ftp_download,ftp_upload,getValueByKeyFromLine, getValueByKeyFromLine2,strTime2MDTime,isException,cal_time_delta,trans_str2dic,getMriskFlag,getRejectReason,getMriskInfo
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
    def get_keys_with_value(selfdict, value, default=None):
        return [k for k, v in selfdict.items() if v == value]

    def getAlgoByalgoFromLine(self, line):
        if self.environment == 'prod_test':
            return line[line.index('StrongStrategy2-algo-') + 21:line.index('-n0]')]
        elif 'test' in self.environment:
            return line[line.index('thread ') + 7:line.index('thread ') + 13]   # TODO:这个位置可能要改，thread的长度不定
        elif (self.environment == 'prod') | ('UAT' in self.environment) | ('night' in self.environment) | (self.environment == 'SHEX') | (self.environment in [ 'SZEX','SZEX_udp', 'SHEX_beta']):
            return line[line.index('EventDrivenStrategy-algo-') + 25:line.index(']')]

    def getAlgoCode(self, line):
        if self.environment == 'prod_test':
            return re.findall(r"StrongStrategy2-algo-(.*)-n0", line)[0]
        elif 'test' in self.environment:
            return re.findall(r"thread (.*?)]", line)[0] # line[line.index('StrongStrategy-StrongStrategy-') + 30:line.index('-n0]')]
        elif (self.environment == 'prod') |  ('night' in self.environment) | (self.environment == 'SHEX') | (self.environment in [ 'SZEX','SZEX_udp', 'SHEX_beta']):
            return re.findall(r"EventDrivenStrategy-algo-(.*?)]", line)[0]
        elif 'UAT' in self.environment:
            return re.findall(r"EventDrivenStrategy-algo-(.*)] INFO", line)[0]
            #return re.findall(r"StrongStrategy-algo-(.*)-n0] INFO  c.h.s.s.StrongAnalyzer - Pause strategy: reason=", line)[0]#)&set(re.findall(r"Pause strategy: reason=",line))

    # TODO:change this
    def getMachineNoFromLine(self,line):
        if  (self.environment == 'UAT_lite') or ('uat_lite' in self.environment):
            return line[line.index('168.') + 4:line.index('-n0]')]
        elif ('UAT' in self.environment) |('night' in self.environment):
            return line[line.index('168.62.') + 7:line.index('-n0]')]
            #return line[line.index('168.') + 4:line.index('-n0]')]
            #return line[line.index('1') + 1:line.index('-n0]')]
        elif self.environment in ['SHEX', 'SHEX_beta']:
            return line[line.index('168.'):line.index(']')]
        elif self.environment == 'SZEX':
            return line[line.index('168.'):line.index(']')]
        elif self.environment == 'SZEX_udp':
            return line[line.index('168.80.') + 7:line.index('-n0]')]
        elif 'test' in self.environment:
            return line[line.index('168.'):line.index(']')]
        else:
            #return line[line.index('1') + 1:line.index('-n0]')]
            return line[line.index('168.') + 7:line.index('-n0]')]

    @staticmethod
    def getSymbolFromStartSuccessLine(line):
        return line[line.index('EventDrivenStrategy-CPP for ') + 28 : line.index(' Version')]

    def openpx_determine(self,x):
        if self.environment == 'prod':
            x = bytes.decode(x,errors='ignore')
            if 'OpenPX' not in x:
                return x
            else:
                #print('OPenPX is in line!!!!')
                return ''
        elif ('UAT' in self.environment) | ('night' in self.environment) | (self.environment == 'SHEX') | (self.environment in ['SZEX','SZEX_udp', 'SHEX_beta']) | ('test' in self.environment):
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

    def filter_triggered_line(self, log_line):
        triggered_lines = list(filter(lambda x: 'Triggered' in str(x), log_line))
        algo_code_set = set()
        for triggered_line in triggered_lines:
            algo_code = self.getAlgoCode(str(triggered_line))
            symbol = getValueByKeyFromLine2(str(triggered_line), by='symbol')
            algo_code_set.add(algo_code + ' ' + symbol)
        print(f'共有{len(algo_code_set)}个实例触发')
        # 这里肯定有symbol了
        log_line_ = list(filter(lambda x: self.getAlgoCode(str(x)) + ' ' + getValueByKeyFromLine2(str(x), by='symbol') in algo_code_set, log_line))
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
        for line in self.lines: # by fengc：根据cpp机器多对多的特性进行修改
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
                # if 'base_context.cpp' in line and 'Start Success' in line:
                if 'Start Success' in line:
                # if ('Pause strategy' in line or 'Pause Strategy' in line) and 'reason=' in line :
                    machine_code = self.getMachineNoFromLine(line)
                    code = self.getSymbolFromStartSuccessLine(line)
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
                key = self.getAlgoByalgoFromLine(line)
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
        algo_dic = {}  # 个股代码对应的实例号
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

    def get_inf_from_log(self, use_zuhe, zuhe_list):
        inf_list = []
        inf_list001 = []
        inf_list_pj2_930 = []
        inf_list_pj2_931 = []
        inf_list_pj2_931_sellv1 = []
        inf_list_pj2_931_sellv3 = []
        inf_list_pj3_930 = []
        inf_list_pj3_931 = []
        factor_list = []
        factor_list_all = []
        factor_list001 = []
        factor_list_all001 = []
        factor_list_pj2_930 = []
        factor_list_pj2_931 = []
        factor_list_pj2_931_sell = []
        factor_list_pj2_930_sell = []
        factor_list_pj3_930 = []
        factor_list_pj3_931 = []
        daily_zt_list = []
        daily_zt_list001 = []
        daily_pj2_list = []
        daily_pj3_list = []
        trade_dic = {}
        now_trade_dic = {}
        new_trade_dic = {}
        order_info_dic = {}
        all_code_model_data = {}
        all_code_model_data001 = {}
        all_code_model_data_pj2_930 = {}
        all_code_model_data_pj2_931 = {}
        all_code_model_data_pj3_930 = {}
        all_code_model_data_pj3_931 = {}
        all_code_model_data_pj2_931_sellv1 ={}
        all_code_model_data_pj2_931_sellv3 = {}
        unfilled_info_dic = {}
        for key, log in self.log_dic.items():
            # key = '20210302-092955-809-0000112-168.62.9.55'
            # log = log_dic[key]
            key_code = self.algo_code_dict[key]
            if key_code != '601688.SH':
                inf_dic = {}
                inf_dic001 = {}
                inf_dic_pj2_930 = {}
                inf_dic_pj2_931 = {}
                inf_dic_pj3_930 = {}
                inf_dic_pj3_931 = {}
                inf_dic_pj2_931_sellv1 = {}
                inf_dic_pj2_931_sellv3 = {}
                factor_dic = {}
                factor_dic_all = {}
                factor_dic001 = {}
                factor_dic_all001 = {}
                factor_dic_pj2_930 = {}
                factor_dic_pj2_931 = {}
                factor_dic_pj3_930 = {}
                factor_dic_pj3_931 = {}
                factor_dic_pj2_931_sell = {}
                factor_dic_pj2_930_sell = {}
                daily_zt_dic = {}
                daily_zt_dic001 = {}
                daily_pj2_dic = {}
                daily_pj3_dic = {}
                daily_pj2_dic_sell = {}
                for line in log:
                    # line = log[0]
                    order_count = 0
                    if ('Calculate factors' in line) & ('saturn' not in line)& ('ceres' not in line)&('JupiterNew' not in line): # jupiter因子耗时
                        inf_dic['factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('Calculate factors' in line) & ('saturn' not in line)& ('ceres' not in line)&('JupiterNew' in line): # jupiter001因子耗时
                        inf_dic001['factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('Triggered' in line) &('JupiterNew' not in line) :# jupiter触发信息
                        print('jupiter triggered', key_code)
                        inf_dic['ZT_Time'] = int(getValueByKeyFromLine(line, by='reachedZTTime'))
                        #inf_dic['ZT_Time'] = int(float(getValueByKeyFromLine(line, by='ZT_Time')))
                        inf_dic['system_time'] = getValueByKeyFromLine(line, by='now')
                        # factor_dic = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')

                    elif ('Triggered' in line) & ('JupiterNew' in line) :# jupiter触发信息
                        print('europa triggered',key_code)
                        inf_dic001['ZT_Time'] = int(float(getValueByKeyFromLine(line, by='reachedZTTime')))
                        #inf_dic001['ZT_Time'] = int(float(getValueByKeyFromLine(line, by='ZT_Time')))
                        inf_dic001['system_time'] = getValueByKeyFromLine(line, by='now')
                        #factor_dic001 = {}
                        # factor_dic001 = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic001 = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')   # TODO: 因子最后格式多了逗号和空格
                    elif ('Total unscaled factors' in line) & ('Saturn' not in line)& ('Ceres' not in line)&('JupiterNew' not in line):# jupiter因子值(nan_scaled)可不用
                        # factor_dic_all = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic_all = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')
                    elif ('Total unscaled factors' in line) & ('Saturn' not in line) & ('Ceres' not in line) & ('JupiterNew' in line):  # jupiter001因子值(nan_scaled)可不用
                        # factor_dic_all001 = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic_all001 = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')
                        #factor_dic_all001={}
                    elif 'nowTrade' in line and 'by SellOrder' not in line:
                        trade_str = line
                        code = getValueByKeyFromLine(trade_str, by='symbol')
                        if code not in now_trade_dic.keys():
                            now_trade_dic[code] = []
                        trade = {
                            # 'TradePrice': float(getValueByKeyFromLine(trade_str, by='price')),
                            #      'TradeQty': float(getValueByKeyFromLine(trade_str, by='quantity')),
                                 # 'TradeMoney': float(getValueByKeyFromLine(trade_str, by='turnover')),    # TODO:少这个turnover
                                 # 'TradeIndex': int(getValueByKeyFromLine(trade_str, by='tradeIndex')),
                                 # 'TradeBuyNo': int(getValueByKeyFromLine(trade_str, by='tradeBuyNo')),
                                 # 'TradeSellNo': int(getValueByKeyFromLine(trade_str, by='tradeSellNo')),
                                 # 'TradeBSFlag': (getValueByKeyFromLine(trade_str, by='side') == 'Offer') + 1,
                                 # 'TradeType': int(getValueByKeyFromLine(trade_str, by='type') == 'Canceled'),
                                 # 'MDTime': strTime2MDTime(getValueByKeyFromLine(trade_str, by='nowTradeTimestamp')),
                                 'MDTime': getValueByKeyFromLine(trade_str, by='nowTradeTimestamp')}    # TODO：MDTime有变化
                        now_trade_dic[code].append(pd.Series(trade))
                    elif 'New trade' in line:
                        trade_str = line
                        code = getValueByKeyFromLine(trade_str, by='symbol')
                        if code not in new_trade_dic.keys():
                            new_trade_dic[code] = []
                        trade = {'TradePrice': float(getValueByKeyFromLine(trade_str, by='price')),
                                 'TradeQty': float(getValueByKeyFromLine(trade_str, by='quantity')),
                                 'TradeMoney': float(getValueByKeyFromLine(trade_str, by='turnover')),
                                 'TradeIndex': int(getValueByKeyFromLine(trade_str, by='tradeIndex')),
                                 'TradeBuyNo': int(getValueByKeyFromLine(trade_str, by='tradeBuyNo')),
                                 'TradeSellNo': int(getValueByKeyFromLine(trade_str, by='tradeSellNo')),
                                 'TradeBSFlag': (getValueByKeyFromLine(trade_str, by='side') == 'Offer') + 1,
                                 'TradeType': int(getValueByKeyFromLine(trade_str, by='type') == 'Canceled'),
                                 'log_ReceiveDateTime': trade_str[11:13] + trade_str[14:16] + trade_str[17:19] + trade_str[20:23]}
                        new_trade_dic[code].append(pd.Series(trade))
                    # elif 'Last1MinTrade' in line:
                    #     trade_str_raw = line
                    #     code = getValueByKeyFromLine(line, by='symbol')
                    #     if code not in trade_dic.keys():
                    #        trade_dic[code] = []
                    #     trade_str_start = trade_str_raw[trade_str_raw.index('startTrade=Trade ') + 17:trade_str_raw.index(', endTrade=Trade')]
                    #     trade_str_end = trade_str_raw[trade_str_raw.index(', endTrade=Trade') + 16:]
                    #     for trade_str_sub in (trade_str_start,trade_str_end):
                    #        trade = {'TradePrice': float(getValueByKeyFromLine(trade_str_sub, by='price')),
                    #                 'TradeQty': float(getValueByKeyFromLine(trade_str_sub, by='quantity')),
                    #                 'TradeMoney': float(getValueByKeyFromLine(trade_str_sub, by='turnover')),
                    #                 'TradeIndex': int(getValueByKeyFromLine(trade_str_sub, by='tradeIndex')),
                    #                 'TradeBuyNo': int(getValueByKeyFromLine(trade_str_sub, by='tradeBuyNo')),
                    #                 'TradeSellNo': int(getValueByKeyFromLine(trade_str_sub, by='tradeSellNo')),
                    #                 'TradeBSFlag': (getValueByKeyFromLine(trade_str_sub, by='side') == 'Offer') + 1,
                    #                 'TradeType': int(getValueByKeyFromLine(trade_str_sub, by='type') == 'Canceled'),
                    #                 'MDTime': strTime2MDTime(trade_str_sub[~27:]),
                    #                 'log_ReceiveDateTime': trade_str_raw[11:13] + trade_str_raw[14:16] + trade_str_raw[17:19] + trade_str_raw[20:23]}
                    #        trade_dic[code].append(pd.Series(trade))
                    elif ('Model prediction' in line) & ('parentPath' not in line) & ('Saturn' not in line)& ('Ceres' not in line)&('JupiterNew' not in line): # jupiter集成模型预测
                        inf_dic['shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldBuySignal')
                        print(key_code, 'jupiter')
                        inf_dic['model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('Model prediction' in line) & ('parentPath' not in line) & ('Saturn' not in line)& ('Ceres' not in line)&('JupiterNew' in line): # jupiter集成模型预测
                        inf_dic001['shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldBuySignal')
                        print(key_code, 'jupiter001')
                        inf_dic001['model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('riskSummary' in line) & ('拉抬打压' in line) & ('Saturn' not in line)& ('Ceres' not in line):
                        inf_dic['MRisk_info'] = '触发拉抬打压'#getValueByKeyFromLine(line,by='riskSummary') # int(getValueByKeyFromLine(line, by='timeCost'))
                        inf_dic001['MRisk_info'] = '触发拉抬打压'
                        print(key_code, inf_dic['MRisk_info'])
                    elif 'isMock' in line:
                        inf_dic['isMock'] = getValueByKeyFromLine(line,by='isMock') # int(getValueByKeyFromLine(line, by='timeCost'))
                        inf_dic001['isMock'] = getValueByKeyFromLine(line,by='isMock') # int(getValueByKeyFromLine(line, by='timeCost'))
                        #print(key_code, inf_dic['isMock'])
                    elif ('isSkip' in line) & ('Saturn' not in line) & ('Ceres' not in line):
                        inf_dic['isSkip'] = getValueByKeyFromLine(line,by='isSkip')  # int(getValueByKeyFromLine(line, by='timeCost'))
                        inf_dic001['isSkip'] = getValueByKeyFromLine(line,by='isSkip')  # int(getValueByKeyFromLine(line, by='timeCost'))
                        #print(key_code, inf_dic['MRisk_info'])
                    # elif ('riskSummary' in line) & ('非50成分股-拉抬打压' in line) & ('Saturn' not in line)& ('Ceres' not in line):
                    #     inf_dic001['MRisk_info'] = '触发拉抬打压'#getValueByKeyFromLine(line,by='riskSummary') # int(getValueByKeyFromLine(line, by='timeCost'))
                    #     print(key_code, 'jupiter001', inf_dic001['MRisk_info'])
                    elif ('predict signals' in line)& ('parentPath' not in line) & ('saturn' not in line)& ('ceres' not in line)& ('Saturn' not in line)& ('Ceres' not in line)&('JupiterNew' not in line): # jupiterN集成模型预测
                        inf_dic['sum_signals'] = getValueByKeyFromLine(line, by='predict signals')
                    elif ('ZT Model predict' in line)& ('parentPath' not in line) & ('saturn' not in line)& ('ceres' not in line)& ('Saturn' not in line)& ('Ceres' not in line): # jupiterZ集成模型预测
                        inf_dic['sum_signals'] = getValueByKeyFromLine(line, by='sum_signals')
                    elif ('predict signals' in line)& ('parentPath' not in line) & ('saturn' not in line)& ('ceres' not in line)& ('Saturn' not in line)& ('Ceres' not in line)&('JupiterNew' in line): # jupiter001集成模型预测
                        inf_dic001['sum_signals'] = getValueByKeyFromLine(line, by='predict signals')
                    elif ('saturn Model prediction' in line) & ('parentPath' in line) & ('sellKey=930' in line): # saturn930子模型预测
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data_pj2_930.keys():
                            all_code_model_data_pj2_930[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic_pj2_930[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('saturn Model prediction' in line) & ('parentPath' in line) & ('saturnKey=931' in line):# saturn931子模型预测
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data_pj2_931.keys():
                            all_code_model_data_pj2_931[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic_pj2_931[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('sell Model prediction' in line) & ('parentPath' in line) & ('sellKey=931' in line) &('modelGroup=v1' in line):# sellv1子模型预测
                        print('sell1')
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data_pj2_931_sellv1.keys():
                            all_code_model_data_pj2_931_sellv1[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic_pj2_931_sellv1[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('sell Model prediction' in line) & ('parentPath' in line) & ('sellKey=931' in line) &('modelGroup=v3' in line):# sellv1子模型预测
                        print('sell3')
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data_pj2_931_sellv3.keys():
                            all_code_model_data_pj2_931_sellv3[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic_pj2_931_sellv3[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('saturn model predict sum_signals' in line) &  ('parentPath' not in line) & ('saturnKey=930' in line):
                        inf_dic_pj2_930['sum_signals'] = getValueByKeyFromLine(line, by='sum_signals')
                    elif ('saturn model predict sum_signals' in line) &  ('parentPath' not in line) & ('saturnKey=931' in line):
                        inf_dic_pj2_931['sum_signals'] = getValueByKeyFromLine(line, by='sum_signals')
                    elif ('sell model predict' in line) &  ('parentPath' not in line) & ('sellKey=931' in line)&('timeCost' not in line):
                        inf_dic_pj2_931_sellv1['sum_signals'] = getValueByKeyFromLine(line, by='v1Signals')
                        inf_dic_pj2_931_sellv3['sum_signals'] = getValueByKeyFromLine(line, by='v3Signals')
                    elif ('ceres Model prediction' in line) & ('parentPath' in line) & ('ceresKey=930' in line):# ceres930子模型预测
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data_pj3_930.keys():
                            all_code_model_data_pj3_930[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic_pj3_930[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('ceres Model prediction' in line) & ('parentPath' in line) & ('ceresKey=931' in line):# ceres931子模型预测
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data_pj3_931.keys():
                            all_code_model_data_pj3_931[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic_pj3_931[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('ceres model predict sum_signals' in line) &  ('parentPath' not in line) & ('ceresKey=930' in line):
                        inf_dic_pj3_930['sum_signals'] = getValueByKeyFromLine(line, by='sum_signals')
                    elif ('ceres model predict sum_signals' in line) &  ('parentPath' not in line) & ('ceresKey=931' in line):
                        inf_dic_pj3_931['sum_signals'] = getValueByKeyFromLine(line, by='sum_signals')
                    elif ('parentPath' in line) & ('Single model' not in line) & ('Saturn' not in line)& ('Ceres' not in line)&('JupiterNew' not in line):# Jupiter子模型预测

                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data.keys():
                            all_code_model_data[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        #print('Jupiter: Single model, parentPath !!!!查看样例', model_name,code)
                        inf_dic[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('parentPath' in line) & ('Single model' not in line) & ('Saturn' not in line)& ('Ceres' not in line)&('JupiterNew' in line):# Jupiter子模型预测

                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data001.keys():
                            all_code_model_data001[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        # print('Jupiter: Single model, parentPath !!!!查看样例', model_name,code)
                        inf_dic001[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')
                    elif ('parentPath' in line) & ('Single model predict timeCost' in line):  # 进不来,计算其中一个的耗时
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        time_cost = int(getValueByKeyFromLine(line, by='Single model predict timeCost'))
                        if model_name + '_tot_time_cost' in inf_dic.keys():
                            inf_dic[model_name + '_tot_time_cost'] = inf_dic[model_name + '_tot_time_cost'] + time_cost
                        else:
                            inf_dic[model_name + '_tot_time_cost'] = time_cost
                        # print('Jupiter: Single model predict timeCost, parentPath !!!!查看样例', model_name, time_cost)
                    elif ('parentPath' in line) & ('Single model scale timeCost' in line):  # 进不来,计算另一类耗时并加和
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        time_cost = int(getValueByKeyFromLine(line, by='Single model scale timeCost'))
                        if model_name + '_tot_time_cost' in inf_dic.keys():
                            inf_dic[model_name + '_tot_time_cost'] = inf_dic[model_name + '_tot_time_cost'] + time_cost
                        else:
                            inf_dic[model_name + '_tot_time_cost'] = time_cost
                        # print('Jupiter: Single model scale timeCost, parentPath !!!!查看样例', model_name, time_cost)

                    elif ('Order info' in line) & ('rejected' not in line)&('placeType=odd_sell' not in line):  #  触发并准备下单,odd_sell小单测试过滤掉
                        order_count += 1
                        trade_type = getValueByKeyFromLine(line, by='placeType')
                        order_type = getValueByKeyFromLine(line, by='orderType')

                        #if self.environment == 'UAT':
                        action_type = getValueByKeyFromLine(line, by='actionSource')
                        if len(action_type)==0:
                            action_type = 'JupiterN'
                        quantity = getValueByKeyFromLine(line, by='quantity')

                        #print(key_code,'quantity=',quantity)
                        if len(quantity)==0:# or isinstance(quantity,str):
                            print(key_code, 'quantity=', quantity)
                            print(line)
                            if 'firstJupiterOrderQty' in line and 'secondJupiterOrderQty' in line:
                                print('二次下单：%s'%key_code)
                                quantity = float(getValueByKeyFromLine(line, by='firstJupiterOrderQty'))+float(getValueByKeyFromLine(line, by='secondJupiterOrderQty'))
                            else:
                                print('用0填充quantity：%s'%key_code)
                                quantity = 0
                        quantity = float(quantity)

                        # if (trade_type != 'A_normal') & (trade_type != 'A_ma') & (trade_type != 'odd_sell') \
                        #         & (trade_type != 'B_low_cover') & (trade_type != 'A_downlimit'):(float(quantity)>0)&
                        if (quantity>0)&(action_type != 'JupiterNew')&((trade_type == 'SplitLastShot') | (trade_type == 'JupiterFirstOrder')| (trade_type == 'MRiskSplitLastShotBuy')| (order_type == 'MRiskSplitShot')): # 捕捉jupiter的下单
                            daily_zt_dic['order_direction'] = trade_type
                            daily_zt_dic['quantity'] = getValueByKeyFromLine(line, by='quantity')
                            daily_zt_dic['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                            daily_zt_dic['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                            daily_zt_dic['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                            daily_zt_dic['price'] = getValueByKeyFromLine(line, by='price')
                            daily_zt_dic['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                            daily_zt_dic['totalOrderAmt'] = float(daily_zt_dic['quantity'])*float(daily_zt_dic['price'])*float(daily_zt_dic['splitOrderNum'])#getValueByKeyFromLine(line, by='totalOrderAmt')
                            inf_dic['totalOrderAmt'] = daily_zt_dic['totalOrderAmt']
                            daily_zt_ser = pd.Series(daily_zt_dic, name=key_code)
                            daily_zt_list.append(daily_zt_ser)
                        elif (action_type == 'JupiterNew')& ((trade_type == 'SplitLastShot') | (trade_type == 'JupiterFirstOrder')| (trade_type == 'MRiskSplitLastShotBuy')| (order_type == 'MRiskSplitShot')): # 捕捉jupiter001的下单
                            daily_zt_dic001['order_direction'] = trade_type
                            daily_zt_dic001['quantity'] = getValueByKeyFromLine(line, by='quantity')
                            daily_zt_dic001['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                            daily_zt_dic001['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                            daily_zt_dic001['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                            daily_zt_dic001['price'] = getValueByKeyFromLine(line, by='price')
                            daily_zt_dic001['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                            daily_zt_dic001['totalOrderAmt'] = float(daily_zt_dic001['quantity'])*float(daily_zt_dic001['price'])*float(daily_zt_dic001['splitOrderNum'])#getValueByKeyFromLine(line, by='totalOrderAmt')
                            inf_dic001['totalOrderAmt'] = daily_zt_dic001['totalOrderAmt']
                            daily_zt_ser001 = pd.Series(daily_zt_dic001, name=key_code)
                            daily_zt_list001.append(daily_zt_ser001)
                        elif trade_type == 'A' and order_type == 'SaturnBuy':
                            daily_pj2_dic['order_direction'] = trade_type
                            daily_pj2_dic['quantity'] = getValueByKeyFromLine(line, by='quantity')
                            daily_pj2_dic['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                            daily_pj2_dic['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                            daily_pj2_dic['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                            daily_pj2_dic['price'] = getValueByKeyFromLine(line, by='price')
                            daily_pj2_dic['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                            daily_pj2_dic['totalOrderAmt'] = getValueByKeyFromLine(line, by='totalOrderAmt')
                            daily_pj2_ser = pd.Series(daily_pj2_dic, name=key_code)
                            daily_pj2_list.append(daily_pj2_ser)
                        elif trade_type == 'A'and order_type == 'CeresBuy':
                            daily_pj3_dic['order_direction'] = trade_type
                            daily_pj3_dic['quantity'] = getValueByKeyFromLine(line, by='quantity')
                            daily_pj3_dic['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                            daily_pj3_dic['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                            daily_pj3_dic['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                            daily_pj3_dic['price'] = getValueByKeyFromLine(line, by='price')
                            daily_pj3_dic['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                            daily_pj3_dic['totalOrderAmt'] = getValueByKeyFromLine(line, by='totalOrderAmt')
                            daily_pj3_ser = pd.Series(daily_pj3_dic, name=key_code)
                            daily_pj3_list.append(daily_pj3_ser)
                    elif 'set current saturn target amt' in line:
                        inf_dic_pj2_931['totalOrderAmt'] = getValueByKeyFromLine(line, by='currentSaturnTargetAmt')
                    elif 'set current ceres target amt' in line:
                        inf_dic_pj3_931['totalOrderAmt'] = getValueByKeyFromLine(line, by='currentCeresTargetAmt')
                    elif 'Order updated' in line:  # 单子实际的进行情况
                        code = getValueByKeyFromLine(line, by='symbol')
                        if code not in order_info_dic.keys():
                            order_info_dic[code] = []
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
                        order_info_dic[code].append(pd.Series(order))
                    elif 'Order was rejected' in line: # 拒单情况
                        code = getValueByKeyFromLine(line, by='symbol')
                        if code not in unfilled_info_dic.keys():
                            unfilled_info_dic[code] = []
                        unfilled_info = {'riskSummary': getRejectReason(line, by1 = 'riskOperation',by2='riskSummary'),
                                         'orderSide': getValueByKeyFromLine(line, by='orderSide'),
                                         'stockcode': code,
                                         'transactTime': getValueByKeyFromLine(line, by='transactTime'),\
                                         'riskOperation': getValueByKeyFromLine(line, by='riskOperation'), \
                                         'riskType': getValueByKeyFromLine(line, by='riskType'), \
                                         'MriskFlag':getMriskFlag(line,by1 = 'riskOperation',by2='riskType'),\
                                         'riskInfo': getMriskInfo(line, by1='riskSummary')}
                        unfilled_info_dic[code].append(pd.Series(unfilled_info))
                    elif ('market data stat info' in line) &('JupiterNew' not in line)  :
                        inf_dic['filledTradeList'] = getValueByKeyFromLine(line, by='filledTradeList', form='(.*?)[;\n]')
                        inf_dic['lxjjFillList'] = getValueByKeyFromLine(line, by='lxjjFillList', form='(.*?)[;\n]')
                        inf_dic['last5SecFillList'] = getValueByKeyFromLine(line, by='last5SecFillList', form='(.*?)[;\n]')
                        inf_dic['last30SecFillList'] = getValueByKeyFromLine(line, by='last30SecFillList', form='(.*?)[;\n]')
                        inf_dic['last2MinFillList'] = getValueByKeyFromLine(line, by='last2MinFillList', form='(.*?)[;\n]')
                        inf_dic['last5MinFillList'] = getValueByKeyFromLine(line, by='last5MinFillList', form='(.*?)[;\n]')
                    elif ('market data stat info' in line) &('JupiterNew' in line)  :
                        inf_dic001['filledTradeList'] = getValueByKeyFromLine(line, by='filledTradeList', form='(.*?)[;\n]')
                        inf_dic001['lxjjFillList'] = getValueByKeyFromLine(line, by='lxjjFillList', form='(.*?)[;\n]')
                        inf_dic001['last5SecFillList'] = getValueByKeyFromLine(line, by='last5SecFillList', form='(.*?)[;\n]')
                        inf_dic001['last30SecFillList'] = getValueByKeyFromLine(line, by='last30SecFillList', form='(.*?)[;\n]')
                        inf_dic001['last2MinFillList'] = getValueByKeyFromLine(line, by='last2MinFillList', form='(.*?)[;\n]')
                        inf_dic001['last5MinFillList'] = getValueByKeyFromLine(line, by='last5MinFillList', form='(.*?)[;\n]')
                    ########################### saturn930模型信息 ###########################
                    elif ('saturn factor' in line) & ('saturnKey=930' in line): # saturn930T日因子
                        # factor_dic_pj2_930 = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic_pj2_930 = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')
                    elif ('saturn calculate factors' in line) & ('saturnKey=930' in line):# saturn930因子耗时
                        inf_dic_pj2_930['p2factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('saturn Model prediction' in line) & ('parentPath' not in line) & (
                            'saturnKey=930' in line):# saturn930集成信号预测
                        inf_dic_pj2_930['p2shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldBuySignal')
                        print(key_code, '930')
                        inf_dic_pj2_930['p2model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    ########################### saturn931模型信息 ###########################
                    elif ('saturn factor' in line) & ('saturnKey=931' in line):# saturn931T日因子
                        # factor_dic_pj2_931 = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic_pj2_931 = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')
                    elif ('saturn calculate factors' in line) & ('saturnKey=931' in line):
                        inf_dic_pj2_931['p2factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('sell factor' in line) & ('sellKey=931' in line):# saturn931T日因子
                        # factor_dic_pj2_931_sell = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic_pj2_931_sell = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')
                    elif ('sell factor' in line) & ('sellKey=930' in line):# saturn931T日因子
                        # factor_dic_pj2_930_sell = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic_pj2_930_sell = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')
                    elif ('sell calculate factors' in line) & ('sellKey=931' in line):
                        inf_dic_pj2_931_sellv1['sellfactor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                        inf_dic_pj2_931_sellv3['sellfactor_time_cost'] = float(getValueByKeyFromLine(line,by='timeCost'))  # int(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('saturn Model prediction' in line) & ('parentPath' not in line) & (
                            'saturnKey=931' in line):
                        inf_dic_pj2_931['p2shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldBuySignal')
                        print(key_code, '931')
                        inf_dic_pj2_931['p2model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('sell Model prediction' in line) & ('parentPath' not in line) & ('sellKey=931' in line)&('timeCost' in line):
                        inf_dic_pj2_931_sellv1['sellmodel_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                        inf_dic_pj2_931_sellv3['sellmodel_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))
                    # elif ('sell Model prediction' in line) & ('parentPath' not in line) & (
                    #         'sellKey=931' in line):
                    #     inf_dic_pj2_931_sellv1['sell1shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldSellSignal')
                    #     inf_dic_pj2_931_sellv3['sell3shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldSellSignal')
                    #     print(key_code, '931')
                    #     inf_dic_pj2_931_sellv1['sellmodel_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    ########################### ceres930模型信息 ###########################
                    elif ('ceres factor' in line) & ('ceresKey=930' in line):
                        # factor_dic_pj3_930 = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic_pj3_930 = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')
                    elif ('ceres calculate factors' in line) & ('ceresKey=930' in line):
                        inf_dic_pj3_930['p3factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('ceres Model prediction' in line) & ('parentPath' not in line) & (
                            'ceresKey=930' in line):
                        inf_dic_pj3_930['p3shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldBuySignal')
                        print(key_code, 'ceres930')
                        inf_dic_pj3_930['p3model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    ########################### ceres930模型信息 ###########################
                    elif ('ceres factor' in line) & ('ceresKey=931' in line):
                        # factor_dic_pj3_931 = trans_str2dic(line[line.index('{'): line.index('}') + 1])
                        factor_dic_pj3_931 = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')
                    elif ('ceres calculate factors' in line) & ('ceresKey=931' in line):
                        inf_dic_pj3_931['p3factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))
                    elif ('ceres Model prediction' in line) & ('parentPath' not in line) & ('ceresKey=931' in line):
                        inf_dic_pj3_931['p3shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldBuySignal')
                        print(key_code, 'ceres931')
                        inf_dic_pj3_931['p3model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))#int(getValueByKeyFromLine(line, by='timeCost'))

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
                # print(len(inf_dic))
                if len(inf_dic) != 0:
                    inf_ser = pd.Series(inf_dic, name=key_code)
                    inf_list.append(inf_ser)
                if len(inf_dic001) != 0:
                    inf_ser001 = pd.Series(inf_dic001, name=key_code)
                    inf_list001.append(inf_ser001)
                if len(inf_dic_pj2_930) != 0:
                    inf_ser_pj2_930 = pd.Series(inf_dic_pj2_930, name=key_code)
                    inf_list_pj2_930.append(inf_ser_pj2_930)
                if len(inf_dic_pj2_931) != 0:
                    inf_ser_pj2_931 = pd.Series(inf_dic_pj2_931, name=key_code)
                    inf_list_pj2_931.append(inf_ser_pj2_931)
                if len(inf_dic_pj2_931_sellv1) != 0:
                    inf_ser_pj2_931 = pd.Series(inf_dic_pj2_931_sellv1, name=key_code)
                    inf_list_pj2_931_sellv1.append(inf_ser_pj2_931)
                if len(inf_dic_pj2_931_sellv3) != 0:
                    inf_ser_pj2_931 = pd.Series(inf_dic_pj2_931_sellv3, name=key_code)
                    inf_list_pj2_931_sellv3.append(inf_ser_pj2_931)
                if len(inf_dic_pj3_930) != 0:
                    inf_ser_pj3_930 = pd.Series(inf_dic_pj3_930, name=key_code)
                    inf_list_pj3_930.append(inf_ser_pj3_930)
                if len(inf_dic_pj3_931) != 0:
                    inf_ser_pj3_931 = pd.Series(inf_dic_pj3_931, name=key_code)
                    inf_list_pj3_931.append(inf_ser_pj3_931)

                factor_dic = factor_dic_all
                factor_dic001 = factor_dic_all001

                if len(factor_dic) != 0:
                    factor_ser = pd.Series(factor_dic, name=key_code)
                    factor_list.append(factor_ser)
                if len(factor_dic_all) != 0:
                    factor_ser_all = pd.Series(factor_dic_all, name=key_code)
                    factor_list_all.append(factor_ser_all)
                if len(factor_dic001) != 0:
                    factor_ser001 = pd.Series(factor_dic001, name=key_code)
                    factor_list001.append(factor_ser001)
                if len(factor_dic_all001) != 0:
                    factor_ser_all001 = pd.Series(factor_dic_all001, name=key_code)
                    factor_list_all001.append(factor_ser_all001)
                if len(factor_dic_pj2_930) != 0:
                    factor_ser_pj2_930 = pd.Series(factor_dic_pj2_930, name=key_code)
                    factor_list_pj2_930.append(factor_ser_pj2_930)
                if len(factor_dic_pj2_931) != 0:
                    factor_ser_pj2_931 = pd.Series(factor_dic_pj2_931, name=key_code)
                    factor_list_pj2_931.append(factor_ser_pj2_931)
                if len(factor_dic_pj2_931_sell) != 0:
                    factor_ser_pj2_931_sell = pd.Series(factor_dic_pj2_931_sell, name=key_code)
                    factor_list_pj2_931_sell.append(factor_ser_pj2_931_sell)
                if len(factor_dic_pj2_930_sell) != 0:
                    factor_ser_pj2_930_sell = pd.Series(factor_dic_pj2_930_sell, name=key_code)
                    factor_list_pj2_930_sell.append(factor_ser_pj2_930_sell)
                if len(factor_dic_pj3_930) != 0:
                    factor_ser_pj3_930 = pd.Series(factor_dic_pj3_930, name=key_code)
                    factor_list_pj3_930.append(factor_ser_pj3_930)
                if len(factor_dic_pj3_931) != 0:
                    factor_ser_pj3_931 = pd.Series(factor_dic_pj3_931, name=key_code)
                    factor_list_pj3_931.append(factor_ser_pj3_931)
        if len(inf_list) == 0:
            print('没有jupiter样本！！！')
            inf_df = pd.DataFrame()
        else:
            inf_df = pd.concat(inf_list, axis=1).T.sort_index()
        if len(inf_list001) == 0:
            print('没有jupiter001样本！！！')
            inf_df001 = pd.DataFrame()
        else:
            inf_df001 = pd.concat(inf_list001, axis=1).T.sort_index()
        if len(inf_list_pj2_930) == 0:
            print('没有saturn930样本！！！')
            inf_df_pj2_930 = pd.DataFrame()
        else:
            inf_df_pj2_930 = pd.concat(inf_list_pj2_930, axis=1).T.sort_index()
        if len(inf_list_pj2_931) == 0:
            print('没有saturn931样本！！！')
            inf_df_pj2_931 = pd.DataFrame()
        else:
            inf_df_pj2_931 = pd.concat(inf_list_pj2_931, axis=1).T.sort_index()
        if len(inf_list_pj2_931_sellv1) == 0:
            print('没有sell样本！！！')
            inf_df_pj2_931_sellv1 = pd.DataFrame()
        else:
            inf_df_pj2_931_sellv1 = pd.concat(inf_list_pj2_931_sellv1, axis=1).T.sort_index()
        if len(inf_list_pj2_931_sellv3) == 0:
            print('没有sell样本！！！')
            inf_df_pj2_931_sellv3 = pd.DataFrame()
        else:
            inf_df_pj2_931_sellv3 = pd.concat(inf_list_pj2_931_sellv3, axis=1).T.sort_index()
        if len(inf_list_pj3_930) == 0:
            print('没有ceres930样本！！！')
            inf_df_pj3_930 = pd.DataFrame()
        else:
            inf_df_pj3_930 = pd.concat(inf_list_pj3_930, axis=1).T.sort_index()
        if len(inf_list_pj3_931) == 0:
            print('没有ceres931样本！！！')
            inf_df_pj3_931 = pd.DataFrame()
        else:
            inf_df_pj3_931 = pd.concat(inf_list_pj3_931, axis=1).T.sort_index()
        if len(factor_list)==0:
            factor_df=pd.DataFrame()
        else:
            factor_df = pd.concat(factor_list, axis=1).T.sort_index()
        if len(factor_list001)==0:
            factor_df001=pd.DataFrame()
        else:
            factor_df001 = pd.concat(factor_list001, axis=1).T.sort_index()
        if len(factor_list_pj2_930) ==0:
            factor_df_pj2_930 = pd.DataFrame()
        else:
            factor_df_pj2_930 = pd.concat(factor_list_pj2_930, axis=1).T.sort_index()
        if len(factor_list_pj2_931) == 0:
            factor_df_pj2_931 = pd.DataFrame()
        else:
            factor_df_pj2_931 = pd.concat(factor_list_pj2_931, axis=1).T.sort_index()
        if len(factor_list_pj2_931_sell) == 0:
            factor_df_pj2_931_sell = pd.DataFrame()
        else:
            factor_df_pj2_931_sell = pd.concat(factor_list_pj2_931_sell, axis=1).T.sort_index()
        if len(factor_list_pj2_930_sell) == 0:
            factor_df_pj2_930_sell = pd.DataFrame()
        else:
            factor_df_pj2_930_sell = pd.concat(factor_list_pj2_930_sell, axis=1).T.sort_index()
        if len(factor_list_pj3_930) ==0:
            factor_df_pj3_930 = pd.DataFrame()
        else:
            factor_df_pj3_930 = pd.concat(factor_list_pj3_930, axis=1).T.sort_index()
        if len(factor_list_pj3_931) == 0:
            factor_df_pj3_931 = pd.DataFrame()
        else:
            factor_df_pj3_931 = pd.concat(factor_list_pj3_931, axis=1).T.sort_index()
        if len(daily_zt_list) != 0:
            daily_zt_df = pd.concat(daily_zt_list, axis=1).T.sort_index()
        else:
            daily_zt_df = pd.DataFrame()
        if len(daily_zt_list001) != 0:
            daily_zt_df001 = pd.concat(daily_zt_list001, axis=1).T.sort_index()
        else:
            daily_zt_df001 = pd.DataFrame()
        if len(daily_pj2_list) != 0:
            daily_pj2_df = pd.concat(daily_pj2_list, axis=1).T.sort_index()
        else:
            daily_pj2_df = pd.DataFrame()
        if len(daily_pj3_list) != 0:
            daily_pj3_df = pd.concat(daily_pj3_list, axis=1).T.sort_index()
        else:
            daily_pj3_df = pd.DataFrame()
        order_info_df = pd.DataFrame()
        for keys, info in order_info_dic.items():
            order_info_df = pd.concat([order_info_df, pd.DataFrame(info)])
        unfilled_info_df = pd.DataFrame()
        for keys, info in unfilled_info_dic.items():
            unfilled_info_df = pd.concat([unfilled_info_df, pd.DataFrame(info)])
        return inf_df, inf_df_pj2_930, inf_df_pj2_931, factor_df, trade_dic, now_trade_dic, all_code_model_data, all_code_model_data_pj2_930, all_code_model_data_pj2_931, daily_zt_df, daily_pj2_df, \
               order_info_df, unfilled_info_df, factor_df_pj2_930, \
               factor_df_pj2_931, new_trade_dic,factor_df_pj3_931,inf_df_pj3_931,factor_df_pj3_930,inf_df_pj3_930,daily_pj3_df,inf_df001,factor_df001,all_code_model_data001,daily_zt_df001, \
               inf_df_pj2_931_sellv1,inf_df_pj2_931_sellv3,all_code_model_data_pj2_931_sellv1,all_code_model_data_pj2_931_sellv3,factor_df_pj2_931_sell,factor_df_pj2_930_sell