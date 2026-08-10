# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 13:41:17 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class Spot_mom_10_IH(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']} 
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        
        hclose = data['close_000016.SH'].iloc[-11:].values
        
        factor = (hclose[-1] / hclose[1] - 1)

        
        return factor