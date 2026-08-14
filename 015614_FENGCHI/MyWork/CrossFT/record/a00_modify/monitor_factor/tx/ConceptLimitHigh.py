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

class ConceptLimitHigh(crossFactor):
    cross_group='sw1'
    cross_func='cross_max'
    extend_days=5
    author='tx'
    logic='板块日内连板高度'
    freq='1min'

    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        stock_close = get_minute_1factor('close', start_datetime=self.cal_start, end_datetime=self.end,
                                         code_list=self.code_list)
        limit_max = get_daily_1factor('limit_max', self.cal_date_range, code_list=self.code_list)
        limit_max_min = pd.DataFrame(np.array(limit_max.loc[stock_close.index.get_level_values('date')]),
                                     index=stock_close.index, columns=stock_close.columns)
        limit_min_num = (stock_close == limit_max_min)
        # 日频数据
        daily_close = get_daily_1factor('close', self.cal_date_range, code_list=self.code_list)
        IfLimit = (daily_close == limit_max)
        IfLimit.fillna(False, inplace=True)

        limit_high = calc_limit_high(IfLimit.fillna(0), 0)

        limit_high = pd.DataFrame(np.array(limit_high.loc[stock_close.index.get_level_values('date')]),
                                   index=stock_close.index, columns=stock_close.columns)

        double_num = (limit_high * limit_min_num+limit_min_num)
        double_num = df_match_index_col(double_num, self.code_list, self.cal_date_range, '1min')  # np.array

        return double_num

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor =  self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())

        #def cal_mean(x,axis):
        #    return np.nanmax(x,axis)

        self.func = self.group_func()
        res = st2groupst(self.factor, self.group, self.func)
        return arr_match_index(res,self.cal_date_range,self.date_range)

    def result(self):
        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return self.cal_groupst()

if __name__=='__main__':
    f = ConceptLimitHigh()
    f.save_result()