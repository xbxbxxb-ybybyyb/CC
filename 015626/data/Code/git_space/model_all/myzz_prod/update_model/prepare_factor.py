import sys, os
sys.path.insert(4, '/data/user/015626/data/Code/git_space/model_all/mobius_model/myzz_prod/')
sys.path.insert(4, '/dfs/user/015626/JupyterNotebooks/utils/') # 引入multifactor

import os
import gc
import numpy as np
import pandas as pd

from strategy.fitting_model import read_pickle, save_pickle
from ts.utility.ts_utility import read_ts_fac_helper

####################################################################################################

# factor end date
fac_lib_date = '20241227'

####################################################################################################

fac_base = '/data/user/015626/model/mobius_prod_zz/factor/minute'

version_list = ['if_v7c', 'ic_v7unifac', 'im_v1unifac']
for version in version_list:
    if version == 'if_v7c':
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IF/prod/20230526_if_v7c.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm/'
        suffix_spec_dict = {'if_v7': ['IF_linear'],
                            'if_v7nl_181': ['IF_linear', 'IF_nonlinear', 'IF_181'],
                            'if_v7nlad_181ad': ['IF_linear', 'IF_nonlinear', 'IF_181', 'IF_nonlinear_diff', 'IF_181_diff']}
    elif version == 'ic_v7unifac':
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IC/prod/20230526_ic_v7unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm/'
        suffix_spec_dict = {'ic_v7_if_v7': ['IC_linear', 'IF_linear'],
                            'ic_v7nl_if_v7nl_181': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181'],
                            'ic_v7nlad_if_v7nlad_181ad': ['IC_linear', 'IF_linear', 'IC_nonlinear', 'IF_nonlinear', 'IF_181', 'IC_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff']}
    elif version == 'im_v1unifac':
        fac_ref_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/factor_lists/for_zsj/IM/prod/20230526_im_v1unifac.pkl'
        path_ever = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm/'
        suffix_spec_dict = {'im_v1_if_v7_2': ['IM_linear', 'IF_linear'],
                            'im_v1nl_181_if_v7_2nl_181': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IM_181', 'IF_181'],
                            'im_v1nlad_181ad_if_v7_2nlad_181ad': ['IM_linear', 'IF_linear', 'IM_nonlinear', 'IF_nonlinear', 'IF_181', 'IM_181', 'IM_nonlinear_diff', 'IF_nonlinear_diff', 'IF_181_diff', 'IM_181_diff']}
    else:
        raise RuntimeError('version error')

    fac_ref = read_pickle(fac_ref_path)
    sub_list = list(fac_ref.keys())
    sub_list.sort()
    for i in sub_list:
        print('%s : %d' % (i, len(fac_ref[i])), flush=True)

    for suffix in suffix_spec_dict:
        print('*** %s ~ %s ***' % (suffix, suffix_spec_dict[suffix]), flush=True)
        fac_list = []
        for path_name_itr in suffix_spec_dict[suffix]:
            fac_list_itr = [i.replace('.h5', '') for i in fac_ref[path_name_itr]]
            if version == 'if_v7c':
                fac_list_itr = [i for i in fac_list_itr if i not in ['wsc_spot_13_if']]
            fac_itr = read_ts_fac_helper(path_ever, fac_list=fac_list_itr)
            fac_list.append(fac_itr)
            s_time, e_time = fac_itr.index[0], fac_itr.index[-1]
            fac_num = fac_itr.shape[1]
            print(path_name_itr, s_time, e_time, fac_num, flush=True)
            print(path_name_itr, flush=True)
        fac_val = pd.concat(fac_list, axis=1).loc[:fac_lib_date]
        fac_cov_ts = np.isfinite(fac_val).sum(axis=1)

        fac_val = fac_val.fillna(0)
        if len(set(fac_val.columns.tolist())) - fac_val.shape[1] != 0:
            print('fac name error', flush=True)
            raise Exception

        fac_path = os.path.join(fac_base, '%s_%s.pkl' % (suffix, fac_lib_date))
        save_pickle(fac_val, fac_path)
        del fac_val, fac_list
        gc.collect()
        print('-' * 40, flush=True)
