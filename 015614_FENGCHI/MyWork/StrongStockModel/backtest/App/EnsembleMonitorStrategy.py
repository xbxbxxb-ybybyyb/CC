from BaseStrategy.BaseStrategy import BaseStrategy
from BaseStrategy.LazyImport import lazy_import
from online_conf import local_config_path
from StrategyState import StrategyState

import os, datetime
import traceback
import pandas as pd
import numpy as np


# manifest.json配置说明
# "strategyName" 需与实际运行的策略主类保持一致
# "alias" 前台展示的策略名称
# "entryFile" 策略主类所在文件
# "paramString" 前台参数，如有修改需要请联系系统团队
class EnsembleMonitor(BaseStrategy):
    # public attributes
    # self.date # 运行日期
    # self.market_data_path # 行情数据地址
    # public methods
    # self.subscribe_factors(time_factor_dic) # 订阅因子接口
    # self.both_ends_log_info(msg) #打印info日志接口
    # self.both_ends_log_error(msg) #打印error日志接口
    # override methods
    # must: on_factor_calculated() #必须实现：因子计算完成后执行的自定义函数
    # optional: on_strategy_started() #可选实现：策略启动后执行的自定义函数

    # 请勿修改__init__内容
    def __init__(self):
        super().__init__()
        # 该策略名称，请与类名保持一致
        self.strategy_name = 'EnsembleMonitor'
        # 与对应Java策略名一致
        self.subscribe_strategy_name = 'AlphaRobotStrategy'
        # 与对应Java策略的publish_key一致
        self.subscribe_key = 'key-EM'
        # 与对应Java策略的subscribe_key一致
        self.publish_key = 'key-EM'

    def on_strategy_started(self):
        fix_factors = pd.read_pickle(local_config_path + 'using_fix_list.pkl')
        # pd.read_pickle(factor_info_path)['fix_factors']
        # WARNING: FORBID DELETING THIS LINE
        super().on_strategy_started()

        # 订阅具体时点所需的因子，可不调用，不调用即订阅全部
        # 需以字典形式提供七个时间点的因子类名
        # 未提供的时间点默认为订阅所有因子
        self.subscribe_factors(
            {
                "1000": fix_factors,
                "1030": fix_factors,
                "1100": fix_factors,
                "1300": fix_factors,
                "1330": fix_factors,
                "1400": fix_factors,
                "1430": fix_factors
            }
        )
        self.logger.info(f'订阅因子成功: fix_factors={fix_factors}')

        self.calculator = lazy_import("Modules").init_Calculator(int(self.date),
                                                                 send_strategy_log=self.both_ends_log_info)
        self.logger.info(f'创建预测模块成功')

        self.both_ends_log_info(f'{self.strategy_name} v1.0.0 策略启动成功, 日期={self.date}, 参数={self.strategy_params}')

    # @input params #
    # point: 触发时间点
    # factor_file_document_path: 本轮因子文件所在目录
    # factor_file_name_list: 本轮因子文件名列表
    def on_factor_calculated(self, time_point: str, factor_file_path: str) -> bool:
        try:
            t1 = datetime.datetime.now()
            self.both_ends_log_info(f'权值计算开始：{t1}')
            if self.calculator.predict(int(time_point), factor_file_path):
                self.both_ends_log_info("权值计算完成，耗时={}".format(datetime.datetime.now() - t1))
                ## for test only
                if time_point == '1000':
                    involved_stk = sorted(list(set(self.calculator.stk_list).union(set(self.calculator.holding.keys()))))
                    holding_info = pd.DataFrame(index=involved_stk)
                    holding_info['PortfolioNO'] = '1'
                    holding_info['NetPosition'] = pd.Series(self.calculator.holding)
                    holding_info['SellAvailable'] = pd.Series(self.calculator.available)
                    holding_info['TotalBuyAmount'] = 0
                    holding_info['TotalSellAmount'] = 0
                    holding_info = holding_info.reset_index().rename(columns={'index': 'Symbol'}).fillna(0)
                else:
                    holding_info = pd.read_pickle(f'{local_config_path}fake_barly_info/{self.calculator.date}/{self.calculator.pre_time}.pkl')
                    last_buy, last_sell = self.calculator.buy_order_record[self.calculator.pre_time], self.calculator.sell_order_record[self.calculator.pre_time]
                    traded_stk = sorted(list(set(last_buy.index).union(set(last_sell.index))))
                    vol = self.calculator.get_realtime_dataflow('volume')[traded_stk].loc[
                          str(self.calculator.date) + str(self.calculator.pre_time):str(self.calculator.date) + str(self.calculator.time)]
                    close = self.calculator.get_realtime_dataflow('close')[traded_stk].loc[
                            str(self.calculator.date) + str(self.calculator.pre_time):str(self.calculator.date) + str(self.calculator.time)]
                    vwap = (vol.fillna(0) * close.fillna(method='pad')).sum() / vol.sum()
                    vol_up = (vol.sum() * 0.1) // 100 * 100
                    last_buy = pd.DataFrame({'target': last_buy, 'up': vol_up.reindex(last_buy.index).fillna(0)}).min(axis=1)
                    last_sell = pd.DataFrame({'target': last_sell, 'up': vol_up.reindex(last_sell.index).fillna(0)}).min(axis=1)
                    last_buy = last_buy[~np.isclose(last_buy, 0)]
                    last_sell = last_sell[~np.isclose(last_sell, 0)]
                    holding_info = holding_info.set_index('Symbol')
                    holding_info.loc[last_buy.index, 'NetPosition'] = holding_info.loc[last_buy.index, 'NetPosition'] + last_buy
                    holding_info.loc[last_sell.index, 'NetPosition'] = holding_info.loc[last_sell.index, 'NetPosition'] - last_sell
                    holding_info.loc[last_sell.index, 'SellAvailable'] = holding_info.loc[last_sell.index, 'SellAvailable'] - last_sell
                    holding_info.loc[last_buy.index, 'TotalBuyAmount'] = holding_info.loc[last_buy.index, 'TotalBuyAmount'] + last_buy * vwap.loc[last_buy.index] * (1 + 0.001)
                    holding_info.loc[last_sell.index, 'TotalSellAmount'] = holding_info.loc[last_sell.index, 'TotalSellAmount'] + last_sell * vwap.loc[last_sell.index] * (
                            1 - 0.001)
                    holding_info = holding_info.reset_index()
                self.on_portfolio_collected(holding_info)
                if not os.path.exists(f'{local_config_path}fake_barly_info/{self.date}/'):
                    os.mkdir(f'{local_config_path}fake_barly_info/{self.date}/')
                pd.to_pickle(holding_info, f'{local_config_path}fake_barly_info/{self.date}/{self.calculator.time}.pkl')
                return True
        except Exception as e:
            self.both_ends_log_error(f'权值计算失败, 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()
        return False

    def on_portfolio_collected(self, portfolio_dataframe: pd.DataFrame) -> str:
        try:
            flag = self.calculator.holding_info_update(portfolio_dataframe)
            res_list = self.calculator.bar_handler()
            # 生成指令
            command = self.gen_new_target_command(res_list, flag)
            self.logger.info(f'command: {command}')
            return command
        except Exception as e:
            self.both_ends_log_error(f'调整指令生成失败, 原因={traceback.format_exc()}')
            self.trade_service.pause_strategy()

    def gen_new_target_command(self, content, flag):
        mes = '{"command": "TARGET", "content": ' + str(content).replace("\'", '"')
        mes += ', "totalBuyAmount": 0'
        mes += ', "totalSellAmount": 0'
        mes += ', "shouldPause": ' + str(int(flag))
        mes += '}'
        return mes
