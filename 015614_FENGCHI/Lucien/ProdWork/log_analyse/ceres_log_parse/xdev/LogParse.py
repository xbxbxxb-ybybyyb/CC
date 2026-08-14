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
            return re.findall(r"Thread (.*?)]", line)[0]
        except:
            return re.findall(r"algo-(.*?)]", line)[0]

    def getAlgoCode(self, line):
        try:
            return re.findall(r"Thread (.*?)]", line)[0]
        except:
            return re.findall(r"algo-(.*?)]", line)[0]

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
        return line[line.index('CeresStrategy-CPP for ') + 29 : line.index(' Version')]

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
        triggered_lines = list(filter(lambda x: 'ceres model prediction' in str(x), log_line))

        #　筛选type==1的标签
        this_type_stocks_lines = list(filter(lambda x: 'sample_type=1' in str(x), log_line))
        this_type_stocks_list = list(map(lambda x: self.getAlgoCode(x), this_type_stocks_lines))

        algo_code_set = set()
        for triggered_line in triggered_lines:
            algo_code = self.getAlgoCode(str(triggered_line))
            symbol = getValueByKeyFromLine2(str(triggered_line), by='symbol')
            if symbol in this_type_stocks_list:
                algo_code_set.add(algo_code + ' ' + symbol)
        print(f'共有{len(algo_code_set)}个实例触发')
        # 这里肯定有symbol了
        # log_line_ = list(filter(lambda x: self.getAlgoCode(str(x)) + ' ' + getValueByKeyFromLine2(str(x), by='symbol') in algo_code_set, log_line))
        log_line_ = log_line
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
        inf_list_ceres = []
        factor_list_ceres = []
        factor_list_ceres930 = []
        trade_dic = {}
        daily_zt_ceres_list = []
        now_trade_dic = {}
        new_trade_dic = {}
        order_info_dic = {}
        all_code_model_data_ceres = {}
        unfilled_info_dic = {}
        for key, log in self.log_dic.items():
            # key = '20210302-092955-809-0000112-168.62.9.55'
            # log = log_dic[key]
            key_code = self.algo_code_dict[key]
            if key_code != '601688.SH':
                inf_dic_ceres = {}
                inf_dic_ceres930 = {}
                daily_zt_ceres_dic = {}
                factor_dic_ceres = {}
                factor_dic_ceres930 = {}
                for line in log:
                    order_count = 0
                    # list(filter(lambda x: 'Order was rejected' in x, log))    # 测试用，看到底有没有这一行
                    if ('calculate factors' in line) & ('ceresKey=931' in line):
                        inf_dic_ceres['factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))
                    if ('calculate factors' in line) & ('ceresKey=930' in line):
                        inf_dic_ceres930['factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))

                    if 'model prediction' in line:
                        # inf_dic_ceres['ZT_Time'] = int(float(getValueByKeyFromLine(line, by='reachedZTTime')))
                        inf_dic_ceres['ZT_Time'] = 93100000

                    if ('total unscaled tday-factors' in line) & ('ceresKey=931' in line):
                        factor_dic_ceres = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')
                    if ('ceres factor' in line) & ('ceresKey=930' in line):
                        factor_dic_ceres930 = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')

                    if 'nowTrade' in line and 'by SellOrder' not in line:
                        code = getValueByKeyFromLine(line, by='symbol')
                        if key not in now_trade_dic.keys():
                            now_trade_dic[key] = []
                        trade = {'TradePrice': float(getValueByKeyFromLine(line, by='price')),
                                 'TradeQty': float(getValueByKeyFromLine(line, by='quantity')),
                                 'TradeIndex': int(getValueByKeyFromLine(line, by='tradeIndex')),
                                 'TradeBuyNo': int(getValueByKeyFromLine(line, by='tradeBuyNo')),
                                 'TradeSellNo': int(getValueByKeyFromLine(line, by='tradeSellNo')),
                                 'TradeBSFlag': (getValueByKeyFromLine(line, by='side')=='Offer') + 1,
                                 'TradeType': int(getValueByKeyFromLine(line, by='type')=='Canceled'),
                                 'MDTime': getValueByKeyFromLine(line, by='nowTradeTimestamp')}
                        now_trade_dic[key].append(pd.Series(trade))
                    elif 'New trade' in line:
                        code = getValueByKeyFromLine(line, by='symbol')
                        if key not in new_trade_dic.keys():
                            new_trade_dic[key] = []
                        trade = {'TradePrice': float(getValueByKeyFromLine(line, by='price')),
                                 'TradeQty': float(getValueByKeyFromLine(line, by='quantity')),
                                 'TradeMoney': float(getValueByKeyFromLine(line, by='turnover')),
                                 'TradeIndex': int(getValueByKeyFromLine(line, by='tradeIndex')),
                                 'TradeBuyNo': int(getValueByKeyFromLine(line, by='tradeBuyNo')),
                                 'TradeSellNo': int(getValueByKeyFromLine(line, by='tradeSellNo')),
                                 'TradeBSFlag': (getValueByKeyFromLine(line, by='side')=='Offer') + 1,
                                 'TradeType': int(getValueByKeyFromLine(line, by='type')=='Canceled'),
                                 'log_ReceiveDateTime': line[11:13] + line[14:16] + line[17:19] + line[20:23]}
                        new_trade_dic[key].append(pd.Series(trade))

                    if ('ceres model prediction' in line) & ('parentPath' not in line):
                        if 'shouldBuy=' in line:
                            inf_dic_ceres['shouldBuySignal'] = bool(int(getValueByKeyFromLine(line, by='shouldBuy')))
                        else:
                            inf_dic_ceres['shouldBuySignal'] = bool(getValueByKeyFromLine(line, by='shouldBuySignal'))   # 这一行其实没用
                        if 'cost=' in line:
                            inf_dic_ceres['model_time_cost'] = float(getValueByKeyFromLine(line, by='cost'))
                        else:
                            inf_dic_ceres['model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))

                    if ('riskSummary' in line) & ('拉抬打压' in line):
                        inf_dic_ceres['MRisk_info'] = '触发拉抬打压'

                    if ('predict sum_signals' in line) & ('parentPath' not in line):
                        inf_dic_ceres['sum_signals'] = getValueByKeyFromLine(line, by='predict sum_signals')

                    if ('parentPath' in line) & ('probability' in line):
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data_ceres.keys():
                            all_code_model_data_ceres[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic_ceres[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')

                    if ('Order info' in line) & ('rejected' not in line):  #  触发并准备下单
                        order_count += 1
                        trade_type = getValueByKeyFromLine(line, by='placeType')
                        order_type = getValueByKeyFromLine(line, by='orderType')

                        action_type = getValueByKeyFromLine(line, by='actionSource')
                        if len(action_type) == 0: action_type = 'Metis'
                        quantity = getValueByKeyFromLine(line, by='quantity')

                        if len(quantity)==0:
                            print(key_code, 'quantity=', quantity)
                            if 'firstJupiterOrderQty' in line and 'secondJupiterOrderQty' in line:
                                print('二次下单：%s'%key_code)
                                quantity = float(getValueByKeyFromLine(line, by='firstJupiterOrderQty')) + float(getValueByKeyFromLine(line, by='secondJupiterOrderQty'))
                            else:
                                print('用0填充quantity：%s' % key_code)
                                quantity = 0
                        quantity = float(quantity)
                        if (quantity > 0) & (action_type != 'JupiterNew') & ((trade_type == 'SplitLastShot') | (trade_type == 'JupiterFirstOrder')| (trade_type == 'MRiskSplitLastShotBuy')| (order_type == 'MRiskSplitShot')): # 捕捉jupiter的下单
                            daily_zt_ceres_dic['order_direction'] = trade_type
                            daily_zt_ceres_dic['quantity'] = getValueByKeyFromLine(line, by='quantity')
                            daily_zt_ceres_dic['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                            daily_zt_ceres_dic['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                            daily_zt_ceres_dic['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                            daily_zt_ceres_dic['price'] = getValueByKeyFromLine(line, by='price')
                            daily_zt_ceres_dic['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                            daily_zt_ceres_dic['totalOrderAmt'] = float(daily_zt_ceres_dic['quantity'])*float(daily_zt_ceres_dic['price'])*float(daily_zt_ceres_dic['splitOrderNum'])
                            inf_dic_ceres['totalOrderAmt'] = daily_zt_ceres_dic['totalOrderAmt']
                            daily_zt_ser = pd.Series(daily_zt_ceres_dic, name=key_code)
                            daily_zt_ceres_list.append(daily_zt_ser)

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

                    if ('market data stat info' in line) & ('Metis' in line):   # 计算因子使用到的行情条数，原来是对比因子不一致时使用
                        inf_dic_ceres['filledTradeList'] = getValueByKeyFromLine(line, by='filledTradeList', form='(.*?)[;\n]')
                        inf_dic_ceres['lxjjFillList'] = getValueByKeyFromLine(line, by='lxjjFillList', form='(.*?)[;\n]')
                        inf_dic_ceres['last5SecFillList'] = getValueByKeyFromLine(line, by='last5SecFillList', form='(.*?)[;\n]')
                        inf_dic_ceres['last30SecFillList'] = getValueByKeyFromLine(line, by='last30SecFillList', form='(.*?)[;\n]')
                        inf_dic_ceres['last2MinFillList'] = getValueByKeyFromLine(line, by='last2MinFillList', form='(.*?)[;\n]')
                        inf_dic_ceres['last5MinFillList'] = getValueByKeyFromLine(line, by='last5MinFillList', form='(.*?)[;\n]')

                if key_code in trade_dic.keys():
                    trade_dic[code] = pd.concat(trade_dic[code], axis=1).T
                if key_code in new_trade_dic.keys():
                    new_trade_dic[code] = pd.concat(new_trade_dic[code], axis=1).T
                if key_code in now_trade_dic.keys():
                    print(key_code, code, key_code==code)
                    if key_code == code:
                        now_trade_dic[code] = pd.concat(now_trade_dic[code], axis=1).T
                if key_code in order_info_dic.keys():
                    try:
                        order_info_dic[code] = pd.concat(order_info_dic[code], axis=1).T
                    except:
                        print(1)
                if key_code in unfilled_info_dic.keys():
                    unfilled_info_dic[code] = pd.concat(unfilled_info_dic[code], axis=1).T

                if len(inf_dic_ceres) != 0:
                    inf_ser_ceres = pd.Series(inf_dic_ceres, name=key_code)
                    inf_list_ceres.append(inf_ser_ceres)

                if len(factor_dic_ceres) != 0:
                    factor_ser_ceres = pd.Series(factor_dic_ceres, name=key_code)
                    factor_list_ceres.append(factor_ser_ceres)
                if len(factor_dic_ceres930) != 0:
                    factor_ser_ceres930 = pd.Series(factor_dic_ceres930, name=key_code)
                    factor_list_ceres930.append(factor_ser_ceres930)

        if len(inf_list_ceres) == 0:
            print('没有ceres样本！！！')
            inf_df_ceres = pd.DataFrame()
        else:
            inf_df_ceres = pd.concat(inf_list_ceres, axis=1).T.sort_index()
            if 'MRisk_info' in inf_df_ceres.columns:
                inf_df_ceres_mrisk_info = inf_df_ceres[~inf_df_ceres['MRisk_info'].isna()]
                inf_df_ceres_mrisk_info = inf_df_ceres_mrisk_info.reset_index().drop_duplicates('index').set_index('index')
                inf_df_ceres.loc[inf_df_ceres_mrisk_info.index, 'MRisk_info'] = inf_df_ceres_mrisk_info.loc[inf_df_ceres_mrisk_info.index, 'MRisk_info']
            if 'ZT_Time' in inf_df_ceres.columns:
                inf_df_ceres = inf_df_ceres.loc[inf_df_ceres['ZT_Time'].notnull()]
                inf_df_ceres = inf_df_ceres.query('ZT_Time > 0')
            else:
                inf_df_ceres = pd.DataFrame()


        if len(factor_list_ceres)==0:
            factor_df_ceres = pd.DataFrame()
        else:
            factor_df_ceres = pd.concat(factor_list_ceres, axis=1).T.sort_index()
        if len(factor_list_ceres930)==0:
            factor_df_ceres930 = pd.DataFrame()
        else:
            factor_df_ceres930 = pd.concat(factor_list_ceres930, axis=1).T.sort_index()

        if len(daily_zt_ceres_list) != 0:
            daily_zt_df_ceres = pd.concat(daily_zt_ceres_list, axis=1).T.sort_index()
        else:
            daily_zt_df_ceres = pd.DataFrame()

        order_info_df = pd.DataFrame()
        for keys, info in order_info_dic.items():
            order_info_df = pd.concat([order_info_df, pd.DataFrame(info)])

        unfilled_info_df = pd.DataFrame()
        for keys, info in unfilled_info_dic.items():
            unfilled_info_df = pd.concat([unfilled_info_df, pd.DataFrame(info)])

        return inf_df_ceres, trade_dic, now_trade_dic, order_info_df, unfilled_info_df, new_trade_dic, factor_df_ceres, factor_df_ceres930, daily_zt_df_ceres, all_code_model_data_ceres