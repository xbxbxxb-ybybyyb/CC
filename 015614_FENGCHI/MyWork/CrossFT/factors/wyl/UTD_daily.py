from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from xquant.factordata import FactorData
from basic.operators import ds_std, ds_mean


class UTD_daily(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 20
    author = 'wyl'
    logic = '''造换手率分布均匀度因子UTD（the Uniformity of Turnover Rate Distribution),只能计算日频数据，因为需要一定量的数据计算标准差'''
    article = '20210301-东吴证券-“技术分析拥抱选股因子”系列研究（四）：换手率分布均匀度，基于分钟成交量的选股因子.pdf'
    freq = 'daily'
    basic_datas = {'1min': ['turn_total']}

    def st_factor(self):
        turn = self.database['1min']['turn_total']
        turn_daily = np.nanstd(turn,axis=1,keepdims=True)
        utd = ds_std(turn_daily,20)/ds_mean(turn_daily,20)
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
