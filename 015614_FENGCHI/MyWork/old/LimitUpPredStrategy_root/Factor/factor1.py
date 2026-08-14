# coding: utf-8
# Author：fengchi863
# Date ：2021/3/5 15:37

from backtest.factor_backtest.TickDataPrepare import TickDataPrepare
from backtest.factor_backtest.StrategyFactorTest2 import StrategyFactorTest2
import time
from LimitUpPredStrategy.conf.path_conf import factor_path

if __name__ == '__main__':
    dp = TickDataPrepare()
    t1 = time.time()
    LastPx = dp.get_data_by_date_list(item='LastPx',  # Tick字段名, 支持的字段见tick_items列表，
                                      # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                      start_date=20140101,
                                      end_date=20201231,
                                      date_list=None,  # 若传列表则忽略start_date和end_date参数
                                      start_tick=91500,  # 默认为91500
                                      end_tick=150000,  # 默认为150000
                                      tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                      return_idx=True  # True返回DataFrame, False返回2darray
                                      )
    buy1price = dp.get_data_by_date_list(item='Buy1Price',  # Tick字段名, 支持的字段见tick_items列表，
                                      # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                      start_date=20140101,
                                      end_date=20201231,
                                      date_list=None,  # 若传列表则忽略start_date和end_date参数
                                      start_tick=91500,  # 默认为91500
                                      end_tick=150000,  # 默认为150000
                                      tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                      return_idx=True  # True返回DataFrame, False返回2darray
                                      )
    buy2price = dp.get_data_by_date_list(item='Buy2Price',  # Tick字段名, 支持的字段见tick_items列表，
                                         # ReceiveDelay为行情延时毫秒数，其余详见行情中心说明文档
                                         start_date=20140101,
                                         end_date=20201231,
                                         date_list=None,  # 若传列表则忽略start_date和end_date参数
                                         start_tick=91500,  # 默认为91500
                                         end_tick=150000,  # 默认为150000
                                         tick_list=None,  # 若传列表则忽略start_tick和end_tick参数
                                         return_idx=True  # True返回DataFrame, False返回2darray
                                         )



    print(time.time() - t1)
    LastPx.to_pickle(factor_path + 'factor1.pkl')

    self = StrategyFactorTest2(start_date=20140101, end_date=20191231)

    self.set_stock_pool(start_tick=94000, stock_pool_address=None)

    self.set_test_params(strength_limit=1., close_limit_up=True)  # 封板定义为第一次涨停后, 收盘前nTick有mTick涨停, 比值m/n, 且收盘涨停

    # 以上条件不变时，因子回测可多次连续进行
    self.test_factor(factor='factor1',  # 因子名称, 可以传入str文件名, 也可直接传入DataFrame
                     address=factor_path,  # 因子路径, 若直接传DataFrame, 此处需为None
                     groups=10,  # 连续型因子分组收益的分组数, 若因子值为离散值则此传参无意义
                     output=factor_path + '回测结果.xlsx'  # 回测结果输出路径, None表示不输出
                     )
