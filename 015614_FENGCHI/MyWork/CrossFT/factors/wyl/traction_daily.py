from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.operators import ds_delay, ds_mean


class traction_daily(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_topval'
    extend_days = 21
    author = 'wyl'
    logic = '''龙头股动量、普通股反转,取累计成交金额占比达到 λ %，认定为龙头股'''
    article = '20200302-开源证券-市场微观结构研究系列（4）：A股行业动量的精细结构.pdf'
    freq = 'daily'
    basic_datas = {'daily': ['close','amt']}

    def st_factor(self):
        close = self.database['daily']['close']
        preclose = ds_delay(close, 1)
        pct = ds_mean(close / preclose - 1, 20)
        return pct

    def cal_customst(self):
        pct = self.st_factor()
        self.stgroup = sameshape(pct, self.group_factor())
        calfunc = self.group_func()
        mom_pct_ind =st2groupst(pct, self.stgroup, calfunc,y=self.database['daily']['amt'],thred=0.3, dfunc=np.nanmean)# 龙头股动量
        inv_pct_ind =st2groupst(pct, self.stgroup, calfunc,y=-self.database['daily']['amt'],thred=0.7, dfunc=np.nanmean)# 普通股反转
        tract_pow = mom_pct_ind-inv_pct_ind
        return arr_match_index(tract_pow, self.cal_date_range, self.date_range)

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
