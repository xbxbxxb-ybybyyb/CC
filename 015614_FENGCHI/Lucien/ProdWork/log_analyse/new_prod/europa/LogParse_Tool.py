import pandas as pd
import re
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
import warnings
warnings.filterwarnings('ignore')
from ProdWork.CommonTools import getValueByKeyFromLine, getValueByKeyFromLine2, isException, \
    trans_str2dic, getMriskFlag, getMriskInfo, format_unix2dt, getRiskViolateRemark, getRejectReason

class LogParse_Tool:
    def __init__(self, environment, date, log_line):
        self.environment = str(environment)
        self.date = str(date)
        self.log_lines = log_line
        self.all_lines = list(map(self.openpx_determine, log_line))
        self.lines = self.filter_triggered_line(log_line)
        self.algo_code_dict = self.get_algo_code_dict()
        self.eur_machine_code_dict, self.machine_counter_dict = self.get_machine_code_dict()
        self.log_dic = self.split_log_algo()

    @staticmethod
    def get_keys_with_value(selfdict, value):
        return [k for k, v in selfdict.items() if v == value]

    def getAlgoByalgoFromLine(self, line):
        return re.findall(r"-algo-(.*?)]", line)[0]

    def getAlgoCode(self, line):
        return re.findall(r"-algo-(.*?)]", line)[0]

    # TODO:change this
    @staticmethod
    def getMachineNoFromLine(line):
        pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
        res = pattern.findall(line)
        return res[0]

    def openpx_determine(self,x):
        if self.environment == 'prod':
            x = bytes.decode(x, errors='ignore')
            if 'OpenPX' not in x:
                return x
            else:
                return ''
        else:
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
        triggered_lines = list(filter(lambda x: 'Calculate factors' in str(x), log_line))
        algo_code_set = set()
        for triggered_line in triggered_lines:
            algo_code = self.getAlgoCode(str(triggered_line))
            symbol = getValueByKeyFromLine2(str(triggered_line), by='symbol')
            algo_code_set.add(algo_code + ' ' + symbol)
        print(f'共有{len(algo_code_set)}个实例触发')
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
                        print(code, algo_code)
                        pass
                    algo_code_dict[algo_code + ' ' + code] = code
            except IndexError:
                pass
        algo_code_dict = {key: val for key, val in algo_code_dict.items() if key not in selkey[:-1]}
        for tmocode in selcode:
            print(tmocode, self.get_keys_with_value(algo_code_dict, tmocode))
        return algo_code_dict

    def get_machine_code_dict(self):
        eur_machine_code_dict = {}
        machine_counter_dict = {}
        for line in self.lines: # by fengc：根据cpp机器多对多的特性进行修改
            if 'symbol=' not in line:
                continue
            try:
                if 'startCal' in line and 'JupiterNew' in line:
                    algo_code = self.getAlgoCode(line)
                    code = getValueByKeyFromLine(line, by='symbol')
                    stock_code = self.algo_code_dict[algo_code + ' ' + code]
                    if stock_code not in eur_machine_code_dict.keys():
                        machine_code = self.getMachineNoFromLine(line)
                        eur_machine_code_dict[stock_code] = machine_code
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
        return eur_machine_code_dict, machine_counter_dict

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
        algo_dic = {}
        tmp_lines = self.all_lines
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
        inf_list001 = []
        factor_list001 = []
        factor_list_all001 = []
        daily_zt_list001 = []
        trade_dic = {}
        now_trade_dic = {}
        new_trade_dic = {}
        order_info_dic = {}
        all_code_model_data001 = {}
        unfilled_info_dic = {}
        for key, log in self.log_dic.items():
            key_code = self.algo_code_dict[key]
            if key_code != '601688.SH':
                inf_dic001 = {}
                factor_dic_all001 = {}
                daily_zt_dic001 = {}
                for line in log:
                    order_count = 0
                    if 'Calculate factors' in line:
                        inf_dic001['factor_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))

                    if 'Triggered' in line:
                        print('europa triggered',key_code)
                        inf_dic001['ZT_Time'] = int(float(getValueByKeyFromLine(line, by='reachedZTTime')))
                        inf_dic001['system_time'] = getValueByKeyFromLine(line, by='now')

                    if 'Total unscaled factors' in line:
                        factor_dic_all001 = trans_str2dic(line[line.index('{'): line.index(', }')] + '}')

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

                    if ('Model prediction' in line) & ('parentPath' not in line):
                        inf_dic001['shouldBuySignal'] = getValueByKeyFromLine(line, by='shouldBuySignal')
                        inf_dic001['model_time_cost'] = float(getValueByKeyFromLine(line, by='timeCost'))

                    if ('riskSummary' in line) & ('拉抬打压' in line):
                        inf_dic001['MRisk_info'] = '触发拉抬打压'

                    if 'isMock' in line:
                        inf_dic001['isMock'] = getValueByKeyFromLine(line, by='isMock')

                    if ('isSkip' in line) & ('Saturn' not in line) & ('Ceres' not in line) & ('JupiterNew' in line):
                        inf_dic001['isSkip'] = getValueByKeyFromLine(line, by='isSkip')

                    if ('predict signals' in line) & ('parentPath' not in line):
                        inf_dic001['sum_signals'] = getValueByKeyFromLine(line, by='predict signals')

                    if ('parentPath' in line) & ('Single model' not in line):
                        model_name = getValueByKeyFromLine(line, by='parentPath')
                        if model_name not in all_code_model_data001.keys():
                            all_code_model_data001[model_name] = {}
                        code = getValueByKeyFromLine(line, by='symbol')
                        inf_dic001[model_name + '_probability'] = getValueByKeyFromLine(line, by='probability')

                    if ('Order info' in line) & ('rejected' not in line) & ('placeType=odd_sell' not in line):  #  触发并准备下单,odd_sell小单测试过滤掉
                        order_count += 1
                        trade_type = getValueByKeyFromLine(line, by='placeType')
                        order_type = getValueByKeyFromLine(line, by='orderType')

                        action_type = getValueByKeyFromLine(line, by='actionSource')

                        if (action_type == 'JupiterNew') & ((trade_type == 'SplitLastShot') | (trade_type == 'JupiterFirstOrder') | (trade_type == 'MRiskSplitLastShotBuy')| (order_type == 'MRiskSplitShot')): # 捕捉Europa的下单
                            daily_zt_dic001['order_direction'] = trade_type
                            daily_zt_dic001['quantity'] = getValueByKeyFromLine(line, by='quantity')
                            daily_zt_dic001['targetAmt'] = getValueByKeyFromLine(line, by='targetAmt')
                            daily_zt_dic001['nowPrice'] = getValueByKeyFromLine(line, by='nowPrice')
                            daily_zt_dic001['highLimitPrice'] = getValueByKeyFromLine(line, by='highLimitPrice')
                            daily_zt_dic001['price'] = getValueByKeyFromLine(line, by='price')
                            daily_zt_dic001['splitOrderNum'] = getValueByKeyFromLine(line, by='splitOrderNum')
                            daily_zt_dic001['totalOrderAmt'] = float(daily_zt_dic001['quantity'])*float(daily_zt_dic001['price'])*float(daily_zt_dic001['splitOrderNum'])
                            inf_dic001['totalOrderAmt'] = daily_zt_dic001['totalOrderAmt']
                            daily_zt_ser001 = pd.Series(daily_zt_dic001, name=key_code)
                            daily_zt_list001.append(daily_zt_ser001)

                    if 'Order updated' in line:
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

                    if 'Order was rejected' in line:
                        code = getValueByKeyFromLine(line, by='symbol')
                        if key not in unfilled_info_dic.keys():
                            unfilled_info_dic[key] = []
                        unfilled_info = {'riskSummary': getRejectReason(line, by1='riskOperation', by2='riskSummary'),
                                         'riskViolateRemark': getRiskViolateRemark(line, by1='riskViolateRemark'),
                                         'orderSide': getValueByKeyFromLine(line, by='orderSide'),
                                         'stockcode': code,
                                         'transactTime': format_unix2dt(getValueByKeyFromLine(line, by='transactTime')),
                                         'riskOperation': getValueByKeyFromLine(line, by='riskOperation'),
                                         'riskType': getValueByKeyFromLine(line, by='riskType'),
                                         'MriskFlag':getMriskFlag(line,by1 = 'riskOperation', by2='riskType'),
                                         'riskInfo': getMriskInfo(line, by1='riskSummary'),
                                         'reason': getValueByKeyFromLine(line, by='reason')}
                        unfilled_info_dic[key].append(pd.Series(unfilled_info))

                if key_code in trade_dic.keys():
                    trade_dic[code] = pd.concat(trade_dic[code], axis=1).T
                if key_code in new_trade_dic.keys():
                    new_trade_dic[code] = pd.concat(new_trade_dic[code], axis=1).T
                if key_code in now_trade_dic.keys():
                    print(key_code, code, key_code == code)
                    if key_code == code:
                        now_trade_dic[code] = pd.concat(now_trade_dic[code], axis=1).T
                if key_code in order_info_dic.keys():
                    try:
                        order_info_dic[code] = pd.concat(order_info_dic[code], axis=1).T
                    except:
                        print(1)
                if key_code in unfilled_info_dic.keys():
                    unfilled_info_dic[code] = pd.concat(unfilled_info_dic[code], axis=1).T

                if len(inf_dic001) != 0:
                    inf_ser001 = pd.Series(inf_dic001, name=key_code)
                    inf_list001.append(inf_ser001)

                factor_dic001 = factor_dic_all001


                if len(factor_dic001) != 0:
                    factor_ser001 = pd.Series(factor_dic001, name=key_code)
                    factor_list001.append(factor_ser001)
                if len(factor_dic_all001) != 0:
                    factor_ser_all001 = pd.Series(factor_dic_all001, name=key_code)
                    factor_list_all001.append(factor_ser_all001)

        if len(inf_list001) == 0:
            print('没有jupiter001样本！！！')
            inf_df001 = pd.DataFrame()
        else:
            inf_df001 = pd.concat(inf_list001, axis=1).T.sort_index()
            if 'ZT_Time' in inf_df001.columns:
                inf_df001 = inf_df001.loc[inf_df001['ZT_Time'].notnull()]
                inf_df001 = inf_df001.query('ZT_Time > 0')
            else:
                inf_df001 = pd.DataFrame()

        if len(factor_list001)==0:
            factor_df001=pd.DataFrame()
        else:
            factor_df001 = pd.concat(factor_list001, axis=1).T.sort_index()

        if len(daily_zt_list001) != 0:
            daily_zt_df001 = pd.concat(daily_zt_list001, axis=1).T.sort_index()
        else:
            daily_zt_df001 = pd.DataFrame()

        order_info_df = pd.DataFrame()
        for keys, info in order_info_dic.items():
            order_info_df = pd.concat([order_info_df, pd.DataFrame(info)])
        unfilled_info_df = pd.DataFrame()
        for keys, info in unfilled_info_dic.items():
            unfilled_info_df = pd.concat([unfilled_info_df, pd.DataFrame(info)])
        return trade_dic, now_trade_dic, order_info_df, unfilled_info_df, new_trade_dic, \
               inf_df001, factor_df001, all_code_model_data001, daily_zt_df001