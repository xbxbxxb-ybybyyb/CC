# -*- coding: utf-8 -*-

import pandas as pd
import re
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
import warnings
warnings.filterwarnings('ignore')
from ProdWork.CommonTools import getValueByKeyFromLine, getValueByKeyFromLine2,isException,trans_str2dic,getMriskFlag,getRejectReason,getMriskInfo, format_unix2dt, getRiskViolateRemark


class LogParse:
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

    def getAlgoByalgoFromLine(self, line):
        try:
            return re.findall(r"algo-(.*?)]", line)[0]
        except:
            return re.findall(r"Thread (.*?)]", line)[0]

    def getAlgoCode(self, line):
        try:
            return re.findall(r"algo-(.*?)]", line)[0]
        except:
            return re.findall(r"Thread (.*?)]", line)[0]

    # TODO:change this
    def getMachineNoFromLine(self,line):
        try:
            pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
            res = pattern.findall(line)
            res = res[0]
        except:
            res = '192.168.0.1'
        return res

    @staticmethod
    def getSymbolFromStartSuccessLine(line):
        return line[line.index('UniTradeTool-CPP for ') + 29 : line.index(' Version')]

    @staticmethod
    def openpx_determine(x):
        if type(x) != str:
            x = bytes.decode(x, errors='ignore')

        if 'OpenPX' not in x:
            return x
        else:
            return ''

    @staticmethod
    def algocode2code(x, algo_dic):
        try:
            code = algo_dic[x]
            return code
        except KeyError:
            return ''

    @staticmethod
    def filter_wrong_lastMatchTime_line(line):
        if 'Order updated' in line:
            if len(getValueByKeyFromLine(line, by='lastMatchTime')) < 10:
                return False
        return True

    def filter_triggered_line(self, log_line):
        triggered_lines = list(filter(lambda x: 'handle_buy_info' in str(x), log_line))

        algo_code_set = set()
        for triggered_line in triggered_lines:
            algo_code = self.getAlgoCode(str(triggered_line))
            symbol = getValueByKeyFromLine2(str(triggered_line), by='symbol')
            algo_code_set.add(algo_code + ' ' + symbol)

        print(f'共有{len(algo_code_set)}个实例触发')
        # 这里肯定有symbol了
        # log_line_ = list(filter(lambda x: self.getAlgoCode(str(x)) + ' ' + getValueByKeyFromLine2(str(x), by='symbol') in algo_code_set, log_line))
        log_line_ = list(filter(lambda x: 'symbol=' in str(x) or 'Symbol=' in str(x), log_line))
        if type(log_line_[0]) != str:
            log_line_ = list(map(lambda x: bytes.decode(x, errors='ignore'), log_line_))
        print(f'非本实例触发票删除完毕，之前{len(log_line)}行，现在{len(log_line_)}行')
        return log_line_

    def get_algo_code_dict(self):
        algo_code_dict = {}
        selcode = []
        for line in self.lines:
            line = str(line)
            try:
                algo_code = self.getAlgoCode(str(line))
                code = getValueByKeyFromLine2(line, by='symbol')
                if ('symbol=' in line) & (algo_code + ' ' + code not in algo_code_dict.keys()):
                    if code in list(algo_code_dict.values()):
                        selcode = list(set(selcode + [code]))
                        print(code, algo_code)
                        pass
                    algo_code_dict[algo_code + ' ' + code] = code
            except IndexError:
                pass
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

        for line in self.lines:
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

    def start_parsing(self):
        inf_list_utt = []
        daily_zt_utt_list = []
        order_info_dic = {}
        unfilled_info_dic = {}
        target_amt_dic = {}
        for key, log in self.log_dic.items():
            # key = '20210302-092955-809-0000112-168.62.9.55'
            # log = log_dic[key]
            key_code = self.algo_code_dict[key]
            if key_code != '601688.SH':
                inf_dic_utt = {}
                daily_zt_utt_dic = {'subject': 'Unknown'}

                for line in log:
                    order_count = 0

                    if 'updated max buy amt' in line:
                        if key not in target_amt_dic.keys():
                            target_amt_dic[key] = []
                        subject = getValueByKeyFromLine(line, by='subject')
                        place_amt = getValueByKeyFromLine(line, by='updated max buy amt')
                        tmp_dict = {
                            'subject': subject,
                            'target_amt': float(place_amt),
                            'code': key_code,
                        }
                        target_amt_dic[key].append(pd.Series(tmp_dict))

                    if ('riskSummary' in line) & ('拉抬打压' in line):
                        subject = getValueByKeyFromLine(line, by='subject')
                        inf_dic_utt['MRisk_info'] = '触发拉抬打压'
                        inf_dic_utt['subject'] = subject
                        inf_ser_utt = pd.Series(inf_dic_utt, name=key_code)
                        inf_list_utt.append(inf_ser_utt)

                    if ('Order info' in line) & ('rejected' not in line):  #  触发并准备下单
                        order_count += 1
                        trade_type = getValueByKeyFromLine(line, by='placeType')
                        subject = getValueByKeyFromLine(line, by='subject')
                        quantity = getValueByKeyFromLine(line, by='quantity')

                        if len(quantity) == 0:
                            print(key_code, 'quantity=', quantity)
                            quantity = 0
                        quantity = float(quantity)
                        if (quantity > 0) & (trade_type == 'A'):
                            daily_zt_utt_dic['order_direction'] = trade_type
                            daily_zt_utt_dic['quantity'] = getValueByKeyFromLine(line, by='quantity')
                            daily_zt_utt_dic['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                            daily_zt_utt_dic['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                            daily_zt_utt_dic['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                            daily_zt_utt_dic['price'] = getValueByKeyFromLine(line, by='price')
                            # daily_zt_utt_dic['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                            daily_zt_utt_dic['totalOrderAmt'] = float(daily_zt_utt_dic['quantity'])*float(daily_zt_utt_dic['price'])
                            daily_zt_utt_dic['subject'] = subject
                            daily_zt_ser = pd.Series(daily_zt_utt_dic, name=key_code)
                            daily_zt_utt_list.append(daily_zt_ser)

                            inf_dic_utt['totalOrderAmt'] = daily_zt_utt_dic['totalOrderAmt']
                            inf_dic_utt['subject'] = subject
                            inf_dic_utt['ZT_Time'] = 93100000
                            inf_ser_utt = pd.Series(inf_dic_utt, name=key_code)
                            inf_list_utt.append(inf_ser_utt)

                    if 'Order updated' in line:  # 单子实际的进行情况
                        code = getValueByKeyFromLine(line, by='symbol')
                        if key not in order_info_dic.keys():
                            order_info_dic[key] = []
                        order = {'transactionTime': format_unix2dt(getValueByKeyFromLine(line, by='transactionTime')),
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
                                         'transactTime': format_unix2dt(getValueByKeyFromLine(line, by='transactTime')),
                                         'riskOperation': getValueByKeyFromLine(line, by='riskOperation'),
                                         'riskType': getValueByKeyFromLine(line, by='riskType'),
                                         'MriskFlag':getMriskFlag(line,by1 = 'riskOperation',by2='riskType'),
                                         'riskInfo': getMriskInfo(line, by1='riskSummary')}
                        unfilled_info_dic[key].append(pd.Series(unfilled_info))

                if key_code in order_info_dic.keys():
                    try:
                        order_info_dic[code] = pd.concat(order_info_dic[code], axis=1).T
                    except:
                        print(1)
                if key_code in unfilled_info_dic.keys():
                    unfilled_info_dic[code] = pd.concat(unfilled_info_dic[code], axis=1).T

                if key_code in target_amt_dic.keys():
                    target_amt_dic[code] = pd.concat(target_amt_dic[code], axis=1).T


        if len(inf_list_utt) == 0:
            print('没有utt样本！！！')
            inf_df_utt = pd.DataFrame()
        else:
            inf_df_utt = pd.concat(inf_list_utt, axis=1).T.sort_index()

        if len(daily_zt_utt_list) != 0:
            daily_zt_df_utt = pd.concat(daily_zt_utt_list, axis=1).T.sort_index()
        else:
            daily_zt_df_utt = pd.DataFrame()

        order_info_df = pd.DataFrame()
        for keys, info in order_info_dic.items():
            order_info_df = pd.concat([order_info_df, pd.DataFrame(info)])

        unfilled_info_df = pd.DataFrame()
        for keys, info in unfilled_info_dic.items():
            unfilled_info_df = pd.concat([unfilled_info_df, pd.DataFrame(info)])

        target_amt_df = pd.DataFrame()
        for keys, info in target_amt_dic.items():
            target_amt_df = pd.concat([target_amt_df, pd.DataFrame(info)])
        target_amt_df = target_amt_df.set_index(['code', 'subject'])

        inf_df_utt = inf_df_utt.reset_index()
        inf_df_utt['target_amt'] = inf_df_utt[['index', 'subject']].apply(lambda x: target_amt_df.loc[(x['index'], x['subject']), 'target_amt'] if (x['index'], x['subject']) in target_amt_df.index else 0, axis=1)
        target_amt_df = target_amt_df.reset_index().set_index('code')

        return inf_df_utt, order_info_df, unfilled_info_df, daily_zt_df_utt