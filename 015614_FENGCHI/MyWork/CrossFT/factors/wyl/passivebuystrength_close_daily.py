from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from xquant.factordata import FactorData
from basic.operators import dt_std, dt_mean


class passivebuystrength_close_daily(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 1
    author = 'wyl'
    logic = '''选取收盘时段(14.27-14:56)，净主买强度 = mean（被动买入金额（成交量））/std（主 动买入金额（成交量））'''
    article = '20200430-海通证券-行业轮动系列研究21：被动买入因子的行业有效性分析.pdf'
    freq = 'daily'
    basic_datas = {'1min': ['passivebuyorderamt']}

    def st_factor(self):
        net = self.database['1min']['passivebuyorderamt']
        strength = dt_mean(net,242)/dt_std(net,242)
        strength_open = np.nanmean(strength[:, -34:-4],axis=1,keepdims=True)
        return strength_open

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
