from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

def _forward_fill(arr, axis , zero_fill = True):
    arr = arr.swapaxes(axis , -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis = -1, out = idx)
    out = arr[tuple(np.arange(idx.shape[x])[(None, )*x + (slice(None),) + (None,)*(idx.ndim-x-1)]
                   for x in range(idx.ndim-1))+(idx, )]
    out = out.swapaxes(axis, -1)
    return out

def calc_limit_high(limitup, error_limit):
    zt = np.array(limitup.astype(int)).T
    no_limit_idx = np.r_[0, (zt==0).sum(axis = 1)[:-1]].cumsum()
    if error_limit == 0:
        no_limit_idx = np.r_[tuple(no_limit_idx)]
        no_limit_arr = np.arange(zt.shape[1])[None, :].repeat(zt.shape[0], axis = 0)[zt == 0]
        no_limit_arr[no_limit_idx] = zt.shape[1]
    else:
        no_limit_idx = np.r_[tuple(no_limit_idx + x for x in range(error_limit))]
        no_limit_arr = np.arange(zt.shape[1])[None, :].repeat(zt.shape[0], axis = 0)[zt == 0]
        no_limit_arr = np.r_[[zt.shape[1]]*error_limit, no_limit_arr[: -error_limit]]
        no_limit_arr[no_limit_idx] = zt.shape[1]
    limit_idx = 1-zt
    limit_idx[limit_idx == 1] = no_limit_arr
    limit_idx = _forward_fill(limit_idx, axis = 1)
    limit_distance = np.arange(zt.shape[1])-limit_idx
    max_distance = np.fmax(limit_distance.max(axis = 0), error_limit)
    limit_high = pd.DataFrame(limit_distance.T, index =limitup.index, columns = limitup.columns)-error_limit
    limit_high[limit_high<0] = 0
    return limit_high

class ConceptDailyLimitHigh(crossFactor):
    cross_group='sw1'
    cross_func='cross_max'
    author='tx'
    extend_days = 60
    logic='板块日间连板高度'
    freq='daily'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        close = get_daily_1factor('close', self.cal_date_range,self.code_list)
        limit_down = get_daily_1factor('limit_max', self.cal_date_range,self.code_list)
        limitDown_num = (close==limit_down)
        limit_high = calc_limit_high(limitDown_num.fillna(0), 0)
        return limit_high


    def result(self):
        return self.cal_groupst()

if __name__=='__main__':
    val1 = cal_factor(numd={})
    val2 = cal_factor(numd={'daily': 10})
    print(np.nansum(abs(val1 - val2)))