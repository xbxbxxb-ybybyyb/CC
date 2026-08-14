# coding: utf-8
# Author：fengchi863
# Date ：2020/12/14 10:10

import os
import sys
sys.path.append('/data/group/800319')
sys.path.append('/data/user/fengchi/MyWork')
sys.path.append("/data/group/800319/Daily_ConCept/")
sys.path.append("/data/group/800319/Daily_ConCept/ConceptApi.py")
sys.path.append('/data/user/fengchi/MyWork/ShortTermTrading')

import numpy as np
import pandas as pd
from tqdm import tqdm
import time
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.stockList import clean_stock_list, trans_int2windcode
from multiprocessing import Pool
from ConceptApi import get_basic_values, Get_Concept_Code

basic_values = get_basic_values('Active_Concept')
concept = Get_Concept_Code()
concept_dict = concept.to_dict()['S_INFO_NAME']
daily_hot_concept = basic_values.rename(columns=concept_dict)
concept_code_list = list(concept_dict.keys())
concept_list = daily_hot_concept.columns.tolist() # 中文所有概念板块列表

