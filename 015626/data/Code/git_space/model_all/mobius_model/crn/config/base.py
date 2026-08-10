# project root
root = '/dfs/user/020529/mobius_product'
pack_model_root = '/data/user/020529/share/mobius_prod/model_trade'
pack_value_root = '/data/user/020529/share/mobius_prod/model_update'

# datetime format
fmt = '%Y-%m-%d %H:%M:%S'

# rank_index path
index_root_dict = {
    'IH': '/data/user/020529/share/mobius_prod/model_update/rank_index/ih_60000_25_75',
    'IF': '/data/user/020529/share/mobius_prod/model_update/rank_index/if_60000_25_75',
    'IC': '/data/user/020529/share/mobius_prod/model_update/rank_index/ic_60000_25_75',
    'IM': '/data/user/020529/share/mobius_prod/model_update/rank_index/im_60000_25_75',
}

# factor root path
factor_root_dict = {
    'IF_ever': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm',
    'IC_unifac_ever': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm',
    'IM_unifac_ever': '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm',

    'IF_ever_50': '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/IF_shift_50/if_ever/minute_norm',
    'IF_ever_55': '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/IF_shift_55/if_ever/minute_norm',

    'IC_unifac_ever_50': '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/IC_shift_50/ic_unifac_ever/minute_norm',
    'IC_unifac_ever_55': '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/IC_shift_55/ic_unifac_ever/minute_norm',

    'IM_unifac_ever_50': '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/IM_shift_50/im_unifac_ever/minute_norm',
    'IM_unifac_ever_55': '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/IM_shift_55/im_unifac_ever/minute_norm',
}

# factor list path
factor_list_dict = {
    'IF_linear_v7': '/dfs/user/020529/mobius_product/data/config/IF_linear_v7.pkl',
    'IC_linear_v7': '/dfs/user/020529/mobius_product/data/config/IC_linear_v7.pkl',
    'IM_linear_v1': '/dfs/user/020529/mobius_product/data/config/IM_linear_v1.pkl',

    'IF_v7b': '/dfs/user/020529/mobius_product/data/config/IF_v7_116ad_181.pkl',
    'IC_v7b': '/dfs/user/020529/mobius_product/data/config/IC_v7_116ad_IF_v7_116ad_181.pkl',
    'IM_v1b': '/dfs/user/020529/mobius_product/data/config/IM_v1_116ad_IF_v7_116ad_181.pkl',

    'IF_v7c': '/dfs/user/020529/mobius_product/data/config/IF_v7_116ad_181ad.pkl',
    'IC_v7c': '/dfs/user/020529/mobius_product/data/config/IC_v7_116ad_IF_v7_116ad_181ad.pkl',
    'IM_v1c': '/dfs/user/020529/mobius_product/data/config/IM_v1_116ad_181ad_IF_v7_116ad_181ad.pkl',

    'IF_trend_v7a': '/dfs/user/020529/mobius_product/data/config/IF_linear_v7.pkl',
    'IC_trend_v7a': '/dfs/user/020529/mobius_product/data/config/IC_linear_v7_IF_linear_v7.pkl',
    'IM_trend_v1a': '/dfs/user/020529/mobius_product/data/config/IM_linear_v1_IF_linear_v7.pkl',
}
