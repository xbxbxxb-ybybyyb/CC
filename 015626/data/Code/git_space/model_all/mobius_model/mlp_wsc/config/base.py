import os


# base_root
data_base_root = '/dfs/user/017024/MobiusProd/data'

# future data
future_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5'
im_sim_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/future_twap_im_interpolation.h5'
returnlib_path = os.path.join(data_base_root, 'returnlib')
factorlib_path = os.path.join(data_base_root, 'factorlib')
factor_list_path = os.path.join(data_base_root, 'factor_list')
siglib_path = os.path.join(data_base_root, 'siglib')
model_save_path = os.path.join(data_base_root, 'model_result')
log_path = os.path.join(data_base_root, 'log')
prod_share_path = '/data/user/017024/share/vars/MobiusProd/'

# factor value path
factor_root_dict = {
    'IF_ever': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm',
    'IC_unifac_ever': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm',
    'IM_unifac_ever': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm',
}

# factor list path
factor_list_dict = {
    'if_v9c': os.path.join(factor_list_path, 'IF_v9c_li_non_nondiff_181_181diff.pkl'),
    'ic_v8uf': os.path.join(factor_list_path, 'IC_v8uf_li_non_nondiff_ifli_ifnon_ifnondiff_if181_if181diff.pkl'),
    'im_v1uf': os.path.join(factor_list_path,
                            'IM_v1uf_li_non_nondiff_181_181diff_ifli_ifnon_ifnondiff_if181_if181diff.pkl'),
    'ic_v8_2uf': os.path.join(factor_list_path, 'IC_v8_2uf_li_non_nondiff_ifli_ifnon_ifnondiff_if181_if181diff.pkl'),
}

# random seed dict
random_seed_dict = {
    3416: 0,
    4351: 1,
    7387: 2,
    8780: 3,
    2537: 4,
}

# other
sig_value_bgn_date = 20220101
