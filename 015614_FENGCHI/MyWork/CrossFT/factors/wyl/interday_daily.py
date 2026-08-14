from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import dt_delay,ds_mean


class interday_daily(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 21
    author = 'wyl'
    logic = '''日内收益率（今收/今开-1）'''
    article = '20200302-开源证券-市场微观结构研究系列（4）：A股行业动量的精细结构.pdf'
    freq = 'daily'
    basic_datas = {'daily': ['close','open']}

    def st_factor(self):
        close, open = self.database['daily']['close'], self.database['daily']['open']
        interday_pct = close/open-1
        return ds_mean(interday_pct,20)

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
    val0 = np.load('/arch1/group/800442/800319/AAcross/factor_result/daily/20140701_20210531/wyl/interday_daily.npy')
    val1 = cal_factor(cross_group = 'sw2',cross_func = 'cross_median')
    # val1= cal_factor('data/user/016385/test/crossft/examples', 'example.py',{'daily':6},notrun=False)
    # val2 = cal_factor('data/user/016385/test/crossft/examples', 'example.py',notrun=False)
    # print(np.nansum(val1-val2))
    print(np.nansum(val0-val1))
