from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from xquant.factordata import FactorData
from basic.operators import dt_std, dt_mean


class netactivebuystrength_5m(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 1
    author = 'wyl'
    logic = '''净主买强度 = mean（主动买入金额（成交量）-主动卖出金额（成交量））/std（主 动买入金额（成交量）-主动买入金额（成交量））'''
    article = '20200430-海通证券-行业轮动系列研究21：主动买入因子的行业有效性分析.pdf'
    freq = '5mins'
    basic_datas = {'1min': ['activebuyorderamt','activesellorderamt']}

    def st_factor(self):
        buy, sell = self.database['1min']['activebuyorderamt'], self.database['1min']['activesellorderamt']
        net = buy - sell
        strength = dt_mean(net,5)/dt_std(net,5)
        strength_daily = cross_resample(strength,'5mins')
        return strength_daily

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
