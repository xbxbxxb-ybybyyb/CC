import sys

sys.path.insert(0, '/data/user/020529/mobius_product_zz/code')

import os
import pandas as pd

####################################################################################################

fac_lib_date = '20250328'

# version_type = 'production'
version_type = 'one_shot'  # pass in rebal_freq_spec
rebal_freq_dt = ['20191227',
                 '20200327', '20200619', '20200925', '20201225',
                 '20210326', '20210625', '20210924', '20211231',
                 '20220325', '20220624', '20220930', '20221230',
                 '20230331', '20230630', '20230922', '20231229',
                 '20240329', '20240628', '20240927', '20241227',
                 '20250328']
rebal_freq_spec = [pd.Timestamp(i + '-14:56:00') for i in rebal_freq_dt]

#suffix_list = ['if_v7c']
#suffix_list = ['ic_v7unifac']
#suffix_list = ['im_v1unifac']
#suffix_list = ['if_v7c_spot']
#suffix_list = ['ic_v7unifac_spot']
suffix_list = ['im_v1unifac_spot']

####################################################################################################

fac_base = '/dfs/user/012398/data/strategy/mobius/mobius_prod_zz/factor/minute'
pred_res_root = '/dfs/user/012398/data/strategy/mobius/mobius_prod_zz/pred_index'

check_flag = False
ftypes = ['GEN_MODEL_FACTORS']
flag_path_mobius = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS'
flat_path_model = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/flag'
flag_gap = 60 * 5
flag_expiration = 60 * 60 * 24

test_run = None
# test_run = -3

# trade_contract_dict
trade_contract_dict = {'if_v7c': 'IF.CFE',
                       'ic_v7unifac': 'IC.CFE',
                       'im_v1unifac': 'IM.CFE',
                       'if_v7c_spot': 'IF.CFE',
                       'ic_v7unifac_spot': 'IC.CFE',
                       'im_v1unifac_spot': 'IM.CFE'}

# hpr
short_list = [1, 5, 10]
long_list = [10, 20, 30]
full_list = [1, 5, 10, 20, 30, 60]

hpr_spec_dd = {}
# prod
version_list_prod = []

# research
# hpr_template = {i: short_list for i in ['lasso_reg', 'lr_cla', 'lgbm_cla', 'lgbm_reg', 'et_cla', 'lstm_cla', 'mlp_reg', 'mlp_cla', 'cnnlstm_cla', 'cnnlstm_reg']}
hpr_template = {i: full_list for i in ['lasso_reg', 'lr_cla', 'lgbm_cla', 'lgbm_reg', 'et_cla', 'lstm_cla', 'mlp_reg', 'mlp_cla']}
linear_fac_dict = {}

save_memory_model_list = []

for v in trade_contract_dict:
    if v not in hpr_spec_dd:
        hpr_spec_dd[v] = hpr_template
    if v not in version_list_prod:
        if v not in save_memory_model_list:
            save_memory_model_list.append(v)

use_new = False
use_dummy = True
update = False
shuffle = True
filter_date = 'prod'

roll_day = 240 * 3
bar_num_day = 240
expanding_window = True
train_s = '20160301'
if train_s == '20190101':
    roll_day = 240 * 1

roll_win = roll_day * bar_num_day

sdate_fit = '20191201'
if version_type == 'research':
    rebal_mode_dict = {'year_year': '20230601'}
    sdate_fit = '20201201'
else:
    rebal_mode_dict = {'quarter_quarter': '20220601'}

##### warning ~suffix_list can't have spot and future mix,im needs seperate training
if suffix_list[0].find('spot') >= 0:
    pred_price = 'twap'
    price_type = 'spot'
    # spot is higher than im order
elif suffix_list[0].find('im') >= 0 and suffix_list[0].find('spot') < 0:
    pred_price = 'twap'
    price_type = 'fake'
else:
    pred_price = 'vwap'
    price_type = 'future_fix'

index_list = ['IC.CFE', 'IF.CFE', 'IH.CFE', 'IM.CFE']

