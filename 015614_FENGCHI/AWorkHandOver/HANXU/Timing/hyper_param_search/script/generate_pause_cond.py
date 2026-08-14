# coding: utf-8
# Author：fengchi863
# Date ：2022/6/29 21:48

import pandas as pd

hyper_evals_ini_path = '/data/group/800442/800319/Timing/BackTest/Signal/hyper_search_setting/'

pause_dict = {
    'XGB400_dc': 100,
    'XGB': 100,
}

pause = pd.DataFrame(pause_dict, index=['max_evals']).T
pd.to_pickle(pause, hyper_evals_ini_path + 'hyper_search_ini.pkl')

