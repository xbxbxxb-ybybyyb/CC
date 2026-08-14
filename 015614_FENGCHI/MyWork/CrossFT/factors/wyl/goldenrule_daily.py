from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import ds_delay, ds_mean


class goldenrule_daily(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_mean'
    extend_days = 21
    author = 'wyl'
    logic = '''日内收益率（今收/今开-1）、隔夜收益率（今开/昨收-1）,日内动量、隔夜反转'''
    article = '20200302-开源证券-市场微观结构研究系列（4）：A股行业动量的精细结构.pdf'
    freq = 'daily'
    basic_datas = {'daily': ['close', 'open']}

    def st_factor(self):
        close, open = self.database['daily']['close'], self.database['daily']['open']
        preclose = ds_delay(close, 1)
        interday_pct = ds_mean(close / open - 1, 20)
        overnight_pct = ds_mean(open / preclose - 1, 20)
        return interday_pct, overnight_pct

    def cal_customst(self):
        interday_pct, overnight_pct = self.st_factor()
        self.stgroup = sameshape(interday_pct, self.group_factor())
        calfunc = self.group_func()
        interday_pct_ind =st2groupst(interday_pct, self.stgroup, calfunc)
        overnight_pct_ind = group2st(self.stgroup, st2group(overnight_pct, self.stgroup, calfunc))
        interday_ranks = np.argsort(np.argsort(interday_pct_ind,axis=-1),axis=-1)
        overnight_ranks = np.argsort(np.argsort(-overnight_pct_ind,axis=-1),axis=-1)
        total_ranks = interday_ranks + overnight_ranks
        return arr_match_index(total_ranks, self.cal_date_range, self.date_range)


    def result(self):
        return self.cal_customst()


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