burn_overnight = False  # True
slice_range = [[930, 1129], [1300, 1456]]
sdate, edate = str(20111201), str(fac_lib_date) + '235959'

minute_fake_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/future_twap_im_interpolation.h5'
fts_path_is = '/dfs/group/800466/warehouse/prod/MD/CHINA_FUTURES/MINUTE/pre_history/FUTURE_DATA_120101_200901.pkl'  # fix start date to 20160301
fts_path_os = '/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/FUTURE_DATA_2020.pkl'
minute_future_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5'
minute_spot_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/TWAP_SPOT.h5'

if suffix_list[0].find('no_dummy') > 0 or suffix_list[0].find('base') > 0:
    use_dummy = False
process_list = None
process_dat_func = None

pred_res_base_dict = {i: os.path.join(pred_res_root, 'minute/%s_%s' % (i, filter_date)) for i in suffix_list}
fac_path_dict = {i: os.path.join(fac_base, '%s_%s.pkl' % (i, fac_lib_date)) for i in suffix_list}

####################################################################################################

spec_fac_suffix = {}

suffix_itr = 'if_v7c'
spec_fac_suffix[suffix_itr] = {'et_cla': 'if_v7nl_181',
                               'lgbm_cla': 'if_v7nlad_181ad',
                               'lgbm_reg': 'if_v7nlad_181ad',
                               'lstm_cla': 'if_v7nl_181',
                               'mlp_reg': 'if_v7nlad_181ad',
                               'mlp_cla': 'if_v7nlad_181ad'}
fac_path_dict[suffix_itr] = {m: os.path.join(fac_base, '%s_%s.pkl' % (spec_fac_suffix[suffix_itr][m], fac_lib_date)) for m in spec_fac_suffix[suffix_itr]}
hpr_spec_dd[suffix_itr] = {**{i: short_list for i in ['lasso_reg', 'lgbm_cla', 'lgbm_reg', 'mlp_reg', 'mlp_cla']},
                           **{i: long_list for i in ['lr_cla', 'et_cla', 'lstm_cla']}}

suffix_itr = 'ic_v7unifac'
spec_fac_suffix[suffix_itr] = {'et_cla': 'ic_v7nl_if_v7nl_181',
                               'lstm_cla': 'ic_v7nl_if_v7nl_181',
                               'lgbm_cla': 'ic_v7nlad_if_v7nlad_181ad',
                               'lgbm_reg': 'ic_v7nlad_if_v7nlad_181ad',
                               'mlp_reg': 'ic_v7nlad_if_v7nlad_181ad',
                               'mlp_cla': 'ic_v7nlad_if_v7nlad_181ad'}
fac_path_dict[suffix_itr] = {m: os.path.join(fac_base, '%s_%s.pkl' % (spec_fac_suffix[suffix_itr][m], fac_lib_date)) for m in spec_fac_suffix[suffix_itr]}
hpr_spec_dd[suffix_itr] = {**{i: short_list for i in ['lasso_reg', 'lr_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg', 'mlp_cla']},
                           **{i: long_list for i in ['et_cla', 'lstm_cla']}}

suffix_itr = 'im_v1unifac'
spec_fac_suffix[suffix_itr] = {'et_cla': 'im_v1nl_181_if_v7_2nl_181',
                               'lstm_cla': 'im_v1nl_181_if_v7_2nl_181',
                               'lgbm_cla': 'im_v1nlad_181ad_if_v7_2nlad_181ad',
                               'lgbm_reg': 'im_v1nlad_181ad_if_v7_2nlad_181ad',
                               'mlp_reg': 'im_v1nlad_181ad_if_v7_2nlad_181ad',
                               'mlp_cla': 'im_v1nlad_181ad_if_v7_2nlad_181ad'}
