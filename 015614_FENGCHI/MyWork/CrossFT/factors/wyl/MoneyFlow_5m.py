from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from xquant.factordata import FactorData
from basic.operators import ts_delay, dt_mean


class MoneyFlow_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_sum'
    extend_days = 1
    author = 'wyl'
    logic = '''证券价格在约定的时间段中处于上升状 态时产生的成交额是推动指数上涨的力量，这部分成交额被定义为资金流入；' \
            证券 价格在约定的时间段中下跌时的成交额是推动指数下跌的力量，这部分成交额被定 义为资金流出；
            若证券价格在约定的时间段前后没有发生变化，则这段时间中的成 交额不计入资金流量。
            当天资金流入和流出的差额可以认为是该证券当天买卖两种 力量相抵之后，推动价格变化的净作用量，即被定义为当天资金净流量。'''
    article = '20090914_国信证券_交易性指标与策略系列之一_国信资金强弱指标（GSMS）的构建'
    freq = '5mins'
    basic_datas = {'1min': ['volume', 'close']}

    def st_factor(self):
        vol = self.database['1min']['volume']
        p = self.database['1min']['close']
        pgap = p - ts_delay(p, 1)
        moneyflow = vol * p * pgap / abs(pgap)
        moneyflow_5min = cross_resample(dt_mean(moneyflow,5),'5mins')
        return  moneyflow_5min

    def cal_groupst(self):
        self.factor = self.st_factor()
        self.stgroup = sameshape(self.factor, self.group_factor())
        calfunc = self.group_func()
        res = st2groupst(self.factor, self.stgroup, calfunc)
        return arr_match_index(res, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()


if __name__ == '__main__':
    # 当进行因子初步计算时，使用这个公式
    # for groups in cross_groups:
    #     f = example(start = 20200101,cross_group=groups)
    #     print(f.result())
    #     break

    # 因子存储时用这个公式，{freq: task_num}
    val1 = cal_factor()
    # val1= cal_factor('data/user/016385/test/crossft/examples', 'example.py',{'daily':6},notrun=False)
    # val2 = cal_factor('data/user/016385/test/crossft/examples', 'example.py',notrun=False)
    # print(np.nansum(val1-val2))
    print(val1)
