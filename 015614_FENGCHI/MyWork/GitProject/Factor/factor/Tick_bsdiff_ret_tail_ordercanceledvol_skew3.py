from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from copy import deepcopy
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class Tick_bsdiff_ret_tail_ordercanceledvol_skew3(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.buyordercanceledvol_minute","FactorData.Basic_factor.sellordercanceledvol_minute","FactorData.Basic_factor.close_minute","FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    reform_window=5
    mini_factor='ret_tail'
    theobject='ordercanceledvol'
    sub_window=5
    stat='skew'
    n=3

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])

        obj_buy_term,obj_sell_term = self.get_theobject_term()
        obj_buy = database.depend_data[obj_buy_term]
        obj_sell =  database.depend_data[obj_sell_term]
        amt_df = database.depend_data['FactorData.Basic_factor.amt_minute']
        obj_buy = obj_buy.iloc[-237:,:]
        obj_sell = obj_sell.iloc[-237:,:]
        bsobj_diff = (obj_buy-obj_sell)/(obj_buy+obj_sell)
        dt_series = pd.Series([i//self.sub_window for i in range(bsobj_diff.shape[0])],index = bsobj_diff.index)
        bsobj_diff_5 = bsobj_diff.groupby(dt_series).mean()
        base = pd.Series(list(range(bsobj_diff_5.shape[0])),index = bsobj_diff_5.index)
        base_tile = pd.DataFrame(np.tile(base,(bsobj_diff_5.shape[1],1)).T,index = bsobj_diff_5.index,columns = bsobj_diff_5.columns)
        # 接下来进行数据的挑选
        if self.mini_factor=='raw':
            if self.stat=='avg':
                ans = bsobj_diff_5.mean()
            elif self.stat=='std':
                ans = bsobj_diff_5.std()
            elif self.stat=='skew':
                ans = bsobj_diff_5.skew()
            elif self.stat=='corr':
                ans = bsobj_diff_5.corrwith(base)
            elif self.stat=='cov':
                ans = bsobj_diff_5.corrwith(base)*bsobj_diff_5.std()
            else:
                raise Exception('Wrong_stat')
            return ans

        if self.mini_factor[-3:] == 'top':
            mini_factor_name = self.mini_factor[:-4]
        elif self.mini_factor[-4:] == 'tail':
            mini_factor_name = self.mini_factor[:-5]

        #1. 自身的边缘
        if mini_factor_name == 'self' :
            minifactor = deepcopy(bsobj_diff_5)

        if mini_factor_name == 'ret':
            close = database.depend_data['FactorData.Basic_factor.close_minute']
            close_5 = close.groupby(dt_series).last()
            minifactor = pd.DataFrame(close_5.values/close_5.shift(1).values-1,index = close_5.index,columns = close_5.columns).fillna(0)

        if mini_factor_name == 'amt_std':
            minifactor = amt_df.groupby(dt_series).std()

        if mini_factor_name == 'ret_std':
            close = database.depend_data['FactorData.Basic_factor.close_minute']
            ret = pd.DataFrame(close.values/close.shift(1).values -1, index = close.index, columns = close.columns)
            minifactor = ret.groupby(dt_series).std()

        if mini_factor_name == 'illq':
            close = database.depend_data['FactorData.Basic_factor.close_minute']
            close_5 = close.groupby(dt_series).last()
            ret_5 = pd.DataFrame(close_5.values/close_5.shift(1).values-1,index = close_5.index,columns = close_5.columns).fillna(0)
            volume = database.depend_data['FactorData.Basic_factor.volume_minute']
            volume_5 = volume.groupby(dt_series).sum()
            minifactor = ret_5/volume_5

        if mini_factor_name == 'hl':
            high = database.depend_data['FactorData.Basic_factor.high_minute']
            low = database.depend_data['FactorData.Basic_factor.low_minute']
            high_5 = high.groupby(dt_series).max()
            low_5 = low.groupby(dt_series).min()
            minifactor = high_5/low_5-1

        if mini_factor_name == 'ret_skew':
            close = database.depend_data['FactorData.Basic_factor.close_minute']
            ret = pd.DataFrame(close.values/close.shift(1).values -1, index = close.index, columns = close.columns)
            minifactor = ret.groupby(dt_series).skew()


        if self.mini_factor.split('_')[-1] == 'top':
            minifactor_rank = minifactor.rank(pct=True,ascending=False)
            if minifactor_rank.shape[0]//5>=5:
                bsobj_diff_5_new = bsobj_diff_5[pd.DataFrame(minifactor_rank.values<0.25 ,index = minifactor_rank.index,columns = minifactor_rank.columns)]
            else:
                bsobj_diff_5_new = bsobj_diff_5[pd.DataFrame(minifactor_rank.values<0.5 ,index = minifactor_rank.index,columns = minifactor_rank.columns)]
        else:
            minifactor_rank = minifactor.rank(pct=True, ascending=True)
            if minifactor_rank.shape[0]//5>=5:
                bsobj_diff_5_new = bsobj_diff_5[pd.DataFrame(minifactor_rank.values<0.25 ,index = minifactor_rank.index,columns = minifactor_rank.columns)]
            else:
                bsobj_diff_5_new = bsobj_diff_5[pd.DataFrame(minifactor_rank.values<0.5 ,index = minifactor_rank.index,columns = minifactor_rank.columns)]

        if self.stat == 'avg':
            ans_new = bsobj_diff_5_new.mean()
        elif self.stat == 'std':
            ans_new = bsobj_diff_5_new.std()
        elif self.stat == 'skew':
            ans_new = bsobj_diff_5_new.skew()
        elif self.stat == 'corr':
            ans_new = self.get_corresponding_corr(bsobj_diff_5_new,base_tile)
        elif self.stat == 'cov':
            ans_new = self.get_corresponding_corr(bsobj_diff_5_new,base_tile) * bsobj_diff_5_new.std()
        else:
            raise Exception('Wrong_stat')
        return ans_new

    def reform(self, temp_result):
        factor_values = -temp_result
        factor_values = factor_values.rolling(self.n).mean()
        return factor_values

    def get_theobject_term(self):
        if '_' in self.theobject:
            theobject_part1 = self.theobject.split('_')[0]
            theobject_part2 = self.theobject.split('_')[1]
            theobject_buy = [i for i in self.depend_data if theobject_part1 in i and theobject_part2 in i and 'buy' in i][0]
            theobject_sell = [i for i in self.depend_data if theobject_part1 in i and theobject_part2 in i and 'sell' in i][0]
        else:
            theobject_buy = [i for i in self.depend_data if self.theobject in i and 'buy' in i][0]
            theobject_sell = [i for i in self.depend_data if self.theobject in i and 'sell' in i][0]
        return theobject_buy,theobject_sell


    @staticmethod
    def get_corresponding_corr(x_df, y_df):
        x_df.dropna(how='all', inplace=True)
        y_df.dropna(how='all', inplace=True)
        common_idx = sorted(list(set(x_df.index).intersection(set(y_df.index))))
        x_df = x_df.reindex(common_idx)
        y_df = y_df.reindex(common_idx)
        subdf1_array = x_df.values
        subdf2_array = y_df.values
        subcorr = np.nanmean(((subdf1_array - np.nanmean(subdf1_array,axis=0)) * (subdf2_array - np.nanmean(subdf2_array))),axis=0)/ (np.nanstd(subdf1_array,axis=0) * np.nanstd(subdf2_array,axis=0))
        subcorr = pd.Series(subcorr, index=x_df.columns)
        return subcorr