fac_path_dict[suffix_itr] = {m: os.path.join(fac_base, '%s_%s.pkl' % (spec_fac_suffix[suffix_itr][m], fac_lib_date)) for m in spec_fac_suffix[suffix_itr]}
hpr_spec_dd[suffix_itr] = {**{i: short_list for i in ['lasso_reg', 'lr_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg', 'mlp_cla']},
                           **{i: long_list for i in ['et_cla', 'lstm_cla']}}

suffix_itr = 'if_v7c_spot'
spec_fac_suffix[suffix_itr] = {'et_cla': 'if_v7nl_181',
                               'lgbm_cla': 'if_v7nlad_181ad',
                               'lgbm_reg': 'if_v7nlad_181ad',
                               'lstm_cla': 'if_v7nl_181',
                               'mlp_reg': 'if_v7nlad_181ad',
                               'mlp_cla': 'if_v7nlad_181ad'}
fac_path_dict[suffix_itr] = {m: os.path.join(fac_base, '%s_%s.pkl' % (spec_fac_suffix[suffix_itr][m], fac_lib_date)) for m in spec_fac_suffix[suffix_itr]}
hpr_spec_dd[suffix_itr] = {**{i: long_list for i in ['lasso_reg', 'lgbm_cla', 'lgbm_reg', 'mlp_reg', 'mlp_cla']},
                           **{i: long_list for i in ['lr_cla', 'et_cla', 'lstm_cla']}}

suffix_itr = 'ic_v7unifac_spot'
spec_fac_suffix[suffix_itr] = {'et_cla': 'ic_v7nl_if_v7nl_181',
                               'lstm_cla': 'ic_v7nl_if_v7nl_181',
                               'lgbm_cla': 'ic_v7nlad_if_v7nlad_181ad',
                               'lgbm_reg': 'ic_v7nlad_if_v7nlad_181ad',
                               'mlp_reg': 'ic_v7nlad_if_v7nlad_181ad',
                               'mlp_cla': 'ic_v7nlad_if_v7nlad_181ad'}
fac_path_dict[suffix_itr] = {m: os.path.join(fac_base, '%s_%s.pkl' % (spec_fac_suffix[suffix_itr][m], fac_lib_date)) for m in spec_fac_suffix[suffix_itr]}
hpr_spec_dd[suffix_itr] = {**{i: long_list for i in ['lasso_reg', 'lr_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg', 'mlp_cla']},
                           **{i: long_list for i in ['et_cla', 'lstm_cla']}}

suffix_itr = 'im_v1unifac_spot'
spec_fac_suffix[suffix_itr] = {'et_cla': 'im_v1nl_181_if_v7_2nl_181',
                               'lstm_cla': 'im_v1nl_181_if_v7_2nl_181',
                               'lgbm_cla': 'im_v1nlad_181ad_if_v7_2nlad_181ad',
                               'lgbm_reg': 'im_v1nlad_181ad_if_v7_2nlad_181ad',
                               'mlp_reg': 'im_v1nlad_181ad_if_v7_2nlad_181ad',
                               'mlp_cla': 'im_v1nlad_181ad_if_v7_2nlad_181ad'}
fac_path_dict[suffix_itr] = {m: os.path.join(fac_base, '%s_%s.pkl' % (spec_fac_suffix[suffix_itr][m], fac_lib_date)) for m in spec_fac_suffix[suffix_itr]}
hpr_spec_dd[suffix_itr] = {**{i: long_list for i in ['lasso_reg', 'lr_cla', 'lgbm_cla', 'lgbm_reg', 'mlp_reg', 'mlp_cla']},
                           **{i: long_list for i in ['et_cla', 'lstm_cla']}}

####################################################################################################

# model spec
return_misc = False
return_model = 3
tsp = False
fold_num = 5

# y return trunc
ts_trunc = True
trunc_day = 20
cut_limit = 0.999
trunc_win = 240 * trunc_day
min_pct_trunc = 0.5
ret_shift = True

use_generator_list = []

# hpr_trend = True
# trend_up = True
# past_weight = 0.5
past_weight = 0.2

hpr_trend = False
trend_up = False

# add_mcount = True
add_mcount = False
