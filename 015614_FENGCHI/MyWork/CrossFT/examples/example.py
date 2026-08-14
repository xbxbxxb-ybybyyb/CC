
from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *
from xquant.factordata import FactorData
from basic.operators import *

class example(crossFactor):
    cross_group = 'sw1'
    cross_func = 'cross_max'
    extend_days =1
    author ='wyl'
    logic = '申万一级行业中换手均值'
    article = '20220101-无语证券-一级行业看换手'
    freq = '5mins'
    basic_datas = {'daily': ['volume', 'open','pre_close','buytradeamt','ret_vwap','close_HS300'],
                   '30mins': ['volume', 'open','pre_close','buytradeamt','ret_vwap','close_HS300'],
                   '5mins': ['volume', 'open','close','buytradeamt','ret_vwap','close_HS300'],
                   '1min': ['volume', 'open','close','buytradeamt','ret_vwap','close_HS300']}

    start = 20140701
    end = 20200205

    def st_factor(self):

        t =cross_resample(self.database['daily']['pre_close'],'30mins')
        t1 = np.repeat(self.database['30mins']['pre_close'],6,axis=1)
        t2 = cross_resample(self.database['30mins']['pre_close'],'1min')
        t3 = dt_forward(t,1)
        return self.database['5mins']['open']+cross_resample(t3,'5mins',shift=True)+cross_resample(t2,'5mins')

    def cal_groupst(self):
        self.factor = self.st_factor()
        self.stgroup = sameshape(self.factor, self.group_factor())
        calfunc = self.group_func()
        res = st2groupst(self.factor, self.stgroup, calfunc)
        return arr_match_index(res, self.cal_date_range, self.date_range)

    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    # 当进行因子初步计算时，使用这个公式
    # for groups in cross_groups:
    #     f = example(start = 20200101,cross_group=groups)
    #     print(f.result())
    #     break

    # 因子存储时用这个公式，{freq: task_num}
    n1,n2 =-1,-1
    t1 = cross_times['5mins'][n1]
    t2 = cross_times['5mins'][n2]
    #
    info1,val1 = cal_factor(start=20210101,end=20210204,cross_group='sw2', cross_func='cross_min',purerun=False,onlycheck=False,numd={'5mins':1})
    info2,val2 = cal_factor(start=20210101, end=20210204, cross_group='sw2', cross_func='cross_max', purerun=False,
                      onlycheck=False, numd={'5mins': 1})
    #val2 = cal_factor(cross_group='sw2', cross_func='cross_min',purerun=False,onlycheck=False,numd={'5mins':10})
    #val2 = cal_factor(start=20210101, end=20210105,mend=t2,cross_group='sw2', cross_func='cross_min', purerun=True)
    #val1= cal_factor('data/user/016385/test/cr ossft/examples', 'example.py',{'daily':6},notrun=False)
    #val2 = cal_factor('data/user/016385/test/crossft/examples', 'example.py',notrun=False)
    gap = abs(np.where(np.isfinite(val1),val1,0)-np.where(np.isfinite(val2),val2,0))
    print(np.nanmean(gap))
    print(val1)



