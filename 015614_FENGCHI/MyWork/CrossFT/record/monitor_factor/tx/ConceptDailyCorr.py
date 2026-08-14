from basic.crossFactor import crossFactor
from basic.crossUtils import *
from basic.crossConfig import *

def array_coef(x, y):
    x_values = np.array(x, dtype=float)
    y_values = np.array(y, dtype=float)
    x_values[np.isinf(x_values)] = np.nan
    y_values[np.isinf(y_values)] = np.nan
    nan_index = np.isnan(x_values) | np.isnan(y_values)
    x_values[nan_index] = np.nan
    y_values[nan_index] = np.nan
    delta_x = x_values - np.nanmean(x_values, axis=0)
    delta_y = y_values - np.nanmean(y_values, axis=0)
    multi = np.nanmean(delta_x * delta_y, axis=0) / (np.nanstd(delta_x, axis=0) * np.nanstd(delta_y, axis=0))
    multi[np.isinf(multi)] = np.nan
    return pd.Series(multi, index=x.columns)

def rolling_corr(df_x, df_y, window=None):
    """"""
    assert df_x.shape[0] == df_y.shape[0], 'dims must be same'

    corr = pd.DataFrame(np.nan, index=df_x.index, columns=df_x.columns)

    if window == None or window <= 0:
        window = df_x.shape[0]
    if window <= df_x.shape[0] and window > 1:
        for idx, index in enumerate(df_x.index):
            if idx >= window - 1:
                corr.loc[index] = array_coef(df_x.iloc[idx - window + 1:idx + 1],
                                             df_y.iloc[idx - window + 1:idx + 1]).values
    return corr

class ConceptDailyCorr(crossFactor):
    def st_factor(self):
        '''
        :return: 1. np.array ,返回个股计算组值需要的个股因子
                2.  list(np.array)， 返回多个个股因子，有些为了计算组值，有些为了计算
        '''
        stock_pct = get_daily_1factor('pct_chg',self.cal_date_range)
        stock_pct = df_match_index_col(stock_pct, self.code_list, self.cal_date_range)# np.array

        return stock_pct

    def cal_groupst(self):
        '''
        :return: np.array,index: datetime, columns: stockpool，个股值==》组值==》个股值 ，没有行业值在和个股值进行某些计算
        '''
        self.factor =  self.st_factor()
        self.group = sameshape(self.factor, self.group_factor())

        #def cal_mean(x,axis):
        #    return np.nanmean(x,axis)

        self.func = self.group_func()
        res = st2groupst(self.factor, self.group, self.func)
        return res

    def result(self):
        stock_pct = self.st_factor()[:,0,:]
        concept_pct = self.cal_groupst()[:,0,:]

        stock_pct = pd.DataFrame(stock_pct,index=self.cal_date_range,columns=self.code_list)
        concept_pct = pd.DataFrame(concept_pct, index=self.cal_date_range, columns=self.code_list)

        res = rolling_corr(stock_pct, concept_pct, window=10)
        res = df_match_index_col(res, self.code_list, self.cal_date_range)  # np.array

        '''
        :return: np.array,
                 如果只是个股计算组值进行平铺，则return cal_groupst()
                 如果是计算了分组然后又跟个股进行了计算，则 return cal_customst()
        '''
        return arr_match_index(res, self.cal_date_range, self.date_range)

if __name__=='__main__':
    f = ConceptDailyCorr(group='sw1', func='cross_mean',author='tx',extend_days=20,factor_name='ConceptDailyCorr',
                         logic='板块与个股涨幅相关性',freq='daily')
    f.save_result()
