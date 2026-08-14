from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from xquant.factordata import FactorData
from basic.operators import dt_pct,ds_std,ds_mean


class UID_daily(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'wyl'
    logic = '''衡量股票“信息分布均匀度”的因子，简称 为UID（the Uniformity of Information Distribution）因子,只能计算日频数据，因为需要一定量的数据计算标准差'''
    article = '20200901-东吴证券-“波动率选股因子”系列研究（二）：信息分布均匀度，基于高频波动率的选股因子'
    freq = 'daily'
    basic_datas = {'1min': ['close']}

    def st_factor(self):
        close = self.database['1min']['close']
        pct = dt_pct(close,1)
        pctvol_daily = np.nanstd(pct,axis=1,keepdims=True)
        utd = ds_std(pctvol_daily,20)/ds_mean(pctvol_daily,20)
        return utd

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
