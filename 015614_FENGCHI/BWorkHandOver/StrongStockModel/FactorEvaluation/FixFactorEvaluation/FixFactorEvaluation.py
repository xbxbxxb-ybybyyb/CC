# @Time : 2021/7/19 10:57
# @Author : Zhichen Lu
# @File : FixFactorEvaluation.py

import pandas as pd
import numpy as np
import bottleneck

bar_list = [1000,1030,1100,1300,1330,1400,1430]
class FactorEvaluator:

    def __init__(self,start,end,factor_address='/data/group/800002/alpha_factor/lib/x_factor_lib/',normalize_window=60):
        self.normalize_window = normalize_window
        self.factor_address = factor_address
        pass

    def load_factor(self,factor_name,return_df = True):

        normalize_window = 60

        factor_name = 'dretvolnew_ntkurtmean_60_10'
        factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
        factor = []
        for bar in bar_list:
            temp_factor = pd.read_pickle(f'{factor_address}Fix{bar}_{factor_name}.pkl')
            temp_factor.index = [(x,bar) for x in temp_factor.index]
            factor.append(temp_factor)
        factor = pd.concat(factor).sort_index()
        index,columns = factor.index,factor.columns
        factor = factor.values.reshape((factor.shape[0]//7,7,factor.shape[-1])).swapaxes(0,1)
        nan_tag = np.isnan(factor)
        factor[nan_tag] = 0
        factor_sum = bottleneck.move_sum(factor.sum(axis=0),window=normalize_window)
        factor2_sum = bottleneck.move_sum((factor**2).sum(axis=0),window=normalize_window)
        factor_count = bottleneck.move_sum(nan_tag.sum(axis=0),window=normalize_window)

        mean = factor_sum/factor_count
        square_mean = factor2_sum/factor_count
        std = (square_mean - mean**2)**0.5
        factor = (factor - mean)/std
        factor[nan_tag] = 0
        factor = factor.swapaxes(0,1).reshape((len(index),len(columns)))
        if return_df:
            return pd.DataFrame(factor,index=index,columns=columns)
        else:
            return factor,index,columns



    def calc_ic_d(self,factor):
        pass

    def calc_ic_t(self,factor):
        pass

    def calc_ic_c(self,factor):
        pass

    def evaluate(self,factor):
        pass




